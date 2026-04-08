import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # WHO
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    actor = models.CharField(max_length=100, default="system")  # 'user', 'system', 'agent'

    # WHAT
    category = models.CharField(max_length=100)  # 'PROJECT', 'AGENT', etc.
    operation = models.CharField(max_length=100)  # 'create', 'update', etc.
    action = models.TextField()  # human-readable description

    # WHERE
    project_id = models.UUIDField(null=True, blank=True)
    sprint_id = models.UUIDField(null=True, blank=True)
    stage = models.CharField(max_length=100, blank=True)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=255, blank=True)

    # RESULT
    status = models.CharField(
        max_length=20,
        choices=[
            ("success", "Success"),
            ("failure", "Failure"),
            ("warning", "Warning"),
        ],
        default="success",
    )
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # WHEN
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "audit_trail"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["category", "operation"]),
            models.Index(fields=["project_id", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError("AuditLog records are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("AuditLog records are immutable and cannot be deleted.")

    def __str__(self) -> str:
        return f"[{self.category}] {self.operation} — {self.status}"
