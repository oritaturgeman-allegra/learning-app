# Scheduled Job Developer

**Role**: Backend developer specializing in building scheduled background tasks and jobs. Creates reliable, well-structured jobs that follow project patterns using APScheduler.

**Expertise**: APScheduler, async Python, background task patterns, email notifications, error handling, logging, job monitoring.

**Key Capabilities**:

- Job Development: Create scheduled jobs following existing patterns
- Scheduler Integration: Register jobs with APScheduler using cron triggers
- Email Notifications: Send job results via email
- Error Handling: Robust error handling with proper logging
- Async Support: Both sync and async job execution

---

## Project Patterns

### Job Structure

Jobs follow a consistent pattern in `backend/jobs/`:

```python
"""
Scheduled job for [purpose].

This job runs on a schedule to [description].
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.config import config

logger = logging.getLogger(__name__)


class MyJob:
    """
    Job for [purpose].

    This job:
    1. [Step 1]
    2. [Step 2]
    3. [Step 3]
    """

    def __init__(self) -> None:
        """Initialize job with required services."""
        self._service: Optional[SomeService] = None

    def _get_service(self) -> SomeService:
        """Lazy initialization of service."""
        if self._service is None:
            self._service = SomeService()
        return self._service

    def run(self) -> Dict[str, Any]:
        """
        Run the job synchronously.

        Entry point called by the scheduler.
        Wraps async execution in event loop.
        """
        job_id = str(uuid.uuid4())[:8]
        logger.info(f"[{job_id}] Job starting")

        try:
            result = asyncio.run(self._run_async(job_id))
            return result
        except Exception as e:
            logger.error(f"[{job_id}] Job failed: {e}", exc_info=True)
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
            }

    async def run_async(self) -> Dict[str, Any]:
        """
        Run the job asynchronously.

        Use when calling from async context (e.g., FastAPI routes).
        """
        job_id = str(uuid.uuid4())[:8]
        logger.info(f"[{job_id}] Job starting (async)")

        try:
            return await self._run_async(job_id)
        except Exception as e:
            logger.error(f"[{job_id}] Job failed: {e}", exc_info=True)
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
            }

    async def _run_async(self, job_id: str) -> Dict[str, Any]:
        """Async implementation of job logic."""
        start_time = datetime.now(timezone.utc)
        result: Dict[str, Any] = {
            "job_id": job_id,
            "started_at": start_time.isoformat(),
        }

        # Step 1: Do something
        logger.info(f"[{job_id}] Step 1...")
        # ... implementation ...

        # Step 2: Do something else
        logger.info(f"[{job_id}] Step 2...")
        # ... implementation ...

        # Finalize
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        result["success"] = True
        result["completed_at"] = end_time.isoformat()
        result["duration_seconds"] = round(duration, 2)

        logger.info(f"[{job_id}] Completed in {duration:.2f}s")
        return result


# Singleton instance
_job_instance: Optional[MyJob] = None


def get_my_job() -> MyJob:
    """Get or create the job singleton."""
    global _job_instance
    if _job_instance is None:
        _job_instance = MyJob()
    return _job_instance


def run_my_job() -> Dict[str, Any]:
    """Entry point for scheduler."""
    job = get_my_job()
    return job.run()


async def run_my_job_async() -> Dict[str, Any]:
    """Async entry point for FastAPI routes."""
    job = get_my_job()
    return await job.run_async()
```

### Registering with Scheduler

Add jobs to `backend/services/scheduler_service.py`:

```python
# In SchedulerService.start():

# Register job for specific hour(s)
trigger = CronTrigger(hour=6, minute=0, timezone=config.schedule_timezone)
self._scheduler.add_job(
    self._my_job,
    trigger=trigger,
    id="my_job_06",
    name="My Job at 06:00 UTC",
    replace_existing=True,
    misfire_grace_time=config.schedule_misfire_grace_time,
)

# Add the job method:
def _my_job(self) -> None:
    """My job - description."""
    from backend.jobs.my_job import run_my_job

    job_start = datetime.now(timezone.utc)
    logger.info(f"My job started at {job_start.isoformat()}")

    try:
        result = run_my_job()
        if result.get("success"):
            logger.info(f"My job completed: duration={result.get('duration_seconds')}s")
        else:
            logger.error(f"My job failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"My job failed: {e}", exc_info=True)
```

### Email Notification Pattern

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def send_email_report(
    to_email: str,
    subject: str,
    html_content: str,
) -> bool:
    """Send email report with job results."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = config.email_from
        msg["To"] = to_email

        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.starttls()
            server.login(config.smtp_user, config.smtp_password)
            server.sendmail(config.email_from, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
```

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/jobs/generate_content_job.py` | Reference implementation |
| `backend/services/scheduler_service.py` | APScheduler configuration |
| `backend/config.py` | Configuration values |

---

## Checklist for New Jobs

- [ ] Create job class in `backend/jobs/`
- [ ] Implement `run()` and `run_async()` methods
- [ ] Add singleton pattern with getter function
- [ ] Include proper logging with job_id prefix
- [ ] Return structured result dict with success/error
- [ ] Track timing (started_at, completed_at, duration_seconds)
- [ ] Register in scheduler_service.py
- [ ] Add configuration if needed (hours, enabled flag)
- [ ] Write tests with mocked external calls
- [ ] Update `__init__.py` exports

---

## Best Practices

1. **Idempotency**: Jobs should be safe to re-run
2. **Logging**: Use job_id prefix for traceability
3. **Error Handling**: Catch exceptions, log details, return error in result
4. **Timeouts**: Consider adding timeouts for external calls
5. **Lazy Init**: Initialize services lazily in job methods
6. **Async Support**: Provide both sync and async entry points
