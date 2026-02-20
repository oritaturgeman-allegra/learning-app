"""
Unit tests for config module.
"""

import pytest
from unittest.mock import patch
from backend.config import AppConfig, _clean_database_url
from backend.exceptions import ConfigurationError


class TestCleanDatabaseUrl:
    """Tests for _clean_database_url helper function."""

    def test_removes_pgbouncer_param(self):
        """Test that pgbouncer parameter is removed from URL."""
        url = "postgresql://user:pass@host:5432/db?pgbouncer=true"
        result = _clean_database_url(url)
        assert result == "postgresql://user:pass@host:5432/db"
        assert "pgbouncer" not in result

    def test_preserves_other_params(self):
        """Test that other parameters are preserved when pgbouncer is removed."""
        url = "postgresql://user:pass@host:5432/db?pgbouncer=true&sslmode=require"
        result = _clean_database_url(url)
        assert "sslmode=require" in result
        assert "pgbouncer" not in result

    def test_preserves_params_when_pgbouncer_last(self):
        """Test that params are preserved when pgbouncer is the last param."""
        url = "postgresql://user:pass@host:5432/db?sslmode=require&pgbouncer=true"
        result = _clean_database_url(url)
        assert "sslmode=require" in result
        assert "pgbouncer" not in result

    def test_no_change_without_pgbouncer(self):
        """Test that URL without pgbouncer is unchanged."""
        url = "postgresql://user:pass@host:5432/db?sslmode=require"
        result = _clean_database_url(url)
        assert result == url

    def test_sqlite_url_unchanged(self):
        """Test that SQLite URLs are not modified."""
        url = "sqlite:///data/newsletter.db"
        result = _clean_database_url(url)
        assert result == url

    def test_empty_string_unchanged(self):
        """Test that empty string is handled."""
        result = _clean_database_url("")
        assert result == ""

    def test_url_without_query_params(self):
        """Test that URL without query params is unchanged."""
        url = "postgresql://user:pass@host:5432/db"
        result = _clean_database_url(url)
        assert result == url


class TestAppConfig:
    """Tests for AppConfig dataclass."""

    @patch("backend.config.load_dotenv")
    @patch("backend.config.os.getenv")
    def test_from_env_with_all_defaults(self, mock_getenv, mock_load_dotenv):
        """Test loading configuration with only required API key and all defaults."""

        def getenv_side_effect(key, default=None):
            if key == "OPENAI_API_KEY":
                return "sk-test-api-key-123"
            return default

        mock_getenv.side_effect = getenv_side_effect

        config = AppConfig.from_env()

        assert config.openai_api_key == "sk-test-api-key-123"
        assert config.feed_timeout == 10
        assert config.feed_max_workers == 5
        assert config.intraday_hours == 12
        assert config.newsletter_cache_ttl == 3600
        assert config.audio_cache_ttl == 86400  # 24 hours (outlasts scheduler gaps)
        assert config.max_articles_per_category == 5
        assert config.tts_model == "tts-1-hd"
        assert config.tts_voice_alex == "nova"
        assert config.tts_voice_guy == "fable"
        assert config.flask_host == "0.0.0.0"
        assert config.flask_port == 5000
        assert config.flask_debug is False
        mock_load_dotenv.assert_called_once()

    @patch("backend.config.load_dotenv")
    @patch("backend.config.os.getenv")
    def test_from_env_with_custom_values(self, mock_getenv, mock_load_dotenv):
        """Test loading configuration with custom environment variables."""

        def getenv_side_effect(key, default=None):
            env_values = {
                "OPENAI_API_KEY": "sk-custom-key",
                "FEED_TIMEOUT": "20",
                "FEED_MAX_WORKERS": "10",
                "INTRADAY_HOURS": "24",
                "NEWSLETTER_CACHE_TTL": "7200",
                "AUDIO_CACHE_TTL": "172800",
                "MAX_ARTICLES_PER_CATEGORY": "15",
                "TTS_MODEL": "tts-1",
                "TTS_VOICE_ALEX": "shimmer",
                "TTS_VOICE_GUY": "echo",
                "FLASK_HOST": "localhost",
                "FLASK_PORT": "8080",
                "FLASK_DEBUG": "true",
            }
            return env_values.get(key, default)

        mock_getenv.side_effect = getenv_side_effect

        config = AppConfig.from_env()

        assert config.openai_api_key == "sk-custom-key"
        assert config.feed_timeout == 20
        assert config.feed_max_workers == 10
        assert config.intraday_hours == 24
        assert config.newsletter_cache_ttl == 7200
        assert config.audio_cache_ttl == 172800
        assert config.max_articles_per_category == 15
        assert config.tts_model == "tts-1"
        assert config.tts_voice_alex == "shimmer"
        assert config.tts_voice_guy == "echo"
        assert config.flask_host == "localhost"
        assert config.flask_port == 8080
        assert config.flask_debug is True

    @patch("backend.config.load_dotenv")
    @patch("backend.config.os.getenv")
    def test_from_env_missing_api_key(self, mock_getenv, mock_load_dotenv):
        """Test that ConfigurationError is raised when API key is missing."""
        mock_getenv.return_value = None

        with pytest.raises(ConfigurationError) as exc_info:
            AppConfig.from_env()

        assert "OPENAI_API_KEY" in str(exc_info.value)
        assert "required" in str(exc_info.value).lower()

    def test_validate_valid_config(self):
        """Test validation passes for valid configuration."""
        config = AppConfig(
            openai_api_key="sk-test-key-123",
            feed_timeout=10,
            feed_max_workers=5,
            intraday_hours=12,
            newsletter_cache_ttl=3600,
            audio_cache_ttl=86400,
            max_articles_per_category=10,
            flask_port=5000,
        )

        # Should not raise any exception
        config.validate()

    def test_validate_invalid_feed_timeout(self):
        """Test validation fails for invalid feed timeout."""
        config = AppConfig(
            openai_api_key="sk-test-key", feed_timeout=0  # Invalid: must be positive
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "feed_timeout" in str(exc_info.value)

    def test_validate_invalid_feed_max_workers(self):
        """Test validation fails for invalid feed_max_workers."""
        config = AppConfig(
            openai_api_key="sk-test-key", feed_max_workers=-1  # Invalid: must be positive
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "feed_max_workers" in str(exc_info.value)

    def test_validate_invalid_intraday_hours(self):
        """Test validation fails for invalid intraday_hours."""
        config = AppConfig(
            openai_api_key="sk-test-key", intraday_hours=0  # Invalid: must be positive
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "intraday_hours" in str(exc_info.value)

    def test_validate_negative_cache_ttl(self):
        """Test validation fails for negative cache TTL."""
        config = AppConfig(
            openai_api_key="sk-test-key", newsletter_cache_ttl=-1  # Invalid: must be non-negative
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "newsletter_cache_ttl" in str(exc_info.value)

    def test_validate_invalid_port(self):
        """Test validation fails for invalid Flask port."""
        config = AppConfig(
            openai_api_key="sk-test-key", flask_port=99999  # Invalid: must be <= 65535
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "flask_port" in str(exc_info.value)

    def test_validate_invalid_api_key_format(self):
        """Test validation fails for invalid API key format."""
        config = AppConfig(
            openai_api_key="invalid-key-no-sk-prefix"  # Invalid: must start with 'sk-'
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "openai_api_key" in str(exc_info.value)
        assert "sk-" in str(exc_info.value)

    def test_mask_api_key_standard(self):
        """Test API key masking for standard length key."""
        config = AppConfig(openai_api_key="sk-proj-1234567890abcdef")

        masked = config.mask_api_key()

        assert masked == "sk-pr...def"
        assert "1234567890" not in masked
        assert "sk-proj-1234567890abcdef" not in masked

    def test_mask_api_key_short(self):
        """Test API key masking for very short key."""
        config = AppConfig(openai_api_key="sk-test")

        masked = config.mask_api_key()

        assert masked == "***"

    def test_mask_api_key_exact_8_chars(self):
        """Test API key masking for exactly 8 character key."""
        config = AppConfig(openai_api_key="sk-12345")

        masked = config.mask_api_key()

        # Should show first 5 and last 3
        assert masked == "sk-12...345"


class TestConfigModule:
    """Tests for global config instance."""

    def test_global_config_exists(self):
        """Test that global config instance exists."""
        from backend.config import config

        assert config is not None
        assert isinstance(config, AppConfig)

    def test_global_config_has_api_key(self):
        """Test that global config has API key (from .env)."""
        from backend.config import config

        assert config.openai_api_key is not None
        assert len(config.openai_api_key) > 0

    def test_backward_compatibility_openai_api_key(self):
        """Test that OPENAI_API_KEY export still works for backward compatibility."""
        from backend.config import OPENAI_API_KEY

        assert OPENAI_API_KEY is not None
        assert len(OPENAI_API_KEY) > 0

    def test_validate_config_function_exists(self):
        """Test that validate_config() function still exists for backward compatibility."""
        from backend.config import validate_config

        # Should not raise exception
        validate_config()


class TestCrossFieldValidation:
    """Tests for cross-field configuration validation."""

    def test_validate_email_config_incomplete(self):
        """Test validation fails when EMAIL_API_KEY set but EMAIL_FROM_ADDRESS missing."""
        config = AppConfig(
            openai_api_key="sk-test-key",
            email_api_key="SG.test-key",
            email_from_address="",  # Missing
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "email_from_address" in str(exc_info.value)
        assert "EMAIL_API_KEY" in str(exc_info.value)

    def test_validate_email_config_complete(self):
        """Test validation passes when email config is complete."""
        config = AppConfig(
            openai_api_key="sk-test-key",
            email_api_key="SG.test-key",
            email_from_address="test@example.com",
        )

        # Should not raise
        config.validate()

    def test_validate_oauth_missing_secret(self):
        """Test validation fails when GOOGLE_CLIENT_ID set but SECRET missing."""
        config = AppConfig(
            openai_api_key="sk-test-key",
            google_client_id="123456.apps.googleusercontent.com",
            google_client_secret="",  # Missing
            google_redirect_uri="http://localhost:5000/callback",
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "google_client_secret" in str(exc_info.value)

    def test_validate_oauth_missing_redirect_uri(self):
        """Test validation fails when GOOGLE_CLIENT_ID set but REDIRECT_URI missing."""
        config = AppConfig(
            openai_api_key="sk-test-key",
            google_client_id="123456.apps.googleusercontent.com",
            google_client_secret="GOCSPX-secret",
            google_redirect_uri="",  # Missing
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "google_redirect_uri" in str(exc_info.value)

    def test_validate_oauth_config_complete(self):
        """Test validation passes when OAuth config is complete."""
        config = AppConfig(
            openai_api_key="sk-test-key",
            google_client_id="123456.apps.googleusercontent.com",
            google_client_secret="GOCSPX-secret",
            google_redirect_uri="http://localhost:5000/callback",
        )

        # Should not raise
        config.validate()

    def test_validate_rate_limit_invalid_login_max(self):
        """Test validation fails for invalid rate_limit_login_max."""
        config = AppConfig(
            openai_api_key="sk-test-key",
            rate_limit_enabled=True,
            rate_limit_login_max=0,  # Invalid
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "rate_limit_login_max" in str(exc_info.value)

    def test_validate_rate_limit_invalid_login_window(self):
        """Test validation fails for invalid rate_limit_login_window."""
        config = AppConfig(
            openai_api_key="sk-test-key",
            rate_limit_enabled=True,
            rate_limit_login_window=-1,  # Invalid
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        assert "rate_limit_login_window" in str(exc_info.value)

    def test_validate_rate_limit_disabled_skips_validation(self):
        """Test that rate limit validation is skipped when disabled."""
        config = AppConfig(
            openai_api_key="sk-test-key",
            rate_limit_enabled=False,
            rate_limit_login_max=0,  # Would be invalid if enabled
            rate_limit_login_window=-1,  # Would be invalid if enabled
        )

        # Should not raise - rate limiting is disabled
        config.validate()
