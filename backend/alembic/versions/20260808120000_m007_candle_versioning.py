"""M007 candle versioning compatibility head.

Revision ID: 20260808120000
Revises: 20260808110000
Create Date: 2026-08-08 12:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260808120000"
down_revision: str | None = "20260808110000"


def upgrade() -> None:
    """Verify the candle versioning schema was applied before recording head."""
    bind = op.get_bind()
    column = bind.execute(
        text(
            """
            select column_name
            from information_schema.columns
            where table_schema = 'public'
              and table_name = 'candles'
              and column_name = 'superseded_by'
            """
        )
    ).scalar_one_or_none()
    if column is None:
        raise RuntimeError(
            "candles.superseded_by is missing; run the Supabase migration first"
        )
    index = bind.execute(
        text(
            """
            select indexname
            from pg_indexes
            where schemaname = 'public'
              and tablename = 'candles'
              and indexname = 'candles_active_open_time_idx'
            """
        )
    ).scalar_one_or_none()
    if index is None:
        raise RuntimeError("candles_active_open_time_idx is missing")


def downgrade() -> None:
    """Prevent destructive rollback of candle versioning."""
    raise RuntimeError(
        "M007 candle versioning is additive-only; create a forward migration instead"
    )
