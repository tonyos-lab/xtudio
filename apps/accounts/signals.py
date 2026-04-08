import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_workspace(sender, instance, created, **kwargs):
    if created:
        try:
            from apps.workspace.services import WorkspaceService

            WorkspaceService.create_user_workspace(instance.username)

            from apps.audit_trail.constants import AuditCategory, AuditOperation
            from apps.audit_trail.services import AuditService

            AuditService.log(
                category=AuditCategory.WORKSPACE,
                operation=AuditOperation.CREATE,
                action=f"User workspace created for {instance.username}",
                user=instance,
                status="success",
            )
        except Exception as exc:
            logger.warning(
                "Failed to create workspace for user %s: %s",
                instance.username,
                exc,
            )
