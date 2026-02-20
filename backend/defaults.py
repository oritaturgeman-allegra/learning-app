"""
Static defaults and constants for services.
"""

from typing import Dict, List, Any

# News categories used across the application
NEWS_CATEGORIES: List[str] = ["us", "israel", "ai", "crypto", "space", "infrastructure", "energy"]

# Category display labels for newsletter formatting
CATEGORY_LABELS: Dict[str, str] = {
    "us": "US MARKET",
    "israel": "ISRAEL MARKET",
    "ai": "AI INDUSTRY",
    "crypto": "CRYPTO",
    "space": "SPACE",
    "infrastructure": "INFRASTRUCTURE",
    "energy": "ENERGY",
}

# Category to input count key mapping (for cache filtering)
CATEGORY_TO_COUNT_KEY: Dict[str, str] = {
    "us": "us_news",
    "israel": "israel_news",
    "ai": "ai_news",
    "crypto": "crypto_news",
    "space": "space_news",
    "infrastructure": "infrastructure_news",
    "energy": "energy_news",
}

# Newsletter structure keys
NEWSLETTER_SECTION_KEYS: List[str] = ["data", "input_counts", "source_stats"]

# Empty newsletter response (fallback)
EMPTY_NEWSLETTER_CONTENT: Dict[str, Any] = {
    "ai_titles": {},
}

# Podcast host configuration
PODCAST_HOSTS = {
    "female": "Alex",
    "male": "Guy",
}

# Podcast generation limits
PODCAST_DAILY_LIMIT: int = 2  # Max podcast generations per user per UTC day

# Task status values for TTS service
TASK_STATUS = {
    "STARTING": "starting",
    "GENERATING": "generating",
    "MERGING": "merging",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELLED": "cancelled",
}

# SSE response headers
SSE_HEADERS: Dict[str, str] = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}

# HTTP headers for RSS feed fetching
RSS_FETCH_HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

# App version (single source of truth)
APP_VERSION = "1.1.0"

# Recent changelog entries (shown in "What's New" popup)
# Keep only the 3 most recent entries. Each entry: (version, description)
APP_CHANGELOG: List[Dict[str, str]] = [
    {
        "version": "1.1.0",
        "text": "Your progress is saved! Stars and game results now persist in the database",
    },
    {
        "version": "1.0.0",
        "text": "Ariel's English Adventure — 4 fun learning games with stars, sounds, and animations",
    },
]

# App metadata
APP_METADATA = {
    "title": "Ariel's English Adventure",
    "description": "Gamified English learning for kids",
    "version": APP_VERSION,
}

# Legacy field mappings for backwards compatibility
LEGACY_FIELD_MAPPINGS: Dict[str, str] = {}

# Fields to remove from legacy responses
LEGACY_BULLET_FIELDS = ["us_bullets", "israel_bullets", "ai_bullets", "crypto_bullets"]


def generate_podcast_cache_key(categories: List[str]) -> str:
    """Generate date-based cache key for podcast sharing across users.

    This key enables podcast caching optimization where users with the same
    category selections on the same UTC day share the same cached podcast.
    This reduces API costs by ~97% (max 16 podcasts/day vs unlimited).

    Args:
        categories: List of categories to include (e.g., ["us", "israel"])

    Returns:
        Human-readable cache key: podcast_YYYY-MM-DD_category1_category2
    """
    from datetime import datetime, timezone

    utc_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cat_suffix = "_".join(sorted(categories))
    return f"podcast_{utc_date}_{cat_suffix}"
