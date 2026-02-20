"""FastAPI app for market newsletter and podcast generation."""

import logging
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import datetime

import sentry_sdk
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from backend.middleware import SecurityHeadersMiddleware, RateLimitMiddleware, RateLimitConfig

from backend.config import config
from backend.defaults import APP_VERSION, APP_METADATA, APP_CHANGELOG
from backend.exceptions import NewsletterError
from backend.logging_config import setup_logging
from backend.routes.api import router as api_router
from backend.routes.auth import router as auth_router
from backend.routes.feedback import router as feedback_router
from backend.routes.game import router as game_router
from backend.sentry_config import init_sentry
from backend.services.db_service import get_db_service
from backend.services.health_service import (
    check_cache_health,
    check_tts_health,
    check_config_health,
)
from backend.services.scheduler_service import get_scheduler_service

# Setup structured logging
setup_logging(
    log_level=config.log_level,
    json_output=config.log_format == "json",
)
logger = logging.getLogger(__name__)

# Initialize Sentry error monitoring
init_sentry(
    dsn=config.sentry_dsn,
    environment=config.sentry_environment,
    traces_sample_rate=config.sentry_traces_sample_rate,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: run retention cleanup
    try:
        db_service = get_db_service()
        deleted = db_service.run_retention_cleanup()
        total = sum(deleted.values())
        if total > 0:
            logger.info(f"Startup cleanup: deleted {total} old records {deleted}")
    except Exception as e:
        logger.warning(f"Startup cleanup failed: {e}")

    # Startup: start scheduler for content generation
    scheduler = get_scheduler_service()
    try:
        scheduler.start()
    except Exception as e:
        logger.warning(f"Scheduler startup failed: {e}")

    yield  # App runs here

    # Shutdown: stop scheduler
    try:
        scheduler.shutdown()
    except Exception as e:
        logger.warning(f"Scheduler shutdown failed: {e}")

    logger.info("Application shutting down")


# Initialize FastAPI app
app = FastAPI(**APP_METADATA, lifespan=lifespan)

# Add security middleware
app.add_middleware(
    SecurityHeadersMiddleware,
    force_https=config.force_https,
    csp_report_only=config.csp_report_only,
)

# Add rate limiting middleware for auth endpoints
app.add_middleware(
    RateLimitMiddleware,
    enabled=config.rate_limit_enabled,
    login_config=RateLimitConfig(
        max_requests=config.rate_limit_login_max,
        window_seconds=config.rate_limit_login_window,
    ),
    signup_config=RateLimitConfig(
        max_requests=config.rate_limit_signup_max,
        window_seconds=config.rate_limit_signup_window,
    ),
    resend_config=RateLimitConfig(
        max_requests=config.rate_limit_resend_max,
        window_seconds=config.rate_limit_resend_window,
    ),
)

# Add HTTPS redirect in production
if config.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)

# Add CORS middleware (for external clients/mobile apps)
if config.cors_enabled and config.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.cors_origins),
        allow_credentials=config.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {config.cors_origins}")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="frontend/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include routers
app.include_router(api_router)
app.include_router(auth_router)
app.include_router(feedback_router)
app.include_router(game_router)


# --- Global Exception Handlers ---


@app.exception_handler(NewsletterError)
async def newsletter_error_handler(request: Request, exc: NewsletterError) -> JSONResponse:
    """Handle all custom NewsletterError exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "Application error: %s",
        str(exc),
        extra={"request_id": request_id, "error_type": type(exc).__name__},
    )
    sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again later."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "Unhandled exception: %s",
        str(exc),
        extra={"request_id": request_id, "error_type": type(exc).__name__},
        exc_info=True,
    )
    sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# --- Request Context Middleware ---


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Attach request ID and Sentry context to each request."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    # Set Sentry scope context
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("request_id", request_id)
        scope.set_tag("endpoint", request.url.path)

        response = await call_next(request)

    response.headers["X-Request-ID"] = request_id
    return response


logger.info("Web application initialized")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the English learning app."""
    return templates.TemplateResponse(
        "english-fun.html",
        {"request": request},
    )


@app.get("/newsletter", response_class=HTMLResponse)
async def newsletter(request: Request):
    """Serve newsletter app page (logged in)."""
    return templates.TemplateResponse(
        "newsletter.html",
        {
            "request": request,
            "version": APP_VERSION,
            "changelog": APP_CHANGELOG,
            "current_year": datetime.now().year,
        },
    )


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    """Serve privacy policy page."""
    return templates.TemplateResponse(
        "privacy.html",
        {"request": request, "version": APP_VERSION, "current_year": datetime.now().year},
    )


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    """Serve terms of use page."""
    return templates.TemplateResponse(
        "terms.html",
        {"request": request, "version": APP_VERSION, "current_year": datetime.now().year},
    )


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        scheduler = get_scheduler_service()
        checks = {
            "cache": check_cache_health(),
            "tts": check_tts_health(),
            "config": check_config_health(),
            "scheduler": scheduler.get_status(),
        }
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": APP_METADATA["version"],
            "checks": checks,
        }

        check_statuses = [check["status"] for check in checks.values()]
        if "unhealthy" in check_statuses:
            health_status["status"] = "unhealthy"
        elif "degraded" in check_statuses:
            health_status["status"] = "degraded"

        logger.info(f"Health check: {health_status['status']}")
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server at http://{config.flask_host}:{config.flask_port}")
    uvicorn.run(
        "backend.web_app:app",
        host=config.flask_host,
        port=config.flask_port,
        reload=config.flask_debug,
    )
