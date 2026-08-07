"""Transaction context used to prohibit network side effects while DB work is open."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

_transaction_depth: ContextVar[int] = ContextVar("transaction_depth", default=0)


@contextmanager
def transaction_scope() -> Iterator[None]:
    """Mark the current execution context as owning an active DB transaction."""
    token = _transaction_depth.set(_transaction_depth.get() + 1)
    try:
        yield
    finally:
        _transaction_depth.reset(token)


def transaction_active() -> bool:
    return _transaction_depth.get() > 0


def assert_network_call_allowed() -> None:
    """Fail fast when provider/network code is invoked inside a DB transaction."""
    if transaction_active():
        raise RuntimeError("network calls are prohibited inside database transactions")
