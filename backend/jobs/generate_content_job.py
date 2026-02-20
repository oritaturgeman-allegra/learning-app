"""
Scheduled job for generating newsletter content.

This job runs on a schedule (default: 5x daily) to pre-generate newsletter
content for all users. Podcast audio is generated on-demand per user request.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.config import config
from backend.defaults import NEWS_CATEGORIES
from backend.services.market_data_service import fetch_market_data_async
from backend.services.ai_content_service import AIContentService
from backend.services.db_service import get_db_service, DatabaseError
from backend.exceptions import FeedFetchError

logger = logging.getLogger(__name__)


class ContentGenerationJob:
    """
    Job for generating newsletter content on a schedule.

    This job:
    1. Fetches RSS feeds for all categories
    2. Generates AI-powered newsletter content (titles, sentiment)
    3. Saves newsletter to database

    Podcast dialog and audio are generated on-demand via POST /api/podcast/generate.
    """

    def __init__(self) -> None:
        """Initialize job with required services."""
        self._ai_content_service: Optional[AIContentService] = None

    def _get_ai_content_service(self) -> AIContentService:
        """Lazy initialization of AI content service."""
        if self._ai_content_service is None:
            self._ai_content_service = AIContentService()
        return self._ai_content_service

    def run(self) -> Dict[str, Any]:
        """
        Run the content generation job synchronously.

        This is the main entry point called by the scheduler.
        It wraps the async execution in an event loop.

        Returns:
            Dict with job execution results
        """
        job_id = str(uuid.uuid4())[:8]
        logger.info(f"[{job_id}] Content generation job starting")

        try:
            # Run async job in a fresh event loop (asyncio.run handles
            # loop creation, execution, and cleanup safely across threads)
            result = asyncio.run(self._run_async(job_id))

            return result

        except Exception as e:
            logger.error(f"[{job_id}] Content generation job failed: {e}", exc_info=True)
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
            }

    async def run_async(self) -> Dict[str, Any]:
        """
        Run the content generation job asynchronously.

        Use this when calling from an async context (e.g., FastAPI routes).

        Returns:
            Dict with job execution results
        """
        job_id = str(uuid.uuid4())[:8]
        logger.info(f"[{job_id}] Content generation job starting (async)")

        try:
            return await self._run_async(job_id)
        except Exception as e:
            logger.error(f"[{job_id}] Content generation job failed: {e}", exc_info=True)
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
            }

    async def _run_async(self, job_id: str) -> Dict[str, Any]:
        """
        Async implementation of content generation.

        Args:
            job_id: Unique identifier for this job run

        Returns:
            Dict with job execution results
        """
        start_time = datetime.now(timezone.utc)
        result: Dict[str, Any] = {
            "job_id": job_id,
            "started_at": start_time.isoformat(),
            "categories": NEWS_CATEGORIES,
        }

        # Step 1: Fetch RSS feeds
        logger.info(f"[{job_id}] Fetching RSS feeds for all categories")
        try:
            data = await fetch_market_data_async(categories=NEWS_CATEGORIES)
            article_counts = {
                "us": len(data.get("raw_us_market_news", [])),
                "israel": len(data.get("raw_israel_market_news", [])),
                "ai": len(data.get("raw_ai_news", [])),
                "crypto": len(data.get("raw_crypto_news", [])),
            }
            result["article_counts"] = article_counts
            logger.info(f"[{job_id}] Fetched articles: {article_counts}")
        except FeedFetchError as e:
            logger.error(f"[{job_id}] Failed to fetch RSS feeds: {e}")
            result["success"] = False
            result["error"] = f"RSS fetch failed: {e}"
            return result

        # Step 2: Generate AI content
        logger.info(f"[{job_id}] Generating AI content (LLM: {config.llm_provider})")
        try:
            ai_service = self._get_ai_content_service()
            sources_metadata = {
                cat: data["articles_metadata"].get(cat, []) for cat in NEWS_CATEGORIES
            }

            newsletter_content = ai_service.generate_newsletter_content(sources_metadata)
            sources_metadata = ai_service.apply_content_to_metadata(
                sources_metadata, newsletter_content
            )

            # Extract sentiment scores
            raw_sentiment = newsletter_content.get("sentiment", {})
            sentiment = {
                cat: score for cat, score in raw_sentiment.items() if sources_metadata.get(cat)
            }

            result["sentiment"] = sentiment
            logger.info(f"[{job_id}] Generated AI content with sentiment: {sentiment}")
        except Exception as e:
            logger.error(f"[{job_id}] Failed to generate AI content: {e}")
            result["success"] = False
            result["error"] = f"AI content generation failed: {e}"
            return result

        # Get source stats and selection records for database
        source_stats = data.get("source_stats", {cat: [] for cat in NEWS_CATEGORIES})
        selection_records = data.get("selection_records", [])

        # Step 3: Save to database
        logger.info(f"[{job_id}] Saving to database")
        try:
            db_service = get_db_service()
            db_service.update_feed_providers(source_stats)
            db_service.save_newsletter_with_stats(
                source_stats=source_stats,
                sources_metadata=sources_metadata,
                language="en",
                sentiment=json.dumps(sentiment),
                llm_provider=config.llm_provider,
                user_id=None,  # Scheduled job, not user-specific
            )
            # Save article selection records for analytics
            if selection_records:
                saved_count = db_service.save_article_selections(selection_records)
                logger.info(f"[{job_id}] Saved {saved_count} article selection records")
            result["saved_to_db"] = True
            logger.info(f"[{job_id}] Saved to database")
        except DatabaseError as e:
            logger.warning(f"[{job_id}] Failed to save to database: {e}")
            result["saved_to_db"] = False

        # Finalize result
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        result["success"] = True
        result["completed_at"] = end_time.isoformat()
        result["duration_seconds"] = round(duration, 2)

        logger.info(
            f"[{job_id}] Content generation completed in {duration:.2f}s - "
            f"articles={sum(article_counts.values())}, "
            f"db={result.get('saved_to_db')}"
        )

        return result


# Singleton instance
_job_instance: Optional[ContentGenerationJob] = None


def get_content_generation_job() -> ContentGenerationJob:
    """Get or create the content generation job singleton."""
    global _job_instance
    if _job_instance is None:
        _job_instance = ContentGenerationJob()
    return _job_instance


def run_content_generation() -> Dict[str, Any]:
    """
    Entry point for scheduler to run content generation.

    This function is called by the scheduler service.

    Returns:
        Dict with job execution results
    """
    job = get_content_generation_job()
    return job.run()


async def run_content_generation_async() -> Dict[str, Any]:
    """
    Async entry point for content generation.

    Use this when calling from an async context (e.g., FastAPI routes).

    Returns:
        Dict with job execution results
    """
    job = get_content_generation_job()
    return await job.run_async()
