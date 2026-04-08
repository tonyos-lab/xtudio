import csv

from django.contrib import admin
from django.http import HttpResponse

from apps.audit_trail.models import AuditLog


@admin.action(description="Export selected as CSV")
def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="audit_logs.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ["created_at", "actor", "category", "operation", "status", "action", "project_id"]
    )
    for obj in queryset:
        writer.writerow(
            [
                obj.created_at,
                obj.actor,
                obj.category,
                obj.operation,
                obj.status,
                obj.action,
                obj.project_id,
            ]
        )
    return response


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "actor", "category", "operation", "status", "user", "project_id"]
    list_filter = ["category", "operation", "status", "actor", "created_at"]
    search_fields = ["action", "error_message", "object_type", "object_id"]
    readonly_fields = [f.name for f in AuditLog._meta.get_fields()]
    actions = [export_as_csv]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
