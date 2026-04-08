import logging
import time

from apps.agent_factory.exceptions import AgentCallError, AgentConfigError, AgentParseError
from apps.agent_factory.logger import AgentLogger
from apps.agent_factory.parser import PromptRenderer, ResponseParser

logger = logging.getLogger("agent_factory")


class AgentFactory:
    @staticmethod
    def run_agent(agent_type: str, context: dict, mode: str | None = None) -> dict:
        """
        Single-shot agent call. Reads AgentTemplate, renders prompt,
        calls Anthropic API, parses response, writes AgentUsageLog.
        """
        from apps.agent_factory.models import AgentTemplate

        template = AgentTemplate.objects.filter(agent_type=agent_type, is_active=True).first()
        if not template:
            raise AgentConfigError(f"No active AgentTemplate for '{agent_type}'")

        effective_mode = mode or ("mock" if template.step_use_mock_response else "live")

        if effective_mode == "mock" or not template.step_call_llm:
            logger.info("AgentFactory.run_agent: mock mode for %s", agent_type)
            return template.mock_response or {"mock": True, "agent_type": agent_type}

        # Live mode — call Anthropic API
        try:
            import anthropic as anthropic_sdk
        except ImportError as exc:
            raise AgentCallError("anthropic SDK not installed. Run: pip install anthropic") from exc

        from django.conf import settings

        api_key = getattr(settings, "ANTHROPIC_API_KEY", "")
        if not api_key:
            raise AgentCallError("ANTHROPIC_API_KEY is not set.")

        rendered_prompt = (
            PromptRenderer.render(template.system_prompt, context)
            if "{" in template.system_prompt
            else template.system_prompt
        )

        start_ms = int(time.monotonic() * 1000)
        try:
            client = anthropic_sdk.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=template.llm_model,
                max_tokens=template.max_tokens,
                system=rendered_prompt,
                messages=[{"role": "user", "content": str(context)}],
            )
        except Exception as exc:
            duration_ms = int(time.monotonic() * 1000) - start_ms
            AgentLogger.log_usage(
                agent_type=agent_type,
                llm_model=template.llm_model,
                input_tokens=0,
                output_tokens=0,
                duration_ms=duration_ms,
                success=False,
                error_message=str(exc),
            )
            raise AgentCallError(f"Anthropic API call failed: {exc}") from exc

        duration_ms = int(time.monotonic() * 1000) - start_ms
        input_tokens = response.usage.input_tokens if response.usage else 0
        output_tokens = response.usage.output_tokens if response.usage else 0
        raw_text = " ".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()

        AgentLogger.log_usage(
            agent_type=agent_type,
            llm_model=template.llm_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            success=True,
        )

        try:
            return ResponseParser.parse_with_fallback(raw_text)
        except AgentParseError as exc:
            raise AgentCallError(f"Response parse failed: {exc}") from exc

    @staticmethod
    def run_agent_async(
        agent_type: str,
        context: dict,
        priority: int = 5,
        object_type: str = "",
        object_id: str = "",
        metadata: dict | None = None,
    ) -> dict:
        """Enqueue agent call as JobQueue record. Returns immediately."""
        from apps.agent_factory.queue import JobQueueService

        job = JobQueueService.enqueue(
            agent_type=agent_type,
            context=context,
            priority=priority,
            object_type=object_type,
            object_id=object_id,
            metadata=metadata,
        )
        return {"job_id": str(job.id), "status": "queued"}

    @staticmethod
    def get_job_status(job_id: str) -> dict:
        """Poll the status of an async job."""
        from apps.agent_factory.models import JobQueue

        try:
            job = JobQueue.objects.get(id=job_id)
            return {"status": job.status, "result": job.result, "error": job.error_message}
        except JobQueue.DoesNotExist:
            return {"status": "not_found", "result": {}, "error": "Job not found"}

    @staticmethod
    def register_agent(agent_type: str, defaults: dict | None = None):
        """Declare a new agent type and seed default AgentTemplate if none exists."""
        from apps.agent_factory.models import AgentTemplate

        defaults = defaults or {}
        template, created = AgentTemplate.objects.get_or_create(
            agent_type=agent_type,
            defaults={
                "label": defaults.get("label", agent_type.replace("_", " ").title()),
                "system_prompt": defaults.get("system_prompt", f"You are the {agent_type} agent."),
                "llm_model": defaults.get("llm_model", "claude-sonnet-4-6"),
                "max_tokens": defaults.get("max_tokens", 1000),
                "max_turns": defaults.get("max_turns", 10),
                "allowed_tools": defaults.get("allowed_tools", []),
                "is_sdk_loop": defaults.get("is_sdk_loop", False),
            },
        )
        if created:
            logger.info("AgentFactory.register_agent: created template for '%s'", agent_type)
        return template

    @staticmethod
    def get_config(agent_type: str):
        """Return active AgentTemplate for agent_type."""
        from apps.agent_factory.models import AgentTemplate

        return AgentTemplate.objects.filter(agent_type=agent_type, is_active=True).first()

    @staticmethod
    def list_agents() -> list:
        """Return all registered agent types with active config status."""
        from apps.agent_factory.models import AgentTemplate

        return list(AgentTemplate.objects.values("agent_type", "label", "is_active", "llm_model"))

    @staticmethod
    def health_check() -> dict:
        """Verify: API key set, DB reachable, active templates exist. Never raises."""
        from django.conf import settings

        issues = []
        try:
            if not getattr(settings, "ANTHROPIC_API_KEY", ""):
                issues.append("ANTHROPIC_API_KEY is not set")
        except Exception as exc:
            issues.append(f"Settings error: {exc}")
        try:
            from apps.agent_factory.models import AgentTemplate

            count = AgentTemplate.objects.filter(is_active=True).count()
            if count == 0:
                issues.append("No active AgentTemplate records found")
        except Exception as exc:
            issues.append(f"DB error: {exc}")
        return {"healthy": len(issues) == 0, "issues": issues}
