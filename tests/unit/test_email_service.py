"""Unit tests for email service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.services.email_service import EmailService, get_email_service
from backend.exceptions import EmailError


class TestEmailService:
    """Tests for EmailService class."""

    def test_is_configured_with_api_key(self):
        """Test is_configured returns True when API key is set."""
        service = EmailService(
            api_key="SG.test_key",
            from_address="test@example.com",
        )
        assert service.is_configured() is True

    @patch("backend.services.email_service.config")
    def test_is_configured_without_api_key(self, mock_config):
        """Test is_configured returns False when API key is missing."""
        # Mock config to have empty values so fallback doesn't override
        mock_config.email_api_key = ""
        mock_config.email_from_address = "test@example.com"
        mock_config.email_from_name = "Test"
        mock_config.base_url = "http://localhost"

        service = EmailService(
            api_key="",
            from_address="test@example.com",
        )
        assert service.is_configured() is False

    def test_is_configured_without_from_address(self):
        """Test is_configured returns False when from_address is empty."""
        # Need to override by directly setting the attribute after init
        # because __init__ may use config defaults
        service = EmailService(api_key="SG.test_key")
        service.from_address = ""  # Override to empty
        assert service.is_configured() is False

    @pytest.mark.asyncio
    @patch("backend.services.email_service.config")
    async def test_send_verification_email_not_configured(self, mock_config):
        """Test send_verification_email returns False when not configured."""
        # Mock config to have empty values so fallback doesn't override
        mock_config.email_api_key = ""
        mock_config.email_from_address = ""
        mock_config.email_from_name = ""
        mock_config.base_url = "http://localhost"

        service = EmailService(api_key="", from_address="")
        result = await service.send_verification_email(
            to_email="user@example.com",
            token="test_token",
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_send_verification_email_success(self):
        """Test successful verification email sending."""
        service = EmailService(
            api_key="SG.test_key",
            from_address="noreply@test.com",
            from_name="Test App",
            base_url="http://localhost:5000",
        )

        # Mock httpx.AsyncClient
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.text = ""

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_verification_email(
                to_email="user@example.com",
                token="test_token_123",
                name="Test User",
            )

        assert result is True
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://api.sendgrid.com/v3/mail/send"
        payload = call_args[1]["json"]
        assert payload["personalizations"][0]["to"][0]["email"] == "user@example.com"
        assert payload["subject"] == "Verify your email - Your Newsletter, Your Way"

    @pytest.mark.asyncio
    async def test_send_verification_email_api_error(self):
        """Test verification email raises error on API failure."""
        service = EmailService(
            api_key="SG.test_key",
            from_address="noreply@test.com",
        )

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(EmailError) as exc_info:
                await service.send_verification_email(
                    to_email="user@example.com",
                    token="test_token",
                )

        assert exc_info.value.operation == "send"
        assert "400" in exc_info.value.details

    @pytest.mark.asyncio
    async def test_send_welcome_email_success(self):
        """Test successful welcome email sending."""
        service = EmailService(
            api_key="SG.test_key",
            from_address="noreply@test.com",
            from_name="Test App",
            base_url="http://localhost:5000",
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ""

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_welcome_email(
                to_email="user@example.com",
                name="Test User",
            )

        assert result is True
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["subject"] == "Welcome to Your Newsletter, Your Way!"

    def test_build_verification_email_html_contains_link(self):
        """Test verification email HTML contains the verification link."""
        service = EmailService(base_url="http://localhost:5000")
        html = service._build_verification_email_html(
            greeting="Hi Test,",
            verification_url="http://localhost:5000/api/auth/verify-email/abc123",
        )
        assert "http://localhost:5000/api/auth/verify-email/abc123" in html
        assert "Hi Test," in html
        assert "Verify My Email" in html

    def test_build_verification_email_text_contains_link(self):
        """Test verification email text contains the verification link."""
        service = EmailService(base_url="http://localhost:5000")
        text = service._build_verification_email_text(
            greeting="Hi Test,",
            verification_url="http://localhost:5000/api/auth/verify-email/abc123",
        )
        assert "http://localhost:5000/api/auth/verify-email/abc123" in text
        assert "Hi Test," in text


class TestGetEmailService:
    """Tests for get_email_service singleton."""

    def test_returns_same_instance(self):
        """Test get_email_service returns the same instance."""
        # Reset the singleton
        import backend.services.email_service as email_module

        email_module._email_service = None

        service1 = get_email_service()
        service2 = get_email_service()
        assert service1 is service2

        # Clean up
        email_module._email_service = None
