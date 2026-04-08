class AuditCategory:
    AUTH = "AUTH"
    PROJECT = "PROJECT"
    SPRINT = "SPRINT"
    AGENT = "AGENT"
    DOCUMENT = "DOCUMENT"
    WORKSPACE = "WORKSPACE"
    PIPELINE = "PIPELINE"
    SYSTEM = "SYSTEM"
    REQUIREMENT = "REQUIREMENT"  # Phase 2


class AuditOperation:
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RUN = "run"
    START = "start"
    COMPLETE = "complete"
    FAIL = "fail"
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    # Phase 2
    EXTRACT = "extract"
    APPROVE = "approve"
    REJECT = "reject"
    BULK_APPROVE = "bulk_approve"
