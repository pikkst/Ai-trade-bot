"""M007 preflight identity + terminal transition enforcement compatibility.

Revision ID: 20260808170000
Revises: 20260808160000
Create Date: 2026-08-08 17:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260808170000"
down_revision: str | None = "20260808160000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the ninth-pass schema was applied before recording head: the
    ingestion_type check must allow 'preflight_failure' and the terminal
    transition trigger must exist."""
    bind = op.get_bind()
    has_preflight = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_constraint
            where conrelid = 'public.market_data_ingestions'::regclass
              and contype = 'c'
              and conname = 'market_data_ingestions_ingestion_type_check'
              and pg_get_constraintdef(oid) like '%preflight_failure%'
            """
        )
    ).scalar_one()
    has_trigger = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_trigger
            where tgname = 'data_quality_events_terminal_transition_trigger'
              and not tgisinternal
            """
        )
    ).scalar_one()
    if not has_preflight:
        raise RuntimeError(
            "market_data_ingestions_ingestion_type_check must include "
            "preflight_failure; run the Supabase migration first"
        )
    if not has_trigger:
        raise RuntimeError(
            "data_quality_events_terminal_transition_trigger is missing; "
            "run the Supabase migration first"
        )


def downgrade() -> None:
    """Prevent destructive rollback of preflight identity."""
    raise RuntimeError(
        "M007 preflight identity is additive-only; create a forward migration instead"
    )
