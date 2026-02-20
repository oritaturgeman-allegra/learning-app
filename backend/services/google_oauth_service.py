"""Google OAuth 2.0 service for authentication."""

import logging
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

import httpx

from backend.config import config
from backend.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Scopes we need from Google
GOOGLE_SCOPES = ["openid", "email", "profile"]


@dataclass
class GoogleUserInfo:
    """User information returned from Google OAuth."""

    google_id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None


class GoogleOAuthService:
    """Service for handling Google OAuth 2.0 authentication flow."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> None:
        """Initialize Google OAuth service with credentials."""
        self.client_id = client_id or config.google_client_id
        self.client_secret = client_secret or config.google_client_secret
        self.redirect_uri = redirect_uri or config.google_redirect_uri

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate the Google OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            URL to redirect user to for Google sign-in
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "access_type": "offline",
            "prompt": "select_account",
        }
        if state:
            params["state"] = state

        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> dict:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from Google callback

        Returns:
            Token response containing access_token, refresh_token, etc.

        Raises:
            AuthenticationError: If token exchange fails
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    GOOGLE_TOKEN_URL,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Token exchange failed: {e.response.text}")
                raise AuthenticationError(
                    "google_oauth", f"Failed to exchange code for tokens: {e.response.status_code}"
                )
            except httpx.RequestError as e:
                logger.error(f"Token exchange request failed: {e}")
                raise AuthenticationError("google_oauth", "Failed to connect to Google")

    async def get_user_info(self, access_token: str) -> GoogleUserInfo:
        """
        Fetch user information from Google using access token.

        Args:
            access_token: OAuth access token

        Returns:
            GoogleUserInfo with user's Google profile data

        Raises:
            AuthenticationError: If fetching user info fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                data = response.json()

                # Google returns 'id' as the unique identifier
                google_id = data.get("id")
                email = data.get("email")

                if not google_id or not email:
                    raise AuthenticationError(
                        "google_oauth", "Google did not return required user information"
                    )

                return GoogleUserInfo(
                    google_id=google_id,
                    email=email,
                    name=data.get("name"),
                    picture=data.get("picture"),
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to fetch user info: {e.response.text}")
                raise AuthenticationError(
                    "google_oauth", f"Failed to fetch user info: {e.response.status_code}"
                )
            except httpx.RequestError as e:
                logger.error(f"User info request failed: {e}")
                raise AuthenticationError("google_oauth", "Failed to connect to Google")

    async def authenticate(self, code: str) -> GoogleUserInfo:
        """
        Complete OAuth flow: exchange code and fetch user info.

        Args:
            code: Authorization code from Google callback

        Returns:
            GoogleUserInfo with user's Google profile data
        """
        tokens = await self.exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        if not access_token:
            raise AuthenticationError("google_oauth", "No access token in response")
        return await self.get_user_info(access_token)


# Global service instance
_google_oauth_service: Optional[GoogleOAuthService] = None


def get_google_oauth_service() -> GoogleOAuthService:
    """Get global Google OAuth service singleton."""
    global _google_oauth_service
    if _google_oauth_service is None:
        _google_oauth_service = GoogleOAuthService()
    return _google_oauth_service
