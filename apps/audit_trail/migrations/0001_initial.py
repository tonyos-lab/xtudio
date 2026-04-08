import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("actor", models.CharField(default="system", max_length=100)),
                ("category", models.CharField(max_length=100)),
                ("operation", models.CharField(max_length=100)),
                ("action", models.TextField()),
                ("project_id", models.UUIDField(blank=True, null=True)),
                ("sprint_id", models.UUIDField(blank=True, null=True)),
                ("stage", models.CharField(blank=True, max_length=100)),
                ("object_type", models.CharField(blank=True, max_length=100)),
                ("object_id", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(
                    choices=[("success", "Success"), ("failure", "Failure"), ("warning", "Warning")],
                    default="success",
                    max_length=20,
                )),
                ("error_message", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="audit_logs",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["user", "created_at"], name="audit_trail_user_idx"),
                    models.Index(fields=["category", "operation"], name="audit_trail_cat_op_idx"),
                    models.Index(fields=["project_id", "created_at"], name="audit_trail_proj_idx"),
                    models.Index(fields=["status", "created_at"], name="audit_trail_status_idx"),
                ],
            },
        ),
    ]
