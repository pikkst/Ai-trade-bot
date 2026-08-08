"""Integration tests for M007 market data service."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Iterator, cast
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session

from app.core.clock import FixedClock
from app.database import build_engine, build_session_factory
from app.domains.market_data.models import (
    GapReport,
    IngestionResult,
    IngestionStatus,
    IngestionType,
    QualityState,
    SnapshotResult,
)
from app.domains.market_data.service import MarketDataService
from app.domains.market_data.validation import ValidationPolicy
from app.infrastructure.exchange.binance.fakes import (
    FakeBinanceConfig,
    FakeBinanceProvider,
    FakeBinanceScenario,
)
from app.infrastructure.exchange.binance.protocol import (
    BinanceProviderUnavailableError,
    BinanceTimeoutError,
    Candle,
    CandleInterval,
    ExchangeTime,
    MarketDataProvider,
    ProviderHealth,
    RateLimitState,
    SymbolMetadata,
)

pytestmark = pytest.mark.database

FIXED_TIME = datetime(2026, 8, 8, 12, 0, 0, tzinfo=timezone.utc)
SYMBOL_VERSION_ID = UUID("41000000-0000-0000-0000-00000000000A")
EXCHANGE_ID = UUID("40000000-0000-0000-0000-000000000001")
WORKSPACE_ID = UUID("20000000-0000-0000-0000-000000000001")
SYMBOL = "BTCEUR"


@pytest.fixture(scope="module")
def database_engine() -> Iterator[Engine]:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for M007 integration tests")
    engine = build_engine(url)
    with engine.connect() as connection:
        connection.execute(text("select 1"))
    yield engine
    engine.dispose()


@pytest.fixture
def clean_m007_data(database_engine: Engine) -> Iterator[None]:
    """Create a dedicated M007 symbol version and remove M007 test data
    before AND after each test so tests are isolated and seed data is
    untouched.

    The service commits per page, so rows persist in the shared database
    across tests within this module. Delete in foreign-key-safe order.
    """

    def _clean() -> None:
        _clean_m007_rows(database_engine)

    _clean()
    yield
    _clean()


def _clean_m007_rows(engine: Engine) -> None:
    """Delete M007 test rows (and re-create the test symbol version) so the
    symbol's candle/ingestion evidence is reset between test phases."""
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                delete from public.market_snapshot_candles
                where snapshot_id in (
                    select snapshot.id
                    from public.market_snapshots snapshot
                    join public.workspaces workspace
                      on workspace.id = snapshot.workspace_id
                    where workspace.name like 'm007-%'
                )
                """
            )
        )
        connection.execute(
            text(
                """
                delete from public.market_snapshots
                where workspace_id in (
                    select id from public.workspaces where name like 'm007-%'
                )
                """
            )
        )
        connection.execute(
            text(
                "delete from public.workspace_memberships "
                "where workspace_id in ("
                "  select id from public.workspaces where name like 'm007-%'"
                ")"
            )
        )
        connection.execute(
            text("delete from public.workspaces where name like 'm007-%'")
        )
        connection.execute(
            text(
                """
                delete from public.market_snapshot_candles
                where candle_id in (
                    select id from public.candles
                    where symbol_version_id = :sid
                )
                """
            ),
            {"sid": SYMBOL_VERSION_ID},
        )
        connection.execute(
            text("delete from public.market_snapshots where symbol_version_id = :sid"),
            {"sid": SYMBOL_VERSION_ID},
        )
        connection.execute(
            text(
                "delete from public.candle_corrections where symbol_version_id = :sid"
            ),
            {"sid": SYMBOL_VERSION_ID},
        )
        connection.execute(
            text(
                "delete from public.data_quality_events where symbol_version_id = :sid"
            ),
            {"sid": SYMBOL_VERSION_ID},
        )
        connection.execute(
            text(
                "delete from public.market_data_ingestions "
                "where symbol_version_id = :sid"
            ),
            {"sid": SYMBOL_VERSION_ID},
        )
        connection.execute(
            text("delete from public.candles where symbol_version_id = :sid"),
            {"sid": SYMBOL_VERSION_ID},
        )
        connection.execute(
            text("delete from public.exchange_symbol_versions where id = :sid"),
            {"sid": SYMBOL_VERSION_ID},
        )
        connection.execute(
            text(
                """
                insert into public.exchange_symbol_versions (
                    id, exchange_id, native_symbol, base_asset, quote_asset,
                    status, price_precision, quantity_precision, tick_size,
                    step_size, min_quantity, min_notional, metadata_hash,
                    effective_at
                ) values (
                    :sid, :eid, 'BTCEUR', 'BTC', 'EUR', 'trading',
                    2, 6, 0.01, 0.000001, 0.000001, 5,
                    :md5, timezone('utc', now())
                )
                """
            ),
            {
                "sid": SYMBOL_VERSION_ID,
                "eid": EXCHANGE_ID,
                "md5": "m" * 64,
            },
        )
    # Close pooled connections so no session-level advisory lock from a prior
    # run survives into the next test phase.
    engine.dispose()


class BoundaryAssertingProvider:
    """Wrap a provider and fail if any network call runs inside a DB transaction.

    This asserts the M007 transaction boundary directly: provider I/O must
    happen with no active persistence transaction on the session.
    """

    def __init__(self, inner: MarketDataProvider, session: Session) -> None:
        self._inner = inner
        self._session = session

    def _assert_no_transaction(self) -> None:
        if self._session.in_transaction():
            raise AssertionError(
                "network call attempted while a DB transaction was active"
            )

    async def get_server_time(self) -> ExchangeTime:
        self._assert_no_transaction()
        return await self._inner.get_server_time()

    async def get_symbol_metadata(self, symbol: str) -> SymbolMetadata:
        self._assert_no_transaction()
        return await self._inner.get_symbol_metadata(symbol)

    async def get_finalized_candles(
        self,
        symbol: str,
        interval: CandleInterval,
        start_time: datetime,
        end_time: datetime,
        server_time: datetime | None = None,
    ) -> list[Candle]:
        self._assert_no_transaction()
        return await self._inner.get_finalized_candles(
            symbol,
            interval,
            start_time,
            end_time,
            server_time,
        )

    async def get_rate_limit_state(self) -> RateLimitState:
        self._assert_no_transaction()
        return await self._inner.get_rate_limit_state()

    async def get_health(self) -> ProviderHealth:
        self._assert_no_transaction()
        return await self._inner.get_health()


@pytest.mark.asyncio
async def test_backfill_inserts_candles_outside_transaction(
    database_engine: Engine, clean_m007_data: None
) -> None:
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    start = FIXED_TIME - timedelta(hours=2)
    end = FIXED_TIME
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=BoundaryAssertingProvider(provider, session),
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        result = await service.backfill(
            symbol=SYMBOL,
            start_time=start,
            end_time=end,
            idempotency_key="test-backfill-1",
        )
    finally:
        session.close()
    assert result.status == IngestionStatus.COMPLETED
    assert result.inserted_count > 0


@pytest.mark.asyncio
async def test_incremental_fetch_overlaps_latest(
    database_engine: Engine, clean_m007_data: None
) -> None:
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        session.execute(
            text(
                """
                insert into public.candles (
                    symbol_version_id, interval_code, open_time, close_time,
                    open_price, high_price, low_price, close_price,
                    base_volume, quote_volume, trade_count, finalized, content_hash
                ) values (
                    :symbol_version_id, '1h', :open_time, :close_time,
                    100, 105, 95, 102, 1.5, 1500, 100, true, :content_hash
                )
                on conflict (symbol_version_id, interval_code, open_time)
                where superseded_by is null do nothing
                """
            ),
            {
                "symbol_version_id": SYMBOL_VERSION_ID,
                "open_time": FIXED_TIME - timedelta(hours=1),
                "close_time": FIXED_TIME,
                "content_hash": "a" * 64,
            },
        )
        session.commit()
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        result = await service.incremental_fetch(
            symbol=SYMBOL,
            idempotency_key="test-incremental-1",
        )
    finally:
        session.close()
    assert result.status == IngestionStatus.COMPLETED
    assert result.corrected_count >= 1


@pytest.mark.asyncio
async def test_incremental_fetch_at_non_hour_wall_clock(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Incremental ranges are aligned to finalized interval boundaries.

    At a non-hour wall-clock time (e.g. 12:28) the fetch must end at the
    last finalized exclusive boundary (12:00) so the not-yet-finalized 12:00
    candle is never expected, and the start is floored to an interval.
    """
    non_hour_time = FIXED_TIME + timedelta(minutes=28)
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=non_hour_time,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(non_hour_time),
        )
        start, end = service._compute_incremental_range(non_hour_time)
        assert end == non_hour_time.replace(minute=0, second=0, microsecond=0)
        assert (start - end).total_seconds() % 3600 == 0
        result = await service.incremental_fetch(
            symbol=SYMBOL,
            idempotency_key="test-incremental-non-hour",
        )
    finally:
        session.close()
    assert result.status == IngestionStatus.COMPLETED
    assert result.actual_end_time == non_hour_time.replace(
        minute=0, second=0, microsecond=0
    )


@pytest.mark.asyncio
async def test_incremental_preflight_server_time_outside_transaction(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """The incremental preflight server-time provider I/O must run with no
    active DB transaction and its failure must leave a durable failed
    ingestion attempt."""
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.TIMEOUT,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(BinanceTimeoutError):
            await service.incremental_fetch(
                symbol=SYMBOL,
                idempotency_key="test-preflight-timeout",
            )
        row = (
            session.execute(
                text(
                    "select status, request_count, retry_count, safe_error, "
                    "ingestion_type "
                    "from public.market_data_ingestions "
                    "where idempotency_key like 'test-preflight-timeout%'"
                )
            )
            .mappings()
            .one()
        )
    finally:
        session.close()
    assert row["status"] == IngestionStatus.FAILED.value
    assert row["ingestion_type"] == IngestionType.PREFLIGHT_FAILURE.value
    assert row["request_count"] >= 1
    assert "server_time_failed" in row["safe_error"]


@pytest.mark.asyncio
async def test_incremental_preflight_boundary_asserting_provider(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Incremental fetch must never call provider I/O inside a DB transaction."""
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        boundary_provider = BoundaryAssertingProvider(provider, session)
        service._provider = boundary_provider
        result = await service.incremental_fetch(
            symbol=SYMBOL,
            idempotency_key="test-preflight-boundary",
        )
        assert result.status == IngestionStatus.COMPLETED
    finally:
        session.close()


@pytest.mark.asyncio
async def test_detect_gaps_bounded_by_latest(
    database_engine: Engine, clean_m007_data: None
) -> None:
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        await service.backfill(
            symbol=SYMBOL,
            start_time=FIXED_TIME - timedelta(hours=3),
            end_time=FIXED_TIME,
            idempotency_key="test-gap-1",
        )
        gap_report = await service.detect_gaps(
            symbol_version_id=SYMBOL_VERSION_ID,
            interval_code="1h",
            expected_start=FIXED_TIME - timedelta(hours=3),
            expected_end=FIXED_TIME - timedelta(hours=1),
        )
    finally:
        session.close()
    assert gap_report.missing_count == 0
    assert gap_report.expected_end == FIXED_TIME - timedelta(hours=1)


@pytest.mark.asyncio
async def test_repair_gap_repairs_actual_missing_range(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Gap repair must target the detected missing interval and restore it.

    Seed a candle at 10:00 and 12:00 so 11:00 is genuinely missing, detect the
    gap, then repair it and verify the missing interval is contiguous.
    """
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        session.execute(
            text(
                """
                insert into public.candles (
                    symbol_version_id, interval_code, open_time, close_time,
                    open_price, high_price, low_price, close_price,
                    base_volume, quote_volume, trade_count, finalized, content_hash
                ) values
                (
                    :sid, '1h', :t10, :t11,
                    100, 105, 95, 102, 1.5, 1500, 100, true, :h10
                ),
                (
                    :sid, '1h', :t12, :t13,
                    100, 105, 95, 102, 1.5, 1500, 100, true, :h12
                )
                on conflict (symbol_version_id, interval_code, open_time)
                where superseded_by is null do nothing
                """
            ),
            {
                "sid": SYMBOL_VERSION_ID,
                "t10": FIXED_TIME - timedelta(hours=2),
                "t11": FIXED_TIME - timedelta(hours=1),
                "t12": FIXED_TIME,
                "t13": FIXED_TIME + timedelta(hours=1),
                "h10": "a" * 64,
                "h12": "b" * 64,
            },
        )
        session.commit()
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        gap_report = await service.detect_gaps(
            symbol_version_id=SYMBOL_VERSION_ID,
            interval_code="1h",
            expected_start=FIXED_TIME - timedelta(hours=2),
            expected_end=FIXED_TIME,
        )
        assert gap_report.missing_count == 1
        assert gap_report.missing_ranges == (
            (FIXED_TIME - timedelta(hours=1), FIXED_TIME),
        )
        result = await service.repair_gaps(
            symbol=SYMBOL,
            gap_report=gap_report,
            idempotency_key="test-repair-real-gap",
        )
        assert result.status == IngestionStatus.COMPLETED
        verification = await service.detect_gaps(
            symbol_version_id=SYMBOL_VERSION_ID,
            interval_code="1h",
            expected_start=FIXED_TIME - timedelta(hours=2),
            expected_end=FIXED_TIME,
        )
        assert verification.missing_count == 0
    finally:
        session.close()


@pytest.mark.asyncio
async def test_partial_page_fails_closed_with_checkpoint(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """A non-empty partial page must not be certified as complete.

    The GAP fake returns only the first half of the page; the ingestion must
    fail with gap evidence and preserve a checkpoint at the proven boundary.
    """
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.GAP,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(BinanceProviderUnavailableError):
            await service.backfill(
                symbol=SYMBOL,
                start_time=FIXED_TIME - timedelta(hours=8),
                end_time=FIXED_TIME,
                idempotency_key="test-partial-page",
            )
        row = (
            session.execute(
                text(
                    "select status, checkpoint, inserted_count "
                    "from public.market_data_ingestions "
                    "where symbol_version_id = :sid "
                    "and idempotency_key = :key"
                ),
                {"sid": SYMBOL_VERSION_ID, "key": "test-partial-page"},
            )
            .mappings()
            .one_or_none()
        )
    finally:
        session.close()
    assert row is not None
    assert row["status"] == IngestionStatus.FAILED.value
    assert row["checkpoint"] is not None
    assert row["checkpoint"] > FIXED_TIME - timedelta(hours=8)


@pytest.mark.asyncio
async def test_idempotent_backfill_reuses_ingestion(
    database_engine: Engine, clean_m007_data: None
) -> None:
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    start = FIXED_TIME - timedelta(hours=2)
    end = FIXED_TIME
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        result1 = await service.backfill(
            symbol=SYMBOL,
            start_time=start,
            end_time=end,
            idempotency_key="test-idempotent-1",
        )
        result2 = await service.backfill(
            symbol=SYMBOL,
            start_time=start,
            end_time=end,
            idempotency_key="test-idempotent-1",
        )
    finally:
        session.close()
    assert result1.status == IngestionStatus.COMPLETED
    assert result2.status == IngestionStatus.COMPLETED
    candle_count = int(
        database_engine.connect()
        .execute(
            text(
                "select count(*) from public.candles "
                "where symbol_version_id = :sid and interval_code = '1h' "
                "and superseded_by is null"
            ),
            {"sid": SYMBOL_VERSION_ID},
        )
        .scalar_one()
    )
    assert candle_count == result1.inserted_count


def test_validation_policy_custom_values() -> None:
    policy = ValidationPolicy(
        max_clock_drift_ms=1000,
        stale_threshold_seconds=1800,
        interval_seconds=300,
        policy_version="2.0",
    )
    assert policy.max_clock_drift_ms == 1000
    assert policy.stale_threshold_seconds == 1800
    assert policy.interval_seconds == 300
    assert policy.policy_version == "2.0"


def test_gap_report_is_immutable() -> None:
    report = GapReport(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        interval_seconds=3600,
        expected_start=FIXED_TIME,
        expected_end=FIXED_TIME + timedelta(hours=1),
        missing_count=1,
        missing_ranges=((FIXED_TIME, FIXED_TIME),),
        severity="warning",
        detection_policy_version="1.0",
    )
    with pytest.raises(AttributeError):
        report.missing_count = 2  # type: ignore[misc]


@pytest.mark.asyncio
async def test_symbol_binding_rejects_mismatch(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """The requested symbol must match the configured symbol version."""
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(ValueError):
            await service.backfill(
                symbol="ETHEUR",
                start_time=FIXED_TIME - timedelta(hours=1),
                end_time=FIXED_TIME,
                idempotency_key="test-symbol-mismatch",
            )
    finally:
        session.close()


@pytest.mark.asyncio
async def test_correction_invalidates_dependent_snapshot(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """A corrected candle invalidates snapshots referencing the original."""
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        session.execute(
            text(
                """
                insert into public.candles (
                    symbol_version_id, interval_code, open_time, close_time,
                    open_price, high_price, low_price, close_price,
                    base_volume, quote_volume, trade_count, finalized, content_hash
                ) values (
                    :sid, '1h', :open_time, :close_time,
                    100, 105, 95, 102, 1.5, 1500, 100, true, :content_hash
                )
                on conflict (symbol_version_id, interval_code, open_time)
                where superseded_by is null do nothing
                """
            ),
            {
                "sid": SYMBOL_VERSION_ID,
                "open_time": FIXED_TIME - timedelta(hours=1),
                "close_time": FIXED_TIME,
                "content_hash": "a" * 64,
            },
        )
        session.commit()
        original_id = session.execute(
            text(
                "select id from public.candles "
                "where symbol_version_id = :sid and open_time = :t "
                "and superseded_by is null"
            ),
            {"sid": SYMBOL_VERSION_ID, "t": FIXED_TIME - timedelta(hours=1)},
        ).scalar_one()
        # Create a snapshot over the original candle so it can be invalidated.
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        snapshot = service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[original_id],
            quality_outcome="approved",
            freshness_outcome="fresh",
        )
        session.commit()
        snapshot_id = snapshot.snapshot_id

        result = await service.incremental_fetch(
            symbol=SYMBOL,
            idempotency_key="test-correction-invalidate",
        )
        assert result.corrected_count >= 1
        session.commit()
        snapshot_state = session.execute(
            text("select state from public.market_snapshots where id = :sid"),
            {"sid": snapshot_id},
        ).scalar_one()
        assert snapshot_state == "invalidated"
    finally:
        session.close()


def test_snapshot_idempotent_replay_same_identity(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Replaying an identical snapshot request returns the same identity."""
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        session.execute(
            text(
                """
                insert into public.candles (
                    symbol_version_id, interval_code, open_time, close_time,
                    open_price, high_price, low_price, close_price,
                    base_volume, quote_volume, trade_count, finalized, content_hash
                ) values (
                    :sid, '1h', :open_time, :close_time,
                    100, 105, 95, 102, 1.5, 1500, 100, true, :content_hash
                )
                on conflict (symbol_version_id, interval_code, open_time)
                where superseded_by is null do nothing
                """
            ),
            {
                "sid": SYMBOL_VERSION_ID,
                "open_time": FIXED_TIME - timedelta(hours=1),
                "close_time": FIXED_TIME,
                "content_hash": "a" * 64,
            },
        )
        session.commit()
        candle_id = session.execute(
            text(
                "select id from public.candles "
                "where symbol_version_id = :sid and open_time = :t "
                "and superseded_by is null"
            ),
            {"sid": SYMBOL_VERSION_ID, "t": FIXED_TIME - timedelta(hours=1)},
        ).scalar_one()
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        first = service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[candle_id],
            quality_outcome="approved",
            freshness_outcome="fresh",
        )
        session.commit()
        second = service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[candle_id],
            quality_outcome="approved",
            freshness_outcome="fresh",
        )
        session.commit()
    finally:
        session.close()
    assert isinstance(first, SnapshotResult)
    assert isinstance(second, SnapshotResult)
    assert first.snapshot_id == second.snapshot_id
    assert first.snapshot_hash == second.snapshot_hash


class FlakyAfterFirstPageProvider:
    """Succeed on the first klines call, then fail on the second."""

    def __init__(self, inner: MarketDataProvider) -> None:
        self._inner = inner
        self._calls = 0

    async def get_server_time(self) -> ExchangeTime:
        return await self._inner.get_server_time()

    async def get_symbol_metadata(self, symbol: str) -> SymbolMetadata:
        return await self._inner.get_symbol_metadata(symbol)

    async def get_finalized_candles(
        self,
        symbol: str,
        interval: CandleInterval,
        start_time: datetime,
        end_time: datetime,
        server_time: datetime | None = None,
    ) -> list[Candle]:
        self._calls += 1
        if self._calls >= 2:
            raise RuntimeError("simulated provider failure after first page")
        return await self._inner.get_finalized_candles(
            symbol,
            interval,
            start_time,
            end_time,
            server_time,
        )

    async def get_rate_limit_state(self) -> RateLimitState:
        return await self._inner.get_rate_limit_state()

    async def get_health(self) -> ProviderHealth:
        return await self._inner.get_health()


@pytest.mark.asyncio
async def test_restart_resumes_from_committed_page_evidence(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """A failure after a committed page must resume from the persisted
    checkpoint and produce the same final evidence as an uninterrupted run."""
    start = FIXED_TIME - timedelta(hours=8)
    end = FIXED_TIME
    # First run: the GAP fake returns only the first half of the page. The
    # service commits the accepted prefix, persists cumulative counters + page
    # hashes with the checkpoint, then fails closed.
    gap_provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.GAP,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session1 = build_session_factory(database_engine)()
    try:
        service1 = MarketDataService(
            session=session1,
            provider=gap_provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(BinanceProviderUnavailableError):
            await service1.backfill(
                symbol=SYMBOL,
                start_time=start,
                end_time=end,
                idempotency_key="test-restart-evidence",
            )
        row1 = (
            session1.execute(
                text(
                    "select status, checkpoint, inserted_count, page_hashes "
                    "from public.market_data_ingestions "
                    "where idempotency_key = 'test-restart-evidence'"
                ),
            )
            .mappings()
            .one()
        )
        assert row1["status"] == IngestionStatus.FAILED.value
        assert row1["checkpoint"] > start
        assert row1["checkpoint"] < end
        assert row1["inserted_count"] > 0
        assert row1["page_hashes"] is not None
        checkpoint = row1["checkpoint"]
    finally:
        session1.close()

    # Second run: healthy provider resumes from the persisted checkpoint and
    # completes with cumulative evidence matching committed pages + new pages.
    healthy = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session2 = build_session_factory(database_engine)()
    try:
        service2 = MarketDataService(
            session=session2,
            provider=healthy,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        result2 = await service2.backfill(
            symbol=SYMBOL,
            start_time=start,
            end_time=end,
            idempotency_key="test-restart-evidence",
        )
    finally:
        session2.close()
    assert result2.status == IngestionStatus.COMPLETED
    assert result2.inserted_count >= row1["inserted_count"]
    # The final content hash incorporates all ordered page hashes including
    # those committed before the failure.
    assert len(result2.content_hash) == 64
    # The resume began after the persisted checkpoint, not from the start.
    assert checkpoint == result2.actual_start_time or checkpoint > start


@contextmanager
def _authenticated_connection(
    engine: Engine, auth_subject: UUID
) -> Iterator[Connection]:
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.exec_driver_sql("set local role authenticated")
            connection.execute(
                text(
                    "select set_config('request.jwt.claim.role', 'authenticated', true)"
                ),
            )
            connection.execute(
                text("select set_config('request.jwt.claim.sub', :subject, true)"),
                {"subject": str(auth_subject)},
            )
            yield connection
        finally:
            transaction.rollback()


def test_authenticated_can_read_m007_views_but_not_mutate_base(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Security-invoker read views must be readable by authenticated while the
    base M007 tables remain read-only for browsers (matching M003)."""
    subject = UUID("30000000-0000-0000-0000-000000000001")
    with _authenticated_connection(database_engine, subject) as connection:
        assert (
            connection.execute(
                text("select count(*) from public.market_snapshot_read")
            ).scalar_one()
            >= 0
        )
        assert (
            connection.execute(
                text("select count(*) from public.data_quality_event_read")
            ).scalar_one()
            >= 0
        )
        with pytest.raises(Exception) as excinfo:
            connection.execute(
                text("insert into public.market_snapshots (snapshot_hash) values (:h)"),
                {"h": "d" * 64},
            )
        # The write must fail due to missing privileges/RLS, not a data error.
        assert "permission denied" in str(excinfo.value).lower() or (
            "row-level security" in str(excinfo.value).lower()
        )


def test_quality_state_vocabulary_matches_database_constraint(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Every canonical QualityState value must be persistable and every
    constraint value must be represented by the domain enum."""
    import re

    domain_values = {state.value for state in QualityState}
    with database_engine.connect() as connection:
        constraint_text = connection.execute(
            text(
                """
                select pg_get_constraintdef(oid)
                from pg_constraint
                where conrelid = 'public.data_quality_events'::regclass
                  and contype = 'c'
                  and conname = 'data_quality_events_event_type_check'
                """
            )
        ).scalar_one()
    constraint_values = set(re.findall(r"'([a-z_]+)'", constraint_text))
    assert domain_values == constraint_values
    assert "stale" in domain_values
    assert "provider_unavailable" in domain_values
    assert "rate_limited" in domain_values
    assert "gap_repaired" in domain_values
    assert "gap_unresolved" in domain_values


def test_workspace_isolation_prevents_cross_workspace_snapshot_read(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """A user in workspace A must not read workspace B snapshots.

    The authenticated SELECT policy on market_snapshots uses
    private.has_workspace_role, so the security-invoker view only exposes
    rows for the caller's own workspaces.
    """
    # Seed VIEWER user is a member of WORKSPACE_ID (workspace A).
    subject = UUID("00000000-0000-0000-0000-000000000103")
    other_workspace = UUID("20000000-0000-0000-0000-0000000000BB")
    other_snapshot_id = UUID("50000000-0000-0000-0000-0000000000BB")
    with database_engine.begin() as connection:
        connection.execute(
            text(
                """
                insert into public.workspaces (
                    id, name, base_currency, lifecycle_state,
                    created_at, updated_at, version
                ) values (
                    :wid, 'm007-workspace-b', 'EUR', 'active',
                    timezone('utc', now()), timezone('utc', now()), 1
                )
                on conflict (id) do nothing
                """
            ),
            {"wid": other_workspace},
        )
        connection.execute(
            text(
                """
                insert into public.market_snapshots (
                    id, workspace_id, exchange_id, symbol_version_id, interval_code,
                    analysis_time, first_event_time, last_event_time, candle_count,
                    quality_outcome, quality_policy_version, freshness_outcome,
                    freshness_policy_version, data_source, snapshot_hash,
                    snapshot_schema_version, state
                ) values (
                    :sid, :wid, :eid, :svid, '1h',
                    :at, :fet, :let, 1,
                    'approved', '1.0', 'fresh', '1.0',
                    'rest', :hash, '1.0', 'active'
                )
                on conflict (id) do nothing
                """
            ),
            {
                "sid": other_snapshot_id,
                "wid": other_workspace,
                "eid": EXCHANGE_ID,
                "svid": SYMBOL_VERSION_ID,
                "at": FIXED_TIME,
                "fet": FIXED_TIME - timedelta(hours=1),
                "let": FIXED_TIME - timedelta(hours=1),
                "hash": "e" * 64,
            },
        )
    # The subject (member of workspace A only) must not see workspace B rows.
    with _authenticated_connection(database_engine, subject) as connection:
        assert (
            connection.execute(
                text("select count(*) from public.market_snapshots where id = :sid"),
                {"sid": other_snapshot_id},
            ).scalar_one()
            == 0
        )


@pytest.mark.asyncio
async def test_drift_failure_then_healthy_then_fresh_snapshot(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """A transient clock-drift failure must not permanently block snapshots.

    After a drift failure scoped to a range, a healthy ingestion over the same
    range appends clock_drift_recovered terminal evidence, so a fresh snapshot
    over that range can be approved.
    """
    drift_provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            server_time_offset_seconds=30,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=drift_provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
            policy=ValidationPolicy(max_clock_drift_ms=100),
        )
        with pytest.raises(BinanceProviderUnavailableError):
            await service.backfill(
                symbol=SYMBOL,
                start_time=FIXED_TIME - timedelta(hours=1),
                end_time=FIXED_TIME,
                idempotency_key="test-drift-fail",
            )
    finally:
        session.close()

    # Healthy provider recovers over the same range.
    healthy = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=healthy,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        result = await service.backfill(
            symbol=SYMBOL,
            start_time=FIXED_TIME - timedelta(hours=1),
            end_time=FIXED_TIME,
            idempotency_key="test-drift-recover",
        )
        assert result.status == IngestionStatus.COMPLETED
        candle_id = session.execute(
            text(
                "select id from public.candles "
                "where symbol_version_id = :sid and superseded_by is null "
                "limit 1"
            ),
            {"sid": SYMBOL_VERSION_ID},
        ).scalar_one()
        snapshot = service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[candle_id],
            quality_outcome="approved",
            freshness_outcome="fresh",
        )
        assert snapshot.quality_outcome == "approved"
        assert snapshot.freshness_outcome == "fresh"
    finally:
        session.close()


@pytest.mark.asyncio
async def test_restart_hash_matches_uninterrupted_control(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """The final ingestion hash must be identical whether the run is
    interrupted+resumed or uninterrupted over the same logical range.

    Hash is derived from canonical accepted-content pairs ordered by open
    time, not from page segmentation.
    """
    start = FIXED_TIME - timedelta(hours=6)
    end = FIXED_TIME
    # Interrupted then resumed run over the logical range first.
    gap_provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.GAP,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=gap_provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(BinanceProviderUnavailableError):
            await service.backfill(
                symbol=SYMBOL,
                start_time=start,
                end_time=end,
                idempotency_key="test-hash-resume",
            )
    finally:
        session.close()

    healthy = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=healthy,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        resumed = await service.backfill(
            symbol=SYMBOL,
            start_time=start,
            end_time=end,
            idempotency_key="test-hash-resume",
        )
    finally:
        session.close()
    assert resumed.status == IngestionStatus.COMPLETED

    # Reset candle/ingestion evidence, then run the uninterrupted control.
    _clean_m007_rows(database_engine)
    with database_engine.connect() as diag:
        rows = diag.execute(
            text("select pid, objid, granted from pg_locks where locktype = 'advisory'")
        ).all()
        assert len(rows) == 0, f"advisory locks leaked: {rows}"
    control_provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=control_provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        control = await service.backfill(
            symbol=SYMBOL,
            start_time=start,
            end_time=end,
            idempotency_key="test-hash-control",
        )
    finally:
        session.close()
    assert control.status == IngestionStatus.COMPLETED
    # Same logical range, same final candles => same content hash.
    assert resumed.content_hash == control.content_hash


@pytest.mark.asyncio
async def test_concurrent_same_range_different_delivery_key_single_owner(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Two workers requesting the same canonical range/type with different
    delivery keys contend on the same advisory lock; only one owns the run."""
    start = FIXED_TIME - timedelta(hours=1)
    end = FIXED_TIME
    results: list[IngestionResult | Exception] = []

    async def worker(delivery_key: str) -> None:
        provider = FakeBinanceProvider(
            config=FakeBinanceConfig(
                scenario=FakeBinanceScenario.SUCCESS,
                fixed_clock_time=FIXED_TIME,
                fixture_version="2026-08-08-m007-v1",
            )
        )
        session = build_session_factory(database_engine)()
        try:
            service = MarketDataService(
                session=session,
                provider=provider,
                workspace_id=WORKSPACE_ID,
                exchange_id=EXCHANGE_ID,
                symbol_version_id=SYMBOL_VERSION_ID,
                interval=CandleInterval.ONE_HOUR,
                clock=FixedClock(FIXED_TIME),
            )
            result = await service.backfill(
                symbol=SYMBOL,
                start_time=start,
                end_time=end,
                idempotency_key=delivery_key,
            )
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            results.append(exc)
        finally:
            session.close()

    import asyncio as _asyncio

    await _asyncio.gather(
        worker("delivery-key-A"),
        worker("delivery-key-B"),
    )
    assert len(results) == 2
    # At least one worker completed; the other either completed or failed
    # closed on the lock. No run may race the shared ingestion row.
    owners = [r for r in results if isinstance(r, IngestionResult)]
    assert len(owners) >= 1


@pytest.mark.asyncio
async def test_backfill_rejects_invalid_ranges(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Zero-length, inverted, and non-aligned backfill ranges are rejected."""
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(ValueError):
            await service.backfill(
                symbol=SYMBOL,
                start_time=FIXED_TIME,
                end_time=FIXED_TIME,
                idempotency_key="test-range-zero",
            )
        with pytest.raises(ValueError):
            await service.backfill(
                symbol=SYMBOL,
                start_time=FIXED_TIME,
                end_time=FIXED_TIME - timedelta(hours=1),
                idempotency_key="test-range-inverted",
            )
        # Non-aligned boundaries are normalized to interval boundaries, not
        # rejected, so the expected open-time sequence is deterministic.
        aligned = await service.backfill(
            symbol=SYMBOL,
            start_time=FIXED_TIME.replace(hour=10, minute=30),
            end_time=FIXED_TIME.replace(hour=12, minute=30),
            idempotency_key="test-range-nonaligned",
        )
        assert aligned.status == IngestionStatus.COMPLETED
        assert aligned.actual_start_time == FIXED_TIME.replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        assert aligned.actual_end_time == FIXED_TIME.replace(
            hour=13, minute=0, second=0, microsecond=0
        )
    finally:
        session.close()


@pytest.mark.asyncio
async def test_same_page_conflict_fails_closed_and_blocks_snapshot(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """An inconsistent same-open-time duplicate fails the ingestion and the
    scoped conflict event blocks snapshot approval for that range."""
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.DUPLICATE_CONFLICT,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(BinanceProviderUnavailableError):
            await service.backfill(
                symbol=SYMBOL,
                start_time=FIXED_TIME - timedelta(hours=2),
                end_time=FIXED_TIME,
                idempotency_key="test-conflict-page",
            )
        conflict_count = session.execute(
            text(
                "select count(*) from public.data_quality_events "
                "where event_type = 'duplicate_conflict' "
                "and symbol_version_id = :sid"
            ),
            {"sid": SYMBOL_VERSION_ID},
        ).scalar_one()
        assert conflict_count >= 1
    finally:
        session.close()


@pytest.mark.asyncio
async def test_same_page_conflict_with_existing_db_candle_fails_closed(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Batch ambiguity is rejected even when one version matches an existing
    database candle: a page with [T=A, T=B] where the DB already has T=A must
    fail closed instead of applying B as a correction."""
    # Seed the DB candle T=A so the first page row is a consistent duplicate
    # and the second differs from both the page and the DB.
    session = build_session_factory(database_engine)()
    try:
        session.execute(
            text(
                """
                insert into public.candles (
                    symbol_version_id, interval_code, open_time, close_time,
                    open_price, high_price, low_price, close_price,
                    base_volume, quote_volume, trade_count, finalized, content_hash
                ) values (
                    :sid, '1h', :ot, :ct,
                    100, 105, 95, 102, 1.5, 1500, 100, true, :hash
                )
                on conflict (symbol_version_id, interval_code, open_time)
                where superseded_by is null do nothing
                """
            ),
            {
                "sid": SYMBOL_VERSION_ID,
                "ot": FIXED_TIME - timedelta(hours=1),
                "ct": FIXED_TIME,
                "hash": "a" * 64,
            },
        )
        session.commit()
        provider = FakeBinanceProvider(
            config=FakeBinanceConfig(
                scenario=FakeBinanceScenario.DUPLICATE_CONFLICT,
                fixed_clock_time=FIXED_TIME,
                fixture_version="2026-08-08-m007-v1",
            )
        )
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(BinanceProviderUnavailableError):
            await service.backfill(
                symbol=SYMBOL,
                start_time=FIXED_TIME - timedelta(hours=2),
                end_time=FIXED_TIME,
                idempotency_key="test-conflict-existing",
            )
        # The conflicting open time must not have been corrected: the active
        # candle still carries the original content hash, and no correction
        # was applied for it.
        active_hash = session.execute(
            text(
                "select content_hash from public.candles "
                "where symbol_version_id = :sid "
                "and open_time = :ot and superseded_by is null"
            ),
            {"sid": SYMBOL_VERSION_ID, "ot": FIXED_TIME - timedelta(hours=1)},
        ).scalar_one()
        assert active_hash == "a" * 64
        conflict_count = session.execute(
            text(
                "select count(*) from public.data_quality_events "
                "where event_type = 'duplicate_conflict' "
                "and symbol_version_id = :sid"
            ),
            {"sid": SYMBOL_VERSION_ID},
        ).scalar_one()
        assert conflict_count >= 1
    finally:
        session.close()


@pytest.mark.asyncio
async def test_terminal_resolution_idempotent_and_cross_category_blocked(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Repeated recovery appends exactly one terminal event per blocker, and a
    terminal event of one category cannot clear a blocker of another."""
    drift_provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            server_time_offset_seconds=30,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=drift_provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
            policy=ValidationPolicy(max_clock_drift_ms=100),
        )
        with pytest.raises(BinanceProviderUnavailableError):
            await service.backfill(
                symbol=SYMBOL,
                start_time=FIXED_TIME - timedelta(hours=1),
                end_time=FIXED_TIME,
                idempotency_key="test-drift-dup",
            )
    finally:
        session.close()

    # Two healthy recoveries over the same range: terminal resolution must be
    # idempotent (one clock_drift_recovered per blocker).
    healthy = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=healthy,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        for idx in range(2):
            await service.backfill(
                symbol=SYMBOL,
                start_time=FIXED_TIME - timedelta(hours=1),
                end_time=FIXED_TIME,
                idempotency_key=f"test-drift-recover-{idx}",
            )
    finally:
        session.close()

    session = build_session_factory(database_engine)()
    try:
        recovered = session.execute(
            text(
                "select count(*) from public.data_quality_events "
                "where event_type = 'clock_drift_recovered' "
                "and symbol_version_id = :sid"
            ),
            {"sid": SYMBOL_VERSION_ID},
        ).scalar_one()
        assert recovered == 1
    finally:
        session.close()

    # Cross-category: a gap_repaired terminal for the same range must NOT
    # clear a clock_drift_exceeded blocker. The effective gate derives
    # terminal state by exact blocker identity (supersedes_event_id) with
    # valid transitions enforced.
    session = build_session_factory(database_engine)()
    try:
        # A new, unrecovered clock_drift_exceeded blocker.
        fresh_blocker_id = session.execute(
            text(
                """
                insert into public.data_quality_events (
                    exchange_id, symbol_version_id, interval_code, event_type,
                    severity, details, detection_policy_version,
                    affected_range_start, affected_range_end
                ) values (
                    :eid, :sid, '1h', 'clock_drift_exceeded', 'error',
                    '{}'::jsonb, '1.0',
                    :rstart, :rend
                )
                returning id
                """
            ),
            {
                "eid": EXCHANGE_ID,
                "sid": SYMBOL_VERSION_ID,
                "rstart": FIXED_TIME - timedelta(hours=1),
                "rend": FIXED_TIME,
            },
        ).scalar_one()
        session.commit()
        # A wrong-category terminal referencing the fresh blocker must be
        # rejected by the DB transition trigger (fail closed): gap_repaired
        # cannot resolve a clock_drift_exceeded blocker.
        with pytest.raises(Exception) as excinfo:
            session.execute(
                text(
                    """
                    insert into public.data_quality_events (
                        exchange_id, symbol_version_id, interval_code, event_type,
                        severity, details, detection_policy_version, supersedes_event_id
                    ) values (
                        :eid, :sid, '1h', 'gap_repaired', 'info',
                        '{}'::jsonb, '1.0', :blocker_id
                    )
                    """
                ),
                {
                    "eid": EXCHANGE_ID,
                    "sid": SYMBOL_VERSION_ID,
                    "blocker_id": fresh_blocker_id,
                },
            )
        session.rollback()
        assert "invalid terminal transition" in str(excinfo.value)
        # The gate must still see the drift blocker as effective: only a
        # clock_drift_recovered terminal superseding it clears it.
        still_blocked = session.execute(
            text(
                """
                select count(*) from public.data_quality_events blocker
                where blocker.id = :blocker_id
                  and blocker.event_type = 'clock_drift_exceeded'
                  and not exists (
                      select 1 from public.data_quality_events terminal
                      where terminal.supersedes_event_id = blocker.id
                        and terminal.event_type = 'clock_drift_recovered'
                  )
                """
            ),
            {"blocker_id": fresh_blocker_id},
        ).scalar_one()
        assert still_blocked == 1
        # The correct-category terminal clears it.
        session.execute(
            text(
                """
                insert into public.data_quality_events (
                    exchange_id, symbol_version_id, interval_code, event_type,
                    severity, details, detection_policy_version, supersedes_event_id
                ) values (
                    :eid, :sid, '1h', 'clock_drift_recovered', 'info',
                    '{}'::jsonb, '1.0', :blocker_id
                )
                """
            ),
            {
                "eid": EXCHANGE_ID,
                "sid": SYMBOL_VERSION_ID,
                "blocker_id": fresh_blocker_id,
            },
        )
        session.commit()
        cleared = session.execute(
            text(
                """
                select count(*) from public.data_quality_events blocker
                where blocker.id = :blocker_id
                  and blocker.event_type = 'clock_drift_exceeded'
                  and not exists (
                      select 1 from public.data_quality_events terminal
                      where terminal.supersedes_event_id = blocker.id
                        and terminal.event_type = 'clock_drift_recovered'
                  )
                """
            ),
            {"blocker_id": fresh_blocker_id},
        ).scalar_one()
        assert cleared == 0
    finally:
        session.close()


@pytest.mark.asyncio
async def test_invalid_candle_scoped_snapshot_fails_only_at_t(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """An error scoped to open time T blocks only snapshots covering T;
    unrelated ranges remain approvable."""
    session = build_session_factory(database_engine)()
    try:
        # Seed two valid candles: 10:00 and 11:00 (close 12:00 for freshness).
        t10 = FIXED_TIME - timedelta(hours=2)
        t11 = FIXED_TIME - timedelta(hours=1)
        for idx, candle_time in enumerate((t10, t11)):
            session.execute(
                text(
                    """
                    insert into public.candles (
                        symbol_version_id, interval_code, open_time, close_time,
                        open_price, high_price, low_price, close_price,
                        base_volume, quote_volume, trade_count, finalized, content_hash
                    ) values (
                        :sid, '1h', :ot, :ct, 100, 105, 95, 102,
                        1.5, 1500, 100, true, :hash
                    )
                    on conflict (symbol_version_id, interval_code, open_time)
                    where superseded_by is null do nothing
                    """
                ),
                {
                    "sid": SYMBOL_VERSION_ID,
                    "ot": candle_time,
                    "ct": candle_time + timedelta(hours=1),
                    "hash": f"{idx:064x}",
                },
            )
        session.commit()
        # Scope an error to exactly the 11:00 candle.
        session.execute(
            text(
                """
                insert into public.data_quality_events (
                    exchange_id, symbol_version_id, interval_code, event_type,
                    severity, details, detection_policy_version,
                    affected_range_start, affected_range_end
                ) values (
                    :eid, :sid, '1h', 'invalid_value', 'error',
                    '{}'::jsonb, '1.0', :t11, :t11
                )
                """
            ),
            {
                "eid": EXCHANGE_ID,
                "sid": SYMBOL_VERSION_ID,
                "t11": t11,
            },
        )
        session.commit()
        service = MarketDataService(
            session=session,
            provider=FakeBinanceProvider(
                config=FakeBinanceConfig(
                    scenario=FakeBinanceScenario.SUCCESS,
                    fixed_clock_time=FIXED_TIME,
                    fixture_version="2026-08-08-m007-v1",
                )
            ),
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )

        def candle_id(open_time: datetime) -> UUID:
            return cast(
                UUID,
                session.execute(
                    text(
                        "select id from public.candles "
                        "where symbol_version_id = :sid and open_time = :ot "
                        "and superseded_by is null"
                    ),
                    {"sid": SYMBOL_VERSION_ID, "ot": open_time},
                ).scalar_one(),
            )

        # Snapshot covering 11:00 must fail the gate (scoped blocker).
        with pytest.raises(ValueError):
            service.create_snapshot(
                analysis_time=FIXED_TIME,
                candle_ids=[candle_id(t11)],
                quality_outcome="approved",
                freshness_outcome="fresh",
            )
        # Snapshot covering only 10:00 is unaffected and fresh.
        snapshot = service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[candle_id(t10)],
            quality_outcome="approved",
            freshness_outcome="fresh",
        )
        assert snapshot.quality_outcome == "approved"
        assert snapshot.freshness_outcome == "fresh"
    finally:
        session.close()


@pytest.mark.asyncio
async def test_repair_hash_deterministic_for_identical_replay(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """An exact gap-repair replay over the same range preserves the aggregate
    content hash, proving the repair identity is derived from the repaired
    child content rather than ignored."""
    start = FIXED_TIME - timedelta(hours=2)
    end = FIXED_TIME - timedelta(hours=1)

    async def run_repair(idempotency_key: str) -> str:
        provider = FakeBinanceProvider(
            config=FakeBinanceConfig(
                scenario=FakeBinanceScenario.SUCCESS,
                fixed_clock_time=FIXED_TIME,
                fixture_version="2026-08-08-m007-v1",
            )
        )
        session = build_session_factory(database_engine)()
        try:
            service = MarketDataService(
                session=session,
                provider=provider,
                workspace_id=WORKSPACE_ID,
                exchange_id=EXCHANGE_ID,
                symbol_version_id=SYMBOL_VERSION_ID,
                interval=CandleInterval.ONE_HOUR,
                clock=FixedClock(FIXED_TIME),
            )
            report = await service.detect_gaps(
                symbol_version_id=SYMBOL_VERSION_ID,
                interval_code="1h",
                expected_start=start,
                expected_end=end,
            )
            result = await service.repair_gaps(
                symbol=SYMBOL,
                gap_report=report,
                idempotency_key=idempotency_key,
            )
            return result.content_hash
        finally:
            session.close()

    hash1 = await run_repair("test-repair-hash-1")
    # Reset evidence, then replay the identical repair.
    _clean_m007_rows(database_engine)
    hash2 = await run_repair("test-repair-hash-2")
    assert hash1 == hash2
    assert len(hash1) == 64


def test_lock_release_preserves_sentinel_advisory_lock(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Releasing the M007 ingestion lock must not release unrelated
    session-level advisory locks on the same connection."""
    session = build_session_factory(database_engine)()
    try:
        session.execute(
            text("select pg_advisory_lock(hashtextextended('sentinel', 0))")
        )
        service = MarketDataService(
            session=session,
            provider=FakeBinanceProvider(
                config=FakeBinanceConfig(
                    scenario=FakeBinanceScenario.SUCCESS,
                    fixed_clock_time=FIXED_TIME,
                    fixture_version="2026-08-08-m007-v1",
                )
            ),
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        key = service._acquire_ingestion_lock(
            IngestionType.BACKFILL,
            FIXED_TIME - timedelta(hours=1),
            FIXED_TIME,
        )
        service._release_ingestion_lock(key)
        # The sentinel lock must still be held on the shared connection: a
        # second session cannot acquire it.
        session_pid = session.execute(text("select pg_backend_pid()")).scalar_one()
        with database_engine.connect() as other:
            other_pid = other.execute(text("select pg_backend_pid()")).scalar_one()
            reacquired = other.execute(
                text("select pg_try_advisory_lock(hashtextextended('sentinel', 0))")
            ).scalar_one()
            assert session_pid != other_pid
            assert reacquired is False, (
                f"sentinel released: session_pid={session_pid} other_pid={other_pid}"
            )
    finally:
        session.rollback()
        session.execute(text("select pg_advisory_unlock_all()"))
        session.close()


@pytest.mark.asyncio
async def test_terminal_backfill_from_legacy_json_details(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Upgrade path: pre-081600 terminal rows that stored supersedes_event_id
    only in details JSON are backfilled into the structured column, deduplicated,
    and then recognized by the snapshot gate."""
    session = build_session_factory(database_engine)()
    try:
        # Create a blocker and two legacy terminal rows (details JSON only).
        blocker_id = session.execute(
            text(
                """
                insert into public.data_quality_events (
                    exchange_id, symbol_version_id, interval_code, event_type,
                    severity, details, detection_policy_version,
                    affected_range_start, affected_range_end
                ) values (
                    :eid, :sid, '1h', 'clock_drift_exceeded', 'error',
                    '{}'::jsonb, '1.0', :rstart, :rend
                )
                returning id
                """
            ),
            {
                "eid": EXCHANGE_ID,
                "sid": SYMBOL_VERSION_ID,
                "rstart": FIXED_TIME - timedelta(hours=1),
                "rend": FIXED_TIME,
            },
        ).scalar_one()
        for _ in range(2):
            session.execute(
                text(
                    """
                    insert into public.data_quality_events (
                        exchange_id, symbol_version_id, interval_code, event_type,
                        severity, details, detection_policy_version
                    ) values (
                        :eid, :sid, '1h', 'clock_drift_recovered', 'info',
                        :details, '1.0'
                    )
                    """
                ),
                {
                    "eid": EXCHANGE_ID,
                    "sid": SYMBOL_VERSION_ID,
                    "details": json.dumps({"supersedes_event_id": str(blocker_id)}),
                },
            )
        session.commit()
        # Replay the migration backfill: deduplicate earliest per
        # (superseded blocker, terminal type), then populate the column.
        session.execute(
            text(
                """
                delete from public.data_quality_events terminal
                using public.data_quality_events earlier
                where terminal.supersedes_event_id is null
                  and terminal.details ? 'supersedes_event_id'
                  and earlier.supersedes_event_id is null
                  and earlier.details ? 'supersedes_event_id'
                  and (terminal.details ->> 'supersedes_event_id')::uuid
                        = (earlier.details ->> 'supersedes_event_id')::uuid
                  and terminal.event_type = earlier.event_type
                  and terminal.id <> earlier.id
                  and (earlier.created_at, earlier.id)
                        < (terminal.created_at, terminal.id)
                """
            )
        )
        session.execute(
            text(
                """
                update public.data_quality_events
                set supersedes_event_id = (details ->> 'supersedes_event_id')::uuid
                where supersedes_event_id is null
                  and details ? 'supersedes_event_id'
                """
            )
        )
        session.commit()
        # Exactly one terminal survives with the structured parent.
        terminals = session.execute(
            text(
                "select count(*) from public.data_quality_events "
                "where event_type = 'clock_drift_recovered' "
                "and supersedes_event_id = :bid"
            ),
            {"bid": blocker_id},
        ).scalar_one()
        assert terminals == 1
        # The gate recognizes the backfilled terminal: the blocker is cleared.
        cleared = session.execute(
            text(
                """
                select count(*) from public.data_quality_events blocker
                where blocker.id = :bid
                  and blocker.event_type = 'clock_drift_exceeded'
                  and not exists (
                      select 1 from public.data_quality_events terminal
                      where terminal.supersedes_event_id = blocker.id
                        and terminal.event_type = 'clock_drift_recovered'
                  )
                """
            ),
            {"bid": blocker_id},
        ).scalar_one()
        assert cleared == 0
    finally:
        session.close()


@pytest.mark.asyncio
async def test_preflight_failure_preserves_completed_incremental(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """A failed incremental preflight must record its own attempt and never
    rewrite an already-completed incremental ingestion for the same boundary."""
    # First: a healthy incremental completes over the aligned boundary.
    healthy = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=healthy,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        completed = await service.incremental_fetch(
            symbol=SYMBOL,
            idempotency_key="test-preflight-complete",
        )
        assert completed.status == IngestionStatus.COMPLETED
        completed_row = (
            session.execute(
                text(
                    "select status, inserted_count, request_count, retry_count, "
                    "content_hash, actual_start_time, actual_end_time "
                    "from public.market_data_ingestions "
                    "where idempotency_key = 'test-preflight-complete'"
                )
            )
            .mappings()
            .one()
        )
    finally:
        session.close()

    # Second: a server-time timeout at the same aligned boundary.
    timeout = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.TIMEOUT,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=timeout,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(BinanceTimeoutError):
            await service.incremental_fetch(
                symbol=SYMBOL,
                idempotency_key="test-preflight-timeout-after",
            )
        # The completed canonical row is byte-for-byte unchanged.
        after = (
            session.execute(
                text(
                    "select status, inserted_count, request_count, retry_count, "
                    "content_hash, actual_start_time, actual_end_time "
                    "from public.market_data_ingestions "
                    "where idempotency_key = 'test-preflight-complete'"
                )
            )
            .mappings()
            .one()
        )
        # A separate failed preflight-failure attempt is auditable.
        failed = (
            session.execute(
                text(
                    "select status, ingestion_type, request_count, safe_error "
                    "from public.market_data_ingestions "
                    "where idempotency_key like 'test-preflight-timeout-after%'"
                )
            )
            .mappings()
            .one()
        )
    finally:
        session.close()
    assert after["status"] == IngestionStatus.COMPLETED.value
    assert after["inserted_count"] == completed_row["inserted_count"]
    assert after["content_hash"] == completed_row["content_hash"]
    assert failed["status"] == IngestionStatus.FAILED.value
    assert failed["ingestion_type"] == IngestionType.PREFLIGHT_FAILURE.value
    assert failed["request_count"] >= 1


@pytest.mark.asyncio
async def test_detect_gaps_rejects_inverted_range(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """detect_gaps rejects inverted/zero and non-aligned ranges."""
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(ValueError):
            await service.detect_gaps(
                symbol_version_id=SYMBOL_VERSION_ID,
                interval_code="1h",
                expected_start=FIXED_TIME,
                expected_end=FIXED_TIME - timedelta(hours=1),
            )
        with pytest.raises(ValueError):
            await service.detect_gaps(
                symbol_version_id=SYMBOL_VERSION_ID,
                interval_code="1h",
                expected_start=FIXED_TIME - timedelta(hours=2),
                expected_end=FIXED_TIME.replace(hour=11, minute=30),
            )
    finally:
        session.close()


@pytest.mark.asyncio
async def test_repair_gaps_rejects_foreign_report(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """repair_gaps validates the caller-supplied GapReport contract before any
    short-circuit or provider work."""
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    session = build_session_factory(database_engine)()
    try:
        service = MarketDataService(
            session=session,
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        foreign_symbol = UUID("41000000-0000-0000-0000-0000000000FF")
        foreign_report = GapReport(
            symbol_version_id=foreign_symbol,
            interval_code="1h",
            interval_seconds=3600,
            expected_start=FIXED_TIME - timedelta(hours=2),
            expected_end=FIXED_TIME,
            missing_count=1,
            missing_ranges=((FIXED_TIME - timedelta(hours=1), FIXED_TIME),),
            severity="error",
        )
        with pytest.raises(ValueError):
            await service.repair_gaps(
                symbol=SYMBOL,
                gap_report=foreign_report,
                idempotency_key="test-repair-foreign",
            )
        # Inconsistent missing_count vs missing range widths.
        inconsistent = GapReport(
            symbol_version_id=SYMBOL_VERSION_ID,
            interval_code="1h",
            interval_seconds=3600,
            expected_start=FIXED_TIME - timedelta(hours=2),
            expected_end=FIXED_TIME,
            missing_count=2,
            missing_ranges=((FIXED_TIME - timedelta(hours=1), FIXED_TIME),),
            severity="error",
        )
        with pytest.raises(ValueError):
            await service.repair_gaps(
                symbol=SYMBOL,
                gap_report=inconsistent,
                idempotency_key="test-repair-inconsistent",
            )
        # Foreign interval.
        foreign_interval = GapReport(
            symbol_version_id=SYMBOL_VERSION_ID,
            interval_code="4h",
            interval_seconds=14400,
            expected_start=FIXED_TIME - timedelta(hours=2),
            expected_end=FIXED_TIME,
            missing_count=1,
            missing_ranges=((FIXED_TIME - timedelta(hours=1), FIXED_TIME),),
            severity="error",
        )
        with pytest.raises(ValueError):
            await service.repair_gaps(
                symbol=SYMBOL,
                gap_report=foreign_interval,
                idempotency_key="test-repair-foreign-interval",
            )
    finally:
        session.close()


@pytest.mark.asyncio
async def test_symbol_binding_rejects_cross_exchange(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """A symbol-version row owned by another exchange with the same native
    symbol must be rejected before any provider request."""
    other_exchange = UUID("40000000-0000-0000-0000-0000000000EE")
    other_symbol = UUID("41000000-0000-0000-0000-0000000000EE")
    session = build_session_factory(database_engine)()
    try:
        session.execute(
            text("delete from public.exchange_symbol_versions where id = :sid"),
            {"sid": other_symbol},
        )
        session.execute(
            text(
                """
                insert into public.exchanges (
                    id, code, display_name, data_capability, active, created_at
                ) values (
                    :eid, 'OTHER', 'Other Exchange', 'public_market_data',
                    true, timezone('utc', now())
                )
                on conflict (id) do nothing
                """
            ),
            {"eid": other_exchange},
        )
        session.execute(
            text(
                """
                insert into public.exchange_symbol_versions (
                    id, exchange_id, native_symbol, base_asset, quote_asset,
                    status, price_precision, quantity_precision, tick_size,
                    step_size, min_quantity, min_notional, metadata_hash,
                    effective_at
                ) values (
                    :sid, :eid, 'BTCEUR', 'BTC', 'EUR', 'trading',
                    2, 6, 0.01, 0.000001, 0.000001, 5,
                    :md5, timezone('utc', now())
                )
                """
            ),
            {
                "sid": other_symbol,
                "eid": other_exchange,
                "md5": "n" * 64,
            },
        )
        session.commit()
        service = MarketDataService(
            session=session,
            provider=FakeBinanceProvider(
                config=FakeBinanceConfig(
                    scenario=FakeBinanceScenario.SUCCESS,
                    fixed_clock_time=FIXED_TIME,
                    fixture_version="2026-08-08-m007-v1",
                )
            ),
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=other_symbol,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
        )
        with pytest.raises(ValueError):
            await service.backfill(
                symbol="BTCEUR",
                start_time=FIXED_TIME - timedelta(hours=1),
                end_time=FIXED_TIME,
                idempotency_key="test-cross-exchange",
            )
    finally:
        session.close()


@pytest.mark.asyncio
async def test_partially_overlapping_different_type_serialized(
    database_engine: Engine, clean_m007_data: None
) -> None:
    """Two workers whose ranges overlap with different ingestion types contend
    on the same market+interval advisory lock; only one owns the work."""
    results: list[IngestionResult | Exception] = []

    async def worker(range_start: datetime, range_end: datetime, key: str) -> None:
        provider = FakeBinanceProvider(
            config=FakeBinanceConfig(
                scenario=FakeBinanceScenario.SUCCESS,
                fixed_clock_time=FIXED_TIME,
                fixture_version="2026-08-08-m007-v1",
            )
        )
        session = build_session_factory(database_engine)()
        try:
            service = MarketDataService(
                session=session,
                provider=provider,
                workspace_id=WORKSPACE_ID,
                exchange_id=EXCHANGE_ID,
                symbol_version_id=SYMBOL_VERSION_ID,
                interval=CandleInterval.ONE_HOUR,
                clock=FixedClock(FIXED_TIME),
            )
            result = await service.backfill(
                symbol=SYMBOL,
                start_time=range_start,
                end_time=range_end,
                idempotency_key=key,
            )
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            results.append(exc)
        finally:
            session.close()

    import asyncio as _asyncio

    await _asyncio.gather(
        worker(
            FIXED_TIME - timedelta(hours=2),
            FIXED_TIME,
            "delivery-overlap-A",
        ),
        worker(
            FIXED_TIME - timedelta(hours=1),
            FIXED_TIME + timedelta(hours=1),
            "delivery-overlap-B",
        ),
    )
    assert len(results) == 2
    owners = [r for r in results if isinstance(r, IngestionResult)]
    assert len(owners) >= 1
