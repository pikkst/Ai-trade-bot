"""M003 foundational schema, Auth mapping, and RLS.

Revision ID: 20260801144500
Revises: None
Create Date: 2026-08-01 14:45:00 UTC
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from alembic import op

revision = "20260801144500"
down_revision: str | None = None
branch_labels: tuple[str, ...] | None = ("m003",)
depends_on: tuple[str, ...] | None = None


def _supabase_migration_sql() -> str:
    repository_root = Path(__file__).resolve().parents[3]
    migration_path = (
        repository_root
        / "supabase"
        / "migrations"
        / "20260801144500_m003_foundation.sql"
    )
    return migration_path.read_text(encoding="utf-8")


def upgrade() -> None:
    """Apply the exact SQL used by the Supabase CLI migration workflow."""
    bind = op.get_bind()
    driver_connection = cast(Any, bind.connection.driver_connection)
    with driver_connection.cursor() as cursor:
        cursor.execute(_supabase_migration_sql(), prepare=False)


def downgrade() -> None:
    """Prevent destructive rollback of identity, audit, and financial state."""
    raise RuntimeError(
        "M003 is additive-only; create a forward migration instead of downgrading"
    )
