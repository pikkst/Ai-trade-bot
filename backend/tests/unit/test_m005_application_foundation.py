from __future__ import annotations

from contextlib import nullcontext
from typing import Any, cast
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app import database
from app.errors import ValidationAppError, install_error_handlers
from app.health import liveness, readiness
from app.idempotency import (
    IdempotencyReservation,
    complete_idempotency,
    request_fingerprint,
    reserve_idempotency,
    update_with_expected_version,
)
from app.main import create_app
from app.observability import redact_value
from app.request_context import bind_context, current_context
from app.settings import AppSettings, SettingsError, load_settings
from app.transaction_guard import assert_network_call_allowed, transaction_active


class FakeTransactionSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


def _fake_factory(session: FakeTransactionSession) -> sessionmaker[Any]:
    return cast(sessionmaker[Any], lambda: session)


class FakeMappings:
    def __init__(self, row: dict[str, Any] | None) -> None:
        self.row = row

    def one_or_none(self) -> dict[str, Any] | None:
        return self.row

    def one(self) -> dict[str, Any]:
        assert self.row is not None
        return self.row


class FakeResult:
    def __init__(
        self,
        *,
        row: dict[str, Any] | None = None,
        scalar: int | None = None,
    ) -> None:
        self.row = row
        self.scalar = scalar

    def mappings(self) -> FakeMappings:
        return FakeMappings(self.row)

    def scalar_one_or_none(self) -> int | None:
        return self.scalar


class FakeIdempotencySession:
    def __init__(self, results: list[FakeResult]) -> None:
        self.results = results
        self.executions: list[tuple[str, dict[str, Any] | None]] = []

    def execute(
        self,
        statement: object,
        parameters: dict[str, Any] | None = None,
    ) -> FakeResult:
        self.executions.append((str(statement), parameters))
        return self.results.pop(0)


class ReadySession:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    def __enter__(self) -> ReadySession:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, _statement: object) -> None:
        if self.fail:
            raise RuntimeError("database unavailable")


def test_settings_defaults_are_safe_and_do_not_expose_database_url() -> None:
    settings = load_settings({})

    assert settings.environment == "local"
    assert settings.ai_provider == "fake"
    assert settings.live_trading_enabled is False
    assert "database_url" not in settings.safe_summary()


def test_settings_use_canonical_environment_names() -> None:
    settings = load_settings(
        {
            "APP_ENV": "development",
            "APP_LOG_LEVEL": "DEBUG",
            "AI_PROVIDER": "fake",
            "GEMINI_ENABLED": "false",
            "PRIVATE_BINANCE_API_ENABLED": "0",
        }
    )

    assert settings.environment == "development"
    assert settings.log_level == "DEBUG"


@pytest.mark.parametrize(
    "name",
    [
        "LIVE_TRADING_ENABLED",
        "BINANCE_TEST_TRADING_ENABLED",
        "PRIVATE_BINANCE_API_ENABLED",
        "EXCHANGE_ORDER_EXECUTION_ENABLED",
    ],
)
def test_settings_reject_prohibited_trading_capabilities(name: str) -> None:
    with pytest.raises(SettingsError, match="paper-only MVP prohibits"):
        load_settings({name: "true"})


def test_settings_reject_paid_provider_in_ci_and_invalid_boolean() -> None:
    with pytest.raises(SettingsError, match="fake AI provider"):
        load_settings(
            {
                "APP_ENV": "ci",
                "AI_PROVIDER": "gemini",
                "GEMINI_ENABLED": "true",
                "ALLOW_PAID_PROVIDER_USAGE": "true",
            }
        )

    with pytest.raises(SettingsError, match="must be one of"):
        load_settings({"LIVE_TRADING_ENABLED": "definitely"})


def test_settings_validation_does_not_echo_database_secret() -> None:
    secret = "postgresql://user:super-secret@example.invalid/db"
    with pytest.raises(SettingsError) as caught:
        load_settings(
            {
                "APP_ENV": "invalid",
                "DATABASE_URL": secret,
            }
        )

    assert "super-secret" not in str(caught.value)


def test_context_binding_and_redaction() -> None:
    with bind_context(
        correlation_id="corr-1",
        request_id="req-1",
        job_id="job-1",
        cycle_id="cycle-1",
    ):
        assert current_context().as_dict() == {
            "correlation_id": "corr-1",
            "request_id": "req-1",
            "job_id": "job-1",
            "cycle_id": "cycle-1",
        }

    redacted = redact_value(
        {
            "password": "hidden",
            "sessionId": "operational-id",
            "message": "Bearer abc.def and postgresql://u:p@example.invalid/db",
        }
    )
    assert redacted["password"] == "[REDACTED]"
    assert redacted["sessionId"] == "operational-id"
    assert "abc.def" not in redacted["message"]
    assert "u:p@" not in redacted["message"]


def test_http_context_health_and_safe_error_envelope() -> None:
    app = create_app(AppSettings())

    @app.get("/validation-error")
    def validation_error() -> None:
        raise ValidationAppError("internal detail must not leak")

    client = TestClient(app)
    response = client.get(
        "/health/live",
        headers={"X-Correlation-ID": "corr-test", "X-Request-ID": "req-test"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"process": "ok"}}
    assert response.headers["X-Correlation-ID"] == "corr-test"
    assert response.headers["X-Request-ID"] == "req-test"

    ready_response = client.get("/health/ready")
    assert ready_response.status_code == 200
    assert ready_response.json()["checks"]["database"] == "not_required"

    error_response = client.get(
        "/validation-error", headers={"X-Correlation-ID": "corr-error"}
    )
    assert error_response.status_code == 400
    body = error_response.json()["error"]
    assert body["code"] == "validation_error"
    assert body["message"] == "The request is invalid."
    assert body["correlation_id"] == "corr-error"
    assert "internal detail" not in error_response.text


def test_invalid_correlation_header_is_replaced() -> None:
    client = TestClient(create_app(AppSettings(max_request_id_length=16)))
    response = client.get("/health", headers={"X-Correlation-ID": "bad id spaces"})

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] != "bad id spaces"
    assert len(response.headers["X-Correlation-ID"]) == 32


def test_unexpected_error_uses_safe_envelope() -> None:
    app = FastAPI()
    install_error_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("database password=secret")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/boom")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "application_error"
    assert "secret" not in response.text


def test_transaction_guard_blocks_network_calls_and_resets() -> None:
    fake = FakeTransactionSession()
    assert transaction_active() is False

    with database.transactional_session(_fake_factory(fake)):
        assert transaction_active() is True
        with pytest.raises(RuntimeError, match="network calls are prohibited"):
            assert_network_call_allowed()

    assert transaction_active() is False
    assert fake.committed is True
    assert fake.closed is True


def test_health_readiness_success_and_failure() -> None:
    assert liveness().status == "ok"

    good_factory = cast(
        sessionmaker[Any],
        lambda: ReadySession(),
    )
    bad_factory = cast(
        sessionmaker[Any],
        lambda: ReadySession(fail=True),
    )

    assert readiness(check_database=True, factory=good_factory).status == "ready"
    result = readiness(check_database=True, factory=bad_factory)
    assert result.status == "not_ready"
    assert result.checks["database"] == "unavailable"

    with pytest.raises(ValueError, match="session factory"):
        readiness(check_database=True, factory=None)


def test_request_fingerprint_is_canonical() -> None:
    first = request_fingerprint({"b": 2, "a": 1})
    second = request_fingerprint({"a": 1, "b": 2})

    assert first == second
    assert len(first) == 64


def test_idempotency_reservation_duplicate_and_conflict() -> None:
    workspace_id = UUID("00000000-0000-0000-0000-000000000101")
    fingerprint = request_fingerprint({"command": "run"})
    inserted = FakeIdempotencySession(
        [FakeResult(row={"request_hash": fingerprint, "response_status": None, "response_body": None})]
    )
    created = reserve_idempotency(
        cast(Any, inserted),
        workspace_id=workspace_id,
        scope="research-cycle",
        key="cycle-1",
        request_hash=fingerprint,
    )
    assert created.created is True

    replay = FakeIdempotencySession(
        [
            FakeResult(row=None),
            FakeResult(
                row={
                    "request_hash": fingerprint,
                    "response_status": 200,
                    "response_body": {"cycle_id": "existing"},
                }
            ),
        ]
    )
    existing = reserve_idempotency(
        cast(Any, replay),
        workspace_id=workspace_id,
        scope="research-cycle",
        key="cycle-1",
        request_hash=fingerprint,
    )
    assert existing.created is False
    assert existing.response_body == {"cycle_id": "existing"}

    conflict = FakeIdempotencySession(
        [
            FakeResult(row=None),
            FakeResult(
                row={
                    "request_hash": "0" * 64,
                    "response_status": None,
                    "response_body": None,
                }
            ),
        ]
    )
    with pytest.raises(Exception, match="idempotency"):
        reserve_idempotency(
            cast(Any, conflict),
            workspace_id=workspace_id,
            scope="research-cycle",
            key="cycle-1",
            request_hash=fingerprint,
        )


def test_complete_idempotency_and_expected_version() -> None:
    workspace_id = UUID("00000000-0000-0000-0000-000000000101")
    reservation = IdempotencyReservation(
        workspace_id=workspace_id,
        scope="command",
        key="key-1",
        request_hash="a" * 64,
        created=True,
    )
    completion_session = FakeIdempotencySession([FakeResult()])
    complete_idempotency(
        cast(Any, completion_session),
        reservation,
        response_status=200,
        response_body={"ok": True},
    )
    assert "public.idempotency_records" in completion_session.executions[0][0]

    update_session = FakeIdempotencySession([FakeResult(scalar=4)])
    new_version = update_with_expected_version(
        cast(Any, update_session),
        table="workspaces",
        row_id=workspace_id,
        expected_version=3,
        values={"name": "Updated"},
    )
    assert new_version == 4

    conflict_session = FakeIdempotencySession([FakeResult(scalar=None)])
    with pytest.raises(Exception, match="resource changed"):
        update_with_expected_version(
            cast(Any, conflict_session),
            table="workspaces",
            row_id=workspace_id,
            expected_version=3,
            values={"name": "Updated"},
        )

    with pytest.raises(ValueError, match="unsupported"):
        update_with_expected_version(
            cast(Any, update_session),
            table="unsafe_table",
            row_id=workspace_id,
            expected_version=1,
            values={"name": "x"},
        )
