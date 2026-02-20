"""Integration tests for rate limiting on auth endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.middleware import RateLimitMiddleware, RateLimitConfig
from backend.routes.auth import router as auth_router

# Enable rate limiting for these tests (opt out of conftest disable)
pytestmark = pytest.mark.enable_rate_limiting


@pytest.fixture
def app_with_rate_limit():
    """Create a test app with rate limiting enabled."""
    app = FastAPI()

    # Add rate limiting middleware with low limits for testing
    app.add_middleware(
        RateLimitMiddleware,
        enabled=True,
        login_config=RateLimitConfig(max_requests=2, window_seconds=60),
        signup_config=RateLimitConfig(max_requests=2, window_seconds=60),
        resend_config=RateLimitConfig(max_requests=2, window_seconds=60),
    )

    app.include_router(auth_router)
    return app


@pytest.fixture
def client(app_with_rate_limit):
    """Create test client."""
    return TestClient(app_with_rate_limit)


class TestLoginRateLimit:
    """Test rate limiting on login endpoint."""

    @patch("backend.routes.auth.get_db_service")
    def test_login_rate_limit_exceeded(self, mock_db_service, client):
        """Test that login is rate limited after max attempts."""
        # Mock DB to always return "user not found" (we just want to test rate limit)
        mock_db = MagicMock()
        mock_db.get_user_by_email.return_value = None
        mock_db_service.return_value = mock_db

        # First 2 requests should work (return 401 for invalid credentials)
        for i in range(2):
            response = client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "password123"},
            )
            assert response.status_code == 401, f"Request {i+1} should return 401"

        # Third request should be rate limited
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert "login" in response.json()["detail"].lower()

    @patch("backend.routes.auth.get_db_service")
    def test_login_different_ips_not_rate_limited(self, mock_db_service, client):
        """Test that different IPs have separate rate limits."""
        mock_db = MagicMock()
        mock_db.get_user_by_email.return_value = None
        mock_db_service.return_value = mock_db

        # Exhaust rate limit for IP1
        for _ in range(2):
            response = client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "password123"},
                headers={"X-Forwarded-For": "10.0.0.1"},
            )

        # IP1 should be rate limited
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password123"},
            headers={"X-Forwarded-For": "10.0.0.1"},
        )
        assert response.status_code == 429

        # IP2 should not be rate limited
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password123"},
            headers={"X-Forwarded-For": "10.0.0.2"},
        )
        assert response.status_code == 401  # Invalid credentials, but not rate limited


class TestSignupRateLimit:
    """Test rate limiting on signup endpoint."""

    @patch("backend.routes.auth.get_db_service")
    def test_signup_rate_limit_exceeded(self, mock_db_service, client):
        """Test that signup is rate limited after max attempts."""
        # Mock DB to return that email already exists with proper User object
        from backend.models.user import User

        mock_user = MagicMock(spec=User)
        mock_user.google_id = None  # Regular password user
        mock_user.email = "test@example.com"

        mock_db = MagicMock()
        mock_db.get_user_by_email.return_value = mock_user
        mock_db_service.return_value = mock_db

        # First 2 requests should work (return 409 Conflict for existing email)
        for i in range(2):
            response = client.post(
                "/api/auth/signup",
                json={
                    "email": "test@example.com",
                    "password": "Password123",
                    "name": "Test User",
                },
            )
            assert response.status_code == 409, f"Request {i+1} should return 409"

        # Third request should be rate limited
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "Password123",
                "name": "Test User",
            },
        )
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert "signup" in response.json()["detail"].lower()


class TestResendVerificationRateLimit:
    """Test rate limiting on resend verification endpoint."""

    @patch("backend.routes.auth.get_db_service")
    def test_resend_rate_limit_exceeded(self, mock_db_service, client):
        """Test that resend verification is rate limited after max attempts."""
        # Mock DB to return user not found
        # Note: endpoint returns 200 even if user doesn't exist (security - don't reveal)
        mock_db = MagicMock()
        mock_db.get_user_by_email.return_value = None
        mock_db_service.return_value = mock_db

        # First 2 requests should work (return 200 - doesn't reveal if email exists)
        for i in range(2):
            response = client.post(
                "/api/auth/resend-verification",
                json={"email": "test@example.com"},
            )
            assert response.status_code == 200, f"Request {i+1} should return 200"

        # Third request should be rate limited
        response = client.post(
            "/api/auth/resend-verification",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 429
        assert "Retry-After" in response.headers


class TestRateLimitHeaders:
    """Test rate limit response headers."""

    @patch("backend.routes.auth.get_db_service")
    def test_retry_after_header_value(self, mock_db_service, client):
        """Test that Retry-After header has correct value."""
        mock_db = MagicMock()
        mock_db.get_user_by_email.return_value = None
        mock_db_service.return_value = mock_db

        # Exhaust rate limit
        for _ in range(2):
            client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "password123"},
            )

        # Check rate limited response
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )

        assert response.status_code == 429
        retry_after = int(response.headers["Retry-After"])
        assert retry_after == 60  # Our test config uses 60 second window


class TestRateLimitDisabled:
    """Test behavior when rate limiting is disabled."""

    @pytest.fixture
    def app_without_rate_limit(self):
        """Create a test app with rate limiting disabled."""
        app = FastAPI()

        app.add_middleware(
            RateLimitMiddleware,
            enabled=False,  # Disabled
            login_config=RateLimitConfig(max_requests=1, window_seconds=60),
        )

        app.include_router(auth_router)
        return app

    @pytest.fixture
    def client_no_limit(self, app_without_rate_limit):
        """Create test client without rate limiting."""
        return TestClient(app_without_rate_limit)

    @patch("backend.routes.auth.get_db_service")
    def test_no_rate_limit_when_disabled(self, mock_db_service, client_no_limit):
        """Test that requests are not rate limited when disabled."""
        mock_db = MagicMock()
        mock_db.get_user_by_email.return_value = None
        mock_db_service.return_value = mock_db

        # Even with limit of 1, all requests should pass through
        for _ in range(5):
            response = client_no_limit.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "password123"},
            )
            # Should get 401 (invalid creds), not 429 (rate limited)
            assert response.status_code == 401
