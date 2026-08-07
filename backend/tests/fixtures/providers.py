"""Versioned provider fixtures and scenario configurations."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.core.clock import DeterministicIdGenerator, FixedClock
from app.infrastructure.ai.fakes import (
    FakeGeminiConfig,
    FakeGeminiProvider,
    FakeGeminiScenario,
)
from app.infrastructure.ai.protocol import (
    AiBudgetDecision,
    AiUsage,
    AnalysisRequest,
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
from app.request_context import ExecutionContext

FIXTURE_VERSION = "2026-08-07-m006-v1"
FIXED_TIME = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)


def make_fixed_clock() -> FixedClock:
    return FixedClock(FIXED_TIME)


def make_deterministic_id_generator() -> DeterministicIdGenerator:
    return DeterministicIdGenerator(prefix="test-")


def make_binance_provider(
    scenario: str | FakeBinanceScenario = FakeBinanceScenario.SUCCESS,
) -> FakeBinanceProvider:
    if isinstance(scenario, str):
        scenario = FakeBinanceScenario(scenario)
    return FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=scenario,
            fixed_clock_time=FIXED_TIME,
            fixture_version=FIXTURE_VERSION,
        )
    )


def make_gemini_provider(
    scenario: str | FakeGeminiScenario = FakeGeminiScenario.SUCCESS,
) -> FakeGeminiProvider:
    if isinstance(scenario, str):
        scenario = FakeGeminiScenario(scenario)
    return FakeGeminiProvider(
        config=FakeGeminiConfig(
            scenario=scenario,
            fixed_clock_time=FIXED_TIME,
            fixture_version=FIXTURE_VERSION,
        )
    )


def make_analysis_request(
    analysis_run_id: str = "run-00000001",
    snapshot_id: str = "snap-00000001",
    snapshot_hash: str = "a" * 64,
) -> AnalysisRequest:
    return AnalysisRequest(
        analysis_run_id=analysis_run_id,
        snapshot_id=snapshot_id,
        snapshot_hash=snapshot_hash,
        symbol="BTCEUR",
        interval="1h",
        analysis_time=FIXED_TIME,
        features={
            "ema_50": Decimal("50000.00"),
            "ema_200": Decimal("49000.00"),
            "rsi_14": Decimal("55.0"),
            "atr_14": Decimal("500.00"),
        },
        prompt_version="1.0",
        schema_version="1.0",
        provider_config_version="1.0",
        budget_decision=AiBudgetDecision(
            allowed=True,
            reason="Fixture budget",
            remaining_requests=100,
            remaining_tokens=10000,
            remaining_cost=Decimal("5.00"),
        ),
        context=ExecutionContext(
            correlation_id="corr-fixture",
            request_id="req-fixture",
            job_id="job-fixture",
            cycle_id="cycle-fixture",
        ),
    )


def make_provider_analysis_response(
    request: AnalysisRequest | None = None,
    *,
    candidate: ProviderCandidate | None = None,
    outcome: ProviderOutcome = ProviderOutcome.SUCCESS,
) -> ProviderAnalysisResponse:
    if request is None:
        request = make_analysis_request()
    if candidate is None:
        candidate = ProviderCandidate(
            candidate_id=request.analysis_run_id,
            schema_version="1.0",
            payload={
                "market_regime": "bullish",
                "recommended_action": "hold",
                "confidence": "0.70",
            },
            provider_code="fixture-provider",
            configured_model="fixture-model",
            raw_response_reference="fixture-response-ref",
        )
    attempt = ProviderAttemptResult(
        attempt_id=request.analysis_run_id,
        provider_code="fixture-provider",
        configured_model="fixture-model",
        outcome=outcome,
        usage=AiUsage(
            prompt_tokens=10,
            response_tokens=5,
            total_tokens=15,
            estimated_cost=Decimal("0.001"),
        ),
        safety_status=SafetySeverity.LOW,
        raw_response_reference="fixture-response-ref",
        latency_ms=50,
        retry_count=0,
    )
    return ProviderAnalysisResponse(attempt=attempt, candidate=candidate)
