"""Tests for provider contracts and deterministic fakes."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

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
    FakeGeminiScenario,
)
from app.infrastructure.ai.protocol import (
    AiBudgetDecision,
    AiUsage,
    LLMEmptyResponseError,
    LLMMalformedResponseError,
    LLMRateLimitError,
    LLMRefusalError,
    LLMSafetyBlockError,
    LLMStaleSourceError,
    LLMTimeoutError,
    ProviderAnalysisResponse,
    ProviderAttemptResult,
    ProviderOutcome,
    SafetySeverity,
    ValidatedAiReport,
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
    make_gemini_provider,
)

FIXED_CLOCK = FixedClock(FIXED_TIME)


def test_fixture_version_is_explicit() -> None:
    assert FIXTURE_VERSION == "2026-08-07-m006-v1"


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


def test_fake_gemini_success_scenario_returns_response_with_report() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SUCCESS)
    request = make_analysis_request()
    budget = asyncio.run(provider.check_budget(request))
    assert budget.allowed is True

    response = asyncio.run(provider.analyze(request))
    assert isinstance(response, ProviderAnalysisResponse)
    assert response.attempt.outcome == ProviderOutcome.SUCCESS
    assert response.report is not None
    assert response.report.schema_version == "1.0"
    assert response.report.market_regime == "bullish"


def test_fake_gemini_timeout_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.TIMEOUT)
    request = make_analysis_request()
    with pytest.raises(LLMTimeoutError):
        asyncio.run(provider.analyze(request))


def test_fake_gemini_rate_limit_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.RATE_LIMIT)
    request = make_analysis_request()
    with pytest.raises(LLMRateLimitError):
        asyncio.run(provider.analyze(request))


def test_fake_gemini_refusal_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.REFUSAL)
    request = make_analysis_request()
    with pytest.raises(LLMRefusalError):
        asyncio.run(provider.analyze(request))


def test_fake_gemini_safety_block_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SAFETY_BLOCK)
    request = make_analysis_request()
    with pytest.raises(LLMSafetyBlockError):
        asyncio.run(provider.analyze(request))


def test_fake_gemini_empty_response_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.EMPTY_RESPONSE)
    request = make_analysis_request()
    with pytest.raises(LLMEmptyResponseError):
        asyncio.run(provider.analyze(request))


def test_fake_gemini_malformed_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.MALFORMED)
    request = make_analysis_request()
    with pytest.raises(LLMMalformedResponseError):
        asyncio.run(provider.analyze(request))


def test_fake_gemini_stale_source_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.STALE_SOURCE)
    request = make_analysis_request()
    with pytest.raises(LLMStaleSourceError):
        asyncio.run(provider.analyze(request))


def test_validated_ai_report_serialization_round_trip() -> None:
    report = ValidatedAiReport(
        schema_version="1.0",
        market_regime="bullish",
        recommended_action="hold",
        confidence=Decimal("0.70"),
        evidence=[{"feature": "ema_50", "observation": "true"}],
        contradictions=[],
        risks=["test_risk"],
        missing_information=[],
        invalidation_conditions=["test_invalidation"],
        summary="Test summary",
    )
    payload = report.model_dump(mode="json")
    restored = ValidatedAiReport.model_validate(payload)
    assert restored == report
    assert restored.confidence == Decimal("0.70")


def _dataclass_to_json(obj: Any) -> str:
    return json.dumps(asdict(obj), default=str)


def _dataclass_from_json(json_str: str, cls: type[Any]) -> Any:
    data = json.loads(json_str)
    if is_dataclass(cls) and not isinstance(cls, type):
        cls = type(cls)
    if not is_dataclass(cls):
        raise TypeError(f"{cls} is not a dataclass")
    return cls(**data)


def test_analysis_request_serialization_round_trip() -> None:
    request = make_analysis_request()
    payload = _dataclass_to_json(request)
    data = json.loads(payload)
    assert data["snapshot_id"] == request.snapshot_id
    assert data["context"]["correlation_id"] == request.context.correlation_id


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
    assert data["attempt_id"] == "attempt-1"
    assert data["usage"]["estimated_cost"] == "0.001"
    assert data["safety_status"] == "low"


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
    assert data["remaining_cost"] == "5.00"


def test_deterministic_repeated_runs_produce_same_result() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SUCCESS)
    request = make_analysis_request()
    result1 = asyncio.run(provider.analyze(request))
    result2 = asyncio.run(provider.analyze(request))
    assert result1.attempt.outcome == result2.attempt.outcome
    assert result1.attempt.latency_ms == result2.attempt.latency_ms
    assert result1.report == result2.report


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
