"""Market data domain package."""

from __future__ import annotations

from app.domains.market_data.models import (
    GapReport,
    IngestionResult,
    IngestionStatus,
    IngestionType,
    QualityEvent,
    QualityState,
    SnapshotResult,
)
from app.domains.market_data.service import MarketDataService
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

__all__ = [
    "GapReport",
    "IngestionResult",
    "IngestionStatus",
    "IngestionType",
    "MarketDataService",
    "QualityEvent",
    "QualityState",
    "SnapshotResult",
    "ValidationPolicy",
    "assess_quality",
    "compute_candle_content_hash",
    "detect_gaps",
    "make_quality_event",
    "validate_candle_ohlc",
    "validate_candle_times",
    "validate_candle_volumes",
]
