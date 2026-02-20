"""
Structured logging configuration for Capital Market Newsletter.

Provides consistent JSON-formatted logging across the application with
request ID tracking and proper log levels.
"""

import logging
import sys
from typing import Any

import structlog
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO", json_output: bool = False) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: If True, output logs in JSON format (for production)
    """
    # Set the log level
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure processors based on output format
    if json_output:
        # Production: JSON output
        renderer = structlog.processors.JSONRenderer()
    else:
        # Development: Pretty console output
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            renderer,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure Python's logging
    handler = logging.StreamHandler(sys.stdout)

    if json_output:
        # JSON formatter for production
        formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "name": "logger"},
        )
        handler.setFormatter(formatter)
    else:
        # Simple formatter for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Remove existing handlers
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def bind_request_id(request_id: str) -> None:
    """
    Bind a request ID to the current logging context.

    Args:
        request_id: Unique request identifier
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)


def log_event(
    logger: Any,
    event: str,
    level: str = "info",
    **kwargs: Any,
) -> None:
    """
    Log a structured event with additional context.

    Args:
        logger: Logger instance
        event: Event name (e.g., "newsletter_generated", "feed_fetched")
        level: Log level (debug, info, warning, error)
        **kwargs: Additional context to log
    """
    log_func = getattr(logger, level, logger.info)
    log_func(event, **kwargs)
