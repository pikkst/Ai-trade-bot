from __future__ import annotations

from typing import Any, cast
from uuid import UUID

import pytest

from app.authorization import (
    AuthContext,
    AuthorizationError,
    WorkspaceRole,
    require_role,
    resolve_auth_context,
)


class FakeMappings:
    def __init__(self, row: dict[str, object] | None) -> None:
        self.row = row

    def one_or_none(self) -> dict[str, object] | None:
        return self.row


class FakeResult:
    def __init__(self, row: dict[str, object] | None) -> None:
        self.row = row

    def mappings(self) -> FakeMappings:
        return FakeMappings(self.row)


class FakeSession:
    def __init__(self, row: dict[str, object] | None) -> None:
        self.row = row
        self.parameters: dict[str, object] | None = None

    def execute(
        self, statement: object, parameters: dict[str, object]
    ) -> FakeResult:
        assert "workspace_memberships" in str(statement)
        self.parameters = parameters
        return FakeResult(self.row)


def test_resolve_auth_context_maps_subject_and_role() -> None:
    auth_subject = UUID("00000000-0000-0000-0000-000000000101")
    user_id = UUID("10000000-0000-0000-0000-000000000101")
    workspace_id = UUID("20000000-0000-0000-0000-000000000001")
    session = FakeSession({"user_id": user_id, "role": "owner"})

    context = resolve_auth_context(
        cast(Any, session),
        auth_subject=auth_subject,
        workspace_id=workspace_id,
    )

    assert context == AuthContext(
        auth_subject=auth_subject,
        user_id=user_id,
        workspace_id=workspace_id,
        role=WorkspaceRole.OWNER,
    )
    assert session.parameters == {
        "auth_subject": auth_subject,
        "workspace_id": workspace_id,
    }


def test_resolve_auth_context_fails_closed() -> None:
    session = FakeSession(None)

    with pytest.raises(AuthorizationError, match="No active membership"):
        resolve_auth_context(
            cast(Any, session),
            auth_subject=UUID("00000000-0000-0000-0000-000000000999"),
            workspace_id=UUID("20000000-0000-0000-0000-000000000001"),
        )


def test_require_role_accepts_explicit_role_and_rejects_others() -> None:
    context = AuthContext(
        auth_subject=UUID("00000000-0000-0000-0000-000000000103"),
        user_id=UUID("10000000-0000-0000-0000-000000000103"),
        workspace_id=UUID("20000000-0000-0000-0000-000000000001"),
        role=WorkspaceRole.VIEWER,
    )

    require_role(context, WorkspaceRole.VIEWER)

    with pytest.raises(AuthorizationError, match="expected one of: owner, operator"):
        require_role(context, WorkspaceRole.OWNER, WorkspaceRole.OPERATOR)
