"""
Integration tests for Google OAuth authentication routes.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from backend.models.base import Base, get_engine, session_scope
from backend.models.user import User
from backend.services.google_oauth_service import GoogleUserInfo


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create fresh tables for each test."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up users after each test
    with session_scope() as session:
        session.query(User).delete()


@pytest.fixture
def client():
    """Create test client."""
    from backend.web_app import app

    return TestClient(app)


class TestGoogleAuthRedirect:
    """Tests for /api/auth/google redirect endpoint."""

    def test_redirects_to_google(self, client):
        """Test that /api/auth/google redirects to Google OAuth."""
        with patch("backend.routes.auth.get_google_oauth_service") as mock_service:
            mock_oauth = MagicMock()
            mock_oauth.get_authorization_url.return_value = (
                "https://accounts.google.com/o/oauth2/v2/auth?client_id=test"
            )
            mock_service.return_value = mock_oauth

            response = client.get("/api/auth/google", follow_redirects=False)

            assert response.status_code == 307
            assert "accounts.google.com" in response.headers["location"]


class TestGoogleCallback:
    """Tests for /api/auth/google/callback endpoint."""

    def test_callback_error_handling(self, client):
        """Test callback handles error parameter."""
        response = client.get("/api/auth/google/callback?error=access_denied")

        assert response.status_code == 200
        assert "cancelled" in response.text.lower() or "denied" in response.text.lower()

    def test_callback_missing_code(self, client):
        """Test callback handles missing code."""
        response = client.get("/api/auth/google/callback")

        assert response.status_code == 200
        assert "authorization code" in response.text.lower()

    def test_callback_creates_new_user(self, client):
        """Test callback creates new user from Google profile and shows profile popup."""
        mock_user_info = GoogleUserInfo(
            google_id="google-123",
            email="newuser@example.com",
            name="New User",
        )

        with patch("backend.routes.auth.get_google_oauth_service") as mock_service:
            mock_oauth = MagicMock()
            mock_oauth.authenticate = AsyncMock(return_value=mock_user_info)
            mock_service.return_value = mock_oauth

            response = client.get("/api/auth/google/callback?code=valid-code")

            assert response.status_code == 200
            assert "newuser@example.com" in response.text
            # New users should see profile completion popup
            assert "Complete Your Profile" in response.text or "full-name" in response.text

            # Verify user was created in database
            with session_scope() as session:
                user = session.query(User).filter_by(email="newuser@example.com").first()
                assert user is not None
                assert user.google_id == "google-123"
                assert user.name == "New User"

    def test_callback_logs_in_existing_google_user(self, client):
        """Test callback logs in existing Google user with mode=login."""
        # Create existing user with Google ID
        with session_scope() as session:
            user = User(
                email="existing@example.com",
                google_id="google-existing",
                name="Existing User",
            )
            session.add(user)
            session.commit()

        mock_user_info = GoogleUserInfo(
            google_id="google-existing",
            email="existing@example.com",
            name="Existing User",
        )

        with patch("backend.routes.auth.get_google_oauth_service") as mock_service:
            mock_oauth = MagicMock()
            mock_oauth.authenticate = AsyncMock(return_value=mock_user_info)
            mock_service.return_value = mock_oauth

            # Must use mode=login for existing users
            response = client.get("/api/auth/google/callback?code=valid-code&state=login")

            assert response.status_code == 200
            # Existing users should NOT see profile popup, just redirect
            assert "Complete Your Profile" not in response.text
            assert "localStorage.setItem" in response.text
            assert "/newsletter" in response.text

            # Verify last_login was updated
            with session_scope() as session:
                user = session.query(User).filter_by(email="existing@example.com").first()
                assert user.last_login_at is not None

    def test_callback_rejects_existing_user_in_signup_mode(self, client):
        """Test callback rejects existing user when using signup mode."""
        # Create existing user with Google ID
        with session_scope() as session:
            user = User(
                email="existing@example.com",
                google_id="google-existing",
                name="Existing User",
            )
            session.add(user)
            session.commit()

        mock_user_info = GoogleUserInfo(
            google_id="google-existing",
            email="existing@example.com",
            name="Existing User",
        )

        with patch("backend.routes.auth.get_google_oauth_service") as mock_service:
            mock_oauth = MagicMock()
            mock_oauth.authenticate = AsyncMock(return_value=mock_user_info)
            mock_service.return_value = mock_oauth

            # Default is signup mode - should reject existing user
            response = client.get("/api/auth/google/callback?code=valid-code")

            assert response.status_code == 200
            assert "This Google account is already registered" in response.text

    def test_callback_rejects_password_user_in_signup_mode(self, client):
        """Test callback rejects existing password user when using Google signup."""
        # Create existing user with password (no Google ID)
        with session_scope() as session:
            user = User(
                email="password-user@example.com",
                password_hash="hashed-password",
                name="Password User",
            )
            session.add(user)
            session.commit()

        mock_user_info = GoogleUserInfo(
            google_id="google-new-link",
            email="password-user@example.com",  # Same email
            name="Password User",
        )

        with patch("backend.routes.auth.get_google_oauth_service") as mock_service:
            mock_oauth = MagicMock()
            mock_oauth.authenticate = AsyncMock(return_value=mock_user_info)
            mock_service.return_value = mock_oauth

            # Signup mode should reject existing email
            response = client.get("/api/auth/google/callback?code=valid-code")

            assert response.status_code == 200
            assert "This email is registered with a password" in response.text

    def test_callback_rejects_password_user_in_login_mode(self, client):
        """Test callback rejects password user trying to login with Google."""
        # Create existing user with password (no Google ID)
        with session_scope() as session:
            user = User(
                email="password-user@example.com",
                password_hash="hashed-password",
                name="Password User",
            )
            session.add(user)
            session.commit()

        mock_user_info = GoogleUserInfo(
            google_id="google-new-link",
            email="password-user@example.com",  # Same email
            name="Password User",
        )

        with patch("backend.routes.auth.get_google_oauth_service") as mock_service:
            mock_oauth = MagicMock()
            mock_oauth.authenticate = AsyncMock(return_value=mock_user_info)
            mock_service.return_value = mock_oauth

            # Login mode should tell user to use password
            response = client.get("/api/auth/google/callback?code=valid-code&state=login")

            assert response.status_code == 200
            assert "registered with a password" in response.text

    def test_callback_creates_user_in_login_mode_if_not_exists(self, client):
        """Test callback auto-creates user when logging in with Google if user doesn't exist."""
        mock_user_info = GoogleUserInfo(
            google_id="google-new",
            email="nonexistent@example.com",
            name="New User",
        )

        with patch("backend.routes.auth.get_google_oauth_service") as mock_service:
            mock_oauth = MagicMock()
            mock_oauth.authenticate = AsyncMock(return_value=mock_user_info)
            mock_service.return_value = mock_oauth

            # Login mode should create user automatically (unified login/signup flow)
            response = client.get("/api/auth/google/callback?code=valid-code&state=login")

            assert response.status_code == 200
            # Should show profile completion popup for new user
            assert "nonexistent@example.com" in response.text or "New User" in response.text

    def test_callback_authentication_error(self, client):
        """Test callback handles authentication errors."""
        from backend.exceptions import AuthenticationError

        with patch("backend.routes.auth.get_google_oauth_service") as mock_service:
            mock_oauth = MagicMock()
            mock_oauth.authenticate = AsyncMock(
                side_effect=AuthenticationError("google_oauth", "Token exchange failed")
            )
            mock_service.return_value = mock_oauth

            response = client.get("/api/auth/google/callback?code=invalid-code")

            assert response.status_code == 200
            assert "failed" in response.text.lower() or "error" in response.text.lower()
