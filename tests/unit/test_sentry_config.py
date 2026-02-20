"""
Unit tests for Sentry configuration and initialization.
"""

from unittest.mock import patch, MagicMock

from backend.sentry_config import init_sentry, _before_send, _scrub_data


class TestScrubData:
    """Tests for sensitive data scrubbing."""

    def test_scrubs_password_field(self) -> None:
        """Passwords are replaced with [Filtered]."""
        data = {"username": "user@test.com", "password": "secret123"}
        result = _scrub_data(data)
        assert result["username"] == "user@test.com"
        assert result["password"] == "[Filtered]"

    def test_scrubs_api_key_fields(self) -> None:
        """API keys are replaced with [Filtered]."""
        data = {
            "openai_api_key": "sk-abc123",
            "gemini_api_key": "gem-xyz",
            "email_api_key": "SG.xxx",
        }
        result = _scrub_data(data)
        for key in data:
            assert result[key] == "[Filtered]"

    def test_scrubs_nested_dicts(self) -> None:
        """Sensitive fields in nested dicts are scrubbed."""
        data = {
            "user": {
                "name": "Test",
                "password": "secret",
                "token": "abc123",
            }
        }
        result = _scrub_data(data)
        assert result["user"]["name"] == "Test"
        assert result["user"]["password"] == "[Filtered]"
        assert result["user"]["token"] == "[Filtered]"

    def test_preserves_non_sensitive_data(self) -> None:
        """Non-sensitive fields are preserved."""
        data = {"name": "test", "email": "test@example.com", "count": 42}
        result = _scrub_data(data)
        assert result == data

    def test_case_insensitive_matching(self) -> None:
        """Key matching is case-insensitive."""
        data = {"Password": "secret", "TOKEN": "abc"}
        result = _scrub_data(data)
        assert result["Password"] == "[Filtered]"
        assert result["TOKEN"] == "[Filtered]"

    def test_empty_dict(self) -> None:
        """Empty dict returns empty dict."""
        assert _scrub_data({}) == {}


class TestBeforeSend:
    """Tests for the Sentry before_send hook."""

    def test_scrubs_request_data(self) -> None:
        """Request body data is scrubbed."""
        event = {
            "request": {
                "url": "/api/auth/login",
                "method": "POST",
                "data": {"email": "test@test.com", "password": "secret"},
            }
        }
        result = _before_send(event, {})
        assert result is not None
        assert result["request"]["data"]["email"] == "test@test.com"
        assert result["request"]["data"]["password"] == "[Filtered]"

    def test_scrubs_request_headers(self) -> None:
        """Authorization headers are scrubbed."""
        event = {
            "request": {
                "headers": {
                    "content-type": "application/json",
                    "authorization": "Bearer token123",
                }
            }
        }
        result = _before_send(event, {})
        assert result is not None
        assert result["request"]["headers"]["content-type"] == "application/json"
        assert result["request"]["headers"]["authorization"] == "[Filtered]"

    def test_scrubs_cookies(self) -> None:
        """Cookies are fully scrubbed."""
        event = {"request": {"cookies": "session=abc123; token=xyz"}}
        result = _before_send(event, {})
        assert result is not None
        assert result["request"]["cookies"] == "[Filtered]"

    def test_scrubs_extra_context(self) -> None:
        """Extra context is scrubbed."""
        event = {
            "extra": {
                "api_key": "sk-secret",
                "endpoint": "/api/newsletter",
            }
        }
        result = _before_send(event, {})
        assert result is not None
        assert result["extra"]["api_key"] == "[Filtered]"
        assert result["extra"]["endpoint"] == "/api/newsletter"

    def test_returns_event_without_request(self) -> None:
        """Events without request data pass through."""
        event = {"message": "test error", "level": "error"}
        result = _before_send(event, {})
        assert result == event

    def test_handles_non_dict_request_data(self) -> None:
        """Non-dict request data is left alone."""
        event = {"request": {"data": "raw string body"}}
        result = _before_send(event, {})
        assert result is not None
        assert result["request"]["data"] == "raw string body"

    def test_filters_keyboard_interrupt(self) -> None:
        """KeyboardInterrupt exceptions are dropped (server shutdown)."""
        event = {"message": "KeyboardInterrupt"}
        hint = {"exc_info": (KeyboardInterrupt, KeyboardInterrupt(), None)}
        result = _before_send(event, hint)
        assert result is None

    def test_passes_other_exceptions(self) -> None:
        """Non-KeyboardInterrupt exceptions are kept."""
        event = {"message": "ValueError"}
        hint = {"exc_info": (ValueError, ValueError("test"), None)}
        result = _before_send(event, hint)
        assert result is not None

    def test_filters_keyboard_interrupt_log_message(self) -> None:
        """KeyboardInterrupt logged by uvicorn as message is dropped."""
        event = {"logentry": {"message": "Traceback... raise KeyboardInterrupt()"}}
        result = _before_send(event, {})
        assert result is None

    def test_passes_normal_log_messages(self) -> None:
        """Normal log messages are kept."""
        event = {"logentry": {"message": "Database connection established"}}
        result = _before_send(event, {})
        assert result is not None


class TestInitSentry:
    """Tests for Sentry initialization."""

    @patch("backend.sentry_config.sentry_sdk.init")
    def test_initializes_with_valid_dsn(self, mock_init: MagicMock) -> None:
        """Sentry initializes when DSN is provided."""
        result = init_sentry(
            dsn="https://test@sentry.io/123",
            environment="testing",
            traces_sample_rate=0.5,
        )
        assert result is True
        mock_init.assert_called_once()
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["dsn"] == "https://test@sentry.io/123"
        assert call_kwargs["environment"] == "testing"
        assert call_kwargs["traces_sample_rate"] == 0.5
        assert call_kwargs["send_default_pii"] is False
        assert call_kwargs["before_send"] == _before_send

    @patch("backend.sentry_config.sentry_sdk.init")
    def test_skips_initialization_without_dsn(self, mock_init: MagicMock) -> None:
        """Sentry is not initialized when DSN is empty."""
        result = init_sentry(dsn="")
        assert result is False
        mock_init.assert_not_called()

    @patch("backend.sentry_config.sentry_sdk.init")
    def test_includes_app_version_as_release(self, mock_init: MagicMock) -> None:
        """Release is set to APP_VERSION."""
        from backend.defaults import APP_VERSION

        init_sentry(dsn="https://test@sentry.io/123")
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["release"] == APP_VERSION

    @patch("backend.sentry_config.sentry_sdk.init")
    def test_default_parameters(self, mock_init: MagicMock) -> None:
        """Default environment and sample rate are applied."""
        init_sentry(dsn="https://test@sentry.io/123")
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["environment"] == "development"
        assert call_kwargs["traces_sample_rate"] == 0.1
