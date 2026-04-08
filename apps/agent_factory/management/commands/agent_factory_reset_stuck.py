from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Reset stuck running agent-factory jobs back to pending"

    def add_arguments(self, parser):
        parser.add_argument("--timeout", type=int, default=30)

    def handle(self, *args, **options):
        from apps.agent_factory.queue import JobQueueService

        count = JobQueueService.reset_stuck(timeout_minutes=options["timeout"])
        self.stdout.write(self.style.SUCCESS(f"Reset {count} stuck job(s)."))
