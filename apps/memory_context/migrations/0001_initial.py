import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MemoryBlock",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("tier", models.CharField(
                    choices=[
                        ("platform", "Platform (Tier 1)"),
                        ("project", "Project (Tier 2)"),
                        ("session", "Session (Tier 3)"),
                    ],
                    max_length=20,
                )),
                ("ref_id", models.UUIDField(blank=True, null=True)),
                ("block_type", models.CharField(max_length=100)),
                ("title", models.CharField(max_length=255)),
                ("content", models.JSONField()),
                ("content_text", models.TextField(blank=True)),
                ("token_estimate", models.PositiveIntegerField(default=0)),
                ("source", models.CharField(blank=True, default="system", max_length=100)),
                ("priority", models.PositiveIntegerField(default=5)),
                ("uri", models.CharField(blank=True, max_length=500)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["tier", "priority", "-created_at"],
                "indexes": [
                    models.Index(fields=["tier", "ref_id"], name="mem_ctx_tier_ref_idx"),
                    models.Index(fields=["tier", "ref_id", "block_type"], name="mem_ctx_tier_ref_type_idx"),
                    models.Index(fields=["tier", "is_active", "priority"], name="mem_ctx_tier_active_prio_idx"),
                ],
            },
        ),
    ]
