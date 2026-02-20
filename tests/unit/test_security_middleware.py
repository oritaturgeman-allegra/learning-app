"""Unit tests for security middleware."""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from backend.middleware.security import SecurityHeadersMiddleware


@pytest.fixture
def app_with_security():
    """Create a test app with security middleware."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/")
    def root():
        return {"message": "hello"}

    @app.get("/api/test")
    def api_test():
        return {"data": "test"}

    return app


@pytest.fixture
def app_with_https():
    """Create a test app with HTTPS/HSTS enabled."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, force_https=True)

    @app.get("/")
    def root():
        return {"message": "hello"}

    return app


@pytest.fixture
def app_with_csp_report_only():
    """Create a test app with CSP in report-only mode."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, csp_report_only=True)

    @app.get("/")
    def root():
        return {"message": "hello"}

    return app


class TestSecurityHeaders:
    """Test security headers are present on responses."""

    def test_x_content_type_options(self, app_with_security):
        """Test X-Content-Type-Options header is set."""
        client = TestClient(app_with_security)
        response = client.get("/")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self, app_with_security):
        """Test X-Frame-Options header is set."""
        client = TestClient(app_with_security)
        response = client.get("/")
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_x_xss_protection(self, app_with_security):
        """Test X-XSS-Protection header is set."""
        client = TestClient(app_with_security)
        response = client.get("/")
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    def test_referrer_policy(self, app_with_security):
        """Test Referrer-Policy header is set."""
        client = TestClient(app_with_security)
        response = client.get("/")
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_permissions_policy(self, app_with_security):
        """Test Permissions-Policy header is set."""
        client = TestClient(app_with_security)
        response = client.get("/")
        permissions = response.headers.get("Permissions-Policy")
        assert permissions is not None
        assert "camera=()" in permissions
        assert "microphone=()" in permissions
        assert "geolocation=()" in permissions

    def test_content_security_policy(self, app_with_security):
        """Test Content-Security-Policy header is set."""
        client = TestClient(app_with_security)
        response = client.get("/")
        csp = response.headers.get("Content-Security-Policy")
        assert csp is not None
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp

    def test_csp_allows_google_oauth(self, app_with_security):
        """Test CSP allows Google OAuth endpoints."""
        client = TestClient(app_with_security)
        response = client.get("/")
        csp = response.headers.get("Content-Security-Policy")
        assert "accounts.google.com" in csp

    def test_csp_allows_google_fonts(self, app_with_security):
        """Test CSP allows Google Fonts."""
        client = TestClient(app_with_security)
        response = client.get("/")
        csp = response.headers.get("Content-Security-Policy")
        assert "fonts.googleapis.com" in csp
        assert "fonts.gstatic.com" in csp

    def test_headers_on_api_endpoints(self, app_with_security):
        """Test security headers are present on API endpoints."""
        client = TestClient(app_with_security)
        response = client.get("/api/test")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("Content-Security-Policy") is not None


class TestHSTSHeader:
    """Test HSTS header behavior."""

    def test_no_hsts_by_default(self, app_with_security):
        """Test HSTS header is NOT present when force_https=False."""
        client = TestClient(app_with_security)
        response = client.get("/")
        assert response.headers.get("Strict-Transport-Security") is None

    def test_hsts_when_force_https(self, app_with_https):
        """Test HSTS header IS present when force_https=True."""
        client = TestClient(app_with_https)
        response = client.get("/")
        hsts = response.headers.get("Strict-Transport-Security")
        assert hsts is not None
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts


class TestCSPReportOnly:
    """Test CSP report-only mode."""

    def test_csp_report_only_header(self, app_with_csp_report_only):
        """Test CSP uses report-only header when configured."""
        client = TestClient(app_with_csp_report_only)
        response = client.get("/")
        # Should have report-only header, not enforcing header
        assert response.headers.get("Content-Security-Policy-Report-Only") is not None
        assert response.headers.get("Content-Security-Policy") is None

    def test_csp_enforcing_by_default(self, app_with_security):
        """Test CSP is enforcing when csp_report_only=False."""
        client = TestClient(app_with_security)
        response = client.get("/")
        # Should have enforcing header, not report-only
        assert response.headers.get("Content-Security-Policy") is not None
        assert response.headers.get("Content-Security-Policy-Report-Only") is None


# =============================================================================
# CORS Middleware Tests
# =============================================================================


@pytest.fixture
def app_with_cors():
    """Create a test app with CORS middleware enabled."""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://example.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {"message": "hello"}

    @app.post("/api/data")
    def post_data():
        return {"success": True}

    return app


@pytest.fixture
def app_with_cors_wildcard():
    """Create a test app with wildcard CORS origins."""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Can't use credentials with wildcard
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {"message": "hello"}

    return app


@pytest.fixture
def app_without_cors():
    """Create a test app without CORS middleware."""
    app = FastAPI()

    @app.get("/")
    def root():
        return {"message": "hello"}

    return app


class TestCORSMiddleware:
    """Test CORS middleware behavior."""

    def test_cors_headers_for_allowed_origin(self, app_with_cors):
        """Test CORS headers are present for allowed origins."""
        client = TestClient(app_with_cors)
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_cors_headers_for_different_allowed_origin(self, app_with_cors):
        """Test CORS headers work for multiple allowed origins."""
        client = TestClient(app_with_cors)
        response = client.get("/", headers={"Origin": "https://example.com"})
        assert response.headers.get("access-control-allow-origin") == "https://example.com"

    def test_no_cors_headers_for_disallowed_origin(self, app_with_cors):
        """Test CORS headers NOT present for disallowed origins."""
        client = TestClient(app_with_cors)
        response = client.get("/", headers={"Origin": "https://evil.com"})
        # Disallowed origins should not get CORS headers
        assert response.headers.get("access-control-allow-origin") is None

    def test_preflight_options_request(self, app_with_cors):
        """Test preflight OPTIONS request returns correct headers."""
        client = TestClient(app_with_cors)
        response = client.options(
            "/api/data",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert "POST" in response.headers.get("access-control-allow-methods", "")

    def test_cors_wildcard_origin(self, app_with_cors_wildcard):
        """Test wildcard CORS allows any origin."""
        client = TestClient(app_with_cors_wildcard)
        response = client.get("/", headers={"Origin": "https://any-site.com"})
        assert response.headers.get("access-control-allow-origin") == "*"

    def test_no_cors_without_middleware(self, app_without_cors):
        """Test no CORS headers when middleware not configured."""
        client = TestClient(app_without_cors)
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.headers.get("access-control-allow-origin") is None
