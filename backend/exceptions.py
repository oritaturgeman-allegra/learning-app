# backend/exceptions.py
"""
Custom exception classes for the Capital Market Newsletter application.

This module defines a hierarchy of exceptions for better error handling
and debugging across the application.
"""

from typing import Any, Optional


class NewsletterError(Exception):
    """Base exception for all newsletter application errors."""

    pass


class FeedFetchError(NewsletterError):
    """
    Raised when RSS feed fetching fails.

    Attributes:
        url: The feed URL that failed to fetch
        reason: Human-readable reason for the failure
    """

    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch feed {url}: {reason}")


class AIGenerationError(NewsletterError):
    """
    Raised when AI content generation fails (OpenAI API errors).

    Attributes:
        operation: The AI operation that failed (e.g., "summary", "podcast")
        details: Optional error details from the API
    """

    def __init__(self, operation: str, details: Optional[str] = None):
        self.operation = operation
        self.details = details
        message = f"AI generation failed for operation '{operation}'"
        if details:
            message += f": {details}"
        super().__init__(message)


class CacheError(NewsletterError):
    """
    Raised when cache operations fail.

    Attributes:
        operation: The cache operation that failed (e.g., "get", "set", "delete")
        cache_key: The cache key involved
        details: Optional error details
    """

    def __init__(self, operation: str, cache_key: str, details: Optional[str] = None):
        self.operation = operation
        self.cache_key = cache_key
        self.details = details
        message = f"Cache {operation} failed for key '{cache_key}'"
        if details:
            message += f": {details}"
        super().__init__(message)


class TTSError(NewsletterError):
    """
    Raised when Text-to-Speech generation fails.

    Attributes:
        details: Error details from the TTS service
    """

    def __init__(self, details: str):
        self.details = details
        super().__init__(f"Text-to-Speech generation failed: {details}")


class ValidationError(NewsletterError):
    """
    Raised when input validation fails.

    Attributes:
        field: The field that failed validation
        value: The invalid value
        constraint: The validation constraint that was violated
    """

    def __init__(self, field: str, value: Any, constraint: str):
        self.field = field
        self.value = value
        self.constraint = constraint
        super().__init__(f"Validation failed for field '{field}': {constraint} " f"(got: {value})")


class ConfigurationError(NewsletterError):
    """
    Raised when application configuration is invalid or missing.

    Attributes:
        config_key: The configuration key that is problematic
        reason: Why the configuration is invalid
    """

    def __init__(self, config_key: str, reason: str):
        self.config_key = config_key
        self.reason = reason
        super().__init__(f"Configuration error for '{config_key}': {reason}")


class LLMError(NewsletterError):
    """
    Raised when LLM service operations fail.

    Attributes:
        details: Error details from the LLM service
    """

    def __init__(self, details: str):
        self.details = details
        super().__init__(f"LLM service error: {details}")


class AuthenticationError(NewsletterError):
    """
    Raised when authentication operations fail.

    Attributes:
        provider: The authentication provider (e.g., "google_oauth", "password")
        details: Error details
    """

    def __init__(self, provider: str, details: str):
        self.provider = provider
        self.details = details
        super().__init__(f"Authentication error ({provider}): {details}")


class EmailError(NewsletterError):
    """
    Raised when email operations fail.

    Attributes:
        operation: The email operation that failed (e.g., "send", "verify")
        details: Error details
    """

    def __init__(self, operation: str, details: str):
        self.operation = operation
        self.details = details
        super().__init__(f"Email {operation} failed: {details}")


class RateLimitExceeded(NewsletterError):
    """
    Raised when rate limit is exceeded.

    Attributes:
        endpoint: The endpoint that was rate limited
        retry_after: Seconds until the rate limit resets
    """

    def __init__(self, endpoint: str, retry_after: int):
        self.endpoint = endpoint
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for {endpoint}. Retry after {retry_after} seconds.")


class GameError(NewsletterError):
    """
    Raised when game operations fail.

    Attributes:
        operation: The game operation that failed (e.g., "save_result", "get_progress")
        details: Error details
    """

    def __init__(self, operation: str, details: str):
        self.operation = operation
        self.details = details
        super().__init__(f"Game {operation} failed: {details}")


class FeedbackError(NewsletterError):
    """
    Raised when feedback submission fails.

    Attributes:
        operation: The feedback operation that failed (e.g., "submit", "validate")
        details: Error details
    """

    def __init__(self, operation: str, details: str):
        self.operation = operation
        self.details = details
        super().__init__(f"Feedback {operation} failed: {details}")
