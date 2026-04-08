class AgentConfigError(Exception):
    """No active AgentTemplate found for agent_type."""


class AgentCallError(Exception):
    """Anthropic API call failed."""


class AgentParseError(Exception):
    """JSON parse and regex extraction both failed."""
