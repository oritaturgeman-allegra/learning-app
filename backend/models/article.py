"""
Article model for storing individual news articles.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Article(Base):
    """
    Stores individual news articles from RSS feeds.

    Each article is linked to a newsletter and contains the full metadata
    from the RSS feed including link, source, text, timestamp, and ai_title.

    Attributes:
        id: Primary key
        newsletter_id: Foreign key to the associated newsletter
        category: News category (us, israel, ai)
        source: Name of the RSS source (e.g., "Globes", "CNBC")
        confidence_score: LLM-assigned quality score (0.0-1.0)
        ai_title: AI-processed article headline/title
        text: Article summary/description text
        link: URL to the original article
        published_at: When the article was published (from RSS feed)
        fetched_at: When we stored this article in the DB
    """

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    newsletter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("newsletters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ai_title: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    link: Mapped[str] = mapped_column(String(1000), nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationship to Newsletter
    newsletter: Mapped["Newsletter"] = relationship("Newsletter", backref="articles_list")

    def __repr__(self) -> str:
        return (
            f"<Article(id={self.id}, source='{self.source}', "
            f"ai_title='{self.ai_title[:30]}...')>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "newsletter_id": self.newsletter_id,
            "category": self.category,
            "source": self.source,
            "confidence_score": self.confidence_score,
            "ai_title": self.ai_title,
            "text": self.text,
            "link": self.link,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }


# Import Newsletter for relationship (avoid circular import)
from backend.models.newsletter import Newsletter  # noqa: E402
