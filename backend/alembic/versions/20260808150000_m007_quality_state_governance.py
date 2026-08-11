"""M007 quality-state governance compatibility head.

Revision ID: 20260808150000
Revises: 20260808140000
Create Date: 2026-08-08 15:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260808150000"
down_revision: str | None = "20260808140000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the quality-state governance schema was applied before
    recording head: the canonical vocabulary includes the append-only
    clock_drift_recovered terminal state, and the app_workflow UPDATE grant
    was revoked because quality resolution is append-only."""
    bind = op.get_bind()
    has_clock_recovered = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_constraint
            where conrelid = 'public.data_quality_events'::regclass
              and contype = 'c'
              and conname = 'data_quality_events_event_type_check'
              and pg_get_constraintdef(oid) like '%clock_drift_recovered%'
            """
        )
    ).scalar_one()
    if not has_clock_recovered:
        raise RuntimeError(
            "data_quality_events_event_type_check must include "
            "clock_drift_recovered; run the Supabase migration first"
        )


def downgrade() -> None:
    """Prevent destructive rollback of quality-state governance."""
    raise RuntimeError(
        "M007 quality-state governance is additive-only; "
        "create a forward migration instead"
    )
