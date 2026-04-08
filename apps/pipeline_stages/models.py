import uuid

from django.conf import settings
from django.db import models


class PipelineDefinition(models.Model):
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "pipeline_stages"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.label


class StageDefinition(models.Model):
    pipeline = models.ForeignKey(
        PipelineDefinition, on_delete=models.CASCADE, related_name="stages"
    )
    code = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    order = models.PositiveIntegerField()
    requires_human_approval = models.BooleanField(default=False)
    is_hard_gate = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        app_label = "pipeline_stages"
        unique_together = [["pipeline", "code"], ["pipeline", "order"]]
        ordering = ["pipeline", "order"]

    def __str__(self) -> str:
        return f"{self.pipeline.code} / {self.code}"


class PipelineInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pipeline = models.ForeignKey(PipelineDefinition, on_delete=models.PROTECT)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "pipeline_stages"
        unique_together = [["pipeline", "object_type", "object_id"]]
        indexes = [models.Index(fields=["object_type", "object_id"])]

    def __str__(self) -> str:
        return f"{self.pipeline.code} / {self.object_type}:{self.object_id}"


class StageInstance(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_AWAITING_APPROVAL = "awaiting_approval"
    STATUS_COMPLETE = "complete"
    STATUS_FAILED = "failed"
    STATUS_LOCKED = "locked"

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("awaiting_approval", "Awaiting Approval"),
        ("complete", "Complete"),
        ("failed", "Failed"),
        ("locked", "Locked"),
    ]

    pipeline_instance = models.ForeignKey(
        PipelineInstance, on_delete=models.CASCADE, related_name="stage_instances"
    )
    stage_definition = models.ForeignKey(StageDefinition, on_delete=models.PROTECT)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_stages",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = "pipeline_stages"
        unique_together = [["pipeline_instance", "stage_definition"]]
        ordering = ["stage_definition__order"]

    def __str__(self) -> str:
        return f"{self.stage_definition.code} — {self.status}"
