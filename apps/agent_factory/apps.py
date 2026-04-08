from django.apps import AppConfig


class AgentFactoryConfig(AppConfig):
    name = "apps.agent_factory"
    label = "agent_factory"
    verbose_name = "Agent Factory"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from django.conf import settings

        if getattr(settings, "AGENT_FACTORY_AUTO_START_WORKERS", False):
            from apps.agent_factory.executor import start_executor

            pool_size = getattr(settings, "AGENT_FACTORY_POOL_SIZE", 4)
            start_executor(pool_size=pool_size)
