import logging

logger = logging.getLogger("agent_factory")


class AgentLogger:
    @staticmethod
    def log_usage(
        agent_type: str,
        llm_model: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: int,
        success: bool,
        cache_creation_tokens: int = 0,
        cache_read_tokens: int = 0,
        error_message: str = "",
        job_id=None,
        object_type: str = "",
        object_id: str = "",
    ):
        """Write immutable AgentUsageLog. Never raises."""
        from apps.agent_factory.models import AgentUsageLog

        try:
            return AgentUsageLog.objects.create(
                agent_type=agent_type,
                llm_model=llm_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_creation_tokens=cache_creation_tokens,
                cache_read_tokens=cache_read_tokens,
                duration_ms=duration_ms,
                success=success,
                error_message=error_message,
                job_id=job_id,
                object_type=object_type,
                object_id=object_id,
            )
        except Exception as exc:
            logger.warning("AgentLogger.log_usage failed: %s", exc)
            return None

    @staticmethod
    def log_event(
        agent_type: str,
        event_type: str,
        content: str = "",
        tool_name: str = "",
        tool_input: dict | None = None,
        tool_result: dict | None = None,
        thinking: str = "",
        tokens_used: int = 0,
        duration_ms: int = 0,
        job=None,
        object_type: str = "",
        object_id: str = "",
    ):
        """Write AgentEventLog for one SDK loop event. Never raises."""
        from apps.agent_factory.models import AgentEventLog

        try:
            return AgentEventLog.objects.create(
                agent_type=agent_type,
                job=job,
                event_type=event_type,
                tool_name=tool_name,
                tool_input=tool_input or {},
                tool_result=tool_result or {},
                content=content,
                thinking=thinking,
                tokens_used=tokens_used,
                duration_ms=duration_ms,
                object_type=object_type,
                object_id=object_id,
            )
        except Exception as exc:
            logger.warning("AgentLogger.log_event failed: %s", exc)
            return None
