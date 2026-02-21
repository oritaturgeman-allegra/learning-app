"""
Game result model for tracking learning progress.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class GameResult(Base):
    """
    Stores results from each completed game session.

    Attributes:
        id: Primary key
        game_type: Game identifier (word_match, sentence_scramble, listen_choose, true_false)
        score: Stars earned in this game
        max_score: Maximum possible stars for this game
        word_results: JSON array of per-word results [{word, correct, category}]
        accuracy: Percentage of correct answers (0.0 to 1.0)
        user_id: Optional user ID for future multi-user support
        played_at: When the game was completed
    """

    __tablename__ = "game_results"

    # Core fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    word_results: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    # Session tracking (which unit the game was played in)
    session_slug: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)

    # Future multi-user support
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Timestamp
    played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<GameResult(id={self.id}, game={self.game_type}, "
            f"score={self.score}/{self.max_score})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "game_type": self.game_type,
            "score": self.score,
            "max_score": self.max_score,
            "accuracy": self.accuracy,
            "word_results": json.loads(self.word_results) if self.word_results else [],
            "session_slug": self.session_slug,
            "played_at": self.played_at.isoformat() if self.played_at else None,
        }
