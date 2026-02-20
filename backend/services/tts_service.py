"""TTS service for podcast generation using OpenAI or Gemini."""

import hashlib
import json
import subprocess
import asyncio
import logging
import wave
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple, Callable, cast
from openai import AsyncOpenAI, RateLimitError, APITimeoutError, APIConnectionError
from tenacity import stop_after_attempt, wait_exponential, retry_if_exception_type, AsyncRetrying

from backend.config import config
from backend.exceptions import TTSError
from backend.defaults import PODCAST_HOSTS, generate_podcast_cache_key
from backend.services.ai_content_service import AIContentService

logger = logging.getLogger(__name__)


def build_audio_metadata(
    model: str,
    female_voice: str,
    male_voice: str,
    script: str,
    file_size_bytes: int,
    dialogue_lines: int = 0,
    batch_size: Optional[int] = None,
    categories: Optional[List[str]] = None,
    podcast_dialog: Optional[List] = None,
) -> Dict:
    """Build metadata for cached audio files."""
    metadata = {
        "created_at": datetime.now().isoformat(),
        "model": model,
        "female_voice": female_voice,
        "male_voice": male_voice,
        "script_preview": script[:200] + "..." if len(script) > 200 else script,
        "file_size_bytes": file_size_bytes,
    }
    if dialogue_lines > 0:
        metadata["dialogue_lines"] = dialogue_lines
    if batch_size:
        metadata["batch_size"] = batch_size
    if categories:
        metadata["categories"] = sorted(categories)
    if podcast_dialog:
        metadata["podcast_dialog"] = podcast_dialog
    return metadata


class TTSService:
    """Podcast audio generation service supporting OpenAI and Gemini."""

    def __init__(self, cache_dir: str = "audio_cache", cache_hours: Optional[int] = None):
        self.provider = config.tts_provider
        self._openai_client = None
        self._gemini_client = None

        # Initialize the configured provider
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            raise TTSError(f"Unsupported TTS provider: {self.provider}")

        self.active_tasks: Dict[str, Dict] = {}
        self.cancelled_tasks: set = set()

        cache_path = Path(cache_dir)
        if not cache_path.is_absolute():
            cache_path = Path.cwd() / cache_dir

        self.cache_dir = cache_path.resolve()
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.cache_hours = (
            cache_hours if cache_hours is not None else (config.audio_cache_ttl // 3600)
        )

        # Provider-specific settings
        if self.provider == "openai":
            self.model = config.tts_model
            self.female_voice = config.tts_voice_alex
            self.male_voice = config.tts_voice_guy
        else:  # gemini
            self.model = config.gemini_tts_model
            self.female_voice = config.gemini_voice_alex
            self.male_voice = config.gemini_voice_guy

        logger.info(f"TTS service initialized: {self.provider} ({self.model})")

    def _init_openai(self) -> None:
        """Initialize OpenAI TTS client."""
        try:
            self._openai_client = AsyncOpenAI(api_key=config.openai_api_key, timeout=120.0)
        except Exception as e:
            raise TTSError(f"Failed to initialize OpenAI TTS: {e}")

    def _init_gemini(self) -> None:
        """Initialize Gemini TTS client."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=config.gemini_api_key)
            self._gemini_client = genai
        except Exception as e:
            raise TTSError(f"Failed to initialize Gemini TTS: {e}")

    async def generate_summary_audio(self, summary_text: str) -> Path:
        """Generate audio for summary text using female voice."""
        if not summary_text or not summary_text.strip():
            raise TTSError("Summary text is empty")

        # Generate cache key for summary
        cache_key = hashlib.sha256(f"summary:{summary_text}".encode()).hexdigest()[:16]
        output_file = self.cache_dir / f"summary_{cache_key}.mp3"

        # Return cached file if exists
        if output_file.exists():
            logger.info(f"Using cached summary audio: {output_file.name}")
            return output_file

        # Generate audio using female voice (nova)
        if self.provider == "openai":
            if self._openai_client is None:
                raise TTSError("OpenAI client not initialized")

            try:
                response = await self._openai_client.audio.speech.create(
                    model=self.model,
                    voice=self.female_voice,
                    input=summary_text,
                    speed=config.tts_speed,
                    timeout=60.0,
                )
                output_file.write_bytes(response.content)
                logger.info(f"Generated summary audio: {output_file.name}")
                return output_file
            except Exception as e:
                raise TTSError(f"Failed to generate summary audio: {e}")
        else:
            raise TTSError("Summary audio only supported with OpenAI TTS")

    def get_dialogue_from_newsletter(self, newsletter_data: Dict) -> List[Tuple[str, str]]:
        """Extract (speaker, text) tuples from newsletter data."""
        ai_podcast_dialog = newsletter_data.get("ai_podcast_dialog", [])
        if ai_podcast_dialog:
            return [tuple(line) for line in ai_podcast_dialog if len(line) >= 2]
        return []

    def format_content_for_speech(self, newsletter_data: Dict) -> str:
        """Format dialogue as script string for cache key."""
        dialogue = self.get_dialogue_from_newsletter(newsletter_data)
        return " ... ".join(f"{PODCAST_HOSTS[speaker]}: {text}" for speaker, text in dialogue)

    def _generate_stable_cache_key(self, categories: List[str]) -> str:
        """Generate date-based cache key for podcast sharing across users.

        This enables podcast caching optimization where users with the same
        category selections on the same UTC day share the same cached podcast.
        """
        return generate_podcast_cache_key(categories)

    def _generate_cache_key(self, content: str, categories: Optional[List[str]] = None) -> str:
        """Generate cache key from content and categories."""
        if categories:
            cat_suffix = "_".join(sorted(categories))
            content_with_cats = f"{content}||CATEGORIES:{cat_suffix}"
        else:
            content_with_cats = content
        return hashlib.sha256(content_with_cats.encode()).hexdigest()

    def _get_categories_key(self, categories: List[str]) -> str:
        """Generate a consistent key suffix from categories."""
        return "_".join(sorted(categories))

    def _get_cache_created_at(self, cache_key: str) -> Optional[str]:
        """Get the creation timestamp from cache metadata."""
        metadata_file = self.cache_dir / f"{cache_key}.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                return metadata.get("created_at")
            except (json.JSONDecodeError, KeyError):
                pass
        return None

    def _get_cached_audio(self, cache_key: str) -> Optional[Path]:
        """Return cached audio path if valid, None otherwise."""
        audio_file = self.cache_dir / f"{cache_key}.mp3"
        metadata_file = self.cache_dir / f"{cache_key}.json"

        if not audio_file.exists() or not metadata_file.exists():
            return None

        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            created_at = datetime.fromisoformat(metadata["created_at"])
            if datetime.now() > created_at + timedelta(hours=self.cache_hours):
                audio_file.unlink(missing_ok=True)
                metadata_file.unlink(missing_ok=True)
                return None
            return audio_file
        except (json.JSONDecodeError, KeyError, ValueError):
            audio_file.unlink(missing_ok=True)
            metadata_file.unlink(missing_ok=True)
            return None

    def _find_superset_audio(self, requested_categories: List[str]) -> Optional[Path]:
        """Find cached audio for EXACT category match only.

        NOTE: We no longer support superset matching because users who select
        US+Israel don't want to hear about AI+Crypto topics in their podcast.
        Only exact category matches are returned.
        """
        # Disabled: superset cache returns wrong content for fewer categories
        # Users selecting US+Israel should NOT get a podcast that includes AI+Crypto
        return None

    def _save_to_cache(self, cache_key: str, audio_data: bytes, script: str) -> Path:
        """Save audio data to cache with metadata."""
        audio_file = self.cache_dir / f"{cache_key}.mp3"
        metadata_file = self.cache_dir / f"{cache_key}.json"

        with open(audio_file, "wb") as f:
            f.write(audio_data)

        metadata = build_audio_metadata(
            model=self.model,
            female_voice=self.female_voice,
            male_voice=self.male_voice,
            script=script,
            file_size_bytes=len(audio_data),
        )
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        return audio_file

    async def _generate_line_async(self, text: str, voice: str, cache_key: str, index: int) -> Path:
        """Generate audio for single dialogue line with retry."""
        if self.provider == "openai":
            return await self._generate_line_openai(text, voice, cache_key, index)
        else:
            return await self._generate_line_gemini(text, voice, cache_key, index)

    async def _generate_line_openai(
        self, text: str, voice: str, cache_key: str, index: int
    ) -> Path:
        """Generate audio using OpenAI TTS."""
        if self._openai_client is None:
            raise TTSError("OpenAI client not initialized")

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1, min=4, max=60),
            retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIConnectionError)),
        ):
            with attempt:
                try:
                    response = await self._openai_client.audio.speech.create(
                        model=self.model,
                        voice=voice,
                        input=text,
                        speed=config.tts_speed,
                        timeout=30.0,
                    )
                    temp_file = self.cache_dir / f"temp_line_{cache_key}_{index}.mp3"
                    temp_file.write_bytes(response.content)
                    return temp_file
                except (RateLimitError, APITimeoutError, APIConnectionError):
                    raise
                except Exception as e:
                    raise TTSError(f"OpenAI TTS error at line {index + 1}: {e}")

        raise TTSError(f"Failed to generate line {index + 1} after retries")

    async def _generate_line_gemini(
        self, text: str, voice: str, cache_key: str, index: int
    ) -> Path:
        """Generate audio using Gemini TTS."""
        try:
            # Run sync Gemini call in executor to avoid blocking
            loop = asyncio.get_event_loop()

            def generate_tts():
                model = self._gemini_client.GenerativeModel(self.model)
                response = model.generate_content(
                    text,
                    generation_config={
                        "response_modalities": ["AUDIO"],
                        "speech_config": {
                            "voice_config": {
                                "prebuilt_voice_config": {
                                    "voice_name": voice,
                                }
                            }
                        },
                    },
                )
                return response

            response = await loop.run_in_executor(None, generate_tts)

            # Extract PCM audio data from response
            audio_data = response.candidates[0].content.parts[0].inline_data.data

            # Convert PCM to WAV, then to MP3 using ffmpeg
            temp_wav = self.cache_dir / f"temp_line_{cache_key}_{index}.wav"
            temp_mp3 = self.cache_dir / f"temp_line_{cache_key}_{index}.mp3"

            # Write WAV file (Gemini outputs 24kHz mono 16-bit PCM)
            with wave.open(str(temp_wav), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(24000)
                wf.writeframes(audio_data)

            # Convert WAV to MP3 using ffmpeg
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        str(temp_wav),
                        "-codec:a",
                        "libmp3lame",
                        "-q:a",
                        "2",
                        str(temp_mp3),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                stderr_lines = (e.stderr or "").strip().splitlines()
                error_lines = [
                    line
                    for line in stderr_lines
                    if not line.startswith("  ") and "Copyright" not in line
                ]
                error_summary = "\n".join(error_lines[-5:]) if error_lines else "no stderr"
                logger.error(f"ffmpeg WAV→MP3 failed (exit {e.returncode}): {error_summary}")
                raise TTSError(f"ffmpeg WAV to MP3 failed: {e.returncode} - {error_summary}")
            finally:
                temp_wav.unlink(missing_ok=True)

            return temp_mp3
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "resource exhausted" in error_str or "rate limit" in error_str:
                logger.warning(f"Gemini TTS rate limit at line {index + 1}: {e}")
            raise TTSError(f"Gemini TTS error at line {index + 1}: {e}")

    async def generate_podcast_async(
        self,
        newsletter_data: Dict,
        task_id: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        use_cache: bool = True,
        batch_size: int = 10,
    ) -> Path:
        """Generate podcast audio asynchronously with progress tracking."""
        if task_id:
            self.active_tasks[task_id] = {
                "status": "starting",
                "progress": 0,
                "total": 0,
                "message": "Preparing...",
                "started_at": datetime.now().isoformat(),
            }

        try:
            if not newsletter_data:
                raise TTSError("Newsletter data cannot be empty")

            # Extract categories for cache key
            categories = newsletter_data.get("categories", ["us", "israel", "ai", "crypto"])

            # Check AUDIO cache FIRST using date-based key (before generating dialog)
            # This saves money by sharing podcasts across users with same categories
            cache_key = self._generate_stable_cache_key(categories)
            logger.info(f"Podcast cache key: {cache_key}")

            if use_cache:
                cached_audio = self._get_cached_audio(cache_key)
                if cached_audio:
                    cache_created_at = self._get_cache_created_at(cache_key)
                    logger.info(f"Podcast cache HIT for key: {cache_key}")
                    if task_id:
                        self.active_tasks[task_id].update(
                            {
                                "status": "completed",
                                "message": "Using cached audio",
                                "completed_at": datetime.now().isoformat(),
                                "cache_created_at": cache_created_at,
                                "audio_file": str(cached_audio),
                                "ai_podcast_dialog": [],  # Not needed for cached audio
                            }
                        )
                    if progress_callback:
                        progress_callback(1, 1, "completed")
                    return cached_audio

            # No cache hit - need to generate dialog and audio
            logger.info(f"Podcast cache MISS for key: {cache_key}")
            existing_dialog = newsletter_data.get("ai_podcast_dialog", [])
            if existing_dialog:
                logger.info(f"Using provided podcast dialog ({len(existing_dialog)} lines)")
                dialogue = [tuple(line) for line in existing_dialog if len(line) >= 2]
            else:
                # Generate podcast dialog from article summaries
                logger.info("Generating podcast dialog from article summaries...")

                sources_metadata = newsletter_data.get("sources_metadata", {})
                if not sources_metadata:
                    raise TTSError("No sources_metadata available to generate podcast dialog")

                ai_content = AIContentService()
                podcast_dialog = ai_content.generate_podcast_dialog(sources_metadata, categories)

                if not podcast_dialog:
                    raise TTSError("Failed to generate podcast dialog")

                # Convert to tuples for processing
                dialogue = [tuple(line) for line in podcast_dialog if len(line) >= 2]

                # Store in newsletter_data for return to frontend
                newsletter_data["ai_podcast_dialog"] = podcast_dialog
                logger.info(f"Generated podcast dialog with {len(dialogue)} lines")

            if not dialogue:
                raise TTSError("Generated dialogue is empty")

            # Cache key already generated at the top using stable key
            line_count = len(dialogue)
            if task_id:
                self.active_tasks[task_id].update(
                    {"total": line_count, "status": "generating", "message": "Generating audio..."}
                )
            if progress_callback:
                progress_callback(0, line_count, "generating")

            temp_files: List[Path] = []
            completed = 0

            for batch_start in range(0, line_count, batch_size):
                if task_id and task_id in self.cancelled_tasks:
                    self.active_tasks[task_id].update(
                        {"status": "cancelled", "message": "Cancelled by user"}
                    )
                    raise TTSError("Podcast generation cancelled")

                batch = dialogue[batch_start : min(batch_start + batch_size, line_count)]
                batch_tasks = [
                    self._generate_line_async(
                        text,
                        self.female_voice if speaker == "female" else self.male_voice,
                        cache_key,
                        batch_start + i,
                    )
                    for i, (speaker, text) in enumerate(batch)
                ]

                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, BaseException):
                        raise result
                    temp_files.append(cast(Path, result))
                    completed += 1
                    if task_id:
                        self.active_tasks[task_id]["progress"] = completed
                    if progress_callback:
                        progress_callback(completed, line_count, "generating")

            if task_id:
                self.active_tasks[task_id].update(
                    {"status": "merging", "message": "Merging audio..."}
                )
            if progress_callback:
                progress_callback(line_count, line_count, "merging")

            if len(temp_files) == 1:
                final_path = self.cache_dir / f"{cache_key}.mp3"
                temp_files[0].rename(final_path)
            else:
                final_path = self._merge_audio_files(temp_files, cache_key)
                for temp_file in temp_files:
                    temp_file.unlink(missing_ok=True)

            metadata_file = self.cache_dir / f"{cache_key}.json"
            # Generate script preview for metadata
            script_preview = self.format_content_for_speech(newsletter_data)
            stored_dialog = newsletter_data.get("ai_podcast_dialog", [])
            if not stored_dialog and dialogue:
                stored_dialog = [list(line) for line in dialogue]
            metadata = build_audio_metadata(
                model=self.model,
                female_voice=self.female_voice,
                male_voice=self.male_voice,
                script=script_preview,
                file_size_bytes=final_path.stat().st_size,
                dialogue_lines=len(dialogue),
                batch_size=batch_size,
                categories=categories,
                podcast_dialog=stored_dialog,
            )
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Podcast generated and cached for categories {categories}")

            # Get cache creation time from the metadata we just wrote
            cache_created_at = self._get_cache_created_at(cache_key)

            # Get dialog for response - use stored dialog or reconstruct from dialogue tuples
            stored_dialog = newsletter_data.get("ai_podcast_dialog", [])
            logger.info(
                f"Podcast completion: newsletter_data has {len(stored_dialog)} dialog lines"
            )
            if not stored_dialog and dialogue:
                # Fallback: reconstruct from dialogue tuples
                stored_dialog = [list(line) for line in dialogue]
                logger.info(
                    f"Fallback: reconstructed {len(stored_dialog)} dialog lines from dialogue tuples"
                )

            if task_id:
                update_data = {
                    "status": "completed",
                    "message": "Done",
                    "completed_at": datetime.now().isoformat(),
                    "cache_created_at": cache_created_at,
                    "audio_file": str(final_path),
                    "ai_podcast_dialog": stored_dialog,
                }
                self.active_tasks[task_id].update(update_data)
                logger.info(
                    f"Updated active_tasks[{task_id}] with ai_podcast_dialog: {len(stored_dialog)} lines"
                )
            if progress_callback:
                progress_callback(line_count, line_count, "completed")

            return final_path

        except TTSError:
            raise
        except Exception as e:
            if task_id:
                self.active_tasks[task_id].update(
                    {"status": "failed", "message": str(e), "error": str(e)}
                )
            if progress_callback:
                progress_callback(0, 0, "failed")
            raise TTSError(f"Failed to generate audio: {e}")

    def get_task_progress(self, task_id: str) -> Optional[Dict]:
        return self.active_tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel an in-progress task."""
        if task_id in self.active_tasks:
            task_info = self.active_tasks[task_id]
            if task_info["status"] in ["generating", "merging", "starting"]:
                self.cancelled_tasks.add(task_id)
                task_info.update({"status": "cancelled", "message": "Cancellation requested"})
                return True
        return False

    def cleanup_task(self, task_id: str) -> None:
        self.active_tasks.pop(task_id, None)
        self.cancelled_tasks.discard(task_id)

    def _merge_audio_files(self, audio_files: List[Path], cache_key: str) -> Path:
        """Merge audio files using ffmpeg with re-encoding for compatibility."""
        output_file = self.cache_dir / f"{cache_key}.mp3"
        concat_file = self.cache_dir / f"concat_{cache_key}.txt"

        # Validate input files exist and are non-empty
        for audio_file in audio_files:
            if not audio_file.exists():
                raise TTSError(f"Audio file missing before merge: {audio_file.name}")
            if audio_file.stat().st_size == 0:
                raise TTSError(f"Audio file is empty before merge: {audio_file.name}")

        with open(concat_file, "w") as f:
            for audio_file in audio_files:
                f.write(f"file '{audio_file.absolute()}'\n")

        try:
            # Re-encode during concat to handle different MP3 parameters
            # between lines (bitrate, sample rate differences cause -c copy to fail)
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(concat_file),
                    "-codec:a",
                    "libmp3lame",
                    "-q:a",
                    "2",
                    str(output_file),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return output_file
        except subprocess.CalledProcessError as e:
            # Extract only the error-relevant lines from stderr (skip ffmpeg version info)
            stderr_lines = (e.stderr or "").strip().splitlines()
            error_lines = [
                line
                for line in stderr_lines
                if not line.startswith("  ")
                and "Copyright" not in line
                and "configuration:" not in line
                and "built with" not in line
                and "lib" not in line[:5]
            ]
            error_summary = (
                "\n".join(error_lines[-5:])
                if error_lines
                else e.stderr[-500:] if e.stderr else "no stderr"
            )
            logger.error(f"ffmpeg merge failed (exit {e.returncode}): {error_summary}")
            raise TTSError(f"ffmpeg merge failed: {e.returncode} - {error_summary}")
        finally:
            concat_file.unlink(missing_ok=True)

    def cleanup_expired_cache(self) -> int:
        """Remove expired cache files."""
        removed = 0
        for metadata_file in self.cache_dir.glob("*.json"):
            if not self._get_cached_audio(metadata_file.stem):
                removed += 1
        return removed

    def get_cache_stats(self) -> Dict:
        audio_files = list(self.cache_dir.glob("*.mp3"))
        total_size = sum(f.stat().st_size for f in audio_files)
        return {
            "total_files": len(audio_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir.absolute()),
        }
