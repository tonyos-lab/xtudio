from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run agent-factory health check"

    def handle(self, *args, **options):
        from apps.agent_factory.factory import AgentFactory
        from apps.agent_factory.queue import JobQueueService

        result = AgentFactory.health_check()
        queue = JobQueueService.get_health()

        if result["healthy"]:
            self.stdout.write(self.style.SUCCESS("agent-factory: healthy ✓"))
        else:
            self.stdout.write(self.style.ERROR("agent-factory: unhealthy ✗"))
            for issue in result["issues"]:
                self.stdout.write(self.style.ERROR(f"  - {issue}"))

        self.stdout.write(
            f"\nQueue: pending={queue['pending']} running={queue['running']} "
            f"failed={queue['failed']} completed={queue['completed']}"
        )
