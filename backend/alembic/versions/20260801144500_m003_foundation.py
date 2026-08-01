"""M003 foundational schema compatibility head.

Revision ID: 20260801144500
Revises: None
Create Date: 2026-08-01 14:45:00 UTC
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "20260801144500"
down_revision: str | None = None
branch_labels: tuple[str, ...] | None = ("m003",)
depends_on: tuple[str, ...] | None = None

_REQUIRED_RELATIONS = (
    "public.users",
    "public.workspaces",
    "public.workspace_memberships",
    "public.workspace_config_versions",
    "public.audit_events",
    "public.exchanges",
    "public.exchange_symbol_versions",
    "public.candles",
    "public.virtual_portfolios",
)


def upgrade() -> None:
    """Verify the Supabase migration schema before recording Alembic state.

    Supabase SQL migrations are the executable DDL source of truth because they
    also provision Auth-aware roles and RLS. Alembic records the application
    compatibility head only after every required relation exists.
    """
    bind = op.get_bind()
    missing = [
        relation
        for relation in _REQUIRED_RELATIONS
        if bind.execute(
            text("select to_regclass(:relation)"), {"relation": relation}
        ).scalar_one()
        is None
    ]
    if missing:
        raise RuntimeError(
            "Apply Supabase migrations before Alembic upgrade; missing: "
            + ", ".join(missing)
        )


def downgrade() -> None:
    """Prevent destructive rollback of identity, audit, and financial state."""
    raise RuntimeError(
        "M003 is additive-only; create a forward migration instead of downgrading"
    )