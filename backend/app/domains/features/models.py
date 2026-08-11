"""Feature engineering domain models for M008."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID


class FeatureStatus(StrEnum):
    COMPLETED = "completed"
    INSUFFICIENT_HISTORY = "insufficient_history"
    INVALID_SOURCE = "invalid_source"
    DIVISION_BY_ZERO = "division_by_zero"
    CALCULATION_ERROR = "calculation_error"
    CANCELLED = "cancelled"


class FeatureCode(StrEnum):
    SMA_20 = "sma_20"
    EMA_20 = "ema_20"
    EMA_50 = "ema_50"
    RSI_14 = "rsi_14"
    ATR_14 = "atr_14"
    RETURNS_SIMPLE = "returns_simple"
    RETURNS_LOG = "returns_log"
    VOLATILITY_ROLLING_20 = "volatility_rolling_20"
    VOLUME_RELATIVE_20 = "volume_relative_20"


@dataclass(frozen=True, slots=True)
class FeatureSetVersion:
    id: UUID
    workspace_id: UUID
    name: str
    semantic_version: str
    implementation_reference: str
    configuration_hash: str
    required_history: int
    warm_up_policy: str
    status: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class FeatureCalculation:
    id: UUID
    snapshot_id: UUID
    feature_set_version_id: UUID
    idempotency_key: str
    status: str
    input_hash: str
    output_hash: str
    calculation_started_at: datetime
    calculation_completed_at: datetime | None = None
    warnings: tuple[str, ...] = ()
    error_message: str | None = None
    creator_cycle_id: str | None = None


@dataclass(frozen=True, slots=True)
class FeatureValue:
    calculation_id: UUID
    feature_code: str
    numeric_value: Decimal | None = None
    string_value: str | None = None
    boolean_value: bool | None = None
    unit: str = ""
    sequence: int = 0
    timestamp: datetime | None = None
    null_reason: str | None = None
