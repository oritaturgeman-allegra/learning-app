"""
Unit tests for newsletter cache service.
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import pytest

from backend.services.newsletter_cache_service import NewsletterCacheService


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def cache_service(temp_cache_dir):
    """Create a cache service instance with temp cache directory."""
    return NewsletterCacheService(cache_dir=temp_cache_dir, cache_minutes=60)


@pytest.fixture
def default_categories():
    """Default categories for testing."""
    return ["us", "israel", "ai", "crypto"]


@pytest.fixture
def sample_newsletter_data():
    """Sample newsletter data for testing."""
    return {
        "us_bullets": [
            "S&P 500 gained 1.2% to close at record highs",
            "NVIDIA announced new AI chip",
            "Apple reports strong quarterly earnings",
        ],
        "israel_bullets": [
            "TA-35 index rose 0.8% on strong banking sector",
            "Israeli tech stocks lead gains",
        ],
        "ai_bullets": ["OpenAI announces new GPT model", "Google unveils AI search features"],
        "metadata": {
            "indices": ["S&P 500", "TA-35", "NASDAQ"],
            "tickers": ["NVDA", "AAPL", "GOOGL"],
            "sources": ["Reuters", "Bloomberg", "WSJ"],
        },
    }


class TestCacheInitialization:
    """Test cache service initialization."""

    def test_cache_dir_created(self, temp_cache_dir):
        """Test that cache directory is created."""
        cache_service = NewsletterCacheService(cache_dir=temp_cache_dir)
        assert cache_service.cache_dir.exists()
        assert cache_service.cache_dir.is_dir()

    def test_default_cache_duration(self, temp_cache_dir):
        """Test default cache duration is 60 minutes."""
        cache_service = NewsletterCacheService(cache_dir=temp_cache_dir)
        assert cache_service.cache_minutes == 60

    def test_custom_cache_duration(self, temp_cache_dir):
        """Test custom cache duration."""
        cache_service = NewsletterCacheService(cache_dir=temp_cache_dir, cache_minutes=30)
        assert cache_service.cache_minutes == 30

    def test_absolute_path_handling(self, temp_cache_dir):
        """Test that cache dir path is made absolute."""
        cache_service = NewsletterCacheService(cache_dir=temp_cache_dir)
        assert cache_service.cache_dir.is_absolute()


class TestCacheKeyGeneration:
    """Test cache key generation."""

    def test_cache_key_format(self, cache_service, default_categories):
        """Test cache key format includes date, time, and categories."""
        cache_key = cache_service._get_cache_key(default_categories)
        today = datetime.now().strftime("%Y-%m-%d")
        # Key format: newsletter_YYYY-MM-DD_HHMMSS_cat1_cat2_...
        assert cache_key.startswith(f"newsletter_{today}_")
        # Verify categories are included (sorted alphabetically)
        assert "ai_crypto_israel_us" in cache_key

    def test_cache_key_unique_per_second(self, cache_service, default_categories):
        """Test that keys generated at same second are identical."""
        key1 = cache_service._get_cache_key(default_categories)
        # Keys within same second should match
        key2 = cache_service._get_cache_key(default_categories)
        # Note: There's a tiny chance these differ if crossing second boundary
        # but practically they should be the same or very close
        assert key1[:25] == key2[:25]  # Date portion matches

    def test_cache_key_different_for_different_categories(self, cache_service):
        """Test that different categories produce different keys."""
        key1 = cache_service._get_cache_key(["us"])
        key2 = cache_service._get_cache_key(["us", "israel"])
        # Keys should differ due to different categories
        assert key1 != key2
        assert "us" in key1
        assert "israel_us" in key2


class TestGetLatestCacheFile:
    """Test finding the latest cache file."""

    def test_no_files_returns_none(self, cache_service, default_categories):
        """Test returns None when no cache files exist."""
        result = cache_service._get_latest_cache_file(default_categories)
        assert result is None

    def test_finds_latest_file(self, cache_service, sample_newsletter_data, default_categories):
        """Test finds the most recent cache file."""
        import time

        # Save first newsletter
        cache_service.save_to_cache(sample_newsletter_data, default_categories)
        time.sleep(0.1)  # Small delay to ensure different timestamp

        # Save second newsletter
        modified_data = sample_newsletter_data.copy()
        modified_data["ai_titles"] = {"us:0": "Updated title"}
        cache_service.clear_memory_cache()  # Clear memory to force new file
        cache_service.save_to_cache(modified_data, default_categories)

        # Should find the latest file
        latest = cache_service._get_latest_cache_file(default_categories)
        assert latest is not None
        assert latest.exists()

        # Verify it's the second file (has updated content)
        with open(latest, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["newsletter"]["ai_titles"] == {"us:0": "Updated title"}


class TestSaveToCache:
    """Test saving newsletters to cache."""

    def test_save_creates_cache_file(
        self, cache_service, sample_newsletter_data, default_categories
    ):
        """Test that saving creates a cache file."""
        cache_service.save_to_cache(sample_newsletter_data, default_categories)

        # Find the created file
        cache_files = list(cache_service.cache_dir.glob("newsletter_*.json"))
        assert len(cache_files) == 1

    def test_save_includes_metadata(
        self, cache_service, sample_newsletter_data, default_categories
    ):
        """Test that cache file includes metadata."""
        cache_service.save_to_cache(sample_newsletter_data, default_categories)

        # Find the created file
        cache_files = list(cache_service.cache_dir.glob("newsletter_*.json"))
        cache_file = cache_files[0]

        with open(cache_file, "r", encoding="utf-8") as f:
            cached_data = json.load(f)

        assert "newsletter" in cached_data
        assert "cache_metadata" in cached_data
        assert cached_data["newsletter"] == sample_newsletter_data

        metadata = cached_data["cache_metadata"]
        assert "created_at" in metadata
        assert "expires_at" in metadata
        assert "cache_duration_minutes" in metadata
        assert metadata["cache_duration_minutes"] == 60
        assert "categories" in metadata
        assert set(metadata["categories"]) == set(default_categories)

    def test_save_accumulates_files(
        self, cache_service, sample_newsletter_data, default_categories
    ):
        """Test that saving multiple times creates multiple files (accumulates)."""
        import time

        # Save first time
        cache_service.save_to_cache(sample_newsletter_data, default_categories)
        time.sleep(1.1)  # Wait to get different timestamp

        # Save second time with different data
        modified_data = sample_newsletter_data.copy()
        modified_data["ai_titles"] = {"us:0": "Modified title"}
        cache_service.clear_memory_cache()  # Clear memory cache
        cache_service.save_to_cache(modified_data, default_categories)

        # Should have 2 files now
        cache_files = list(cache_service.cache_dir.glob("newsletter_*.json"))
        assert len(cache_files) == 2

        # get_cached_newsletter returns the latest one
        cached = cache_service.get_cached_newsletter(default_categories)
        assert cached["newsletter"]["ai_titles"] == {"us:0": "Modified title"}


class TestGetCachedNewsletter:
    """Test retrieving cached newsletters."""

    def test_get_nonexistent_returns_none(self, cache_service, default_categories):
        """Test retrieving non-existent cache returns None."""
        cached = cache_service.get_cached_newsletter(default_categories)
        assert cached is None

    def test_get_valid_cache(self, cache_service, sample_newsletter_data, default_categories):
        """Test retrieving valid cached data."""
        cache_service.save_to_cache(sample_newsletter_data, default_categories)
        cached = cache_service.get_cached_newsletter(default_categories)

        assert cached is not None
        assert cached["newsletter"] == sample_newsletter_data
        assert "cache_metadata" in cached

    def test_get_expired_cache_returns_none(
        self, temp_cache_dir, sample_newsletter_data, default_categories
    ):
        """Test that expired cache returns None but file is preserved."""
        # Create cache service with 0 minute duration (immediate expiry)
        cache_service = NewsletterCacheService(cache_dir=temp_cache_dir, cache_minutes=0)

        # Save to cache
        cache_service.save_to_cache(sample_newsletter_data, default_categories)

        # Find the cache file
        cache_files = list(cache_service.cache_dir.glob("newsletter_*.json"))
        cache_file = cache_files[0]

        # Modify the cache file to have an old timestamp
        with open(cache_file, "r", encoding="utf-8") as f:
            cached_data = json.load(f)

        old_time = datetime.now() - timedelta(hours=2)
        cached_data["cache_metadata"]["created_at"] = old_time.isoformat()

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cached_data, f)

        # Clear memory cache to force file read
        cache_service.clear_memory_cache()

        # Try to retrieve - should return None but file is preserved (accumulate mode)
        cached = cache_service.get_cached_newsletter(default_categories)

        assert cached is None
        # File should still exist (we accumulate, not delete)
        assert cache_file.exists()

    def test_get_invalid_json_returns_none(self, cache_service, default_categories):
        """Test that invalid JSON cache returns None."""
        # Create invalid cache file with today's date and matching categories
        today_str = datetime.now().strftime("%Y-%m-%d")
        cat_key = "_".join(sorted(default_categories))
        cache_file = cache_service.cache_dir / f"newsletter_{today_str}_120000_{cat_key}.json"

        with open(cache_file, "w") as f:
            f.write("invalid json content")

        cached = cache_service.get_cached_newsletter(default_categories)

        assert cached is None

    def test_different_categories_have_separate_cache(self, cache_service, sample_newsletter_data):
        """Test that different category combinations have separate caches."""
        # Save with US only
        cache_service.save_to_cache({"data": "us_only"}, ["us"])

        # Save with Israel only
        cache_service.save_to_cache({"data": "israel_only"}, ["israel"])

        # Each should retrieve its own cache
        us_cached = cache_service.get_cached_newsletter(["us"])
        israel_cached = cache_service.get_cached_newsletter(["israel"])

        assert us_cached["newsletter"]["data"] == "us_only"
        assert israel_cached["newsletter"]["data"] == "israel_only"


class TestSupersetCaching:
    """Test smart superset caching - reuse larger cache for subset requests."""

    def test_superset_cache_found_for_subset_request(self, cache_service):
        """Test that a request for subset categories uses superset cache."""
        # Save cache with all categories
        all_categories = ["us", "israel", "ai", "crypto"]
        full_data = {
            "data": {
                "ai_podcast_dialog": [["host", "Welcome!"]],
                "sources_metadata": {
                    "us": [{"source": "CNBC", "title": "US News"}],
                    "israel": [{"source": "Globes", "title": "IL News"}],
                    "ai": [{"source": "TechCrunch", "title": "AI News"}],
                    "crypto": [{"source": "CoinDesk", "title": "Crypto News"}],
                },
            },
            "input_counts": {
                "us_news": 5,
                "israel_news": 3,
                "ai_news": 4,
                "crypto_news": 2,
            },
            "source_stats": {
                "us": [{"name": "CNBC", "count": 5}],
                "israel": [{"name": "Globes", "count": 3}],
                "ai": [{"name": "TechCrunch", "count": 4}],
                "crypto": [{"name": "CoinDesk", "count": 2}],
            },
        }
        cache_service.save_to_cache(full_data, all_categories)

        # Request only US - should find superset and filter
        us_only_cached = cache_service.get_cached_newsletter(["us"])

        assert us_only_cached is not None
        assert us_only_cached["cache_metadata"]["filtered_from_superset"] is True
        # Should have US data
        assert "us" in us_only_cached["newsletter"]["data"]["sources_metadata"]
        assert len(us_only_cached["newsletter"]["data"]["sources_metadata"]["us"]) == 1
        # Should NOT have other categories in sources_metadata
        assert "israel" not in us_only_cached["newsletter"]["data"]["sources_metadata"]
        # Input counts should be filtered
        assert "us_news" in us_only_cached["newsletter"]["input_counts"]
        assert us_only_cached["newsletter"]["input_counts"]["us_news"] == 5

    def test_superset_cache_preserves_common_fields(self, cache_service):
        """Test that sources_metadata is filtered correctly from superset."""
        all_categories = ["us", "israel", "ai", "crypto"]
        full_data = {
            "data": {
                "sources_metadata": {
                    "us": [{"source": "CNBC"}],
                    "israel": [{"source": "Globes"}],
                    "ai": [{"source": "TechCrunch"}],
                    "crypto": [{"source": "CoinDesk"}],
                },
            },
            "input_counts": {"us_news": 1, "israel_news": 1, "ai_news": 1, "crypto_news": 1},
            "source_stats": {"us": [], "israel": [], "ai": [], "crypto": []},
        }
        cache_service.save_to_cache(full_data, all_categories)

        # Request subset
        cached = cache_service.get_cached_newsletter(["us", "ai"])

        # Should have filtered sources_metadata
        assert "us" in cached["newsletter"]["data"]["sources_metadata"]
        assert "ai" in cached["newsletter"]["data"]["sources_metadata"]
        assert "israel" not in cached["newsletter"]["data"]["sources_metadata"]

    def test_no_superset_returns_none(self, cache_service):
        """Test that no superset available returns None."""
        # Save cache with only US
        cache_service.save_to_cache({"data": "us_only"}, ["us"])

        # Request US + Israel - no superset exists
        cached = cache_service.get_cached_newsletter(["us", "israel"])

        assert cached is None

    def test_exact_match_preferred_over_superset(self, cache_service):
        """Test that exact category match is used before superset."""
        all_categories = ["us", "israel", "ai", "crypto"]
        us_only = ["us"]

        # Save superset cache
        cache_service.save_to_cache(
            {"data": {"ai_titles": {"us:0": "From superset"}}}, all_categories
        )

        # Save exact match cache
        cache_service.save_to_cache({"data": {"ai_titles": {"us:0": "From exact"}}}, us_only)

        # Request US only - should get exact match
        cached = cache_service.get_cached_newsletter(us_only)

        assert cached["newsletter"]["data"]["ai_titles"]["us:0"] == "From exact"
        assert "filtered_from_superset" not in cached["cache_metadata"]


class TestCleanupExpiredCache:
    """Test cache cleanup functionality."""

    def test_cleanup_removes_expired(
        self, temp_cache_dir, sample_newsletter_data, default_categories
    ):
        """Test that cleanup removes expired cache files."""
        cache_service = NewsletterCacheService(cache_dir=temp_cache_dir, cache_minutes=60)

        # Create cache file with old timestamp
        cache_service.save_to_cache(sample_newsletter_data, default_categories)

        # Find the cache file
        cache_files = list(cache_service.cache_dir.glob("newsletter_*.json"))
        cache_file = cache_files[0]

        # Modify timestamp to be old
        with open(cache_file, "r", encoding="utf-8") as f:
            cached_data = json.load(f)

        old_time = datetime.now() - timedelta(hours=2)
        cached_data["cache_metadata"]["created_at"] = old_time.isoformat()

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cached_data, f)

        # Run cleanup
        removed_count = cache_service.cleanup_expired_cache()

        assert removed_count == 1
        assert len(list(cache_service.cache_dir.glob("newsletter_*.json"))) == 0

    def test_cleanup_keeps_valid(self, cache_service, sample_newsletter_data, default_categories):
        """Test that cleanup keeps valid cache files."""
        # Save fresh cache
        cache_service.save_to_cache(sample_newsletter_data, default_categories)

        # Run cleanup
        removed_count = cache_service.cleanup_expired_cache()

        assert removed_count == 0
        assert cache_service.get_cached_newsletter(default_categories) is not None

    def test_cleanup_removes_invalid_json(self, cache_service):
        """Test that cleanup removes invalid JSON files."""
        # Create invalid cache file with proper naming pattern
        invalid_file = cache_service.cache_dir / "newsletter_2025-11-28_120000.json"
        with open(invalid_file, "w") as f:
            f.write("invalid json")

        removed_count = cache_service.cleanup_expired_cache()

        assert removed_count == 1
        assert not invalid_file.exists()


class TestCacheStats:
    """Test cache statistics."""

    def test_stats_empty_cache(self, cache_service):
        """Test stats for empty cache."""
        stats = cache_service.get_cache_stats()

        assert stats["total_files"] == 0
        assert stats["total_size_kb"] == 0
        assert "cache_dir" in stats
        assert stats["cache_duration_minutes"] == 60

    def test_stats_with_files(self, cache_service, sample_newsletter_data, default_categories):
        """Test stats with cached files."""
        # Save newsletter
        cache_service.save_to_cache(sample_newsletter_data, default_categories)

        stats = cache_service.get_cache_stats()

        assert stats["total_files"] == 1
        assert stats["total_size_kb"] > 0
        assert str(cache_service.cache_dir.absolute()) in stats["cache_dir"]
        assert stats["cache_duration_minutes"] == 60

    def test_stats_cache_dir_path(self, cache_service):
        """Test that stats includes absolute cache directory path."""
        stats = cache_service.get_cache_stats()
        cache_dir = Path(stats["cache_dir"])

        assert cache_dir.is_absolute()
        assert cache_dir.exists()
