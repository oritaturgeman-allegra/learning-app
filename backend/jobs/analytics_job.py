"""
Scheduled job for generating feed provider analytics.

This job runs daily at 08:00 UTC (10:00 AM Israel) to analyze
feed provider performance and send insights via email.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from backend.services.ai_analytics_service import get_analytics_service
from backend.services.db_service import get_db_service
from backend.services.email_service import get_email_service

logger = logging.getLogger(__name__)

# Latest report cached in memory for fast access
_latest_report: Optional[Dict[str, Any]] = None

# Default recipient for analytics reports
ANALYTICS_EMAIL = "yournewsletter.yourway@gmail.com"


class AnalyticsJob:
    """
    Job for analyzing feed provider performance daily.

    This job:
    1. Queries article selection data from yesterday
    2. Analyzes performance using LLM
    3. Sends insights via email
    """

    def __init__(self) -> None:
        """Initialize job with required services."""
        self._analytics_service = None
        self._email_service = None

    def _get_analytics_service(self):
        """Lazy initialization of analytics service."""
        if self._analytics_service is None:
            self._analytics_service = get_analytics_service()
        return self._analytics_service

    def _get_email_service(self):
        """Lazy initialization of email service."""
        if self._email_service is None:
            self._email_service = get_email_service()
        return self._email_service

    def run(self) -> Dict[str, Any]:
        """
        Run the analytics job synchronously.

        This is the main entry point called by the scheduler.
        It wraps the async execution in an event loop.

        Returns:
            Dict with job execution results
        """
        job_id = str(uuid.uuid4())[:8]
        logger.info(f"[{job_id}] Analytics job starting")

        try:
            result = asyncio.run(self._run_async(job_id))
            return result
        except Exception as e:
            logger.error(f"[{job_id}] Analytics job failed: {e}", exc_info=True)
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
            }

    async def run_async(self) -> Dict[str, Any]:
        """
        Run the analytics job asynchronously.

        Use this when calling from an async context (e.g., FastAPI routes).

        Returns:
            Dict with job execution results
        """
        job_id = str(uuid.uuid4())[:8]
        logger.info(f"[{job_id}] Analytics job starting (async)")

        try:
            return await self._run_async(job_id)
        except Exception as e:
            logger.error(f"[{job_id}] Analytics job failed: {e}", exc_info=True)
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
            }

    async def _run_async(self, job_id: str) -> Dict[str, Any]:
        """
        Async implementation of analytics job.

        Args:
            job_id: Unique identifier for this job run

        Returns:
            Dict with job execution results
        """
        start_time = datetime.now(timezone.utc)
        result: Dict[str, Any] = {
            "job_id": job_id,
            "started_at": start_time.isoformat(),
        }

        # Analyze yesterday's data
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        logger.info(f"[{job_id}] Analyzing feed providers for {yesterday.date()}")

        try:
            analytics_service = self._get_analytics_service()
            analysis = analytics_service.analyze_feed_providers(yesterday)

            if not analysis.get("success"):
                logger.warning(f"[{job_id}] Analysis returned no data: {analysis.get('error')}")
                result["analysis_success"] = False
                result["analysis_error"] = analysis.get("error", "Unknown error")
                # Don't send email if no data
                result["email_sent"] = False
                result["success"] = True  # Job succeeded, just no data
                return result

            result["analysis_success"] = True
            result["analysis_summary"] = analysis.get("summary", "")
            result["data"] = analysis.get("data", {})
            logger.info(f"[{job_id}] Analysis complete: {analysis.get('summary', '')[:100]}")

            # Save report for copy-to-clipboard page
            _save_report(analysis)

        except Exception as e:
            logger.error(f"[{job_id}] Analysis failed: {e}")
            result["success"] = False
            result["error"] = f"Analysis failed: {e}"
            return result

        # Send email report
        logger.info(f"[{job_id}] Sending analytics report to {ANALYTICS_EMAIL}")
        try:
            email_service = self._get_email_service()
            email_sent = await email_service.send_analytics_report(
                to_email=ANALYTICS_EMAIL,
                analysis=analysis,
            )
            result["email_sent"] = email_sent
            if email_sent:
                logger.info(f"[{job_id}] Analytics report sent to {ANALYTICS_EMAIL}")
            else:
                logger.warning(f"[{job_id}] Failed to send analytics report")
        except Exception as e:
            logger.error(f"[{job_id}] Email sending failed: {e}")
            result["email_sent"] = False
            result["email_error"] = str(e)

        # Finalize result
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        result["success"] = True
        result["completed_at"] = end_time.isoformat()
        result["duration_seconds"] = round(duration, 2)

        logger.info(
            f"[{job_id}] Analytics job completed in {duration:.2f}s - "
            f"analysis={result.get('analysis_success')}, "
            f"email={result.get('email_sent')}"
        )

        return result


# Singleton instance
_job_instance: Optional[AnalyticsJob] = None


def get_analytics_job() -> AnalyticsJob:
    """Get or create the analytics job singleton."""
    global _job_instance
    if _job_instance is None:
        _job_instance = AnalyticsJob()
    return _job_instance


def run_analytics() -> Dict[str, Any]:
    """
    Entry point for scheduler to run analytics.

    This function is called by the scheduler service.

    Returns:
        Dict with job execution results
    """
    job = get_analytics_job()
    return job.run()


async def run_analytics_async() -> Dict[str, Any]:
    """
    Async entry point for analytics.

    Use this when calling from an async context (e.g., FastAPI routes).

    Returns:
        Dict with job execution results
    """
    job = get_analytics_job()
    return await job.run_async()


def _save_report(analysis: Dict[str, Any]) -> None:
    """Save report to memory cache and database."""
    global _latest_report
    _latest_report = analysis
    try:
        report_date = analysis.get("date", "unknown")
        report_json = json.dumps(analysis, ensure_ascii=False)
        db = get_db_service()
        db.save_analytics_report(report_date, report_json)
        logger.info("Analytics report saved to database")
    except Exception as e:
        logger.warning(f"Failed to save report to database: {e}")


def get_latest_report() -> Optional[Dict[str, Any]]:
    """Get the latest analytics report (memory cache first, then DB fallback)."""
    global _latest_report
    if _latest_report is not None:
        return _latest_report
    try:
        db = get_db_service()
        report = db.get_latest_analytics_report()
        if report:
            _latest_report = report
            return _latest_report
    except Exception as e:
        logger.warning(f"Failed to read report from database: {e}")
    return None
