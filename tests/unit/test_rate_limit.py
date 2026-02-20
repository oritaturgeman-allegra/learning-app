"""Unit tests for rate limiting middleware."""

import pytest
from unittest.mock import MagicMock

from backend.middleware.rate_limit import RateLimitMiddleware, RateLimitConfig


class TestRateLimitConfig:
    """Tests for RateLimitConfig dataclass."""

    def test_config_creation(self):
        """Test creating a rate limit config."""
        config = RateLimitConfig(max_requests=5, window_seconds=900)
        assert config.max_requests == 5
        assert config.window_seconds == 900


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware."""

    def test_middleware_disabled(self):
        """Test that disabled middleware passes all requests."""
        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=False,
            login_config=RateLimitConfig(max_requests=1, window_seconds=60),
        )
        assert middleware.enabled is False

    def test_middleware_enabled_with_configs(self):
        """Test that enabled middleware stores configs."""
        app = MagicMock()
        login_config = RateLimitConfig(max_requests=5, window_seconds=900)
        signup_config = RateLimitConfig(max_requests=3, window_seconds=3600)

        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=login_config,
            signup_config=signup_config,
        )

        assert middleware.enabled is True
        assert "/api/auth/login" in middleware.configs
        assert "/api/auth/signup" in middleware.configs
        assert middleware.configs["/api/auth/login"].max_requests == 5
        assert middleware.configs["/api/auth/signup"].max_requests == 3

    def test_get_client_ip_direct(self):
        """Test getting client IP from direct connection."""
        app = MagicMock()
        middleware = RateLimitMiddleware(app, enabled=True)

        request = MagicMock()
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.100"

        ip = middleware._get_client_ip(request)
        assert ip == "192.168.1.100"

    def test_get_client_ip_forwarded(self):
        """Test getting client IP from X-Forwarded-For header."""
        app = MagicMock()
        middleware = RateLimitMiddleware(app, enabled=True)

        request = MagicMock()
        request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}
        request.client = MagicMock()
        request.client.host = "192.168.1.100"

        ip = middleware._get_client_ip(request)
        assert ip == "10.0.0.1"  # First IP in the chain

    def test_get_client_ip_no_client(self):
        """Test getting client IP when client is None."""
        app = MagicMock()
        middleware = RateLimitMiddleware(app, enabled=True)

        request = MagicMock()
        request.headers = {}
        request.client = None

        ip = middleware._get_client_ip(request)
        assert ip == "unknown"

    def test_is_rate_limited_under_limit(self):
        """Test that requests under limit are not rate limited."""
        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=RateLimitConfig(max_requests=5, window_seconds=900),
        )

        # First request should not be limited
        is_limited, retry_after = middleware._is_rate_limited("/api/auth/login", "192.168.1.1")
        assert is_limited is False
        assert retry_after == 0

    def test_is_rate_limited_at_limit(self):
        """Test that requests at limit are rate limited."""
        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=RateLimitConfig(max_requests=2, window_seconds=900),
        )

        # Simulate 2 previous requests
        middleware._increment_counter("/api/auth/login", "192.168.1.1")
        middleware._increment_counter("/api/auth/login", "192.168.1.1")

        # Third request should be limited
        is_limited, retry_after = middleware._is_rate_limited("/api/auth/login", "192.168.1.1")
        assert is_limited is True
        assert retry_after == 900

    def test_increment_counter(self):
        """Test that counter increments correctly."""
        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=RateLimitConfig(max_requests=5, window_seconds=900),
        )

        cache = middleware.caches["/api/auth/login"]

        # Initially no count
        assert cache.get("192.168.1.1", 0) == 0

        # After increment
        middleware._increment_counter("/api/auth/login", "192.168.1.1")
        assert cache.get("192.168.1.1") == 1

        # After second increment
        middleware._increment_counter("/api/auth/login", "192.168.1.1")
        assert cache.get("192.168.1.1") == 2

    def test_different_ips_have_separate_counts(self):
        """Test that different IPs have separate rate limit counts."""
        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=RateLimitConfig(max_requests=2, window_seconds=900),
        )

        # IP1 makes 2 requests (at limit)
        middleware._increment_counter("/api/auth/login", "192.168.1.1")
        middleware._increment_counter("/api/auth/login", "192.168.1.1")

        # IP1 should be limited
        is_limited, _ = middleware._is_rate_limited("/api/auth/login", "192.168.1.1")
        assert is_limited is True

        # IP2 should not be limited
        is_limited, _ = middleware._is_rate_limited("/api/auth/login", "192.168.1.2")
        assert is_limited is False

    def test_different_endpoints_have_separate_counts(self):
        """Test that different endpoints have separate rate limit counts."""
        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=RateLimitConfig(max_requests=2, window_seconds=900),
            signup_config=RateLimitConfig(max_requests=2, window_seconds=3600),
        )

        # Login endpoint at limit
        middleware._increment_counter("/api/auth/login", "192.168.1.1")
        middleware._increment_counter("/api/auth/login", "192.168.1.1")

        # Login should be limited
        is_limited, _ = middleware._is_rate_limited("/api/auth/login", "192.168.1.1")
        assert is_limited is True

        # Signup should not be limited (different endpoint)
        is_limited, _ = middleware._is_rate_limited("/api/auth/signup", "192.168.1.1")
        assert is_limited is False

    def test_error_message_login(self):
        """Test error message for login endpoint."""
        app = MagicMock()
        middleware = RateLimitMiddleware(app, enabled=True)

        message = middleware._get_error_message("/api/auth/login", 900)
        assert "login" in message.lower()
        assert "15 minutes" in message

    def test_error_message_signup(self):
        """Test error message for signup endpoint."""
        app = MagicMock()
        middleware = RateLimitMiddleware(app, enabled=True)

        message = middleware._get_error_message("/api/auth/signup", 3600)
        assert "signup" in message.lower()
        assert "60 minutes" in message

    def test_unconfigured_path_not_rate_limited(self):
        """Test that unconfigured paths are not rate limited."""
        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=RateLimitConfig(max_requests=1, window_seconds=60),
        )

        # Unconfigured path
        is_limited, _ = middleware._is_rate_limited("/api/other", "192.168.1.1")
        assert is_limited is False


@pytest.mark.asyncio
class TestRateLimitMiddlewareDispatch:
    """Integration tests for middleware dispatch."""

    async def test_dispatch_allows_request_under_limit(self):
        """Test that requests under limit are allowed through."""

        # Create mock app and call_next
        async def mock_call_next(request):
            return MagicMock(status_code=200)

        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=RateLimitConfig(max_requests=5, window_seconds=900),
        )

        # Create mock request
        request = MagicMock()
        request.url.path = "/api/auth/login"
        request.method = "POST"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.1"

        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200

    async def test_dispatch_blocks_request_over_limit(self):
        """Test that requests over limit return 429."""

        async def mock_call_next(request):
            return MagicMock(status_code=200)

        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=RateLimitConfig(max_requests=1, window_seconds=900),
        )

        request = MagicMock()
        request.url.path = "/api/auth/login"
        request.method = "POST"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.1"

        # First request - allowed
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200

        # Second request - blocked
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 429
        assert response.headers.get("Retry-After") == "900"

    async def test_dispatch_skips_get_requests(self):
        """Test that GET requests are not rate limited."""

        async def mock_call_next(request):
            return MagicMock(status_code=200)

        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=True,
            login_config=RateLimitConfig(max_requests=1, window_seconds=900),
        )

        request = MagicMock()
        request.url.path = "/api/auth/login"
        request.method = "GET"  # GET request
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.1"

        # Multiple GET requests should all be allowed
        for _ in range(5):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

    async def test_dispatch_skips_when_disabled(self):
        """Test that disabled middleware allows all requests."""

        async def mock_call_next(request):
            return MagicMock(status_code=200)

        app = MagicMock()
        middleware = RateLimitMiddleware(
            app,
            enabled=False,
            login_config=RateLimitConfig(max_requests=1, window_seconds=900),
        )

        request = MagicMock()
        request.url.path = "/api/auth/login"
        request.method = "POST"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.1"

        # Multiple requests should all be allowed when disabled
        for _ in range(5):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200
