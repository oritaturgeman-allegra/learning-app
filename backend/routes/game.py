"""
API routes for the English learning game.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.defaults import (
    APP_CHANGELOG,
    APP_VERSION,
    REWARD_TIERS,
    SESSIONS_BY_SUBJECT,
    TOPICS_BY_SUBJECT,
)
from backend.exceptions import GameError
from backend.services.game_service import get_game_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/game", tags=["game"])


# --- Request/Response Models ---


class WordResult(BaseModel):
    """A single word result from a game round."""

    word: str = Field(..., min_length=1)
    correct: bool
    category: str = Field(default="")


class SaveGameResultRequest(BaseModel):
    """Request body for saving a game result."""

    game_type: str = Field(..., pattern="^(word_match|sentence_scramble|listen_choose|true_false|quick_solve|missing_number|true_false_math|bubble_pop)$")
    score: int = Field(..., ge=0)
    max_score: int = Field(..., gt=0)
    word_results: List[WordResult] = Field(default_factory=list)
    session_slug: Optional[str] = None


class ProgressResponse(BaseModel):
    """Response body for progress endpoint."""

    total_stars: int
    games_played: int
    accuracy_by_game: Dict[str, Any]
    weak_words: List[Dict[str, Any]]
    recent_games: List[Dict[str, Any]]
    earned_rewards: List[str]
    next_reward: Optional[Dict[str, Any]]


# --- Endpoints ---


@router.post("/result")
async def save_game_result(request: SaveGameResultRequest) -> Dict[str, Any]:
    """
    Save a completed game result.

    Records the game type, score, and per-word accuracy for progress tracking.
    """
    try:
        game_service = get_game_service()
        result = game_service.save_game_result(
            game_type=request.game_type,
            score=request.score,
            max_score=request.max_score,
            word_results=[w.model_dump() for w in request.word_results],
            session_slug=request.session_slug,
        )
        return {
            "success": True,
            "data": result.to_dict(),
        }
    except GameError as e:
        logger.error(f"Failed to save game result: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/progress")
async def get_progress() -> Dict[str, Any]:
    """
    Get overall learning progress.

    Returns total stars, games played, accuracy per game type,
    weak words that need review, and recent game history.
    """
    try:
        game_service = get_game_service()
        progress = game_service.get_progress()
        return {
            "success": True,
            "data": progress,
        }
    except GameError as e:
        logger.error(f"Failed to get progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/practiced-words")
async def get_practiced_words(session_slug: Optional[str] = None) -> Dict[str, Any]:
    """
    Get unique vocabulary words practiced since the last reset.

    Returns a sorted list of word strings derived from game result history.
    Optionally filtered by session_slug to scope results to a specific session.
    """
    try:
        game_service = get_game_service()
        words = game_service.get_practiced_words(session_slug=session_slug)
        return {
            "success": True,
            "data": {"practiced_words": words},
        }
    except GameError as e:
        logger.error(f"Failed to get practiced words: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_practiced_words() -> Dict[str, Any]:
    """
    Reset practiced words for a fresh practice round.

    Sets a reset_at timestamp so only future games count toward
    the word tracker. Stars and game history are preserved.
    """
    try:
        game_service = get_game_service()
        reset_at = game_service.reset_practiced_words()
        return {
            "success": True,
            "data": {"reset_at": reset_at},
        }
    except GameError as e:
        logger.error(f"Failed to reset practiced words: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config(subject: Optional[str] = None, session_slug: Optional[str] = None) -> Dict[str, Any]:
    """
    Get app configuration for the React frontend.

    Returns reward tiers, sessions, version, and changelog that were
    previously injected via Jinja2 template context.
    """
    sessions = SESSIONS_BY_SUBJECT.get(subject, []) if subject else SESSIONS_BY_SUBJECT
    return {
        "success": True,
        "data": {
            "version": APP_VERSION,
            "changelog": APP_CHANGELOG,
            "reward_tiers": REWARD_TIERS,
            "sessions": sessions,
            "sessions_by_subject": SESSIONS_BY_SUBJECT,
            "topics_by_subject": TOPICS_BY_SUBJECT,
            "subject": subject,
            "session_slug": session_slug,
        },
    }
