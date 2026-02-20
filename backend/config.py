"""
Configuration module for the Capital Market Newsletter application.

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
            # Parse query params and remove unsupported ones
            params = parse_qs(parsed.query, keep_blank_values=True)
            params.pop("pgbouncer", None)

            # Rebuild query string (parse_qs returns lists, flatten single values)
            clean_params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
            new_query = urlencode(clean_params, doseq=True)

            # Rebuild URL
            return urlunparse(parsed._replace(query=new_query))
    except Exception:
        pass  # If parsing fails, return original URL

    return url


@dataclass
class AppConfig:
    """
    Application configuration with validation.

    All configuration values are loaded from environment variables with
    sensible defaults for development.
    """

    # API Keys
    openai_api_key: str
    gemini_api_key: str = ""  # Optional, required only if using Gemini

    # LLM Settings
    llm_provider: str = "openai"  # "openai" or "gemini"
    openai_model: str = "gpt-4o-mini"  # OpenAI model for analysis
    gemini_model: str = "gemini-2.0-flash"  # Gemini model for analysis

    # Database Settings
    database_url: str = "sqlite:///data/newsletter.db"  # SQLite for dev, PostgreSQL for prod
    sql_echo: bool = False  # Log SQL queries

    # Feed Settings
    feed_timeout: int = 10  # seconds
    feed_max_workers: int = 5  # concurrent feed fetches
    intraday_hours: int = 12  # time window for recent articles

    # Cache Settings
    newsletter_cache_ttl: int = 21600  # 6 hours (matches scheduler gaps, reduces LLM costs)
    audio_cache_ttl: int = 86400  # 24 hours (must outlast scheduler gaps: up to 15h overnight)

    # Content Settings
    max_articles_per_category: int = 5  # max articles per category (US, Israel, AI)

    # TTS Settings
    tts_provider: str = "openai"  # "openai" or "gemini"
    tts_model: str = "tts-1-hd"  # OpenAI model
    gemini_tts_model: str = "gemini-2.5-flash-preview-tts"  # Gemini TTS model
    tts_voice_alex: str = "nova"  # OpenAI female host
    tts_voice_guy: str = "fable"  # OpenAI male host
    tts_speed: float = 1.0  # TTS speech speed (0.25-4.0)
    gemini_voice_alex: str = "Aoede"  # Gemini female (Breezy)
    gemini_voice_guy: str = "Orus"  # Gemini male (Firm)

    # Server Settings
    flask_host: str = "0.0.0.0"
    flask_port: int = 5000
    flask_debug: bool = False

    # Google OAuth Settings
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:5000/api/auth/google/callback"

    # Email Settings
    email_api_key: str = ""  # SendGrid API key
    email_from_address: str = "yournewsletter.yourway@gmail.com"
    email_from_name: str = "Your Newsletter, Your Way"
    base_url: str = "http://localhost:5000"  # For verification links
    verification_token_ttl_hours: int = 24  # Token expiration time

    # Scheduler Settings
    schedule_enabled: bool = True  # Enable/disable scheduled content generation
    schedule_hours_utc: tuple = (11, 14, 18, 20)  # Hours in UTC to run content generation
    schedule_timezone: str = "UTC"  # Timezone for scheduler
    schedule_misfire_grace_time: int = 900  # 15 minutes grace period for missed jobs

    # Admin Settings
    admin_api_key: str = ""  # API key for admin endpoints (e.g., /api/admin/refresh)

    # Security Settings
    force_https: bool = False  # Force HTTPS redirect and enable HSTS (production only)
    csp_report_only: bool = True  # Use Content-Security-Policy-Report-Only for testing

    # CORS Settings
    cors_enabled: bool = False  # Enable CORS middleware (for external clients/mobile apps)
    cors_origins: tuple = ()  # Allowed origins (empty = no cross-origin allowed)
    cors_allow_credentials: bool = True  # Allow cookies/auth headers in cross-origin requests

    # Sentry Settings
    sentry_dsn: str = ""  # Sentry DSN for error monitoring (empty = disabled)
    sentry_environment: str = "development"  # development | staging | production
    sentry_traces_sample_rate: float = 0.1  # Fraction of transactions to trace (0.0-1.0)

    # Logging Settings
    log_format: str = "text"  # text | json (json for production)
    log_level: str = "INFO"  # DEBUG | INFO | WARNING | ERROR

    # Rate Limiting Settings
    rate_limit_enabled: bool = True  # Enable rate limiting for auth endpoints
    rate_limit_login_max: int = 5  # Max login attempts
    rate_limit_login_window: int = 900  # 15 minutes in seconds
    rate_limit_signup_max: int = 3  # Max signup attempts
    rate_limit_signup_window: int = 3600  # 1 hour in seconds
    rate_limit_resend_max: int = 3  # Max resend verification attempts
    rate_limit_resend_window: int = 3600  # 1 hour in seconds

    @classmethod
    def from_env(cls) -> "AppConfig":
        """
        Load configuration from environment variables.

        Returns:
            AppConfig: Configured application settings

        Raises:
            ConfigurationError: If required environment variables are missing
        """
        # Load .env file
        load_dotenv()

        # Get required API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY",
                "Environment variable is required. Please set it in your .env file.",
            )

        # Get optional Gemini API key
        gemini_key = os.getenv("GEMINI_API_KEY", "")

        # Get LLM provider setting
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

        # Load optional settings with defaults
        return cls(
            openai_api_key=api_key,
            gemini_api_key=gemini_key,
            llm_provider=llm_provider,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            database_url=_clean_database_url(
                os.getenv("DATABASE_URL", "sqlite:///data/newsletter.db")
            ),
            sql_echo=os.getenv("SQL_ECHO", "false").lower() == "true",
            feed_timeout=int(os.getenv("FEED_TIMEOUT", "10")),
            feed_max_workers=int(os.getenv("FEED_MAX_WORKERS", "5")),
            intraday_hours=int(os.getenv("INTRADAY_HOURS", "12")),
            newsletter_cache_ttl=int(os.getenv("NEWSLETTER_CACHE_TTL", "3600")),
            audio_cache_ttl=int(os.getenv("AUDIO_CACHE_TTL", "86400")),
            max_articles_per_category=int(os.getenv("MAX_ARTICLES_PER_CATEGORY", "5")),
            tts_provider=os.getenv("TTS_PROVIDER", "openai").lower(),
            tts_model=os.getenv("TTS_MODEL", "tts-1-hd"),
            gemini_tts_model=os.getenv("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts"),
            tts_voice_alex=os.getenv("TTS_VOICE_ALEX", "nova"),
            tts_voice_guy=os.getenv("TTS_VOICE_GUY", "fable"),
            gemini_voice_alex=os.getenv("GEMINI_VOICE_ALEX", "Aoede"),
            gemini_voice_guy=os.getenv("GEMINI_VOICE_GUY", "Orus"),
            flask_host=os.getenv("FLASK_HOST", "0.0.0.0"),
            flask_port=int(os.getenv("FLASK_PORT", "5000")),
            flask_debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
            google_client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            google_redirect_uri=os.getenv(
                "GOOGLE_REDIRECT_URI", "http://localhost:5000/api/auth/google/callback"
            ),
            # Email settings
            email_api_key=os.getenv("EMAIL_API_KEY", ""),
            email_from_address=os.getenv("EMAIL_FROM_ADDRESS", "yournewsletter.yourway@gmail.com"),
            email_from_name=os.getenv("EMAIL_FROM_NAME", "Your Newsletter, Your Way"),
            base_url=os.getenv("BASE_URL", "http://localhost:5000"),
            verification_token_ttl_hours=int(os.getenv("VERIFICATION_TOKEN_TTL_HOURS", "24")),
            # Scheduler settings
            schedule_enabled=os.getenv("SCHEDULE_ENABLED", "true").lower() == "true",
            schedule_hours_utc=tuple(
                int(h) for h in os.getenv("SCHEDULE_HOURS_UTC", "11,14,18,20").split(",")
            ),
            schedule_timezone=os.getenv("SCHEDULE_TIMEZONE", "UTC"),
            schedule_misfire_grace_time=int(os.getenv("SCHEDULE_MISFIRE_GRACE_TIME", "900")),
            # Admin settings
            admin_api_key=os.getenv("ADMIN_API_KEY", ""),
            # Security settings
            force_https=os.getenv("FORCE_HTTPS", "false").lower() == "true",
            csp_report_only=os.getenv("CSP_REPORT_ONLY", "true").lower() == "true",
            # CORS settings
            cors_enabled=os.getenv("CORS_ENABLED", "false").lower() == "true",
            cors_origins=tuple(
                origin.strip()
                for origin in os.getenv("CORS_ORIGINS", "").split(",")
                if origin.strip()
            ),
            cors_allow_credentials=os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
            # Sentry settings
            sentry_dsn=os.getenv("SENTRY_DSN", ""),
            sentry_environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
            sentry_traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            # Logging settings
            log_format=os.getenv("LOG_FORMAT", "text").lower(),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            # Rate limiting settings
            rate_limit_enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
            rate_limit_login_max=int(os.getenv("RATE_LIMIT_LOGIN_MAX", "5")),
            rate_limit_login_window=int(os.getenv("RATE_LIMIT_LOGIN_WINDOW", "900")),
            rate_limit_signup_max=int(os.getenv("RATE_LIMIT_SIGNUP_MAX", "3")),
            rate_limit_signup_window=int(os.getenv("RATE_LIMIT_SIGNUP_WINDOW", "3600")),
            rate_limit_resend_max=int(os.getenv("RATE_LIMIT_RESEND_MAX", "3")),
            rate_limit_resend_window=int(os.getenv("RATE_LIMIT_RESEND_WINDOW", "3600")),
        )

    def validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ConfigurationError: If any configuration value is invalid
        """
        # Validate positive integers
        if self.feed_timeout <= 0:
            raise ConfigurationError("feed_timeout", "Must be positive")

        if self.feed_max_workers <= 0:
            raise ConfigurationError("feed_max_workers", "Must be positive")

        if self.intraday_hours <= 0:
            raise ConfigurationError("intraday_hours", "Must be positive")

        if self.newsletter_cache_ttl < 0:
            raise ConfigurationError("newsletter_cache_ttl", "Must be non-negative")

        if self.audio_cache_ttl < 0:
            raise ConfigurationError("audio_cache_ttl", "Must be non-negative")

        if self.max_articles_per_category <= 0:
            raise ConfigurationError("max_articles_per_category", "Must be positive")

        if self.flask_port <= 0 or self.flask_port > 65535:
            raise ConfigurationError("flask_port", "Must be between 1 and 65535")

        # Validate API key format (basic check)
        if not self.openai_api_key.startswith("sk-"):
            raise ConfigurationError(
                "openai_api_key", 'Invalid format. OpenAI API keys should start with "sk-"'
            )

        # Validate LLM provider
        if self.llm_provider not in ("openai", "gemini"):
            raise ConfigurationError(
                "llm_provider", f'Must be "openai" or "gemini", got "{self.llm_provider}"'
            )

        # Validate Gemini API key if using Gemini
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            raise ConfigurationError(
                "gemini_api_key",
                "GEMINI_API_KEY is required when LLM_PROVIDER=gemini",
            )

        # Validate TTS provider
        if self.tts_provider not in ("openai", "gemini"):
            raise ConfigurationError(
                "tts_provider", f'Must be "openai" or "gemini", got "{self.tts_provider}"'
            )

        # Validate Gemini API key if using Gemini TTS
        if self.tts_provider == "gemini" and not self.gemini_api_key:
            raise ConfigurationError(
                "gemini_api_key",
                "GEMINI_API_KEY is required when TTS_PROVIDER=gemini",
            )

        # Validate TTS voice names match the provider
        valid_openai_voices = {
            "nova",
            "shimmer",
            "echo",
            "onyx",
            "fable",
            "alloy",
            "ash",
            "sage",
            "coral",
        }
        if self.tts_provider == "openai":
            if self.tts_voice_alex not in valid_openai_voices:
                raise ConfigurationError(
                    "tts_voice_alex",
                    f"Invalid OpenAI voice '{self.tts_voice_alex}'. "
                    f"Valid voices: {', '.join(sorted(valid_openai_voices))}",
                )
            if self.tts_voice_guy not in valid_openai_voices:
                raise ConfigurationError(
                    "tts_voice_guy",
                    f"Invalid OpenAI voice '{self.tts_voice_guy}'. "
                    f"Valid voices: {', '.join(sorted(valid_openai_voices))}",
                )

        # Validate scheduler settings
        for hour in self.schedule_hours_utc:
            if not 0 <= hour <= 23:
                raise ConfigurationError(
                    "schedule_hours_utc",
                    f"Hour {hour} is invalid. Must be between 0 and 23.",
                )

        # Validate email configuration completeness
        if self.email_api_key and not self.email_from_address:
            raise ConfigurationError(
                "email_from_address",
                "EMAIL_FROM_ADDRESS is required when EMAIL_API_KEY is set",
            )

        # Validate OAuth configuration completeness
        if self.google_client_id:
            if not self.google_client_secret:
                raise ConfigurationError(
                    "google_client_secret",
                    "GOOGLE_CLIENT_SECRET is required when GOOGLE_CLIENT_ID is set",
                )
            if not self.google_redirect_uri:
                raise ConfigurationError(
                    "google_redirect_uri",
                    "GOOGLE_REDIRECT_URI is required when GOOGLE_CLIENT_ID is set",
                )

        # Validate rate limiting bounds
        if self.rate_limit_enabled:
            rate_limit_fields = [
                "rate_limit_login_max",
                "rate_limit_login_window",
                "rate_limit_signup_max",
                "rate_limit_signup_window",
                "rate_limit_resend_max",
                "rate_limit_resend_window",
            ]
            for field in rate_limit_fields:
                if getattr(self, field) <= 0:
                    raise ConfigurationError(field, "Must be positive")

    def mask_api_key(self) -> str:
        """
        Mask API key for safe logging.

        Returns:
            str: Masked API key (e.g., "sk-pr...xyz")
        """
        if len(self.openai_api_key) < 8:
            return "***"
        return f"{self.openai_api_key[:5]}...{self.openai_api_key[-3:]}"


# Global configuration instance
config = AppConfig.from_env()
config.validate()

# Backward compatibility: export OPENAI_API_KEY for existing code
OPENAI_API_KEY = config.openai_api_key


def validate_config() -> None:
    """
    Validate configuration (backward compatibility function).

    This function is kept for backward compatibility with existing code.
    The validation now happens automatically when config is loaded.
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info(
        "Configuration loaded successfully",
        extra={
            "api_key": config.mask_api_key(),
            "llm_provider": config.llm_provider,
            "llm_model": (
                config.gemini_model if config.llm_provider == "gemini" else config.openai_model
            ),
            "feed_timeout": config.feed_timeout,
            "newsletter_cache_ttl_min": config.newsletter_cache_ttl // 60,
            "audio_cache_ttl_min": config.audio_cache_ttl // 60,
        },
    )
