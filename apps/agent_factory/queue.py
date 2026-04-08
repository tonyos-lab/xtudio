import logging

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger("agent_factory")


class JobQueueService:
    @staticmethod
    def enqueue(
        agent_type: str,
        context: dict,
        priority: int = 5,
        object_type: str = "",
        object_id: str = "",
        metadata: dict | None = None,
    ):
        """Create a pending JobQueue record."""
        from apps.agent_factory.models import JobQueue

        return JobQueue.objects.create(
            agent_type=agent_type,
            context=context,
            priority=priority,
            object_type=object_type,
            object_id=object_id,
            metadata=metadata or {},
        )

    @staticmethod
    def claim_next(worker_id: str):
        """Claim next pending job via SELECT FOR UPDATE SKIP LOCKED."""
        from apps.agent_factory.models import JobQueue

        with transaction.atomic():
            job = (
                JobQueue.objects.select_for_update(skip_locked=True)
                .filter(status=JobQueue.STATUS_PENDING)
                .order_by("priority", "created_at")
                .first()
            )
            if job is None:
                return None
            job.status = JobQueue.STATUS_RUNNING
            job.worker_id = worker_id
            job.started_at = timezone.now()
            job.save()
            return job

    @staticmethod
    def mark_running(job, worker_id: str) -> None:
        job.status = "running"
        job.worker_id = worker_id
        job.started_at = timezone.now()
        job.save(update_fields=["status", "worker_id", "started_at", "updated_at"])

    @staticmethod
    def mark_completed(job, result: dict) -> None:
        job.status = "completed"
        job.result = result
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "result", "completed_at", "updated_at"])

    @staticmethod
    def mark_failed(job, error: str) -> None:
        job.status = "failed"
        job.error_message = error
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "error_message", "completed_at", "updated_at"])

    @staticmethod
    def reset_stuck(timeout_minutes: int = 30) -> int:
        """Reset stuck running jobs back to pending."""
        from apps.agent_factory.models import JobQueue

        cutoff = timezone.now() - timezone.timedelta(minutes=timeout_minutes)
        return JobQueue.objects.filter(
            status=JobQueue.STATUS_RUNNING,
            started_at__lt=cutoff,
        ).update(status=JobQueue.STATUS_PENDING, worker_id="", started_at=None)

    @staticmethod
    def get_health() -> dict:
        """Return queue health counts."""
        from apps.agent_factory.models import JobQueue

        counts = {}
        for status in ["pending", "running", "completed", "failed"]:
            counts[status] = JobQueue.objects.filter(status=status).count()
        return counts
