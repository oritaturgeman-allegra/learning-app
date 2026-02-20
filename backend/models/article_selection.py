"""
ArticleSelection model for tracking all fetched articles (selected + rejected).

Used by the AI Analytics Service to analyze feed provider performance.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class ArticleSelection(Base):
    """
    Tracks all articles fetched from RSS feeds for analytics purposes.

    Unlike the Article table (which only stores selected articles),
    this table stores ALL fetched articles with their selection status.

    Attributes:
        id: Primary key
        source_name: RSS source name (e.g., "Yahoo Finance", "CNBC")
        category: News category (us, israel, ai, crypto)
        title: Article headline (truncated to 500 chars)
        link: URL to the original article
        selected: Whether the article was selected for the newsletter
        newsletter_id: FK to newsletter (only if selected)
        fetched_at: When the article was fetched
    """

    __tablename__ = "article_selections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    link: Mapped[str] = mapped_column(String(1000), nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    newsletter_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("newsletters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        status = "SELECTED" if self.selected else "REJECTED"
        return f"<ArticleSelection({status}, source='{self.source_name}', title='{self.title[:30]}...')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "source_name": self.source_name,
            "category": self.category,
            "title": self.title,
            "link": self.link,
            "selected": self.selected,
            "newsletter_id": self.newsletter_id,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }
