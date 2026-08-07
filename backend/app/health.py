"""Liveness/readiness foundations with optional database verification."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, Session


@dataclass(frozen=True, slots=True)
class HealthStatus:
    status: str
    checks: dict[str, str]

    def as_dict(self) -> dict[str, object]:
        return {"status": self.status, "checks": self.checks}


def liveness() -> HealthStatus:
    """Liveness proves the process can serve Python code without external I/O."""
    return HealthStatus(status="ok", checks={"process": "ok"})


def readiness(
    *,
    check_database: bool,
    factory: sessionmaker[Session] | None = None,
) -> HealthStatus:
    """Readiness optionally verifies the configured database dependency."""
    checks = {"process": "ok"}
    if not check_database:
        checks["database"] = "not_required"
        return HealthStatus(status="ready", checks=checks)
    if factory is None:
        raise ValueError("a session factory is required when database readiness is enabled")
    try:
        with factory() as session:
            session.execute(text("select 1"))
    except Exception:
        checks["database"] = "unavailable"
        return HealthStatus(status="not_ready", checks=checks)
    checks["database"] = "ok"
    return HealthStatus(status="ready", checks=checks)
