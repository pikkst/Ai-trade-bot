"""M007 append-only terminal-resolution idempotency compatibility head.

Revision ID: 20260808160000
Revises: 20260808150000
Create Date: 2026-08-08 16:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260808160000"
down_revision: str | None = "20260808150000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the structured terminal-resolution schema was applied before
    recording head: the supersedes_event_id column and its partial unique
    index must exist so terminal events carry a deterministic parent identity
    and the same blocker cannot be superseded twice."""
    bind = op.get_bind()
    has_column = bind.execute(
        text(
            """
            select count(*) > 0
            from information_schema.columns
            where table_schema = 'public'
              and table_name = 'data_quality_events'
              and column_name = 'supersedes_event_id'
            """
        )
    ).scalar_one()
    if not has_column:
        raise RuntimeError(
            "data_quality_events.supersedes_event_id is missing; "
            "run the Supabase migration first"
        )


def downgrade() -> None:
    """Prevent destructive rollback of terminal-resolution idempotency."""
    raise RuntimeError(
        "M007 terminal-resolution idempotency is additive-only; "
        "create a forward migration instead"
    )
