"""M003 workflow/service/migration role compatibility head.

Revision ID: 20260801151000
Revises: 20260801150000
Create Date: 2026-08-01 15:10:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260801151000"
down_revision: str | None = "20260801150000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify that the workflow role has an explicit audit read policy."""
    bind = op.get_bind()
    policy_exists = bind.execute(
        text(
            """
            select exists (
                select 1
                from pg_policies
                where schemaname = 'public'
                  and tablename = 'audit_events'
                  and policyname = 'workflow_audit_read'
                  and 'app_workflow' = any(roles)
            )
            """
        )
    ).scalar_one()
    if not policy_exists:
        raise RuntimeError("Missing workflow_audit_read RLS policy")


def downgrade() -> None:
    """Prevent destructive rollback of security policy history."""
    raise RuntimeError(
        "M003 is additive-only; create a forward migration instead of downgrading"
    )
