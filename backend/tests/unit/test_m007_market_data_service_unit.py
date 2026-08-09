"""Unit tests for M007 market data service logic."""

from __future__ import annotations

import asyncio
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

    def __iter__(self) -> Any:
        return iter(self._scalars_value)


class MockSession:
    def __init__(self) -> None:
        self.candles: dict[tuple[UUID, str, datetime], dict[str, Any]] = {}
        self.ingestions: dict[UUID, dict[str, Any]] = {}

    def execute(
        self, statement: Any, params: dict[str, Any] | None = None
    ) -> MockResult:
        if params is None:
            params = {}
        sql = " ".join(str(statement).lower().split())
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
            self.ingestions[ingestion_id] = {
                "id": ingestion_id,
                "status": "running",
                "page_hashes": None,
            }
            result._scalar_one_value = ingestion_id
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
        if "select min(effective_at) from public.exchange_symbol_versions" in sql:
            result._scalar_one_value = None
            return result
        if "select effective_at from public.exchange_symbol_versions" in sql:
            result._scalar_one_value = FIXED_TIME
            return result
        if "from public.exchange_symbol_versions" in sql:
            result._one_or_none_value = {
                "id": SYMBOL_VERSION_ID,
                "native_symbol": "BTCEUR",
                "exchange_id": EXCHANGE_ID,
                "superseded_by": None,
                "retrieved_at": FIXED_TIME,
            }
            return result
        if "from public.market_data_ingestions where id" in sql:
            ingestion_id = params.get("ingestion_id")
            ingestion = self.ingestions.get(ingestion_id) if ingestion_id else None
            if ingestion is None:
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
            else:
                result._one_or_none_value = {
                    "exchange_id": EXCHANGE_ID,
                    "symbol_version_id": SYMBOL_VERSION_ID,
                    "interval_code": "1h",
                    "status": IngestionStatus.COMPLETED.value,
                    "requested_start_time": FIXED_TIME - timedelta(hours=2),
                    "requested_end_time": FIXED_TIME,
                    "page_hashes": ingestion.get("page_hashes"),
                }
            return result
        if "from public.data_quality_events" in sql and "count(*)" in sql:
            result._scalar_one_value = 0
            return result
        if "update public.market_data_ingestions" in sql:
            ingestion_id = params.get("id") or params.get("ingestion_id")
            if ingestion_id in self.ingestions:
                update_fields = {}
                if "status" in params:
                    update_fields["status"] = params["status"]
                if "safe_error" in params:
                    update_fields["safe_error"] = params["safe_error"]
                if "content_hash" in params:
                    update_fields["content_hash"] = params["content_hash"]
                if "actual_start_time" in params:
                    update_fields["actual_start_time"] = params["actual_start_time"]
                if "actual_end_time" in params:
                    update_fields["actual_end_time"] = params["actual_end_time"]
                if "checkpoint" in params:
                    update_fields["checkpoint"] = params["checkpoint"]
                self.ingestions[ingestion_id].update(update_fields)
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
            open_time = params.get("open_time")
            for c in self.candles.values():
                if (
                    c.get("symbol_version_id") == params.get("symbol_version_id")
                    and c.get("interval_code") == params.get("interval_code")
                    and c.get("open_time") == open_time
                ):
                    result._scalar_one_or_none_value = c["content_hash"]
                    break
            else:
                result._scalar_one_or_none_value = None
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
        "close_time": FIXED_TIME - timedelta(hours=2),
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
    session.ingestions[UUID("00000000-0000-0000-0000-000000000002")] = {
        "id": UUID("00000000-0000-0000-0000-000000000002"),
        "status": "completed",
        "page_hashes": [],
    }
    with pytest.raises(ValueError):
        service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
            quality_outcome="approved",
            freshness_outcome="fresh",
            ingestion_id=UUID("00000000-0000-0000-0000-000000000002"),
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
    # Seed the expected candle so re-verification proves the dataset is
    # actually gap-free (a zero-gap report is only certified against
    # persisted evidence).
    session.candles[(SYMBOL_VERSION_ID, "1h", FIXED_TIME - timedelta(hours=1))] = {
        "symbol_version_id": SYMBOL_VERSION_ID,
        "interval_code": "1h",
        "open_time": FIXED_TIME - timedelta(hours=1),
        "close_time": FIXED_TIME,
        "content_hash": "a" * 64,
        "finalized": True,
    }
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
    session.ingestions[UUID("00000000-0000-0000-0000-000000000002")] = {
        "id": UUID("00000000-0000-0000-0000-000000000002"),
        "status": "completed",
        "page_hashes": [[(FIXED_TIME - timedelta(hours=1)).isoformat(), "a" * 64]],
    }
    snapshot = service.create_snapshot(
        analysis_time=FIXED_TIME,
        candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
        quality_outcome="approved",
        freshness_outcome="fresh",
        ingestion_id=UUID("00000000-0000-0000-0000-000000000002"),
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
    session.ingestions[UUID("00000000-0000-0000-0000-000000000002")] = {
        "id": UUID("00000000-0000-0000-0000-000000000002"),
        "status": "completed",
        "page_hashes": [[(FIXED_TIME - timedelta(hours=1)).isoformat(), "a" * 64]],
    }
    snapshot = service.create_snapshot(
        analysis_time=FIXED_TIME,
        candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
        quality_outcome="approved",
        freshness_outcome="fresh",
        ingestion_id=UUID("00000000-0000-0000-0000-000000000002"),
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
    session.ingestions[UUID("00000000-0000-0000-0000-000000000002")] = {
        "id": UUID("00000000-0000-0000-0000-000000000002"),
        "status": "completed",
        "page_hashes": [[(FIXED_TIME - timedelta(hours=1)).isoformat(), "a" * 64]],
    }
    with pytest.raises(ValueError):
        service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
            quality_outcome="approved",
            freshness_outcome="fresh",
            ingestion_id=UUID("00000000-0000-0000-0000-000000000002"),
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


def test_snapshot_hash_includes_policy_versions() -> None:
    """The snapshot content hash must bind the policy and schema versions so a
    different policy version with identical labels cannot collide."""
    session = MockSession()
    provider = FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=FakeBinanceScenario.SUCCESS,
            fixed_clock_time=FIXED_TIME,
            fixture_version="2026-08-08-m007-v1",
        )
    )
    candle_ids = [UUID("42000000-0000-0000-0000-000000000001")]

    def make_service(policy_version: str) -> MarketDataService:
        return MarketDataService(
            session=session,  # type: ignore[arg-type]
            provider=provider,
            workspace_id=WORKSPACE_ID,
            exchange_id=EXCHANGE_ID,
            symbol_version_id=SYMBOL_VERSION_ID,
            interval=CandleInterval.ONE_HOUR,
            clock=FixedClock(FIXED_TIME),
            policy=ValidationPolicy(
                interval_seconds=3600,
                policy_version=policy_version,
            ),
        )

    v1 = make_service("policy-v1")
    v2 = make_service("policy-v2")
    kwargs = {
        "analysis_time": FIXED_TIME,
        "first_time": FIXED_TIME - timedelta(hours=1),
        "last_time": FIXED_TIME - timedelta(hours=1),
        "count": 1,
        "quality_outcome": "approved",
        "freshness_outcome": "fresh",
    }
    hash_v1 = v1._compute_snapshot_hash(candle_ids, **kwargs)
    hash_v2 = v2._compute_snapshot_hash(candle_ids, **kwargs)
    assert hash_v1 != hash_v2
    assert v1._compute_snapshot_hash(candle_ids, **kwargs) == hash_v1


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
    assert result.status == IngestionStatus.FAILED
    assert result.safe_error == "future_persisted_candle_or_invalid_range"
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
    # Seed the expected candle so re-verification proves the dataset is
    # actually gap-free (a zero-gap report is only certified against
    # persisted evidence).
    session.candles[(SYMBOL_VERSION_ID, "1h", FIXED_TIME - timedelta(hours=1))] = {
        "symbol_version_id": SYMBOL_VERSION_ID,
        "interval_code": "1h",
        "open_time": FIXED_TIME - timedelta(hours=1),
        "close_time": FIXED_TIME,
        "content_hash": "a" * 64,
        "finalized": True,
    }
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
    session.ingestions[UUID("00000000-0000-0000-0000-000000000002")] = {
        "id": UUID("00000000-0000-0000-0000-000000000002"),
        "status": "completed",
        "page_hashes": [[(FIXED_TIME - timedelta(hours=1)).isoformat(), "a" * 64]],
    }
    snapshot = service.create_snapshot(
        analysis_time=FIXED_TIME,
        candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
        quality_outcome="approved",
        freshness_outcome="fresh",
        ingestion_id=UUID("00000000-0000-0000-0000-000000000002"),
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


def test_incremental_range_bounded_by_max_range_stale_latest() -> None:
    session = MockSession()
    service = MarketDataService(
        session=session,  # type: ignore[arg-type]
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
        incremental_max_range_hours=2,
    )
    session.candles[(SYMBOL_VERSION_ID, "1h", FIXED_TIME - timedelta(hours=10))] = {
        "symbol_version_id": SYMBOL_VERSION_ID,
        "interval_code": "1h",
        "open_time": FIXED_TIME - timedelta(hours=10),
        "close_time": FIXED_TIME - timedelta(hours=9),
        "content_hash": "a" * 64,
        "finalized": True,
    }
    start, end = service._compute_incremental_range(FIXED_TIME)
    assert end == FIXED_TIME
    assert start == FIXED_TIME - timedelta(hours=2)


def test_validate_candle_times_rejects_non_aligned() -> None:
    from app.domains.market_data.validation import validate_candle_times

    ok, reasons = validate_candle_times(
        open_time=FIXED_TIME.replace(minute=30),
        close_time=FIXED_TIME.replace(minute=30) + timedelta(hours=1),
        interval_seconds=3600,
    )
    assert not ok
    assert "interval_alignment_mismatch" in reasons


@pytest.mark.asyncio
async def test_out_of_order_page_no_canonical_mutation() -> None:
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
    c_earlier = Candle(
        time=FIXED_TIME - timedelta(hours=2),
        close_time=FIXED_TIME - timedelta(hours=1),
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("1.5"),
        quote_volume=Decimal("1530"),
        trade_count=100,
    )
    c_later = Candle(
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
        [c_later, c_earlier],
        existing_hashes=set(),
        existing_times=set(),
        batch_by_time={},
        clock_drift_ms=0,
    )
    assert all(r.out_of_order for r in results)
    assert all(r.is_valid for r in results)
    assert all(not r.is_duplicate for r in results)
    assert session.candles == {}


def test_snapshot_lineage_rejects_missing_page_hashes() -> None:
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
    session.ingestions[UUID("00000000-0000-0000-0000-000000000002")] = {
        "id": UUID("00000000-0000-0000-0000-000000000002"),
        "status": "completed",
        "page_hashes": None,
    }
    with pytest.raises(ValueError, match="no accepted page evidence"):
        service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
            quality_outcome="approved",
            freshness_outcome="fresh",
            ingestion_id=UUID("00000000-0000-0000-0000-000000000002"),
        )


def test_snapshot_lineage_rejects_hash_mismatch() -> None:
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
    session.ingestions[UUID("00000000-0000-0000-0000-000000000002")] = {
        "id": UUID("00000000-0000-0000-0000-000000000002"),
        "status": "completed",
        "page_hashes": [[(FIXED_TIME - timedelta(hours=1)).isoformat(), "b" * 64]],
    }
    with pytest.raises(ValueError, match="has hash .* but ingestion"):
        service.create_snapshot(
            analysis_time=FIXED_TIME,
            candle_ids=[UUID("42000000-0000-0000-0000-000000000001")],
            quality_outcome="approved",
            freshness_outcome="fresh",
            ingestion_id=UUID("00000000-0000-0000-0000-000000000002"),
        )


@pytest.mark.asyncio
async def test_incremental_preflight_cancelled_persists_cancelled() -> None:
    session = MockSession()

    class CancellingProvider:
        async def get_server_time(self) -> Any:
            raise asyncio.CancelledError()

        async def get_symbol_metadata(self, symbol: str) -> Any:
            raise asyncio.CancelledError()

        async def get_finalized_candles(
            self,
            symbol: str,
            interval: Any,
            start_time: datetime,
            end_time: datetime,
            server_time: datetime | None = None,
        ) -> list[Any]:
            raise asyncio.CancelledError()

        async def get_rate_limit_state(self) -> Any:
            raise asyncio.CancelledError()

        async def get_health(self) -> Any:
            raise asyncio.CancelledError()

    service = MarketDataService(
        session=session,  # type: ignore[arg-type]
        provider=CancellingProvider(),  # type: ignore[arg-type]
        workspace_id=WORKSPACE_ID,
        exchange_id=EXCHANGE_ID,
        symbol_version_id=SYMBOL_VERSION_ID,
        interval=CandleInterval.ONE_HOUR,
        clock=FixedClock(FIXED_TIME),
    )
    with pytest.raises(asyncio.CancelledError):
        await service.incremental_fetch(
            symbol="BTCEUR",
            idempotency_key="test-preflight-cancelled",
        )
    rows = list(session.ingestions.values())
    assert len(rows) == 1
    assert rows[0]["status"] == "cancelled"
