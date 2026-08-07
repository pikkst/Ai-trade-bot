"""Tests for provider contracts and deterministic fakes."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

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
    FakeGeminiScenario,
)
from app.infrastructure.ai.protocol import (
    LLMEmptyResponseError,
    LLMMalformedResponseError,
    LLMRateLimitError,
    LLMRefusalError,
    LLMSafetyBlockError,
    LLMStaleSourceError,
    LLMTimeoutError,
    ProviderAttemptResult,
    ProviderOutcome,
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
    BinanceTimeoutError,
    Candle,
    CandleInterval,
    ExchangeTime,
    RateLimitState,
)
from tests.fixtures.providers import (
    FIXED_TIME,
    make_analysis_request,
    make_binance_provider,
    make_gemini_provider,
)

FIXED_CLOCK = FixedClock(FIXED_TIME)


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


def test_fake_gemini_success_scenario() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SUCCESS)
    request = make_analysis_request()
    budget = asyncio.run(provider.check_budget(request))
    assert budget.allowed is True

    result = asyncio.run(provider.analyze(request))
    assert isinstance(result, ProviderAttemptResult)
    assert result.outcome == ProviderOutcome.SUCCESS


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


def test_validated_ai_report_schema_enforces_fields() -> None:
    report = ValidatedAiReport(
        schema_version="1.0",
        market_regime="bullish",
        recommended_action="hold",
        confidence=Decimal("0.70"),
        evidence=[],
        contradictions=[],
        risks=[],
        missing_information=[],
        invalidation_conditions=[],
        summary="Test summary",
    )
    assert report.confidence == Decimal("0.70")


def test_deterministic_repeated_runs_produce_same_result() -> None:
    provider = make_gemini_provider(FakeGeminiScenario.SUCCESS)
    request = make_analysis_request()
    result1 = asyncio.run(provider.analyze(request))
    result2 = asyncio.run(provider.analyze(request))
    assert result1.outcome == result2.outcome
    assert result1.latency_ms == result2.latency_ms


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
