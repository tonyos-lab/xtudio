from django.contrib import admin

from apps.agent_factory.models import AgentEventLog, AgentTemplate, AgentUsageLog, JobQueue


@admin.register(AgentTemplate)
class AgentTemplateAdmin(admin.ModelAdmin):
    list_display = ["agent_type", "label", "llm_model", "is_active", "is_sdk_loop", "updated_at"]
    list_filter = ["is_active", "is_sdk_loop", "llm_model"]
    search_fields = ["agent_type", "label"]
    list_editable = ["is_active"]


@admin.register(JobQueue)
class JobQueueAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "agent_type",
        "status",
        "priority",
        "worker_id",
        "created_at",
        "completed_at",
    ]
    list_filter = ["status", "agent_type"]
    readonly_fields = ["id", "created_at", "updated_at", "started_at", "completed_at"]


@admin.register(AgentUsageLog)
class AgentUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        "agent_type",
        "llm_model",
        "input_tokens",
        "output_tokens",
        "success",
        "created_at",
    ]
    list_filter = ["agent_type", "success"]
    readonly_fields = [f.name for f in AgentUsageLog._meta.get_fields()]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AgentEventLog)
class AgentEventLogAdmin(admin.ModelAdmin):
    list_display = ["agent_type", "event_type", "tool_name", "tokens_used", "created_at"]
    list_filter = ["agent_type", "event_type"]
    readonly_fields = [f.name for f in AgentEventLog._meta.get_fields()]
