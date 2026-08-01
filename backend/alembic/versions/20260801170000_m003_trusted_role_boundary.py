"""M003 trusted-role boundary compatibility head.

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
    """Verify trusted attributes without prescribing deployment principals."""
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
        prohibited_members = list(
            bind.execute(
                text(
                    """
                    select member_role.rolname
                    from pg_auth_members membership
                    join pg_roles trusted_role
                      on trusted_role.oid = membership.roleid
                    join pg_roles member_role
                      on member_role.oid = membership.member
                    where trusted_role.rolname = :role
                      and member_role.rolname in (
                          'anon',
                          'authenticated',
                          'service_role',
                          'app_runtime'
                      )
                    order by member_role.rolname
                    """
                ),
                {"role": role},
            ).scalars()
        )
        if attributes != expected:
            failures.append(f"{role} attributes differ from {expected}")
        if prohibited_members:
            failures.append(
                f"{role} has prohibited runtime/browser members: "
                f"{prohibited_members}"
            )
    if failures:
        raise RuntimeError("Invalid trusted-role graph: " + "; ".join(failures))


def downgrade() -> None:
    """Prevent destructive rollback of trusted-role security history."""
    raise RuntimeError(
        "M003 is additive-only; create a forward migration instead of downgrading"
    )
