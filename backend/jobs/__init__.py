"""
Scheduled jobs for the Capital Market Newsletter application.
"""

from backend.jobs.generate_content_job import (
    ContentGenerationJob,
    get_content_generation_job,
    run_content_generation,
    run_content_generation_async,
)
from backend.jobs.analytics_job import (
    AnalyticsJob,
    get_analytics_job,
    get_latest_report,
    run_analytics,
    run_analytics_async,
)

__all__ = [
    "ContentGenerationJob",
    "get_content_generation_job",
    "run_content_generation",
    "run_content_generation_async",
    "AnalyticsJob",
    "get_analytics_job",
    "get_latest_report",
    "run_analytics",
    "run_analytics_async",
]
