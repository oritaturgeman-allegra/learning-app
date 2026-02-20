"""
Tests for the game service — save results and progress tracking.
"""

import pytest

from backend.exceptions import GameError
from backend.models.base import init_db, session_scope
from backend.models.game_result import GameResult
from backend.services.game_service import GameService


@pytest.fixture
def game_service():
    """Create a fresh GameService with clean game_results table."""
    init_db()
    # Clean up any leftover data from previous tests
    with session_scope() as session:
        session.query(GameResult).delete()
    return GameService()


class TestSaveGameResult:
    """Tests for GameService.save_game_result()."""

    def test_save_valid_result(self, game_service):
        """Save a valid game result and verify it's stored."""
        result = game_service.save_game_result(
            game_type="word_match",
            score=7,
            max_score=10,
            word_results=[
                {"word": "coat", "correct": True, "category": "clothes"},
                {"word": "boots", "correct": False, "category": "clothes"},
            ],
        )
        assert result.game_type == "word_match"
        assert result.score == 7
        assert result.max_score == 10
        assert result.accuracy == 0.7

    def test_save_perfect_score(self, game_service):
        """Save a game with perfect score."""
        result = game_service.save_game_result(
            game_type="true_false",
            score=8,
            max_score=8,
            word_results=[],
        )
        assert result.accuracy == 1.0

    def test_save_zero_score(self, game_service):
        """Save a game with zero score."""
        result = game_service.save_game_result(
            game_type="listen_choose",
            score=0,
            max_score=10,
            word_results=[],
        )
        assert result.accuracy == 0.0

    def test_save_invalid_game_type_raises(self, game_service):
        """Invalid game type should raise GameError."""
        with pytest.raises(GameError, match="Invalid game type"):
            game_service.save_game_result(
                game_type="invalid_game",
                score=5,
                max_score=10,
                word_results=[],
            )

    def test_save_negative_score_raises(self, game_service):
        """Negative score should raise GameError."""
        with pytest.raises(GameError, match="Invalid score"):
            game_service.save_game_result(
                game_type="word_match",
                score=-1,
                max_score=10,
                word_results=[],
            )

    def test_save_score_exceeds_max_raises(self, game_service):
        """Score exceeding max should raise GameError."""
        with pytest.raises(GameError, match="Invalid score"):
            game_service.save_game_result(
                game_type="word_match",
                score=15,
                max_score=10,
                word_results=[],
            )

    def test_save_sentence_scramble_result(self, game_service):
        """Save a sentence scramble result with higher star value."""
        result = game_service.save_game_result(
            game_type="sentence_scramble",
            score=10,
            max_score=12,
            word_results=[
                {"word": "She is wearing a blue dress", "correct": True, "category": "sentence"},
            ],
        )
        assert result.game_type == "sentence_scramble"
        assert result.score == 10


class TestGetProgress:
    """Tests for GameService.get_progress()."""

    def test_empty_progress(self, game_service):
        """No games played returns empty progress."""
        progress = game_service.get_progress()
        assert progress["total_stars"] == 0
        assert progress["games_played"] == 0
        assert progress["accuracy_by_game"] == {}
        assert progress["weak_words"] == []
        assert progress["recent_games"] == []

    def test_progress_after_games(self, game_service):
        """Progress accumulates across multiple games."""
        game_service.save_game_result(
            game_type="word_match",
            score=8,
            max_score=10,
            word_results=[
                {"word": "coat", "correct": True, "category": "clothes"},
                {"word": "boots", "correct": True, "category": "clothes"},
            ],
        )
        game_service.save_game_result(
            game_type="true_false",
            score=6,
            max_score=8,
            word_results=[
                {"word": "A coat is warm", "correct": True, "category": "true_false"},
            ],
        )

        progress = game_service.get_progress()
        assert progress["total_stars"] == 14
        assert progress["games_played"] == 2
        assert "word_match" in progress["accuracy_by_game"]
        assert "true_false" in progress["accuracy_by_game"]
        assert len(progress["recent_games"]) == 2

    def test_weak_words_detection(self, game_service):
        """Words with low accuracy are flagged as weak."""
        # Play twice with "boots" wrong both times
        for _ in range(2):
            game_service.save_game_result(
                game_type="word_match",
                score=5,
                max_score=10,
                word_results=[
                    {"word": "coat", "correct": True, "category": "clothes"},
                    {"word": "boots", "correct": False, "category": "clothes"},
                ],
            )

        progress = game_service.get_progress()
        weak = progress["weak_words"]
        weak_word_names = [w["word"] for w in weak]
        assert "boots" in weak_word_names

    def test_recent_games_limited_to_10(self, game_service):
        """Recent games should be limited to the 10 most recent."""
        for i in range(15):
            game_service.save_game_result(
                game_type="word_match",
                score=i % 10,
                max_score=10,
                word_results=[],
            )

        progress = game_service.get_progress()
        assert len(progress["recent_games"]) == 10
