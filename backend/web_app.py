"""FastAPI app for Ariel Learning App."""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.config import config
from backend.defaults import (
    APP_METADATA,
    APP_VERSION,
    REWARD_TIERS,
    SESSIONS,
    SESSIONS_BY_SUBJECT,
    VALID_SESSION_SLUGS,
    VALID_SUBJECTS,
)
from backend.exceptions import AppError
from backend.logging_config import setup_logging
from backend.routes.game import router as game_router
from backend.sentry_config import init_sentry

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

# Initialize FastAPI app
app = FastAPI(**APP_METADATA)

# Setup Jinja2 templates and static files (legacy frontend)
templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Serve React build assets if available (new frontend)
REACT_DIST = Path("frontend/dist")
if REACT_DIST.is_dir():
    app.mount("/app/assets", StaticFiles(directory=str(REACT_DIST / "assets")), name="react-assets")

# Include routers
app.include_router(game_router)


# --- Global Exception Handlers ---


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle all custom AppError exceptions."""
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

    with sentry_sdk.new_scope() as scope:
        scope.set_tag("request_id", request_id)
        scope.set_tag("endpoint", request.url.path)
        response = await call_next(request)

    response.headers["X-Request-ID"] = request_id
    return response


logger.info("Web application initialized")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Serve the landing page."""
    return templates.TemplateResponse(
        "english-fun.html",
        {
            "request": request,
            "version": APP_VERSION,
            "reward_tiers": REWARD_TIERS,
            "sessions": SESSIONS,
            "initial_screen": "welcome",
        },
    )


@app.get("/learning", response_class=HTMLResponse)
async def learning(request: Request) -> HTMLResponse:
    """Serve the subject picker screen."""
    return templates.TemplateResponse(
        "english-fun.html",
        {
            "request": request,
            "version": APP_VERSION,
            "reward_tiers": REWARD_TIERS,
            "sessions": SESSIONS,
            "initial_screen": "subject-picker",
        },
    )


@app.get("/learning/{subject}/{session_slug}", response_class=HTMLResponse)
async def learning_session(request: Request, subject: str, session_slug: str) -> HTMLResponse:
    """Serve the game menu for a specific learning session under a subject."""
    if subject not in VALID_SUBJECTS:
        raise HTTPException(status_code=404, detail="Subject not found")
    if session_slug not in VALID_SESSION_SLUGS:
        raise HTTPException(status_code=404, detail="Session not found")
    template_name = "math-fun.html" if subject == "math" else "english-fun.html"
    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "version": APP_VERSION,
            "reward_tiers": REWARD_TIERS,
            "sessions": SESSIONS,
            "subject": subject,
            "session_slug": session_slug,
            "initial_screen": "menu",
        },
    )


@app.get("/learning/{subject_or_slug}", response_class=HTMLResponse)
async def learning_subject_or_redirect(request: Request, subject_or_slug: str) -> HTMLResponse:
    """Serve session picker for a subject, or redirect old session slug URLs."""
    if subject_or_slug in VALID_SUBJECTS:
        return templates.TemplateResponse(
            "english-fun.html",
            {
                "request": request,
                "version": APP_VERSION,
                "reward_tiers": REWARD_TIERS,
                "sessions": SESSIONS_BY_SUBJECT.get(subject_or_slug, []),
                "subject": subject_or_slug,
                "initial_screen": "session-picker",
            },
        )
    if subject_or_slug in VALID_SESSION_SLUGS:
        return RedirectResponse(url=f"/learning/english/{subject_or_slug}", status_code=301)
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": APP_METADATA["version"],
    }


# --- React SPA Catch-All ---
# Serves React's index.html for any unmatched route so React Router handles navigation.
# Only active when frontend/dist/ exists (after `npm run build`).
# Legacy Jinja2 routes above take priority since they're registered first.


@app.get("/app/{full_path:path}", response_class=HTMLResponse)
async def react_spa(full_path: str) -> FileResponse:
    """Serve the React SPA for all /app/* routes."""
    index_file = REACT_DIST / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=404, detail="React build not found. Run: cd frontend && npm run build")
    return FileResponse(str(index_file))


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server at http://{config.flask_host}:{config.flask_port}")
    uvicorn.run(
        "backend.web_app:app",
        host=config.flask_host,
        port=config.flask_port,
        reload=config.flask_debug,
    )
