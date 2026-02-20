"""
Unit tests for Google OAuth service.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.exceptions import AuthenticationError
from backend.services.google_oauth_service import (
    GoogleOAuthService,
    GoogleUserInfo,
    GOOGLE_AUTH_URL,
    GOOGLE_SCOPES,
)


class TestGoogleOAuthService:
    """Tests for GoogleOAuthService."""

    def test_init_with_defaults(self):
        """Test service initializes with config defaults."""
        with patch("backend.services.google_oauth_service.config") as mock_config:
            mock_config.google_client_id = "test-client-id"
            mock_config.google_client_secret = "test-secret"
            mock_config.google_redirect_uri = "http://localhost/callback"

            service = GoogleOAuthService()

            assert service.client_id == "test-client-id"
            assert service.client_secret == "test-secret"
            assert service.redirect_uri == "http://localhost/callback"

    def test_init_with_custom_values(self):
        """Test service initializes with custom values."""
        service = GoogleOAuthService(
            client_id="custom-id",
            client_secret="custom-secret",
            redirect_uri="http://custom/callback",
        )

        assert service.client_id == "custom-id"
        assert service.client_secret == "custom-secret"
        assert service.redirect_uri == "http://custom/callback"

    def test_get_authorization_url(self):
        """Test generating authorization URL."""
        service = GoogleOAuthService(
            client_id="test-client-id",
            client_secret="test-secret",
            redirect_uri="http://localhost/callback",
        )

        url = service.get_authorization_url()

        assert GOOGLE_AUTH_URL in url
        assert "client_id=test-client-id" in url
        assert "redirect_uri=http" in url
        assert "response_type=code" in url
        assert "scope=" in url
        for scope in GOOGLE_SCOPES:
            assert (
                scope in url or scope.replace(" ", "+") in url or scope.replace(" ", "%20") in url
            )

    def test_get_authorization_url_with_state(self):
        """Test generating authorization URL with state parameter."""
        service = GoogleOAuthService(
            client_id="test-client-id",
            client_secret="test-secret",
            redirect_uri="http://localhost/callback",
        )

        url = service.get_authorization_url(state="random-state-123")

        assert "state=random-state-123" in url

    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_success(self):
        """Test successful code exchange."""
        service = GoogleOAuthService(
            client_id="test-client-id",
            client_secret="test-secret",
            redirect_uri="http://localhost/callback",
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await service.exchange_code_for_tokens("auth-code-123")

            assert result["access_token"] == "mock-access-token"
            assert result["refresh_token"] == "mock-refresh-token"

    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_failure(self):
        """Test code exchange failure."""
        import httpx

        service = GoogleOAuthService(
            client_id="test-client-id",
            client_secret="test-secret",
            redirect_uri="http://localhost/callback",
        )

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid code"

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Error", request=MagicMock(), response=mock_response
                )
            )
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(AuthenticationError) as exc_info:
                await service.exchange_code_for_tokens("invalid-code")

            assert "google_oauth" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_info_success(self):
        """Test successful user info fetch."""
        service = GoogleOAuthService(
            client_id="test-client-id",
            client_secret="test-secret",
            redirect_uri="http://localhost/callback",
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "google-user-123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/photo.jpg",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await service.get_user_info("mock-access-token")

            assert isinstance(result, GoogleUserInfo)
            assert result.google_id == "google-user-123"
            assert result.email == "test@example.com"
            assert result.name == "Test User"
            assert result.picture == "https://example.com/photo.jpg"

    @pytest.mark.asyncio
    async def test_get_user_info_missing_email(self):
        """Test user info fetch with missing email."""
        service = GoogleOAuthService(
            client_id="test-client-id",
            client_secret="test-secret",
            redirect_uri="http://localhost/callback",
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "google-user-123",
            # No email
            "name": "Test User",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(AuthenticationError) as exc_info:
                await service.get_user_info("mock-access-token")

            assert "required user information" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_authenticate_full_flow(self):
        """Test full authentication flow."""
        service = GoogleOAuthService(
            client_id="test-client-id",
            client_secret="test-secret",
            redirect_uri="http://localhost/callback",
        )

        # Mock token exchange
        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {"access_token": "mock-access-token"}
        token_response.raise_for_status = MagicMock()

        # Mock user info
        userinfo_response = MagicMock()
        userinfo_response.status_code = 200
        userinfo_response.json.return_value = {
            "id": "google-user-123",
            "email": "test@example.com",
            "name": "Test User",
        }
        userinfo_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=token_response)
            mock_client_instance.get = AsyncMock(return_value=userinfo_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await service.authenticate("auth-code-123")

            assert isinstance(result, GoogleUserInfo)
            assert result.google_id == "google-user-123"
            assert result.email == "test@example.com"


class TestGoogleUserInfo:
    """Tests for GoogleUserInfo dataclass."""

    def test_create_with_required_fields(self):
        """Test creating GoogleUserInfo with required fields only."""
        user_info = GoogleUserInfo(
            google_id="123",
            email="test@example.com",
        )

        assert user_info.google_id == "123"
        assert user_info.email == "test@example.com"
        assert user_info.name is None
        assert user_info.picture is None

    def test_create_with_all_fields(self):
        """Test creating GoogleUserInfo with all fields."""
        user_info = GoogleUserInfo(
            google_id="123",
            email="test@example.com",
            name="Test User",
            picture="https://example.com/photo.jpg",
        )

        assert user_info.google_id == "123"
        assert user_info.email == "test@example.com"
        assert user_info.name == "Test User"
        assert user_info.picture == "https://example.com/photo.jpg"
