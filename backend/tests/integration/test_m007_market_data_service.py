"""Integration tests for M007 market data service."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Iterator
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.clock import FixedClock
from app.database import build_engine, build_session_factory
from app.domains.market_data.models import (
    GapReport,
    IngestionStatus,
)
from app.domains.market_data.service import MarketDataService
from app.domains.market_data.validation import ValidationPolicy
from app.infrastructure.exchange.binance.fakes import (
    FakeBinanceConfig,
    FakeBinanceProvider,
    FakeBinanceScenario,
)
from app.infrastructure.exchange.binance.protocol import CandleInterval

pytestmark = pytest.mark.database

FIXED_TIME = datetime(2026, 8, 8, 12, 0, 0, tzinfo=timezone.utc)
SYMBOL_VERSION_ID = UUID("41000000-0000-0000-0000-000000000001")
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


@pytest.mark.asyncio
async def test_backfill_inserts_candles(database_engine: Engine) -> None:
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
async def test_incremental_fetch_overlaps_latest(database_engine: Engine) -> None:
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
                on conflict (symbol_version_id, interval_code, open_time) do nothing
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
    assert result.duplicate_count >= 1


@pytest.mark.asyncio
async def test_detect_gaps_bounded_by_latest(database_engine: Engine) -> None:
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
    assert gap_report.expected_end == FIXED_TIME


@pytest.mark.asyncio
async def test_idempotent_backfill_reuses_ingestion(database_engine: Engine) -> None:
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
                "where symbol_version_id = :sid and interval_code = '1h'"
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
