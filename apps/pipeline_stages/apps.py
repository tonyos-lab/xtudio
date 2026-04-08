from django.apps import AppConfig


class PipelineStagesConfig(AppConfig):
    name = "apps.pipeline_stages"
    label = "pipeline_stages"
    verbose_name = "Pipeline Stages"
    default_auto_field = "django.db.models.BigAutoField"
