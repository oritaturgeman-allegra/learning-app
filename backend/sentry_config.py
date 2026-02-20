"""
Sentry error monitoring configuration for Capital Market Newsletter.

Initializes Sentry SDK with FastAPI integration, data scrubbing,
and release tracking. No-op when SENTRY_DSN is not configured.
"""

import logging
from typing import Any, Dict, Optional

import sentry_sdk

from backend.defaults import APP_VERSION

logger = logging.getLogger(__name__)

# Fields to scrub from Sentry events
SENSITIVE_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "authorization",
        "cookie",
        "session",
        "credit_card",
        "ssn",
        "openai_api_key",
        "gemini_api_key",
        "email_api_key",
        "admin_api_key",
        "sentry_dsn",
        "google_client_secret",
    }
)


def _scrub_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively scrub sensitive fields from a dictionary.

    Args:
        data: Dictionary to scrub

    Returns:
        Scrubbed dictionary with sensitive values replaced
    """
    scrubbed: Dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in SENSITIVE_KEYS:
            scrubbed[key] = "[Filtered]"
        elif isinstance(value, dict):
            scrubbed[key] = _scrub_data(value)
        else:
            scrubbed[key] = value
    return scrubbed


def _before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Scrub sensitive data before sending events to Sentry.

    Args:
        event: Sentry event dictionary
        hint: Additional context about the event

    Returns:
        Scrubbed event, or None to drop it
    """
    # Filter out KeyboardInterrupt (normal server shutdown via Ctrl+C)
    if "exc_info" in hint:
        exc_type = hint["exc_info"][0]
        if exc_type is KeyboardInterrupt:
            return None

    # Filter KeyboardInterrupt logged as message by uvicorn
    log_entry = event.get("logentry", {})
    message = log_entry.get("message", "") or log_entry.get("formatted", "")
    if "KeyboardInterrupt" in message:
        return None

    # Scrub request data
    if "request" in event:
        request_data = event["request"]
        if "data" in request_data and isinstance(request_data["data"], dict):
            request_data["data"] = _scrub_data(request_data["data"])
        if "headers" in request_data and isinstance(request_data["headers"], dict):
            request_data["headers"] = _scrub_data(request_data["headers"])
        if "cookies" in request_data:
            request_data["cookies"] = "[Filtered]"

    # Scrub extra context
    if "extra" in event and isinstance(event["extra"], dict):
        event["extra"] = _scrub_data(event["extra"])

    return event


def init_sentry(
    dsn: str,
    environment: str = "development",
    traces_sample_rate: float = 0.1,
) -> bool:
    """Initialize Sentry SDK for error monitoring.

    Does nothing if dsn is empty. Safe to call multiple times.

    Args:
        dsn: Sentry DSN string
        environment: Deployment environment name
        traces_sample_rate: Fraction of transactions to trace (0.0-1.0)

    Returns:
        True if Sentry was initialized, False if skipped
    """
    if not dsn:
        logger.info("Sentry not configured (no SENTRY_DSN)")
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=APP_VERSION,
        traces_sample_rate=traces_sample_rate,
        send_default_pii=False,
        before_send=_before_send,
    )

    logger.info(
        "Sentry initialized",
        extra={
            "environment": environment,
            "release": APP_VERSION,
            "traces_sample_rate": traces_sample_rate,
        },
    )
    return True
