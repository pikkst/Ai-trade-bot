"""Supabase Auth subject mapping and workspace role enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    OPERATOR = "operator"
    VIEWER = "viewer"


@dataclass(frozen=True, slots=True)
class AuthContext:
    auth_subject: UUID
    user_id: UUID
    workspace_id: UUID
    role: WorkspaceRole


class AuthorizationError(RuntimeError):
    """Raised when an Auth subject has no active workspace authorization."""


def resolve_auth_context(
    session: Session,
    *,
    auth_subject: UUID,
    workspace_id: UUID,
) -> AuthContext:
    """Map one Supabase Auth subject to an active workspace membership."""
    row = (
        session.execute(
            text(
                """
                select app_user.id as user_id, membership.role
                from public.users app_user
                join public.workspace_memberships membership
                  on membership.user_id = app_user.id
                where app_user.auth_subject = :auth_subject
                  and app_user.account_state = 'active'
                  and membership.workspace_id = :workspace_id
                  and membership.state = 'active'
                  and (
                      membership.expires_at is null
                      or membership.expires_at > timezone('utc', now())
                  )
                """
            ),
            {
                "auth_subject": auth_subject,
                "workspace_id": workspace_id,
            },
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise AuthorizationError("No active membership for Auth subject and workspace")

    return AuthContext(
        auth_subject=auth_subject,
        user_id=UUID(str(row["user_id"])),
        workspace_id=workspace_id,
        role=WorkspaceRole(str(row["role"])),
    )


def require_role(context: AuthContext, *allowed: WorkspaceRole) -> None:
    """Fail closed unless the resolved role is explicitly allowed."""
    if context.role not in allowed:
        allowed_values = ", ".join(role.value for role in allowed)
        raise AuthorizationError(
            f"Role {context.role.value} is not allowed; expected one of: {allowed_values}"
        )
