"""API routes for market newsletter and podcast generation."""

import json
import uuid
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

from fastapi import APIRouter, Query, HTTPException, Header
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from backend.config import config
from backend.services.tts_service import TTSService
from backend.services.db_service import get_db_service, DatabaseError
from backend.exceptions import TTSError
from backend.defaults import (
    NEWS_CATEGORIES,
    CATEGORY_TO_COUNT_KEY,
    PODCAST_DAILY_LIMIT,
    generate_podcast_cache_key,
    APP_VERSION,
    APP_CHANGELOG,
)
from backend.jobs.generate_content_job import run_content_generation_async
from backend.jobs.analytics_job import get_latest_report

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api", tags=["api"])

# Rate limiting for admin refresh endpoint
_last_admin_refresh_time: datetime | None = None
ADMIN_REFRESH_MIN_INTERVAL_MINUTES = 15

# Initialize services
tts_service = TTSService()


@router.get("/version")
async def get_version() -> Dict[str, Any]:
    """Return the current app version and recent changelog.

    Used by the frontend to detect version changes on stale tabs
    (via visibilitychange) and show "What's New" popups.

    Returns:
        Version string and list of recent changelog entries.
    """
    return {
        "version": APP_VERSION,
        "changelog": APP_CHANGELOG,
    }


@router.get("/analyze")
async def analyze(
    categories: str = Query(default="us,israel,ai,crypto"),
    user_id: int = Query(default=None),
) -> Dict[str, Any]:
    """Run market analysis and return JSON.

    Returns pre-generated content from DB or file cache.
    Fresh content generation is only available via /api/admin/refresh.

    Args:
        categories: Comma-separated list of categories to include (us,israel,ai,crypto)
    """
    request_id = str(uuid.uuid4())[:8]

    # Parse and validate categories
    selected_categories = [c.strip() for c in categories.split(",") if c.strip() in NEWS_CATEGORIES]
    if not selected_categories:
        selected_categories = NEWS_CATEGORIES.copy()

    logger.info(f"[{request_id}] Newsletter analysis requested (categories={selected_categories})")

    try:
        db_service = get_db_service()
        db_newsletter = db_service.get_latest_newsletter_with_articles()

        if not db_newsletter:
            logger.warning(f"[{request_id}] No content available in DB")
            raise HTTPException(
                status_code=404,
                detail="No newsletter content available. Use /api/admin/refresh to generate content.",
            )

        logger.info(f"[{request_id}] Returning newsletter from DB")

        # Filter sources_metadata by selected categories
        filtered_metadata = {
            cat: db_newsletter["sources_metadata"].get(cat, []) for cat in selected_categories
        }

        # Filter sentiment by selected categories
        filtered_sentiment = {
            cat: score
            for cat, score in db_newsletter.get("sentiment", {}).items()
            if cat in selected_categories
        }

        # Calculate input_counts from articles
        input_counts = {
            CATEGORY_TO_COUNT_KEY[cat]: len(filtered_metadata.get(cat, []))
            for cat in selected_categories
        }

        response = {
            "success": True,
            "data": {
                "sources_metadata": filtered_metadata,
                "sentiment": filtered_sentiment,
                "llm_provider": db_newsletter.get("llm_provider"),
            },
            "input_counts": input_counts,
            "cache_metadata": {
                "is_cached": True,
                "created_at": db_newsletter["created_at"],
                "last_generated_at": db_newsletter["created_at"],
            },
        }

        # Add sentiment history
        try:
            response["sentiment_history"] = db_service.get_sentiment_history(days=7)
        except Exception as hist_err:
            logger.warning(f"[{request_id}] Failed to get sentiment history: {hist_err}")
            response["sentiment_history"] = {}

        return response
    except HTTPException:
        raise
    except DatabaseError as db_err:
        logger.error(f"[{request_id}] Database error: {db_err}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/latest")
async def get_latest_content() -> Dict[str, Any]:
    """Return most recent pre-generated newsletter from DB.

    This endpoint is optimized for speed - it returns cached content
    from the database without any LLM calls or RSS fetching.

    Returns:
        Newsletter data matching /api/analyze response structure.

    Raises:
        HTTPException 404: If no newsletters exist in the database.
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Latest content requested")

    try:
        db_service = get_db_service()
        newsletter_data = db_service.get_latest_newsletter_with_articles()

        if not newsletter_data:
            logger.info(f"[{request_id}] No newsletters found in database")
            raise HTTPException(
                status_code=404,
                detail="No newsletters available. Content will be generated on the next scheduled run.",
            )

        # Build response matching /api/analyze structure
        response = {
            "success": True,
            "data": {
                "sources_metadata": newsletter_data["sources_metadata"],
                "sentiment": newsletter_data["sentiment"],
                "llm_provider": newsletter_data["llm_provider"],
            },
            "cache_metadata": {
                "is_cached": True,
                "created_at": newsletter_data["created_at"],
                "last_generated_at": newsletter_data["created_at"],
            },
        }

        # Add sentiment history
        try:
            response["sentiment_history"] = db_service.get_sentiment_history(days=7)
        except Exception as hist_err:
            logger.warning(f"[{request_id}] Failed to get sentiment history: {hist_err}")
            response["sentiment_history"] = {}

        logger.info(f"[{request_id}] Returning latest newsletter from DB")
        return response

    except HTTPException:
        raise
    except DatabaseError as db_err:
        logger.error(f"[{request_id}] Database error: {db_err}")
        raise HTTPException(status_code=500, detail="Database error retrieving newsletter")
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/podcast/latest")
async def get_latest_podcast() -> Dict[str, Any]:
    """Deprecated: Podcasts are now generated on-demand.

    Use POST /api/podcast/generate with selected categories instead.
    """
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use POST /api/podcast/generate with your selected categories.",
    )


class PodcastGenerateRequest(BaseModel):
    """Request body for POST /api/podcast/generate."""

    categories: List[str] = Field(..., min_length=1)
    user_id: int = Field(...)


@router.post("/podcast/generate")
async def generate_podcast(request: PodcastGenerateRequest) -> Dict[str, Any]:
    """Generate an on-demand podcast for the user's selected categories.

    Checks combination cache first (instant if cached). If not cached,
    generates podcast dialog via LLM and audio via TTS. Limited to
    1 generation per user per UTC day (cache hits don't count).

    Args:
        request: Categories list and authenticated user_id.

    Returns:
        Audio URL, podcast dialog, and metadata.

    Raises:
        HTTPException 400: Invalid categories
        HTTPException 404: No newsletter data available
        HTTPException 429: Daily generation limit reached
        HTTPException 500: Generation failed
    """
    request_id = str(uuid.uuid4())[:8]

    # Validate categories
    selected_categories = [c for c in request.categories if c in NEWS_CATEGORIES]
    if not selected_categories:
        raise HTTPException(status_code=400, detail="No valid categories provided")

    logger.info(
        f"[{request_id}] Podcast generation requested by user {request.user_id} "
        f"for categories: {selected_categories}"
    )

    try:
        db_service = get_db_service()

        # Get latest newsletter data with articles
        db_newsletter = db_service.get_latest_newsletter_with_articles()
        if not db_newsletter:
            raise HTTPException(
                status_code=404,
                detail="No newsletter data available. Wait for the next scheduled content generation.",
            )

        sources_metadata = db_newsletter.get("sources_metadata", {})

        # Filter sources_metadata to only selected categories
        filtered_metadata = {
            cat: sources_metadata.get(cat, [])
            for cat in selected_categories
            if sources_metadata.get(cat)
        }

        if not filtered_metadata:
            raise HTTPException(
                status_code=404,
                detail="No articles available for the selected categories.",
            )

        # Check audio cache first (free, no daily limit consumed)
        cache_key = generate_podcast_cache_key(selected_categories)
        cached_audio = tts_service._get_cached_audio(cache_key)

        if cached_audio:
            logger.info(f"[{request_id}] Podcast cache HIT for key: {cache_key}")

            # Record cache hit for analytics (doesn't count against daily limit)
            db_service.record_podcast_generation(
                user_id=request.user_id,
                categories=selected_categories,
                cache_key=cache_key,
                cached=True,
            )

            # Load metadata and dialog if available
            metadata_file = tts_service.cache_dir / f"{cache_key}.json"
            audio_metadata = {}
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r") as f:
                        audio_metadata = json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass

            return {
                "success": True,
                "cached": True,
                "audio_url": f"/api/audio/{cache_key}.mp3",
                "categories": selected_categories,
                "podcast_dialog": audio_metadata.get("podcast_dialog", []),
                "audio_metadata": {
                    "created_at": audio_metadata.get("created_at"),
                    "file_size_bytes": audio_metadata.get("file_size_bytes"),
                    "dialogue_lines": audio_metadata.get("dialogue_lines"),
                },
            }

        # Cache miss — check daily generation limit
        now = datetime.now(timezone.utc)
        generation_count = db_service.get_user_podcast_generation_count(request.user_id, now)

        if generation_count >= PODCAST_DAILY_LIMIT:
            logger.info(
                f"[{request_id}] User {request.user_id} reached daily podcast limit "
                f"({generation_count}/{PODCAST_DAILY_LIMIT})"
            )
            raise HTTPException(
                status_code=429,
                detail="Today's podcast delivered! More podcasts? Premium plans coming soon.",
            )

        # Generate podcast
        logger.info(f"[{request_id}] Generating podcast for {selected_categories}")

        newsletter_data = {
            "sources_metadata": filtered_metadata,
            "categories": selected_categories,
        }

        audio_path = await tts_service.generate_podcast_async(
            newsletter_data,
            task_id=f"ondemand_{request_id}",
        )

        # Record generation (counts against daily limit)
        db_service.record_podcast_generation(
            user_id=request.user_id,
            categories=selected_categories,
            cache_key=cache_key,
            cached=False,
        )

        # Load metadata
        metadata_file = tts_service.cache_dir / f"{cache_key}.json"
        audio_metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, "r") as f:
                    audio_metadata = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Get dialog from newsletter_data (mutated by TTS service) or metadata
        podcast_dialog = newsletter_data.get("ai_podcast_dialog", [])
        if not podcast_dialog:
            podcast_dialog = audio_metadata.get("podcast_dialog", [])

        logger.info(f"[{request_id}] Podcast generated: {audio_path.name}")
        return {
            "success": True,
            "cached": False,
            "audio_url": f"/api/audio/{cache_key}.mp3",
            "categories": selected_categories,
            "podcast_dialog": podcast_dialog,
            "audio_metadata": {
                "created_at": audio_metadata.get("created_at"),
                "file_size_bytes": audio_metadata.get("file_size_bytes"),
                "dialogue_lines": audio_metadata.get("dialogue_lines"),
            },
        }

    except HTTPException:
        raise
    except DatabaseError as db_err:
        logger.error(f"[{request_id}] Database error: {db_err}")
        raise HTTPException(status_code=500, detail="Database error")
    except TTSError as tts_err:
        logger.error(f"[{request_id}] TTS error: {tts_err}")
        raise HTTPException(status_code=500, detail=f"Podcast generation failed: {tts_err}")
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Podcast generation failed")


class SummaryAudioRequest(BaseModel):
    """Request body for /api/summary-audio."""

    summary_text: str = Field(..., min_length=1, max_length=5000)


@router.post("/summary-audio")
async def generate_summary_audio(request: SummaryAudioRequest) -> Dict[str, Any]:
    """Generate TTS audio for the summary text."""
    try:
        audio_path = await tts_service.generate_summary_audio(request.summary_text)
        audio_url = f"/api/audio/{audio_path.name}"
        return {"success": True, "audio_url": audio_url}
    except TTSError as e:
        logger.error(f"Summary TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating summary audio: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audio")


@router.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve cached audio file."""
    try:
        audio_path = tts_service.cache_dir / filename
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")

        # Summary audio files don't have metadata - just serve if exists
        if not filename.startswith("summary_"):
            cache_key = audio_path.stem
            if not tts_service._get_cached_audio(cache_key):
                raise HTTPException(status_code=410, detail="Audio file expired")

        return FileResponse(audio_path, media_type="audio/mpeg", filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache-stats")
async def cache_stats() -> Dict[str, Any]:
    """Get audio cache statistics."""
    try:
        return {"success": True, "stats": tts_service.get_cache_stats()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Admin Endpoints
# =============================================================================


@router.post("/admin/refresh")
async def admin_refresh(
    x_admin_key: str = Header(..., alias="X-Admin-Key"),
) -> Dict[str, Any]:
    """Generate fresh content and return it (admin only).

    This endpoint bypasses the schedule and generates fresh newsletter content
    immediately. Waits for generation to complete and returns the fresh data.
    Protected by API key and rate limited.

    Headers:
        X-Admin-Key: Admin API key (must match ADMIN_API_KEY env var)

    Returns:
        Fresh newsletter data (same structure as /api/analyze)

    Raises:
        HTTPException 401: Invalid or missing API key
        HTTPException 429: Rate limit exceeded (15 min between calls)
        HTTPException 500: Server configuration error or generation failed
    """
    global _last_admin_refresh_time
    request_id = str(uuid.uuid4())[:8]

    # Validate API key is configured
    if not config.admin_api_key:
        logger.error(f"[{request_id}] Admin refresh attempted but ADMIN_API_KEY not configured")
        raise HTTPException(
            status_code=500,
            detail="Admin API key not configured. Set ADMIN_API_KEY in environment.",
        )

    # Validate API key
    if x_admin_key != config.admin_api_key:
        logger.warning(f"[{request_id}] Admin refresh attempted with invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Check rate limit
    now = datetime.now()
    if _last_admin_refresh_time:
        minutes_since_last = (now - _last_admin_refresh_time).total_seconds() / 60
        if minutes_since_last < ADMIN_REFRESH_MIN_INTERVAL_MINUTES:
            remaining = ADMIN_REFRESH_MIN_INTERVAL_MINUTES - minutes_since_last
            logger.warning(
                f"[{request_id}] Admin refresh rate limited. "
                f"Last refresh was {minutes_since_last:.1f} min ago"
            )
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Please wait {remaining:.0f} minutes before refreshing again.",
            )

    # Update last refresh time
    _last_admin_refresh_time = now

    # Run content generation asynchronously
    logger.info(f"[{request_id}] Admin refresh started - generating fresh content")
    try:
        result = await run_content_generation_async()
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {result.get('error', 'Unknown error')}",
            )
        logger.info(
            f"[{request_id}] Admin refresh completed in {result.get('duration_seconds', '?')}s"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Admin refresh failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

    # Fetch and return the fresh content from DB
    try:
        db_service = get_db_service()
        db_newsletter = db_service.get_latest_newsletter_with_articles()

        if not db_newsletter:
            raise HTTPException(status_code=500, detail="Content generated but not found in DB")

        # Build response matching /api/analyze structure
        response = {
            "success": True,
            "data": {
                "sources_metadata": db_newsletter["sources_metadata"],
                "sentiment": db_newsletter.get("sentiment", {}),
                "llm_provider": db_newsletter.get("llm_provider"),
            },
            "input_counts": {
                "us_news": len(db_newsletter["sources_metadata"].get("us", [])),
                "israel_news": len(db_newsletter["sources_metadata"].get("israel", [])),
                "ai_news": len(db_newsletter["sources_metadata"].get("ai", [])),
                "crypto_news": len(db_newsletter["sources_metadata"].get("crypto", [])),
            },
            "cache_metadata": {
                "is_cached": False,
                "created_at": db_newsletter["created_at"],
                "last_generated_at": db_newsletter["created_at"],
            },
            "generation_result": {
                "duration_seconds": result.get("duration_seconds"),
                "article_counts": result.get("article_counts"),
                "podcast_generated": result.get("podcast_generated"),
            },
        }

        # Add sentiment history
        try:
            response["sentiment_history"] = db_service.get_sentiment_history(days=7)
        except Exception:
            response["sentiment_history"] = {}

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Failed to fetch generated content: {e}")
        raise HTTPException(status_code=500, detail="Content generated but failed to retrieve")


# =============================================================================
# Analytics Report Copy Page
# =============================================================================


@router.get("/analytics/report", response_class=HTMLResponse)
async def analytics_report_copy_page() -> HTMLResponse:
    """Serve a minimal page with the latest analytics report JSON and a copy button."""
    report = get_latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No analytics report available")

    report_json = json.dumps(report, indent=2, ensure_ascii=False)
    # Escape HTML entities in JSON for safe embedding
    report_json_escaped = (
        report_json.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Report — Copy Data</title>
    <style>
        body {{ margin: 0; padding: 40px 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #fcfbf8; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #2e2e2e; font-size: 20px; margin: 0 0 8px; }}
        .date {{ color: #7a9ab8; font-size: 14px; margin: 0 0 20px; }}
        .copy-btn {{
            display: inline-flex; align-items: center; gap: 8px;
            padding: 10px 20px; border: none; border-radius: 8px;
            background: #c4a882; color: white; font-size: 14px; font-weight: 600;
            cursor: pointer; margin-bottom: 16px; transition: background 0.2s;
        }}
        .copy-btn:hover {{ background: #b09570; }}
        .copy-btn.copied {{ background: #4CAF50; }}
        pre {{
            background: #1e1e1e; color: #d4d4d4; border-radius: 12px;
            padding: 20px; font-size: 12px; line-height: 1.5;
            white-space: pre-wrap; word-wrap: break-word; overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Feed Analytics Report</h1>
        <p class="date">{report.get("date", "")}</p>
        <button class="copy-btn" onclick="copyReport(this)">
            📋 Copy to Clipboard
        </button>
        <pre id="report-json">{report_json_escaped}</pre>
    </div>
    <script>
        function copyReport(btn) {{
            const text = document.getElementById('report-json').textContent;
            navigator.clipboard.writeText(text).then(() => {{
                btn.textContent = '✓ Copied!';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.textContent = '📋 Copy to Clipboard';
                    btn.classList.remove('copied');
                }}, 2000);
            }});
        }}
    </script>
</body>
</html>"""
    return HTMLResponse(content=html)
