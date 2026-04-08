import json
import re

from apps.agent_factory.exceptions import AgentParseError


class ResponseParser:
    @staticmethod
    def parse_json(raw_text: str) -> dict:
        """Extract and clean JSON from LLM raw output."""
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned.strip()).strip()

        # Find outermost { or [
        start = -1
        for i, ch in enumerate(cleaned):
            if ch in ("{", "["):
                start = i
                break

        if start >= 0:
            open_ch = cleaned[start]
            close_ch = "}" if open_ch == "{" else "]"
            depth, in_str, escape = 0, False, False
            for i in range(start, len(cleaned)):
                ch = cleaned[i]
                if escape:
                    escape = False
                    continue
                if ch == "\\" and in_str:
                    escape = True
                    continue
                if ch == '"':
                    in_str = not in_str
                    continue
                if in_str:
                    continue
                if ch == open_ch:
                    depth += 1
                elif ch == close_ch:
                    depth -= 1
                    if depth == 0:
                        cleaned = cleaned[start : i + 1]
                        break

        cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

        try:
            result = json.loads(cleaned)
            if not isinstance(result, dict):
                raise AgentParseError(f"Expected dict, got {type(result)}")
            return result
        except json.JSONDecodeError as exc:
            raise AgentParseError(f"JSON parse failed: {exc}") from exc

    @staticmethod
    def parse_with_fallback(raw_text: str, schema: dict | None = None) -> dict:
        """Attempt JSON parse, fall back to regex. Raises AgentParseError if both fail."""
        try:
            return ResponseParser.parse_json(raw_text)
        except AgentParseError:
            pass

        result = {}
        score_match = re.search(r'"score"\s*:\s*(\d+)', raw_text)
        if score_match:
            result["score"] = int(score_match.group(1))
        status_match = re.search(r'"status"\s*:\s*"(\w+)"', raw_text)
        if status_match:
            result["status"] = status_match.group(1)

        if result:
            result["parse_warning"] = "regex_fallback_used"
            result["raw_text"] = raw_text
            return result

        raise AgentParseError(
            f"JSON parse and regex fallback both failed. raw_text_preview={raw_text[:200]!r}"
        )


class ContextBuilder:
    @staticmethod
    def merge(base_context: dict, override_context: dict) -> dict:
        """Deep merge two context dicts. Override values take precedence."""
        result = base_context.copy()
        for key, value in override_context.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ContextBuilder.merge(result[key], value)
            else:
                result[key] = value
        return result


class PromptRenderer:
    @staticmethod
    def render(template_str: str, context: dict) -> str:
        """Render a prompt template string with context variables."""
        import logging

        _logger = logging.getLogger("agent_factory")

        def replacer(match):
            key = match.group(1)
            if key in context:
                return str(context[key])
            _logger.warning("PromptRenderer: missing context key '%s'", key)
            return match.group(0)

        return re.sub(r"\{(\w+)\}", replacer, template_str)
