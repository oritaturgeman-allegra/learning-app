"""
Integration tests for web API.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from backend.web_app import app


def assert_in_html(needle: str, html: str, msg: str = None) -> None:
    """Assert that needle is in HTML without dumping entire HTML on failure."""
    if needle not in html:
        error_msg = msg or f"Expected '{needle}' in HTML response"
        raise AssertionError(error_msg)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear newsletter cache files before each test."""
    cache_dir = Path.cwd() / "newsletter_cache"
    if cache_dir.exists():
        # Delete all files in cache directory, but keep the directory
        for file in cache_dir.glob("*.json"):
            file.unlink(missing_ok=True)
    yield
    # Cleanup after test
    if cache_dir.exists():
        for file in cache_dir.glob("*.json"):
            file.unlink(missing_ok=True)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestWebAppRoutes:
    """Tests for web application routes."""

    def test_index_route_returns_200(self, client):
        """Test that index route returns 200 status code."""
        response = client.get("/")
        assert response.status_code == 200, "Index route should return 200"

    def test_index_route_returns_html(self, client):
        """Test that index route returns HTML content."""
        response = client.get("/")
        assert "text/html" in response.headers["content-type"], "Response should be HTML"

    def test_index_route_contains_title(self, client):
        """Test that index page contains the project title."""
        response = client.get("/")
        assert_in_html("Your Newsletter, Your Way", response.text, "Missing page title")

    def test_index_route_contains_version_in_footer(self, client):
        """Test that index page contains version in footer."""
        response = client.get("/")
        assert_in_html("v1.", response.text, "Missing version number (v1.x) in footer")

    def test_index_route_contains_cta_button(self, client):
        """Test that index page contains CTA button."""
        response = client.get("/")
        html = response.text
        assert_in_html('id="get-newsletter-btn"', html, "Missing get-newsletter-btn id")
        assert_in_html("Get My Newsletter", html, "Missing 'Get My Newsletter' button text")

    def test_index_route_contains_auth_modals(self, client):
        """Test that landing page contains login and signup modals."""
        response = client.get("/")
        html = response.text
        assert_in_html("login-modal", html, "Missing login-modal")
        assert_in_html("signup-modal", html, "Missing signup-modal")

    def test_index_route_contains_benefit_strip(self, client):
        """Test that landing page contains benefit strip."""
        response = client.get("/")
        html = response.text
        assert_in_html("benefit-strip", html, "Missing benefit-strip")
        assert_in_html("AI-Powered", html, "Missing AI-Powered benefit")

    def test_index_route_contains_footer(self, client):
        """Test that index page contains footer with required elements."""
        response = client.get("/")
        html = response.text
        assert_in_html('class="footer"', html, "Missing footer class")
        assert_in_html("Powered by AI", html, "Missing 'Powered by AI' text")

    def test_index_route_contains_header_with_external_css(self, client):
        """Test that header element exists and external CSS is loaded."""
        response = client.get("/")
        html = response.text
        assert_in_html('class="header"', html, "Missing header class")
        assert_in_html('<link rel="stylesheet"', html, "Missing stylesheet link")
        assert_in_html("/static/css/", html, "Missing CSS path")

    def test_newsletter_route_returns_200(self, client):
        """Test that newsletter route returns 200 status code."""
        response = client.get("/newsletter")
        assert response.status_code == 200, "Newsletter route should return 200"

    def test_newsletter_route_contains_app_elements(self, client):
        """Test that newsletter page contains app elements for logged-in users."""
        response = client.get("/newsletter")
        html = response.text
        assert_in_html("podcast-section", html, "Missing podcast-section")
        assert_in_html("podcast-sidebar", html, "Missing podcast-sidebar")
        assert_in_html("newsletter.js", html, "Missing newsletter.js script")


class TestAnalyzeAPIEndpoint:
    """Tests for /api/analyze endpoint (DB/cache-based)."""

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_success(self, mock_get_db, client):
        """Test successful analysis request returns cached content."""
        # Mock DB to return newsletter data
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"text": "news1"}, {"text": "news2"}],
                "israel": [{"text": "news3"}, {"text": "news4"}],
                "ai": [{"text": "news5"}, {"text": "news6"}],
                "crypto": [],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "input_counts" in data

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_returns_404_when_no_content(self, mock_get_db, client):
        """Test that analyze endpoint returns 404 when no cached content exists."""
        # Mock DB to return None
        mock_get_db.return_value.get_latest_newsletter_with_articles.return_value = None

        response = client.get("/api/analyze")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No newsletter content available" in data["detail"]

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_returns_correct_structure(self, mock_get_db, client):
        """Test that analyze endpoint returns correctly structured response."""
        # Mock DB to return newsletter data
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"text": "n1", "source": "CNBC"}],
                "israel": [{"text": "n2", "source": "Globes"}],
                "ai": [{"text": "n3", "source": "TechCrunch"}],
                "crypto": [],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze")
        data = response.json()

        assert "success" in data
        assert "data" in data
        assert "input_counts" in data
        assert "us_news" in data["input_counts"]
        assert "israel_news" in data["input_counts"]
        assert "ai_news" in data["input_counts"]

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_counts_inputs_correctly(self, mock_get_db, client):
        """Test that input counts are calculated from DB articles."""
        # Mock DB to return newsletter with specific article counts
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"text": "1"}, {"text": "2"}, {"text": "3"}],
                "israel": [{"text": "a"}, {"text": "b"}],
                "ai": [{"text": "x"}, {"text": "y"}, {"text": "z"}, {"text": "w"}],
                "crypto": [],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze")
        data = response.json()

        assert data["input_counts"]["us_news"] == 3
        assert data["input_counts"]["israel_news"] == 2
        assert data["input_counts"]["ai_news"] == 4

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_returns_sentiment(self, mock_get_db, client):
        """Test that analyze endpoint returns sentiment from DB."""
        # Mock DB to return newsletter with sentiment
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"text": "news1"}],
                "israel": [{"text": "news2"}],
                "ai": [{"text": "news3"}],
                "crypto": [],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze")

        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data["data"]
        assert data["data"]["sentiment"]["us"] == 65

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_includes_source_metadata(self, mock_get_db, client):
        """Test that analyze endpoint includes sources_metadata in response."""
        # Mock DB to return newsletter with articles
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [
                    {
                        "source": "CNBC",
                        "published_at": "2025-11-28T10:00:00",
                        "text": "US News 1",
                        "ai_title": "US Title 1",
                    },
                    {
                        "source": "WSJ",
                        "published_at": "2025-11-28T11:00:00",
                        "text": "US News 2",
                        "ai_title": "US Title 2",
                    },
                ],
                "israel": [
                    {
                        "source": "Globes",
                        "published_at": "2025-11-28T09:00:00",
                        "text": "IL News 1",
                        "ai_title": "IL Title",
                    }
                ],
                "ai": [
                    {
                        "source": "TechCrunch",
                        "published_at": "2025-11-28T12:00:00",
                        "text": "AI News 1",
                        "ai_title": "AI Title",
                    }
                ],
                "crypto": [],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze")
        data = response.json()

        # Verify sources_metadata is included in response
        assert response.status_code == 200
        assert data["success"] is True
        assert "sources_metadata" in data["data"]
        assert "us" in data["data"]["sources_metadata"]
        assert "israel" in data["data"]["sources_metadata"]
        assert "ai" in data["data"]["sources_metadata"]

        # Verify metadata structure
        us_metadata = data["data"]["sources_metadata"]["us"]
        assert len(us_metadata) == 2
        assert us_metadata[0]["source"] == "CNBC"
        assert us_metadata[0]["published_at"] == "2025-11-28T10:00:00"
        assert us_metadata[1]["source"] == "WSJ"

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_returns_cache_metadata(self, mock_get_db, client):
        """Test that analyze endpoint returns cache metadata with created_at."""
        # Mock DB to return newsletter
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"source": "CNBC", "text": "US News", "ai_title": "US Title"}],
                "israel": [],
                "ai": [],
                "crypto": [],
            },
            "sentiment": {"us": 65},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Cache metadata should be present
        assert "cache_metadata" in data
        assert data["cache_metadata"]["is_cached"] is True
        assert data["cache_metadata"]["created_at"] == "2026-01-27T12:00:00"
        assert "last_generated_at" in data["cache_metadata"]


class TestAnalyzeDBFirstBehavior:
    """Tests for /api/analyze DB-first lookup behavior."""

    @patch("backend.routes.api.get_db_service")
    def test_analyze_checks_db_first(self, mock_get_db, client):
        """Test that analyze endpoint checks DB before file cache."""
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"source": "CNBC", "ai_title": "US News"}],
                "israel": [],
                "ai": [],
                "crypto": [],
            },
            "sentiment": {"us": 65},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Verify DB was checked
        mock_db.get_latest_newsletter_with_articles.assert_called_once()
        # Verify input_counts is included
        assert "input_counts" in data
        assert data["input_counts"]["us_news"] == 1

    @patch("backend.routes.api.get_db_service")
    def test_analyze_includes_last_generated_at(self, mock_get_db, client):
        """Test that analyze response includes last_generated_at in cache_metadata."""
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {"us": [], "israel": [], "ai": [], "crypto": []},
            "sentiment": {},
            "llm_provider": "gemini",
            "created_at": "2026-01-27T14:30:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze")

        assert response.status_code == 200
        data = response.json()
        assert "cache_metadata" in data
        assert "last_generated_at" in data["cache_metadata"]
        assert data["cache_metadata"]["last_generated_at"] == "2026-01-27T14:30:00"

    @patch("backend.routes.api.get_db_service")
    def test_analyze_filters_by_categories(self, mock_get_db, client):
        """Test that analyze filters DB results by requested categories."""
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"source": "CNBC"}],
                "israel": [{"source": "Globes"}],
                "ai": [{"source": "TechCrunch"}],
                "crypto": [{"source": "CoinDesk"}],
            },
            "sentiment": {"us": 65, "israel": 48, "ai": 72, "crypto": 55},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        # Request only US and AI
        response = client.get("/api/analyze?categories=us,ai")

        assert response.status_code == 200
        data = response.json()
        # Should only include requested categories
        assert "us" in data["data"]["sources_metadata"]
        assert "ai" in data["data"]["sources_metadata"]
        assert "israel" not in data["data"]["sources_metadata"]
        assert "crypto" not in data["data"]["sources_metadata"]
        # Sentiment should also be filtered
        assert "us" in data["data"]["sentiment"]
        assert "ai" in data["data"]["sentiment"]
        assert "israel" not in data["data"]["sentiment"]


class TestLatestContentEndpoint:
    """Tests for /api/content/latest endpoint."""

    @patch("backend.routes.api.get_db_service")
    def test_latest_content_returns_newsletter_data(self, mock_get_db, client):
        """Test that latest content endpoint returns newsletter from DB."""
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1, "language": "en"},
            "sources_metadata": {
                "us": [{"source": "CNBC", "ai_title": "US News"}],
                "israel": [],
                "ai": [],
                "crypto": [],
            },
            "sentiment": {"us": 65},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {
            "us": [0, 0, 0, 0, 0, 0, 65],
            "israel": [0, 0, 0, 0, 0, 0, 0],
            "ai": [0, 0, 0, 0, 0, 0, 0],
            "crypto": [0, 0, 0, 0, 0, 0, 0],
        }

        response = client.get("/api/content/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "sources_metadata" in data["data"]
        assert data["data"]["sources_metadata"]["us"][0]["source"] == "CNBC"
        assert data["data"]["sentiment"]["us"] == 65
        assert data["data"]["llm_provider"] == "openai"

    @patch("backend.routes.api.get_db_service")
    def test_latest_content_returns_404_when_empty(self, mock_get_db, client):
        """Test that latest content returns 404 when no newsletters exist."""
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = None

        response = client.get("/api/content/latest")

        assert response.status_code == 404
        data = response.json()
        assert "No newsletters available" in data["detail"]

    @patch("backend.routes.api.get_db_service")
    def test_latest_content_includes_cache_metadata(self, mock_get_db, client):
        """Test that latest content includes cache metadata."""
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {"us": [], "israel": [], "ai": [], "crypto": []},
            "sentiment": {},
            "llm_provider": "gemini",
            "created_at": "2026-01-27T14:30:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/content/latest")

        assert response.status_code == 200
        data = response.json()
        assert "cache_metadata" in data
        assert data["cache_metadata"]["is_cached"] is True
        assert data["cache_metadata"]["created_at"] == "2026-01-27T14:30:00"
        assert data["cache_metadata"]["last_generated_at"] == "2026-01-27T14:30:00"

    @patch("backend.routes.api.get_db_service")
    def test_latest_content_includes_sentiment_history(self, mock_get_db, client):
        """Test that latest content includes sentiment history."""
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {"us": [], "israel": [], "ai": [], "crypto": []},
            "sentiment": {},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {
            "us": [50, 55, 60, 65, 70, 75, 80],
            "israel": [40, 45, 50, 55, 60, 65, 70],
            "ai": [0, 0, 0, 0, 0, 0, 0],
            "crypto": [0, 0, 0, 0, 0, 0, 0],
        }

        response = client.get("/api/content/latest")

        assert response.status_code == 200
        data = response.json()
        assert "sentiment_history" in data
        assert data["sentiment_history"]["us"] == [50, 55, 60, 65, 70, 75, 80]

    @patch("backend.routes.api.get_db_service")
    def test_latest_content_handles_sentiment_history_error(self, mock_get_db, client):
        """Test that endpoint handles sentiment history errors gracefully."""
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {"us": [], "israel": [], "ai": [], "crypto": []},
            "sentiment": {},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.side_effect = Exception("DB error")

        response = client.get("/api/content/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["sentiment_history"] == {}


class TestAnalyzeAPICategoryFiltering:
    """Tests for /api/analyze endpoint category filtering (DB-based)."""

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_filters_by_category(self, mock_get_db, client):
        """Test that analyze endpoint filters DB results by requested category."""
        # Mock DB to return newsletter with all categories
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"text": "news1"}],
                "israel": [{"text": "news2"}],
                "ai": [{"text": "news3"}],
                "crypto": [{"text": "news4"}],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70, "crypto": 60},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze?categories=us")

        assert response.status_code == 200
        data = response.json()
        # Only US category should have content
        assert len(data["data"]["sources_metadata"]["us"]) == 1
        # Other categories should not be in the response (filtered out)
        assert "israel" not in data["data"]["sources_metadata"]
        assert "ai" not in data["data"]["sources_metadata"]
        assert "crypto" not in data["data"]["sources_metadata"]
        # Only US sentiment should be included
        assert "us" in data["data"]["sentiment"]
        assert "israel" not in data["data"]["sentiment"]

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_accepts_multiple_categories(self, mock_get_db, client):
        """Test that analyze endpoint accepts multiple categories."""
        # Mock DB to return newsletter with all categories
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"text": "news1"}],
                "israel": [{"text": "news2"}],
                "ai": [{"text": "news3"}],
                "crypto": [{"text": "news4"}],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70, "crypto": 60},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze?categories=us,ai")

        assert response.status_code == 200
        data = response.json()
        # US and AI should have content
        assert len(data["data"]["sources_metadata"]["us"]) == 1
        assert len(data["data"]["sources_metadata"]["ai"]) == 1
        # Israel and Crypto should not be in the response
        assert "israel" not in data["data"]["sources_metadata"]
        assert "crypto" not in data["data"]["sources_metadata"]

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_defaults_to_all_categories(self, mock_get_db, client):
        """Test that analyze endpoint returns all categories when none specified."""
        # Mock DB to return newsletter with all categories
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"text": "news1"}],
                "israel": [{"text": "news2"}],
                "ai": [{"text": "news3"}],
                "crypto": [{"text": "news4"}],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70, "crypto": 60},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze")

        assert response.status_code == 200
        data = response.json()
        # All categories should have content
        assert len(data["data"]["sources_metadata"]["us"]) == 1
        assert len(data["data"]["sources_metadata"]["israel"]) == 1
        assert len(data["data"]["sources_metadata"]["ai"]) == 1
        assert len(data["data"]["sources_metadata"]["crypto"]) == 1

    @patch("backend.routes.api.get_db_service")
    def test_analyze_endpoint_ignores_invalid_categories(self, mock_get_db, client):
        """Test that analyze endpoint ignores invalid category names."""
        # Mock DB to return newsletter
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"text": "news1"}],
                "israel": [{"text": "news2"}],
                "ai": [{"text": "news3"}],
                "crypto": [{"text": "news4"}],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70, "crypto": 60},
            "llm_provider": "openai",
            "created_at": "2026-01-27T12:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.get("/api/analyze?categories=us,invalid,fake")

        assert response.status_code == 200
        data = response.json()
        # Only US should have content (invalid categories ignored)
        assert len(data["data"]["sources_metadata"]["us"]) == 1
        # Other categories should not be in the response
        assert "israel" not in data["data"]["sources_metadata"]
        assert "ai" not in data["data"]["sources_metadata"]
        assert "crypto" not in data["data"]["sources_metadata"]

    def test_newsletter_page_contains_filter_checkboxes(self, client):
        """Test that newsletter page contains filter checkbox elements."""
        response = client.get("/newsletter")
        html = response.text
        assert_in_html('class="filter-section"', html, "Missing filter-section")
        assert_in_html('class="filter-toggles"', html, "Missing filter-toggles")
        assert_in_html('id="filter-us"', html, "Missing filter-us")
        assert_in_html('id="filter-israel"', html, "Missing filter-israel")
        assert_in_html('id="filter-ai"', html, "Missing filter-ai")
        assert_in_html('id="filter-crypto"', html, "Missing filter-crypto")

    def test_index_page_cta_button_has_id(self, client):
        """Test that CTA button has id for JavaScript control."""
        response = client.get("/")
        html = response.text
        assert_in_html('id="get-newsletter-btn"', html, "Missing get-newsletter-btn id")


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_endpoint_returns_200(self, client):
        """Test that health endpoint returns 200 status code."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_includes_scheduler_status(self, client):
        """Test that health endpoint includes scheduler status."""
        response = client.get("/health")
        data = response.json()

        assert "checks" in data
        assert "scheduler" in data["checks"]
        assert "status" in data["checks"]["scheduler"]

    def test_health_endpoint_scheduler_has_jobs(self, client):
        """Test that scheduler shows scheduled jobs in health check."""
        response = client.get("/health")
        data = response.json()

        scheduler_status = data["checks"]["scheduler"]
        # Scheduler should be running with jobs when app starts
        if scheduler_status["status"] == "healthy":
            assert "jobs" in scheduler_status
            assert len(scheduler_status["jobs"]) == 4  # 11, 14, 18, 20 UTC


class TestAdminRefreshEndpoint:
    """Tests for /api/admin/refresh endpoint."""

    def test_admin_refresh_requires_api_key(self, client):
        """Test that admin refresh requires X-Admin-Key header."""
        response = client.post("/api/admin/refresh")
        assert response.status_code == 422  # Missing required header

    @patch("backend.routes.api.config")
    def test_admin_refresh_rejects_invalid_api_key(self, mock_config, client):
        """Test that admin refresh rejects invalid API key."""
        mock_config.admin_api_key = "correct-key"

        response = client.post(
            "/api/admin/refresh",
            headers={"X-Admin-Key": "wrong-key"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid API key" in data["detail"]

    @patch("backend.routes.api.config")
    def test_admin_refresh_fails_when_not_configured(self, mock_config, client):
        """Test that admin refresh fails when ADMIN_API_KEY not set."""
        mock_config.admin_api_key = ""

        response = client.post(
            "/api/admin/refresh",
            headers={"X-Admin-Key": "any-key"},
        )

        assert response.status_code == 500
        data = response.json()
        assert "not configured" in data["detail"]

    @patch("backend.routes.api.get_db_service")
    @patch("backend.routes.api.run_content_generation_async", new_callable=AsyncMock)
    @patch("backend.routes.api.config")
    def test_admin_refresh_returns_fresh_content(
        self, mock_config, mock_run_job, mock_get_db, client
    ):
        """Test that admin refresh generates and returns fresh content."""
        mock_config.admin_api_key = "test-admin-key"
        mock_run_job.return_value = {
            "success": True,
            "duration_seconds": 45.5,
            "article_counts": {"us": 3, "israel": 2, "ai": 4, "crypto": 1},
            "podcast_generated": True,
        }
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {
                "us": [{"text": "news1"}],
                "israel": [{"text": "news2"}],
                "ai": [{"text": "news3"}],
                "crypto": [],
            },
            "sentiment": {"us": 65, "israel": 55, "ai": 70},
            "llm_provider": "openai",
            "created_at": "2026-01-29T14:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        response = client.post(
            "/api/admin/refresh",
            headers={"X-Admin-Key": "test-admin-key"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "sources_metadata" in data["data"]
        assert "generation_result" in data
        assert data["generation_result"]["duration_seconds"] == 45.5

    @patch("backend.routes.api._last_admin_refresh_time", None)
    @patch("backend.routes.api.get_db_service")
    @patch("backend.routes.api.run_content_generation_async", new_callable=AsyncMock)
    @patch("backend.routes.api.config")
    def test_admin_refresh_rate_limiting(self, mock_config, mock_run_job, mock_get_db, client):
        """Test that admin refresh enforces rate limiting."""
        import backend.routes.api as api_module

        mock_config.admin_api_key = "test-admin-key"
        mock_run_job.return_value = {"success": True, "duration_seconds": 30}
        mock_db = mock_get_db.return_value
        mock_db.get_latest_newsletter_with_articles.return_value = {
            "newsletter": {"id": 1},
            "sources_metadata": {"us": [], "israel": [], "ai": [], "crypto": []},
            "sentiment": {},
            "llm_provider": "openai",
            "created_at": "2026-01-29T14:00:00",
        }
        mock_db.get_sentiment_history.return_value = {}

        # First request should succeed
        response1 = client.post(
            "/api/admin/refresh",
            headers={"X-Admin-Key": "test-admin-key"},
        )
        assert response1.status_code == 200

        # Second request immediately after should be rate limited
        response2 = client.post(
            "/api/admin/refresh",
            headers={"X-Admin-Key": "test-admin-key"},
        )
        assert response2.status_code == 429
        data = response2.json()
        assert "Rate limit exceeded" in data["detail"]

        # Reset the rate limit tracker for other tests
        api_module._last_admin_refresh_time = None
