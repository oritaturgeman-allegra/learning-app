"""
Custom exception classes for Ariel's English Adventure.
"""

from typing import Optional


class AppError(Exception):
    """Base exception for all application errors."""

    pass


class ConfigurationError(AppError):
    """Raised when application configuration is invalid or missing."""

    def __init__(self, config_key: str, reason: str):
        self.config_key = config_key
        self.reason = reason
        super().__init__(f"Configuration error for '{config_key}': {reason}")


class GameError(AppError):
    """Raised when game operations fail."""

    def __init__(self, operation: str, details: str):
        self.operation = operation
        self.details = details
        super().__init__(f"Game {operation} failed: {details}")
