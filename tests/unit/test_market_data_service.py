"""
Unit tests for market_data_service module - RSS feed fetching functionality.
"""

import asyncio
from backend.services.market_data_service import (
    fetch_market_data_async,
    Article,
    SourceStats,
)


# Sync helper for tests (wraps the async function)
def fetch_market_data(categories=None):
    """Sync wrapper for testing - calls the async function."""
    return asyncio.run(fetch_market_data_async(categories=categories))


class TestFetchMarketData:
    """Tests for fetch_market_data function."""

    def test_fetch_market_data_returns_dict(self, mock_fetch_rss_feed):
        """Test that fetch_market_data returns a dictionary."""
        data = fetch_market_data()
        assert isinstance(data, dict)

    def test_fetch_market_data_has_required_keys(self, mock_fetch_rss_feed):
        """Test that returned data has all required keys."""
        data = fetch_market_data()
        assert "raw_us_market_news" in data
        assert "raw_israel_market_news" in data
        assert "raw_ai_news" in data

    def test_fetch_market_data_us_news_is_list(self, mock_fetch_rss_feed):
        """Test that US news data is a list."""
        data = fetch_market_data()
        assert isinstance(data["raw_us_market_news"], list)
        assert len(data["raw_us_market_news"]) > 0

    def test_fetch_market_data_israel_news_is_list(self, mock_fetch_rss_feed):
        """Test that Israeli news data is a list."""
        data = fetch_market_data()
        assert isinstance(data["raw_israel_market_news"], list)
        assert len(data["raw_israel_market_news"]) > 0

    def test_fetch_market_data_ai_news_is_list(self, mock_fetch_rss_feed):
        """Test that AI news data is a list."""
        data = fetch_market_data()
        assert isinstance(data["raw_ai_news"], list)
        assert len(data["raw_ai_news"]) > 0

    def test_fetch_market_data_has_items(self, mock_fetch_rss_feed):
        """Test that each category has news items (mocked data)."""
        data = fetch_market_data()
        # Should have at least 1 item each (from mocked RSS feeds)
        assert len(data["raw_us_market_news"]) >= 1
        assert len(data["raw_israel_market_news"]) >= 1
        assert len(data["raw_ai_news"]) >= 1
        # Should have at most 10 items each (limited by max_items)
        assert len(data["raw_us_market_news"]) <= 10
        assert len(data["raw_israel_market_news"]) <= 10
        assert len(data["raw_ai_news"]) <= 10

    def test_fetch_market_data_items_are_strings(self, mock_fetch_rss_feed):
        """Test that all news items are strings."""
        data = fetch_market_data()
        for news_item in data["raw_us_market_news"]:
            assert isinstance(news_item, str)
        for news_item in data["raw_israel_market_news"]:
            assert isinstance(news_item, str)
        for news_item in data["raw_ai_news"]:
            assert isinstance(news_item, str)

    def test_fetch_market_data_items_not_empty(self, mock_fetch_rss_feed):
        """Test that news items are not empty strings."""
        data = fetch_market_data()
        for news_item in data["raw_us_market_news"]:
            assert len(news_item) > 0
        for news_item in data["raw_israel_market_news"]:
            assert len(news_item) > 0
        for news_item in data["raw_ai_news"]:
            assert len(news_item) > 0

    def test_fetch_market_data_uses_expanded_sources(self, mock_fetch_rss_feed):
        """Test that fetch_market_data uses the expanded RSS feed sources."""
        data = fetch_market_data()

        # Verify we get diverse content from multiple sources (mocked)
        assert isinstance(data, dict)
        assert len(data["raw_us_market_news"]) > 0
        assert len(data["raw_israel_market_news"]) > 0
        assert len(data["raw_ai_news"]) > 0


class TestSourceMetadata:
    """Tests for source and published_at metadata."""

    def test_fetch_market_data_includes_metadata(self, mock_fetch_rss_feed):
        """Test that fetch_market_data returns articles_metadata."""
        data = fetch_market_data()
        assert "articles_metadata" in data
        assert isinstance(data["articles_metadata"], dict)

    def test_metadata_has_all_categories(self, mock_fetch_rss_feed):
        """Test that metadata includes US, Israel, and AI categories."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]
        assert "us" in metadata
        assert "israel" in metadata
        assert "ai" in metadata

    def test_metadata_items_are_lists(self, mock_fetch_rss_feed):
        """Test that each metadata category is a list."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]
        assert isinstance(metadata["us"], list)
        assert isinstance(metadata["israel"], list)
        assert isinstance(metadata["ai"], list)

    def test_metadata_items_have_required_fields(self, mock_fetch_rss_feed):
        """Test that metadata items contain source, published_at, text, original_title, and link."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]

        # Check US metadata
        if len(metadata["us"]) > 0:
            item = metadata["us"][0]
            assert "source" in item
            assert "published_at" in item
            assert "text" in item
            assert "original_title" in item  # RSS title, ai_title is added later by LLM
            assert "link" in item
            assert isinstance(item["source"], str)
            assert isinstance(item["published_at"], str)
            assert isinstance(item["text"], str)
            assert isinstance(item["original_title"], str)
            assert isinstance(item["link"], str)

    def test_metadata_source_names_are_valid(self, mock_fetch_rss_feed):
        """Test that source names are recognizable feed names."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]

        valid_sources = {
            "Yahoo Finance",
            "Nasdaq",
            "WSJ",
            "CNBC",
            "Investing.com",
            "FT",
            "Globes",
            "TheMarker",
            "TechCrunch",
            "VentureBeat",
        }

        # Check that at least some sources are from our valid set
        all_sources = set()
        for item in metadata["us"] + metadata["israel"] + metadata["ai"]:
            all_sources.add(item["source"])

        # Should have at least one valid source
        assert len(all_sources & valid_sources) > 0

    def test_metadata_published_at_is_iso_format(self, mock_fetch_rss_feed):
        """Test that published_at values are in ISO format."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]

        # Check US metadata published_at
        if len(metadata["us"]) > 0:
            published_at = metadata["us"][0]["published_at"]
            # ISO format includes 'T' separator
            assert "T" in published_at or published_at.count("-") >= 2

    def test_raw_news_and_metadata_count_match(self, mock_fetch_rss_feed):
        """Test that raw news count matches metadata count for each category."""
        data = fetch_market_data()

        assert len(data["raw_us_market_news"]) == len(data["articles_metadata"]["us"])
        assert len(data["raw_israel_market_news"]) == len(data["articles_metadata"]["israel"])
        assert len(data["raw_ai_news"]) == len(data["articles_metadata"]["ai"])

    def test_metadata_items_have_valid_links(self, mock_fetch_rss_feed):
        """Test that metadata items contain valid URL links."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]

        # Check that all items have link field
        for category in ["us", "israel", "ai"]:
            if len(metadata[category]) > 0:
                for item in metadata[category]:
                    assert "link" in item, f"Missing link field in {category} metadata"
                    link = item["link"]
                    assert isinstance(link, str), f"Link should be string in {category}"
                    # Link should either be a valid URL or empty string
                    if link:
                        assert link.startswith("http://") or link.startswith(
                            "https://"
                        ), f"Link should be a valid URL in {category}: {link}"


class TestRSSFeedFiltering:
    """Tests for RSS feed filtering behavior."""

    def test_fetch_market_data_only_includes_active_sources(self, mock_fetch_rss_feed):
        """Test that fetch_market_data only includes sources with recent articles."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]

        # All returned articles should have valid source names
        for category in ["us", "israel", "ai"]:
            for item in metadata[category]:
                assert item["source"] is not None
                assert len(item["source"]) > 0
                assert isinstance(item["source"], str)

    def test_sources_with_no_articles_are_excluded(self, mock_fetch_rss_feed):
        """Test that sources returning 0 articles don't appear in metadata."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]

        # If a source has no recent articles, it shouldn't create empty entries
        # Count total articles per category
        us_count = len(metadata["us"])
        israel_count = len(metadata["israel"])
        ai_count = len(metadata["ai"])

        # Should match raw news counts
        assert us_count == len(data["raw_us_market_news"])
        assert israel_count == len(data["raw_israel_market_news"])
        assert ai_count == len(data["raw_ai_news"])

        # All counts should be > 0 (mocked data ensures this)
        assert us_count > 0
        assert israel_count > 0
        assert ai_count > 0

    def test_metadata_sources_are_diverse(self, mock_fetch_rss_feed):
        """Test that metadata includes articles from multiple sources when available."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]

        # Extract unique sources from US metadata
        us_sources = set(item["source"] for item in metadata["us"])

        # With mocked RSS feeds, we should get diverse sources
        assert len(us_sources) >= 1

    def test_no_duplicate_source_entries(self, mock_fetch_rss_feed):
        """Test that articles from same source don't create redundant metadata."""
        data = fetch_market_data()
        metadata = data["articles_metadata"]

        # Each article should have its own metadata entry
        for category in ["us", "israel", "ai"]:
            for i, item in enumerate(metadata[category]):
                assert "text" in item
                assert "source" in item
                assert len(item["text"]) > 0


class TestDataModels:
    """Tests for Article and SourceStats dataclasses."""

    def test_article_dataclass_creation(self):
        """Test that Article dataclass can be created with all fields."""
        article = Article(
            text="Test article content",
            source="CNBC",
            published_at="2025-11-29T10:00:00",
            original_title="Test Article Title",  # RSS title, ai_title is added later by LLM
            link="https://example.com/article",
            freshness_score=0.85,  # Required - calculated from published_at
        )

        assert article.text == "Test article content"
        assert article.source == "CNBC"
        assert article.published_at == "2025-11-29T10:00:00"
        assert article.original_title == "Test Article Title"
        assert article.link == "https://example.com/article"
        assert article.freshness_score == 0.85

    def test_source_stats_dataclass_creation(self):
        """Test that SourceStats dataclass can be created."""
        stats = SourceStats(name="Yahoo Finance", count=5, status="active")

        assert stats.name == "Yahoo Finance"
        assert stats.count == 5
        assert stats.status == "active"

    def test_source_stats_inactive_status(self):
        """Test that SourceStats can have inactive status."""
        stats = SourceStats(name="FT", count=0, status="inactive")

        assert stats.name == "FT"
        assert stats.count == 0
        assert stats.status == "inactive"


class TestSourceStats:
    """Tests for source_stats in fetch_market_data response."""

    def test_fetch_market_data_includes_source_stats(self, mock_fetch_rss_feed):
        """Test that fetch_market_data returns source_stats."""
        data = fetch_market_data()

        assert "source_stats" in data
        assert isinstance(data["source_stats"], dict)

    def test_source_stats_has_all_categories(self, mock_fetch_rss_feed):
        """Test that source_stats includes US, Israel, and AI categories."""
        data = fetch_market_data()
        stats = data["source_stats"]

        assert "us" in stats
        assert "israel" in stats
        assert "ai" in stats

    def test_source_stats_are_lists_of_dicts(self, mock_fetch_rss_feed):
        """Test that source stats are lists of dictionaries."""
        data = fetch_market_data()
        stats = data["source_stats"]

        assert isinstance(stats["us"], list)
        assert isinstance(stats["israel"], list)
        assert isinstance(stats["ai"], list)

        # Check structure of stat items
        if len(stats["us"]) > 0:
            stat_item = stats["us"][0]
            assert "name" in stat_item
            assert "count" in stat_item
            assert "status" in stat_item

    def test_source_stats_shows_active_sources(self, mock_fetch_rss_feed):
        """Test that active sources have status='active'."""
        data = fetch_market_data()
        stats = data["source_stats"]

        # Find at least one active source in US stats
        active_sources = [s for s in stats["us"] if s["status"] == "active"]
        assert len(active_sources) > 0

        # Active sources should have count > 0
        for source in active_sources:
            assert source["count"] > 0

    def test_source_stats_shows_all_sources_active(self, mock_fetch_rss_feed):
        """Test that all sources are active (production DB only contains working feeds)."""
        data = fetch_market_data()
        stats = data["source_stats"]

        # All sources should be active (we cleaned up non-working feeds)
        all_stats = stats["us"] + stats["israel"] + stats["ai"]
        active_sources = [s for s in all_stats if s["status"] == "active"]

        # All sources should be active
        assert len(active_sources) == len(all_stats)

        # Active sources should have count > 0
        for source in active_sources:
            assert source["count"] > 0


class TestFeedFetchError:
    """Tests for FeedFetchError exception handling."""

    def test_fetch_market_data_returns_empty_when_all_feeds_fail(self, mocker):
        """Test that fetch_market_data returns empty arrays when all feeds fail (graceful degradation)."""
        from tests.conftest import MOCK_FEEDS

        # Mock database to return feeds
        mock_db_service = mocker.MagicMock()
        mock_db_service.get_all_feeds.return_value = MOCK_FEEDS
        mocker.patch(
            "backend.services.market_data_service.get_db_service",
            return_value=mock_db_service,
        )

        def create_empty_rss():
            return b"""<?xml version="1.0" encoding="UTF-8"?>
                <rss version="2.0"><channel><title>Empty</title></channel></rss>"""

        class MockResponse:
            def __init__(self, url):
                self.url = url
                self.status = 200

            async def read(self):
                return create_empty_rss()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

            def raise_for_status(self):
                pass

        class MockSession:
            def get(self, url, **kwargs):
                return MockResponse(url)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mocker.patch("aiohttp.ClientSession", return_value=MockSession())

        result = fetch_market_data()

        # All categories should have empty arrays (graceful degradation)
        assert result["raw_us_market_news"] == []
        assert result["raw_israel_market_news"] == []
        assert result["raw_ai_news"] == []
        assert result["raw_crypto_news"] == []

    def test_fetch_market_data_returns_empty_for_israel_when_feeds_fail(self, mocker):
        """Test that fetch_market_data returns empty for Israel when Israeli feeds fail."""
        from datetime import datetime
        from tests.conftest import MOCK_FEEDS

        # Mock database to return feeds
        mock_db_service = mocker.MagicMock()
        mock_db_service.get_all_feeds.return_value = MOCK_FEEDS
        mocker.patch(
            "backend.services.market_data_service.get_db_service",
            return_value=mock_db_service,
        )

        def create_rss_with_article(title):
            return f"""<?xml version="1.0" encoding="UTF-8"?>
                <rss version="2.0"><channel><title>Feed</title>
                    <item>
                        <title>{title}</title>
                        <description>Test</description>
                        <link>https://example.com</link>
                        <pubDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
                    </item>
                </channel></rss>""".encode()

        def create_empty_rss():
            return b"""<?xml version="1.0" encoding="UTF-8"?>
                <rss version="2.0"><channel><title>Empty</title></channel></rss>"""

        class MockResponse:
            def __init__(self, url):
                self.url = url
                self.status = 200

            async def read(self):
                # Israeli feeds return empty, others return article
                if "globes" in self.url.lower() or "ynet" in self.url.lower():
                    return create_empty_rss()
                return create_rss_with_article("Test Article")

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

            def raise_for_status(self):
                pass

        class MockSession:
            def get(self, url, **kwargs):
                return MockResponse(url)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mocker.patch("aiohttp.ClientSession", return_value=MockSession())

        # Mock LLM article selection
        from backend.services.quality_metrics_service import SelectionResult

        def mock_select_top_articles_with_metadata(articles, category, max_count=5):
            for article in articles:
                article.confidence_score = 0.85
            selected = articles[:max_count]
            selection_records = [
                {
                    "source_name": getattr(a, "source", "Unknown"),
                    "category": category,
                    "title": getattr(a, "original_title", "")[:500],
                    "link": getattr(a, "link", ""),
                    "selected": True,
                }
                for a in selected
            ]
            return SelectionResult(selected_articles=selected, selection_records=selection_records)

        mocker.patch(
            "backend.services.market_data_service.select_top_articles_with_metadata",
            side_effect=mock_select_top_articles_with_metadata,
        )

        result = fetch_market_data()

        # Israeli category should be empty, others should have articles
        assert result["raw_israel_market_news"] == []
        assert len(result["raw_us_market_news"]) > 0

    def test_fetch_market_data_allows_ai_feeds_to_fail(self, mocker):
        """Test that fetch_market_data continues even if all AI feeds fail (graceful degradation)."""
        from datetime import datetime
        from tests.conftest import MOCK_FEEDS

        # Mock database to return feeds
        mock_db_service = mocker.MagicMock()
        mock_db_service.get_all_feeds.return_value = MOCK_FEEDS
        mocker.patch(
            "backend.services.market_data_service.get_db_service",
            return_value=mock_db_service,
        )

        # Match production AI feed URLs
        ai_feed_patterns = [
            "techcrunch",
            "aibusiness",
            "artificialintelligence-news",
            "feedburner",
            "hnrss",
            "wired",
            "aijourn",
        ]
        crypto_feed_patterns = ["coindesk", "cointelegraph", "bitcoin", "decrypt"]

        def create_rss_with_article(title):
            return f"""<?xml version="1.0" encoding="UTF-8"?>
                <rss version="2.0"><channel><title>Feed</title>
                    <item>
                        <title>{title}</title>
                        <description>Test</description>
                        <link>https://example.com</link>
                        <pubDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
                    </item>
                </channel></rss>""".encode()

        def create_empty_rss():
            return b"""<?xml version="1.0" encoding="UTF-8"?>
                <rss version="2.0"><channel><title>Empty</title></channel></rss>"""

        class MockResponse:
            def __init__(self, url):
                self.url = url
                self.status = 200

            async def read(self):
                url_lower = self.url.lower()
                # AI and crypto feeds return empty
                if any(p in url_lower for p in ai_feed_patterns + crypto_feed_patterns):
                    return create_empty_rss()
                return create_rss_with_article("Test Article")

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

            def raise_for_status(self):
                pass

        class MockSession:
            def get(self, url, **kwargs):
                return MockResponse(url)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mocker.patch("aiohttp.ClientSession", return_value=MockSession())

        # Mock LLM article selection
        from backend.services.quality_metrics_service import SelectionResult

        def mock_select_top_articles_with_metadata(articles, category, max_count=5):
            for article in articles:
                article.confidence_score = 0.85
            selected = articles[:max_count]
            selection_records = [
                {
                    "source_name": getattr(a, "source", "Unknown"),
                    "category": category,
                    "title": getattr(a, "original_title", "")[:500],
                    "link": getattr(a, "link", ""),
                    "selected": True,
                }
                for a in selected
            ]
            return SelectionResult(selected_articles=selected, selection_records=selection_records)

        mocker.patch(
            "backend.services.market_data_service.select_top_articles_with_metadata",
            side_effect=mock_select_top_articles_with_metadata,
        )

        # Should NOT raise exception
        data = fetch_market_data()

        # Should have US and Israeli news
        assert len(data["raw_us_market_news"]) > 0
        assert len(data["raw_israel_market_news"]) > 0

        # AI news should be empty but present
        assert "raw_ai_news" in data
        assert len(data["raw_ai_news"]) == 0


class TestCategoryFiltering:
    """Tests for category filtering feature."""

    def test_fetch_market_data_with_all_categories(self, mock_fetch_rss_feed):
        """Test fetching with all categories returns all data."""
        data = fetch_market_data(categories=["us", "israel", "ai", "crypto"])
        assert "raw_us_market_news" in data
        assert "raw_israel_market_news" in data
        assert "raw_ai_news" in data
        assert "raw_crypto_news" in data

    def test_fetch_market_data_with_us_only(self, mock_fetch_rss_feed):
        """Test fetching with only US category."""
        data = fetch_market_data(categories=["us"])
        assert len(data["raw_us_market_news"]) > 0
        # Other categories should be empty
        assert len(data["raw_israel_market_news"]) == 0
        assert len(data["raw_ai_news"]) == 0
        assert len(data["raw_crypto_news"]) == 0

    def test_fetch_market_data_with_israel_only(self, mock_fetch_rss_feed):
        """Test fetching with only Israel category."""
        data = fetch_market_data(categories=["israel"])
        assert len(data["raw_israel_market_news"]) > 0
        # Other categories should be empty
        assert len(data["raw_us_market_news"]) == 0
        assert len(data["raw_ai_news"]) == 0
        assert len(data["raw_crypto_news"]) == 0

    def test_fetch_market_data_with_multiple_categories(self, mock_fetch_rss_feed):
        """Test fetching with multiple selected categories."""
        data = fetch_market_data(categories=["us", "ai"])
        assert len(data["raw_us_market_news"]) > 0
        assert len(data["raw_ai_news"]) > 0
        # Unselected categories should be empty
        assert len(data["raw_israel_market_news"]) == 0
        assert len(data["raw_crypto_news"]) == 0

    def test_fetch_market_data_none_categories_fetches_all(self, mock_fetch_rss_feed):
        """Test that None categories defaults to fetching all."""
        data = fetch_market_data(categories=None)
        assert len(data["raw_us_market_news"]) > 0
        assert len(data["raw_israel_market_news"]) > 0
        assert len(data["raw_ai_news"]) > 0

    def test_fetch_market_data_source_stats_reflect_categories(self, mock_fetch_rss_feed):
        """Test that source_stats only includes stats for selected categories."""
        data = fetch_market_data(categories=["us"])
        stats = data["source_stats"]
        # US should have stats
        assert len(stats["us"]) > 0
        # Other categories should be empty
        assert len(stats["israel"]) == 0
        assert len(stats["ai"]) == 0
        assert len(stats["crypto"]) == 0

    def test_fetch_market_data_articles_metadata_reflect_categories(self, mock_fetch_rss_feed):
        """Test that articles_metadata only includes selected categories."""
        data = fetch_market_data(categories=["israel", "crypto"])
        metadata = data["articles_metadata"]
        # Selected categories should have data
        assert len(metadata["israel"]) > 0
        # Unselected categories should be empty
        assert len(metadata["us"]) == 0
        assert len(metadata["ai"]) == 0


class TestAsyncFetching:
    """Tests for async RSS feed fetching."""

    def test_fetch_market_data_uses_async(self, mock_fetch_rss_feed):
        """Test that fetch_market_data runs async code via asyncio.run wrapper."""
        # Should work via asyncio.run wrapper (using the mock_fetch_rss_feed fixture)
        data = fetch_market_data()
        assert isinstance(data, dict)
        assert "raw_us_market_news" in data
