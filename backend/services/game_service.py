"""
Game service for tracking learning progress and game results.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from backend.defaults import REWARD_TIERS
from backend.exceptions import GameError
from backend.models.app_state import AppState
from backend.models.base import init_db, session_scope
from backend.models.game_result import GameResult

logger = logging.getLogger(__name__)

# Valid game types
VALID_GAME_TYPES = {
    "word_match", "sentence_scramble", "listen_choose", "true_false",
    "quick_solve", "missing_number", "true_false_math", "bubble_pop",
}

# Stars per correct answer by game type
STARS_PER_CORRECT = {
    "word_match": 1,
    "sentence_scramble": 2,
    "listen_choose": 1,
    "true_false": 1,
    "quick_solve": 1,
    "missing_number": 1,
    "true_false_math": 1,
    "bubble_pop": 1,
}

# Category (subject) by game type
MATH_GAME_TYPES = {"quick_solve", "missing_number", "true_false_math", "bubble_pop"}

# Rounds per game type
ROUNDS_PER_GAME = {
    "word_match": 10,
    "sentence_scramble": 6,
    "listen_choose": 10,
    "true_false": 8,
    "quick_solve": 10,
    "missing_number": 8,
    "true_false_math": 10,
    "bubble_pop": 8,
}


class GameService:
    """Service for managing game results and progress tracking."""

    def __init__(self) -> None:
        try:
            init_db()
        except SQLAlchemyError as e:
            raise GameError("initialization", str(e))

    def save_game_result(
        self,
        game_type: str,
        score: int,
        max_score: int,
        word_results: List[Dict[str, Any]],
        user_id: Optional[int] = None,
        session_slug: Optional[str] = None,
    ) -> GameResult:
        """
        Save a completed game result to the database.

        Args:
            game_type: One of word_match, sentence_scramble, listen_choose, true_false
            score: Stars earned
            max_score: Maximum possible stars
            word_results: List of {word, correct, category} dicts
            user_id: Optional user ID for future multi-user support

        Returns:
            The saved GameResult

        Raises:
            GameError: If save fails
        """
        if game_type not in VALID_GAME_TYPES:
            raise GameError("save_result", f"Invalid game type: {game_type}")

        if score < 0 or score > max_score:
            raise GameError("save_result", f"Invalid score {score}/{max_score}")

        accuracy = score / max_score if max_score > 0 else 0.0
        category = "math" if game_type in MATH_GAME_TYPES else "english"

        try:
            with session_scope() as session:
                result = GameResult(
                    category=category,
                    game_type=game_type,
                    score=score,
                    max_score=max_score,
                    accuracy=accuracy,
                    word_results=json.dumps(word_results, ensure_ascii=False),
                    session_slug=session_slug,
                    user_id=user_id,
                )
                session.add(result)
                session.flush()
                session.refresh(result)
                session.expunge(result)

                logger.info(
                    f"Saved game result: {game_type} "
                    f"score={score}/{max_score} accuracy={accuracy:.0%}"
                )
                return result

        except SQLAlchemyError as e:
            raise GameError("save_result", str(e))

    def get_progress(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get overall learning progress summary.

        Args:
            user_id: Optional user ID filter

        Returns:
            Dict with total_stars, games_played, accuracy_by_game, weak_words, recent_games
        """
        try:
            with session_scope() as session:
                query = session.query(GameResult)
                if user_id is not None:
                    query = query.filter(GameResult.user_id == user_id)

                results = query.order_by(GameResult.played_at.desc()).all()

                if not results:
                    return {
                        "total_stars": 0,
                        "games_played": 0,
                        "accuracy_by_game": {},
                        "stars_by_session": {},
                        "weak_words": [],
                        "recent_games": [],
                        "earned_rewards": [],
                        "next_reward": REWARD_TIERS[0],
                    }

                # Total stars
                total_stars = sum(r.score for r in results)

                # Accuracy by game type
                accuracy_by_game: Dict[str, Dict[str, Any]] = {}
                for game_type in VALID_GAME_TYPES:
                    game_results = [r for r in results if r.game_type == game_type]
                    if game_results:
                        avg_accuracy = sum(r.accuracy for r in game_results) / len(game_results)
                        accuracy_by_game[game_type] = {
                            "games_played": len(game_results),
                            "average_accuracy": round(avg_accuracy, 2),
                            "total_stars": sum(r.score for r in game_results),
                        }

                # Weak words (words answered incorrectly most often)
                word_stats: Dict[str, Dict[str, int]] = {}
                for r in results:
                    word_list = json.loads(r.word_results) if r.word_results else []
                    for w in word_list:
                        word = w.get("word", "")
                        if not word:
                            continue
                        if word not in word_stats:
                            word_stats[word] = {"correct": 0, "total": 0}
                        word_stats[word]["total"] += 1
                        if w.get("correct"):
                            word_stats[word]["correct"] += 1

                weak_words = []
                for word, stats in word_stats.items():
                    if stats["total"] >= 2:  # Only include words seen at least twice
                        acc = stats["correct"] / stats["total"]
                        if acc < 0.7:  # Below 70% accuracy
                            weak_words.append({
                                "word": word,
                                "accuracy": round(acc, 2),
                                "attempts": stats["total"],
                            })
                weak_words.sort(key=lambda w: w["accuracy"])

                # Stars by session slug
                stars_by_session: Dict[str, int] = {}
                for r in results:
                    slug = r.session_slug or "unknown"
                    stars_by_session[slug] = stars_by_session.get(slug, 0) + r.score

                # Recent games (last 10)
                recent_games = [r.to_dict() for r in results[:10]]

                # Earned rewards based on total stars
                earned_rewards = [t["id"] for t in REWARD_TIERS if t["stars"] <= total_stars]
                unearned = [t for t in REWARD_TIERS if t["stars"] > total_stars]
                next_reward = unearned[0] if unearned else None

                return {
                    "total_stars": total_stars,
                    "games_played": len(results),
                    "accuracy_by_game": accuracy_by_game,
                    "stars_by_session": stars_by_session,
                    "weak_words": weak_words[:10],
                    "recent_games": recent_games,
                    "earned_rewards": earned_rewards,
                    "next_reward": next_reward,
                }

        except SQLAlchemyError as e:
            raise GameError("get_progress", str(e))

    def _get_reset_at(self, session: Any) -> Optional[datetime]:
        """
        Get the current reset_at timestamp from app_state.

        Args:
            session: Active SQLAlchemy session

        Returns:
            The reset_at datetime, or None if never reset
        """
        row = session.query(AppState).filter(AppState.key == "reset_at").first()
        if row:
            return datetime.fromisoformat(row.value)
        return None

    def reset_practiced_words(self) -> str:
        """
        Start a fresh practice round by setting reset_at to now.

        Words practiced before this timestamp will no longer appear
        in get_practiced_words(). Stars and game history are preserved.

        Returns:
            The reset_at ISO timestamp string

        Raises:
            GameError: If reset fails
        """
        try:
            with session_scope() as session:
                now = datetime.now(timezone.utc)
                now_iso = now.isoformat()

                row = session.query(AppState).filter(AppState.key == "reset_at").first()
                if row:
                    row.value = now_iso
                    row.updated_at = now
                else:
                    session.add(AppState(key="reset_at", value=now_iso, updated_at=now))

                logger.info(f"Practice round reset at {now_iso}")
                return now_iso

        except SQLAlchemyError as e:
            raise GameError("reset_practiced_words", str(e))

    def get_practiced_words(self, user_id: Optional[int] = None) -> List[str]:
        """
        Get unique vocabulary words practiced since the last reset.

        Extracts words from the word_results JSON column of game results
        played after the most recent reset_at timestamp.

        Args:
            user_id: Optional user ID filter

        Returns:
            Sorted list of unique practiced word strings
        """
        try:
            with session_scope() as session:
                reset_at = self._get_reset_at(session)

                query = session.query(GameResult.word_results)
                if user_id is not None:
                    query = query.filter(GameResult.user_id == user_id)
                if reset_at is not None:
                    query = query.filter(GameResult.played_at > reset_at)

                rows = query.all()

                practiced: set[str] = set()
                for (word_results_json,) in rows:
                    if not word_results_json:
                        continue
                    word_list = json.loads(word_results_json)
                    for w in word_list:
                        word = w.get("word", "").strip()
                        if word:
                            practiced.add(word.lower())

                return sorted(practiced)

        except SQLAlchemyError as e:
            raise GameError("get_practiced_words", str(e))


# Singleton instance
_game_service: Optional[GameService] = None


def get_game_service() -> GameService:
    """Get or create the singleton GameService instance."""
    global _game_service
    if _game_service is None:
        _game_service = GameService()
    return _game_service
