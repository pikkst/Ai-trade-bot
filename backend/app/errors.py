"""Stable application/domain errors and safe API error envelopes."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from app.observability import redact_value
from app.request_context import current_context


class ErrorBody(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    correlation_id: str
    details: dict[str, Any] | None = None


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)

    error: ErrorBody


class AppError(Exception):
    """Project-owned operational error safe to map at transport boundaries."""

    code = "application_error"
    status_code = 500
    public_message = "The request could not be completed."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message or self.public_message)
        self.details = details


class ValidationAppError(AppError):
    code = "validation_error"
    status_code = 400
    public_message = "The request is invalid."


class NotFoundAppError(AppError):
    code = "not_found"
    status_code = 404
    public_message = "The requested resource was not found."


class ConflictAppError(AppError):
    code = "conflict"
    status_code = 409
    public_message = "The request conflicts with current state."


class ConcurrencyConflictError(ConflictAppError):
    code = "concurrency_conflict"
    public_message = "The resource changed before the request could be applied."


class IdempotencyConflictError(ConflictAppError):
    code = "idempotency_conflict"
    public_message = "The idempotency key was already used for a different request."


class DependencyUnavailableError(AppError):
    code = "dependency_unavailable"
    status_code = 503
    public_message = "A required dependency is temporarily unavailable."


def error_response(error: AppError) -> JSONResponse:
    context = current_context()
    details = redact_value(error.details) if error.details is not None else None
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code=error.code,
            message=error.public_message,
            correlation_id=context.correlation_id,
            details=details,
        )
    )
    return JSONResponse(status_code=error.status_code, content=envelope.model_dump())


def install_error_handlers(app: FastAPI) -> None:
    """Install fail-safe project-owned exception mapping."""

    @app.exception_handler(AppError)
    async def _app_error_handler(_request: Request, error: AppError) -> JSONResponse:
        return error_response(error)

    @app.exception_handler(Exception)
    async def _unexpected_error_handler(
        _request: Request, _error: Exception
    ) -> JSONResponse:
        return error_response(AppError())
