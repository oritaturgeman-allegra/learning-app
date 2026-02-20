"""
Unit tests for AI Analytics Service.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from backend.services.ai_analytics_service import (
    AIAnalyticsService,
    get_analytics_service,
)

# Fixed test date to avoid time-dependent failures
TEST_DATE = datetime(2026, 2, 13, tzinfo=timezone.utc)


@pytest.fixture
def service():
    """Create a fresh service instance for testing."""
    return AIAnalyticsService()


@pytest.fixture
def mock_selection_summary():
    """Sample selection summary from database."""
    return {
        "date": "2026-02-13",
        "total_articles": 50,
        "total_selected": 20,
        "by_source": [
            {
                "source_name": "Yahoo Finance",
                "category": "us",
                "total": 15,
                "selected": 5,
                "acceptance_rate": 0.33,
                "rejected_titles": ["Lifestyle article", "Political news"],
            },
            {
                "source_name": "CNBC",
                "category": "us",
                "total": 10,
                "selected": 8,
                "acceptance_rate": 0.80,
                "rejected_titles": [],
            },
        ],
        "by_category": {
            "us": {"total": 25, "selected": 13, "acceptance_rate": 0.52},
            "ai": {"total": 15, "selected": 5, "acceptance_rate": 0.33},
            "crypto": {"total": 10, "selected": 2, "acceptance_rate": 0.20},
        },
    }


@pytest.fixture
def mock_lifetime_stats():
    """Sample lifetime feed provider stats."""
    return [
        {
            "source_name": "CNBC",
            "category": "us",
            "reliability": 0.85,
            "total_runs": 100,
            "success_count": 85,
        },
        {
            "source_name": "Yahoo Finance",
            "category": "us",
            "reliability": 0.45,
            "total_runs": 100,
            "success_count": 45,
        },
    ]


@pytest.fixture
def mock_llm_response():
    """Sample LLM analysis response."""
    return {
        "summary": "Good day overall with 40% acceptance rate.",
        "highlights": ["CNBC performing well at 80%"],
        "action_items": [
            {
                "priority": "medium",
                "action": "Review Yahoo Finance filters",
                "source": "Yahoo Finance",
                "category": "us",
                "reason": "Low acceptance rate with too much lifestyle content",
            }
        ],
    }


class TestAIAnalyticsService:
    """Tests for AIAnalyticsService class."""

    def test_service_initialization(self, service):
        """Service should initialize with None client (lazy loading)."""
        assert service._client is None

    @patch("backend.services.ai_analytics_service.get_db_service")
    def test_analyze_no_data(self, mock_db_service, service):
        """Should handle case when no data is available."""
        mock_db = MagicMock()
        mock_db.get_selection_summary_for_date.return_value = {
            "date": "2026-02-13",
            "total_articles": 0,
            "total_selected": 0,
            "by_source": [],
            "by_category": {},
        }
        mock_db_service.return_value = mock_db

        result = service.analyze_feed_providers()

        assert result["success"] is False
        assert "No data available" in result.get("error", "")

    @patch("backend.services.ai_analytics_service.get_db_service")
    @patch("backend.services.ai_analytics_service.OpenAI")
    def test_analyze_success(
        self,
        mock_openai_class,
        mock_db_service,
        service,
        mock_selection_summary,
        mock_lifetime_stats,
        mock_llm_response,
    ):
        """Should successfully analyze feed providers."""
        # Setup DB mock
        mock_db = MagicMock()
        mock_db.get_selection_summary_for_date.return_value = mock_selection_summary
        mock_db.get_feed_provider_stats.return_value = mock_lifetime_stats
        mock_db_service.return_value = mock_db

        # Setup OpenAI mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            '{"summary": "Test summary", "highlights": [], "action_items": []}'
        )
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        # Pass explicit date to avoid time-dependent failures
        result = service.analyze_feed_providers(target_date=TEST_DATE)

        assert result["success"] is True
        assert "summary" in result
        assert result["date"] == "2026-02-13"
        assert result["data"]["total_articles"] == 50

    def test_build_prompt(self, service, mock_selection_summary, mock_lifetime_stats):
        """Should build a proper prompt with data."""
        prompt = service._build_prompt(mock_selection_summary, mock_lifetime_stats)

        assert "2026-02-13" in prompt
        assert "50" in prompt  # total_articles
        assert "20" in prompt  # total_selected
        assert "Yahoo Finance" in prompt
        assert "CNBC" in prompt

    @patch("backend.services.ai_analytics_service.OpenAI")
    def test_call_llm_json_parse_error(self, mock_openai_class, service):
        """Should handle malformed JSON from LLM."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not valid json"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        result = service._call_llm("test prompt")

        assert "raw_response" in result
        assert len(result.get("action_items", [])) > 0
        assert "JSON parsing failed" in result["action_items"][0]["action"]


class TestGetAnalyticsService:
    """Tests for singleton getter."""

    def test_returns_same_instance(self):
        """Should return the same singleton instance."""
        service1 = get_analytics_service()
        service2 = get_analytics_service()
        assert service1 is service2
