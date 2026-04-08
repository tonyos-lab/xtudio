import uuid

from django.conf import settings
from django.db import models


class Document(models.Model):
    SOURCE_UPLOAD = "upload"
    SOURCE_AGENT = "agent"
    SOURCE_SYSTEM = "system"

    SOURCE_CHOICES = [
        ("upload", "User Upload"),
        ("agent", "Agent Generated"),
        ("system", "System Generated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20)
    file_size = models.PositiveIntegerField(default=0)
    file_path = models.CharField(max_length=500)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="upload")
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "source"]),
            models.Index(fields=["project", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.filename
