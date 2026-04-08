import signal
import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start agent-factory background worker pool"

    def add_arguments(self, parser):
        parser.add_argument("--pool-size", type=int, default=None)

    def handle(self, *args, **options):
        from django.conf import settings

        from apps.agent_factory.executor import _stop_event, start_executor

        pool_size = options["pool_size"] or getattr(settings, "AGENT_FACTORY_POOL_SIZE", 4)
        self.stdout.write(self.style.SUCCESS(f"Starting {pool_size} agent workers..."))
        start_executor(pool_size=pool_size)

        def shutdown(sig, frame):
            self.stdout.write("\nShutting down workers...")
            _stop_event.set()

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        while not _stop_event.is_set():
            time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Workers stopped."))
