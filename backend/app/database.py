"""SQLAlchemy 2 session and PostgreSQL request-context helpers."""

from __future__ import annotations

import os
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from typing import Literal
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@127.0.0.1:54322/postgres"
)
DatabaseRole = Literal[
    "anon",
    "authenticated",
    "service_role",
    "app_workflow",
    "app_migration",
]
_ALLOWED_DATABASE_ROLES: frozenset[str] = frozenset(
    {"anon", "authenticated", "service_role", "app_workflow", "app_migration"}
)

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def database_url() -> str:
    """Return the configured database URL without requiring cloud credentials."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def build_engine(url: str | None = None) -> Engine:
    """Build a PostgreSQL engine with safe connection liveness checks."""
    return create_engine(url or database_url(), pool_pre_ping=True)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build an explicit SQLAlchemy 2 session factory."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session_factory() -> sessionmaker[Session]:
    """Return the process session factory, initializing it lazily."""
    global _engine, _session_factory
    if _session_factory is None:
        _engine = build_engine()
        _session_factory = build_session_factory(_engine)
    return _session_factory


@contextmanager
def transactional_session(
    factory: sessionmaker[Session] | None = None,
) -> Iterator[Session]:
    """Commit successful work and roll back every raised exception."""
    session = (factory or get_session_factory())()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def session_dependency() -> Generator[Session, None, None]:
    """FastAPI dependency that owns one transaction per request."""
    with transactional_session() as session:
        yield session


def apply_request_context(
    session: Session,
    *,
    role: DatabaseRole,
    auth_subject: UUID | None,
) -> None:
    """Apply the same role/JWT context used by Supabase Data API requests.

    The database role is selected from a closed allowlist before interpolation.
    JWT values use bound parameters. The settings are transaction-local and are
    removed automatically on commit or rollback.
    """
    if role not in _ALLOWED_DATABASE_ROLES:
        raise ValueError(f"Unsupported database role: {role}")

    session.execute(text(f"set local role {role}"))
    session.execute(
        text("select set_config('request.jwt.claim.role', :role, true)"),
        {"role": role},
    )
    session.execute(
        text("select set_config('request.jwt.claim.sub', :subject, true)"),
        {"subject": "" if auth_subject is None else str(auth_subject)},
    )
