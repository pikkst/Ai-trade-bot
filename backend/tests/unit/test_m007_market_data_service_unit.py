"""Unit tests for M007 market data service logic."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import pytest

from app.core.clock import FixedClock
from app.domains.market_data.service import MarketDataService
from app.domains.market_data.validation import ValidationPolicy
from app.infrastructure.exchange.binance.fakes import (
    FakeBinanceConfig,
    FakeBinanceProvider,
    FakeBinanceScenario,
)
from app.infrastructure.exchange.binance.protocol import (
    BinanceProviderUnavailableError,
    CandleInterval,
    ExchangeTime,
)

FIXED_TIME = datetime(2026, 8, 8, 12, 0, 0, tzinfo=timezone.utc)
SYMBOL_VERSION_ID = UUID("41000000-0000-0000-0000-000000000001")
EXCHANGE_ID = UUID("40000000-0000-0000-0000-000000000001")
WORKSPACE_ID = UUID("20000000-0000-0000-0000-000000000001")


class MockResult:
    def __init__(self) -> None:
        self._one_or_none_value: dict[str, Any] | None = None
        self._one_value: dict[str, Any] = {"cnt": 0, "min_time": None, "max_time": None}
        self._scalars_value: list[Any] = []

    def scalar_one(self) -> UUID:
        return UUID("00000000-0000-0000-0000-000000000001")

    def mappings(self) -> "MockResult":
        return self

    def one_or_none(self) -> dict[str, Any] | None:
        return self._one_or_none_value

    def one(self) -> dict[str, Any]:
        return self._one_value

    def scalars(self) -> "MockResult":
        return self

    def all(self) -> list[Any]:
        return self._scalars_value


class MockSession:
    def __init__(self) -> None:
        self.candles: dict[tuple[UUID, str, datetime], dict[str, Any]] = {}
        self.ingestions: dict[UUID, dict[str, Any]] = {}

    def execute(
        self, statement: Any, params: dict[str, Any] | None = None
    ) -> MockResult:
        if params is None:
            params = {}
        sql = str(statement).lower()
        result = MockResult()
        if "insert into public.candles" in sql:
            key = (
                params["symbol_version_id"],
                params["interval_code"],
                params["open_time"],
            )
            self.candles[key] = {
                "symbol_version_id": params["symbol_version_id"],
                "interval_code": params["interval_code"],
                "open_time": params["open_time"],
                "close_time": params["close_time"],
                "open_price": params["open_price"],
                "high_price": params["high_price"],
                "low_price": params["low_price"],
                "close_price": params["close_price"],
                "base_volume": params["base_volume"],
                "quote_volume": params["quote_volume"],
                "trade_count": params["trade_count"],
                "finalized": True,
                "content_hash": params["content_hash"],
            }
            return result
        if "insert into public.market_data_ingestions" in sql:
            ingestion_id = UUID("00000000-0000-0000-0000-000000000002")
            self.ingestions[ingestion_id] = {"id": ingestion_id, "status": "running"}
            return result
        if "max(candle.open_time)" in sql:
            times = [c["open_time"] for c in self.candles.values()]
            max_time = max(times) if times else None
            result._one_or_none_value = {"max_time": max_time} if max_time else None
            return result
        if "count(*)" in sql and "candles" in sql:
            result._one_value = {
                "cnt": len(self.candles),
                "min_time": None,
                "max_time": None,
            }
            return result
        if "select candle.open_time" in sql:
            result._scalars_value = [c["open_time"] for c in self.candles.values()]
            return result
        return result

    def commit(self) -> None:
        pass


def test_incremental_overlap_from_latest() -> None:
    session = MockSession()
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    service = MarketDataService(
        session=session,  # type: ignore[arg-type]
        provider=provider,
        workspace_id=WORKSPACE_ID,
        exchange_id=EXCHANGE_ID,
        symbol_version_id=SYMBOL_VERSION_ID,
        interval=CandleInterval.ONE_HOUR,
        clock=FixedClock(FIXED_TIME),
    )
    session.candles[(SYMBOL_VERSION_ID, "1h", FIXED_TIME - timedelta(hours=1))] = {
        "symbol_version_id": SYMBOL_VERSION_ID,
        "interval_code": "1h",
        "open_time": FIXED_TIME - timedelta(hours=1),
        "close_time": FIXED_TIME - timedelta(hours=1),
        "content_hash": "a" * 64,
        "finalized": True,
    }
    start, end = service._compute_incremental_range()
    assert start == FIXED_TIME - timedelta(hours=2)
    assert end == FIXED_TIME


@pytest.mark.asyncio
async def test_gap_detection_bounded_by_latest() -> None:
    session = MockSession()
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    service = MarketDataService(
        session=session,  # type: ignore[arg-type]
        provider=provider,
        workspace_id=WORKSPACE_ID,
        exchange_id=EXCHANGE_ID,
        symbol_version_id=SYMBOL_VERSION_ID,
        interval=CandleInterval.ONE_HOUR,
        clock=FixedClock(FIXED_TIME),
    )
    for hour in range(3):
        session.candles[
            (SYMBOL_VERSION_ID, "1h", FIXED_TIME - timedelta(hours=hour))
        ] = {
            "symbol_version_id": SYMBOL_VERSION_ID,
            "interval_code": "1h",
            "open_time": FIXED_TIME - timedelta(hours=hour),
            "finalized": True,
        }
    report = await service.detect_gaps(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
    )
    assert report.missing_count == 0
    assert report.expected_end == FIXED_TIME


def test_clock_drift_enforced() -> None:
    session = MockSession()
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    service = MarketDataService(
        session=session,  # type: ignore[arg-type]
        provider=provider,
        workspace_id=WORKSPACE_ID,
        exchange_id=EXCHANGE_ID,
        symbol_version_id=SYMBOL_VERSION_ID,
        interval=CandleInterval.ONE_HOUR,
        clock=FixedClock(FIXED_TIME),
        policy=ValidationPolicy(max_clock_drift_ms=100),
    )
    server_time = ExchangeTime(
        server_time=FIXED_TIME + timedelta(milliseconds=200),
        clock_drift_ms=200,
    )
    with pytest.raises(BinanceProviderUnavailableError):
        service._check_clock_drift(server_time)


def test_ingestion_hash_deterministic() -> None:
    session = MockSession()
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    service = MarketDataService(
        session=session,  # type: ignore[arg-type]
        provider=provider,
        workspace_id=WORKSPACE_ID,
        exchange_id=EXCHANGE_ID,
        symbol_version_id=SYMBOL_VERSION_ID,
        interval=CandleInterval.ONE_HOUR,
        clock=FixedClock(FIXED_TIME),
    )
    hash1 = service._compute_ingestion_hash(
        FIXED_TIME - timedelta(hours=1),
        FIXED_TIME,
        1,
        0,
        0,
        0,
        1,
    )
    hash2 = service._compute_ingestion_hash(
        FIXED_TIME - timedelta(hours=1),
        FIXED_TIME,
        1,
        0,
        0,
        0,
        1,
    )
    assert hash1 == hash2
    assert len(hash1) == 64


def test_snapshot_membership_validated() -> None:
    session = MockSession()
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    service = MarketDataService(
        session=session,  # type: ignore[arg-type]
        provider=provider,
        workspace_id=WORKSPACE_ID,
        exchange_id=EXCHANGE_ID,
        symbol_version_id=SYMBOL_VERSION_ID,
        interval=CandleInterval.ONE_HOUR,
        clock=FixedClock(FIXED_TIME),
    )
    other_svid = UUID("41000000-0000-0000-0000-000000000002")
    session.candles[(other_svid, "1h", FIXED_TIME - timedelta(hours=1))] = {
        "symbol_version_id": other_svid,
        "interval_code": "1h",
        "open_time": FIXED_TIME - timedelta(hours=1),
        "finalized": True,
        "id": UUID("42000000-0000-0000-0000-000000000001"),
    }
    with pytest.raises(ValueError):
        service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
            quality_outcome="approved",
            freshness_outcome="fresh",
        )
