"""
Tests for configuration module.
"""

import pytest

from backend.config import _clean_database_url, AppConfig
from backend.exceptions import ConfigurationError


class TestCleanDatabaseUrl:
    """Tests for _clean_database_url()."""

    def test_sqlite_url_unchanged(self):
        """SQLite URLs are returned as-is."""
        url = "sqlite:///data/learning.db"
        assert _clean_database_url(url) == url

    def test_empty_url_unchanged(self):
        """Empty string is returned as-is."""
        assert _clean_database_url("") == ""

    def test_strips_pgbouncer_param(self):
        """pgbouncer=true is removed from Postgres URLs."""
        url = "postgresql://user:pass@host:5432/db?pgbouncer=true"
        cleaned = _clean_database_url(url)
        assert "pgbouncer" not in cleaned
        assert "postgresql://user:pass@host:5432/db" in cleaned

    def test_preserves_other_params(self):
        """Other query params are preserved when stripping pgbouncer."""
        url = "postgresql://user:pass@host:5432/db?pgbouncer=true&sslmode=require"
        cleaned = _clean_database_url(url)
        assert "pgbouncer" not in cleaned
        assert "sslmode=require" in cleaned

    def test_url_without_params_unchanged(self):
        """Postgres URL without query params is returned as-is."""
        url = "postgresql://user:pass@host:5432/db"
        assert _clean_database_url(url) == url


class TestAppConfigValidation:
    """Tests for AppConfig.validate()."""

    def test_valid_config_passes(self):
        """Valid config does not raise."""
        config = AppConfig(flask_port=8000)
        config.validate()  # Should not raise

    def test_port_zero_raises(self):
        """Port 0 raises ConfigurationError."""
        config = AppConfig(flask_port=0)
        with pytest.raises(ConfigurationError, match="flask_port"):
            config.validate()

    def test_port_negative_raises(self):
        """Negative port raises ConfigurationError."""
        config = AppConfig(flask_port=-1)
        with pytest.raises(ConfigurationError, match="flask_port"):
            config.validate()

    def test_port_too_high_raises(self):
        """Port above 65535 raises ConfigurationError."""
        config = AppConfig(flask_port=70000)
        with pytest.raises(ConfigurationError, match="flask_port"):
            config.validate()

    def test_port_max_valid(self):
        """Port 65535 is valid."""
        config = AppConfig(flask_port=65535)
        config.validate()  # Should not raise
