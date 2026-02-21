"""
App state model for persistent application-level settings.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class AppState(Base):
    """
    Key-value store for application state (e.g., reset_at timestamp).

    Attributes:
        id: Primary key
        key: Unique state key (e.g., "reset_at")
        value: State value as string
        updated_at: When this state was last modified
    """

    __tablename__ = "app_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<AppState(key={self.key}, value={self.value})>"
