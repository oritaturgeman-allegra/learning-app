"""
Unit tests for scheduler service.
"""

import pytest
from unittest.mock import patch

from backend.config import config
from backend.services.scheduler_service import SchedulerService, get_scheduler_service


@pytest.fixture
def scheduler_service():
    """Create a fresh scheduler service instance for testing."""
    service = SchedulerService()
    yield service
    # Cleanup: ensure scheduler is stopped
    if service.is_running():
        service.shutdown()


class TestSchedulerInitialization:
    """Test scheduler service initialization."""

    def test_scheduler_not_running_initially(self, scheduler_service):
        """Scheduler should not be running before start() is called."""
        assert scheduler_service.is_running() is False

    def test_get_status_before_start(self, scheduler_service):
        """Status should show not running before start."""
        status = scheduler_service.get_status()
        assert status["status"] == "unhealthy"
        assert status["running"] is False
        assert status["jobs"] == []


class TestSchedulerStart:
    """Test scheduler start functionality."""

    def test_start_creates_jobs(self, scheduler_service):
        """Starting scheduler should create jobs for configured hours plus analytics."""
        scheduler_service.start()

        assert scheduler_service.is_running() is True
        status = scheduler_service.get_status()
        assert status["status"] == "healthy"
        assert status["running"] is True
        # 4 content generation jobs + 1 analytics job = 5 total
        assert len(status["jobs"]) == len(config.schedule_hours_utc) + 1

    def test_start_twice_logs_warning(self, scheduler_service):
        """Starting scheduler twice should not create duplicate jobs."""
        scheduler_service.start()
        scheduler_service.start()  # Should log warning, not crash

        assert scheduler_service.is_running() is True
        status = scheduler_service.get_status()
        # 4 content generation jobs + 1 analytics job = 5 total
        assert len(status["jobs"]) == len(config.schedule_hours_utc) + 1

    @patch("backend.services.scheduler_service.config")
    def test_start_disabled_via_config(self, mock_config, scheduler_service):
        """Scheduler should not start if disabled in config."""
        mock_config.schedule_enabled = False

        scheduler_service.start()

        assert scheduler_service.is_running() is False


class TestSchedulerShutdown:
    """Test scheduler shutdown functionality."""

    def test_shutdown_stops_scheduler(self, scheduler_service):
        """Shutdown should stop the scheduler."""
        scheduler_service.start()
        assert scheduler_service.is_running() is True

        scheduler_service.shutdown()
        assert scheduler_service.is_running() is False

    def test_shutdown_when_not_running(self, scheduler_service):
        """Shutdown when not running should not crash."""
        scheduler_service.shutdown()  # Should not raise
        assert scheduler_service.is_running() is False


class TestSchedulerStatus:
    """Test scheduler status reporting."""

    def test_status_includes_scheduled_hours(self, scheduler_service):
        """Status should include configured schedule hours."""
        scheduler_service.start()
        status = scheduler_service.get_status()

        assert "scheduled_hours_utc" in status
        assert status["scheduled_hours_utc"] == list(config.schedule_hours_utc)

    def test_status_includes_timezone(self, scheduler_service):
        """Status should include timezone."""
        scheduler_service.start()
        status = scheduler_service.get_status()

        assert status["timezone"] == "UTC"

    def test_jobs_have_next_run_time(self, scheduler_service):
        """Each job should have a next_run time."""
        scheduler_service.start()
        status = scheduler_service.get_status()

        for job in status["jobs"]:
            assert "next_run" in job
            assert job["next_run"] is not None

    @patch("backend.services.scheduler_service.config")
    def test_status_when_disabled(self, mock_config):
        """Status should show disabled when scheduler is disabled."""
        mock_config.schedule_enabled = False

        service = SchedulerService()
        status = service.get_status()

        assert status["status"] == "disabled"
        assert status["enabled"] is False


class TestMisfireGraceTime:
    """Test misfire grace time configuration."""

    def test_jobs_have_misfire_grace_time(self, scheduler_service):
        """Jobs should be configured with misfire_grace_time from config."""
        scheduler_service.start()

        jobs = scheduler_service._scheduler.get_jobs()
        for job in jobs:
            assert job.misfire_grace_time == 900  # Default 15 minutes


class TestManualTrigger:
    """Test manual job triggering."""

    def test_trigger_now_when_running(self, scheduler_service):
        """Manual trigger should work when scheduler is running."""
        scheduler_service.start()

        result = scheduler_service.trigger_now()

        assert result is True

    def test_trigger_now_when_not_running(self, scheduler_service):
        """Manual trigger should fail when scheduler is not running."""
        result = scheduler_service.trigger_now()

        assert result is False


class TestSingleton:
    """Test singleton pattern."""

    def test_get_scheduler_service_returns_same_instance(self):
        """get_scheduler_service should return the same instance."""
        service1 = get_scheduler_service()
        service2 = get_scheduler_service()

        assert service1 is service2
