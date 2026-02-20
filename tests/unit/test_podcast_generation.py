"""
Unit tests for on-demand podcast generation.

Tests the POST /api/podcast/generate endpoint, PodcastGeneration model,
and DatabaseService podcast tracking methods.
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, AsyncMock

import pytest

from backend.models.base import Base, get_engine, session_scope
from backend.models.podcast_generation import PodcastGeneration
from backend.models.newsletter import Newsletter
from backend.models.article import Article
from backend.models.user import User
from backend.services.db_service import DatabaseService


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create fresh tables for each test."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield
    with session_scope() as session:
        session.query(PodcastGeneration).delete()
        session.query(Article).delete()
        session.query(Newsletter).delete()
        session.query(User).delete()


@pytest.fixture
def db_service():
    """Provide a DatabaseService instance."""
    return DatabaseService()


@pytest.fixture
def sample_newsletter(db_service):
    """Create a sample newsletter with articles in the test DB."""
    source_stats = {"us": [], "israel": [], "ai": [], "crypto": []}
    sources_metadata = {
        "us": [
            {
                "ai_title": "S&P 500 rises on strong earnings",
                "text": "Market summary",
                "source": "CNBC",
                "link": "https://cnbc.com/1",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "israel": [
            {
                "ai_title": "Tel Aviv index gains 2%",
                "text": "Israeli market summary",
                "source": "Globes",
                "link": "https://globes.co.il/1",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "ai": [
            {
                "ai_title": "OpenAI launches new model",
                "text": "AI news",
                "source": "TechCrunch",
                "link": "https://techcrunch.com/1",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "crypto": [
            {
                "ai_title": "Bitcoin hits new high",
                "text": "Crypto news",
                "source": "CoinDesk",
                "link": "https://coindesk.com/1",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }
    db_service.save_newsletter_with_stats(
        source_stats=source_stats,
        sources_metadata=sources_metadata,
        language="en",
        llm_provider="openai",
    )
    return sources_metadata


class TestPodcastGenerationModel:
    """Tests for PodcastGeneration model."""

    def test_creation(self):
        """Test creating a PodcastGeneration record."""
        with session_scope() as session:
            record = PodcastGeneration(
                user_id=1,
                categories='["us","ai"]',
                cache_key="abc123def456",
            )
            session.add(record)
            session.commit()
            assert record.id is not None
            assert record.user_id == 1
            assert record.created_at is not None

    def test_repr(self):
        """Test string representation."""
        record = PodcastGeneration(
            id=1,
            user_id=42,
            categories='["us"]',
            cache_key="test_key",
        )
        repr_str = repr(record)
        assert "PodcastGeneration" in repr_str
        assert "user_id=42" in repr_str


class TestDatabaseServicePodcastTracking:
    """Tests for DatabaseService podcast generation tracking."""

    def test_get_user_podcast_generation_count_no_records(self, db_service):
        """Test count returns 0 when no generations exist."""
        now = datetime.now(timezone.utc)
        count = db_service.get_user_podcast_generation_count(user_id=1, date=now)
        assert count == 0

    def test_get_user_podcast_generation_count_with_records(self, db_service):
        """Test count returns correct number of generations today."""
        db_service.record_podcast_generation(user_id=1, categories=["us", "ai"], cache_key="key1")
        db_service.record_podcast_generation(user_id=1, categories=["crypto"], cache_key="key2")

        now = datetime.now(timezone.utc)
        count = db_service.get_user_podcast_generation_count(user_id=1, date=now)
        assert count == 2

    def test_get_user_podcast_generation_count_different_users(self, db_service):
        """Test count is per-user."""
        db_service.record_podcast_generation(user_id=1, categories=["us"], cache_key="key1")
        db_service.record_podcast_generation(user_id=2, categories=["us"], cache_key="key2")

        now = datetime.now(timezone.utc)
        assert db_service.get_user_podcast_generation_count(user_id=1, date=now) == 1
        assert db_service.get_user_podcast_generation_count(user_id=2, date=now) == 1

    def test_get_user_podcast_generation_count_different_days(self, db_service):
        """Test count only considers the specified day."""
        db_service.record_podcast_generation(user_id=1, categories=["us"], cache_key="key1")

        # Check for tomorrow — should be 0
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        count = db_service.get_user_podcast_generation_count(user_id=1, date=tomorrow)
        assert count == 0

    def test_record_podcast_generation(self, db_service):
        """Test recording a podcast generation."""
        record = db_service.record_podcast_generation(
            user_id=42, categories=["us", "israel"], cache_key="test_cache_key"
        )
        assert record.id is not None
        assert record.user_id == 42
        assert json.loads(record.categories) == ["israel", "us"]  # sorted
        assert record.cache_key == "test_cache_key"


class TestPodcastGenerateEndpoint:
    """Tests for POST /api/podcast/generate endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from fastapi.testclient import TestClient
        from backend.web_app import app

        return TestClient(app)

    def test_invalid_categories(self, client):
        """Test with no valid categories."""
        response = client.post(
            "/api/podcast/generate",
            json={"categories": ["invalid", "bad"], "user_id": 1},
        )
        assert response.status_code == 400
        assert "No valid categories" in response.json()["detail"]

    def test_no_newsletter_data(self, client):
        """Test when no newsletter exists in DB."""
        response = client.post(
            "/api/podcast/generate",
            json={"categories": ["us", "ai"], "user_id": 1},
        )
        assert response.status_code == 404

    def test_cache_hit(self, client, sample_newsletter):
        """Test that a cached podcast is returned without consuming daily limit."""
        import tempfile

        cache_key = "test_cache_key_123"
        audio_file = Path(tempfile.mkdtemp()) / f"{cache_key}.mp3"
        audio_file.write_bytes(b"fake mp3 data")
        cache_dir = audio_file.parent

        # Write metadata file
        metadata_path = cache_dir / f"{cache_key}.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "created_at": "2026-02-03T10:00:00",
                    "file_size_bytes": 1024,
                    "dialogue_lines": 10,
                }
            )
        )

        from backend.routes.api import tts_service as real_tts

        original_cache_dir = real_tts.cache_dir
        original_get_cached = real_tts._get_cached_audio

        try:
            real_tts.cache_dir = cache_dir
            real_tts._get_cached_audio = lambda key: audio_file

            response = client.post(
                "/api/podcast/generate",
                json={"categories": ["us"], "user_id": 1},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["cached"] is True
            assert "audio_url" in data
        finally:
            real_tts.cache_dir = original_cache_dir
            real_tts._get_cached_audio = original_get_cached
            audio_file.unlink(missing_ok=True)
            metadata_path.unlink(missing_ok=True)
            cache_dir.rmdir()

    def test_daily_limit_reached(self, client, db_service, sample_newsletter):
        """Test that 429 is returned when daily limit is reached."""
        # Record generations for today (PODCAST_DAILY_LIMIT = 2)
        db_service.record_podcast_generation(user_id=1, categories=["us"], cache_key="key1")
        db_service.record_podcast_generation(user_id=1, categories=["israel"], cache_key="key2")

        with patch("backend.routes.api.tts_service") as mock_tts:
            mock_tts._get_cached_audio.return_value = None  # No cache hit
            # Defensive: use AsyncMock in case limit check fails unexpectedly
            mock_tts.generate_podcast_async = AsyncMock(return_value=Path("/tmp/fake.mp3"))

            response = client.post(
                "/api/podcast/generate",
                json={"categories": ["ai", "crypto"], "user_id": 1},
            )
            assert response.status_code == 429
            assert "podcast" in response.json()["detail"].lower()

    def test_missing_user_id(self, client):
        """Test request without user_id fails validation."""
        response = client.post(
            "/api/podcast/generate",
            json={"categories": ["us"]},
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_empty_categories(self, client):
        """Test request with empty categories list fails validation."""
        response = client.post(
            "/api/podcast/generate",
            json={"categories": [], "user_id": 1},
        )
        assert response.status_code == 422
