import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AgentTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("agent_type", models.CharField(max_length=100, unique=True)),
                ("label", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("llm_model", models.CharField(default="claude-sonnet-4-6", max_length=100)),
                ("max_tokens", models.PositiveIntegerField(default=1000)),
                ("max_turns", models.PositiveIntegerField(default=10)),
                ("system_prompt", models.TextField()),
                ("allowed_tools", models.JSONField(default=list)),
                ("step_call_llm", models.BooleanField(default=True)),
                ("step_use_mock_response", models.BooleanField(default=False)),
                ("mock_response", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("is_sdk_loop", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["agent_type"]},
        ),
        migrations.CreateModel(
            name="JobQueue",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("agent_type", models.CharField(max_length=100)),
                ("context", models.JSONField(default=dict)),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Pending"),
                        ("running", "Running"),
                        ("completed", "Completed"),
                        ("failed", "Failed"),
                    ],
                    default="pending",
                    max_length=20,
                )),
                ("priority", models.PositiveIntegerField(default=5)),
                ("worker_id", models.CharField(blank=True, max_length=100)),
                ("result", models.JSONField(blank=True, default=dict)),
                ("error_message", models.TextField(blank=True)),
                ("object_type", models.CharField(blank=True, max_length=100)),
                ("object_id", models.CharField(blank=True, max_length=255)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ["priority", "created_at"],
                "indexes": [
                    models.Index(fields=["status", "priority", "created_at"], name="af_job_status_prio_idx"),
                    models.Index(fields=["agent_type", "status"], name="af_job_type_status_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="AgentUsageLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("agent_type", models.CharField(max_length=100)),
                ("llm_model", models.CharField(max_length=100)),
                ("input_tokens", models.PositiveIntegerField(default=0)),
                ("output_tokens", models.PositiveIntegerField(default=0)),
                ("cache_creation_tokens", models.PositiveIntegerField(default=0)),
                ("cache_read_tokens", models.PositiveIntegerField(default=0)),
                ("duration_ms", models.PositiveIntegerField(default=0)),
                ("success", models.BooleanField(default=True)),
                ("error_message", models.TextField(blank=True)),
                ("job_id", models.UUIDField(blank=True, null=True)),
                ("object_type", models.CharField(blank=True, max_length=100)),
                ("object_id", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["agent_type", "created_at"], name="af_usage_type_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="AgentEventLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("agent_type", models.CharField(max_length=100)),
                ("event_type", models.CharField(
                    choices=[
                        ("text", "Text"),
                        ("tool_use", "Tool Use"),
                        ("tool_result", "Tool Result"),
                        ("thinking", "Thinking"),
                        ("subagent_spawn", "Subagent Spawn"),
                        ("subagent_result", "Subagent Result"),
                        ("error", "Error"),
                    ],
                    max_length=30,
                )),
                ("tool_name", models.CharField(blank=True, max_length=100)),
                ("tool_input", models.JSONField(blank=True, default=dict)),
                ("tool_result", models.JSONField(blank=True, default=dict)),
                ("content", models.TextField(blank=True)),
                ("thinking", models.TextField(blank=True)),
                ("tokens_used", models.PositiveIntegerField(default=0)),
                ("duration_ms", models.PositiveIntegerField(default=0)),
                ("object_type", models.CharField(blank=True, max_length=100)),
                ("object_id", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("job", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="events",
                    to="agent_factory.jobqueue",
                )),
            ],
            options={
                "ordering": ["created_at"],
                "indexes": [
                    models.Index(fields=["agent_type", "created_at"], name="af_event_type_idx"),
                    models.Index(fields=["job", "created_at"], name="af_event_job_idx"),
                ],
            },
        ),
    ]
