"""Unit tests for M007 market data service logic."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, cast
from uuid import UUID

import pytest

from app.core.clock import FixedClock
from app.domains.market_data.models import (
    GapReport,
    IngestionStatus,
    QualityEvent,
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
        self._scalar_one_or_none_value: Any = None
        self.rowcount = 1

    def scalar_one(self) -> Any:
        return self._scalar_one_value

    def scalar_one_or_none(self) -> Any:
        return self._scalar_one_or_none_value

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
        if "pg_try_advisory_lock" in sql:
            result._scalar_one_value = True
            return result
        if "pg_advisory_unlock" in sql:
            result._scalar_one_value = True
            return result
        if "insert into public.market_data_ingestions" in sql:
            ingestion_id = UUID("00000000-0000-0000-0000-000000000002")
            self.ingestions[ingestion_id] = {"id": ingestion_id, "status": "running"}
            return result
        if "insert into public.candle_corrections" in sql:
            return result
        if "insert into public.market_snapshot_candles" in sql:
            return result
        if "insert into public.market_snapshots" in sql:
            return result
        if "update public.market_snapshots" in sql:
            result._scalars_value = []
            return result
        if "update public.candles" in sql:
            return result
        if "from public.exchange_symbol_versions" in sql:
            result._one_or_none_value = {
                "native_symbol": "BTCEUR",
                "exchange_id": EXCHANGE_ID,
            }
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
                "page_hashes": None,
            }
            return result
        if "from public.data_quality_events" in sql and "count(*)" in sql:
            result._scalar_one_value = 0
            return result
        if "update public.market_data_ingestions" in sql:
            return result
        if "candle.id as id" in sql:
            rows = []
            for c in self.candles.values():
                if c.get("symbol_version_id") == params.get("symbol_version_id"):
                    rows.append(
                        {
                            "id": c.get("id")
                            or UUID("42000000-0000-0000-0000-000000000001"),
                            "open_time": c["open_time"],
                        }
                    )
            result._scalars_value = rows
            return result
        if "max(candle.close_time)" in sql:
            times = [cast(datetime, c["close_time"]) for c in self.candles.values()]
            result._scalar_one_value = max(times) if times else None
            return result
        if "from public.market_snapshots" in sql:
            result._scalar_one_or_none_value = None
            return result
        if "max(candle.open_time)" in sql and "min(candle.open_time)" not in sql:
            times = [cast(datetime, c["open_time"]) for c in self.candles.values()]
            max_time = max(times) if times else None
            result._one_or_none_value = {"max_time": max_time} if max_time else None
            return result
        if "min(candle.open_time)" in sql:
            matched = [
                c
                for c in self.candles.values()
                if c.get("symbol_version_id") == params.get("symbol_version_id")
            ]
            times = [cast(datetime, c["open_time"]) for c in matched]
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
    start, end = service._compute_incremental_range(FIXED_TIME)
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
        expected_start=FIXED_TIME - timedelta(hours=2),
        expected_end=FIXED_TIME,
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
        {
            FIXED_TIME - timedelta(hours=1): "a" * 64,
        },
    )
    hash2 = service._compute_ingestion_hash(
        FIXED_TIME - timedelta(hours=1),
        FIXED_TIME,
        {
            FIXED_TIME - timedelta(hours=1): "a" * 64,
        },
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
        "close_time": FIXED_TIME - timedelta(hours=2),
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
    candle_id = UUID("42000000-0000-0000-0000-000000000001")
    # No candle rows: the boundary falls back to last_event_time + interval.
    assert (
        service._derive_freshness_outcome(
            FIXED_TIME, [candle_id], FIXED_TIME - timedelta(hours=1)
        )
        == "fresh"
    )
    assert (
        service._derive_freshness_outcome(
            FIXED_TIME, [candle_id], FIXED_TIME - timedelta(hours=3)
        )
        == "stale"
    )
    assert (
        service._derive_freshness_outcome(
            FIXED_TIME, [candle_id], FIXED_TIME + timedelta(hours=1)
        )
        == "clock_drift_exceeded"
    )


def test_compute_accepted_boundary_partial() -> None:
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
    boundary = service._compute_accepted_boundary(
        {
            FIXED_TIME - timedelta(hours=2),
            FIXED_TIME - timedelta(hours=1),
        },
        FIXED_TIME - timedelta(hours=2),
        FIXED_TIME,
    )
    assert boundary == FIXED_TIME


def test_compute_accepted_boundary_gap_tail() -> None:
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
    boundary = service._compute_accepted_boundary(
        {FIXED_TIME - timedelta(hours=2)},
        FIXED_TIME - timedelta(hours=2),
        FIXED_TIME,
    )
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


def test_derive_quality_outcome_contiguous() -> None:
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
    outcome = service._derive_quality_outcome(
        [UUID("42000000-0000-0000-0000-000000000001")],
        FIXED_TIME - timedelta(hours=1),
        FIXED_TIME - timedelta(hours=1),
    )
    assert outcome == "approved"


def test_derive_quality_outcome_sparse_membership_rejected() -> None:
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
    # Two candles at 10:00 and 12:00 with 11:00 missing => sparse, rejected.
    session.candles[(SYMBOL_VERSION_ID, "1h", FIXED_TIME - timedelta(hours=2))] = {
        "symbol_version_id": SYMBOL_VERSION_ID,
        "interval_code": "1h",
        "open_time": FIXED_TIME - timedelta(hours=2),
        "close_time": FIXED_TIME - timedelta(hours=1),
        "content_hash": "a" * 64,
        "finalized": True,
    }
    session.candles[(SYMBOL_VERSION_ID, "1h", FIXED_TIME)] = {
        "symbol_version_id": SYMBOL_VERSION_ID,
        "interval_code": "1h",
        "open_time": FIXED_TIME,
        "close_time": FIXED_TIME + timedelta(hours=1),
        "content_hash": "b" * 64,
        "finalized": True,
    }
    outcome = service._derive_quality_outcome(
        [
            UUID("42000000-0000-0000-0000-000000000001"),
            UUID("42000000-0000-0000-0000-000000000002"),
        ],
        FIXED_TIME - timedelta(hours=2),
        FIXED_TIME,
    )
    assert outcome == "incomplete"


def test_apply_correction_preserves_original_and_links_replacement() -> None:
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
    original_id = UUID("42000000-0000-0000-0000-000000000001")
    candle = Candle(
        time=FIXED_TIME - timedelta(hours=1),
        close_time=FIXED_TIME,
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("1.5"),
        quote_volume=Decimal("1530"),
        trade_count=100,
    )
    result = type(
        "CandleValidationResult",
        (),
        {
            "candle": candle,
            "content_hash": "b" * 64,
            "existing_id": original_id,
            "existing_hash": "a" * 64,
        },
    )
    events: list[QualityEvent] = []
    service._apply_correction(
        result, UUID("00000000-0000-0000-0000-000000000002"), events
    )
    assert len(events) == 1
    assert events[0].event_type == QualityState.CORRECTION_APPLIED.value
    # The replacement is persisted as a new row; the original is not mutated.
    replacement = session.candles.get(
        (SYMBOL_VERSION_ID, "1h", FIXED_TIME - timedelta(hours=1))
    )
    assert replacement is not None
    assert replacement["content_hash"] == "b" * 64


@pytest.mark.asyncio
async def test_incremental_fetch_noop_when_range_empty() -> None:
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
    # Latest candle is in the future, so the incremental range is empty.
    session.candles[(SYMBOL_VERSION_ID, "1h", FIXED_TIME + timedelta(hours=2))] = {
        "symbol_version_id": SYMBOL_VERSION_ID,
        "interval_code": "1h",
        "open_time": FIXED_TIME + timedelta(hours=2),
        "close_time": FIXED_TIME + timedelta(hours=3),
        "content_hash": "a" * 64,
        "finalized": True,
    }
    result = await service.incremental_fetch(
        symbol="BTCEUR",
        idempotency_key="test-incremental-noop",
    )
    assert result.status == IngestionStatus.COMPLETED
    assert result.inserted_count == 0
    assert result.duplicate_count == 0


@pytest.mark.asyncio
async def test_repair_gaps_no_missing_returns_completed() -> None:
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


def test_snapshot_idempotent_replay_returns_existing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
    existing_id = UUID("99999999-0000-0000-0000-000000000009")

    class ExistingSnapshotResult(MockResult):
        def __init__(self) -> None:
            super().__init__()
            self._scalar_one_or_none_value = existing_id
            self._scalar_one_value = existing_id

    def fake_execute(statement: Any, params: dict[str, Any] | None = None) -> Any:
        if params is None:
            params = {}
        sql = str(statement).lower()
        if "from public.market_snapshots" in sql:
            return ExistingSnapshotResult()
        if "into public.market_snapshots" in sql:
            return ExistingSnapshotResult()
        return original_execute(statement, params)

    original_execute = session.execute
    session.execute = fake_execute  # type: ignore[method-assign]
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
    assert snapshot.snapshot_id == existing_id


def test_validate_candles_same_page_conflict() -> None:
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
        time=FIXED_TIME - timedelta(hours=1),
        close_time=FIXED_TIME,
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("1.5"),
        quote_volume=Decimal("1530"),
        trade_count=100,
    )
    c2 = Candle(
        time=FIXED_TIME - timedelta(hours=1),
        close_time=FIXED_TIME,
        open=Decimal("101"),
        high=Decimal("106"),
        low=Decimal("96"),
        close=Decimal("103"),
        volume=Decimal("1.6"),
        quote_volume=Decimal("1648"),
        trade_count=101,
    )
    results = service._validate_candles(
        [c1, c2],
        existing_hashes=set(),
        existing_times=set(),
        batch_by_time={},
        clock_drift_ms=0,
    )
    # First candle is accepted as new; second conflicts on the same open time.
    assert results[0].is_duplicate is False
    assert results[1].duplicate_conflict is True
    assert results[1].is_duplicate is False


@pytest.mark.asyncio
async def test_detect_gaps_rejects_identity_mismatch() -> None:
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
    other_svid = UUID("41000000-0000-0000-0000-000000000099")
    with pytest.raises(ValueError):
        await service.detect_gaps(
            symbol_version_id=other_svid,
            interval_code="1h",
        )
    with pytest.raises(ValueError):
        await service.detect_gaps(
            symbol_version_id=SYMBOL_VERSION_ID,
            interval_code="5m",
        )


@pytest.mark.asyncio
async def test_detect_gaps_empty_range_reports_all_missing() -> None:
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
    report = await service.detect_gaps(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        expected_start=FIXED_TIME - timedelta(hours=2),
        expected_end=FIXED_TIME,
    )
    assert report.missing_count == 2
    assert report.severity == "error"


@pytest.mark.asyncio
async def test_detect_gaps_missing_leading_candle() -> None:
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
    session.candles[(SYMBOL_VERSION_ID, "1h", FIXED_TIME)] = {
        "symbol_version_id": SYMBOL_VERSION_ID,
        "interval_code": "1h",
        "open_time": FIXED_TIME,
        "close_time": FIXED_TIME + timedelta(hours=1),
        "content_hash": "a" * 64,
        "finalized": True,
    }
    report = await service.detect_gaps(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        expected_start=FIXED_TIME - timedelta(hours=1),
        expected_end=FIXED_TIME,
    )
    # The leading candle at FIXED_TIME-1h is missing; half-open range
    # [FIXED_TIME-1h, FIXED_TIME).
    assert report.missing_count == 1
    assert report.missing_ranges == ((FIXED_TIME - timedelta(hours=1), FIXED_TIME),)


def test_canonicalize_candle_ids_rejects_shrink() -> None:
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
    valid_id = UUID("42000000-0000-0000-0000-000000000001")
    foreign_id = UUID("42000000-0000-0000-0000-0000000000FF")
    # Foreign id cannot be canonicalized to the same multiset.
    with pytest.raises(ValueError):
        service._canonicalize_candle_ids([valid_id, foreign_id])


@pytest.mark.asyncio
async def test_backfill_partial_page_fails_closed() -> None:
    session = MockSession()
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.GAP,
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
    with pytest.raises(BinanceProviderUnavailableError):
        await service.backfill(
            symbol="BTCEUR",
            start_time=FIXED_TIME - timedelta(hours=8),
            end_time=FIXED_TIME,
            idempotency_key="test-partial-unit",
        )
    row = session.ingestions.get(UUID("00000000-0000-0000-0000-000000000002"))
    assert row is not None


@pytest.mark.asyncio
async def test_backfill_empty_page_fails_closed() -> None:
    session = MockSession()

    class EmptyProvider:
        async def get_server_time(self) -> ExchangeTime:
            return ExchangeTime(server_time=FIXED_TIME, clock_drift_ms=0)

        async def get_finalized_candles(
            self,
            symbol: str,
            interval: CandleInterval,
            start_time: datetime,
            end_time: datetime,
            server_time: datetime | None = None,
        ) -> list[Candle]:
            return []

    service = MarketDataService(
        session=session,  # type: ignore[arg-type]
        provider=EmptyProvider(),  # type: ignore[arg-type]
        workspace_id=WORKSPACE_ID,
        exchange_id=EXCHANGE_ID,
        symbol_version_id=SYMBOL_VERSION_ID,
        interval=CandleInterval.ONE_HOUR,
        clock=FixedClock(FIXED_TIME),
    )
    with pytest.raises(BinanceProviderUnavailableError):
        await service.backfill(
            symbol="BTCEUR",
            start_time=FIXED_TIME - timedelta(hours=2),
            end_time=FIXED_TIME,
            idempotency_key="test-empty-unit",
        )


@pytest.mark.asyncio
async def test_server_time_failure_persists_attempt() -> None:
    session = MockSession()
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.UNAVAILABLE,
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
    with pytest.raises(BinanceProviderUnavailableError):
        await service.backfill(
            symbol="BTCEUR",
            start_time=FIXED_TIME - timedelta(hours=1),
            end_time=FIXED_TIME,
            idempotency_key="test-server-time-fail",
        )
