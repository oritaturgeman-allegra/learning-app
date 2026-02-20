"""
FeedProvider model for storing accumulated RSS feed provider statistics.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class FeedProvider(Base):
    """
    Stores accumulated statistics for each RSS feed provider.
    One row per provider per category (lifetime stats).
    """

    __tablename__ = "feed_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    feed_url: Mapped[str] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reliability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (UniqueConstraint("source_name", "category", name="uq_feed_provider"),)

    def __repr__(self) -> str:
        return f"<FeedProvider(source='{self.source_name}', category='{self.category}', reliability={self.reliability:.1%})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        return {
            "source_name": self.source_name,
            "feed_url": self.feed_url,
            "category": self.category,
            "success_count": self.success_count,
            "total_runs": self.total_runs,
            "reliability": self.reliability,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }
