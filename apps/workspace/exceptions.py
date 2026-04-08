# Claude Code: implement workspace exceptions


class WorkspaceError(Exception):
    """Raised on invalid workspace operations including path traversal attempts."""
