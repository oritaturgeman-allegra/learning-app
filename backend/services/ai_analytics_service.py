"""
AI Analytics Service - LLM-powered feed provider analysis.

This service analyzes feed provider performance data and generates
actionable insights using OpenAI.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from openai import OpenAI

from backend.config import config
from backend.prompts import ANALYTICS_SYSTEM_PROMPT, ANALYTICS_PROMPT_TEMPLATE
from backend.services.db_service import get_db_service

logger = logging.getLogger(__name__)


class AIAnalyticsService:
    """
    Service for generating AI-powered analytics on feed provider performance.

    Uses OpenAI directly (not config.llm_provider) to ensure consistent
    analytics quality.
    """

    def __init__(self) -> None:
        """Initialize the analytics service with OpenAI client."""
        self._client: Optional[OpenAI] = None
        self._model = config.openai_model or "gpt-4o-mini"
        logger.info(f"AIAnalyticsService initialized (model: {self._model})")

    def _get_client(self) -> OpenAI:
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            self._client = OpenAI(api_key=config.openai_api_key)
        return self._client

    def analyze_feed_providers(
        self,
        target_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Analyze feed provider performance for a specific date.

        Args:
            target_date: Date to analyze (defaults to yesterday)

        Returns:
            Dict with analysis results including summary, recommendations, etc.
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc) - timedelta(days=1)

        logger.info(f"Analyzing feed providers for {target_date.date()}")

        # Get data from database
        db_service = get_db_service()
        selection_summary = db_service.get_selection_summary_for_date(target_date)
        lifetime_stats = db_service.get_feed_provider_stats()

        # Check if we have data
        if selection_summary["total_articles"] == 0:
            logger.warning(f"No article selection data for {target_date.date()}")
            return {
                "success": False,
                "error": "No data available for the specified date",
                "date": target_date.date().isoformat(),
            }

        # Build the prompt
        prompt = self._build_prompt(selection_summary, lifetime_stats)

        # Call OpenAI
        try:
            analysis = self._call_llm(prompt)
            analysis["success"] = True
            analysis["date"] = target_date.date().isoformat()
            analysis["data"] = {
                "total_articles": selection_summary["total_articles"],
                "total_selected": selection_summary["total_selected"],
                "acceptance_rate": (
                    round(
                        selection_summary["total_selected"] / selection_summary["total_articles"],
                        2,
                    )
                    if selection_summary["total_articles"] > 0
                    else 0
                ),
            }
            return analysis
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "date": target_date.date().isoformat(),
            }

    def _build_prompt(
        self,
        selection_summary: Dict[str, Any],
        lifetime_stats: list,
    ) -> str:
        """Build the analysis prompt with data."""
        # Format source performance
        source_lines = []
        for source in selection_summary.get("by_source", []):
            rate = source["acceptance_rate"] * 100
            status = "✓" if rate >= 50 else "⚠️" if rate >= 25 else "❌"
            rejected_sample = ""
            if source.get("rejected_titles"):
                rejected_sample = f" | Sample rejected: '{source['rejected_titles'][0][:50]}...'"
            source_lines.append(
                f"{status} {source['source_name']} ({source['category']}): "
                f"{source['selected']}/{source['total']} selected ({rate:.0f}%){rejected_sample}"
            )
        source_performance = "\n".join(source_lines) if source_lines else "No source data"

        # Format category performance
        cat_lines = []
        for cat, stats in selection_summary.get("by_category", {}).items():
            rate = stats["acceptance_rate"] * 100
            cat_lines.append(f"- {cat}: {stats['selected']}/{stats['total']} ({rate:.0f}%)")
        category_performance = "\n".join(cat_lines) if cat_lines else "No category data"

        # Format lifetime stats
        lifetime_lines = []
        for provider in lifetime_stats[:20]:  # Top 20 providers
            rel = provider["reliability"] * 100
            lifetime_lines.append(
                f"- {provider['source_name']} ({provider['category']}): "
                f"{rel:.0f}% reliability over {provider['total_runs']} runs"
            )
        lifetime_stats_str = "\n".join(lifetime_lines) if lifetime_lines else "No lifetime data"

        # Calculate acceptance rate
        total = selection_summary["total_articles"]
        selected = selection_summary["total_selected"]
        acceptance_rate = selected / total if total > 0 else 0

        return ANALYTICS_PROMPT_TEMPLATE.format(
            date=selection_summary["date"],
            total_articles=total,
            total_selected=selected,
            acceptance_rate=acceptance_rate,
            source_performance=source_performance,
            category_performance=category_performance,
            lifetime_stats=lifetime_stats_str,
        )

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI and parse the response."""
        client = self._get_client()

        logger.info(f"Sending analytics request to OpenAI (prompt length: {len(prompt)})")

        response = client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": ANALYTICS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1500,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        logger.info(f"OpenAI response received (length: {len(content)})")

        # Parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Return a fallback structure
            return {
                "summary": "Analysis completed but response format was invalid.",
                "highlights": [],
                "action_items": [
                    {
                        "priority": "high",
                        "action": "Review raw LLM response — JSON parsing failed",
                        "source": None,
                        "category": None,
                        "reason": str(e),
                    }
                ],
                "raw_response": content[:500],
            }


# Singleton instance
_analytics_service: Optional[AIAnalyticsService] = None


def get_analytics_service() -> AIAnalyticsService:
    """Get or create the analytics service singleton."""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AIAnalyticsService()
    return _analytics_service
