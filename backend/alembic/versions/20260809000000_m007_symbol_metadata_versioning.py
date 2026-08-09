"""M007 symbol-metadata versioning compatibility.

Revision ID: 20260809000000
Revises: 20260808170000
Create Date: 2026-08-09 00:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260809000000"
down_revision: str | None = "20260808170000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the symbol-metadata versioning schema was applied."""
    bind = op.get_bind()
    has_superseded_by = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_attribute
            where attrelid = 'public.exchange_symbol_versions'::regclass
              and attname = 'superseded_by'
              and not attisdropped
            """
        )
    ).scalar_one()
    has_max_quantity = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_attribute
            where attrelid = 'public.exchange_symbol_versions'::regclass
              and attname = 'max_quantity'
              and not attisdropped
            """
        )
    ).scalar_one()
    has_max_notional = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_attribute
            where attrelid = 'public.exchange_symbol_versions'::regclass
              and attname = 'max_notional'
              and not attisdropped
            """
        )
    ).scalar_one()
    if not has_superseded_by:
        raise RuntimeError(
            "exchange_symbol_versions.superseded_by is missing; "
            "run the Supabase migration first"
        )
    if not has_max_quantity:
        raise RuntimeError(
            "exchange_symbol_versions.max_quantity is missing; "
            "run the Supabase migration first"
        )
    if not has_max_notional:
        raise RuntimeError(
            "exchange_symbol_versions.max_notional is missing; "
            "run the Supabase migration first"
        )


def downgrade() -> None:
    """Prevent destructive rollback of symbol-metadata versioning."""
    raise RuntimeError(
        "M007 symbol-metadata versioning is additive-only; "
        "create a forward migration instead"
    )
