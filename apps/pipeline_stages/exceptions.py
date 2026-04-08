class StageGateError(Exception):
    """Raised when a hard gate blocks stage progression."""


class StageLockedError(Exception):
    """Raised when attempting to modify a locked/complete stage."""


class StagePrerequisiteError(Exception):
    """Raised when prerequisites for a stage are not met."""
