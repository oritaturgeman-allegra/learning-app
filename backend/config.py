"""
Configuration module for Ariel's English Adventure.

Provides type-safe configuration loading with validation and default values.
"""

import os
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from dotenv import load_dotenv

from backend.exceptions import ConfigurationError


def _clean_database_url(url: str) -> str:
    """
    Remove unsupported parameters from database URL.

    Supabase adds 'pgbouncer=true' to connection strings, but psycopg2
    doesn't recognize this parameter. This function strips it out.
    """
    if not url or url.startswith("sqlite"):
        return url

    try:
        parsed = urlparse(url)
        if parsed.query:
            params = parse_qs(parsed.query, keep_blank_values=True)
            params.pop("pgbouncer", None)
            clean_params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
            new_query = urlencode(clean_params, doseq=True)
            return urlunparse(parsed._replace(query=new_query))
    except Exception:
        pass

    return url


@dataclass
class AppConfig:
    """
    Application configuration with validation.

    All configuration values are loaded from environment variables with
    sensible defaults for development.
    """

    # Database Settings
    database_url: str = "sqlite:///data/learning.db"
    sql_echo: bool = False

    # Server Settings
    flask_host: str = "0.0.0.0"
    flask_port: int = 8000
    flask_debug: bool = False

    # Sentry Settings
    sentry_dsn: str = ""
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1

    # Logging Settings
    log_format: str = "text"  # text | json
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        load_dotenv()

        return cls(
            database_url=_clean_database_url(
                os.getenv("LEARNING_DATABASE_URL", "sqlite:///data/learning.db")
            ),
            sql_echo=os.getenv("SQL_ECHO", "false").lower() == "true",
            flask_host=os.getenv("FLASK_HOST", "0.0.0.0"),
            flask_port=int(os.getenv("FLASK_PORT", "8000")),
            flask_debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
            sentry_dsn=os.getenv("SENTRY_DSN", ""),
            sentry_environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
            sentry_traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            log_format=os.getenv("LOG_FORMAT", "text").lower(),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )

    def validate(self) -> None:
        """Validate configuration values."""
        if self.flask_port <= 0 or self.flask_port > 65535:
            raise ConfigurationError("flask_port", "Must be between 1 and 65535")


# Global configuration instance
config = AppConfig.from_env()
config.validate()
