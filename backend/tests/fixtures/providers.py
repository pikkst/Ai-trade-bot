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
    BudgetEvaluationRequest,
    FeatureCalculationReference,
    FeatureValue,
    FreshnessPolicy,
    FreshnessQualityOutcome,
    JsonValue,
    ProviderAnalysisResponse,
    ProviderAttemptResult,
    ProviderCandidate,
    ProviderOutcome,
    SafetySeverity,
    TrustedSummaryReference,
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
    feature_calc = FeatureCalculationReference(
        calculation_id="calc-001",
        calculation_hash="calc-hash-001",
        calculation_version="1.0",
        feature_set_hash="feature-set-hash-001",
    )
    freshness = FreshnessQualityOutcome(
        policy_version="1.0",
        outcome=FreshnessPolicy.ACCEPTED,
        latest_candle_time=FIXED_TIME,
        max_age_minutes=60,
        gap_count=0,
        notes="",
    )
    return AnalysisRequest(
        analysis_run_id=analysis_run_id,
        snapshot_id=snapshot_id,
        snapshot_hash=snapshot_hash,
        exchange="binance",
        symbol="BTCEUR",
        interval="1h",
        analysis_time=FIXED_TIME,
        latest_candle_time=FIXED_TIME,
        freshness_quality=freshness,
        feature_calculation=feature_calc,
        allowed_evidence_ids=["ema_50", "ema_200", "rsi_14", "atr_14"],
        prompt_version="1.0",
        schema_version="1.0",
        safety_version="1.0",
        validation_version="1.0",
        provider_config_version="1.0",
        logical_request_id="logical-001",
        idempotency_key="fixture-test-value",
        features={
            "ema_50": FeatureValue(value="50000.00", unit="USD", version="1.0"),
            "ema_200": FeatureValue(value="49000.00", unit="USD", version="1.0"),
            "rsi_14": FeatureValue(value="55.0", unit="index", version="1.0"),
            "atr_14": FeatureValue(value="500.00", unit="USD", version="1.0"),
        },
        trusted_summary_references=[
            TrustedSummaryReference(
                source_id="summary-001",
                summary_type="market_context",
                reference="summary-ref-001",
            )
        ],
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


def make_budget_evaluation_request(
    analysis_run_id: str = "run-00000001",
    snapshot_id: str = "snap-00000001",
    snapshot_hash: str = "a" * 64,
) -> BudgetEvaluationRequest:
    feature_calc = FeatureCalculationReference(
        calculation_id="calc-001",
        calculation_hash="calc-hash-001",
        calculation_version="1.0",
        feature_set_hash="feature-set-hash-001",
    )
    return BudgetEvaluationRequest(
        analysis_run_id=analysis_run_id,
        snapshot_id=snapshot_id,
        snapshot_hash=snapshot_hash,
        exchange="binance",
        symbol="BTCEUR",
        interval="1h",
        feature_calculation=feature_calc,
        prompt_version="1.0",
        schema_version="1.0",
        safety_version="1.0",
        validation_version="1.0",
        provider_config_version="1.0",
        logical_request_id="logical-001",
        idempotency_key="fixture-test-value",
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
    attempt_id: str | None = None,
) -> ProviderAnalysisResponse:
    if request is None:
        request = make_analysis_request()
    if candidate is None:
        evidence: list[JsonValue] = (
            [{"feature": request.allowed_evidence_ids[0], "observation": "true"}]
            if request.allowed_evidence_ids
            else []
        )
        candidate = ProviderCandidate(
            candidate_id=request.analysis_run_id,
            schema_version="1.0",
            payload={
                "schema_version": "1.0",
                "market_regime": "bullish",
                "recommended_action": "hold",
                "confidence": "0.70",
                "evidence": evidence,
                "contradictions": [],
                "risks": ["test_risk"],
                "missing_information": [],
                "invalidation_conditions": ["test_invalidation"],
                "summary": "Fake Gemini analysis for testing.",
            },
            provider_code="fixture-provider",
            configured_model="fixture-model",
            raw_response_reference="fixture-response-ref",
        )
    if attempt_id is None:
        attempt_id = f"{request.analysis_run_id}-attempt-01"
    attempt = ProviderAttemptResult(
        attempt_id=attempt_id,
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
