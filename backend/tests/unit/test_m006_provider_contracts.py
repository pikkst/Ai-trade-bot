"""Tests for provider contracts and deterministic fakes."""

from __future__ import annotations

import asyncio
import json
import types
from dataclasses import asdict, is_dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, cast, get_type_hints

import pytest

from app.core.clock import (
    DeterministicIdGenerator,
    FixedClock,
    SchedulerContext,
    SystemClock,
    SystemIdGenerator,
    bind_clock,
    bind_id_generator,
    bind_scheduler_context,
    get_clock,
    get_id_generator,
    get_scheduler_context,
)
from app.infrastructure.ai.fakes import (
    FakeGeminiConfig,
    FakeGeminiProvider,
    FakeGeminiScenario,
)
from app.infrastructure.ai.protocol import (
    AiBudgetDecision,
    AiUsage,
    BudgetEvaluationRequest,
    FreshnessPolicy,
    JsonValue,
    ProviderAnalysisResponse,
    ProviderAttemptResult,
    ProviderCandidate,
    ProviderOutcome,
    SafetySeverity,
)
from app.infrastructure.exchange.binance.fakes import (
    FakeBinanceConfig,
    FakeBinanceProvider,
    FakeBinanceScenario,
)
from app.infrastructure.exchange.binance.protocol import (
    BinanceInvalidSymbolError,
    BinanceMalformedDataError,
    BinanceProviderUnavailableError,
    BinanceRateLimitError,
    BinanceStaleDataError,
    BinanceTimeoutError,
    Candle,
    CandleInterval,
    ExchangeTime,
    RateLimitState,
)
from tests.fixtures.providers import (
    FIXED_TIME,
    FIXTURE_VERSION,
    make_analysis_request,
    make_binance_provider,
    make_budget_evaluation_request,
    make_gemini_provider,
)

FIXED_CLOCK = FixedClock(FIXED_TIME)


def test_fixture_version_is_explicit() -> None:
    assert FIXTURE_VERSION == "2026-08-07-m006-v1"


def test_fake_binance_config_carries_fixture_version() -> None:
    config = FakeBinanceConfig(fixture_version=FIXTURE_VERSION)
    assert config.fixture_version == FIXTURE_VERSION


def test_fake_gemini_config_carries_fixture_version() -> None:
    config = FakeGeminiConfig(fixture_version=FIXTURE_VERSION)
    assert config.fixture_version == FIXTURE_VERSION


def test_fake_binance_config_requires_fixture_version() -> None:
    with pytest.raises(ValueError, match="fixture_version must be non-empty"):
        FakeBinanceConfig(fixture_version="")


def test_fake_gemini_config_requires_fixture_version() -> None:
    with pytest.raises(ValueError, match="fixture_version must be non-empty"):
        FakeGeminiConfig(fixture_version="")


def test_fake_binance_provider_requires_explicit_config() -> None:
    config = FakeBinanceConfig(fixture_version=FIXTURE_VERSION)
    provider = FakeBinanceProvider(config=config)
    assert provider.config is config


def test_fake_gemini_provider_requires_explicit_config() -> None:
    config = FakeGeminiConfig(fixture_version=FIXTURE_VERSION)
    provider = FakeGeminiProvider(config=config)
    assert provider.config is config


def test_make_binance_provider_binds_fixture_version() -> None:
    provider = make_binance_provider()
    assert provider.config.fixture_version == FIXTURE_VERSION


def test_make_gemini_provider_binds_fixture_version() -> None:
    provider = make_gemini_provider()
    assert provider.config.fixture_version == FIXTURE_VERSION


def test_fake_binance_scenario_validation_fails_closed() -> None:
    with pytest.raises(ValueError, match="FakeBinanceScenario"):
        FakeBinanceConfig(scenario="rate_limt")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="FakeBinanceScenario"):
        make_binance_provider("typo")


def test_fake_gemini_scenario_validation_fails_closed() -> None:
    with pytest.raises(ValueError, match="FakeGeminiScenario"):
        FakeGeminiConfig(scenario="typo")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="FakeGeminiScenario"):
        make_gemini_provider("typo")


def test_fixed_clock_returns_constant_time() -> None:
    assert FIXED_CLOCK.now() == FIXED_TIME


def test_system_clock_returns_current_time() -> None:
    clock = SystemClock()
    now = clock.now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None


def test_deterministic_id_generator_produces_sequence() -> None:
    generator = DeterministicIdGenerator(prefix="test-")
    ids = [generator.generate() for _ in range(5)]
    assert ids == [
        "test-00000001",
        "test-00000002",
        "test-00000003",
        "test-00000004",
        "test-00000005",
    ]


def test_system_id_generator_produces_unique_ids() -> None:
    generator = SystemIdGenerator()
    ids = [generator.generate("run-") for _ in range(10)]
    assert len(set(ids)) == 10
    assert all(id.startswith("run-") for id in ids)


def test_clock_context_injection() -> None:
    custom_clock = FixedClock(FIXED_TIME)
    with bind_clock(custom_clock):
        assert get_clock() is custom_clock
    assert isinstance(get_clock(), SystemClock)


def test_id_generator_context_injection() -> None:
    custom_generator = DeterministicIdGenerator(prefix="injected-")
    with bind_id_generator(custom_generator):
        assert get_id_generator() is custom_generator
    assert isinstance(get_id_generator(), SystemIdGenerator)


def test_scheduler_context_round_trip() -> None:
    context = SchedulerContext(scheduled_time=FIXED_TIME)
    with bind_scheduler_context(context):
        assert get_scheduler_context() is context
    assert get_scheduler_context() is None


def test_fake_binance_success_scenario() -> None:
    provider = make_binance_provider(FakeBinanceScenario.SUCCESS)
    time = asyncio.run(provider.get_server_time())
    assert isinstance(time, ExchangeTime)

    metadata = asyncio.run(provider.get_symbol_metadata("BTCEUR"))
    assert metadata.symbol == "BTCEUR"
    assert metadata.base_asset == "BTC"
    assert metadata.quote_asset == "EUR"

    candles = asyncio.run(
        provider.get_finalized_candles(
            "BTCEUR",
            CandleInterval.ONE_HOUR,
            FIXED_TIME,
            FIXED_TIME + timedelta(hours=2),
        )
    )
    assert len(candles) == 2
    assert all(isinstance(c, Candle) for c in candles)

    health = asyncio.run(provider.get_health())
    assert health.healthy is True


def test_fake_binance_timeout_scenario() -> None:
    provider = make_binance_provider(FakeBinanceScenario.TIMEOUT)
    with pytest.raises(BinanceTimeoutError):
        asyncio.run(provider.get_server_time())


def test_fake_binance_rate_limit_scenario() -> None:
    provider = make_binance_provider(FakeBinanceScenario.RATE_LIMIT)
    with pytest.raises(BinanceRateLimitError):
        asyncio.run(provider.get_symbol_metadata("BTCEUR"))


def test_fake_binance_unavailable_scenario() -> None:
    provider = make_binance_provider(FakeBinanceScenario.UNAVAILABLE)
    with pytest.raises(BinanceProviderUnavailableError):
        asyncio.run(
            provider.get_finalized_candles(
                "BTCEUR",
                CandleInterval.ONE_HOUR,
                FIXED_TIME,
                FIXED_TIME + timedelta(hours=1),
            )
        )


def test_fake_binance_invalid_symbol_scenario() -> None:
    provider = make_binance_provider(FakeBinanceScenario.INVALID_SYMBOL)
    with pytest.raises(BinanceInvalidSymbolError):
        asyncio.run(provider.get_symbol_metadata("UNKNOWN"))


def test_fake_binance_malformed_scenario() -> None:
    provider = make_binance_provider(FakeBinanceScenario.MALFORMED)
    with pytest.raises(BinanceMalformedDataError):
        asyncio.run(
            provider.get_finalized_candles(
                "BTCEUR",
                CandleInterval.ONE_HOUR,
                FIXED_TIME,
                FIXED_TIME + timedelta(hours=1),
            )
        )


def test_fake_binance_stale_scenario_raises_stale_error() -> None:
    provider = make_binance_provider(FakeBinanceScenario.STALE)
    with pytest.raises(BinanceStaleDataError):
        asyncio.run(
            provider.get_finalized_candles(
                "BTCEUR",
                CandleInterval.ONE_HOUR,
                FIXED_TIME,
                FIXED_TIME + timedelta(hours=1),
            )
        )


def test_fake_binance_gap_scenario_skips_candles() -> None:
    config = FakeBinanceConfig(
        scenario=FakeBinanceScenario.GAP,
        fixed_clock_time=FIXED_TIME,
        fixture_version=FIXTURE_VERSION,
        gap_start=FIXED_TIME,
        gap_end=FIXED_TIME + timedelta(hours=1),
    )
    provider = FakeBinanceProvider(config=config)
    candles = asyncio.run(
        provider.get_finalized_candles(
            "BTCEUR",
            CandleInterval.ONE_HOUR,
            FIXED_TIME,
            FIXED_TIME + timedelta(hours=2),
        )
    )
    assert len(candles) == 1


def test_fake_binance_rate_limit_state() -> None:
    provider = make_binance_provider(FakeBinanceScenario.SUCCESS)
    state = asyncio.run(provider.get_rate_limit_state())
    assert isinstance(state, RateLimitState)
    assert state.remaining_requests == 1000


def test_fake_gemini_success_scenario_returns_candidate() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SUCCESS)
    budget_request = make_budget_evaluation_request()
    budget = asyncio.run(provider.check_budget(budget_request))
    assert budget.allowed is True

    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.SUCCESS
    assert response.candidate is not None
    assert response.candidate.schema_version == "1.0"
    assert response.candidate.payload["schema_version"] == "1.0"
    assert response.candidate.payload["market_regime"] == "bullish"
    assert response.candidate.provider_code == "fake-gemini"
    evidence_features = [
        cast(dict[str, JsonValue], e)["feature"]
        for e in cast(list[JsonValue], response.candidate.payload.get("evidence", []))
    ]
    assert all(f in request.allowed_evidence_ids for f in evidence_features)


def test_fake_gemini_success_scenario_empty_evidence_ids() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SUCCESS)
    request = make_analysis_request()
    request = replace(request, allowed_evidence_ids=[])
    response = asyncio.run(provider.analyze(request))
    assert response.candidate is not None
    evidence = cast(list[JsonValue], response.candidate.payload.get("evidence", []))
    assert len(evidence) == 0


def test_fake_gemini_invalid_schema_scenario_returns_success_with_candidate() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.INVALID_SCHEMA)
    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.SUCCESS
    assert response.candidate is not None
    assert response.candidate.payload["market_regime"] == "bullish"
    assert "evidence" not in response.candidate.payload


def test_fake_gemini_timeout_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.TIMEOUT)
    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.TIMEOUT
    assert response.attempt.attempt_id.endswith("-attempt-00000001")
    assert response.attempt.retry_count == 0
    assert response.candidate is None


def test_fake_gemini_rate_limit_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.RATE_LIMIT)
    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.RATE_LIMITED
    assert response.attempt.attempt_id.endswith("-attempt-00000001")
    assert response.attempt.retry_count == 0
    assert response.candidate is None


def test_fake_gemini_refusal_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.REFUSAL)
    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.REFUSAL
    assert response.attempt.attempt_id.endswith("-attempt-00000001")
    assert response.attempt.retry_count == 0
    assert response.candidate is None


def test_fake_gemini_safety_block_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SAFETY_BLOCK)
    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.SAFETY_BLOCKED
    assert response.attempt.attempt_id.endswith("-attempt-00000001")
    assert response.attempt.retry_count == 0
    assert response.candidate is None


def test_fake_gemini_empty_response_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.EMPTY_RESPONSE)
    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.EMPTY_CANDIDATE
    assert response.attempt.attempt_id.endswith("-attempt-00000001")
    assert response.attempt.retry_count == 0
    assert response.candidate is None


def test_fake_gemini_malformed_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.MALFORMED)
    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.MALFORMED_RESPONSE
    assert response.attempt.attempt_id.endswith("-attempt-00000001")
    assert response.attempt.retry_count == 0
    assert response.candidate is None


def test_fake_gemini_stale_source_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.STALE_SOURCE)
    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.SUCCESS
    assert response.attempt.attempt_id.endswith("-attempt-00000001")
    assert response.attempt.retry_count == 0
    assert response.attempt.stale_source is True
    assert response.candidate is not None
    assert response.candidate.payload["schema_version"] == "1.0"
    assert "stale_source" not in response.candidate.payload


def _dataclass_to_json(obj: Any) -> str:
    return json.dumps(asdict(obj), default=str)


def _restore_from_dataclass_json(data: dict[str, Any], cls: Any) -> Any:
    hints = get_type_hints(cls)
    restored_kwargs: dict[str, Any] = {}

    def _unwrap_union(tp: Any) -> Any:
        if isinstance(tp, types.UnionType):
            args = tp.__args__
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                return non_none[0]
            return tp
        return tp

    for name, value in data.items():
        expected_type = hints.get(name)
        unwrapped = _unwrap_union(expected_type)

        if unwrapped is not None and is_dataclass(unwrapped):
            restored_kwargs[name] = _restore_from_dataclass_json(value, unwrapped)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            item_type = None
            origin = getattr(expected_type, "__origin__", None)
            if origin is list or origin is None:
                item_type = (
                    expected_type.__args__[0]  # type: ignore[union-attr]
                    if hasattr(expected_type, "__args__")
                    else None
                )
            item_type = _unwrap_union(item_type)
            if item_type is not None and is_dataclass(item_type):
                restored_kwargs[name] = [
                    _restore_from_dataclass_json(item, item_type) for item in value
                ]
            else:
                restored_kwargs[name] = value
        elif isinstance(unwrapped, type) and issubclass(unwrapped, Decimal):
            restored_kwargs[name] = Decimal(str(value))
        elif isinstance(unwrapped, type) and issubclass(unwrapped, Enum):
            restored_kwargs[name] = unwrapped(value)
        elif isinstance(unwrapped, type) and issubclass(unwrapped, datetime):
            restored_kwargs[name] = datetime.fromisoformat(value)
        elif (
            hasattr(expected_type, "__origin__")
            and expected_type.__origin__ is not None  # type: ignore[union-attr]
        ):
            origin = expected_type.__origin__  # type: ignore[union-attr]
            args = getattr(expected_type, "__args__", ())
            if origin is not None and args:
                if origin is dict and len(args) == 2:
                    value_type = _unwrap_union(args[1])
                    if is_dataclass(value_type) and isinstance(value, dict):
                        restored_kwargs[name] = {
                            k: _restore_from_dataclass_json(v, value_type)
                            for k, v in value.items()
                        }
                    else:
                        restored_kwargs[name] = value
                else:
                    inner = _unwrap_union(args[0])
                    if is_dataclass(inner):
                        restored_kwargs[name] = _restore_from_dataclass_json(
                            value, inner
                        )
                    elif isinstance(inner, type) and issubclass(inner, Decimal):
                        restored_kwargs[name] = Decimal(str(value))
                    elif isinstance(inner, type) and issubclass(inner, datetime):
                        restored_kwargs[name] = datetime.fromisoformat(value)
                    elif isinstance(inner, type) and issubclass(inner, Enum):
                        restored_kwargs[name] = inner(value)
                    else:
                        restored_kwargs[name] = value
            else:
                restored_kwargs[name] = value
        else:
            restored_kwargs[name] = value
    return cls(**restored_kwargs)


def test_analysis_request_serialization_round_trip() -> None:
    request = make_analysis_request()
    payload = _dataclass_to_json(request)
    data = json.loads(payload)
    restored = _restore_from_dataclass_json(data, type(request))
    assert restored.analysis_run_id == request.analysis_run_id
    assert restored.snapshot_id == request.snapshot_id
    assert restored.analysis_time == request.analysis_time
    assert restored.exchange == request.exchange
    assert restored.symbol == request.symbol
    assert restored.interval == request.interval
    assert restored.logical_request_id == request.logical_request_id
    assert restored.idempotency_key == request.idempotency_key
    assert restored.context.correlation_id == request.context.correlation_id
    assert restored.budget_decision.remaining_cost == Decimal("5.00")
    assert restored.features["ema_50"].value == "50000.00"
    assert restored.features["ema_50"].unit == "USD"
    assert restored.freshness_quality is not None
    assert restored.freshness_quality.outcome == FreshnessPolicy.ACCEPTED
    assert restored.feature_calculation is not None
    assert restored.feature_calculation.calculation_id == "calc-001"


def test_provider_attempt_result_serialization_round_trip() -> None:
    result = ProviderAttemptResult(
        attempt_id="attempt-1",
        provider_code="fake",
        configured_model="model",
        outcome=ProviderOutcome.SUCCESS,
        usage=AiUsage(
            prompt_tokens=10,
            response_tokens=5,
            total_tokens=15,
            estimated_cost=Decimal("0.001"),
        ),
        safety_status=SafetySeverity.LOW,
        raw_response_reference="ref",
        latency_ms=50,
        retry_count=0,
    )
    payload = _dataclass_to_json(result)
    data = json.loads(payload)
    restored = _restore_from_dataclass_json(data, ProviderAttemptResult)
    assert restored == result
    assert isinstance(restored.usage, AiUsage)
    assert restored.usage.estimated_cost == Decimal("0.001")
    assert isinstance(restored.outcome, ProviderOutcome)


def test_ai_budget_decision_serialization_round_trip() -> None:
    decision = AiBudgetDecision(
        allowed=True,
        reason="Budget available",
        remaining_requests=100,
        remaining_tokens=10000,
        remaining_cost=Decimal("5.00"),
    )
    payload = _dataclass_to_json(decision)
    data = json.loads(payload)
    restored = _restore_from_dataclass_json(data, AiBudgetDecision)
    assert restored == decision
    assert restored.remaining_cost == Decimal("5.00")


def test_provider_candidate_serialization_round_trip() -> None:
    candidate = ProviderCandidate(
        candidate_id="cand-1",
        schema_version="1.0",
        payload={"market_regime": "bullish", "confidence": "0.70"},
        provider_code="fake-gemini",
        configured_model="model",
        raw_response_reference="ref",
    )
    payload = _dataclass_to_json(candidate)
    data = json.loads(payload)
    restored = _restore_from_dataclass_json(data, ProviderCandidate)
    assert restored == candidate
    assert isinstance(restored.payload, dict)
    assert restored.payload["market_regime"] == "bullish"


def test_budget_evaluation_request_serialization_round_trip() -> None:
    request = make_budget_evaluation_request()
    payload = _dataclass_to_json(request)
    data = json.loads(payload)
    restored = _restore_from_dataclass_json(data, BudgetEvaluationRequest)
    assert restored.analysis_run_id == request.analysis_run_id
    assert restored.exchange == request.exchange
    assert restored.symbol == request.symbol
    assert restored.feature_calculation.calculation_id == "calc-001"
    assert restored.context.correlation_id == request.context.correlation_id


def test_deterministic_repeated_runs_produce_same_result() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SUCCESS)
    request = make_analysis_request()
    result1 = asyncio.run(provider.analyze(request))
    result2 = asyncio.run(provider.analyze(request))
    assert result1.attempt.outcome == result2.attempt.outcome
    assert result1.attempt.latency_ms == result2.attempt.latency_ms
    assert result1.candidate == result2.candidate


def test_fake_gemini_retry_creates_unique_attempt_identity() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SUCCESS)
    request = make_analysis_request()
    result1 = asyncio.run(provider.analyze(request))
    result2 = asyncio.run(provider.analyze(request))
    assert result1.attempt.attempt_id != result2.attempt.attempt_id
    assert result1.attempt.retry_count == 0
    assert result2.attempt.retry_count == 1


def test_fake_gemini_independent_requests_get_independent_sequences() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SUCCESS)
    request_a = make_analysis_request()
    request_b = replace(request_a, logical_request_id="logical-b")
    result_a = asyncio.run(provider.analyze(request_a))
    result_b = asyncio.run(provider.analyze(request_b))
    assert result_a.attempt.attempt_id == "logical-001-attempt-00000001"
    assert result_b.attempt.attempt_id == "logical-b-attempt-00000002"
    assert result_a.attempt.retry_count == 0
    assert result_b.attempt.retry_count == 0


def test_fake_gemini_cross_instance_unique_attempt_identity() -> None:
    shared_generator = DeterministicIdGenerator()
    provider_a = make_gemini_provider(
        FakeGeminiScenario.SUCCESS, id_generator=shared_generator
    )
    provider_b = make_gemini_provider(
        FakeGeminiScenario.SUCCESS, id_generator=shared_generator
    )
    request = make_analysis_request()
    result_a = asyncio.run(provider_a.analyze(request))
    result_b = asyncio.run(provider_b.analyze(request))
    assert result_a.attempt.attempt_id != result_b.attempt.attempt_id
    assert result_a.attempt.attempt_id == "logical-001-attempt-00000001"
    assert result_b.attempt.attempt_id == "logical-001-attempt-00000002"


def test_fake_gemini_failure_preserves_attempt_metadata() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.TIMEOUT)
    request = make_analysis_request()
    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.TIMEOUT
    assert response.attempt.attempt_id == "logical-001-attempt-00000001"
    assert response.attempt.retry_count == 0
    assert response.attempt.provider_code == "fake-gemini"
    assert response.attempt.configured_model == "fake-model"
    assert response.attempt.error_message == "Fake error"
    assert response.candidate is None


def test_no_network_call_in_normal_unit_tests() -> None:
    provider = make_binance_provider(FakeBinanceScenario.SUCCESS)
    candles = asyncio.run(
        provider.get_finalized_candles(
            "BTCEUR",
            CandleInterval.ONE_HOUR,
            FIXED_TIME,
            FIXED_TIME + timedelta(hours=1),
        )
    )
    assert len(candles) == 1
    assert isinstance(candles[0], Candle)


def test_network_guard_blocks_non_loopback_connections() -> None:
    socket_module = pytest.importorskip("socket")
    with pytest.raises(
        ConnectionError, match="Unit tests must not open network connections"
    ):
        socket_module.create_connection(("8.8.8.8", 53))


def test_network_guard_blocks_udp_sendto() -> None:
    socket_module = pytest.importorskip("socket")
    sock = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_DGRAM)
    with pytest.raises(
        ConnectionError, match="Unit tests must not open network connections"
    ):
        sock.sendto(b"ping", ("8.8.8.8", 53))
    sock.close()


def test_network_guard_blocks_dns_getaddrinfo() -> None:
    socket_module = pytest.importorskip("socket")
    with pytest.raises(
        ConnectionError, match="Unit tests must not open network connections"
    ):
        socket_module.getaddrinfo("example.com", 80)
