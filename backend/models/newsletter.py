"""
Newsletter model for storing generated newsletter data.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Newsletter(Base):
    """
    Stores newsletter metadata and AI-generated content.

    Articles are stored in the separate `articles` table (related via newsletter_id).

    Attributes:
        id: Primary key
        user_id: Optional foreign key to users table (nullable for anonymous/legacy)
        sentiment: Market sentiment scores per category (JSON format: {"us": <score>, "israel": <score>, ...})
        language: Language code (en/he)
        podcast_dialog: Pre-generated podcast dialog (JSON array: [["female", "text"], ["male", "text"], ...])
        llm_provider: LLM provider used for text generation (e.g., openai, gemini)
        tts_provider: TTS provider used for podcast audio (e.g., openai, gemini)
        created_at: When the newsletter was generated
    """

    __tablename__ = "newsletters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sentiment: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # JSON: {"us": 65, "israel": 48}
    language: Mapped[str] = mapped_column(String(5), default="en", nullable=False)
    podcast_dialog: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # JSON: [["female", "Hello..."], ["male", "Today..."]]
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tts_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Newsletter(id={self.id}, language='{self.language}', created_at='{self.created_at}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        import json

        return {
            "id": self.id,
            "user_id": self.user_id,
            "sentiment": json.loads(self.sentiment) if self.sentiment else None,
            "language": self.language,
            "podcast_dialog": json.loads(self.podcast_dialog) if self.podcast_dialog else None,
            "llm_provider": self.llm_provider,
            "tts_provider": self.tts_provider,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
