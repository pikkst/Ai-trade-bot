from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID

import pytest
from alembic.config import Config
from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import DBAPIError

from alembic import command
from app.authorization import WorkspaceRole, resolve_auth_context
from app.database import (
    apply_request_context,
    build_engine,
    build_session_factory,
    transactional_session,
)

pytestmark = pytest.mark.database

OWNER_SUBJECT = UUID("00000000-0000-0000-0000-000000000101")
OPERATOR_SUBJECT = UUID("00000000-0000-0000-0000-000000000102")
VIEWER_SUBJECT = UUID("00000000-0000-0000-0000-000000000103")
WORKSPACE_ID = UUID("20000000-0000-0000-0000-000000000001")


@pytest.fixture(scope="module")
def database_engine() -> Iterator[Engine]:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for local Supabase tests")
    engine = build_engine(url)
    with engine.connect() as connection:
        connection.execute(text("select 1"))
    yield engine
    engine.dispose()


@contextmanager
def role_connection(
    engine: Engine,
    *,
    role: str,
    auth_subject: UUID | None,
) -> Iterator[Connection]:
    with engine.connect() as connection, connection.begin():
        connection.exec_driver_sql(f"set local role {role}")
        connection.execute(
            text("select set_config('request.jwt.claim.role', :role, true)"),
            {"role": role},
        )
        connection.execute(
            text("select set_config('request.jwt.claim.sub', :subject, true)"),
            {"subject": "" if auth_subject is None else str(auth_subject)},
        )
        yield connection


def test_supabase_migrations_seed_and_alembic_head(database_engine: Engine) -> None:
    with database_engine.connect() as connection:
        migration_count = connection.execute(
            text(
                """
                select count(*)
                from supabase_migrations.schema_migrations
                where version in (
                    '20260801144500',
                    '20260801150000',
                    '20260801151000'
                )
                """
            )
        ).scalar_one()
        assert migration_count == 3
        assert (
            connection.execute(text("select count(*) from public.users")).scalar_one()
            == 3
        )
        assert (
            connection.execute(
                text("select count(*) from public.workspaces")
            ).scalar_one()
            == 1
        )
        assert (
            connection.execute(text("select count(*) from public.candles")).scalar_one()
            == 2
        )
        assert (
            connection.execute(
                text("select cash_balance from public.virtual_portfolios")
            ).scalar_one()
            == 10000
        )

    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", os.environ["TEST_DATABASE_URL"])
    command.upgrade(config, "head")

    with database_engine.connect() as connection:
        assert (
            connection.execute(
                text("select version_num from private.alembic_version")
            ).scalar_one()
            == "20260801151000"
        )


@pytest.mark.parametrize(
    (
        "role",
        "subject",
        "workspace_count",
        "audit_count",
        "membership_count",
        "profile_count",
    ),
    [
        ("authenticated", VIEWER_SUBJECT, 1, 0, 1, 1),
        ("authenticated", OPERATOR_SUBJECT, 1, 1, 1, 1),
        ("authenticated", OWNER_SUBJECT, 1, 1, 3, 1),
        ("app_workflow", None, 1, 1, 3, 3),
        ("service_role", None, 1, 1, 3, 3),
        ("app_migration", None, 1, 1, 3, 3),
    ],
)
def test_rls_role_matrix(
    database_engine: Engine,
    role: str,
    subject: UUID | None,
    workspace_count: int,
    audit_count: int,
    membership_count: int,
    profile_count: int,
) -> None:
    with role_connection(
        database_engine, role=role, auth_subject=subject
    ) as connection:
        assert (
            connection.execute(
                text("select count(*) from public.workspace_overview")
            ).scalar_one()
            == workspace_count
        )
        assert (
            connection.execute(
                text("select count(*) from public.workspace_audit_read")
            ).scalar_one()
            == audit_count
        )
        assert (
            connection.execute(
                text("select count(*) from public.current_workspace_memberships")
            ).scalar_one()
            == membership_count
        )
        assert (
            connection.execute(
                text("select count(*) from public.current_user_profile")
            ).scalar_one()
            == profile_count
        )


def test_anonymous_role_is_denied(database_engine: Engine) -> None:
    with (
        pytest.raises(DBAPIError),
        role_connection(database_engine, role="anon", auth_subject=None) as connection,
    ):
        connection.execute(text("select * from public.workspace_overview")).all()


@pytest.mark.parametrize("subject", [OWNER_SUBJECT, OPERATOR_SUBJECT, VIEWER_SUBJECT])
def test_browser_roles_cannot_write_financial_state(
    database_engine: Engine, subject: UUID
) -> None:
    with (
        pytest.raises(DBAPIError),
        role_connection(
            database_engine, role="authenticated", auth_subject=subject
        ) as connection,
    ):
        connection.execute(
            text(
                """
                insert into public.virtual_portfolios (
                    id, workspace_id, name, base_currency, cash_balance
                ) values (
                    '50000000-0000-0000-0000-000000000999',
                    :workspace_id,
                    'Forbidden Browser Portfolio',
                    'EUR',
                    1
                )
                """
            ),
            {"workspace_id": WORKSPACE_ID},
        )


def test_workspace_isolation(database_engine: Engine) -> None:
    isolated_workspace = UUID("20000000-0000-0000-0000-000000000999")
    with database_engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.exec_driver_sql("set local role app_migration")
            connection.execute(
                text(
                    """
                    insert into public.workspaces (
                        id, name, base_currency, lifecycle_state
                    ) values (:id, 'Isolated Workspace', 'EUR', 'active')
                    """
                ),
                {"id": isolated_workspace},
            )
            connection.execute(
                text(
                    """
                    insert into public.virtual_portfolios (
                        id, workspace_id, name, base_currency, cash_balance
                    ) values (
                        '50000000-0000-0000-0000-000000000998',
                        :workspace_id,
                        'Isolated Portfolio',
                        'EUR',
                        500
                    )
                    """
                ),
                {"workspace_id": isolated_workspace},
            )

            connection.exec_driver_sql("set local role authenticated")
            connection.execute(
                text(
                    "select set_config('request.jwt.claim.role', 'authenticated', true)"
                )
            )
            connection.execute(
                text("select set_config('request.jwt.claim.sub', :subject, true)"),
                {"subject": str(OWNER_SUBJECT)},
            )

            workspace_ids = set(
                connection.execute(
                    text("select id from public.workspace_overview")
                ).scalars()
            )
            portfolio_workspace_ids = set(
                connection.execute(
                    text("select workspace_id from public.portfolio_summary")
                ).scalars()
            )
            assert workspace_ids == {WORKSPACE_ID}
            assert portfolio_workspace_ids == {WORKSPACE_ID}
        finally:
            transaction.rollback()


def test_transaction_commit_and_rollback(database_engine: Engine) -> None:
    committed_id = UUID("60000000-0000-0000-0000-000000000901")
    rolled_back_id = UUID("60000000-0000-0000-0000-000000000902")
    factory = build_session_factory(database_engine)

    with database_engine.begin() as connection:
        connection.execute(
            text(
                "delete from public.audit_events where id in (:committed, :rolled_back)"
            ),
            {"committed": committed_id, "rolled_back": rolled_back_id},
        )

    with transactional_session(factory) as session:
        apply_request_context(session, role="app_workflow", auth_subject=None)
        session.execute(
            text(
                """
                insert into public.audit_events (
                    id, workspace_id, actor_kind, action, resource_type, reason
                ) values (
                    :id, :workspace_id, 'workflow', 'commit_test', 'test', 'M003'
                )
                """
            ),
            {"id": committed_id, "workspace_id": WORKSPACE_ID},
        )

    with (
        pytest.raises(RuntimeError, match="rollback test"),
        transactional_session(factory) as session,
    ):
        apply_request_context(session, role="app_workflow", auth_subject=None)
        session.execute(
            text(
                """
                insert into public.audit_events (
                    id, workspace_id, actor_kind, action, resource_type, reason
                ) values (
                    :id, :workspace_id, 'workflow', 'rollback_test', 'test', 'M003'
                )
                """
            ),
            {"id": rolled_back_id, "workspace_id": WORKSPACE_ID},
        )
        raise RuntimeError("rollback test")

    with database_engine.begin() as connection:
        assert (
            connection.execute(
                text("select count(*) from public.audit_events where id = :id"),
                {"id": committed_id},
            ).scalar_one()
            == 1
        )
        assert (
            connection.execute(
                text("select count(*) from public.audit_events where id = :id"),
                {"id": rolled_back_id},
            ).scalar_one()
            == 0
        )
        connection.execute(
            text("delete from public.audit_events where id = :id"),
            {"id": committed_id},
        )


def test_real_auth_subject_mapping(database_engine: Engine) -> None:
    factory = build_session_factory(database_engine)
    with factory() as session:
        context = resolve_auth_context(
            session,
            auth_subject=OPERATOR_SUBJECT,
            workspace_id=WORKSPACE_ID,
        )
    assert context.role is WorkspaceRole.OPERATOR
    assert context.workspace_id == WORKSPACE_ID


def test_every_public_table_forces_rls_and_views_hide_raw_config(
    database_engine: Engine,
) -> None:
    with database_engine.connect() as connection:
        unprotected = connection.execute(
            text(
                """
                select relation.relname
                from pg_class relation
                join pg_namespace namespace on namespace.oid = relation.relnamespace
                where namespace.nspname = 'public'
                  and relation.relkind = 'r'
                  and relation.relname in (
                      'users',
                      'workspaces',
                      'workspace_memberships',
                      'workspace_config_versions',
                      'audit_events',
                      'exchanges',
                      'exchange_symbol_versions',
                      'candles',
                      'virtual_portfolios'
                  )
                  and (not relation.relrowsecurity or not relation.relforcerowsecurity)
                """
            )
        ).scalars()
        assert list(unprotected) == []

        config_columns = set(
            connection.execute(
                text(
                    """
                    select column_name
                    from information_schema.columns
                    where table_schema = 'public'
                      and table_name = 'active_workspace_configuration'
                    """
                )
            ).scalars()
        )
        assert "configuration" not in config_columns
        assert {"configuration_hash", "version", "workspace_id"} <= config_columns
