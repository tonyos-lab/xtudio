class MemoryTier:
    PLATFORM = "platform"  # Tier 1 — global
    PROJECT = "project"  # Tier 2 — per project
    SESSION = "session"  # Tier 3 — per sprint/session

    ALL = [PLATFORM, PROJECT, SESSION]
    RANK = {PLATFORM: 1, PROJECT: 2, SESSION: 3}


class MemoryBlockType:
    # Tier 1 — Platform
    TECH_PROFILE = "tech_profile"
    PLATFORM_RULES = "platform_rules"
    GLOBAL_PATTERNS = "global_patterns"

    # Tier 2 — Project
    ARCHITECTURE = "architecture"
    TECH_STACK = "tech_stack"
    REQUIREMENTS = "requirements"
    DESIGN_DECISIONS = "design_decisions"
    PROJECT_RULES = "project_rules"

    # Tier 3 — Session
    AGENT_OUTPUT = "agent_output"
    AGENT_ERRORS = "agent_errors"
    SPRINT_RESULTS = "sprint_results"
    IN_RUN_EVENTS = "in_run_events"
