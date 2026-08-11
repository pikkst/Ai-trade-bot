"""M007 evidence idempotency and durable resume compatibility head.

Revision ID: 20260808130000
Revises: 20260808120000
Create Date: 2026-08-08 13:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260808130000"
down_revision: str | None = "20260808120000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the evidence-idempotency schema was applied before recording head."""
    bind = op.get_bind()
    column = bind.execute(
        text(
            """
            select column_name
            from information_schema.columns
            where table_schema = 'public'
              and table_name = 'market_data_ingestions'
              and column_name = 'page_hashes'
            """
        )
    ).scalar_one_or_none()
    if column is None:
        raise RuntimeError(
            "market_data_ingestions.page_hashes is missing; "
            "run the Supabase migration first"
        )
    index = bind.execute(
        text(
            """
            select indexname
            from pg_indexes
            where schemaname = 'public'
              and tablename = 'market_snapshots'
              and indexname = 'market_snapshots_hash_uniq'
            """
        )
    ).scalar_one_or_none()
    if index is None:
        raise RuntimeError("market_snapshots_hash_uniq is missing")


def downgrade() -> None:
    """Prevent destructive rollback of evidence idempotency."""
    raise RuntimeError(
        "M007 evidence idempotency is additive-only; create a forward migration instead"
    )
