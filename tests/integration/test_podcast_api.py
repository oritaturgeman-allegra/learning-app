"""
Integration tests for podcast API endpoints.
"""

import json
import tempfile
import shutil
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.web_app import app
from backend.routes.api import tts_service


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def temp_cache():
    """Setup temporary cache directory for testing."""
    temp_dir = tempfile.mkdtemp()
    original_cache_dir = tts_service.cache_dir
    tts_service.cache_dir = Path(temp_dir)
    tts_service.cache_dir.mkdir(exist_ok=True)

    yield temp_dir

    # Cleanup
    tts_service.cache_dir = original_cache_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestLatestPodcastEndpoint:
    """Test the /api/podcast/latest endpoint (deprecated)."""

    def test_podcast_latest_returns_410_deprecated(self, client):
        """Test that /api/podcast/latest returns 410 Gone with deprecation message."""
        response = client.get("/api/podcast/latest")

        assert response.status_code == 410
        data = response.json()
        assert "detail" in data
        assert "deprecated" in data["detail"].lower()
        assert "POST /api/podcast/generate" in data["detail"]


class TestServeAudioEndpoint:
    """Test the /api/audio/<filename> endpoint."""

    def test_serve_audio_success(self, client, temp_cache):
        """Test serving an existing audio file."""
        # Create a test audio file
        test_filename = "test_audio_123.mp3"
        audio_path = tts_service.cache_dir / test_filename
        metadata_path = tts_service.cache_dir / "test_audio_123.json"

        # Write fake audio file
        with open(audio_path, "wb") as f:
            f.write(b"fake audio content")

        # Write metadata
        from datetime import datetime

        metadata = {"created_at": datetime.now().isoformat(), "model": "tts-1-hd", "voice": "fable"}
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

        # Request the audio file
        response = client.get(f"/api/audio/{test_filename}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.content == b"fake audio content"

    def test_serve_audio_not_found(self, client):
        """Test serving a non-existent audio file."""
        response = client.get("/api/audio/nonexistent_file.mp3")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Audio file not found" in data["detail"]

    def test_serve_audio_expired(self, client, temp_cache):
        """Test that expired audio files return 410 Gone."""
        from datetime import datetime, timedelta

        # Create an expired audio file
        test_filename = "expired_audio.mp3"
        audio_path = tts_service.cache_dir / test_filename
        metadata_path = tts_service.cache_dir / "expired_audio.json"

        with open(audio_path, "wb") as f:
            f.write(b"old audio")

        # Create metadata with old timestamp
        old_time = datetime.now() - timedelta(days=2)
        metadata = {"created_at": old_time.isoformat(), "model": "tts-1-hd", "voice": "fable"}
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

        # Request the expired file
        response = client.get(f"/api/audio/{test_filename}")

        assert response.status_code == 410  # Gone
        data = response.json()
        assert "detail" in data
        assert "Audio file expired" in data["detail"]


class TestCacheStatsEndpoint:
    """Test the /api/cache-stats endpoint."""

    def test_cache_stats_empty(self, client, temp_cache):
        """Test cache stats when cache is empty."""
        response = client.get("/api/cache-stats")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "stats" in data
        assert data["stats"]["total_files"] == 0
        assert data["stats"]["total_size_mb"] == 0.0

    def test_cache_stats_with_files(self, client, temp_cache):
        """Test cache stats with cached files."""
        # Create some test cache files
        for i in range(3):
            audio_path = tts_service.cache_dir / f"test_{i}.mp3"
            with open(audio_path, "wb") as f:
                f.write(b"x" * 1000)  # 1KB each

        response = client.get("/api/cache-stats")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["stats"]["total_files"] == 3
        assert data["stats"]["total_size_mb"] >= 0  # Small files may round down to 0.0
        assert data["stats"]["total_size_mb"] < 1  # 3KB should be less than 1MB
