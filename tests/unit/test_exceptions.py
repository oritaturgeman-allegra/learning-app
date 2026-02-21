"""
Tests for custom exception classes.
"""

from backend.exceptions import AppError, ConfigurationError, GameError


class TestExceptions:
    """Tests for exception hierarchy and messages."""

    def test_app_error_is_exception(self):
        """AppError inherits from Exception."""
        err = AppError("test")
        assert isinstance(err, Exception)

    def test_configuration_error_message(self):
        """ConfigurationError includes key and reason."""
        err = ConfigurationError("flask_port", "Must be between 1 and 65535")
        assert "flask_port" in str(err)
        assert "Must be between 1 and 65535" in str(err)
        assert err.config_key == "flask_port"
        assert err.reason == "Must be between 1 and 65535"

    def test_game_error_message(self):
        """GameError includes operation and details."""
        err = GameError("save_result", "Invalid game type: bogus")
        assert "save_result" in str(err)
        assert "Invalid game type: bogus" in str(err)
        assert err.operation == "save_result"
        assert err.details == "Invalid game type: bogus"

    def test_game_error_is_app_error(self):
        """GameError inherits from AppError."""
        err = GameError("test", "details")
        assert isinstance(err, AppError)

    def test_configuration_error_is_app_error(self):
        """ConfigurationError inherits from AppError."""
        err = ConfigurationError("key", "reason")
        assert isinstance(err, AppError)
