import logging

logger = logging.getLogger("audit_trail")


class AuditService:
    @staticmethod
    def log(
        category: str,
        operation: str,
        action: str,
        status: str = "success",
        user=None,
        actor: str = "system",
        project_id=None,
        sprint_id=None,
        stage: str = "",
        object_type: str = "",
        object_id: str = "",
        error_message: str = "",
        metadata: dict | None = None,
    ):
        """Create an immutable audit log entry. Never raises."""
        from apps.audit_trail.models import AuditLog

        try:
            return AuditLog.objects.create(
                user=user,
                actor=actor,
                category=category,
                operation=operation,
                action=action,
                status=status,
                project_id=project_id,
                sprint_id=sprint_id,
                stage=stage,
                object_type=object_type,
                object_id=str(object_id) if object_id else "",
                error_message=error_message,
                metadata=metadata or {},
            )
        except Exception as exc:
            logger.warning("AuditService.log failed: %s", exc)
            return None

    @staticmethod
    def log_success(category: str, operation: str, action: str, **kwargs):
        """Shortcut for successful operations."""
        return AuditService.log(
            category=category,
            operation=operation,
            action=action,
            status="success",
            **kwargs,
        )

    @staticmethod
    def log_failure(category: str, operation: str, action: str, error: str = "", **kwargs):
        """Shortcut for failed operations."""
        return AuditService.log(
            category=category,
            operation=operation,
            action=action,
            status="failure",
            error_message=error,
            **kwargs,
        )

    @staticmethod
    def get_project_logs(project_id, limit: int = 100):
        """Return audit logs for a specific project."""
        from apps.audit_trail.models import AuditLog

        return AuditLog.objects.filter(project_id=project_id).order_by("-created_at")[:limit]

    @staticmethod
    def get_user_logs(user, limit: int = 100):
        """Return audit logs for a specific user."""
        from apps.audit_trail.models import AuditLog

        return AuditLog.objects.filter(user=user).order_by("-created_at")[:limit]

    @staticmethod
    def get_category_logs(category: str, limit: int = 100):
        """Return audit logs for a specific category."""
        from apps.audit_trail.models import AuditLog

        return AuditLog.objects.filter(category=category).order_by("-created_at")[:limit]
