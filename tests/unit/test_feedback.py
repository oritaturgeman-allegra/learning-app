"""Unit tests for feedback API endpoint and email service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from backend.web_app import app
from backend.services.email_service import EmailService
from backend.exceptions import EmailError


class TestFeedbackEndpoint:
    """Tests for feedback API endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_submit_feedback_missing_text(self, client):
        """Test feedback submission fails without text."""
        response = client.post("/api/feedback", data={})
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_submit_feedback_success(self):
        """Test successful feedback submission."""
        with patch("backend.routes.feedback.get_email_service") as mock_get_email_service:
            mock_service = MagicMock()
            mock_service.send_feedback_email = AsyncMock(return_value=True)
            mock_get_email_service.return_value = mock_service

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(
                    "/api/feedback",
                    data={"feedback_text": "Great app! Love the design."},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Thank you" in data["message"]

            mock_service.send_feedback_email.assert_called_once()
            call_kwargs = mock_service.send_feedback_email.call_args[1]
            assert call_kwargs["feedback_text"] == "Great app! Love the design."
            assert call_kwargs["user_name"] is None
            assert call_kwargs["user_email"] is None

    @pytest.mark.asyncio
    async def test_submit_feedback_with_user_info(self):
        """Test feedback submission includes user name and email."""
        with patch("backend.routes.feedback.get_email_service") as mock_get_email_service:
            mock_service = MagicMock()
            mock_service.send_feedback_email = AsyncMock(return_value=True)
            mock_get_email_service.return_value = mock_service

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(
                    "/api/feedback",
                    data={
                        "feedback_text": "Love it!",
                        "user_name": "Jane Doe",
                        "user_email": "jane@example.com",
                    },
                )

            assert response.status_code == 200
            call_kwargs = mock_service.send_feedback_email.call_args[1]
            assert call_kwargs["user_name"] == "Jane Doe"
            assert call_kwargs["user_email"] == "jane@example.com"

    @pytest.mark.asyncio
    async def test_submit_feedback_with_file(self):
        """Test feedback submission with file attachment."""
        with patch("backend.routes.feedback.get_email_service") as mock_get_email_service:
            mock_service = MagicMock()
            mock_service.send_feedback_email = AsyncMock(return_value=True)
            mock_get_email_service.return_value = mock_service

            # Create a fake image file
            image_content = b"fake image content"

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(
                    "/api/feedback",
                    data={"feedback_text": "Here's a screenshot"},
                    files={"files": ("test.png", image_content, "image/png")},
                )

            assert response.status_code == 200
            mock_service.send_feedback_email.assert_called_once()
            call_kwargs = mock_service.send_feedback_email.call_args[1]
            assert call_kwargs["attachments"] is not None
            assert len(call_kwargs["attachments"]) == 1
            assert call_kwargs["attachments"][0][0] == "test.png"

    @pytest.mark.asyncio
    async def test_submit_feedback_invalid_file_type(self):
        """Test feedback submission rejects invalid file types."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/feedback",
                data={"feedback_text": "Test feedback"},
                files={"files": ("test.exe", b"malicious content", "application/x-msdownload")},
            )

        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_submit_feedback_image_too_large(self):
        """Test feedback submission rejects oversized images (>10MB)."""
        # Create an image larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/feedback",
                data={"feedback_text": "Test feedback"},
                files={"files": ("large.png", large_content, "image/png")},
            )

        assert response.status_code == 400
        assert "exceeds maximum size" in response.json()["detail"]
        assert "10MB" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_submit_feedback_video_too_large(self):
        """Test feedback submission rejects oversized videos (>50MB)."""
        # Create a video larger than 50MB
        large_content = b"x" * (51 * 1024 * 1024)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/feedback",
                data={"feedback_text": "Test feedback"},
                files={"files": ("large.mp4", large_content, "video/mp4")},
            )

        assert response.status_code == 400
        assert "exceeds maximum size" in response.json()["detail"]
        assert "50MB" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_submit_feedback_too_many_files(self):
        """Test feedback submission rejects too many files."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            files = [
                ("files", (f"file{i}.png", b"content", "image/png"))
                for i in range(6)  # More than MAX_FILES (5)
            ]
            response = await ac.post(
                "/api/feedback",
                data={"feedback_text": "Test feedback"},
                files=files,
            )

        assert response.status_code == 400
        assert "Maximum" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_submit_feedback_email_error(self):
        """Test feedback submission handles email errors gracefully."""
        with patch("backend.routes.feedback.get_email_service") as mock_get_email_service:
            mock_service = MagicMock()
            mock_service.send_feedback_email = AsyncMock(
                side_effect=EmailError("send", "SendGrid error")
            )
            mock_get_email_service.return_value = mock_service

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(
                    "/api/feedback",
                    data={"feedback_text": "Test feedback"},
                )

            assert response.status_code == 500
            assert "Failed to send feedback" in response.json()["detail"]


class TestFeedbackEmailService:
    """Tests for feedback email functionality in EmailService."""

    @pytest.mark.asyncio
    @patch("backend.services.email_service.config")
    async def test_send_feedback_email_not_configured(self, mock_config):
        """Test send_feedback_email returns False when not configured."""
        mock_config.email_api_key = ""
        mock_config.email_from_address = ""
        mock_config.email_from_name = ""
        mock_config.base_url = "http://localhost"

        service = EmailService(api_key="", from_address="")
        result = await service.send_feedback_email(feedback_text="Test feedback")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_feedback_email_success(self):
        """Test successful feedback email sending."""
        service = EmailService(
            api_key="SG.test_key",
            from_address="noreply@test.com",
            from_name="Test App",
            base_url="http://localhost:5000",
        )

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.text = ""

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_feedback_email(
                feedback_text="Great app!",
            )

        assert result is True
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert (
            payload["personalizations"][0]["to"][0]["email"] == "yournewsletter.yourway@gmail.com"
        )
        assert payload["subject"] == "User Feedback - Your Newsletter, Your Way"

    @pytest.mark.asyncio
    async def test_send_feedback_email_with_attachments(self):
        """Test feedback email with attachments."""
        service = EmailService(
            api_key="SG.test_key",
            from_address="noreply@test.com",
            from_name="Test App",
        )

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.text = ""

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        attachments = [
            ("screenshot.png", b"fake image data", "image/png"),
            ("video.mp4", b"fake video data", "video/mp4"),
        ]

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.send_feedback_email(
                feedback_text="Check these attachments",
                attachments=attachments,
            )

        assert result is True
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert "attachments" in payload
        assert len(payload["attachments"]) == 2
        assert payload["attachments"][0]["filename"] == "screenshot.png"
        assert payload["attachments"][1]["filename"] == "video.mp4"

    def test_build_feedback_email_html_contains_text(self):
        """Test feedback email HTML contains the feedback text."""
        service = EmailService(base_url="http://localhost:5000")
        html = service._build_feedback_email_html(
            feedback_text="This is my feedback message",
        )
        assert "This is my feedback message" in html
        assert "New User Feedback" in html

    def test_build_feedback_email_html_with_user_info(self):
        """Test feedback email HTML includes user name and email."""
        service = EmailService(base_url="http://localhost:5000")
        html = service._build_feedback_email_html(
            feedback_text="Great app!",
            user_name="Jane Doe",
            user_email="jane@example.com",
        )
        assert "Feedback from Jane Doe" in html
        assert "jane@example.com" in html
        assert "New User Feedback" not in html

    def test_build_feedback_email_text_contains_text(self):
        """Test feedback email text contains the feedback text."""
        service = EmailService(base_url="http://localhost:5000")
        text = service._build_feedback_email_text(
            feedback_text="This is my feedback message",
        )
        assert "This is my feedback message" in text

    def test_build_feedback_email_text_with_user_info(self):
        """Test feedback email text includes user name and email."""
        service = EmailService(base_url="http://localhost:5000")
        text = service._build_feedback_email_text(
            feedback_text="Great app!",
            user_name="Jane Doe",
            user_email="jane@example.com",
        )
        assert "Feedback from Jane Doe" in text
        assert "jane@example.com" in text
