import uuid

from django.db import models


class MemoryBlock(models.Model):
    TIER_CHOICES = [
        ("platform", "Platform (Tier 1)"),
        ("project", "Project (Tier 2)"),
        ("session", "Session (Tier 3)"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Scope
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    ref_id = models.UUIDField(null=True, blank=True)  # project_id or session_id

    # Identity
    block_type = models.CharField(max_length=100)  # 'architecture', 'agent_output'
    title = models.CharField(max_length=255)

    # Content
    content = models.JSONField()
    content_text = models.TextField(blank=True)  # plain text for token estimation
    token_estimate = models.PositiveIntegerField(default=0)

    # Metadata
    source = models.CharField(max_length=100, blank=True, default="system")
    priority = models.PositiveIntegerField(default=5)  # 1=highest, 10=lowest
    uri = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "memory_context"
        ordering = ["tier", "priority", "-created_at"]
        indexes = [
            models.Index(fields=["tier", "ref_id"]),
            models.Index(fields=["tier", "ref_id", "block_type"]),
            models.Index(fields=["tier", "is_active", "priority"]),
        ]

    def __str__(self) -> str:
        return f"[{self.tier}] {self.title}"
