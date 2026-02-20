"""Shared fixtures for integration tests."""

import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def disable_rate_limiting(request):
    """Disable rate limiting for integration tests.

    Rate limiting is tested separately in tests/integration/test_rate_limit.py
    with its own isolated app instance.

    Tests can opt out by using: @pytest.mark.enable_rate_limiting
    """
    # Check if test has marker to enable rate limiting
    if request.node.get_closest_marker("enable_rate_limiting"):
        yield
        return

    with patch(
        "backend.middleware.rate_limit.RateLimitMiddleware._is_rate_limited",
        return_value=(False, 0),
    ):
        yield
