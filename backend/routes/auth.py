"""Authentication routes for user signup and login."""

import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, EmailStr

from backend.config import config
from backend.defaults import APP_VERSION
from backend.exceptions import AuthenticationError, EmailError
from backend.services.db_service import get_db_service, DatabaseError
from backend.services.email_service import get_email_service
from backend.services.google_oauth_service import get_google_oauth_service

# Setup templates for OAuth pages
templates = Jinja2Templates(directory="frontend/templates")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if not has_upper:
        return False, "Password must contain at least one uppercase letter"
    if not has_lower:
        return False, "Password must contain at least one lowercase letter"
    if not has_digit:
        return False, "Password must contain at least one number"

    return True, ""


logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignupRequest(BaseModel):
    """Request body for /api/auth/signup."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ..., min_length=8, description="Password (min 8 chars, upper+lower+number)"
    )
    name: Optional[str] = Field(None, max_length=100, description="Display name")


class LoginRequest(BaseModel):
    """Request body for /api/auth/login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="Password")


class UserResponse(BaseModel):
    """User data returned in responses."""

    id: int
    name: Optional[str]
    email: str
    preferred_categories: list
    is_active: bool
    email_verified: bool
    last_login_at: Optional[str]
    created_at: str


@router.post("/signup", status_code=201)
async def signup(request: SignupRequest) -> dict:
    """Create a new user account with hashed password and send verification email."""
    try:
        db = get_db_service()

        # Validate password strength
        is_valid, error_msg = validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Check if user already exists
        existing_user = db.get_user_by_email(request.email)
        if existing_user:
            if existing_user.google_id:
                raise HTTPException(
                    status_code=409,
                    detail="This email is registered with Google. Please log in with Google.",
                )
            raise HTTPException(
                status_code=409,
                detail="This email is already registered. Please log in with your email and password.",
            )

        # Hash password and create user
        hashed_password = hash_password(request.password)
        user = db.create_user(
            email=request.email,
            password_hash=hashed_password,
            name=request.name,
        )

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        token_expires_at = datetime.now(timezone.utc) + timedelta(
            hours=config.verification_token_ttl_hours
        )
        db.set_verification_token(user.id, verification_token, token_expires_at)

        # Send verification email (non-blocking - don't fail signup if email fails)
        try:
            email_service = get_email_service()
            await email_service.send_verification_email(
                to_email=user.email,
                token=verification_token,
                name=user.name,
            )
            logger.info(f"Verification email sent to {user.email}")
        except EmailError as e:
            logger.warning(f"Failed to send verification email: {e}")
            # Continue with signup - user can request resend

        logger.info(f"New user created: {user.email}")

        return {
            "success": True,
            "message": "Account created successfully. Please check your email to verify your account.",
            "user": UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                preferred_categories=user.to_dict()["preferred_categories"],
                is_active=user.is_active,
                email_verified=user.email_verified,
                last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
                created_at=user.created_at.isoformat(),
            ).model_dump(),
        }
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error during signup: {e}")
        raise HTTPException(status_code=500, detail="Failed to create account")
    except Exception as e:
        logger.error(f"Unexpected error during signup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/login")
async def login(request: LoginRequest) -> dict:
    """Log in with email and password (bcrypt verified)."""
    try:
        db = get_db_service()

        # Find user by email
        user = db.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Check if account is active
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")

        # Check if email is verified (skip for Google OAuth users who don't have password)
        if not user.email_verified and user.password_hash:
            raise HTTPException(
                status_code=403,
                detail="Please verify your email before logging in. Check your inbox for the verification link.",
            )

        # Check if this is a Google-only account (no password)
        if not user.password_hash and user.google_id:
            raise HTTPException(
                status_code=401,
                detail="This email is registered with Google. Please log in with Google.",
            )

        # Verify password with bcrypt
        if not user.password_hash or not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Update last login
        db.update_user_last_login(user.id)

        # Refresh user data to get updated last_login_at
        refreshed_user = db.get_user_by_id(user.id)
        if not refreshed_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve user data")

        logger.info(f"User logged in: {refreshed_user.email}")

        return {
            "success": True,
            "message": "Login successful",
            "user": UserResponse(
                id=refreshed_user.id,
                name=refreshed_user.name,
                email=refreshed_user.email,
                preferred_categories=refreshed_user.to_dict()["preferred_categories"],
                is_active=refreshed_user.is_active,
                email_verified=refreshed_user.email_verified,
                last_login_at=(
                    refreshed_user.last_login_at.isoformat()
                    if refreshed_user.last_login_at
                    else None
                ),
                created_at=refreshed_user.created_at.isoformat(),
            ).model_dump(),
        }
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error during login: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/me")
async def get_current_user(user_id: int) -> dict:
    """Get current user's profile.

    TODO: Replace user_id query param with proper session/JWT token.
    """
    try:
        db = get_db_service()
        user = db.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "success": True,
            "user": UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                preferred_categories=user.to_dict()["preferred_categories"],
                is_active=user.is_active,
                email_verified=user.email_verified,
                last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
                created_at=user.created_at.isoformat(),
            ).model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch user")


# ==================== Email Verification ====================


@router.get("/verify-email/{token}")
async def verify_email(token: str) -> HTMLResponse:
    """
    Verify user's email address using the token from verification email.

    Returns an HTML page showing success or error.
    """
    try:
        db = get_db_service()

        # Find user by token
        user = db.get_user_by_verification_token(token)
        if not user:
            logger.warning("Invalid verification token attempted")
            return _create_verification_error_page("Invalid or expired verification link.")

        # Check if token has expired
        if user.verification_token_expires_at:
            # Handle both timezone-aware and naive datetimes (SQLite returns naive)
            expires_at = user.verification_token_expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires_at:
                logger.warning(f"Expired verification token for user {user.email}")
                return _create_verification_error_page(
                    "This verification link has expired. Please request a new one."
                )

        # Mark email as verified
        verified_user = db.mark_email_verified(user.id)
        if not verified_user:
            raise DatabaseError("mark_email_verified", "Failed to update user")

        logger.info(f"Email verified for user: {verified_user.email}")

        # Send welcome email (non-blocking)
        try:
            email_service = get_email_service()
            await email_service.send_welcome_email(
                to_email=verified_user.email,
                name=verified_user.name,
            )
        except EmailError as e:
            logger.warning(f"Failed to send welcome email: {e}")

        # If user has no name, show profile completion popup (same as Google OAuth)
        if not verified_user.name:
            return _create_oauth_profile_popup(verified_user)

        return _create_verification_success_page(verified_user.name)

    except DatabaseError as e:
        logger.error(f"Database error during email verification: {e}")
        return _create_verification_error_page("An error occurred. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error during email verification: {e}", exc_info=True)
        return _create_verification_error_page("An unexpected error occurred.")


class ResendVerificationRequest(BaseModel):
    """Request body for /api/auth/resend-verification."""

    email: EmailStr = Field(..., description="User's email address")


@router.post("/resend-verification")
async def resend_verification(request: ResendVerificationRequest) -> dict:
    """
    Resend verification email to user.

    Rate limited to 3 requests per hour per email (TODO: implement rate limiting).
    """
    try:
        db = get_db_service()

        # Find user by email
        user = db.get_user_by_email(request.email)
        if not user:
            # Don't reveal if email exists - return success anyway
            return {
                "success": True,
                "message": "If an account exists with this email, a verification link has been sent.",
            }

        # Check if already verified
        if user.email_verified:
            return {
                "success": True,
                "message": "Your email is already verified. You can log in.",
            }

        # Generate new verification token
        verification_token = secrets.token_urlsafe(32)
        token_expires_at = datetime.now(timezone.utc) + timedelta(
            hours=config.verification_token_ttl_hours
        )
        db.set_verification_token(user.id, verification_token, token_expires_at)

        # Send verification email
        try:
            email_service = get_email_service()
            await email_service.send_verification_email(
                to_email=user.email,
                token=verification_token,
                name=user.name,
            )
            logger.info(f"Verification email resent to {user.email}")
        except EmailError as e:
            logger.error(f"Failed to resend verification email: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send verification email. Please try again later.",
            )

        return {
            "success": True,
            "message": "If an account exists with this email, a verification link has been sent.",
        }

    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error during resend verification: {e}")
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error during resend verification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


def _create_verification_success_page(name: Optional[str]) -> HTMLResponse:
    """Create HTML page for successful email verification."""
    greeting = name or "there"
    template = templates.get_template("email_verified_success.html")
    html = template.render(greeting=greeting, version=APP_VERSION)
    return HTMLResponse(content=html)


def _create_verification_error_page(message: str) -> HTMLResponse:
    """Create HTML page for verification error."""
    template = templates.get_template("email_verified_error.html")
    html = template.render(message=message, version=APP_VERSION)
    return HTMLResponse(content=html)


# ==================== Google OAuth ====================


@router.get("/google")
async def google_auth(mode: str = Query("signup")) -> RedirectResponse:
    """Redirect user to Google OAuth consent screen.

    Args:
        mode: 'login' for existing users, 'signup' for new users
    """
    oauth_service = get_google_oauth_service()
    # Pass mode in state parameter so callback knows whether to create users
    auth_url = oauth_service.get_authorization_url(state=mode)
    logger.info(f"Redirecting user to Google OAuth (mode: {mode})")
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
) -> HTMLResponse:
    """
    Handle Google OAuth callback.

    After Google authenticates the user, it redirects here with an authorization code.
    We exchange it for tokens, fetch user info, and create/login the user.

    Args:
        state: 'login' or 'signup' - determines if new users can be created
    """
    # Determine mode from state parameter early
    mode = state if state in ("login", "signup") else "signup"

    # Handle user denying consent
    if error:
        logger.warning(f"Google OAuth error: {error}")
        return _create_oauth_error_response("Google sign-in was cancelled or denied.", mode=mode)

    if not code:
        logger.warning("Google OAuth callback missing code")
        return _create_oauth_error_response(
            "No authorization code received from Google.", mode=mode
        )

    try:
        # Exchange code for user info
        oauth_service = get_google_oauth_service()
        google_user = await oauth_service.authenticate(code)

        db = get_db_service()

        # Check if user exists by Google ID or email
        user = db.get_user_by_google_id(google_user.google_id)
        existing_email_user = db.get_user_by_email(google_user.email)

        is_new_user = False

        if mode == "signup":
            # Signup mode - user must NOT exist
            if user:
                # Already has a Google account
                logger.info(
                    f"Google OAuth signup attempted for existing Google user: {google_user.email}"
                )
                return _create_oauth_error_response(
                    "This Google account is already registered. Please log in instead.",
                    mode=mode,
                )
            if existing_email_user:
                # Email registered with password
                logger.info(
                    f"Google OAuth signup attempted for existing password user: {google_user.email}"
                )
                return _create_oauth_error_response(
                    "This email is registered with a password. Please log in with your email and password.",
                    mode=mode,
                )
            # Create new user with Google
            user = db.create_user(
                email=google_user.email,
                google_id=google_user.google_id,
                name=google_user.name,
                email_verified=True,
            )
            is_new_user = True
            logger.info(f"New Google OAuth user created: {user.email}")
        else:
            # Login mode - create user if doesn't exist (unified login/signup flow)
            if user:
                # Existing Google user - login
                db.update_user_last_login(user.id)
                logger.info(f"Google OAuth login: {user.email}")
            elif existing_email_user:
                # Email exists but with password, not Google
                logger.info(
                    f"Google OAuth login attempted on password account: {google_user.email}"
                )
                return _create_oauth_error_response(
                    "This email is registered with a password. Please log in with your email and password.",
                    mode=mode,
                )
            else:
                # No user found - create new account automatically
                user = db.create_user(
                    email=google_user.email,
                    google_id=google_user.google_id,
                    name=google_user.name,
                    email_verified=True,
                )
                is_new_user = True
                logger.info(f"New Google OAuth user created via login: {user.email}")

        # Only show name verification popup for NEW users
        if is_new_user:
            return _create_oauth_profile_popup(user)
        else:
            return _create_oauth_login_response(user)

    except AuthenticationError as e:
        logger.error(f"Google OAuth authentication failed: {e}")
        return _create_oauth_error_response(
            "Authentication with Google failed. Please try again.", mode=mode
        )
    except DatabaseError as e:
        logger.error(f"Database error during Google OAuth: {e}")
        return _create_oauth_error_response(
            "Failed to create account. Please try again.", mode=mode
        )
    except Exception as e:
        logger.error(f"Unexpected error during Google OAuth: {e}", exc_info=True)
        return _create_oauth_error_response(
            "An unexpected error occurred. Please try again.", mode=mode
        )


class UpdateNameRequest(BaseModel):
    """Request body for /api/auth/update-name."""

    user_id: int = Field(..., description="User ID")
    name: str = Field(..., min_length=1, max_length=100, description="Full name")


@router.post("/update-name")
async def update_name(request: UpdateNameRequest) -> dict:
    """Update user's name after Google OAuth."""
    try:
        db = get_db_service()
        user = db.update_user(user_id=request.user_id, name=request.name)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"Updated name for user {user.id}: {user.name}")

        return {
            "success": True,
            "user": UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                preferred_categories=user.to_dict()["preferred_categories"],
                is_active=user.is_active,
                email_verified=user.email_verified,
                last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
                created_at=user.created_at.isoformat(),
            ).model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating name: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update name")


def _create_oauth_profile_popup(user) -> HTMLResponse:
    """Create HTML response with name verification popup for NEW users only."""
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "preferred_categories": (
            json.loads(user.preferred_categories) if user.preferred_categories else []
        ),
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

    template = templates.get_template("oauth_complete_profile.html")
    html = template.render(
        user_id=user.id,
        user_email=user.email,
        current_name=user.name or "",
        user_data=json.dumps(user_data),
        version=APP_VERSION,
    )
    return HTMLResponse(content=html)


def _create_oauth_login_response(user) -> HTMLResponse:
    """Create HTML response that stores user and redirects to newsletter (no popup)."""
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "preferred_categories": (
            json.loads(user.preferred_categories) if user.preferred_categories else []
        ),
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

    template = templates.get_template("oauth_login_redirect.html")
    html = template.render(user_data=json.dumps(user_data), version=APP_VERSION)
    return HTMLResponse(content=html)


def _create_oauth_error_response(message: str, mode: str = "login") -> HTMLResponse:
    """Create styled HTML error page using template.

    Args:
        message: The error message to display
        mode: 'login' or 'signup' - determines the title
    """
    title = "Sign Up Error" if mode == "signup" else "Log In Error"
    template = templates.get_template("oauth_error.html")
    html = template.render(message=message, title=title, version=APP_VERSION)
    return HTMLResponse(content=html)
