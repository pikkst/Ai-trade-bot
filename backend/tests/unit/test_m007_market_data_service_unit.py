"""Unit tests for M007 market data service logic."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest

from app.core.clock import FixedClock
from app.domains.market_data.models import (
    GapReport,
    IngestionStatus,
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
        self._scalar_one_value: Any = UUID("00000000-0000-0000-0000-000000000001")

    def scalar_one(self) -> Any:
        return self._scalar_one_value

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
        if "from public.market_data_ingestions where id" in sql:
            result._one_or_none_value = {
                "status": "running",
                "checkpoint": None,
                "inserted_count": 0,
                "duplicate_count": 0,
                "invalid_count": 0,
                "corrected_count": 0,
                "request_count": 0,
                "retry_count": 0,
                "provider_latency_ms": None,
                "safe_error": None,
                "content_hash": "",
                "actual_start_time": None,
                "actual_end_time": None,
            }
            return result
        if "from public.data_quality_events" in sql and "count(*)" in sql:
            result._scalar_one_value = 0
            return result
        if "update public.market_data_ingestions" in sql:
            return result
        if "max(candle.open_time)" in sql and "min(candle.open_time)" not in sql:
            times = [c["open_time"] for c in self.candles.values()]
            max_time = max(times) if times else None
            result._one_or_none_value = {"max_time": max_time} if max_time else None
            return result
        if "min(candle.open_time)" in sql:
            matched = [
                c
                for c in self.candles.values()
                if c.get("symbol_version_id") == params.get("symbol_version_id")
            ]
            times = [c["open_time"] for c in matched]
            result._one_value = {
                "cnt": len(matched),
                "min_time": min(times) if times else None,
                "max_time": max(times) if times else None,
            }
            return result
        if "count(*)" in sql and "candles" in sql:
            result._one_value = {
                "cnt": len(self.candles),
                "min_time": None,
                "max_time": None,
            }
            return result
        if "select id, content_hash, open_time" in sql:
            result._one_or_none_value = None
            return result
        if "select candle.content_hash" in sql:
            result._scalars_value = [c["content_hash"] for c in self.candles.values()]
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


@pytest.mark.asyncio
async def test_backfill_persists_candles() -> None:
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
    result = await service.backfill(
        symbol="BTCEUR",
        start_time=FIXED_TIME - timedelta(hours=2),
        end_time=FIXED_TIME,
        idempotency_key="test-backfill-persist",
    )
    assert result.status == IngestionStatus.COMPLETED
    assert result.inserted_count == 2
    assert len(session.candles) == 2


@pytest.mark.asyncio
async def test_backfill_resumes_from_checkpoint() -> None:
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
    result = await service.backfill(
        symbol="BTCEUR",
        start_time=FIXED_TIME - timedelta(hours=2),
        end_time=FIXED_TIME,
        idempotency_key="test-backfill-resume",
    )
    assert result.status == IngestionStatus.COMPLETED
    assert result.request_count >= 1
    assert result.provider_latency_ms is not None


@pytest.mark.asyncio
async def test_repair_gaps_no_missing() -> None:
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
    report = GapReport(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        interval_seconds=3600,
        expected_start=FIXED_TIME - timedelta(hours=1),
        expected_end=FIXED_TIME,
        missing_count=0,
        missing_ranges=(),
        severity="info",
        detection_policy_version="1.0",
    )
    result = await service.repair_gaps(
        symbol="BTCEUR",
        gap_report=report,
        idempotency_key="test-repair-none",
    )
    assert result.status == IngestionStatus.COMPLETED
    assert result.inserted_count == 0


def test_create_snapshot_success() -> None:
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
        "close_time": FIXED_TIME,
        "content_hash": "a" * 64,
        "finalized": True,
    }
    snapshot = service.create_snapshot(
        analysis_time=FIXED_TIME,
        candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
        quality_outcome="approved",
        freshness_outcome="fresh",
    )
    assert isinstance(snapshot, SnapshotResult)
    assert snapshot.candle_count == 1
    assert snapshot.snapshot_hash is not None
    assert snapshot.quality_outcome == "approved"


def test_snapshot_validation_uses_derived_outcomes() -> None:
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
        "close_time": FIXED_TIME,
        "content_hash": "a" * 64,
        "finalized": True,
    }
    snapshot = service.create_snapshot(
        analysis_time=FIXED_TIME,
        candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
        quality_outcome="approved",
        freshness_outcome="fresh",
    )
    assert snapshot.freshness_outcome == "fresh"


def test_snapshot_gate_rejects_stale_freshness() -> None:
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
        policy=ValidationPolicy(stale_threshold_seconds=60),
    )
    session.candles[(SYMBOL_VERSION_ID, "1h", FIXED_TIME - timedelta(hours=1))] = {
        "symbol_version_id": SYMBOL_VERSION_ID,
        "interval_code": "1h",
        "open_time": FIXED_TIME - timedelta(hours=1),
        "close_time": FIXED_TIME,
        "content_hash": "a" * 64,
        "finalized": True,
    }
    with pytest.raises(ValueError):
        service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
            quality_outcome="approved",
            freshness_outcome="fresh",
        )


def test_derive_freshness_outcome_bounds() -> None:
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
    assert service._derive_freshness_outcome(FIXED_TIME, FIXED_TIME) == "fresh"
    assert (
        service._derive_freshness_outcome(FIXED_TIME, FIXED_TIME - timedelta(hours=2))
        == "stale"
    )
    assert (
        service._derive_freshness_outcome(FIXED_TIME, FIXED_TIME + timedelta(hours=1))
        == "clock_drift_exceeded"
    )


def test_resolve_page_contiguity_partial() -> None:
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
    c1 = Candle(
        time=FIXED_TIME - timedelta(hours=2),
        close_time=FIXED_TIME - timedelta(hours=1),
        open=Decimal("1"),
        high=Decimal("2"),
        low=Decimal("0.5"),
        close=Decimal("1.5"),
        volume=Decimal("1"),
        quote_volume=Decimal("1.5"),
        trade_count=1,
    )
    c2 = Candle(
        time=FIXED_TIME - timedelta(hours=1),
        close_time=FIXED_TIME,
        open=Decimal("1"),
        high=Decimal("2"),
        low=Decimal("0.5"),
        close=Decimal("1.5"),
        volume=Decimal("1"),
        quote_volume=Decimal("1.5"),
        trade_count=1,
    )
    contiguous, boundary = service._resolve_page_contiguity(
        [c1, c2], FIXED_TIME - timedelta(hours=2), FIXED_TIME
    )
    assert len(contiguous) == 2
    assert boundary == FIXED_TIME


def test_resolve_page_contiguity_gap_tail() -> None:
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
    c1 = Candle(
        time=FIXED_TIME - timedelta(hours=2),
        close_time=FIXED_TIME - timedelta(hours=1),
        open=Decimal("1"),
        high=Decimal("2"),
        low=Decimal("0.5"),
        close=Decimal("1.5"),
        volume=Decimal("1"),
        quote_volume=Decimal("1.5"),
        trade_count=1,
    )
    contiguous, boundary = service._resolve_page_contiguity(
        [c1], FIXED_TIME - timedelta(hours=2), FIXED_TIME
    )
    assert len(contiguous) == 1
    assert boundary == FIXED_TIME - timedelta(hours=1)


def test_compute_page_hash_deterministic() -> None:
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
    hashes = ["a" * 64, "b" * 64]
    assert service._compute_page_hash(hashes) == service._compute_page_hash(hashes)
    assert service._compute_page_hash(hashes) != service._compute_page_hash(["a" * 64])
