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

from backend.config import config
from backend.defaults import APP_METADATA
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

# Include API routers (must be before static file mounts)
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


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": APP_METADATA["version"],
    }


# --- Backward-compatibility redirect for old /app/ URLs ---


@app.get("/app/{full_path:path}")
async def redirect_app_urls(full_path: str) -> RedirectResponse:
    """Redirect old /app/ URLs to root equivalents."""
    return RedirectResponse(url=f"/{full_path}", status_code=301)


# --- React SPA ---
# Mount /assets for built JS/CSS chunks.
# Catch-all route serves index.html for SPA client-side routing,
# or static files from dist root (favicon, SVGs).

REACT_DIST = Path("frontend/dist")
if REACT_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=str(REACT_DIST / "assets")), name="react-assets")


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def react_spa(full_path: str) -> FileResponse:
    """Serve static files from dist or fall back to index.html for SPA routing."""
    # First check if this is a real file in dist (favicon.png, SVGs)
    file_path = REACT_DIST / full_path
    if full_path and file_path.is_file():
        return FileResponse(str(file_path))
    # Otherwise serve index.html for React Router
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
