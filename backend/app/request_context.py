"""Context propagation for requests, jobs, and research cycles."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Iterator
from uuid import uuid4

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
_job_id: ContextVar[str | None] = ContextVar("job_id", default=None)
_cycle_id: ContextVar[str | None] = ContextVar("cycle_id", default=None)


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    correlation_id: str
    request_id: str | None = None
    job_id: str | None = None
    cycle_id: str | None = None

    def as_dict(self) -> dict[str, str]:
        return {
            key: value
            for key, value in {
                "correlation_id": self.correlation_id,
                "request_id": self.request_id,
                "job_id": self.job_id,
                "cycle_id": self.cycle_id,
            }.items()
            if value is not None
        }


def current_context() -> ExecutionContext:
    return ExecutionContext(
        correlation_id=_correlation_id.get() or uuid4().hex,
        request_id=_request_id.get(),
        job_id=_job_id.get(),
        cycle_id=_cycle_id.get(),
    )


@contextmanager
def bind_context(
    *,
    correlation_id: str | None = None,
    request_id: str | None = None,
    job_id: str | None = None,
    cycle_id: str | None = None,
) -> Iterator[ExecutionContext]:
    correlation = correlation_id or uuid4().hex
    tokens: list[tuple[ContextVar[str | None], Token[str | None]]] = []
    for variable, value in (
        (_correlation_id, correlation),
        (_request_id, request_id),
        (_job_id, job_id),
        (_cycle_id, cycle_id),
    ):
        tokens.append((variable, variable.set(value)))
    try:
        yield ExecutionContext(correlation, request_id, job_id, cycle_id)
    finally:
        for variable, token in reversed(tokens):
            variable.reset(token)
