"""
Scheduler service for scheduled content generation.

Uses APScheduler to run content generation jobs at configured UTC times.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED, EVENT_JOB_EXECUTED
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.config import config

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Service for managing scheduled content generation jobs.

    Runs content generation at configured UTC hours using APScheduler.
    """

    def __init__(self) -> None:
        """Initialize the scheduler service."""
        self._scheduler: BackgroundScheduler | None = None
        self._is_running: bool = False

    def start(self) -> None:
        """
        Start the scheduler and register jobs.

        Only starts if schedule_enabled is True in config.
        """
        if not config.schedule_enabled:
            logger.info("Scheduler disabled via config (SCHEDULE_ENABLED=false)")
            return

        if self._is_running:
            logger.warning("Scheduler already running")
            return

        # Configure with explicit executor to ensure reliable scheduling
        executors = {
            "default": ThreadPoolExecutor(max_workers=3),
        }
        job_defaults = {
            "coalesce": True,  # Combine multiple missed runs into one
            "max_instances": 1,  # Only one instance of each job at a time
        }
        self._scheduler = BackgroundScheduler(
            timezone=config.schedule_timezone,
            executors=executors,
            job_defaults=job_defaults,
        )

        # Register content generation job for each configured hour
        for hour in config.schedule_hours_utc:
            trigger = CronTrigger(hour=hour, minute=0, timezone=config.schedule_timezone)
            self._scheduler.add_job(
                self._generate_content_job,
                trigger=trigger,
                id=f"content_generation_{hour:02d}",
                name=f"Content Generation at {hour:02d}:00 UTC",
                replace_existing=True,
                misfire_grace_time=config.schedule_misfire_grace_time,
            )
            logger.info(f"Scheduled content generation job at {hour:02d}:00 UTC")

        # Register analytics job at 08:00 UTC (10:00 AM Israel)
        analytics_trigger = CronTrigger(hour=8, minute=0, timezone=config.schedule_timezone)
        self._scheduler.add_job(
            self._analytics_job,
            trigger=analytics_trigger,
            id="analytics_08",
            name="Feed Analytics at 08:00 UTC",
            replace_existing=True,
            misfire_grace_time=config.schedule_misfire_grace_time,
        )
        logger.info("Scheduled analytics job at 08:00 UTC")

        # Add event listeners for job diagnostics
        self._scheduler.add_listener(self._on_job_executed, EVENT_JOB_EXECUTED)
        self._scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)
        self._scheduler.add_listener(self._on_job_missed, EVENT_JOB_MISSED)

        self._scheduler.start()
        self._is_running = True

        # Log all scheduled jobs
        jobs = self._scheduler.get_jobs()
        logger.info(
            f"Scheduler started with {len(jobs)} jobs: "
            f"{[f'{h:02d}:00 UTC' for h in config.schedule_hours_utc]}"
        )

    def shutdown(self) -> None:
        """Shut down the scheduler gracefully."""
        if self._scheduler and self._is_running:
            self._scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("Scheduler shut down")

    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._is_running

    def get_status(self) -> Dict[str, Any]:
        """
        Get scheduler status for health checks.

        Returns:
            Dict with scheduler status information
        """
        if not config.schedule_enabled:
            return {
                "status": "disabled",
                "enabled": False,
                "running": False,
                "jobs": [],
            }

        if not self._is_running or not self._scheduler:
            return {
                "status": "unhealthy",
                "enabled": config.schedule_enabled,
                "running": False,
                "jobs": [],
            }

        jobs = self._scheduler.get_jobs()
        return {
            "status": "healthy",
            "enabled": config.schedule_enabled,
            "running": self._is_running,
            "timezone": config.schedule_timezone,
            "scheduled_hours_utc": list(config.schedule_hours_utc),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                }
                for job in jobs
            ],
        }

    def trigger_now(self) -> bool:
        """
        Manually trigger content generation immediately.

        Returns:
            True if job was triggered, False if scheduler not running
        """
        if not self._is_running:
            logger.warning("Cannot trigger job: scheduler not running")
            return False

        logger.info("Manually triggering content generation")
        self._generate_content_job()
        return True

    @staticmethod
    def _on_job_executed(event: Any) -> None:
        """Log when a scheduled job executes successfully."""
        logger.info(f"Scheduler job executed: {event.job_id}")

    @staticmethod
    def _on_job_error(event: Any) -> None:
        """Log when a scheduled job raises an exception."""
        logger.error(
            f"Scheduler job error: {event.job_id} - {event.exception}",
            exc_info=event.exception,
        )

    @staticmethod
    def _on_job_missed(event: Any) -> None:
        """Log when a scheduled job is missed (past misfire_grace_time)."""
        logger.warning(f"Scheduler job MISSED: {event.job_id} at {event.scheduled_run_time}")

    def _generate_content_job(self) -> None:
        """
        Content generation job - fetches RSS, generates newsletter, creates podcast.

        This job runs on schedule and generates content for all users.
        """
        from backend.jobs.generate_content_job import run_content_generation

        job_start = datetime.now(timezone.utc)
        logger.info(f"Content generation job started at {job_start.isoformat()}")

        try:
            result = run_content_generation()

            if result.get("success"):
                logger.info(
                    f"Content generation completed: "
                    f"articles={sum(result.get('article_counts', {}).values())}, "
                    f"duration={result.get('duration_seconds')}s"
                )
            else:
                logger.error(f"Content generation failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"Content generation job failed: {e}", exc_info=True)

        finally:
            job_duration = (datetime.now(timezone.utc) - job_start).total_seconds()
            logger.info(f"Content generation job completed in {job_duration:.2f}s")

    def _analytics_job(self) -> None:
        """
        Analytics job - analyzes feed provider performance and sends email report.

        This job runs daily at 08:00 UTC (10:00 AM Israel).
        """
        from backend.jobs.analytics_job import run_analytics

        job_start = datetime.now(timezone.utc)
        logger.info(f"Analytics job started at {job_start.isoformat()}")

        try:
            result = run_analytics()

            if result.get("success"):
                logger.info(
                    f"Analytics completed: "
                    f"analysis={result.get('analysis_success')}, "
                    f"email={result.get('email_sent')}, "
                    f"duration={result.get('duration_seconds')}s"
                )
            else:
                logger.error(f"Analytics failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"Analytics job failed: {e}", exc_info=True)

        finally:
            job_duration = (datetime.now(timezone.utc) - job_start).total_seconds()
            logger.info(f"Analytics job completed in {job_duration:.2f}s")


# Singleton instance
_scheduler_service: SchedulerService | None = None


def get_scheduler_service() -> SchedulerService:
    """Get or create the scheduler service singleton."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
