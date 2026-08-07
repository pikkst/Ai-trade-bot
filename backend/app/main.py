"""FastAPI entry point for The Daily Roast AI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.database import get_session_factory
from app.errors import install_error_handlers
from app.health import liveness, readiness
from app.observability import CorrelationIdMiddleware, configure_logging
from app.settings import AppSettings, load_settings


def create_app(settings: AppSettings | None = None) -> FastAPI:
    """Create a fully configured application without performing provider I/O."""
    runtime_settings = settings or load_settings()
    configure_logging(level=runtime_settings.log_level)

    application = FastAPI(title="The Daily Roast AI", version="0.1.0")
    application.state.settings = runtime_settings
    application.add_middleware(
        CorrelationIdMiddleware,
        max_id_length=runtime_settings.max_request_id_length,
    )
    install_error_handlers(application)

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/health/live")
    def health_live() -> dict[str, object]:
        return liveness().as_dict()

    @application.get("/health/ready")
    def health_ready() -> JSONResponse:
        check = readiness(
            check_database=runtime_settings.health_database_check,
            factory=(
                get_session_factory()
                if runtime_settings.health_database_check
                else None
            ),
        )
        return JSONResponse(
            status_code=200 if check.status == "ready" else 503,
            content=check.as_dict(),
        )

    @application.get("/")
    def root() -> dict[str, str]:
        return {
            "name": "The Daily Roast AI",
            "environment": runtime_settings.environment,
        }

    return application


app = create_app()
