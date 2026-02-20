"""Health check service for monitoring application status."""

from typing import Dict, Any

from backend.config import config
from backend.services.tts_service import TTSService
from backend.services.newsletter_cache_service import NewsletterCacheService


# Lazy-initialized services (avoid circular imports)
_tts_service: TTSService | None = None
_newsletter_cache: NewsletterCacheService | None = None


def _get_tts_service() -> TTSService:
    """Get or create TTS service instance."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service


def _get_newsletter_cache() -> NewsletterCacheService:
    """Get or create newsletter cache service instance."""
    global _newsletter_cache
    if _newsletter_cache is None:
        _newsletter_cache = NewsletterCacheService(cache_minutes=config.newsletter_cache_ttl // 60)
    return _newsletter_cache


def check_cache_health() -> Dict[str, Any]:
    """Check newsletter cache health status."""
    try:
        stats = _get_newsletter_cache().get_cache_stats()
        return {"status": "healthy", "cached_files": stats.get("total_files", 0)}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


def check_tts_health() -> Dict[str, Any]:
    """Check TTS service health status."""
    try:
        stats = _get_tts_service().get_cache_stats()
        return {"status": "healthy", "cached_files": stats["total_files"]}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


def check_config_health() -> Dict[str, Any]:
    """Check configuration health status."""
    try:
        config.validate()
        return {
            "status": "healthy",
            "llm_provider": config.llm_provider,
            "llm_model": (
                config.gemini_model if config.llm_provider == "gemini" else config.openai_model
            ),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
