"""
Unit tests for analytics job.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from backend.jobs.analytics_job import (
    AnalyticsJob,
    get_analytics_job,
    run_analytics,
)


@pytest.fixture
def job():
    """Create a fresh job instance for testing."""
    return AnalyticsJob()


@pytest.fixture
def mock_analysis_result():
    """Sample analysis result from AIAnalyticsService."""
    return {
        "success": True,
        "date": "2026-02-13",
        "summary": "Good performance overall.",
        "highlights": ["CNBC at 85%"],
        "action_items": [],
        "data": {
            "total_articles": 50,
            "total_selected": 20,
            "acceptance_rate": 0.40,
        },
    }


class TestAnalyticsJob:
    """Tests for AnalyticsJob class."""

    def test_job_initialization(self, job):
        """Job should initialize with None services (lazy loading)."""
        assert job._analytics_service is None
        assert job._email_service is None

    @patch("backend.jobs.analytics_job.get_db_service")
    @patch("backend.jobs.analytics_job.get_analytics_service")
    @patch("backend.jobs.analytics_job.get_email_service")
    def test_run_success(
        self,
        mock_email_service,
        mock_analytics_service,
        mock_db_service,
        job,
        mock_analysis_result,
    ):
        """Job should complete successfully with all steps."""
        # Setup mocks
        mock_analytics = MagicMock()
        mock_analytics.analyze_feed_providers.return_value = mock_analysis_result
        mock_analytics_service.return_value = mock_analytics

        mock_email = MagicMock()
        mock_email.send_analytics_report = AsyncMock(return_value=True)
        mock_email_service.return_value = mock_email

        mock_db = MagicMock()
        mock_db_service.return_value = mock_db

        # Run job
        result = job.run()

        # Verify
        assert result["success"] is True
        assert result["analysis_success"] is True
        assert result["email_sent"] is True
        assert "duration_seconds" in result
        mock_db.save_analytics_report.assert_called_once()

    @patch("backend.jobs.analytics_job.get_analytics_service")
    @patch("backend.jobs.analytics_job.get_email_service")
    def test_run_no_data(
        self,
        mock_email_service,
        mock_analytics_service,
        job,
    ):
        """Job should handle case when no analysis data is available."""
        # Setup mocks
        mock_analytics = MagicMock()
        mock_analytics.analyze_feed_providers.return_value = {
            "success": False,
            "error": "No data available",
            "date": "2026-02-13",
        }
        mock_analytics_service.return_value = mock_analytics

        mock_email = MagicMock()
        mock_email_service.return_value = mock_email

        # Run job
        result = job.run()

        # Verify - job succeeds but no email sent
        assert result["success"] is True
        assert result["analysis_success"] is False
        assert result["email_sent"] is False
        # Email should not have been called
        mock_email.send_analytics_report.assert_not_called()

    @patch("backend.jobs.analytics_job.get_db_service")
    @patch("backend.jobs.analytics_job.get_analytics_service")
    @patch("backend.jobs.analytics_job.get_email_service")
    def test_run_email_fails(
        self,
        mock_email_service,
        mock_analytics_service,
        mock_db_service,
        job,
        mock_analysis_result,
    ):
        """Job should handle email sending failure gracefully."""
        # Setup mocks
        mock_analytics = MagicMock()
        mock_analytics.analyze_feed_providers.return_value = mock_analysis_result
        mock_analytics_service.return_value = mock_analytics

        mock_email = MagicMock()
        mock_email.send_analytics_report = AsyncMock(return_value=False)
        mock_email_service.return_value = mock_email

        mock_db_service.return_value = MagicMock()

        # Run job
        result = job.run()

        # Verify - job succeeds but email not sent
        assert result["success"] is True
        assert result["analysis_success"] is True
        assert result["email_sent"] is False

    @patch("backend.jobs.analytics_job.get_analytics_service")
    def test_run_analysis_exception(
        self,
        mock_analytics_service,
        job,
    ):
        """Job should handle analysis exceptions."""
        # Setup mock to raise exception
        mock_analytics = MagicMock()
        mock_analytics.analyze_feed_providers.side_effect = Exception("API error")
        mock_analytics_service.return_value = mock_analytics

        # Run job
        result = job.run()

        # Verify
        assert result["success"] is False
        assert "Analysis failed" in result.get("error", "")


class TestGetAnalyticsJob:
    """Tests for singleton getter."""

    def test_returns_same_instance(self):
        """Should return the same singleton instance."""
        job1 = get_analytics_job()
        job2 = get_analytics_job()
        assert job1 is job2


class TestRunAnalytics:
    """Tests for run_analytics entry point."""

    @patch("backend.jobs.analytics_job.get_analytics_job")
    def test_run_analytics_calls_job(self, mock_get_job):
        """run_analytics should call job.run()."""
        mock_job = MagicMock()
        mock_job.run.return_value = {"success": True}
        mock_get_job.return_value = mock_job

        result = run_analytics()

        mock_job.run.assert_called_once()
        assert result["success"] is True
