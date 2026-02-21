"""
Tests for database models.
"""

from backend.models.base import init_db, session_scope
from backend.models.game_result import GameResult


class TestGameResultModel:
    """Tests for the GameResult model."""

    def test_repr(self):
        """GameResult repr shows key fields."""
        init_db()
        with session_scope() as session:
            result = GameResult(
                game_type="word_match",
                score=8,
                max_score=10,
                accuracy=0.8,
                word_results="[]",
            )
            session.add(result)
            session.flush()

            repr_str = repr(result)
            assert "word_match" in repr_str
            assert "8" in repr_str
            assert "10" in repr_str

    def test_to_dict(self):
        """to_dict returns all expected fields."""
        init_db()
        with session_scope() as session:
            result = GameResult(
                game_type="listen_choose",
                score=7,
                max_score=10,
                accuracy=0.7,
                word_results='[{"word": "coat", "correct": true}]',
            )
            session.add(result)
            session.flush()
            session.refresh(result)

            d = result.to_dict()
            assert d["game_type"] == "listen_choose"
            assert d["score"] == 7
            assert d["max_score"] == 10
            assert d["accuracy"] == 0.7
            assert len(d["word_results"]) == 1
            assert d["word_results"][0]["word"] == "coat"
            assert "played_at" in d
            assert d["id"] is not None

    def test_to_dict_empty_word_results(self):
        """to_dict handles empty word_results gracefully."""
        init_db()
        with session_scope() as session:
            result = GameResult(
                game_type="true_false",
                score=5,
                max_score=8,
                accuracy=0.625,
                word_results="",
            )
            session.add(result)
            session.flush()
            session.refresh(result)

            d = result.to_dict()
            assert d["word_results"] == []
