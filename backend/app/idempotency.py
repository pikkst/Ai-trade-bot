"""Durable idempotency and optimistic-concurrency primitives."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import TextClause, text
from sqlalchemy.orm import Session

from app.errors import ConcurrencyConflictError, IdempotencyConflictError


@dataclass(frozen=True, slots=True)
class IdempotencyReservation:
    workspace_id: UUID
    scope: str
    key: str
    request_hash: str
    created: bool
    response_status: int | None = None
    response_body: dict[str, Any] | None = None


_CONCURRENCY_STATEMENTS: dict[tuple[str, frozenset[str]], TextClause] = {
    ("workspaces", frozenset({"name"})): text(
        """
        update public.workspaces
        set name = :value_name, version = version + 1
        where id = :row_id and version = :expected_version
        returning version
        """
    ),
    ("workspaces", frozenset({"lifecycle_state"})): text(
        """
        update public.workspaces
        set lifecycle_state = :value_lifecycle_state, version = version + 1
        where id = :row_id and version = :expected_version
        returning version
        """
    ),
    ("workspaces", frozenset({"name", "lifecycle_state"})): text(
        """
        update public.workspaces
        set name = :value_name,
            lifecycle_state = :value_lifecycle_state,
            version = version + 1
        where id = :row_id and version = :expected_version
        returning version
        """
    ),
    ("virtual_portfolios", frozenset({"name"})): text(
        """
        update public.virtual_portfolios
        set name = :value_name, version = version + 1
        where id = :row_id and version = :expected_version
        returning version
        """
    ),
    ("virtual_portfolios", frozenset({"lifecycle_state"})): text(
        """
        update public.virtual_portfolios
        set lifecycle_state = :value_lifecycle_state, version = version + 1
        where id = :row_id and version = :expected_version
        returning version
        """
    ),
    ("virtual_portfolios", frozenset({"name", "lifecycle_state"})): text(
        """
        update public.virtual_portfolios
        set name = :value_name,
            lifecycle_state = :value_lifecycle_state,
            version = version + 1
        where id = :row_id and version = :expected_version
        returning version
        """
    ),
}


def request_fingerprint(payload: Any) -> str:
    """Hash a canonical JSON representation."""
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def reserve_idempotency(
    session: Session,
    *,
    workspace_id: UUID,
    scope: str,
    key: str,
    request_hash: str,
) -> IdempotencyReservation:
    """Reserve a durable key or return the matching prior reservation."""
    if not key.strip() or len(key) > 200:
        raise ValueError(
            "idempotency key must contain 1..200 non-whitespace characters"
        )
    if not scope.strip() or len(scope) > 100:
        raise ValueError(
            "idempotency scope must contain 1..100 non-whitespace characters"
        )

    inserted = (
        session.execute(
            text(
                """
                insert into public.idempotency_records (
                    workspace_id, scope, idempotency_key, request_hash
                ) values (:workspace_id, :scope, :key, :request_hash)
                on conflict (workspace_id, scope, idempotency_key) do nothing
                returning request_hash, response_status, response_body
                """
            ),
            {
                "workspace_id": workspace_id,
                "scope": scope,
                "key": key,
                "request_hash": request_hash,
            },
        )
        .mappings()
        .one_or_none()
    )
    if inserted is not None:
        return IdempotencyReservation(
            workspace_id=workspace_id,
            scope=scope,
            key=key,
            request_hash=request_hash,
            created=True,
        )

    existing = (
        session.execute(
            text(
                """
                select request_hash, response_status, response_body
                from public.idempotency_records
                where workspace_id = :workspace_id
                  and scope = :scope
                  and idempotency_key = :key
                for update
                """
            ),
            {
                "workspace_id": workspace_id,
                "scope": scope,
                "key": key,
            },
        )
        .mappings()
        .one()
    )
    if existing["request_hash"] != request_hash:
        raise IdempotencyConflictError()
    return IdempotencyReservation(
        workspace_id=workspace_id,
        scope=scope,
        key=key,
        request_hash=request_hash,
        created=False,
        response_status=existing["response_status"],
        response_body=existing["response_body"],
    )


def complete_idempotency(
    session: Session,
    reservation: IdempotencyReservation,
    *,
    response_status: int,
    response_body: dict[str, Any],
) -> None:
    """Persist a replayable result in the transaction owning its effects."""
    session.execute(
        text(
            """
            update public.idempotency_records
            set response_status = :status,
                response_body = cast(:body as jsonb),
                completed_at = timezone('utc', now())
            where workspace_id = :workspace_id
              and scope = :scope
              and idempotency_key = :key
              and request_hash = :request_hash
            """
        ),
        {
            "workspace_id": reservation.workspace_id,
            "scope": reservation.scope,
            "key": reservation.key,
            "request_hash": reservation.request_hash,
            "status": response_status,
            "body": json.dumps(
                response_body,
                sort_keys=True,
                separators=(",", ":"),
            ),
        },
    )


def update_with_expected_version(
    session: Session,
    *,
    table: str,
    row_id: UUID,
    expected_version: int,
    values: dict[str, Any],
) -> int:
    """Apply a closed-set optimistic update and return the next version."""
    statement = _CONCURRENCY_STATEMENTS.get((table, frozenset(values)))
    if statement is None:
        raise ValueError("unsupported optimistic-concurrency target")

    parameters = {f"value_{column}": value for column, value in values.items()}
    parameters.update({"row_id": row_id, "expected_version": expected_version})
    result = session.execute(statement, parameters).scalar_one_or_none()
    if result is None:
        raise ConcurrencyConflictError()
    return int(result)
