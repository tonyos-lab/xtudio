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
            name="PipelineDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=100, unique=True)),
                ("label", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["code"]},
        ),
        migrations.CreateModel(
            name="StageDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=100)),
                ("label", models.CharField(max_length=200)),
                ("order", models.PositiveIntegerField()),
                ("requires_human_approval", models.BooleanField(default=False)),
                ("is_hard_gate", models.BooleanField(default=True)),
                ("description", models.TextField(blank=True)),
                ("pipeline", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="stages",
                    to="pipeline_stages.pipelinedefinition",
                )),
            ],
            options={"ordering": ["pipeline", "order"]},
        ),
        migrations.CreateModel(
            name="PipelineInstance",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("object_type", models.CharField(max_length=100)),
                ("object_id", models.CharField(max_length=255)),
                ("is_complete", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("pipeline", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to="pipeline_stages.pipelinedefinition",
                )),
            ],
            options={
                "indexes": [
                    models.Index(fields=["object_type", "object_id"], name="pipeline_inst_obj_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="StageInstance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Pending"),
                        ("running", "Running"),
                        ("awaiting_approval", "Awaiting Approval"),
                        ("complete", "Complete"),
                        ("failed", "Failed"),
                        ("locked", "Locked"),
                    ],
                    default="pending",
                    max_length=30,
                )),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("pipeline_instance", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="stage_instances",
                    to="pipeline_stages.pipelineinstance",
                )),
                ("stage_definition", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to="pipeline_stages.stagedefinition",
                )),
                ("approved_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="approved_stages",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["stage_definition__order"]},
        ),
        migrations.AddConstraint(
            model_name="stagedefinition",
            constraint=models.UniqueConstraint(
                fields=["pipeline", "code"], name="pipeline_stages_stage_def_pipeline_code_uniq"
            ),
        ),
        migrations.AddConstraint(
            model_name="stagedefinition",
            constraint=models.UniqueConstraint(
                fields=["pipeline", "order"], name="pipeline_stages_stage_def_pipeline_order_uniq"
            ),
        ),
        migrations.AddConstraint(
            model_name="pipelineinstance",
            constraint=models.UniqueConstraint(
                fields=["pipeline", "object_type", "object_id"],
                name="pipeline_inst_unique",
            ),
        ),
        migrations.AddConstraint(
            model_name="stageinstance",
            constraint=models.UniqueConstraint(
                fields=["pipeline_instance", "stage_definition"],
                name="stage_inst_unique",
            ),
        ),
    ]
