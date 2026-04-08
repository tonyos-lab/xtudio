def notification_context(request) -> dict:
    """Add unread_notification_count to all template contexts."""
    try:
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return {"unread_notification_count": 0}
        from apps.notification_hub.models import Notification

        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {"unread_notification_count": count}
    except Exception:
        return {"unread_notification_count": 0}
