"""M003 RLS-backed Data API grants and approved views.

Revision ID: 20260801150000
Revises: 20260801144500
Create Date: 2026-08-01 15:00:00 UTC
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from alembic import op

revision = "20260801150000"
down_revision: str | None = "20260801144500"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def _supabase_migration_sql() -> str:
    repository_root = Path(__file__).resolve().parents[3]
    migration_path = (
        repository_root
        / "supabase"
        / "migrations"
        / "20260801150000_m003_data_api_grants.sql"
    )
    return migration_path.read_text(encoding="utf-8")


def upgrade() -> None:
    """Apply the exact SQL used by the Supabase CLI migration workflow."""
    bind = op.get_bind()
    driver_connection = cast(Any, bind.connection.driver_connection)
    with driver_connection.cursor() as cursor:
        cursor.execute(_supabase_migration_sql(), prepare=False)


def downgrade() -> None:
    """Prevent destructive rollback of security policy history."""
    raise RuntimeError(
        "M003 is additive-only; create a forward migration instead of downgrading"
    )
