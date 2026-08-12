"""Integration tests for M008 database hardening.

Requires TEST_DATABASE_URL to be set; skipped otherwise.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Iterator
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.database import build_engine
from app.domains.features.models import FeatureCode

pytestmark = pytest.mark.database

FIXED_TIME = datetime(2026, 8, 8, 12, 0, 0, tzinfo=timezone.utc)
WORKSPACE_ID = UUID("20000000-0000-0000-0000-000000000001")
SNAPSHOT_ID = UUID("30000000-0000-0000-0000-000000000001")
FEATURE_SET_ID = UUID("50000000-0000-0000-0000-000000000001")
SYMBOL_VERSION_ID = UUID("41000000-0000-0000-0000-000000000001")
EXCHANGE_ID = UUID("40000000-0000-0000-0000-000000000001")


def _read_migration_statements(filename: str) -> list[str]:
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "supabase" / "migrations" / filename
    content = path.read_text(encoding="utf-8")
    statements: list[str] = []
    current: list[str] = []
    in_dollar = False
    i = 0
    while i < len(content):
        char = content[i]
        if char == "$" and not in_dollar and content[i : i + 2] == "$$":
            in_dollar = True
            current.append("$$")
            i += 2
            continue
        if char == "$" and in_dollar and content[i : i + 2] == "$$":
            in_dollar = False
            current.append("$$")
            i += 2
            continue
        current.append(char)
        if char == ";" and not in_dollar:
            stmt = "".join(current).strip()
            if stmt:
                non_comment_lines = [
                    line
                    for line in stmt.splitlines()
                    if not line.strip().startswith("--")
                ]
                if non_comment_lines:
                    statements.append(stmt)
            current = []
        i += 1
    if current:
        stmt = "".join(current).strip()
        if stmt:
            non_comment_lines = [
                line for line in stmt.splitlines() if not line.strip().startswith("--")
            ]
            if non_comment_lines:
                statements.append(stmt)
    return statements


def _ensure_m008_migration(engine: Engine) -> None:
    with engine.begin() as connection:
        row = connection.execute(
            text(
                """
                select count(*)
                from information_schema.columns
                where table_schema = 'public'
                  and table_name = 'feature_values'
                  and column_name = 'null_reason'
                """
            )
        ).scalar_one()
        if row > 0:
            return
        repo_root = Path(__file__).resolve().parents[3]
        migration_path = (
            repo_root / "supabase" / "migrations" / "20260812000000_m008_features.sql"
        )
        hardening_path = (
            repo_root / "supabase" / "migrations" / "20260812010000_m008_hardening.sql"
        )
        for migration_file in (migration_path, hardening_path):
            sql = migration_file.read_text(encoding="utf-8")
            statements = _read_migration_statements(sql)
            for stmt in statements:
                connection.execute(text(stmt))


def _clean_m008_rows(cleanup_engine: Engine) -> None:
    with cleanup_engine.begin() as conn:
        conn.execute(text("delete from public.feature_values"))
        conn.execute(text("delete from public.feature_calculation_invalidations"))
        conn.execute(text("delete from public.feature_calculations"))
        conn.execute(text("delete from public.market_snapshot_candles"))
        conn.execute(text("delete from public.market_snapshots"))
        conn.execute(text("delete from public.candles"))
        conn.execute(text("delete from public.feature_set_versions"))


@pytest.fixture(scope="session")
def database_engine() -> Iterator[Engine]:
    url: str | None = __import__("os").getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for M008 integration tests")
    engine = build_engine(url)
    yield engine
    engine.dispose()


@pytest.fixture()
def clean_m008_data(database_engine: Engine) -> Iterator[None]:
    _ensure_m008_migration(database_engine)
    cleanup_engine = build_engine(database_engine.url)
    _clean_m008_rows(cleanup_engine)
    yield
    _clean_m008_rows(cleanup_engine)
    cleanup_engine.dispose()


def test_validate_snapshot_membership_rejects_wrong_symbol(
    clean_m008_data: None, database_engine: Engine
) -> None:
    with database_engine.connect() as conn, conn.begin():
        conn.execute(
            text(
                """
                insert into public.candles (
                    id, exchange_id, symbol_version_id, interval_code,
                    open_time, close_time, open_price, high_price,
                    low_price, close_price, base_volume, quote_volume,
                    trade_count, finalized, superseded_by, content_hash
                ) values (
                    :id, :exchange_id, :symbol_version_id, :interval_code,
                    :open_time, :close_time, :open_price, :high_price,
                    :low_price, :close_price, :base_volume, :quote_volume,
                    :trade_count, true, null, 'hash'
                )
                """
            ),
            {
                "id": UUID("c0000000-0000-0000-0000-000000000001"),
                "exchange_id": EXCHANGE_ID,
                "symbol_version_id": SYMBOL_VERSION_ID,
                "interval_code": "1h",
                "open_time": FIXED_TIME - timedelta(hours=1),
                "close_time": FIXED_TIME,
                "open_price": Decimal("100"),
                "high_price": Decimal("100"),
                "low_price": Decimal("100"),
                "close_price": Decimal("100"),
                "base_volume": Decimal("1"),
                "quote_volume": Decimal("100"),
                "trade_count": 1,
            },
        )
        conn.execute(
            text(
                """
                insert into public.market_snapshots (
                    id, workspace_id, exchange_id, symbol_version_id,
                    interval_code, analysis_time, first_event_time,
                    last_event_time, candle_count, quality_outcome,
                    freshness_outcome, snapshot_hash, state,
                    invalidation_reason, data_source
                ) values (
                    :id, :workspace_id, :exchange_id, :symbol_version_id,
                    :interval_code, :analysis_time, :first_event_time,
                    :last_event_time, :candle_count, :quality_outcome,
                    :freshness_outcome, :snapshot_hash, :state,
                    :invalidation_reason, :data_source
                )
                """
            ),
            {
                "id": SNAPSHOT_ID,
                "workspace_id": WORKSPACE_ID,
                "exchange_id": EXCHANGE_ID,
                "symbol_version_id": SYMBOL_VERSION_ID,
                "interval_code": "1h",
                "analysis_time": FIXED_TIME,
                "first_event_time": FIXED_TIME - timedelta(hours=1),
                "last_event_time": FIXED_TIME,
                "candle_count": 1,
                "quality_outcome": "approved",
                "freshness_outcome": "fresh",
                "snapshot_hash": "a" * 64,
                "state": "active",
                "invalidation_reason": None,
                "data_source": "rest",
            },
        )
        conn.execute(
            text(
                """
                insert into public.market_snapshot_candles (
                    snapshot_id, candle_id, sequence, candle_content_hash
                ) values (
                    :snapshot_id, :candle_id, :sequence, :candle_content_hash
                )
                """
            ),
            {
                "snapshot_id": SNAPSHOT_ID,
                "candle_id": UUID("c0000000-0000-0000-0000-000000000001"),
                "sequence": 1,
                "candle_content_hash": "hash",
            },
        )
    with (
        pytest.raises(Exception, match="wrong symbol/interval"),
        database_engine.connect() as conn2,
        conn2.begin(),
    ):
        conn2.execute(
            text("select public.validate_snapshot_membership(:snapshot_id)"),
            {"snapshot_id": SNAPSHOT_ID},
        )


def test_consumable_view_excludes_invalidated(
    clean_m008_data: None, database_engine: Engine
) -> None:
    with database_engine.connect() as conn, conn.begin():
        conn.execute(
            text(
                """
                insert into public.feature_calculations (
                    id, snapshot_id, feature_set_version_id,
                    idempotency_key, status, input_hash, output_hash,
                    calculation_started_at, calculation_completed_at,
                    warnings, error_message, creator_cycle_id
                ) values (
                    :id, :snapshot_id, :feature_set_version_id,
                    :idempotency_key, :status, :input_hash, :output_hash,
                    :started_at, :completed_at,
                    :warnings, :error_message, :creator_cycle_id
                )
                """
            ),
            {
                "id": UUID("f0000000-0000-0000-0000-000000000001"),
                "snapshot_id": SNAPSHOT_ID,
                "feature_set_version_id": FEATURE_SET_ID,
                "idempotency_key": "key1",
                "status": "completed",
                "input_hash": "a" * 64,
                "output_hash": "b" * 64,
                "started_at": FIXED_TIME,
                "completed_at": FIXED_TIME,
                "warnings": [],
                "error_message": None,
                "creator_cycle_id": "cycle1",
            },
        )
        row = conn.execute(
            text(
                "select id from public.consumable_feature_calculations "
                "where idempotency_key = :key"
            ),
            {"key": "key1"},
        ).scalar_one_or_none()
        assert row == UUID("f0000000-0000-0000-0000-000000000001")
        conn.execute(
            text(
                """
                insert into public.feature_calculation_invalidations (
                    calculation_id, reason
                ) values (
                    :calculation_id, :reason
                )
                """
            ),
            {
                "calculation_id": UUID("f0000000-0000-0000-0000-000000000001"),
                "reason": "candle_correction",
            },
        )
        row = conn.execute(
            text(
                "select id from public.consumable_feature_calculations "
                "where idempotency_key = :key"
            ),
            {"key": "key1"},
        ).scalar_one_or_none()
        assert row is None


def test_invalidation_idempotent(
    clean_m008_data: None, database_engine: Engine
) -> None:
    with database_engine.connect() as conn, conn.begin():
        conn.execute(
            text(
                """
                insert into public.feature_calculations (
                    id, snapshot_id, feature_set_version_id,
                    idempotency_key, status, input_hash, output_hash,
                    calculation_started_at, calculation_completed_at,
                    warnings, error_message, creator_cycle_id
                ) values (
                    :id, :snapshot_id, :feature_set_version_id,
                    :idempotency_key, :status, :input_hash, :output_hash,
                    :started_at, :completed_at,
                    :warnings, :error_message, :creator_cycle_id
                )
                """
            ),
            {
                "id": UUID("f0000000-0000-0000-0000-000000000002"),
                "snapshot_id": SNAPSHOT_ID,
                "feature_set_version_id": FEATURE_SET_ID,
                "idempotency_key": "key2",
                "status": "completed",
                "input_hash": "a" * 64,
                "output_hash": "b" * 64,
                "started_at": FIXED_TIME,
                "completed_at": FIXED_TIME,
                "warnings": [],
                "error_message": None,
                "creator_cycle_id": "cycle1",
            },
        )
        conn.execute(
            text(
                "select public.invalidate_feature_calculations_for_snapshot("
                ":snapshot_id, :reason)"
            ),
            {"snapshot_id": SNAPSHOT_ID, "reason": "correction"},
        )
        conn.execute(
            text(
                "select public.invalidate_feature_calculations_for_snapshot("
                ":snapshot_id, :reason)"
            ),
            {"snapshot_id": SNAPSHOT_ID, "reason": "correction"},
        )
        count = conn.execute(
            text(
                "select count(*) from public.feature_calculation_invalidations "
                "where calculation_id = :id"
            ),
            {"id": UUID("f0000000-0000-0000-0000-000000000002")},
        ).scalar_one()
        assert count == 1


def test_output_hash_check_requires_64_chars(
    clean_m008_data: None, database_engine: Engine
) -> None:
    with database_engine.connect() as conn, conn.begin():
        conn.execute(
            text(
                """
                insert into public.feature_calculations (
                    id, snapshot_id, feature_set_version_id,
                    idempotency_key, status, input_hash, output_hash,
                    calculation_started_at, calculation_completed_at,
                    warnings, error_message, creator_cycle_id
                ) values (
                    :id, :snapshot_id, :feature_set_version_id,
                    :idempotency_key, :status, :input_hash, :output_hash,
                    :started_at, :completed_at,
                    :warnings, :error_message, :creator_cycle_id
                )
                """
            ),
            {
                "id": UUID("f0000000-0000-0000-0000-000000000003"),
                "snapshot_id": SNAPSHOT_ID,
                "feature_set_version_id": FEATURE_SET_ID,
                "idempotency_key": "key3",
                "status": "completed",
                "input_hash": "a" * 64,
                "output_hash": "b" * 64,
                "started_at": FIXED_TIME,
                "completed_at": FIXED_TIME,
                "warnings": [],
                "error_message": None,
                "creator_cycle_id": "cycle1",
            },
        )
    with (
        pytest.raises(Exception, match="feature_calculations_output_hash_check"),
        database_engine.connect() as conn2,
        conn2.begin(),
    ):
        conn2.execute(
            text(
                """
                insert into public.feature_calculations (
                    id, snapshot_id, feature_set_version_id,
                    idempotency_key, status, input_hash, output_hash,
                    calculation_started_at, calculation_completed_at,
                    warnings, error_message, creator_cycle_id
                ) values (
                    :id, :snapshot_id, :feature_set_version_id,
                    :idempotency_key, :status, :input_hash, :output_hash,
                    :started_at, :completed_at,
                    :warnings, :error_message, :creator_cycle_id
                )
                """
            ),
            {
                "id": UUID("f0000000-0000-0000-0000-000000000003"),
                "snapshot_id": SNAPSHOT_ID,
                "feature_set_version_id": FEATURE_SET_ID,
                "idempotency_key": "key3",
                "status": "completed",
                "input_hash": "a" * 64,
                "output_hash": "short",
                "started_at": FIXED_TIME,
                "completed_at": FIXED_TIME,
                "warnings": [],
                "error_message": None,
                "creator_cycle_id": "cycle1",
            },
        )


def test_warm_up_check_allows_all_null_with_reason(
    clean_m008_data: None, database_engine: Engine
) -> None:
    with database_engine.connect() as conn, conn.begin():
        conn.execute(
            text(
                """
                insert into public.feature_calculations (
                    id, snapshot_id, feature_set_version_id,
                    idempotency_key, status, input_hash, output_hash,
                    calculation_started_at, calculation_completed_at,
                    warnings, error_message, creator_cycle_id
                ) values (
                    :id, :snapshot_id, :feature_set_version_id,
                    :idempotency_key, :status, :input_hash, :output_hash,
                    :started_at, :completed_at,
                    :warnings, :error_message, :creator_cycle_id
                )
                """
            ),
            {
                "id": UUID("f0000000-0000-0000-0000-000000000004"),
                "snapshot_id": SNAPSHOT_ID,
                "feature_set_version_id": FEATURE_SET_ID,
                "idempotency_key": "key4",
                "status": "completed",
                "input_hash": "a" * 64,
                "output_hash": "b" * 64,
                "started_at": FIXED_TIME,
                "completed_at": FIXED_TIME,
                "warnings": [],
                "error_message": None,
                "creator_cycle_id": "cycle1",
            },
        )
        conn.execute(
            text(
                """
                insert into public.feature_values (
                    calculation_id, feature_code, numeric_value,
                    string_value, boolean_value, unit, sequence,
                    timestamp, null_reason
                ) values (
                    :calculation_id, :feature_code, :numeric_value,
                    :string_value, :boolean_value, :unit, :sequence,
                    :timestamp, :null_reason
                )
                """
            ),
            {
                "calculation_id": UUID("f0000000-0000-0000-0000-000000000004"),
                "feature_code": FeatureCode.SMA_20.value,
                "numeric_value": None,
                "string_value": None,
                "boolean_value": None,
                "unit": "price",
                "sequence": 0,
                "timestamp": FIXED_TIME,
                "null_reason": "insufficient_history",
            },
        )
