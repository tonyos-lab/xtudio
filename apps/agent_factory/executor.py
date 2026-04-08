import atexit
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("agent_factory")

_executor: ThreadPoolExecutor | None = None
_started = False
_lock = threading.Lock()
_stop_event = threading.Event()


def start_executor(pool_size: int = 4) -> None:
    global _executor, _started
    with _lock:
        if _started:
            return
        _stop_event.clear()
        _executor = ThreadPoolExecutor(max_workers=pool_size + 1, thread_name_prefix="xtudio-agent")
        for i in range(pool_size):
            _executor.submit(_worker_loop, f"worker-{i}")
        _executor.submit(_maintenance_loop)
        _started = True
        logger.info("agent_factory executor started with %d workers", pool_size)
    atexit.register(_shutdown_executor)


def _shutdown_executor():
    global _started
    _stop_event.set()
    if _executor is not None:
        _executor.shutdown(wait=False, cancel_futures=True)
    _started = False


def _worker_loop(worker_name: str) -> None:
    from django.db import close_old_connections

    from apps.agent_factory.factory import AgentFactory
    from apps.agent_factory.queue import JobQueueService

    logger.info("Worker %s started", worker_name)
    while not _stop_event.is_set():
        try:
            job = JobQueueService.claim_next(worker_name)
            if job is None:
                close_old_connections()
                _stop_event.wait(2)
                continue
            logger.info("%s: processing job %s (%s)", worker_name, job.id, job.agent_type)
            try:
                result = AgentFactory.run_agent(job.agent_type, job.context)
                JobQueueService.mark_completed(job, result or {})
                logger.info("%s: job %s completed", worker_name, job.id)
            except Exception as exc:
                logger.exception("%s: job %s failed: %s", worker_name, job.id, exc)
                JobQueueService.mark_failed(job, str(exc))
            finally:
                close_old_connections()
        except Exception as exc:
            logger.error("%s: unexpected error: %s", worker_name, exc)
            _stop_event.wait(5)


def _maintenance_loop() -> None:
    from django.db import close_old_connections

    from apps.agent_factory.queue import JobQueueService

    while not _stop_event.is_set():
        _stop_event.wait(60)
        if _stop_event.is_set():
            break
        try:
            reset_count = JobQueueService.reset_stuck()
            if reset_count:
                logger.info("Maintenance: reset %d stuck jobs", reset_count)
        except Exception as exc:
            logger.warning("Maintenance loop error: %s", exc)
        finally:
            close_old_connections()
