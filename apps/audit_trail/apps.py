from django.apps import AppConfig


class AuditTrailConfig(AppConfig):
    name = "apps.audit_trail"
    label = "audit_trail"
    verbose_name = "Audit Trail"
    default_auto_field = "django.db.models.BigAutoField"
