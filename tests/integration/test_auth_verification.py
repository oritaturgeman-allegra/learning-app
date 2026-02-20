"""Integration tests for email verification endpoints."""

import secrets
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from backend.web_app import app
from backend.models.base import Base, get_engine, session_scope
from backend.models.user import User
from backend.services.db_service import DatabaseService


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create fresh tables for each test."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up data after each test
    with session_scope() as session:
        session.query(User).delete()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def db_service():
    """Get database service."""
    return DatabaseService()


@pytest.fixture
def mock_email_service():
    """Mock email service to avoid sending real emails."""
    with patch("backend.routes.auth.get_email_service") as mock:
        mock_service = AsyncMock()
        mock_service.send_verification_email = AsyncMock(return_value=True)
        mock_service.send_welcome_email = AsyncMock(return_value=True)
        mock.return_value = mock_service
        yield mock_service


class TestSignupWithVerification:
    """Tests for signup endpoint with email verification."""

    def test_signup_returns_email_verified_false(self, client, mock_email_service):
        """Test signup returns email_verified: false for new users."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["user"]["email_verified"] is False
        assert "verify your account" in data["message"].lower()

    def test_signup_sends_verification_email(self, client, mock_email_service):
        """Test signup sends verification email."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "verifytest@example.com",
                "password": "SecurePass123",
            },
        )
        assert response.status_code == 201
        mock_email_service.send_verification_email.assert_called_once()
        call_args = mock_email_service.send_verification_email.call_args
        assert call_args[1]["to_email"] == "verifytest@example.com"
        assert call_args[1]["token"] is not None

    def test_signup_sets_verification_token(self, client, mock_email_service, db_service):
        """Test signup sets verification token in database."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "tokentest@example.com",
                "password": "SecurePass123",
            },
        )
        assert response.status_code == 201

        user = db_service.get_user_by_email("tokentest@example.com")
        assert user.verification_token is not None
        assert user.verification_token_expires_at is not None
        # Handle timezone-naive datetime from SQLite
        expires_at = user.verification_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        assert expires_at > datetime.now(timezone.utc)


class TestVerifyEmail:
    """Tests for email verification endpoint."""

    def test_verify_email_success(self, client, db_service, mock_email_service):
        """Test successful email verification."""
        # Create user with token and name (name required to see success page)
        user = db_service.create_user(
            email="verify@example.com",
            password_hash="hashed_password",
            name="Test User",
        )
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        db_service.set_verification_token(user.id, token, expires_at)

        response = client.get(f"/api/auth/verify-email/{token}")
        assert response.status_code == 200
        assert "Email Verified" in response.text

        # Check user is now verified
        updated_user = db_service.get_user_by_id(user.id)
        assert updated_user.email_verified is True
        assert updated_user.verification_token is None

    def test_verify_email_invalid_token(self, client):
        """Test verification with invalid token shows error."""
        response = client.get("/api/auth/verify-email/invalid_token_123")
        assert response.status_code == 200  # Returns HTML page
        assert "Verification Failed" in response.text
        assert "Invalid or expired" in response.text

    def test_verify_email_expired_token(self, client, db_service):
        """Test verification with expired token shows error."""
        # Create user with expired token
        user = db_service.create_user(
            email="expired@example.com",
            password_hash="hashed_password",
        )
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) - timedelta(hours=1)  # Expired
        db_service.set_verification_token(user.id, token, expires_at)

        response = client.get(f"/api/auth/verify-email/{token}")
        assert response.status_code == 200
        assert "expired" in response.text.lower()

    def test_verify_email_sends_welcome_email(self, client, db_service, mock_email_service):
        """Test successful verification sends welcome email."""
        user = db_service.create_user(
            email="welcome@example.com",
            password_hash="hashed_password",
            name="Welcome User",
        )
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        db_service.set_verification_token(user.id, token, expires_at)

        client.get(f"/api/auth/verify-email/{token}")
        mock_email_service.send_welcome_email.assert_called_once()


class TestResendVerification:
    """Tests for resend verification endpoint."""

    def test_resend_verification_success(self, client, db_service, mock_email_service):
        """Test successful resend verification."""
        # Create unverified user
        db_service.create_user(
            email="resend@example.com",
            password_hash="hashed_password",
        )

        response = client.post(
            "/api/auth/resend-verification",
            json={"email": "resend@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        mock_email_service.send_verification_email.assert_called_once()

    def test_resend_verification_nonexistent_email(self, client, mock_email_service):
        """Test resend for non-existent email doesn't reveal if email exists."""
        response = client.post(
            "/api/auth/resend-verification",
            json={"email": "nonexistent@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should not send email for non-existent user
        mock_email_service.send_verification_email.assert_not_called()

    def test_resend_verification_already_verified(self, client, db_service, mock_email_service):
        """Test resend for already verified user."""
        db_service.create_user(
            email="alreadyverified@example.com",
            password_hash="hashed_password",
            email_verified=True,
        )

        response = client.post(
            "/api/auth/resend-verification",
            json={"email": "alreadyverified@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "already verified" in data["message"].lower()
        mock_email_service.send_verification_email.assert_not_called()

    def test_resend_verification_generates_new_token(self, client, db_service, mock_email_service):
        """Test resend generates a new token."""
        user = db_service.create_user(
            email="newtoken@example.com",
            password_hash="hashed_password",
        )
        old_token = secrets.token_urlsafe(32)
        old_expires = datetime.now(timezone.utc) + timedelta(hours=12)
        db_service.set_verification_token(user.id, old_token, old_expires)

        client.post(
            "/api/auth/resend-verification",
            json={"email": "newtoken@example.com"},
        )

        updated_user = db_service.get_user_by_email("newtoken@example.com")
        assert updated_user.verification_token != old_token
        # Handle timezone-naive datetime from SQLite
        new_expires = updated_user.verification_token_expires_at
        if new_expires.tzinfo is None:
            new_expires = new_expires.replace(tzinfo=timezone.utc)
        assert new_expires > old_expires


class TestLoginWithVerification:
    """Tests for login endpoint with email verification status."""

    def test_login_returns_email_verified_status(self, client, db_service):
        """Test login returns email_verified status."""
        # Create verified user with bcrypt hash
        import bcrypt

        password = "SecurePass123"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        db_service.create_user(
            email="logintest@example.com",
            password_hash=password_hash,
            email_verified=True,
        )

        response = client.post(
            "/api/auth/login",
            json={
                "email": "logintest@example.com",
                "password": password,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email_verified"] is True

    def test_login_unverified_user_is_blocked(self, client, db_service):
        """Test unverified users are blocked from logging in."""
        import bcrypt

        password = "SecurePass123"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        db_service.create_user(
            email="unverifiedlogin@example.com",
            password_hash=password_hash,
            email_verified=False,
        )

        response = client.post(
            "/api/auth/login",
            json={
                "email": "unverifiedlogin@example.com",
                "password": password,
            },
        )
        assert response.status_code == 403
        data = response.json()
        assert "verify your email" in data["detail"].lower()
