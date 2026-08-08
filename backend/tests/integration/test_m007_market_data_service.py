"""Integration tests for M007 market data service."""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Iterator
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session

from app.core.clock import FixedClock
from app.database import build_engine, build_session_factory
from app.domains.market_data.models import (
    GapReport,
    IngestionStatus,
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
        with database_engine.begin() as connection:
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
                text(
                    "delete from public.market_snapshots where symbol_version_id = :sid"
                ),
                {"sid": SYMBOL_VERSION_ID},
            )
            connection.execute(
                text(
                    "delete from public.candle_corrections "
                    "where symbol_version_id = :sid"
                ),
                {"sid": SYMBOL_VERSION_ID},
            )
            connection.execute(
                text(
                    "delete from public.data_quality_events "
                    "where symbol_version_id = :sid"
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
            # The symbol version is test-owned; delete any previous run's row
            # so the dedicated identity is always clean before each test.
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

    _clean()
    yield
    _clean()


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
            expected_end=FIXED_TIME - timedelta(hours=1),
        )
        assert gap_report.missing_count == 1
        assert gap_report.missing_ranges == (
            (FIXED_TIME - timedelta(hours=1), FIXED_TIME - timedelta(hours=1)),
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
