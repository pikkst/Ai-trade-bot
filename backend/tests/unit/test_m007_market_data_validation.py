"""Tests for M007 market data domain models and validation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from app.domains.market_data.models import (
    IngestionResult,
    IngestionStatus,
    IngestionType,
    QualityEvent,
    QualityState,
    SnapshotResult,
)
from app.domains.market_data.validation import (
    ValidationPolicy,
    assess_quality,
    compute_candle_content_hash,
    detect_gaps,
    make_quality_event,
    validate_candle_ohlc,
    validate_candle_times,
    validate_candle_volumes,
)

FIXED_TIME = datetime(2026, 8, 8, 12, 0, 0, tzinfo=timezone.utc)
SYMBOL_VERSION_ID = UUID("41000000-0000-0000-0000-000000000001")
EXCHANGE_ID = UUID("40000000-0000-0000-0000-000000000001")
WORKSPACE_ID = UUID("20000000-0000-0000-0000-000000000001")


def test_validate_candle_ohlc_valid() -> None:
    valid, reasons = validate_candle_ohlc(
        Decimal("100.00"), Decimal("105.00"), Decimal("95.00"), Decimal("102.00")
    )
    assert valid is True
    assert reasons == []


def test_validate_candle_ohlc_non_positive() -> None:
    valid, reasons = validate_candle_ohlc(
        Decimal("0.00"), Decimal("105.00"), Decimal("95.00"), Decimal("102.00")
    )
    assert valid is False
    assert "non_positive_price" in reasons


def test_validate_candle_ohlc_high_below_component() -> None:
    valid, reasons = validate_candle_ohlc(
        Decimal("100.00"), Decimal("99.00"), Decimal("95.00"), Decimal("102.00")
    )
    assert valid is False
    assert "high_below_component" in reasons


def test_validate_candle_ohlc_low_above_component() -> None:
    valid, reasons = validate_candle_ohlc(
        Decimal("100.00"), Decimal("105.00"), Decimal("101.00"), Decimal("102.00")
    )
    assert valid is False
    assert "low_above_component" in reasons


def test_validate_candle_times_valid() -> None:
    start = FIXED_TIME
    end = FIXED_TIME + timedelta(hours=1)
    valid, reasons = validate_candle_times(start, end, 3600)
    assert valid is True
    assert reasons == []


def test_validate_candle_times_close_not_after_open() -> None:
    valid, reasons = validate_candle_times(FIXED_TIME, FIXED_TIME, 3600)
    assert valid is False
    assert "close_not_after_open" in reasons


def test_validate_candle_volumes_valid() -> None:
    valid, reasons = validate_candle_volumes(Decimal("1.5"), Decimal("1500.00"), 100)
    assert valid is True
    assert reasons == []


def test_validate_candle_volumes_negative() -> None:
    valid, reasons = validate_candle_volumes(Decimal("-1.0"), Decimal("1500.00"), 100)
    assert valid is False
    assert "negative_volume" in reasons


def test_compute_candle_content_hash_deterministic() -> None:
    hash1 = compute_candle_content_hash(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        open_time=FIXED_TIME,
        close_time=FIXED_TIME,
        open_price=Decimal("100.00"),
        high_price=Decimal("105.00"),
        low_price=Decimal("95.00"),
        close_price=Decimal("102.00"),
        base_volume=Decimal("1.5"),
        quote_volume=Decimal("1500.00"),
        trade_count=100,
    )
    hash2 = compute_candle_content_hash(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        open_time=FIXED_TIME,
        close_time=FIXED_TIME,
        open_price=Decimal("100.00"),
        high_price=Decimal("105.00"),
        low_price=Decimal("95.00"),
        close_price=Decimal("102.00"),
        base_volume=Decimal("1.5"),
        quote_volume=Decimal("1500.00"),
        trade_count=100,
    )
    assert hash1 == hash2
    assert len(hash1) == 64


def test_compute_candle_content_hash_changes_with_input() -> None:
    hash1 = compute_candle_content_hash(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        open_time=FIXED_TIME,
        close_time=FIXED_TIME,
        open_price=Decimal("100.00"),
        high_price=Decimal("105.00"),
        low_price=Decimal("95.00"),
        close_price=Decimal("102.00"),
        base_volume=Decimal("1.5"),
        quote_volume=Decimal("1500.00"),
        trade_count=100,
    )
    hash2 = compute_candle_content_hash(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        open_time=FIXED_TIME,
        close_time=FIXED_TIME,
        open_price=Decimal("100.01"),
        high_price=Decimal("105.00"),
        low_price=Decimal("95.00"),
        close_price=Decimal("102.00"),
        base_volume=Decimal("1.5"),
        quote_volume=Decimal("1500.00"),
        trade_count=100,
    )
    assert hash1 != hash2


def test_assess_quality_approved() -> None:
    state, reasons = assess_quality(
        candle=None,
        is_duplicate=False,
        duplicate_conflict=False,
        out_of_order=False,
        invalid_reasons=[],
        content_hash="abc",
        policy=ValidationPolicy(),
    )
    assert state == QualityState.APPROVED
    assert reasons == []


def test_assess_quality_invalid_value() -> None:
    state, reasons = assess_quality(
        candle=None,
        is_duplicate=False,
        duplicate_conflict=False,
        out_of_order=False,
        invalid_reasons=["non_positive_price"],
        content_hash="abc",
        policy=ValidationPolicy(),
    )
    assert state == QualityState.INVALID_VALUE
    assert "non_positive_price" in reasons


def test_assess_quality_out_of_order() -> None:
    state, reasons = assess_quality(
        candle=None,
        is_duplicate=False,
        duplicate_conflict=False,
        out_of_order=True,
        invalid_reasons=[],
        content_hash="abc",
        policy=ValidationPolicy(),
    )
    assert state == QualityState.OUT_OF_ORDER
    assert reasons == ["out_of_order"]


def test_assess_quality_duplicate_conflict() -> None:
    state, reasons = assess_quality(
        candle=None,
        is_duplicate=False,
        duplicate_conflict=True,
        out_of_order=False,
        invalid_reasons=[],
        content_hash="abc",
        policy=ValidationPolicy(),
    )
    assert state == QualityState.DUPLICATE_CONFLICT
    assert reasons == ["duplicate_conflict"]


def test_assess_quality_duplicate_consistent() -> None:
    state, reasons = assess_quality(
        candle=None,
        is_duplicate=True,
        duplicate_conflict=False,
        out_of_order=False,
        invalid_reasons=[],
        content_hash="abc",
        policy=ValidationPolicy(),
    )
    assert state == QualityState.DUPLICATE_CONSISTENT
    assert reasons == ["duplicate_consistent"]


def test_detect_gaps_no_missing() -> None:
    candles = [
        {"open_time": FIXED_TIME},
        {"open_time": FIXED_TIME + timedelta(hours=1)},
        {"open_time": FIXED_TIME + timedelta(hours=2)},
    ]
    existing = {
        FIXED_TIME,
        FIXED_TIME + timedelta(hours=1),
        FIXED_TIME + timedelta(hours=2),
    }
    report = detect_gaps(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        interval_seconds=3600,
        candles=candles,
        existing_open_times=existing,
        policy=ValidationPolicy(),
    )
    assert report.missing_count == 0
    assert report.missing_ranges == ()
    assert report.severity == "info"


def test_detect_gaps_single_missing() -> None:
    candles = [
        {"open_time": FIXED_TIME},
        {"open_time": FIXED_TIME + timedelta(hours=2)},
    ]
    existing = {FIXED_TIME, FIXED_TIME + timedelta(hours=2)}
    report = detect_gaps(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        interval_seconds=3600,
        candles=candles,
        existing_open_times=existing,
        policy=ValidationPolicy(),
    )
    assert report.missing_count == 1
    expected_range = (
        FIXED_TIME + timedelta(hours=1),
        FIXED_TIME + timedelta(hours=1),
    )
    assert report.missing_ranges == (expected_range,)
    assert report.severity == "warning"


def test_detect_gaps_multiple_missing() -> None:
    candles = [
        {"open_time": FIXED_TIME},
        {"open_time": FIXED_TIME + timedelta(hours=3)},
    ]
    existing = {FIXED_TIME, FIXED_TIME + timedelta(hours=3)}
    report = detect_gaps(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        interval_seconds=3600,
        candles=candles,
        existing_open_times=existing,
        policy=ValidationPolicy(),
    )
    assert report.missing_count == 2
    assert len(report.missing_ranges) == 1
    assert report.severity == "error"


def test_detect_gaps_empty_candles() -> None:
    report = detect_gaps(
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        interval_seconds=3600,
        candles=[],
        existing_open_times=set(),
        policy=ValidationPolicy(),
    )
    assert report.missing_count == 0
    assert report.severity == "info"


def test_make_quality_event() -> None:
    event = make_quality_event(
        event_type="gap_detected",
        severity="error",
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
        details={"missing_count": 2},
        ingestion_id=UUID("12345678-1234-1234-1234-123456789abc"),
    )
    assert event.event_type == "gap_detected"
    assert event.severity == "error"
    assert event.symbol_version_id == SYMBOL_VERSION_ID
    assert event.details["missing_count"] == 2


def test_quality_event_defaults() -> None:
    event = QualityEvent(
        event_type="approved",
        severity="info",
        symbol_version_id=SYMBOL_VERSION_ID,
        interval_code="1h",
    )
    assert event.detection_policy_version == "1.0"
    assert event.affected_candle_id is None
    assert event.ingestion_id is None


def test_ingestion_result_defaults() -> None:
    result = IngestionResult(
        ingestion_type=IngestionType.BACKFILL,
        status=IngestionStatus.COMPLETED,
        inserted_count=10,
        duplicate_count=0,
        invalid_count=0,
        corrected_count=0,
        gap_count=0,
        retry_count=0,
        request_count=1,
        provider_latency_ms=500,
        safe_error=None,
        content_hash="abc123",
        idempotency_key="key-1",
    )
    assert result.actual_start_time is None
    assert result.actual_end_time is None


def test_snapshot_result_fields() -> None:
    result = SnapshotResult(
        snapshot_id=UUID("12345678-1234-1234-1234-123456789abc"),
        snapshot_hash="def456",
        candle_count=100,
        quality_outcome="approved",
        freshness_outcome="fresh",
        first_event_time=FIXED_TIME,
        last_event_time=FIXED_TIME + timedelta(hours=99),
        analysis_time=FIXED_TIME + timedelta(hours=100),
    )
    assert result.candle_count == 100
    assert result.snapshot_hash == "def456"


def test_validation_policy_defaults() -> None:
    policy = ValidationPolicy()
    assert policy.max_clock_drift_ms == 5000
    assert policy.stale_threshold_seconds == 3600
    assert policy.interval_seconds == 3600
    assert policy.policy_version == "1.0"
