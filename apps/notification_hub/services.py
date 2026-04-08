import logging

from django.utils import timezone

logger = logging.getLogger("notification_hub")


class NotificationService:
    @staticmethod
    def create(
        user,
        title: str,
        message: str,
        category: str = "",
        reference_id=None,
        reference_type: str = "",
        metadata: dict | None = None,
    ):
        """Create in-app notification. Never raises."""
        from apps.notification_hub.models import Notification

        try:
            return Notification.objects.create(
                user=user,
                title=title,
                message=message,
                category=category,
                reference_id=reference_id,
                reference_type=reference_type,
                metadata=metadata or {},
            )
        except Exception as exc:
            logger.warning("NotificationService.create failed: %s", exc)
            return None

    @staticmethod
    def mark_read(notification_id, user) -> bool:
        """Mark a single notification as read."""
        from apps.notification_hub.models import Notification

        try:
            updated = Notification.objects.filter(
                id=notification_id, user=user, is_read=False
            ).update(is_read=True, read_at=timezone.now())
            return updated > 0
        except Exception as exc:
            logger.warning("NotificationService.mark_read failed: %s", exc)
            return False

    @staticmethod
    def mark_all_read(user) -> int:
        """Mark all unread notifications as read. Returns count marked."""
        from apps.notification_hub.models import Notification

        try:
            return Notification.objects.filter(user=user, is_read=False).update(
                is_read=True, read_at=timezone.now()
            )
        except Exception as exc:
            logger.warning("NotificationService.mark_all_read failed: %s", exc)
            return 0

    @staticmethod
    def get_unread(user, limit: int = 50):
        """Return unread notifications for user."""
        from apps.notification_hub.models import Notification

        return Notification.objects.filter(user=user, is_read=False).order_by("-created_at")[:limit]

    @staticmethod
    def get_all(user, limit: int = 100):
        """Return all notifications for user."""
        from apps.notification_hub.models import Notification

        return Notification.objects.filter(user=user).order_by("-created_at")[:limit]

    @staticmethod
    def get_unread_count(user) -> int:
        """Return count of unread notifications."""
        from apps.notification_hub.models import Notification

        try:
            return Notification.objects.filter(user=user, is_read=False).count()
        except Exception:
            return 0
