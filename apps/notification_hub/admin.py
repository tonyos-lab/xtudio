from django.contrib import admin

from apps.notification_hub.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "title", "category", "is_read"]
    list_filter = ["is_read", "category", "created_at"]
    search_fields = ["title", "message", "user__username", "user__email"]
    readonly_fields = ["id", "created_at", "read_at"]
