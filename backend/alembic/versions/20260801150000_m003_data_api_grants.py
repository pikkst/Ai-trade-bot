"""M003 RLS-backed Data API compatibility head.

Revision ID: 20260801150000
Revises: 20260801144500
Create Date: 2026-08-01 15:00:00 UTC
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "20260801150000"
down_revision: str | None = "20260801144500"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None

_REQUIRED_VIEWS = (
    "public.current_user_profile",
    "public.workspace_overview",
    "public.current_workspace_memberships",
    "public.active_workspace_configuration",
    "public.workspace_audit_read",
    "public.market_candle_read",
    "public.portfolio_summary",
)


def upgrade() -> None:
    """Verify approved views and deny-by-default RLS before recording head."""
    bind = op.get_bind()
    missing_views = [
        view
        for view in _REQUIRED_VIEWS
        if bind.execute(text("select to_regclass(:view)"), {"view": view}).scalar_one()
        is None
    ]
    unprotected_tables = bind.execute(
        text(
            """
            select table_name
            from information_schema.tables table_info
            join pg_class relation on relation.relname = table_info.table_name
            join pg_namespace namespace on namespace.oid = relation.relnamespace
            where table_info.table_schema = 'public'
              and table_info.table_name = any(:table_names)
              and namespace.nspname = 'public'
              and (not relation.relrowsecurity or not relation.relforcerowsecurity)
            order by table_name
            """
        ),
        {
            "table_names": [
                "users",
                "workspaces",
                "workspace_memberships",
                "workspace_config_versions",
                "audit_events",
                "exchanges",
                "exchange_symbol_versions",
                "candles",
                "virtual_portfolios",
            ]
        },
    ).scalars()
    unprotected = list(unprotected_tables)
    failures: list[str] = []
    if missing_views:
        failures.append("missing views: " + ", ".join(missing_views))
    if unprotected:
        failures.append("RLS not forced: " + ", ".join(unprotected))
    if failures:
        raise RuntimeError("; ".join(failures))


def downgrade() -> None:
    """Prevent destructive rollback of security policy history."""
    raise RuntimeError(
        "M003 is additive-only; create a forward migration instead of downgrading"
    )