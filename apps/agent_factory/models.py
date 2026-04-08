import uuid

from django.db import models


class AgentTemplate(models.Model):
    agent_type = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    llm_model = models.CharField(max_length=100, default="claude-sonnet-4-6")
    max_tokens = models.PositiveIntegerField(default=1000)
    max_turns = models.PositiveIntegerField(default=10)
    system_prompt = models.TextField()
    allowed_tools = models.JSONField(default=list)
    step_call_llm = models.BooleanField(default=True)
    step_use_mock_response = models.BooleanField(default=False)
    mock_response = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    is_sdk_loop = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "agent_factory"
        ordering = ["agent_type"]

    def __str__(self) -> str:
        return f"{self.agent_type} ({self.llm_model})"


class JobQueue(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_type = models.CharField(max_length=100)
    context = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.PositiveIntegerField(default=5)
    worker_id = models.CharField(max_length=100, blank=True)
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "agent_factory"
        ordering = ["priority", "created_at"]
        indexes = [
            models.Index(fields=["status", "priority", "created_at"]),
            models.Index(fields=["agent_type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.agent_type} [{self.status}]"


class AgentUsageLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_type = models.CharField(max_length=100)
    llm_model = models.CharField(max_length=100)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    cache_creation_tokens = models.PositiveIntegerField(default=0)
    cache_read_tokens = models.PositiveIntegerField(default=0)
    duration_ms = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    job_id = models.UUIDField(null=True, blank=True)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "agent_factory"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["agent_type", "created_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk and AgentUsageLog.objects.filter(pk=self.pk).exists():
            raise ValueError("AgentUsageLog records are immutable.")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.agent_type} — {self.input_tokens}+{self.output_tokens} tokens"


class AgentEventLog(models.Model):
    EVENT_CHOICES = [
        ("text", "Text"),
        ("tool_use", "Tool Use"),
        ("tool_result", "Tool Result"),
        ("thinking", "Thinking"),
        ("subagent_spawn", "Subagent Spawn"),
        ("subagent_result", "Subagent Result"),
        ("error", "Error"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_type = models.CharField(max_length=100)
    job = models.ForeignKey(
        JobQueue, null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    tool_name = models.CharField(max_length=100, blank=True)
    tool_input = models.JSONField(default=dict, blank=True)
    tool_result = models.JSONField(default=dict, blank=True)
    content = models.TextField(blank=True)
    thinking = models.TextField(blank=True)
    tokens_used = models.PositiveIntegerField(default=0)
    duration_ms = models.PositiveIntegerField(default=0)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "agent_factory"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["agent_type", "created_at"]),
            models.Index(fields=["job", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.agent_type} / {self.event_type}"
