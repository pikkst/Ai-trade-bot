"""M003 local administrator role-membership compatibility head.

Revision ID: 20260801170000
Revises: 20260801151000
Create Date: 2026-08-01 17:00:00 UTC
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "20260801170000"
down_revision: str | None = "20260801151000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the narrow trusted-role graph used by local M003 checks."""
    bind = op.get_bind()
    expected_attributes = {
        "app_workflow": (False, False, False),
        "app_migration": (False, False, True),
    }
    failures: list[str] = []
    for role, expected in expected_attributes.items():
        attributes = bind.execute(
            text(
                """
                select rolcanlogin, rolinherit, rolbypassrls
                from pg_roles
                where rolname = :role
                """
            ),
            {"role": role},
        ).one_or_none()
        members = list(
            bind.execute(
                text(
                    """
                    select pg_get_userbyid(member)
                    from pg_auth_members
                    where roleid = (select oid from pg_roles where rolname = :role)
                    order by 1
                    """
                ),
                {"role": role},
            ).scalars()
        )
        if attributes != expected:
            failures.append(f"{role} attributes differ from {expected}")
        if members != ["postgres"]:
            failures.append(f"{role} members differ from ['postgres']")
    if failures:
        raise RuntimeError("Invalid trusted-role graph: " + "; ".join(failures))


def downgrade() -> None:
    """Prevent destructive rollback of security role history."""
    raise RuntimeError(
        "M003 is additive-only; create a forward migration instead of downgrading"
    )
