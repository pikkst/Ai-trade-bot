"""M007 quality-gate fixes compatibility head.

Revision ID: 20260808140000
Revises: 20260808130000
Create Date: 2026-08-08 14:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260808140000"
down_revision: str | None = "20260808130000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the quality-gate schema was applied before recording head."""
    bind = op.get_bind()
    policy = bind.execute(
        text(
            """
            select policyname
            from pg_policies
            where schemaname = 'public'
              and tablename = 'market_snapshots'
              and policyname = 'authenticated_snapshots_select'
            """
        )
    ).scalar_one_or_none()
    if policy is None:
        raise RuntimeError(
            "authenticated_snapshots_select policy is missing; "
            "run the Supabase migration first"
        )


def downgrade() -> None:
    """Prevent destructive rollback of quality-gate fixes."""
    raise RuntimeError(
        "M007 quality-gate fixes are additive-only; create a forward migration instead"
    )
