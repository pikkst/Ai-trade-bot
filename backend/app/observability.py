"""Structured logging, redaction, and request context middleware."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.request_context import bind_context, current_context

_REDACTED = "[REDACTED]"
_SENSITIVE_KEY_RE = re.compile(
    r"(^|_)(authorization|cookie|password|passwd|secret|token|api_key|apikey|"
    r"database_url|dsn)($|_)",
    re.IGNORECASE,
)
_BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")
_URL_CREDENTIAL_RE = re.compile(
    r"(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*://)[^\s/@:]+:[^\s/@]+@"
)


def redact_value(value: Any, *, key: str | None = None) -> Any:
    """Recursively redact credentials while preserving operational IDs."""
    if key is not None and _SENSITIVE_KEY_RE.search(key):
        return _REDACTED
    if isinstance(value, Mapping):
        return {
            str(item_key): redact_value(item, key=str(item_key))
            for item_key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)
    if isinstance(value, str):
        redacted = _BEARER_RE.sub(f"Bearer {_REDACTED}", value)
        return _URL_CREDENTIAL_RE.sub(r"\g<scheme>[REDACTED]@", redacted)
    return value


def _redact_processor(
    _logger: Any,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    return {
        key: redact_value(value, key=key)
        for key, value in event_dict.items()
    }


def _context_processor(
    _logger: Any,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    for key, value in current_context().as_dict().items():
        event_dict.setdefault(key, value)
    return event_dict


def configure_logging(*, level: str = "INFO") -> None:
    """Configure JSON structured logging with mandatory secret redaction."""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(message)s",
        force=True,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _context_processor,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _redact_processor,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Bind correlation/request IDs and return them on every HTTP response."""

    def __init__(self, app: Any, *, max_id_length: int = 128) -> None:
        super().__init__(app)
        self._max_id_length = max_id_length

    def _clean_id(self, value: str | None) -> str | None:
        if value is None:
            return None
        candidate = value.strip()
        if not candidate or len(candidate) > self._max_id_length:
            return None
        if not all(
            character.isalnum() or character in "-_.:"
            for character in candidate
        ):
            return None
        return candidate

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = (
            self._clean_id(request.headers.get("X-Request-ID")) or uuid4().hex
        )
        correlation_id = (
            self._clean_id(request.headers.get("X-Correlation-ID"))
            or request_id
        )
        with bind_context(
            correlation_id=correlation_id,
            request_id=request_id,
        ):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
            return response
