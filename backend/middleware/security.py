"""Security middleware for adding HTTP security headers."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all HTTP responses.

    Headers added:
    - X-Content-Type-Options: Prevents MIME-type sniffing
    - X-Frame-Options: Prevents clickjacking
    - X-XSS-Protection: Legacy XSS protection (for older browsers)
    - Referrer-Policy: Controls referrer information
    - Permissions-Policy: Restricts browser features
    - Content-Security-Policy: Controls resource loading
    - Strict-Transport-Security: HSTS (only when force_https=True)
    """

    def __init__(
        self,
        app,
        force_https: bool = False,
        csp_report_only: bool = False,
    ) -> None:
        """
        Initialize security headers middleware.

        Args:
            app: The ASGI application
            force_https: If True, adds HSTS header (production only)
            csp_report_only: If True, uses Content-Security-Policy-Report-Only
        """
        super().__init__(app)
        self.force_https = force_https
        self.csp_report_only = csp_report_only

    def _build_csp(self) -> str:
        """
        Build Content-Security-Policy header value.

        Policy allows:
        - Self-hosted resources
        - Google OAuth (accounts.google.com)
        - Google Fonts
        - Inline styles/scripts (needed for current codebase)
        - Data URIs for images
        """
        directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://accounts.google.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self' https://accounts.google.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self' https://accounts.google.com",
        ]
        return "; ".join(directives)

    def _build_permissions_policy(self) -> str:
        """
        Build Permissions-Policy header value.

        Restricts access to sensitive browser features.
        """
        policies = [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()",
        ]
        return ", ".join(policies)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers to the response."""
        response = await call_next(request)

        # Basic security headers (always added)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = self._build_permissions_policy()

        # Content-Security-Policy
        csp_header = (
            "Content-Security-Policy-Report-Only"
            if self.csp_report_only
            else "Content-Security-Policy"
        )
        response.headers[csp_header] = self._build_csp()

        # HSTS - only in production with HTTPS
        if self.force_https:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
