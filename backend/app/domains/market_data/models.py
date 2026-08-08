"""Market data domain models for M007."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class QualityState(str, Enum):
    APPROVED = "approved"
    INCOMPLETE = "incomplete"
    STALE = "stale"
    DUPLICATE_CONSISTENT = "duplicate_consistent"
    DUPLICATE_CONFLICT = "duplicate_conflict"
    INVALID_VALUE = "invalid_value"
    INVALID_INTERVAL = "invalid_interval"
    OUT_OF_ORDER = "out_of_order"
    GAP_DETECTED = "gap_detected"
    GAP_REPAIR_PENDING = "gap_repair_pending"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    RATE_LIMITED = "rate_limited"
    CLOCK_DRIFT_EXCEEDED = "clock_drift_exceeded"
    CORRECTION_PENDING = "correction_pending"
    CORRECTION_APPLIED = "correction_applied"
    QUARANTINED = "quarantined"
    INVALIDATED = "invalidated"


class IngestionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IngestionType(str, Enum):
    BACKFILL = "backfill"
    INCREMENTAL = "incremental"
    GAP_REPAIR = "gap_repair"


@dataclass(frozen=True, slots=True)
class CandleValidationResult:
    candle: object
    quality_state: QualityState
    is_valid: bool
    is_duplicate: bool
    duplicate_conflict: bool
    out_of_order: bool
    invalid_reasons: tuple[str, ...] = ()
    content_hash: str = ""


@dataclass(frozen=True, slots=True)
class QualityEvent:
    event_type: str
    severity: str
    symbol_version_id: UUID
    interval_code: str
    details: dict[str, Any] = field(default_factory=dict)
    affected_candle_id: UUID | None = None
    affected_range_start: datetime | None = None
    affected_range_end: datetime | None = None
    detection_policy_version: str = "1.0"
    resolution: str | None = None
    replacement_candle_id: UUID | None = None
    invalidated_candle_id: UUID | None = None
    ingestion_id: UUID | None = None
    snapshot_id: UUID | None = None
    reviewer_user_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class GapReport:
    symbol_version_id: UUID
    interval_code: str
    interval_seconds: int
    expected_start: datetime
    expected_end: datetime
    missing_count: int
    missing_ranges: tuple[tuple[datetime, datetime], ...]
    severity: str
    detection_policy_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class IngestionResult:
    ingestion_type: IngestionType
    status: IngestionStatus
    inserted_count: int
    duplicate_count: int
    invalid_count: int
    corrected_count: int
    gap_count: int
    retry_count: int
    request_count: int
    provider_latency_ms: int | None
    safe_error: str | None
    content_hash: str
    idempotency_key: str
    actual_start_time: datetime | None = None
    actual_end_time: datetime | None = None


@dataclass(frozen=True, slots=True)
class SnapshotResult:
    snapshot_id: UUID
    snapshot_hash: str
    candle_count: int
    quality_outcome: str
    freshness_outcome: str
    first_event_time: datetime
    last_event_time: datetime
    analysis_time: datetime
