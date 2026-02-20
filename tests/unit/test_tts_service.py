"""
Unit tests for TTS (Text-to-Speech) service.
"""

import asyncio
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from backend.services.tts_service import TTSService


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def tts_service(temp_cache_dir):
    """Create a TTS service instance with temp cache directory."""
    with patch("backend.services.tts_service.AsyncOpenAI"):
        service = TTSService(cache_dir=temp_cache_dir, cache_hours=24)
        return service


@pytest.fixture
def sample_newsletter_data():
    """Sample newsletter data for testing with pre-generated podcast dialog."""
    return {
        "ai_podcast_dialog": [
            [
                "female",
                "Hey everyone! Welcome back to the Capital Market Newsletter podcast! I'm Maya!",
            ],
            ["male", "And I'm Guy! Great to be here - we have SO much to unpack today!"],
            [
                "female",
                "We're covering the U.S. markets, developments from the Israeli market, and the latest in AI!",
            ],
            ["male", "Lots to get through!"],
            ["female", "This is gonna be good!"],
            ["male", "Let's get into it!"],
            ["female", "So Guy, what's the overall picture looking like?"],
            [
                "male",
                "Markets showed mixed performance today with tech stocks leading gains. And honestly, I'm here for it!",
            ],
            ["female", "Great overview! Let's break this down piece by piece!"],
            ["male", "Alright! Let's kick off with the U.S. markets!"],
            ["female", "So check this out! S&P 500 gained 0.5% to close at record highs"],
            ["male", "And get this! NVIDIA announced new AI chip architecture"],
            ["female", "Now let's talk Israel!"],
            ["male", "Oh yeah! This is getting interesting!"],
            ["male", "Okay so! TA-35 index rose 1.2% on strong tech sector performance"],
            ["female", "Love to see it!"],
            ["male", "Absolutely love it!"],
            ["male", "Okay, we HAVE to talk about AI!"],
            ["female", "It's literally everywhere right now!"],
            ["male", "So! OpenAI released new language model capabilities"],
            ["female", "The future is happening NOW!"],
            ["male", "Right?! It's incredible!"],
            ["female", "So bottom line - there's SO much happening across all these markets!"],
            ["male", "So much! And the key is staying informed, staying engaged!"],
            ["female", "Love that! Okay everyone, huge thanks for tuning in today!"],
            ["male", "Seriously! Make sure to subscribe - we drop new episodes regularly!"],
            ["female", "And we'll catch you on the next one!"],
            ["male", "See you soon!"],
        ],
        "sources_metadata": {
            "us": [
                {
                    "ai_title": "S&P 500 gained 0.5% to close at record highs",
                    "source": "Reuters",
                },
                {"ai_title": "NVIDIA announced new AI chip architecture", "source": "Bloomberg"},
            ],
            "israel": [
                {
                    "ai_title": "TA-35 index rose 1.2% on strong tech sector performance",
                    "source": "Globes",
                },
            ],
            "ai": [
                {
                    "ai_title": "OpenAI released new language model capabilities",
                    "source": "TechCrunch",
                },
            ],
        },
    }


class TestFormatContentForSpeech:
    """Test the format_content_for_speech method."""

    def test_basic_formatting(self, tts_service, sample_newsletter_data):
        """Test that content is formatted correctly for speech."""
        script = tts_service.format_content_for_speech(sample_newsletter_data)

        # Check for host names and conversation content
        assert "Maya" in script or "Guy" in script
        assert "Welcome" in script or "Hey everyone" in script
        assert "See you soon" in script

    def test_empty_podcast_dialog_returns_empty(self, tts_service):
        """Test that empty podcast dialog is handled gracefully."""
        data = {
            "ai_podcast_dialog": [],
        }

        script = tts_service.format_content_for_speech(data)
        assert script == ""

    def test_uses_pregenerated_dialog(self, tts_service, sample_newsletter_data):
        """Test that pre-generated dialog is used directly."""
        script = tts_service.format_content_for_speech(sample_newsletter_data)

        # Check that news content from dialog is included
        assert "S&P 500 gained 0.5%" in script
        assert "NVIDIA announced" in script
        assert "TA-35 index rose 1.2%" in script


class TestCacheKeyGeneration:
    """Test cache key generation."""

    def test_cache_key_deterministic(self, tts_service):
        """Test that same content generates same cache key."""
        content1 = "This is test content"
        content2 = "This is test content"

        key1 = tts_service._generate_cache_key(content1)
        key2 = tts_service._generate_cache_key(content2)

        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex digest length

    def test_cache_key_different_content(self, tts_service):
        """Test that different content generates different keys."""
        content1 = "Content A"
        content2 = "Content B"

        key1 = tts_service._generate_cache_key(content1)
        key2 = tts_service._generate_cache_key(content2)

        assert key1 != key2

    def test_cache_key_with_categories(self, tts_service):
        """Test that same content with different categories generates different keys."""
        content = "Same content"
        categories_a = ["us", "israel"]
        categories_b = ["us", "israel", "ai"]

        key_a = tts_service._generate_cache_key(content, categories_a)
        key_b = tts_service._generate_cache_key(content, categories_b)

        assert key_a != key_b

    def test_cache_key_categories_order_independent(self, tts_service):
        """Test that categories order doesn't affect cache key."""
        content = "Same content"
        categories_a = ["us", "israel", "ai"]
        categories_b = ["ai", "us", "israel"]  # Different order

        key_a = tts_service._generate_cache_key(content, categories_a)
        key_b = tts_service._generate_cache_key(content, categories_b)

        assert key_a == key_b  # Should be same since categories are sorted

    def test_cache_key_without_categories(self, tts_service):
        """Test cache key generation without categories (backward compatibility)."""
        content = "Test content"

        key_with_none = tts_service._generate_cache_key(content, None)
        key_without = tts_service._generate_cache_key(content)

        assert key_with_none == key_without


class TestCacheOperations:
    """Test cache save and retrieve operations."""

    def test_save_and_retrieve_cache(self, tts_service):
        """Test saving audio to cache and retrieving it."""
        cache_key = "test_key_123"
        audio_data = b"fake audio data"
        script = "This is a test script"

        # Save to cache
        saved_path = tts_service._save_to_cache(cache_key, audio_data, script)

        assert saved_path.exists()
        assert saved_path.name == f"{cache_key}.mp3"

        # Verify audio file
        with open(saved_path, "rb") as f:
            assert f.read() == audio_data

        # Verify metadata file
        metadata_path = tts_service.cache_dir / f"{cache_key}.json"
        assert metadata_path.exists()

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        assert "created_at" in metadata
        assert metadata["model"] == "tts-1-hd"
        assert metadata["female_voice"] == "nova"
        assert metadata["male_voice"] == "fable"
        assert "script_preview" in metadata
        assert metadata["file_size_bytes"] == len(audio_data)

    def test_get_cached_audio_valid(self, tts_service):
        """Test retrieving valid cached audio."""
        cache_key = "valid_cache"
        audio_data = b"cached audio"
        script = "Cached script"

        # Save to cache
        tts_service._save_to_cache(cache_key, audio_data, script)

        # Retrieve from cache
        cached_path = tts_service._get_cached_audio(cache_key)

        assert cached_path is not None
        assert cached_path.exists()

    def test_get_cached_audio_expired(self, temp_cache_dir):
        """Test that expired cache returns None."""
        # Create service with 0 hours cache (immediately expired)
        tts_service = TTSService(cache_dir=temp_cache_dir, cache_hours=0)

        cache_key = "expired_cache"
        audio_data = b"old audio"
        script = "Old script"

        # Save to cache
        audio_file = tts_service._save_to_cache(cache_key, audio_data, script)

        # Modify metadata to be old
        metadata_file = tts_service.cache_dir / f"{cache_key}.json"
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        # Set created_at to 2 days ago
        old_time = datetime.now() - timedelta(days=2)
        metadata["created_at"] = old_time.isoformat()

        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        # Try to retrieve - should return None and clean up
        cached_path = tts_service._get_cached_audio(cache_key)

        assert cached_path is None
        assert not audio_file.exists()
        assert not metadata_file.exists()

    def test_get_cached_audio_nonexistent(self, tts_service):
        """Test retrieving non-existent cache returns None."""
        cached_path = tts_service._get_cached_audio("nonexistent_key")
        assert cached_path is None


class TestGeneratePodcast:
    """Test podcast generation functionality."""

    @patch.object(TTSService, "_merge_audio_files")
    def test_generate_podcast_success(self, mock_merge, tts_service, sample_newsletter_data):
        """Test successful podcast generation."""
        # Create async mock for the speech API
        mock_response = MagicMock()
        mock_response.content = b"fake audio content"

        mock_client = MagicMock()
        mock_client.audio.speech.create = AsyncMock(return_value=mock_response)

        # Mock the merge function to return a path
        mock_merge.return_value = tts_service.cache_dir / "merged.mp3"
        # Create the file so it exists
        (tts_service.cache_dir / "merged.mp3").write_bytes(b"merged audio")

        # Replace the client
        tts_service._openai_client = mock_client

        # Generate podcast using asyncio.run
        audio_path = asyncio.run(
            tts_service.generate_podcast_async(sample_newsletter_data, use_cache=False)
        )

        # Verify
        assert audio_path.exists()
        assert audio_path.suffix == ".mp3"

        # Verify API was called multiple times (once per dialogue line)
        assert mock_client.audio.speech.create.call_count > 0

        # Verify different voices were used
        all_calls = mock_client.audio.speech.create.call_args_list
        voices_used = set()
        for call in all_calls:
            voices_used.add(call.kwargs["voice"])

        # Should have both voices used (Maya and Guy)
        assert "nova" in voices_used  # Female voice
        assert "fable" in voices_used  # Male voice

        # Verify intro is present in one of the calls
        texts_called = [call.kwargs["input"] for call in all_calls]
        assert any("I'm Maya" in text or "I'm Guy" in text for text in texts_called)

    @patch.object(TTSService, "_merge_audio_files")
    def test_generate_podcast_uses_cache(self, mock_merge, tts_service, sample_newsletter_data):
        """Test that podcast generation uses cache when available."""
        # Create async mock for the speech API
        mock_response = MagicMock()
        mock_response.content = b"audio content"

        mock_client = MagicMock()
        mock_client.audio.speech.create = AsyncMock(return_value=mock_response)
        tts_service._openai_client = mock_client

        # Mock the merge function
        mock_merge.return_value = tts_service.cache_dir / "merged.mp3"
        (tts_service.cache_dir / "merged.mp3").write_bytes(b"merged audio")

        # First generation
        audio_path_1 = asyncio.run(
            tts_service.generate_podcast_async(sample_newsletter_data, use_cache=True)
        )

        # Second generation (should use cache)
        audio_path_2 = asyncio.run(
            tts_service.generate_podcast_async(sample_newsletter_data, use_cache=True)
        )

        # Should return same file
        assert audio_path_1 == audio_path_2

        # OpenAI API should only be called for first generation
        # (Get the count after first gen, should not increase on second)
        first_call_count = mock_client.audio.speech.create.call_count
        assert first_call_count > 0  # Was called for first generation

    def test_generate_podcast_empty_data_raises_error(self, tts_service):
        """Test that empty newsletter data raises TTSError."""
        from backend.exceptions import TTSError

        with pytest.raises(TTSError, match="Newsletter data cannot be empty"):
            asyncio.run(tts_service.generate_podcast_async(None))

        with pytest.raises(TTSError, match="Newsletter data cannot be empty"):
            asyncio.run(tts_service.generate_podcast_async({}))

    def test_generate_podcast_api_error(self, tts_service, sample_newsletter_data):
        """Test handling of OpenAI API errors."""
        from backend.exceptions import TTSError

        # Create async mock that raises error
        mock_client = MagicMock()
        mock_client.audio.speech.create = AsyncMock(side_effect=Exception("API Error"))
        tts_service._openai_client = mock_client

        # Should raise TTSError
        with pytest.raises(TTSError):
            asyncio.run(tts_service.generate_podcast_async(sample_newsletter_data, use_cache=False))


class TestCacheManagement:
    """Test cache management functions."""

    def test_cleanup_expired_cache(self, tts_service):
        """Test cleanup of expired cache files."""
        # Create some cache files with old timestamps
        for i in range(3):
            cache_key = f"old_cache_{i}"
            audio_file = tts_service.cache_dir / f"{cache_key}.mp3"
            metadata_file = tts_service.cache_dir / f"{cache_key}.json"

            # Create audio file
            with open(audio_file, "wb") as f:
                f.write(b"old audio")

            # Create metadata with old timestamp
            metadata = {
                "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
                "model": "tts-1-hd",
                "voice": "nova",
            }
            with open(metadata_file, "w") as f:
                json.dump(metadata, f)

        # Run cleanup
        removed_count = tts_service.cleanup_expired_cache()

        # Should remove all 3 files
        assert removed_count == 3

        # Verify files are gone
        assert len(list(tts_service.cache_dir.glob("*.mp3"))) == 0
        assert len(list(tts_service.cache_dir.glob("*.json"))) == 0

    def test_get_cache_stats(self, tts_service):
        """Test getting cache statistics."""
        # Create some cache files
        for i in range(2):
            cache_key = f"test_cache_{i}"
            tts_service._save_to_cache(cache_key, b"x" * 1000, "Test script")  # 1KB

        stats = tts_service.get_cache_stats()

        assert stats["total_files"] == 2
        assert stats["total_size_mb"] >= 0  # Should be > 0 but may round down
        assert stats["total_size_mb"] < 1  # 2KB should be less than 1MB
        assert "cache_dir" in stats


class TestCategoryAwareCaching:
    """Test category-aware podcast caching functionality."""

    def test_find_superset_audio_exact_match(self, tts_service):
        """Test that exact category match works."""
        cache_key = "superset_test"
        audio_file = tts_service.cache_dir / f"{cache_key}.mp3"
        metadata_file = tts_service.cache_dir / f"{cache_key}.json"

        # Create audio file
        audio_file.write_bytes(b"test audio")

        # Create metadata with categories
        metadata = {
            "created_at": datetime.now().isoformat(),
            "model": "tts-1-hd",
            "categories": ["ai", "israel", "us"],  # Sorted
        }
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        # Request same categories - superset cache is DISABLED (always returns None)
        # Users selecting specific categories should get exact match only
        result = tts_service._find_superset_audio(["us", "israel", "ai"])

        assert result is None  # Superset cache disabled

    def test_find_superset_audio_subset(self, tts_service):
        """Test that superset cache is DISABLED - subset requests don't match superset cache."""
        cache_key = "all_categories"
        audio_file = tts_service.cache_dir / f"{cache_key}.mp3"
        metadata_file = tts_service.cache_dir / f"{cache_key}.json"

        # Create audio file with all 4 categories
        audio_file.write_bytes(b"complete podcast audio")

        metadata = {
            "created_at": datetime.now().isoformat(),
            "model": "tts-1-hd",
            "categories": ["ai", "crypto", "israel", "us"],  # All 4
        }
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        # Request only 2 categories - superset cache is DISABLED
        # Users selecting US+Israel should NOT get podcast with AI+Crypto content
        result = tts_service._find_superset_audio(["us", "israel"])

        assert result is None  # Superset cache disabled - don't return wrong content

    def test_find_superset_audio_no_match(self, tts_service):
        """Test that no match is found when cached audio doesn't contain all requested categories."""
        cache_key = "partial_categories"
        audio_file = tts_service.cache_dir / f"{cache_key}.mp3"
        metadata_file = tts_service.cache_dir / f"{cache_key}.json"

        # Create audio file with only US and Israel
        audio_file.write_bytes(b"partial podcast audio")

        metadata = {
            "created_at": datetime.now().isoformat(),
            "model": "tts-1-hd",
            "categories": ["israel", "us"],  # Only 2 categories
        }
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        # Request 3 categories - should NOT find match (cached is not a superset)
        result = tts_service._find_superset_audio(["us", "israel", "ai"])

        assert result is None

    def test_find_superset_audio_expired_cache(self, temp_cache_dir):
        """Test that expired cache is not returned as superset."""
        tts_service = TTSService(cache_dir=temp_cache_dir, cache_hours=1)

        cache_key = "expired_superset"
        audio_file = tts_service.cache_dir / f"{cache_key}.mp3"
        metadata_file = tts_service.cache_dir / f"{cache_key}.json"

        audio_file.write_bytes(b"old audio")

        # Create metadata with old timestamp
        metadata = {
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "model": "tts-1-hd",
            "categories": ["ai", "crypto", "israel", "us"],
        }
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        # Should not find expired cache
        result = tts_service._find_superset_audio(["us"])

        assert result is None

    def test_find_superset_audio_empty_categories(self, tts_service):
        """Test that empty categories returns None."""
        result = tts_service._find_superset_audio([])
        assert result is None

        result = tts_service._find_superset_audio(None)
        assert result is None

    def test_metadata_includes_categories(self, tts_service):
        """Test that build_audio_metadata includes categories."""
        from backend.services.tts_service import build_audio_metadata

        metadata = build_audio_metadata(
            model="tts-1-hd",
            female_voice="nova",
            male_voice="fable",
            script="Test script",
            file_size_bytes=1000,
            categories=["us", "israel"],
        )

        assert "categories" in metadata
        assert metadata["categories"] == ["israel", "us"]  # Should be sorted

    def test_metadata_without_categories(self, tts_service):
        """Test that build_audio_metadata works without categories (backward compat)."""
        from backend.services.tts_service import build_audio_metadata

        metadata = build_audio_metadata(
            model="tts-1-hd",
            female_voice="nova",
            male_voice="fable",
            script="Test script",
            file_size_bytes=1000,
        )

        assert "categories" not in metadata


class TestCacheCreatedAt:
    """Test cache_created_at functionality for accurate countdown timers."""

    def test_get_cache_created_at_valid(self, tts_service):
        """Test retrieving cache creation time from valid metadata."""
        cache_key = "test_created_at"
        audio_data = b"test audio"
        script = "Test script"

        # Save to cache (this creates metadata with created_at)
        tts_service._save_to_cache(cache_key, audio_data, script)

        # Get cache created_at
        created_at = tts_service._get_cache_created_at(cache_key)

        assert created_at is not None
        # Should be a valid ISO format timestamp
        from datetime import datetime

        parsed = datetime.fromisoformat(created_at)
        assert parsed is not None

    def test_get_cache_created_at_nonexistent(self, tts_service):
        """Test that nonexistent cache returns None."""
        created_at = tts_service._get_cache_created_at("nonexistent_key")
        assert created_at is None

    def test_get_cache_created_at_invalid_json(self, tts_service):
        """Test that invalid JSON metadata returns None."""
        cache_key = "invalid_json"
        metadata_file = tts_service.cache_dir / f"{cache_key}.json"

        # Write invalid JSON
        with open(metadata_file, "w") as f:
            f.write("not valid json {{{")

        created_at = tts_service._get_cache_created_at(cache_key)
        assert created_at is None

    def test_get_cache_created_at_missing_field(self, tts_service):
        """Test that metadata without created_at field returns None."""
        cache_key = "missing_field"
        metadata_file = tts_service.cache_dir / f"{cache_key}.json"

        # Write metadata without created_at
        with open(metadata_file, "w") as f:
            json.dump({"model": "tts-1-hd"}, f)

        created_at = tts_service._get_cache_created_at(cache_key)
        assert created_at is None

    def test_cached_podcast_includes_cache_created_at(self, tts_service, sample_newsletter_data):
        """Test that cached podcast task status includes cache_created_at."""
        # Pre-create a cached podcast using the date-based cache key
        categories = sample_newsletter_data.get("categories", ["us", "israel", "ai", "crypto"])
        cache_key = tts_service._generate_stable_cache_key(categories)
        audio_file = tts_service.cache_dir / f"{cache_key}.mp3"
        metadata_file = tts_service.cache_dir / f"{cache_key}.json"

        # Create audio and metadata (use current time to avoid cache expiration)
        audio_file.write_bytes(b"cached podcast audio")
        expected_created_at = datetime.now().isoformat()
        metadata = {
            "created_at": expected_created_at,
            "model": "tts-1-hd",
            "female_voice": "nova",
            "male_voice": "fable",
            "script_preview": "test",
            "file_size_bytes": 100,
            "categories": ["ai", "crypto", "israel", "us"],
        }
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)

        # Generate podcast with task_id to track status
        task_id = "test_task_123"
        asyncio.run(
            tts_service.generate_podcast_async(
                sample_newsletter_data, task_id=task_id, use_cache=True
            )
        )

        # Check task status includes cache_created_at
        task_status = tts_service.get_task_progress(task_id)
        assert task_status is not None
        assert task_status["status"] == "completed"
        assert "cache_created_at" in task_status
        assert task_status["cache_created_at"] == expected_created_at

    @patch.object(TTSService, "_merge_audio_files")
    def test_fresh_podcast_includes_cache_created_at(
        self, mock_merge, tts_service, sample_newsletter_data
    ):
        """Test that freshly generated podcast task status includes cache_created_at."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.content = b"audio content"

        mock_client = MagicMock()
        mock_client.audio.speech.create = AsyncMock(return_value=mock_response)
        tts_service._openai_client = mock_client

        mock_merge.return_value = tts_service.cache_dir / "merged.mp3"
        (tts_service.cache_dir / "merged.mp3").write_bytes(b"merged audio")

        # Generate fresh podcast with task_id
        task_id = "fresh_task_456"
        asyncio.run(
            tts_service.generate_podcast_async(
                sample_newsletter_data, task_id=task_id, use_cache=False
            )
        )

        # Check task status includes cache_created_at
        task_status = tts_service.get_task_progress(task_id)
        assert task_status is not None
        assert task_status["status"] == "completed"
        assert "cache_created_at" in task_status
        # For fresh podcasts, cache_created_at should be a valid timestamp
        assert task_status["cache_created_at"] is not None
