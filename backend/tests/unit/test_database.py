from __future__ import annotations

from typing import Any, cast
from uuid import UUID

import pytest
from sqlalchemy.orm import sessionmaker

from app import database


class FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False
        self.executions: list[tuple[str, dict[str, object] | None]] = []

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True

    def execute(
        self, statement: object, parameters: dict[str, object] | None = None
    ) -> None:
        self.executions.append((str(statement), parameters))


def fake_factory(session: FakeSession) -> sessionmaker[Any]:
    return cast(sessionmaker[Any], lambda: session)


def test_database_url_defaults_and_allows_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert database.database_url() == database.DEFAULT_DATABASE_URL

    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    assert database.database_url() == "sqlite+pysqlite:///:memory:"


def test_build_engine_and_factory() -> None:
    engine = database.build_engine("sqlite+pysqlite:///:memory:")
    try:
        factory = database.build_session_factory(engine)
        with factory() as session:
            assert session.bind is engine
    finally:
        engine.dispose()


def test_transactional_session_commits_and_closes() -> None:
    fake = FakeSession()

    with database.transactional_session(fake_factory(fake)) as session:
        assert session is fake

    assert fake.committed
    assert not fake.rolled_back
    assert fake.closed


def test_transactional_session_rolls_back_and_closes() -> None:
    fake = FakeSession()

    with pytest.raises(RuntimeError, match="boom"):
        with database.transactional_session(fake_factory(fake)):
            raise RuntimeError("boom")

    assert not fake.committed
    assert fake.rolled_back
    assert fake.closed


def test_session_dependency_uses_transaction_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = FakeSession()
    monkeypatch.setattr(database, "get_session_factory", lambda: fake_factory(fake))

    dependency = database.session_dependency()
    assert next(dependency) is fake
    with pytest.raises(StopIteration):
        next(dependency)

    assert fake.committed
    assert fake.closed


def test_apply_request_context_uses_allowlist_and_bound_claims() -> None:
    fake = FakeSession()
    subject = UUID("00000000-0000-0000-0000-000000000101")

    database.apply_request_context(
        cast(Any, fake), role="authenticated", auth_subject=subject
    )

    assert fake.executions[0][0] == "set local role authenticated"
    assert fake.executions[1][1] == {"role": "authenticated"}
    assert fake.executions[2][1] == {"subject": str(subject)}

    with pytest.raises(ValueError, match="Unsupported database role"):
        database.apply_request_context(
            cast(Any, fake), role=cast(Any, "postgres"), auth_subject=None
        )
