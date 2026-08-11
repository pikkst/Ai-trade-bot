"""M007 market-data quality and snapshot schema compatibility head.

Revision ID: 20260808110000
Revises: 20260801170000
Create Date: 2026-08-08 11:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260808110000"
down_revision: str | None = "20260801170000"
branch_labels: tuple[str, ...] | None = ("m007",)
depends_on: tuple[str, ...] | None = None

_REQUIRED_TABLES = (
    "public.market_data_ingestions",
    "public.data_quality_events",
    "public.candle_corrections",
    "public.market_snapshots",
    "public.market_snapshot_candles",
)

_REQUIRED_VIEWS = (
    "public.market_snapshot_read",
    "public.data_quality_event_read",
)


def upgrade() -> None:
    """Verify M007 tables and views exist before recording Alembic head."""
    bind = op.get_bind()
    missing_tables = [
        table
        for table in _REQUIRED_TABLES
        if bind.execute(
            text("select to_regclass(:table)"), {"table": table}
        ).scalar_one()
        is None
    ]
    missing_views = [
        view
        for view in _REQUIRED_VIEWS
        if bind.execute(text("select to_regclass(:view)"), {"view": view}).scalar_one()
        is None
    ]
    if missing_tables or missing_views:
        parts = []
        if missing_tables:
            parts.append("missing tables: " + ", ".join(missing_tables))
        if missing_views:
            parts.append("missing views: " + ", ".join(missing_views))
        raise RuntimeError("; ".join(parts))


def downgrade() -> None:
    """Prevent destructive rollback of market-data quality evidence."""
    raise RuntimeError(
        "M007 is additive-only; create a forward migration instead of downgrading"
    )
