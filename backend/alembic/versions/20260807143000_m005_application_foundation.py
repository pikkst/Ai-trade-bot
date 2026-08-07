"""M005 application-foundation compatibility head.

Revision ID: 20260807143000
Revises: 20260801170000
Create Date: 2026-08-07 14:30:00 UTC
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "20260807143000"
down_revision: str | None = "20260801170000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the durable idempotency table and its fail-closed RLS boundary."""
    bind = op.get_bind()
    exists = bind.execute(
        text("select to_regclass('public.idempotency_records')")
    ).scalar_one()
    if exists is None:
        raise RuntimeError(
            "M005 requires Supabase migration 20260807143000_m005_application_foundation"
        )

    rls = bind.execute(
        text(
            """
            select relrowsecurity, relforcerowsecurity
            from pg_class relation
            join pg_namespace namespace on namespace.oid = relation.relnamespace
            where namespace.nspname = 'public'
              and relation.relname = 'idempotency_records'
            """
        )
    ).one()
    if rls != (True, True):
        raise RuntimeError("public.idempotency_records must enable and force RLS")

    browser_privileges = bind.execute(
        text(
            """
            select count(*)
            from information_schema.role_table_grants
            where table_schema = 'public'
              and table_name = 'idempotency_records'
              and grantee in ('anon', 'authenticated')
            """
        )
    ).scalar_one()
    if browser_privileges:
        raise RuntimeError("browser roles must not access idempotency records directly")


def downgrade() -> None:
    """Prevent destructive rollback of durable command evidence."""
    raise RuntimeError(
        "M005 is additive-only; create a forward migration instead of downgrading"
    )
