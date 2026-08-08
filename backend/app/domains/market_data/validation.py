"""Candle validation and quality assessment for M007."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.domains.market_data.models import (
    GapReport,
    QualityEvent,
    QualityState,
)

_MAX_CLOCK_DRIFT_MS = 5000
_STALE_THRESHOLD_SECONDS = 3600


@dataclass(frozen=True, slots=True)
class ValidationPolicy:
    max_clock_drift_ms: int = _MAX_CLOCK_DRIFT_MS
    stale_threshold_seconds: int = _STALE_THRESHOLD_SECONDS
    interval_seconds: int = 3600
    policy_version: str = "1.0"


def validate_candle_ohlc(
    open_price: Decimal,
    high_price: Decimal,
    low_price: Decimal,
    close_price: Decimal,
) -> tuple[bool, list[str]]:
    reasons = []
    if open_price <= 0 or high_price <= 0 or low_price <= 0 or close_price <= 0:
        reasons.append("non_positive_price")
    if high_price < max(open_price, close_price, low_price):
        reasons.append("high_below_component")
    if low_price > min(open_price, close_price, high_price):
        reasons.append("low_above_component")
    return len(reasons) == 0, reasons


def validate_candle_times(
    open_time: datetime,
    close_time: datetime,
    interval_seconds: int,
) -> tuple[bool, list[str]]:
    reasons = []
    if close_time <= open_time:
        reasons.append("close_not_after_open")
    expected_duration = (close_time - open_time).total_seconds()
    if expected_duration <= 0:
        reasons.append("non_positive_duration")
    if interval_seconds > 0 and abs(expected_duration - interval_seconds) > 1:
        reasons.append("interval_duration_mismatch")
    return len(reasons) == 0, reasons


def validate_candle_volumes(
    base_volume: Decimal,
    quote_volume: Decimal,
    trade_count: int,
) -> tuple[bool, list[str]]:
    reasons = []
    if base_volume < 0 or quote_volume < 0:
        reasons.append("negative_volume")
    if trade_count < 0:
        reasons.append("negative_trade_count")
    return len(reasons) == 0, reasons


def compute_candle_content_hash(
    symbol_version_id: UUID,
    interval_code: str,
    open_time: datetime,
    close_time: datetime,
    open_price: Decimal,
    high_price: Decimal,
    low_price: Decimal,
    close_price: Decimal,
    base_volume: Decimal,
    quote_volume: Decimal,
    trade_count: int,
) -> str:
    payload = {
        "symbol_version_id": str(symbol_version_id),
        "interval_code": interval_code,
        "open_time": open_time.isoformat(),
        "close_time": close_time.isoformat(),
        "open_price": str(open_price),
        "high_price": str(high_price),
        "low_price": str(low_price),
        "close_price": str(close_price),
        "base_volume": str(base_volume),
        "quote_volume": str(quote_volume),
        "trade_count": trade_count,
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def assess_quality(
    candle: object,
    is_duplicate: bool,
    duplicate_conflict: bool,
    out_of_order: bool,
    invalid_reasons: list[str],
    content_hash: str,
    policy: ValidationPolicy,
    clock_drift_ms: int | None = None,
) -> tuple[QualityState, list[str]]:
    reasons = list(invalid_reasons)
    if out_of_order:
        return QualityState.OUT_OF_ORDER, ["out_of_order"]
    if duplicate_conflict:
        return QualityState.DUPLICATE_CONFLICT, ["duplicate_conflict"]
    if is_duplicate:
        return QualityState.DUPLICATE_CONSISTENT, ["duplicate_consistent"]
    if clock_drift_ms is not None and abs(clock_drift_ms) > policy.max_clock_drift_ms:
        return QualityState.CLOCK_DRIFT_EXCEEDED, ["clock_drift_exceeded"]
    if reasons:
        if (
            "non_positive_price" in reasons
            or "high_below_component" in reasons
            or "low_above_component" in reasons
        ):
            return QualityState.INVALID_VALUE, reasons
        return QualityState.INVALID_VALUE, reasons
    return QualityState.APPROVED, []


def detect_gaps(
    symbol_version_id: UUID,
    interval_code: str,
    interval_seconds: int,
    candles: list[dict[str, Any]],
    existing_open_times: set[datetime],
    policy: ValidationPolicy,
) -> GapReport:
    if not candles:
        return GapReport(
            symbol_version_id=symbol_version_id,
            interval_code=interval_code,
            interval_seconds=interval_seconds,
            expected_start=datetime.min.replace(tzinfo=timezone.utc),
            expected_end=datetime.min.replace(tzinfo=timezone.utc),
            missing_count=0,
            missing_ranges=(),
            severity="info",
            detection_policy_version=policy.policy_version,
        )
    sorted_candles = sorted(candles, key=lambda c: c["open_time"])
    first_time = sorted_candles[0]["open_time"]
    last_time = sorted_candles[-1]["open_time"]
    expected_times: set[datetime] = set()
    current = first_time
    while current <= last_time:
        expected_times.add(current)
        current += timedelta(seconds=interval_seconds)
    missing = sorted(expected_times - existing_open_times)
    if not missing:
        return GapReport(
            symbol_version_id=symbol_version_id,
            interval_code=interval_code,
            interval_seconds=interval_seconds,
            expected_start=first_time,
            expected_end=last_time,
            missing_count=0,
            missing_ranges=(),
            severity="info",
            detection_policy_version=policy.policy_version,
        )
    missing_ranges: list[tuple[datetime, datetime]] = []
    range_start = missing[0]
    range_end = missing[0]
    for t in missing[1:]:
        if t == range_end + timedelta(seconds=interval_seconds):
            range_end = t
        else:
            missing_ranges.append((range_start, range_end))
            range_start = t
            range_end = t
    missing_ranges.append((range_start, range_end))
    return GapReport(
        symbol_version_id=symbol_version_id,
        interval_code=interval_code,
        interval_seconds=interval_seconds,
        expected_start=first_time,
        expected_end=last_time,
        missing_count=len(missing),
        missing_ranges=tuple(missing_ranges),
        severity="error" if len(missing) > 1 else "warning",
        detection_policy_version=policy.policy_version,
    )


def make_quality_event(
    event_type: str,
    severity: str,
    symbol_version_id: UUID,
    interval_code: str,
    details: dict[str, Any] | None = None,
    affected_candle_id: UUID | None = None,
    affected_range_start: datetime | None = None,
    affected_range_end: datetime | None = None,
    detection_policy_version: str = "1.0",
    resolution: str | None = None,
    replacement_candle_id: UUID | None = None,
    invalidated_candle_id: UUID | None = None,
    supersedes_event_id: UUID | None = None,
    ingestion_id: UUID | None = None,
    snapshot_id: UUID | None = None,
    reviewer_user_id: UUID | None = None,
) -> QualityEvent:
    return QualityEvent(
        event_type=event_type,
        severity=severity,
        symbol_version_id=symbol_version_id,
        interval_code=interval_code,
        details=details or {},
        affected_candle_id=affected_candle_id,
        affected_range_start=affected_range_start,
        affected_range_end=affected_range_end,
        detection_policy_version=detection_policy_version,
        resolution=resolution,
        replacement_candle_id=replacement_candle_id,
        invalidated_candle_id=invalidated_candle_id,
        supersedes_event_id=supersedes_event_id,
        ingestion_id=ingestion_id,
        snapshot_id=snapshot_id,
        reviewer_user_id=reviewer_user_id,
    )
