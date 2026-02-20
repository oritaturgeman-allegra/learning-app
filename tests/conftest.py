"""
Shared pytest fixtures for all tests.
"""

import os
import tempfile

# CRITICAL: Set test database BEFORE any backend imports to prevent
# the production database from being used or modified during tests
_test_db_file = tempfile.NamedTemporaryFile(suffix="_test.db", delete=False)
_test_db_path = _test_db_file.name
_test_db_file.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"
os.environ["TESTING"] = "true"
os.environ["SENTRY_DSN"] = ""  # Disable Sentry during tests - errors go to CI logs only

import pytest  # noqa: E402
from datetime import datetime  # noqa: E402
from backend.services import newsletter_cache_service  # noqa: E402


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear in-memory caches before each test to prevent test pollution."""
    # Clear the global memory cache
    newsletter_cache_service._memory_cache.clear()
    yield
    # Also clear after test
    newsletter_cache_service._memory_cache.clear()


@pytest.fixture
def mock_rss_articles():
    """
    Mock RSS feed articles with realistic data for testing.
    Returns a dictionary with mock articles for each category.
    """
    return {
        "us": [
            {
                "original_title": "S&P 500 Gains 1.2% on Strong Tech Earnings",  # RSS title
                "text": "S&P 500 Gains 1.2% on Strong Tech Earnings - Market rallied today",
                "source": "CNBC",
                "published_at": datetime.now().isoformat(),
                "link": "https://www.cnbc.com/article1",
            },
            {
                "original_title": "Fed Signals Potential Rate Cut in Q2",
                "text": "Fed Signals Potential Rate Cut in Q2 - Federal Reserve indicated",
                "source": "WSJ",
                "published_at": datetime.now().isoformat(),
                "link": "https://www.wsj.com/article2",
            },
            {
                "original_title": "Apple Reports Record Q1 Revenue of $125B",
                "text": "Apple Reports Record Q1 Revenue of $125B - Apple Inc announced",
                "source": "Yahoo Finance",
                "published_at": datetime.now().isoformat(),
                "link": "https://finance.yahoo.com/article3",
            },
            {
                "original_title": "Tesla Stock Jumps 8% on Production Milestone",
                "text": "Tesla Stock Jumps 8% on Production Milestone - Tesla achieved",
                "source": "Nasdaq",
                "published_at": datetime.now().isoformat(),
                "link": "https://www.nasdaq.com/article4",
            },
            {
                "original_title": "Oil Prices Rise on Middle East Tensions",
                "text": "Oil Prices Rise on Middle East Tensions - Crude oil prices",
                "source": "Investing.com",
                "published_at": datetime.now().isoformat(),
                "link": "https://www.investing.com/article5",
            },
        ],
        "israel": [
            {
                "original_title": "Tel Aviv 35 Index Closes Up 2.1%",
                "text": "Tel Aviv 35 Index Closes Up 2.1% - Israeli market surged",
                "source": "Globes",
                "published_at": datetime.now().isoformat(),
                "link": "https://www.globes.co.il/article6",
            },
            {
                "original_title": "Bank of Israel Holds Interest Rate at 4.5%",
                "text": "Bank of Israel Holds Interest Rate at 4.5% - Central bank",
                "source": "Globes",
                "published_at": datetime.now().isoformat(),
                "link": "https://www.globes.co.il/article8",
            },
            {
                "original_title": "Israeli Tech Sector Reports Strong Q1 Growth",
                "text": "Israeli Tech Sector Reports Strong Q1 Growth - Venture capital investments rise",
                "source": "Ynet Calcala",
                "published_at": datetime.now().isoformat(),
                "link": "https://www.ynet.co.il/article9",
            },
        ],
        "ai": [
            {
                "original_title": "OpenAI Launches GPT-5 with Enhanced Reasoning",
                "text": "OpenAI Launches GPT-5 with Enhanced Reasoning - OpenAI announced",
                "source": "TechCrunch",
                "published_at": datetime.now().isoformat(),
                "link": "https://techcrunch.com/article9",
            },
            {
                "original_title": "Google Unveils New AI Chip Architecture",
                "text": "Google Unveils New AI Chip Architecture - Google revealed",
                "source": "VentureBeat",
                "published_at": datetime.now().isoformat(),
                "link": "https://venturebeat.com/article10",
            },
            {
                "original_title": "AI Startup Anthropic Raises $500M Series C",
                "text": "AI Startup Anthropic Raises $500M Series C - Anthropic secured",
                "source": "TechCrunch",
                "published_at": datetime.now().isoformat(),
                "link": "https://techcrunch.com/article11",
            },
            {
                "original_title": "Microsoft Integrates AI Across Office Suite",
                "text": "Microsoft Integrates AI Across Office Suite - Microsoft announced",
                "source": "VentureBeat",
                "published_at": datetime.now().isoformat(),
                "link": "https://venturebeat.com/article12",
            },
        ],
        "crypto": [
            {
                "original_title": "Bitcoin Surges Past $100K Mark",
                "text": "Bitcoin Surges Past $100K Mark - Cryptocurrency markets rally",
                "source": "CoinDesk",
                "published_at": datetime.now().isoformat(),
                "link": "https://coindesk.com/article13",
            },
            {
                "original_title": "Ethereum 2.0 Upgrade Completes Successfully",
                "text": "Ethereum 2.0 Upgrade Completes Successfully - Network transition",
                "source": "Cointelegraph",
                "published_at": datetime.now().isoformat(),
                "link": "https://cointelegraph.com/article14",
            },
        ],
    }


# Mock feed data - matches production Supabase feed_providers table
MOCK_FEEDS = [
    # US feeds (4 sources)
    ("https://finance.yahoo.com/news/rssindex", "Yahoo Finance", "us"),
    ("https://www.cnbc.com/id/100003114/device/rss/rss.html", "CNBC", "us"),
    ("https://feeds.marketwatch.com/marketwatch/topstories/", "MarketWatch", "us"),
    (
        "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
        "Reuters Business",
        "us",
    ),
    # Israel feeds (2 sources)
    (
        "https://www.globes.co.il/webservice/rss/rssfeeder.asmx/FeederNode?iID=585",
        "Globes",
        "israel",
    ),
    ("https://www.ynet.co.il/Integration/StoryRss6.xml", "Ynet Calcala", "israel"),
    # AI feeds (8 sources)
    ("https://aibusiness.com/rss.xml", "AI Business", "ai"),
    ("https://www.artificialintelligence-news.com/feed/", "AI News", "ai"),
    ("http://feeds.feedburner.com/blogspot/gJZg", "Google AI Blog", "ai"),
    ("https://hnrss.org/newest?q=AI+artificial+intelligence", "Hacker News AI", "ai"),
    ("http://feeds.feedburner.com/nvidiablog", "NVIDIA AI Blog", "ai"),
    ("https://techcrunch.com/category/artificial-intelligence/feed/", "TechCrunch AI", "ai"),
    ("https://aijourn.com/feed/", "The AI Journal", "ai"),
    ("https://www.wired.com/feed/tag/ai/latest/rss", "Wired AI", "ai"),
    # Crypto feeds (4 sources)
    ("https://bitcoinmagazine.com/feed", "Bitcoin Magazine", "crypto"),
    ("https://www.coindesk.com/arc/outboundfeeds/rss/", "CoinDesk", "crypto"),
    ("https://cointelegraph.com/rss", "Cointelegraph", "crypto"),
    ("https://decrypt.co/feed", "Decrypt", "crypto"),
]


@pytest.fixture
def mock_fetch_rss_feed(mocker, mock_rss_articles):
    """
    Mock aiohttp to return predetermined RSS content based on URL.
    Also mocks database to return feed URLs and LLM calls for quality scoring.

    This prevents tests from making real HTTP requests to RSS feeds or LLM APIs.
    """
    from datetime import datetime

    # Mock the database service to return feeds
    mock_db_service = mocker.MagicMock()
    mock_db_service.get_all_feeds.return_value = MOCK_FEEDS
    mocker.patch(
        "backend.services.market_data_service.get_db_service",
        return_value=mock_db_service,
    )

    # Mock LLM article selection - set confidence scores and return SelectionResult
    from backend.services.quality_metrics_service import SelectionResult

    def mock_select_top_articles_with_metadata(articles, category, max_count=5):
        """Mock LLM selection: set confidence scores and return SelectionResult."""
        for article in articles:
            article.confidence_score = 0.85  # High confidence for test articles
        selected = articles[:max_count]
        # Build selection records for analytics
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

    def create_rss_xml(articles):
        """Create RSS XML from article dicts."""
        items = []
        for art in articles:
            items.append(
                f"""
                <item>
                    <title>{art['original_title']}</title>
                    <description>{art['text']}</description>
                    <link>{art['link']}</link>
                    <pubDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
                </item>
            """
            )
        return f"""<?xml version="1.0" encoding="UTF-8"?>
            <rss version="2.0">
                <channel>
                    <title>Mock Feed</title>
                    {''.join(items)}
                </channel>
            </rss>
        """.encode()

    def get_articles_for_url(url):
        """Return mock articles based on URL."""
        url_lower = url.lower()
        # US feeds
        if "cnbc" in url_lower:
            return [mock_rss_articles["us"][0]]
        elif "yahoo" in url_lower:
            return [mock_rss_articles["us"][2]]
        elif "marketwatch" in url_lower:
            return [mock_rss_articles["us"][1]]
        elif "reuters" in url_lower:
            return [mock_rss_articles["us"][3], mock_rss_articles["us"][4]]
        # Israel feeds
        elif "globes" in url_lower:
            return [mock_rss_articles["israel"][0], mock_rss_articles["israel"][1]]
        elif "ynet" in url_lower:
            return [mock_rss_articles["israel"][2]]
        # AI feeds
        elif "techcrunch" in url_lower:
            return [mock_rss_articles["ai"][0], mock_rss_articles["ai"][2]]
        elif "wired" in url_lower or "aijourn" in url_lower:
            return [mock_rss_articles["ai"][1], mock_rss_articles["ai"][3]]
        elif "aibusiness" in url_lower or "artificialintelligence-news" in url_lower:
            return [mock_rss_articles["ai"][0]]
        elif "feedburner" in url_lower or "hnrss" in url_lower:
            return [mock_rss_articles["ai"][1]]
        # Crypto feeds
        elif "coindesk" in url_lower:
            return [mock_rss_articles["crypto"][0]]
        elif "cointelegraph" in url_lower:
            return [mock_rss_articles["crypto"][1]]
        elif "bitcoinmagazine" in url_lower or "decrypt" in url_lower:
            return [mock_rss_articles["crypto"][0]]
        else:
            return []

    class MockResponse:
        def __init__(self, url):
            self.url = url
            self.status = 200

        async def read(self):
            articles = get_articles_for_url(self.url)
            return create_rss_xml(articles)

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

    return mocker.patch(
        "aiohttp.ClientSession",
        return_value=MockSession(),
    )
