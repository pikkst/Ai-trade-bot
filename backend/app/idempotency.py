"""Durable idempotency and optimistic-concurrency primitives."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import text
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


def request_fingerprint(payload: Any) -> str:
    """Hash a canonical JSON representation without depending on object identity."""
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
    """Reserve a durable key or return the matching previous reservation."""
    if not key.strip() or len(key) > 200:
        raise ValueError("idempotency key must contain 1..200 non-whitespace characters")
    if not scope.strip() or len(scope) > 100:
        raise ValueError("idempotency scope must contain 1..100 non-whitespace characters")

    inserted = session.execute(
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
    ).mappings().one_or_none()
    if inserted is not None:
        return IdempotencyReservation(
            workspace_id=workspace_id,
            scope=scope,
            key=key,
            request_hash=request_hash,
            created=True,
        )

    existing = session.execute(
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
        {"workspace_id": workspace_id, "scope": scope, "key": key},
    ).mappings().one()
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
    """Persist the replayable command result in the same transaction as effects."""
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
            "body": json.dumps(response_body, sort_keys=True, separators=(",", ":")),
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
    """Apply an allowlisted optimistic update and return the next version."""
    allowed_tables: dict[str, set[str]] = {
        "workspaces": {"name", "lifecycle_state"},
        "virtual_portfolios": {"name", "lifecycle_state"},
    }
    allowed_columns = allowed_tables.get(table)
    if allowed_columns is None or not values or not set(values).issubset(allowed_columns):
        raise ValueError("unsupported optimistic-concurrency target")
    assignments = ", ".join(f"{column} = :value_{column}" for column in sorted(values))
    parameters = {f"value_{column}": value for column, value in values.items()}
    parameters.update({"row_id": row_id, "expected_version": expected_version})
    result = session.execute(
        text(
            f"update public.{table} set {assignments}, version = version + 1 "
            "where id = :row_id and version = :expected_version returning version"
        ),
        parameters,
    ).scalar_one_or_none()
    if result is None:
        raise ConcurrencyConflictError()
    return int(result)
