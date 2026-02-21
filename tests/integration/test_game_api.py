"""
Integration tests for the game API endpoints.

Tests the full request/response cycle through FastAPI's TestClient.
"""

import time

import pytest
from fastapi.testclient import TestClient

from backend.models.app_state import AppState
from backend.models.base import init_db, session_scope
from backend.models.game_result import GameResult
from backend.web_app import app


@pytest.fixture(autouse=True)
def clean_db():
    """Ensure a clean database for each test."""
    init_db()
    with session_scope() as session:
        session.query(GameResult).delete()
        session.query(AppState).delete()
    yield


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_ok(self, client):
        """Health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data


class TestSaveGameResultAPI:
    """Tests for POST /api/game/result."""

    def test_save_valid_result(self, client):
        """Save a valid game result via API."""
        response = client.post("/api/game/result", json={
            "game_type": "word_match",
            "score": 8,
            "max_score": 10,
            "word_results": [
                {"word": "coat", "correct": True, "category": "clothes"},
                {"word": "boots", "correct": False, "category": "clothes"},
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["game_type"] == "word_match"
        assert data["data"]["score"] == 8

    def test_save_all_game_types(self, client):
        """All four game types are accepted."""
        for game_type in ["word_match", "sentence_scramble", "listen_choose", "true_false"]:
            response = client.post("/api/game/result", json={
                "game_type": game_type,
                "score": 5,
                "max_score": 10,
                "word_results": [],
            })
            assert response.status_code == 200

    def test_invalid_game_type_rejected(self, client):
        """Invalid game type returns 422 (Pydantic validation)."""
        response = client.post("/api/game/result", json={
            "game_type": "invalid_game",
            "score": 5,
            "max_score": 10,
            "word_results": [],
        })
        assert response.status_code == 422

    def test_negative_score_rejected(self, client):
        """Negative score returns 422."""
        response = client.post("/api/game/result", json={
            "game_type": "word_match",
            "score": -1,
            "max_score": 10,
            "word_results": [],
        })
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Missing required fields returns 422."""
        response = client.post("/api/game/result", json={
            "game_type": "word_match",
        })
        assert response.status_code == 422


class TestProgressAPI:
    """Tests for GET /api/game/progress."""

    def test_empty_progress(self, client):
        """No games played returns zero progress."""
        response = client.get("/api/game/progress")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_stars"] == 0
        assert data["data"]["games_played"] == 0

    def test_progress_after_game(self, client):
        """Progress reflects saved game results."""
        client.post("/api/game/result", json={
            "game_type": "word_match",
            "score": 8,
            "max_score": 10,
            "word_results": [
                {"word": "coat", "correct": True, "category": "clothes"},
            ],
        })

        response = client.get("/api/game/progress")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_stars"] == 8
        assert data["games_played"] == 1
        assert "word_match" in data["accuracy_by_game"]


class TestPracticedWordsAPI:
    """Tests for GET /api/game/practiced-words."""

    def test_empty_practiced_words(self, client):
        """No games returns empty practiced words list."""
        response = client.get("/api/game/practiced-words")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["practiced_words"] == []

    def test_practiced_words_after_games(self, client):
        """Practiced words accumulate from game results."""
        client.post("/api/game/result", json={
            "game_type": "word_match",
            "score": 8,
            "max_score": 10,
            "word_results": [
                {"word": "coat", "correct": True, "category": "clothes"},
                {"word": "boots", "correct": False, "category": "clothes"},
            ],
        })
        client.post("/api/game/result", json={
            "game_type": "listen_choose",
            "score": 7,
            "max_score": 10,
            "word_results": [
                {"word": "dress", "correct": True, "category": "clothes"},
            ],
        })

        response = client.get("/api/game/practiced-words")
        words = response.json()["data"]["practiced_words"]
        assert "boots" in words
        assert "coat" in words
        assert "dress" in words
        assert len(words) == 3

    def test_practiced_words_are_sorted(self, client):
        """Practiced words are returned in alphabetical order."""
        client.post("/api/game/result", json={
            "game_type": "word_match",
            "score": 5,
            "max_score": 10,
            "word_results": [
                {"word": "summer", "correct": True, "category": "seasons"},
                {"word": "coat", "correct": True, "category": "clothes"},
                {"word": "autumn", "correct": True, "category": "seasons"},
            ],
        })

        response = client.get("/api/game/practiced-words")
        words = response.json()["data"]["practiced_words"]
        assert words == ["autumn", "coat", "summer"]


class TestErrorHandling:
    """Tests for API error responses."""

    def test_save_result_score_exceeds_max(self, client):
        """Score > max_score returns 400 from service validation."""
        response = client.post("/api/game/result", json={
            "game_type": "word_match",
            "score": 15,
            "max_score": 10,
            "word_results": [],
        })
        assert response.status_code == 400
        assert "Invalid score" in response.json()["detail"]

    def test_save_result_empty_body(self, client):
        """Empty request body returns 422."""
        response = client.post("/api/game/result", json={})
        assert response.status_code == 422

    def test_save_result_wrong_content_type(self, client):
        """Non-JSON content type returns 422."""
        response = client.post("/api/game/result", content="not json")
        assert response.status_code == 422


class TestFullGameFlow:
    """End-to-end test: play a game, check progress, check practiced words."""

    def test_complete_game_flow(self, client):
        """Play a game → save result → check progress → check practiced words."""
        # 1. Save a game result
        save_response = client.post("/api/game/result", json={
            "game_type": "word_match",
            "score": 9,
            "max_score": 10,
            "word_results": [
                {"word": "coat", "correct": True, "category": "clothes"},
                {"word": "boots", "correct": True, "category": "clothes"},
                {"word": "dress", "correct": True, "category": "clothes"},
                {"word": "shirt", "correct": True, "category": "clothes"},
                {"word": "pants", "correct": True, "category": "clothes"},
                {"word": "shoes", "correct": True, "category": "clothes"},
                {"word": "socks", "correct": True, "category": "clothes"},
                {"word": "winter", "correct": True, "category": "seasons"},
                {"word": "spring", "correct": True, "category": "seasons"},
                {"word": "summer", "correct": False, "category": "seasons"},
            ],
        })
        assert save_response.status_code == 200

        # 2. Check progress
        progress = client.get("/api/game/progress").json()["data"]
        assert progress["total_stars"] == 9
        assert progress["games_played"] == 1
        assert progress["accuracy_by_game"]["word_match"]["average_accuracy"] == 0.9

        # 3. Check practiced words
        words = client.get("/api/game/practiced-words").json()["data"]["practiced_words"]
        assert len(words) == 10
        assert words[0] == "boots"  # alphabetically first
        assert words[-1] == "winter"  # alphabetically last


class TestResetAPI:
    """Tests for POST /api/game/reset."""

    def test_reset_returns_success(self, client):
        """Reset endpoint returns success with reset_at timestamp."""
        response = client.post("/api/game/reset")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reset_at" in data["data"]

    def test_full_reset_flow(self, client):
        """Play → reset → practiced words empty → play again → new words appear."""
        # 1. Play a game
        client.post("/api/game/result", json={
            "game_type": "word_match",
            "score": 8,
            "max_score": 10,
            "word_results": [
                {"word": "coat", "correct": True, "category": "clothes"},
                {"word": "boots", "correct": True, "category": "clothes"},
            ],
        })
        words = client.get("/api/game/practiced-words").json()["data"]["practiced_words"]
        assert len(words) == 2

        # 2. Reset
        reset_response = client.post("/api/game/reset")
        assert reset_response.status_code == 200

        # 3. Practiced words should be empty
        words = client.get("/api/game/practiced-words").json()["data"]["practiced_words"]
        assert words == []

        # 4. Stars should be preserved
        progress = client.get("/api/game/progress").json()["data"]
        assert progress["total_stars"] == 8

        # 5. Play again — new words appear
        time.sleep(0.05)
        client.post("/api/game/result", json={
            "game_type": "listen_choose",
            "score": 7,
            "max_score": 10,
            "word_results": [
                {"word": "dress", "correct": True, "category": "clothes"},
            ],
        })
        words = client.get("/api/game/practiced-words").json()["data"]["practiced_words"]
        assert words == ["dress"]
        assert "coat" not in words
