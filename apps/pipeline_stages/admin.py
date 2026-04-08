from django.contrib import admin

from apps.pipeline_stages.models import (
    PipelineDefinition,
    PipelineInstance,
    StageDefinition,
    StageInstance,
)


@admin.register(PipelineDefinition)
class PipelineDefinitionAdmin(admin.ModelAdmin):
    list_display = ["code", "label", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["code", "label"]


@admin.register(StageDefinition)
class StageDefinitionAdmin(admin.ModelAdmin):
    list_display = ["pipeline", "code", "label", "order", "requires_human_approval", "is_hard_gate"]
    list_filter = ["pipeline", "requires_human_approval", "is_hard_gate"]


@admin.register(PipelineInstance)
class PipelineInstanceAdmin(admin.ModelAdmin):
    list_display = ["id", "pipeline", "object_type", "object_id", "is_complete", "created_at"]
    list_filter = ["pipeline", "is_complete"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(StageInstance)
class StageInstanceAdmin(admin.ModelAdmin):
    list_display = ["pipeline_instance", "stage_definition", "status", "started_at", "completed_at"]
    list_filter = ["status", "stage_definition__pipeline"]
    readonly_fields = ["started_at", "completed_at", "approved_at"]
