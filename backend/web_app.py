"""FastAPI app for Ariel's English Adventure."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.config import config
from backend.defaults import APP_METADATA, APP_VERSION
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

# Setup Jinja2 templates and static files
templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

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
    """Serve the English learning app."""
    return templates.TemplateResponse(
        "english-fun.html",
        {"request": request, "version": APP_VERSION},
    )


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": APP_METADATA["version"],
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server at http://{config.flask_host}:{config.flask_port}")
    uvicorn.run(
        "backend.web_app:app",
        host=config.flask_host,
        port=config.flask_port,
        reload=config.flask_debug,
    )
