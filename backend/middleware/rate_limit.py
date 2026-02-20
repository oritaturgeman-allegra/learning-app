"""Rate limiting middleware for auth endpoints."""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from cachetools import TTLCache
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for a rate-limited endpoint."""

    max_requests: int
    window_seconds: int


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that rate limits specific endpoints.

    Uses in-memory TTL cache for tracking requests per IP.
    Each endpoint can have its own rate limit configuration.

    Note: This implementation uses in-memory storage, so rate limits
    are not shared across multiple worker processes. For production
    at scale, consider using Redis.
    """

    def __init__(
        self,
        app,
        enabled: bool = True,
        login_config: Optional[RateLimitConfig] = None,
        signup_config: Optional[RateLimitConfig] = None,
        resend_config: Optional[RateLimitConfig] = None,
    ) -> None:
        """
        Initialize rate limit middleware.

        Args:
            app: The ASGI application
            enabled: Whether rate limiting is enabled
            login_config: Rate limit config for /api/auth/login
            signup_config: Rate limit config for /api/auth/signup
            resend_config: Rate limit config for /api/auth/resend-verification
        """
        super().__init__(app)
        self.enabled = enabled

        # Default configs if not provided
        self.configs: Dict[str, RateLimitConfig] = {}
        if login_config:
            self.configs["/api/auth/login"] = login_config
        if signup_config:
            self.configs["/api/auth/signup"] = signup_config
        if resend_config:
            self.configs["/api/auth/resend-verification"] = resend_config

        # Create separate TTL caches for each endpoint
        # maxsize is generous - 10000 unique IPs per endpoint
        self.caches: Dict[str, TTLCache] = {}
        for path, config in self.configs.items():
            self.caches[path] = TTLCache(maxsize=10000, ttl=config.window_seconds)

        if enabled and self.configs:
            logger.info(f"Rate limiting enabled for endpoints: {list(self.configs.keys())}")

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.

        Checks X-Forwarded-For header for proxied requests,
        falls back to direct client IP.
        """
        # Check for forwarded header (from reverse proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    def _is_rate_limited(self, path: str, client_ip: str) -> tuple[bool, int]:
        """
        Check if request is rate limited.

        Args:
            path: The request path
            client_ip: The client IP address

        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        if path not in self.caches:
            return False, 0

        cache = self.caches[path]
        config = self.configs[path]

        # Get current count for this IP
        current_count = cache.get(client_ip, 0)

        if current_count >= config.max_requests:
            # Calculate retry-after (approximate - TTL cache doesn't expose exact expiry)
            # Use full window as conservative estimate
            return True, config.window_seconds

        return False, 0

    def _increment_counter(self, path: str, client_ip: str) -> None:
        """Increment request counter for client IP."""
        if path not in self.caches:
            return

        cache = self.caches[path]
        current_count = cache.get(client_ip, 0)
        cache[client_ip] = current_count + 1

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)

        path = request.url.path

        # Only rate limit configured endpoints and POST requests
        if path not in self.configs or request.method != "POST":
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        is_limited, retry_after = self._is_rate_limited(path, client_ip)

        if is_limited:
            # Log the violation
            logger.warning(f"Rate limit exceeded: IP={client_ip}, endpoint={path}")

            # Return 429 Too Many Requests
            return JSONResponse(
                status_code=429,
                content={
                    "detail": self._get_error_message(path, retry_after),
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Increment counter before processing request
        self._increment_counter(path, client_ip)

        return await call_next(request)

    def _get_error_message(self, path: str, retry_after: int) -> str:
        """Get user-friendly error message for the endpoint."""
        minutes = retry_after // 60

        if path == "/api/auth/login":
            return f"Too many login attempts. Please try again in {minutes} minutes."
        elif path == "/api/auth/signup":
            return f"Too many signup attempts. Please try again in {minutes} minutes."
        elif path == "/api/auth/resend-verification":
            return f"Too many requests. Please try again in {minutes} minutes."

        return f"Rate limit exceeded. Please try again in {minutes} minutes."
