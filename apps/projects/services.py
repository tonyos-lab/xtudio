import logging
from typing import Any

from django.db.models import QuerySet

from apps.projects.models import Project
from apps.workspace.services import WorkspaceService

logger = logging.getLogger(__name__)


class ProjectService:
    @staticmethod
    def create(owner: Any, name: str, description: str = "", tech_stack: str = "") -> Project:
        project = Project.objects.create(
            owner=owner,
            name=name,
            description=description,
            tech_stack=tech_stack,
        )

        ws_path = WorkspaceService.create_project_workspace(
            username=owner.username,
            project_id=str(project.id),
        )
        project.workspace_path = str(ws_path)
        project.save(update_fields=["workspace_path"])

        try:
            from apps.audit_trail.constants import AuditCategory, AuditOperation
            from apps.audit_trail.services import AuditService

            AuditService.log_success(
                category=AuditCategory.PROJECT,
                operation=AuditOperation.CREATE,
                action=f'Project "{name}" created',
                user=owner,
                project_id=project.id,
            )
        except Exception as exc:
            logger.warning("Failed to write audit log for project creation: %s", exc)

        try:
            from apps.notification_hub.services import NotificationService

            NotificationService.create(
                user=owner,
                title="Project Created",
                message=f'Your project "{name}" is ready.',
                category="project",
            )
        except Exception as exc:
            logger.warning("Failed to send notification for project creation: %s", exc)

        return project

    @staticmethod
    def update(project: Project, **fields: Any) -> Project:
        allowed = {"name", "description", "tech_stack", "status"}
        update_fields = []
        for key, value in fields.items():
            if key in allowed:
                setattr(project, key, value)
                update_fields.append(key)
        if update_fields:
            update_fields.append("updated_at")
            project.save(update_fields=update_fields)

        try:
            from apps.audit_trail.constants import AuditCategory, AuditOperation
            from apps.audit_trail.services import AuditService

            AuditService.log_success(
                category=AuditCategory.PROJECT,
                operation=AuditOperation.UPDATE,
                action=f'Project "{project.name}" updated',
                project_id=project.id,
            )
        except Exception as exc:
            logger.warning("Failed to write audit log for project update: %s", exc)

        return project

    @staticmethod
    def archive(project: Project) -> Project:
        project.status = Project.STATUS_ARCHIVED
        project.save(update_fields=["status", "updated_at"])

        try:
            from apps.audit_trail.constants import AuditCategory, AuditOperation
            from apps.audit_trail.services import AuditService

            AuditService.log_success(
                category=AuditCategory.PROJECT,
                operation=AuditOperation.UPDATE,
                action=f'Project "{project.name}" archived',
                project_id=project.id,
            )
        except Exception as exc:
            logger.warning("Failed to write audit log for project archive: %s", exc)

        return project

    @staticmethod
    def get_for_user(user: Any) -> QuerySet[Project]:
        return Project.objects.filter(owner=user).order_by("-created_at")
