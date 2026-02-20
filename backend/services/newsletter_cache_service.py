"""Newsletter caching service with memory + file persistence."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from cachetools import TTLCache

from backend.defaults import (
    CATEGORY_TO_COUNT_KEY,
    NEWSLETTER_SECTION_KEYS,
)
from backend.logging_config import get_logger

logger = get_logger(__name__)

_memory_cache: TTLCache = TTLCache(maxsize=100, ttl=3600)


class NewsletterCacheService:
    """Newsletter API response cache."""

    def __init__(self, cache_dir: str = "newsletter_cache", cache_minutes: int = 60):
        global _memory_cache

        cache_path = Path(cache_dir)
        if not cache_path.is_absolute():
            cache_path = Path.cwd() / cache_dir

        self.cache_dir = cache_path.resolve()
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.cache_minutes = cache_minutes

        _memory_cache = TTLCache(maxsize=100, ttl=cache_minutes * 60)

    def _get_categories_key(self, categories: List[str]) -> str:
        """Generate a consistent key suffix from categories."""
        return "_".join(sorted(categories))

    def _get_cache_key(self, categories: List[str]) -> str:
        cat_key = self._get_categories_key(categories)
        return f"newsletter_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{cat_key}"

    def _get_latest_cache_file(self, categories: List[str]) -> Optional[Path]:
        """Find most recent cache file for today with exact category match."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        cat_key = self._get_categories_key(categories)
        # Pattern: newsletter_YYYY-MM-DD_HHMMSS_cat1_cat2.json
        # Use [0-9] pattern for timestamp to avoid matching extra underscores
        pattern = f"newsletter_{today_str}_[0-9][0-9][0-9][0-9][0-9][0-9]_{cat_key}.json"
        today_files = list(self.cache_dir.glob(pattern))
        return max(today_files, key=lambda f: f.stat().st_mtime) if today_files else None

    def _find_superset_cache(self, requested_categories: List[str]) -> Optional[Dict]:
        """Find a valid cached superset that contains all requested categories."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        requested_set = set(requested_categories)
        today_files = sorted(
            self.cache_dir.glob(f"newsletter_{today_str}_*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )

        for cache_file in today_files:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)

                created_at = datetime.fromisoformat(cached_data["cache_metadata"]["created_at"])
                if datetime.now() > created_at + timedelta(minutes=self.cache_minutes):
                    continue

                cached_categories = set(cached_data["cache_metadata"].get("categories", []))
                if requested_set.issubset(cached_categories):
                    logger.info(f"Found superset cache {cached_categories} for {requested_set}")
                    return self._filter_cache_to_categories(cached_data, requested_categories)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

        return None

    def _filter_cache_to_categories(self, cached_data: Dict, categories: List[str]) -> Dict:
        """Filter cached data to only include the requested categories."""
        filtered_data = {
            "newsletter": {},
            "cache_metadata": cached_data["cache_metadata"].copy(),
        }

        newsletter = cached_data["newsletter"]
        filtered_newsletter = filtered_data["newsletter"]

        # Copy non-category-specific fields
        for key in NEWSLETTER_SECTION_KEYS:
            if key in newsletter:
                filtered_newsletter[key] = {}

        # Filter the data section
        if "data" in newsletter:
            data = newsletter["data"]
            filtered_data_section = {}

            # Filter sources_metadata by category
            if "sources_metadata" in data:
                filtered_data_section["sources_metadata"] = {
                    cat: data["sources_metadata"].get(cat, []) for cat in categories
                }

            # Filter sentiment by category
            if "sentiment" in data:
                filtered_data_section["sentiment"] = {
                    cat: data["sentiment"].get(cat)
                    for cat in categories
                    if data["sentiment"].get(cat) is not None
                }

            filtered_newsletter["data"] = filtered_data_section

        # Filter input_counts
        if "input_counts" in newsletter:
            filtered_newsletter["input_counts"] = {
                CATEGORY_TO_COUNT_KEY[cat]: newsletter["input_counts"].get(
                    CATEGORY_TO_COUNT_KEY[cat], 0
                )
                for cat in categories
                if cat in CATEGORY_TO_COUNT_KEY
            }

        # Filter source_stats
        if "source_stats" in newsletter:
            filtered_newsletter["source_stats"] = {
                cat: newsletter["source_stats"].get(cat, []) for cat in categories
            }

        # Update metadata to reflect filtered categories
        filtered_data["cache_metadata"]["categories"] = categories
        filtered_data["cache_metadata"]["filtered_from_superset"] = True

        return filtered_data

    def get_cached_newsletter(self, categories: List[str]) -> Optional[Dict]:
        """Get cached newsletter if valid, checking memory, exact file match, then superset."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        cat_key = self._get_categories_key(categories)
        memory_cache_key = f"latest_{today_str}_{cat_key}"

        # 1. Check memory cache for exact match
        if memory_cache_key in _memory_cache:
            cached_data = _memory_cache[memory_cache_key]
            try:
                created_at = datetime.fromisoformat(cached_data["cache_metadata"]["created_at"])
                if datetime.now() <= created_at + timedelta(minutes=self.cache_minutes):
                    logger.info(f"Cache hit (memory) for categories {categories}")
                    return cached_data
                del _memory_cache[memory_cache_key]
            except (KeyError, ValueError):
                del _memory_cache[memory_cache_key]

        # 2. Check file cache for exact match
        cache_file = self._get_latest_cache_file(categories)
        if cache_file is not None:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)

                created_at = datetime.fromisoformat(cached_data["cache_metadata"]["created_at"])
                if datetime.now() <= created_at + timedelta(minutes=self.cache_minutes):
                    _memory_cache[memory_cache_key] = cached_data
                    logger.info(f"Cache hit (file) for categories {categories}")
                    return cached_data
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        # 3. Try to find a superset cache and filter it
        superset_cache = self._find_superset_cache(categories)
        if superset_cache is not None:
            logger.info(f"Cache hit (superset) for categories {categories}")
            return superset_cache

        return None

    def save_to_cache(self, newsletter_data: Dict, categories: List[str]) -> None:
        """Save newsletter to memory and file cache."""
        file_cache_key = self._get_cache_key(categories)
        cache_file = self.cache_dir / f"{file_cache_key}.json"

        today_str = datetime.now().strftime("%Y-%m-%d")
        cat_key = self._get_categories_key(categories)
        memory_cache_key = f"latest_{today_str}_{cat_key}"

        cache_data = {
            "newsletter": newsletter_data,
            "cache_metadata": {
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=self.cache_minutes)).isoformat(),
                "cache_duration_minutes": self.cache_minutes,
                "categories": categories,
            },
        }

        _memory_cache[memory_cache_key] = cache_data
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    def clear_memory_cache(self) -> None:
        global _memory_cache
        _memory_cache.clear()

    def cleanup_expired_cache(self) -> int:
        """Remove expired cache files."""
        removed = 0
        for cache_file in self.cache_dir.glob("newsletter_*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                created_at = datetime.fromisoformat(cached_data["cache_metadata"]["created_at"])
                if datetime.now() > created_at + timedelta(minutes=self.cache_minutes):
                    cache_file.unlink()
                    removed += 1
            except (json.JSONDecodeError, KeyError, ValueError):
                cache_file.unlink(missing_ok=True)
                removed += 1
        return removed

    def get_cache_stats(self) -> Dict:
        cache_files = list(self.cache_dir.glob("newsletter_*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        return {
            "total_files": len(cache_files),
            "total_size_kb": round(total_size / 1024, 2),
            "cache_dir": str(self.cache_dir.absolute()),
            "cache_duration_minutes": self.cache_minutes,
        }
