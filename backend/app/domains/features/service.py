"""Deterministic feature engineering service for M008."""

from __future__ import annotations

import hashlib
import json
import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, getcontext
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.clock import Clock, get_clock
from app.domains.features.models import (
    FeatureCalculation,
    FeatureCode,
    FeatureSetVersion,
    FeatureStatus,
    FeatureValue,
)
from app.domains.market_data.models import QualityState
from app.transaction_guard import assert_network_call_allowed

getcontext().prec = 28

logger = logging.getLogger(__name__)

_FEATURE_SCHEMA_VERSION = "1.0"
_WARM_UP_NULL_REASON = "insufficient_history"
_DEFAULT_REQUIRED_HISTORY = 60
_MIN_HISTORY_FOR_RETURNS = 1
_MIN_HISTORY_FOR_SMA = 1
_MIN_HISTORY_FOR_EMA = 1
_MIN_HISTORY_FOR_RSI = 14
_MIN_HISTORY_FOR_ATR = 14
_MIN_HISTORY_FOR_VOLATILITY = 21
_MIN_HISTORY_FOR_VOLUME_RELATIVE = 20


@dataclass(frozen=True, slots=True)
class CandleData:
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    quote_volume: Decimal
    trade_count: int


@dataclass(frozen=True, slots=True)
class FeatureResult:
    calculation: FeatureCalculation
    values: tuple[FeatureValue, ...]


class FeatureService:
    """Compute deterministic features from an approved market snapshot."""

    def __init__(
        self,
        session: Session,
        snapshot_id: UUID,
        feature_set_version_id: UUID,
        *,
        workspace_id: UUID,
        clock: Clock | None = None,
    ) -> None:
        self._session = session
        self._snapshot_id = snapshot_id
        self._feature_set_version_id = feature_set_version_id
        self._workspace_id = workspace_id
        self._clock = clock or get_clock()
        self._schema_version = _FEATURE_SCHEMA_VERSION

    def compute_features(self) -> FeatureResult:
        """Compute all baseline features for the snapshot.

        Loads the snapshot and its ordered candle membership, validates
        quality/freshness, checks history sufficiency, computes deterministic
        indicators, hashes inputs and outputs, and persists the result.
        """
        assert_network_call_allowed()
        snapshot = self._load_snapshot()
        candles = self._load_snapshot_candles(snapshot)
        feature_set = self._load_feature_set_version()
        candle_count = len(candles)
        if candle_count < feature_set["required_history"]:
            return self._record_insufficient_history(
                snapshot, candles, feature_set,
                f"snapshot has {candle_count} candles, "
                f"required_history={feature_set['required_history']}",
            )
        input_hash = self._compute_input_hash(snapshot, candles, feature_set)
        idempotency_key = self._build_idempotency_key(
            snapshot, feature_set, input_hash
        )
        existing = self._find_existing_calculation(idempotency_key)
        if existing is not None:
            values = self._load_values(existing.id)
            return FeatureResult(calculation=existing, values=values)
        started_at = self._clock.now()
        warnings: list[str] = []
        values: list[FeatureValue] = []
        try:
            values.extend(self._compute_returns(candles, warnings))
            values.extend(self._compute_sma(candles, warnings))
            values.extend(self._compute_ema(candles, warnings))
            values.extend(self._compute_rsi(candles, warnings))
            values.extend(self._compute_atr(candles, warnings))
            values.extend(self._compute_volatility(candles, warnings))
            values.extend(self._compute_volume_relative(candles, warnings))
        except Exception as exc:
            logger.exception("feature_calculation_error")
            return self._record_error(
                snapshot, candles, feature_set, input_hash, idempotency_key,
                started_at, str(exc), warnings,
            )
        output_hash = self._compute_output_hash(values)
        completed_at = self._clock.now()
        calculation = self._insert_calculation(
            snapshot=snapshot,
            feature_set=feature_set,
            idempotency_key=idempotency_key,
            input_hash=input_hash,
            output_hash=output_hash,
            started_at=started_at,
            completed_at=completed_at,
            warnings=warnings,
        )
        self._insert_values(calculation.id, values)
        return FeatureResult(calculation=calculation, values=tuple(values))

    def _load_snapshot(self) -> dict[str, Any]:
        row = (
            self._session.execute(
                text(
                    """
                    select id, workspace_id, exchange_id, symbol_version_id,
                           interval_code, analysis_time, first_event_time,
                           last_event_time, candle_count, quality_outcome,
                           freshness_outcome, snapshot_hash, state,
                           invalidation_reason, data_source
                    from public.market_snapshots
                    where id = :snapshot_id
                    """
                ),
                {"snapshot_id": self._snapshot_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise ValueError(f"snapshot {self._snapshot_id} does not exist")
        snapshot = dict(row)
        if snapshot["state"] != "active":
            raise ValueError(
                f"snapshot {self._snapshot_id} state={snapshot['state']} "
                f"is not active"
            )
        if snapshot["quality_outcome"] != QualityState.APPROVED.value:
            raise ValueError(
                f"snapshot {self._snapshot_id} quality="
                f"{snapshot['quality_outcome']} is not approved"
            )
        if snapshot["freshness_outcome"] != "fresh":
            raise ValueError(
                f"snapshot {self._snapshot_id} freshness="
                f"{snapshot['freshness_outcome']} is not fresh"
            )
        if snapshot["workspace_id"] != self._workspace_id:
            raise ValueError("snapshot workspace does not match service")
        return snapshot

    def _load_snapshot_candles(
        self, snapshot: dict[str, Any]
    ) -> list[CandleData]:
        rows = (
            self._session.execute(
                text(
                    """
                    select candle.open_time, candle.close_time,
                           candle.open_price, candle.high_price,
                           candle.low_price, candle.close_price,
                           candle.base_volume, candle.quote_volume,
                           candle.trade_count
                    from public.market_snapshot_candles msc
                    join public.candles candle
                      on candle.id = msc.candle_id
                    where msc.snapshot_id = :snapshot_id
                    order by msc.sequence asc
                    """
                ),
                {"snapshot_id": self._snapshot_id},
            )
            .mappings()
            .all()
        )
        return [
            CandleData(
                open_time=row["open_time"],
                close_time=row["close_time"],
                open=Decimal(str(row["open_price"])),
                high=Decimal(str(row["high_price"])),
                low=Decimal(str(row["low_price"])),
                close=Decimal(str(row["close_price"])),
                volume=Decimal(str(row["base_volume"])),
                quote_volume=Decimal(str(row["quote_volume"])),
                trade_count=int(row["trade_count"]),
            )
            for row in rows
        ]

    def _load_feature_set_version(self) -> dict[str, Any]:
        row = (
            self._session.execute(
                text(
                    """
                    select id, workspace_id, name, semantic_version,
                           implementation_reference, configuration_hash,
                           required_history, warm_up_policy, status, created_at
                    from public.feature_set_versions
                    where id = :feature_set_version_id
                    """
                ),
                {"feature_set_version_id": self._feature_set_version_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise ValueError(
                f"feature_set_version {self._feature_set_version_id} does not exist"
            )
        feature_set = dict(row)
        if feature_set["workspace_id"] != self._workspace_id:
            raise ValueError("feature_set_version workspace does not match service")
        if feature_set["status"] != "active":
            raise ValueError(
                f"feature_set_version {self._feature_set_version_id} "
                f"status={feature_set['status']} is not active"
            )
        return feature_set

    def _build_idempotency_key(
        self,
        snapshot: dict[str, Any],
        feature_set: dict[str, Any],
        input_hash: str,
    ) -> str:
        payload = {
            "snapshot_id": str(snapshot["id"]),
            "snapshot_hash": snapshot["snapshot_hash"],
            "feature_set_version_id": str(feature_set["id"]),
            "feature_set_semantic_version": feature_set["semantic_version"],
            "input_hash": input_hash,
            "schema_version": self._schema_version,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _find_existing_calculation(
        self, idempotency_key: str
    ) -> FeatureCalculation | None:
        row = (
            self._session.execute(
                text(
                    """
                    select id, snapshot_id, feature_set_version_id, status,
                           input_hash, output_hash, calculation_started_at,
                           calculation_completed_at, warnings, error_message,
                           creator_cycle_id
                    from public.feature_calculations
                    where idempotency_key = :idempotency_key
                    limit 1
                    """
                ),
                {"idempotency_key": idempotency_key},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return FeatureCalculation(
            id=row["id"],
            snapshot_id=row["snapshot_id"],
            feature_set_version_id=row["feature_set_version_id"],
            idempotency_key=idempotency_key,
            status=row["status"],
            input_hash=row["input_hash"],
            output_hash=row["output_hash"],
            calculation_started_at=row["calculation_started_at"],
            calculation_completed_at=row["calculation_completed_at"],
            warnings=tuple(row["warnings"] or []),
            error_message=row["error_message"],
            creator_cycle_id=row["creator_cycle_id"],
        )

    def _load_values(self, calculation_id: UUID) -> tuple[FeatureValue, ...]:
        rows = (
            self._session.execute(
                text(
                    """
                    select feature_code, numeric_value, string_value,
                           boolean_value, unit, sequence, timestamp, null_reason
                    from public.feature_values
                    where calculation_id = :calculation_id
                    order by sequence asc
                    """
                ),
                {"calculation_id": calculation_id},
            )
            .mappings()
            .all()
        )
        return tuple(
            FeatureValue(
                calculation_id=calculation_id,
                feature_code=row["feature_code"],
                numeric_value=Decimal(str(row["numeric_value"])) if row["numeric_value"] is not None else None,
                string_value=row["string_value"],
                boolean_value=row["boolean_value"],
                unit=row["unit"] or "",
                sequence=int(row["sequence"]),
                timestamp=row["timestamp"],
                null_reason=row["null_reason"],
            )
            for row in rows
        )

    def _compute_input_hash(
        self,
        snapshot: dict[str, Any],
        candles: list[CandleData],
        feature_set: dict[str, Any],
    ) -> str:
        candle_hashes = []
        for c in candles:
            payload = {
                "open_time": c.open_time.isoformat(),
                "close_time": c.close_time.isoformat(),
                "open": str(c.open),
                "high": str(c.high),
                "low": str(c.low),
                "close": str(c.close),
                "volume": str(c.volume),
                "quote_volume": str(c.quote_volume),
                "trade_count": c.trade_count,
            }
            serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            candle_hashes.append(hashlib.sha256(serialized.encode("utf-8")).hexdigest())
        payload = {
            "snapshot_id": str(snapshot["id"]),
            "snapshot_hash": snapshot["snapshot_hash"],
            "feature_set_version_id": str(feature_set["id"]),
            "feature_set_semantic_version": feature_set["semantic_version"],
            "schema_version": self._schema_version,
            "candle_count": len(candles),
            "candle_hashes": candle_hashes,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _compute_output_hash(self, values: list[FeatureValue]) -> str:
        value_hashes = []
        for v in values:
            payload = {
                "feature_code": v.feature_code,
                "numeric_value": str(v.numeric_value) if v.numeric_value is not None else None,
                "string_value": v.string_value,
                "boolean_value": v.boolean_value,
                "unit": v.unit,
                "sequence": v.sequence,
                "timestamp": v.timestamp.isoformat() if v.timestamp else None,
                "null_reason": v.null_reason,
            }
            serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            value_hashes.append(hashlib.sha256(serialized.encode("utf-8")).hexdigest())
        payload = {
            "schema_version": self._schema_version,
            "value_count": len(values),
            "value_hashes": value_hashes,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _record_insufficient_history(
        self,
        snapshot: dict[str, Any],
        candles: list[CandleData],
        feature_set: dict[str, Any],
        reason: str,
    ) -> FeatureResult:
        input_hash = self._compute_input_hash(snapshot, candles, feature_set)
        idempotency_key = self._build_idempotency_key(
            snapshot, feature_set, input_hash
        )
        started_at = self._clock.now()
        completed_at = self._clock.now()
        calculation = self._insert_calculation(
            snapshot=snapshot,
            feature_set=feature_set,
            idempotency_key=idempotency_key,
            input_hash=input_hash,
            output_hash="",
            started_at=started_at,
            completed_at=completed_at,
            warnings=[reason],
            status=FeatureStatus.INSUFFICIENT_HISTORY.value,
            error_message=reason,
        )
        return FeatureResult(calculation=calculation, values=())

    def _record_error(
        self,
        snapshot: dict[str, Any],
        candles: list[CandleData],
        feature_set: dict[str, Any],
        input_hash: str,
        idempotency_key: str,
        started_at: datetime,
        error_message: str,
        warnings: list[str],
    ) -> FeatureResult:
        completed_at = self._clock.now()
        calculation = self._insert_calculation(
            snapshot=snapshot,
            feature_set=feature_set,
            idempotency_key=idempotency_key,
            input_hash=input_hash,
            output_hash="",
            started_at=started_at,
            completed_at=completed_at,
            warnings=warnings,
            status=FeatureStatus.CALCULATION_ERROR.value,
            error_message=error_message,
        )
        return FeatureResult(calculation=calculation, values=())

    def _insert_calculation(
        self,
        snapshot: dict[str, Any],
        feature_set: dict[str, Any],
        idempotency_key: str,
        input_hash: str,
        output_hash: str,
        started_at: datetime,
        completed_at: datetime,
        warnings: list[str],
        status: str = FeatureStatus.COMPLETED.value,
        error_message: str | None = None,
    ) -> FeatureCalculation:
        row = self._session.execute(
            text(
                """
                insert into public.feature_calculations (
                    workspace_id, snapshot_id, feature_set_version_id,
                    idempotency_key, status, input_hash, output_hash,
                    calculation_started_at, calculation_completed_at,
                    warnings, error_message, creator_cycle_id
                ) values (
                    :workspace_id, :snapshot_id, :feature_set_version_id,
                    :idempotency_key, :status, :input_hash, :output_hash,
                    :started_at, :completed_at,
                    :warnings, :error_message, :creator_cycle_id
                )
                on conflict (snapshot_id, feature_set_version_id, input_hash) do nothing
                returning id, snapshot_id, feature_set_version_id, status,
                           input_hash, output_hash, calculation_started_at,
                           calculation_completed_at, warnings, error_message,
                           creator_cycle_id
                """
            ),
            {
                "workspace_id": self._workspace_id,
                "snapshot_id": self._snapshot_id,
                "feature_set_version_id": self._feature_set_version_id,
                "idempotency_key": idempotency_key,
                "status": status,
                "input_hash": input_hash,
                "output_hash": output_hash,
                "started_at": started_at,
                "completed_at": completed_at,
                "warnings": warnings,
                "error_message": error_message,
                "creator_cycle_id": None,
            },
        ).mappings().one_or_none()
        if row is None:
            row = (
                self._session.execute(
                    text(
                        """
                        select id, snapshot_id, feature_set_version_id, status,
                               input_hash, output_hash, calculation_started_at,
                               calculation_completed_at, warnings, error_message,
                               creator_cycle_id
                        from public.feature_calculations
                        where snapshot_id = :snapshot_id
                          and feature_set_version_id = :feature_set_version_id
                          and input_hash = :input_hash
                        limit 1
                        """
                    ),
                    {
                        "snapshot_id": self._snapshot_id,
                        "feature_set_version_id": self._feature_set_version_id,
                        "input_hash": input_hash,
                    },
                )
                .mappings()
                .one()
            )
        return FeatureCalculation(
            id=row["id"],
            snapshot_id=row["snapshot_id"],
            feature_set_version_id=row["feature_set_version_id"],
            idempotency_key=idempotency_key,
            status=row["status"],
            input_hash=row["input_hash"],
            output_hash=row["output_hash"],
            calculation_started_at=row["calculation_started_at"],
            calculation_completed_at=row["calculation_completed_at"],
            warnings=tuple(row["warnings"] or []),
            error_message=row["error_message"],
            creator_cycle_id=row["creator_cycle_id"],
        )

    def _insert_values(
        self, calculation_id: UUID, values: list[FeatureValue]
    ) -> None:
        if not values:
            return
        value_rows = []
        params: dict[str, Any] = {"calculation_id": calculation_id}
        for idx, v in enumerate(values):
            prefix = f"v{idx}"
            value_rows.append(
                f"(:{prefix}_calculation_id, :{prefix}_feature_code, "
                f":{prefix}_numeric_value, :{prefix}_string_value, "
                f":{prefix}_boolean_value, :{prefix}_unit, "
                f":{prefix}_sequence, :{prefix}_timestamp, :{prefix}_null_reason)"
            )
            params.update({
                f"{prefix}_calculation_id": calculation_id,
                f"{prefix}_feature_code": v.feature_code,
                f"{prefix}_numeric_value": v.numeric_value,
                f"{prefix}_string_value": v.string_value,
                f"{prefix}_boolean_value": v.boolean_value,
                f"{prefix}_unit": v.unit,
                f"{prefix}_sequence": v.sequence,
                f"{prefix}_timestamp": v.timestamp,
                f"{prefix}_null_reason": v.null_reason,
            })
        sql = (
            "insert into public.feature_values "
            "(calculation_id, feature_code, numeric_value, string_value, "
            "boolean_value, unit, sequence, timestamp, null_reason) "
            f"values {','.join(value_rows)} "
            "on conflict (calculation_id, feature_code, sequence) do nothing"
        )
        self._session.execute(text(sql), params)

    def _make_value(
        self,
        feature_code: FeatureCode,
        sequence: int,
        timestamp: datetime | None,
        numeric_value: Decimal | None = None,
        string_value: str | None = None,
        boolean_value: bool | None = None,
        unit: str = "",
        null_reason: str | None = None,
    ) -> FeatureValue:
        return FeatureValue(
            calculation_id=UUID(int=0),
            feature_code=feature_code.value,
            numeric_value=numeric_value,
            string_value=string_value,
            boolean_value=boolean_value,
            unit=unit,
            sequence=sequence,
            timestamp=timestamp,
            null_reason=null_reason,
        )

    def _compute_returns(
        self, candles: list[CandleData], warnings: list[str]
    ) -> list[FeatureValue]:
        values: list[FeatureValue] = []
        for i in range(1, len(candles)):
            prev_close = candles[i - 1].close
            curr_close = candles[i].close
            if prev_close == Decimal("0"):
                values.append(self._make_value(
                    FeatureCode.RETURNS_SIMPLE, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="ratio",
                ))
                values.append(self._make_value(
                    FeatureCode.RETURNS_LOG, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="ratio",
                ))
                continue
            simple = (curr_close - prev_close) / prev_close
            if curr_close <= 0 or prev_close <= 0:
                log_val: Decimal | None = None
                null_reason = _WARM_UP_NULL_REASON
            else:
                try:
                    log_val = Decimal(str(math.log(float(curr_close / prev_close))))
                    null_reason = None
                except (InvalidOperation, ValueError):
                    log_val = None
                    null_reason = _WARM_UP_NULL_REASON
            values.append(self._make_value(
                FeatureCode.RETURNS_SIMPLE, i, candles[i].open_time,
                numeric_value=simple, unit="ratio",
            ))
            values.append(self._make_value(
                FeatureCode.RETURNS_LOG, i, candles[i].open_time,
                numeric_value=log_val, unit="ratio", null_reason=null_reason,
            ))
        return values

    def _compute_sma(
        self, candles: list[CandleData], warnings: list[str]
    ) -> list[FeatureValue]:
        values: list[FeatureValue] = []
        period = 20
        if len(candles) < period:
            for i in range(len(candles)):
                values.append(self._make_value(
                    FeatureCode.SMA_20, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="price",
                ))
            return values
        running_sum = sum(
            (candles[i].close for i in range(period)),
            start=Decimal("0"),
        )
        for i in range(len(candles)):
            if i < period - 1:
                values.append(self._make_value(
                    FeatureCode.SMA_20, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="price",
                ))
                continue
            if i >= period:
                running_sum -= candles[i - period].close
                running_sum += candles[i].close
            sma = running_sum / Decimal(period)
            values.append(self._make_value(
                FeatureCode.SMA_20, i, candles[i].open_time,
                numeric_value=sma, unit="price",
            ))
        return values

    def _compute_ema(
        self, candles: list[CandleData], warnings: list[str]
    ) -> list[FeatureValue]:
        values: list[FeatureValue] = []
        period = 20
        if len(candles) < period:
            for i in range(len(candles)):
                values.append(self._make_value(
                    FeatureCode.EMA_20, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="price",
                ))
            return values
        alpha = Decimal("2") / Decimal(period + 1)
        ema_50_values: list[FeatureValue] = []
        ema_50_period = 50
        if len(candles) >= ema_50_period:
            alpha_50 = Decimal("2") / Decimal(ema_50_period + 1)
            sma_50_start = sum(
                (candles[i].close for i in range(ema_50_period)),
                start=Decimal("0"),
            ) / Decimal(ema_50_period)
            ema_50 = sma_50_start
            for i in range(len(candles)):
                if i < ema_50_period - 1:
                    ema_50_values.append(self._make_value(
                        FeatureCode.EMA_50, i, candles[i].open_time,
                        null_reason=_WARM_UP_NULL_REASON, unit="price",
                    ))
                    continue
                if i == ema_50_period - 1:
                    ema_50 = sma_50_start
                else:
                    ema_50 = alpha_50 * candles[i].close + (Decimal("1") - alpha_50) * ema_50
                ema_50_values.append(self._make_value(
                    FeatureCode.EMA_50, i, candles[i].open_time,
                    numeric_value=ema_50, unit="price",
                ))
        else:
            for i in range(len(candles)):
                ema_50_values.append(self._make_value(
                    FeatureCode.EMA_50, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="price",
                ))
        sma_start = sum(
            (candles[i].close for i in range(period)),
            start=Decimal("0"),
        ) / Decimal(period)
        ema = sma_start
        for i in range(len(candles)):
            if i < period - 1:
                values.append(self._make_value(
                    FeatureCode.EMA_20, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="price",
                ))
                continue
            if i == period - 1:
                ema = sma_start
            else:
                ema = alpha * candles[i].close + (Decimal("1") - alpha) * ema
            values.append(self._make_value(
                FeatureCode.EMA_20, i, candles[i].open_time,
                numeric_value=ema, unit="price",
            ))
        values.extend(ema_50_values)
        return values

    def _compute_rsi(
        self, candles: list[CandleData], warnings: list[str]
    ) -> list[FeatureValue]:
        values: list[FeatureValue] = []
        period = 14
        if len(candles) < period + 1:
            for i in range(len(candles)):
                values.append(self._make_value(
                    FeatureCode.RSI_14, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="index",
                ))
            return values
        gains: list[Decimal] = []
        losses: list[Decimal] = []
        for i in range(1, period + 1):
            change = candles[i].close - candles[i - 1].close
            gains.append(change if change > Decimal("0") else Decimal("0"))
            losses.append(-change if change < Decimal("0") else Decimal("0"))
        avg_gain = sum(gains, start=Decimal("0")) / Decimal(period)
        avg_loss = sum(losses, start=Decimal("0")) / Decimal(period)
        for i in range(len(candles)):
            if i < period:
                values.append(self._make_value(
                    FeatureCode.RSI_14, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="index",
                ))
                continue
            if i > period:
                change = candles[i].close - candles[i - 1].close
                gain = change if change > Decimal("0") else Decimal("0")
                loss = -change if change < Decimal("0") else Decimal("0")
                avg_gain = (avg_gain * Decimal(period - 1) + gain) / Decimal(period)
                avg_loss = (avg_loss * Decimal(period - 1) + loss) / Decimal(period)
            if avg_loss == Decimal("0"):
                rsi = Decimal("100")
            else:
                rs = avg_gain / avg_loss
                rsi = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
            values.append(self._make_value(
                FeatureCode.RSI_14, i, candles[i].open_time,
                numeric_value=rsi, unit="index",
            ))
        return values

    def _compute_atr(
        self, candles: list[CandleData], warnings: list[str]
    ) -> list[FeatureValue]:
        values: list[FeatureValue] = []
        period = 14
        if len(candles) < period + 1:
            for i in range(len(candles)):
                values.append(self._make_value(
                    FeatureCode.ATR_14, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="price",
                ))
            return values
        trs: list[Decimal] = []
        for i in range(1, len(candles)):
            tr = max(
                candles[i].high - candles[i].low,
                abs(candles[i].high - candles[i - 1].close),
                abs(candles[i].low - candles[i - 1].close),
            )
            trs.append(tr)
        if len(trs) < period:
            for i in range(len(candles)):
                values.append(self._make_value(
                    FeatureCode.ATR_14, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="price",
                ))
            return values
        atr = sum(trs[:period], start=Decimal("0")) / Decimal(period)
        for i in range(len(candles)):
            if i < period:
                values.append(self._make_value(
                    FeatureCode.ATR_14, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="price",
                ))
                continue
            if i > period:
                atr = ((atr * Decimal(period - 1)) + trs[i - 1]) / Decimal(period)
            values.append(self._make_value(
                FeatureCode.ATR_14, i, candles[i].open_time,
                numeric_value=atr, unit="price",
            ))
        return values

    def _compute_volatility(
        self, candles: list[CandleData], warnings: list[str]
    ) -> list[FeatureValue]:
        values: list[FeatureValue] = []
        period = 20
        if len(candles) < period + 1:
            for i in range(len(candles)):
                values.append(self._make_value(
                    FeatureCode.VOLATILITY_ROLLING_20, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="annualized_ratio",
                ))
            return values
        returns: list[Decimal] = []
        for i in range(1, len(candles)):
            prev = candles[i - 1].close
            curr = candles[i].close
            if prev == Decimal("0") or curr == Decimal("0"):
                returns.append(Decimal("0"))
            else:
                returns.append(curr / prev - Decimal("1"))
        for i in range(len(candles)):
            if i < period:
                values.append(self._make_value(
                    FeatureCode.VOLATILITY_ROLLING_20, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="annualized_ratio",
                ))
                continue
            window = returns[i - period : i]
            mean = sum(window, start=Decimal("0")) / Decimal(period)
            variance = sum((r - mean) ** 2 for r in window) / Decimal(period)
            std = variance.sqrt()
            annualized = std * Decimal(str(math.sqrt(252.0 * 24)))
            values.append(self._make_value(
                FeatureCode.VOLATILITY_ROLLING_20, i, candles[i].open_time,
                numeric_value=annualized, unit="annualized_ratio",
            ))
        return values

    def _compute_volume_relative(
        self, candles: list[CandleData], warnings: list[str]
    ) -> list[FeatureValue]:
        values: list[FeatureValue] = []
        period = 20
        if len(candles) < period:
            for i in range(len(candles)):
                values.append(self._make_value(
                    FeatureCode.VOLUME_RELATIVE_20, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="ratio",
                ))
            return values
        running_sum = sum(
            (candles[i].volume for i in range(period)),
            start=Decimal("0"),
        )
        for i in range(len(candles)):
            if i < period - 1:
                values.append(self._make_value(
                    FeatureCode.VOLUME_RELATIVE_20, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="ratio",
                ))
                continue
            if i >= period:
                running_sum -= candles[i - period].volume
                running_sum += candles[i].volume
            sma_volume = running_sum / Decimal(period)
            if sma_volume == Decimal("0"):
                values.append(self._make_value(
                    FeatureCode.VOLUME_RELATIVE_20, i, candles[i].open_time,
                    null_reason=_WARM_UP_NULL_REASON, unit="ratio",
                ))
                continue
            relative = candles[i].volume / sma_volume
            values.append(self._make_value(
                FeatureCode.VOLUME_RELATIVE_20, i, candles[i].open_time,
                numeric_value=relative, unit="ratio",
            ))
        return values
