"""
PodcastGeneration model for tracking on-demand podcast generations.

Used to enforce daily generation limits per user and track
which category combinations have been generated.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class PodcastGeneration(Base):
    """
    Tracks each on-demand podcast request (both cache hits and misses).

    Used to enforce the daily limit (counts only actual generations, not cache hits)
    and to track all podcast usage for analytics.

    Attributes:
        id: Primary key
        user_id: The user who triggered the request
        categories: JSON array of selected categories (e.g., '["us","ai"]')
        cache_key: The audio cache key (date-based format)
        cached: True if served from cache, False if newly generated
        created_at: When the request was made
    """

    __tablename__ = "podcast_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    categories: Mapped[str] = mapped_column(Text, nullable=False)
    cache_key: Mapped[str] = mapped_column(String(64), nullable=False)
    cached: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<PodcastGeneration(id={self.id}, user_id={self.user_id}, "
            f"cached={self.cached}, created_at='{self.created_at}')>"
        )
