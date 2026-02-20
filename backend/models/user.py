"""
User model for authentication and preferences.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class User(Base):
    """
    Stores user account information and preferences.

    Attributes:
        id: Primary key
        name: Display name
        email: User's email address (unique, used for login)
        preferred_categories: JSON array of selected categories (e.g., '["us","israel","ai","crypto"]')
        is_active: Whether account is enabled
        last_login_at: Last login timestamp
        password_hash: Hashed password (nullable for Google-only auth)
        google_id: Google OAuth identifier (nullable, unique)
        email_verified: Whether email has been verified
        verification_token: Token for email verification (nullable)
        verification_token_expires_at: When the verification token expires
        email_notifications: Whether user wants email digests
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"

    # Core fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    preferred_categories: Mapped[str] = mapped_column(
        Text, default='["us","israel","ai","crypto"]', nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Auth fields
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)

    # Email verification
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_token: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, nullable=True
    )
    verification_token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Settings
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        import json

        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "preferred_categories": (
                json.loads(self.preferred_categories) if self.preferred_categories else []
            ),
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "email_notifications": self.email_notifications,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
