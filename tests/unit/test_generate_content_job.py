"""
Unit tests for content generation job.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from backend.jobs.generate_content_job import (
    ContentGenerationJob,
    get_content_generation_job,
    run_content_generation,
)


@pytest.fixture
def job():
    """Create a fresh job instance for testing."""
    return ContentGenerationJob()


@pytest.fixture
def mock_market_data():
    """Sample market data returned by fetch_market_data_async."""
    return {
        "raw_us_market_news": ["news1", "news2"],
        "raw_israel_market_news": ["news3"],
        "raw_ai_news": ["news4", "news5"],
        "raw_crypto_news": ["news6"],
        "articles_metadata": {
            "us": [{"text": "news1"}, {"text": "news2"}],
            "israel": [{"text": "news3"}],
            "ai": [{"text": "news4"}, {"text": "news5"}],
            "crypto": [{"text": "news6"}],
        },
        "source_stats": {"us": [], "israel": [], "ai": [], "crypto": []},
    }


@pytest.fixture
def mock_newsletter_content():
    """Sample newsletter content from AI service."""
    return {
        "ai_titles": {"us:0": "Title 1", "us:1": "Title 2"},
        "sentiment": {"us": 50, "israel": 60, "ai": 70, "crypto": 45},
    }


class TestContentGenerationJob:
    """Tests for ContentGenerationJob class."""

    def test_job_initialization(self, job):
        """Job should initialize with None services (lazy loading)."""
        assert job._ai_content_service is None

    @patch("backend.jobs.generate_content_job.fetch_market_data_async", new_callable=AsyncMock)
    @patch("backend.jobs.generate_content_job.AIContentService")
    @patch("backend.jobs.generate_content_job.get_db_service")
    def test_run_success(
        self,
        mock_db_service,
        mock_ai_class,
        mock_fetch,
        job,
        mock_market_data,
        mock_newsletter_content,
    ):
        """Job should complete successfully with all steps."""
        # Setup mocks
        mock_fetch.return_value = mock_market_data

        mock_ai = MagicMock()
        mock_ai.generate_newsletter_content.return_value = mock_newsletter_content
        mock_ai.apply_content_to_metadata.return_value = mock_market_data["articles_metadata"]
        mock_ai_class.return_value = mock_ai

        mock_db = MagicMock()
        mock_db_service.return_value = mock_db

        # Run job
        result = job.run()

        # Verify success
        assert result["success"] is True
        assert "job_id" in result
        assert "duration_seconds" in result
        assert result["article_counts"] == {"us": 2, "israel": 1, "ai": 2, "crypto": 1}

        # Verify services were called (no podcast generation)
        mock_fetch.assert_called_once()
        mock_ai.generate_newsletter_content.assert_called_once()
        mock_ai.generate_podcast_dialog.assert_not_called()
        mock_db.save_newsletter_with_stats.assert_called_once()

    @patch("backend.jobs.generate_content_job.fetch_market_data_async", new_callable=AsyncMock)
    def test_run_handles_rss_fetch_error(self, mock_fetch, job):
        """Job should handle RSS fetch errors gracefully."""
        from backend.exceptions import FeedFetchError

        mock_fetch.side_effect = FeedFetchError("http://test.com", "Connection failed")

        result = job.run()

        assert result["success"] is False
        assert "RSS fetch failed" in result["error"]

    @patch("backend.jobs.generate_content_job.fetch_market_data_async", new_callable=AsyncMock)
    @patch("backend.jobs.generate_content_job.AIContentService")
    def test_run_handles_ai_content_error(self, mock_ai_class, mock_fetch, job, mock_market_data):
        """Job should handle AI content generation errors gracefully."""
        mock_fetch.return_value = mock_market_data

        mock_ai = MagicMock()
        mock_ai.generate_newsletter_content.side_effect = Exception("LLM API error")
        mock_ai_class.return_value = mock_ai

        result = job.run()

        assert result["success"] is False
        assert "AI content generation failed" in result["error"]


class TestSingleton:
    """Test singleton pattern."""

    def test_get_content_generation_job_returns_same_instance(self):
        """get_content_generation_job should return same instance."""
        job1 = get_content_generation_job()
        job2 = get_content_generation_job()
        assert job1 is job2


class TestRunContentGeneration:
    """Test the entry point function."""

    @patch("backend.jobs.generate_content_job.get_content_generation_job")
    def test_run_content_generation_calls_job(self, mock_get_job):
        """run_content_generation should call the job's run method."""
        mock_job = MagicMock()
        mock_job.run.return_value = {"success": True}
        mock_get_job.return_value = mock_job

        result = run_content_generation()

        mock_job.run.assert_called_once()
        assert result["success"] is True
