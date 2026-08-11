"""Unit tests for M008 deterministic feature engineering."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest

from app.core.clock import FixedClock
from app.domains.features.models import (
    FeatureCode,
    FeatureStatus,
)
from app.domains.features.service import CandleData, FeatureResult, FeatureService
from app.domains.market_data.models import QualityState

FIXED_TIME = datetime(2026, 8, 8, 12, 0, 0, tzinfo=timezone.utc)
WORKSPACE_ID = UUID("20000000-0000-0000-0000-000000000001")
SNAPSHOT_ID = UUID("30000000-0000-0000-0000-000000000001")
FEATURE_SET_ID = UUID("50000000-0000-0000-0000-000000000001")


def _make_candle(
    open_time: datetime,
    close: Decimal,
    volume: Decimal = Decimal("1"),
    close_time: datetime | None = None,
) -> CandleData:
    return CandleData(
        open_time=open_time,
        close_time=close_time if close_time is not None else open_time,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=volume,
        quote_volume=close * volume,
        trade_count=1,
    )


def _make_candles(
    count: int, base: Decimal = Decimal("100"), volume: Decimal = Decimal("1")
) -> list[CandleData]:
    return [
        _make_candle(
            FIXED_TIME - timedelta(hours=count - i),
            base + Decimal(i),
            volume,
        )
        for i in range(count)
    ]


def _make_candles_alternating_volume(
    count: int, base: Decimal = Decimal("100")
) -> list[CandleData]:
    return [
        _make_candle(
            FIXED_TIME - timedelta(hours=count - i),
            base + Decimal(i),
            Decimal("5") if i % 2 == 0 else Decimal("15"),
        )
        for i in range(count)
    ]


class MockResult:
    def __init__(self) -> None:
        self._one_or_none_value: dict[str, Any] | None = None
        self._one_value: dict[str, Any] = {}
        self._scalars_value: list[Any] = []
        self._scalar_one_value: Any = None
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
        self.snapshots: dict[UUID, dict[str, Any]] = {}
        self.feature_sets: dict[UUID, dict[str, Any]] = {}
        self.calculations: dict[UUID, dict[str, Any]] = {}
        self.values: dict[UUID, list[dict[str, Any]]] = {}
        self.invalidations: list[dict[str, Any]] = []
        self.next_calc_id = uuid4()
        self.simulate_conflict = False

    def commit(self) -> None:
        return

    def rollback(self) -> None:
        return

    def execute(
        self, statement: Any, params: dict[str, Any] | None = None
    ) -> MockResult:
        if params is None:
            params = {}
        sql = " ".join(str(statement).lower().split())
        result = MockResult()
        if "from public.market_snapshots" in sql:
            result._one_or_none_value = self.snapshots.get(params.get("snapshot_id"))
            return result
        if (
            "from public.market_snapshot_candles" in sql
            and "join public.candles" in sql
        ):
            snapshot = self.snapshots.get(params.get("snapshot_id"), {})
            result._scalars_value = snapshot.get("candles", [])
            return result
        if "from public.feature_set_versions" in sql:
            result._one_or_none_value = self.feature_sets.get(
                params.get("feature_set_version_id")
            )
            return result
        if "insert into public.feature_calculations" in sql:
            for calc in self.calculations.values():
                if (
                    calc["snapshot_id"] == params["snapshot_id"]
                    and calc["feature_set_version_id"]
                    == params["feature_set_version_id"]
                    and calc["input_hash"] == params["input_hash"]
                ):
                    result._one_or_none_value = calc
                    return result
            if self.simulate_conflict:
                self.simulate_conflict = False
                result._one_or_none_value = None
                return result
            calc_id = self.next_calc_id
            self.next_calc_id = uuid4()
            row = {
                "id": calc_id,
                "snapshot_id": params["snapshot_id"],
                "feature_set_version_id": params["feature_set_version_id"],
                "idempotency_key": params["idempotency_key"],
                "status": params["status"],
                "input_hash": params["input_hash"],
                "output_hash": params["output_hash"],
                "calculation_started_at": params["started_at"],
                "calculation_completed_at": params["completed_at"],
                "warnings": params["warnings"],
                "error_message": params["error_message"],
                "creator_cycle_id": params["creator_cycle_id"],
            }
            self.calculations[calc_id] = row
            result._one_or_none_value = row
            return result
        if "from public.feature_calculations" in sql and "idempotency_key" in sql:
            for calc in self.calculations.values():
                if calc.get("idempotency_key") == params.get("idempotency_key"):
                    result._one_or_none_value = calc
                    return result
            result._one_or_none_value = None
            return result
        if "from public.feature_values" in sql:
            calc_id = params.get("calculation_id")
            result._scalars_value = self.values.get(calc_id, [])
            return result
        if "insert into public.feature_values" in sql:
            calc_id = params.get("calculation_id")
            if calc_id not in self.values:
                self.values[calc_id] = []
            for idx in range(
                len(
                    [
                        k
                        for k in params
                        if k.startswith("v") and k.endswith("_feature_code")
                    ]
                )
            ):
                prefix = f"v{idx}"
                self.values[calc_id].append(
                    {
                        "feature_code": params.get(f"{prefix}_feature_code"),
                        "numeric_value": params.get(f"{prefix}_numeric_value"),
                        "string_value": params.get(f"{prefix}_string_value"),
                        "boolean_value": params.get(f"{prefix}_boolean_value"),
                        "unit": params.get(f"{prefix}_unit"),
                        "sequence": params.get(f"{prefix}_sequence"),
                        "timestamp": params.get(f"{prefix}_timestamp"),
                        "null_reason": params.get(f"{prefix}_null_reason"),
                    }
                )
            return result
        if "insert into public.feature_calculation_invalidations" in sql:
            self.invalidations.append(
                {
                    "calculation_id": params.get("calculation_id"),
                    "reason": params.get("reason"),
                    "replacement_calculation_id": params.get(
                        "replacement_calculation_id"
                    ),
                }
            )
            return result
        if (
            "from public.feature_calculations" in sql
            and "snapshot_id" in sql
            and "status = 'completed'" in sql
        ):
            rows = []
            for calc in self.calculations.values():
                if (
                    calc["snapshot_id"] == params.get("snapshot_id")
                    and calc["status"] == "completed"
                ):
                    rows.append(calc["id"])
            result._scalars_value = rows
            return result
        if "from public.feature_calculations" in sql and "input_hash" in sql:
            for calc in self.calculations.values():
                if (
                    calc["snapshot_id"] == params.get("snapshot_id")
                    and calc["feature_set_version_id"]
                    == params.get("feature_set_version_id")
                    and calc["input_hash"] == params.get("input_hash")
                ):
                    result._one_or_none_value = calc
                    return result
            result._one_or_none_value = None
            return result
        return result


def _setup_session(candles: list[CandleData]) -> MockSession:
    session = MockSession()
    analysis_time = candles[-1].close_time if candles else FIXED_TIME
    session.snapshots[SNAPSHOT_ID] = {
        "id": SNAPSHOT_ID,
        "workspace_id": WORKSPACE_ID,
        "exchange_id": UUID("40000000-0000-0000-0000-000000000001"),
        "symbol_version_id": UUID("41000000-0000-0000-0000-000000000001"),
        "interval_code": "1h",
        "analysis_time": analysis_time,
        "first_event_time": candles[0].open_time if candles else None,
        "last_event_time": candles[-1].open_time if candles else None,
        "candle_count": len(candles),
        "quality_outcome": QualityState.APPROVED.value,
        "freshness_outcome": "fresh",
        "snapshot_hash": "a" * 64,
        "state": "active",
        "invalidation_reason": None,
        "data_source": "rest",
        "candles": [
            {
                "open_time": c.open_time,
                "close_time": c.close_time,
                "open_price": c.open,
                "high_price": c.high,
                "low_price": c.low,
                "close_price": c.close,
                "base_volume": c.volume,
                "quote_volume": c.quote_volume,
                "trade_count": c.trade_count,
            }
            for c in candles
        ],
    }
    session.feature_sets[FEATURE_SET_ID] = {
        "id": FEATURE_SET_ID,
        "workspace_id": WORKSPACE_ID,
        "name": "baseline-v1",
        "semantic_version": "1.0.0",
        "implementation_reference": "m008-baseline",
        "configuration_hash": "b" * 64,
        "required_history": 1,
        "warm_up_policy": "insufficient_history_null",
        "status": "active",
        "created_at": FIXED_TIME,
    }
    return session


def _compute_service(session: MockSession) -> FeatureResult:
    service = FeatureService(
        session=session,
        snapshot_id=SNAPSHOT_ID,
        feature_set_version_id=FEATURE_SET_ID,
        workspace_id=WORKSPACE_ID,
        clock=FixedClock(FIXED_TIME),
    )
    return service.compute_features()


def test_reference_simple_returns() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    assert result.calculation.status == FeatureStatus.COMPLETED.value
    returns = [
        v for v in result.values if v.feature_code == FeatureCode.RETURNS_SIMPLE.value
    ]
    assert len(returns) == 4
    assert returns[0].numeric_value == Decimal("0.01")
    assert returns[1].numeric_value == Decimal("0.009900990099009901")
    assert returns[2].numeric_value == Decimal("0.009803921568627451")
    assert returns[3].numeric_value == Decimal("0.009708737864077670")


def test_reference_log_returns() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    returns = [
        v for v in result.values if v.feature_code == FeatureCode.RETURNS_LOG.value
    ]
    assert len(returns) == 4
    assert returns[0].numeric_value == Decimal("0.009950330853168083")
    assert returns[1].numeric_value == Decimal("0.009852296443011630")
    assert returns[2].numeric_value == Decimal("0.009756174945364690")
    assert returns[3].numeric_value == Decimal("0.009661910911736894")


def test_reference_sma() -> None:
    candles = _make_candles(25, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    sma_values = [
        v for v in result.values if v.feature_code == FeatureCode.SMA_20.value
    ]
    assert len(sma_values) == 25
    for i in range(19):
        assert sma_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    assert sma_values[19].numeric_value == Decimal("109.5")
    assert sma_values[24].numeric_value == Decimal("114.5")


def test_reference_ema() -> None:
    candles = _make_candles(25, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    ema_values = [
        v for v in result.values if v.feature_code == FeatureCode.EMA_20.value
    ]
    assert len(ema_values) == 25
    for i in range(19):
        assert ema_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    assert ema_values[19].numeric_value == Decimal("109.5")
    assert ema_values[24].numeric_value == Decimal("114.5")


def test_reference_rsi() -> None:
    candles = _make_candles(20, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    rsi_values = [
        v for v in result.values if v.feature_code == FeatureCode.RSI_14.value
    ]
    assert len(rsi_values) == 20
    for i in range(14):
        assert rsi_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    assert rsi_values[14].numeric_value == Decimal("100")
    assert rsi_values[19].numeric_value == Decimal("100")


def test_reference_atr() -> None:
    candles = _make_candles(20, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    atr_values = [
        v for v in result.values if v.feature_code == FeatureCode.ATR_14.value
    ]
    assert len(atr_values) == 20
    for i in range(14):
        assert atr_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    assert atr_values[14].numeric_value == Decimal("1")
    assert atr_values[19].numeric_value == Decimal("1")


def test_reference_volatility() -> None:
    candles = _make_candles(25, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    vol_values = [
        v
        for v in result.values
        if v.feature_code == FeatureCode.VOLATILITY_ROLLING_20.value
    ]
    assert len(vol_values) == 25
    for i in range(20):
        assert vol_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    assert vol_values[20].numeric_value == Decimal("0.037628946682999756")
    assert vol_values[24].numeric_value == Decimal("0.035008583618491817")


def test_reference_volume_relative() -> None:
    candles = _make_candles(25, base=Decimal("100"), volume=Decimal("10"))
    session = _setup_session(candles)
    result = _compute_service(session)
    vol_values = [
        v
        for v in result.values
        if v.feature_code == FeatureCode.VOLUME_RELATIVE_20.value
    ]
    assert len(vol_values) == 25
    for i in range(19):
        assert vol_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    assert vol_values[19].numeric_value == Decimal("1")
    assert vol_values[24].numeric_value == Decimal("1")


def test_insufficient_history_rejection() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.feature_sets[FEATURE_SET_ID]["required_history"] = 100
    result = _compute_service(session)
    assert result.calculation.status == FeatureStatus.INSUFFICIENT_HISTORY.value
    assert not result.values


def test_stale_snapshot_rejection() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.snapshots[SNAPSHOT_ID]["quality_outcome"] = QualityState.INVALID_VALUE.value
    with pytest.raises(ValueError, match="quality="):
        _compute_service(session)


def test_invalid_state_snapshot_rejection() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.snapshots[SNAPSHOT_ID]["state"] = "invalidated"
    with pytest.raises(ValueError, match="state="):
        _compute_service(session)


def test_non_fresh_snapshot_rejection() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.snapshots[SNAPSHOT_ID]["freshness_outcome"] = "stale"
    with pytest.raises(ValueError, match="freshness="):
        _compute_service(session)


def test_deterministic_hash_identical_inputs() -> None:
    candles = _make_candles(30, base=Decimal("100"), volume=Decimal("5"))
    session_a = _setup_session(candles)
    session_b = _setup_session(candles)
    result_a = _compute_service(session_a)
    result_b = _compute_service(session_b)
    assert result_a.calculation.input_hash == result_b.calculation.input_hash
    assert result_a.calculation.output_hash == result_b.calculation.output_hash


def test_different_inputs_produce_different_hashes() -> None:
    candles_a = _make_candles(30, base=Decimal("100"), volume=Decimal("5"))
    candles_b = _make_candles(30, base=Decimal("101"), volume=Decimal("5"))
    session_a = _setup_session(candles_a)
    session_b = _setup_session(candles_b)
    result_a = _compute_service(session_a)
    result_b = _compute_service(session_b)
    assert result_a.calculation.input_hash != result_b.calculation.input_hash


def test_idempotency_returns_existing() -> None:
    candles = _make_candles(30, base=Decimal("100"), volume=Decimal("5"))
    session = _setup_session(candles)
    result_a = _compute_service(session)
    result_b = _compute_service(session)
    assert result_a.calculation.id == result_b.calculation.id
    assert result_a.calculation.output_hash == result_b.calculation.output_hash


def test_no_look_ahead_assertion() -> None:
    candles = _make_candles(30, base=Decimal("100"), volume=Decimal("5"))
    session = _setup_session(candles)
    result = _compute_service(session)
    sma_values = [
        v for v in result.values if v.feature_code == FeatureCode.SMA_20.value
    ]
    for i, value in enumerate(sma_values):
        if value.numeric_value is not None:
            expected = sum(candles[j].close for j in range(i - 19, i + 1)) / Decimal(20)
            assert value.numeric_value == expected


def test_warm_up_null_reason_explicit() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    sma_values = [
        v for v in result.values if v.feature_code == FeatureCode.SMA_20.value
    ]
    assert sma_values[0].null_reason == _get_warm_up_null_reason()
    assert sma_values[0].numeric_value is None


def test_output_hash_changes_with_values() -> None:
    candles_a = _make_candles_alternating_volume(30, base=Decimal("100"))
    candles_b = _make_candles_alternating_volume(30, base=Decimal("101"))
    session_a = _setup_session(candles_a)
    session_b = _setup_session(candles_b)
    result_a = _compute_service(session_a)
    result_b = _compute_service(session_b)
    assert result_a.calculation.input_hash != result_b.calculation.input_hash
    assert result_a.calculation.output_hash != result_b.calculation.output_hash


def test_feature_values_are_decimal() -> None:
    candles = _make_candles(30, base=Decimal("100"), volume=Decimal("5"))
    session = _setup_session(candles)
    result = _compute_service(session)
    for value in result.values:
        if value.numeric_value is not None:
            assert isinstance(value.numeric_value, Decimal)


def test_correction_invalidation_lineage_blocked() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.snapshots[SNAPSHOT_ID]["state"] = "invalidated"
    session.snapshots[SNAPSHOT_ID]["invalidation_reason"] = "candle_correction"
    with pytest.raises(ValueError, match="state="):
        _compute_service(session)


def test_feature_set_workspace_mismatch_rejected() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.feature_sets[FEATURE_SET_ID]["workspace_id"] = UUID(
        "99999999-0000-0000-0000-000000000000"
    )
    with pytest.raises(ValueError, match="workspace"):
        _compute_service(session)


def test_division_by_zero_in_returns() -> None:
    candles = [
        _make_candle(FIXED_TIME - timedelta(hours=2), Decimal("100"), Decimal("1")),
        _make_candle(FIXED_TIME - timedelta(hours=1), Decimal("0"), Decimal("1")),
        _make_candle(FIXED_TIME, Decimal("100"), Decimal("1")),
    ]
    session = _setup_session(candles)
    result = _compute_service(session)
    returns = [
        v for v in result.values if v.feature_code == FeatureCode.RETURNS_SIMPLE.value
    ]
    assert len(returns) == 2
    assert returns[0].numeric_value == Decimal("-1")
    assert returns[1].null_reason == _get_warm_up_null_reason()


def test_snapshot_not_found() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.snapshots.clear()
    with pytest.raises(ValueError, match="snapshot .* does not exist"):
        _compute_service(session)


def test_feature_set_version_not_found() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.feature_sets.clear()
    with pytest.raises(ValueError, match="feature_set_version .* does not exist"):
        _compute_service(session)


def test_feature_set_version_inactive() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.feature_sets[FEATURE_SET_ID]["status"] = "inactive"
    with pytest.raises(ValueError, match="status=inactive"):
        _compute_service(session)


def test_record_error_path() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    service = FeatureService(
        session=session,
        snapshot_id=SNAPSHOT_ID,
        feature_set_version_id=FEATURE_SET_ID,
        workspace_id=WORKSPACE_ID,
        clock=FixedClock(FIXED_TIME),
    )
    original_compute = service._compute_returns
    service._compute_returns = lambda candles, warnings: (_ for _ in ()).throw(
        RuntimeError("boom")
    )
    result = service.compute_features()
    assert result.calculation.status == FeatureStatus.CALCULATION_ERROR.value
    assert result.calculation.error_message == "boom"
    assert not result.values
    service._compute_returns = original_compute


def test_insert_conflict_returns_existing() -> None:
    candles = _make_candles(30, base=Decimal("100"), volume=Decimal("5"))
    session = _setup_session(candles)
    result_a = _compute_service(session)
    session.simulate_conflict = True
    result_b = _compute_service(session)
    assert result_a.calculation.id == result_b.calculation.id
    assert result_a.calculation.output_hash == result_b.calculation.output_hash


def test_load_values_with_data() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    calc_id = result.calculation.id
    stored = session.values.get(calc_id, [])
    assert len(stored) > 0
    for row in stored:
        assert "feature_code" in row
        assert "numeric_value" in row


def test_log_returns_invalid_operation() -> None:
    candles = [
        _make_candle(FIXED_TIME - timedelta(hours=2), Decimal("100"), Decimal("1")),
        _make_candle(FIXED_TIME - timedelta(hours=1), Decimal("-1"), Decimal("1")),
        _make_candle(FIXED_TIME, Decimal("100"), Decimal("1")),
    ]
    session = _setup_session(candles)
    result = _compute_service(session)
    log_returns = [
        v for v in result.values if v.feature_code == FeatureCode.RETURNS_LOG.value
    ]
    assert len(log_returns) == 2
    assert log_returns[0].null_reason == _get_warm_up_null_reason()
    assert log_returns[1].null_reason == _get_warm_up_null_reason()


def test_ema_50_computed_when_sufficient_history() -> None:
    candles = _make_candles(55, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    ema_50_values = [
        v for v in result.values if v.feature_code == FeatureCode.EMA_50.value
    ]
    assert len(ema_50_values) == 55
    for i in range(49):
        assert ema_50_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    assert ema_50_values[49].numeric_value is not None
    assert ema_50_values[54].numeric_value is not None


def test_rsi_avg_loss_nonzero() -> None:
    candles = [
        _make_candle(
            FIXED_TIME - timedelta(hours=20 + 1 - i),
            Decimal("100") if i % 2 == 0 else Decimal("99"),
            Decimal("1"),
        )
        for i in range(20 + 1)
    ]
    session = _setup_session(candles)
    result = _compute_service(session)
    rsi_values = [
        v for v in result.values if v.feature_code == FeatureCode.RSI_14.value
    ]
    assert len(rsi_values) == 21
    for i in range(14):
        assert rsi_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    assert rsi_values[14].numeric_value is not None
    assert rsi_values[14].numeric_value != Decimal("100")


def test_volatility_zero_price() -> None:
    candles = [
        _make_candle(
            FIXED_TIME - timedelta(hours=25 - i),
            Decimal("100") if i != 10 else Decimal("0"),
            Decimal("1"),
        )
        for i in range(25)
    ]
    session = _setup_session(candles)
    result = _compute_service(session)
    vol_values = [
        v
        for v in result.values
        if v.feature_code == FeatureCode.VOLATILITY_ROLLING_20.value
    ]
    assert len(vol_values) == 25
    for i in range(20):
        assert vol_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    assert vol_values[20].numeric_value is not None


def test_volume_relative_zero_sma() -> None:
    candles = [
        _make_candle(FIXED_TIME - timedelta(hours=25 - i), Decimal("100"), Decimal("0"))
        for i in range(25)
    ]
    session = _setup_session(candles)
    result = _compute_service(session)
    vol_values = [
        v
        for v in result.values
        if v.feature_code == FeatureCode.VOLUME_RELATIVE_20.value
    ]
    assert len(vol_values) == 25
    for i in range(19):
        assert vol_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
    for i in range(19, 25):
        assert vol_values[i].null_reason == _get_warm_up_null_reason(), f"index {i}"
        assert vol_values[i].numeric_value is None


def test_membership_count_mismatch() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.snapshots[SNAPSHOT_ID]["candle_count"] = 99
    with pytest.raises(ValueError, match="membership count mismatch"):
        _compute_service(session)


def test_membership_future_candle() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.snapshots[SNAPSHOT_ID]["analysis_time"] = candles[-1].open_time - timedelta(
        seconds=1
    )
    with pytest.raises(ValueError, match="future candle"):
        _compute_service(session)


def test_empty_output_hash_is_canonical() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    session.feature_sets[FEATURE_SET_ID]["required_history"] = 100
    result = _compute_service(session)
    assert result.calculation.status == FeatureStatus.INSUFFICIENT_HISTORY.value
    assert len(result.calculation.output_hash) == 64
    assert result.calculation.output_hash == hashlib.sha256(b"").hexdigest()


def test_error_output_hash_is_canonical() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    service = FeatureService(
        session=session,
        snapshot_id=SNAPSHOT_ID,
        feature_set_version_id=FEATURE_SET_ID,
        workspace_id=WORKSPACE_ID,
        clock=FixedClock(FIXED_TIME),
    )
    original_compute = service._compute_returns
    service._compute_returns = lambda candles, warnings: (_ for _ in ()).throw(
        RuntimeError("boom")
    )
    result = service.compute_features()
    assert result.calculation.status == FeatureStatus.CALCULATION_ERROR.value
    assert len(result.calculation.output_hash) == 64
    assert result.calculation.output_hash == hashlib.sha256(b"").hexdigest()
    service._compute_returns = original_compute


def test_output_hash_round_trip_from_stored_precision() -> None:
    candles = _make_candles(30, base=Decimal("100"), volume=Decimal("5"))
    session = _setup_session(candles)
    result = _compute_service(session)
    stored_values = session.values.get(result.calculation.id, [])
    assert len(stored_values) > 0
    recomputed_hashes = []
    for stored in stored_values:
        payload = {
            "feature_code": stored["feature_code"],
            "numeric_value": str(stored["numeric_value"])
            if stored["numeric_value"] is not None
            else None,
            "string_value": stored["string_value"],
            "boolean_value": stored["boolean_value"],
            "unit": stored["unit"],
            "sequence": stored["sequence"],
            "timestamp": stored["timestamp"].isoformat()
            if stored["timestamp"]
            else None,
            "null_reason": stored["null_reason"],
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        recomputed_hashes.append(hashlib.sha256(serialized.encode("utf-8")).hexdigest())
    output_payload = {
        "schema_version": "1.0",
        "value_count": len(stored_values),
        "value_hashes": recomputed_hashes,
    }
    serialized = json.dumps(output_payload, sort_keys=True, separators=(",", ":"))
    recomputed_output_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    assert result.calculation.output_hash == recomputed_output_hash


def test_input_hash_includes_full_feature_set_config() -> None:
    candles = _make_candles(30, base=Decimal("100"), volume=Decimal("5"))
    session_a = _setup_session(candles)
    session_b = _setup_session(candles)
    session_b.feature_sets[FEATURE_SET_ID]["configuration_hash"] = "c" * 64
    result_a = _compute_service(session_a)
    result_b = _compute_service(session_b)
    assert result_a.calculation.input_hash != result_b.calculation.input_hash


def test_correction_invalidation_lineage_full_sequence() -> None:
    candles = _make_candles(30, base=Decimal("100"), volume=Decimal("5"))
    session = _setup_session(candles)
    result = _compute_service(session)
    assert result.calculation.status == FeatureStatus.COMPLETED.value
    service = FeatureService(
        session=session,
        snapshot_id=SNAPSHOT_ID,
        feature_set_version_id=FEATURE_SET_ID,
        workspace_id=WORKSPACE_ID,
        clock=FixedClock(FIXED_TIME),
    )
    service.invalidate_calculations_for_snapshot(
        SNAPSHOT_ID,
        reason="candle_correction",
        replacement_calculation_id=None,
    )
    reloaded = service._find_existing_calculation(result.calculation.idempotency_key)
    assert reloaded is None
    assert len(session.invalidations) == 1
    assert session.invalidations[0]["reason"] == "candle_correction"
    assert session.invalidations[0]["calculation_id"] == result.calculation.id


def test_warm_up_rows_allow_all_null_with_reason() -> None:
    candles = _make_candles(5, base=Decimal("100"), volume=Decimal("1"))
    session = _setup_session(candles)
    result = _compute_service(session)
    warm_up = [v for v in result.values if v.null_reason == _get_warm_up_null_reason()]
    assert len(warm_up) > 0
    for v in warm_up:
        assert v.numeric_value is None
        assert v.string_value is None
        assert v.boolean_value is None
        assert v.null_reason == _get_warm_up_null_reason()


def test_get_warm_up_null_reason() -> None:
    assert _get_warm_up_null_reason() == "insufficient_history"


def _get_warm_up_null_reason() -> str | None:
    return "insufficient_history"
