"""Deterministic fake Gemini provider for tests and local development."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from app.core.clock import Clock, FixedClock, IdGenerator, SystemIdGenerator
from app.infrastructure.ai.protocol import (
    AiBudgetDecision,
    AiUsage,
    AnalysisRequest,
    BudgetEvaluationRequest,
    JsonValue,
    ProviderAnalysisResponse,
    ProviderAttemptResult,
    ProviderCandidate,
    ProviderOutcome,
    SafetySeverity,
)


class FakeGeminiScenario(str, Enum):
    SUCCESS = "success"
    INVALID_SCHEMA = "invalid_schema"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    REFUSAL = "refusal"
    SAFETY_BLOCK = "safety_block"
    EMPTY_RESPONSE = "empty_response"
    MALFORMED = "malformed"
    STALE_SOURCE = "stale_source"


@dataclass(frozen=True, slots=True)
class FakeGeminiConfig:
    scenario: FakeGeminiScenario = FakeGeminiScenario.SUCCESS
    confidence: Decimal = Decimal("0.70")
    market_regime: str = "bullish"
    recommended_action: str = "hold"
    fixed_clock_time: datetime | None = None
    latency_ms: int = 50
    fixture_version: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.scenario, FakeGeminiScenario):
            raise ValueError(
                f"Invalid FakeGeminiScenario: {self.scenario!r}. "
                f"Valid values: {[s.value for s in FakeGeminiScenario]}"
            )
        if not self.fixture_version:
            raise ValueError("fixture_version must be non-empty")


class FakeGeminiProvider:
    _clock: Clock | None

    def __init__(
        self,
        config: FakeGeminiConfig,
        *,
        id_generator: IdGenerator | None = None,
    ) -> None:
        self.config = config
        self._id_generator = id_generator or SystemIdGenerator()
        if self.config.fixed_clock_time is not None:
            self._clock = FixedClock(self.config.fixed_clock_time)
        else:
            self._clock = None

    def _now(self) -> datetime:
        if self._clock is not None:
            return self._clock.now()
        return datetime.now(timezone.utc)

    async def check_budget(self, request: BudgetEvaluationRequest) -> AiBudgetDecision:
        return AiBudgetDecision(
            allowed=True,
            reason="Budget available",
            remaining_requests=100,
            remaining_tokens=10000,
            remaining_cost=Decimal("5.00"),
        )

    async def analyze(self, request: AnalysisRequest) -> ProviderAnalysisResponse:
        attempt_id = self._id_generator.generate(
            f"{request.logical_request_id}-attempt-"
        )

        if self.config.scenario == FakeGeminiScenario.SUCCESS:
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
                    "market_regime": self.config.market_regime,
                    "recommended_action": self.config.recommended_action,
                    "confidence": str(self.config.confidence),
                    "evidence": evidence,
                    "contradictions": [],
                    "risks": ["test_risk"],
                    "missing_information": [],
                    "invalidation_conditions": ["test_invalidation"],
                    "summary": "Fake Gemini analysis for testing.",
                },
                provider_code="fake-gemini",
                configured_model="fake-model",
                raw_response_reference="fake-response-ref",
            )
            return ProviderAnalysisResponse(
                attempt=ProviderAttemptResult(
                    attempt_id=attempt_id,
                    provider_code="fake-gemini",
                    configured_model="fake-model",
                    outcome=ProviderOutcome.SUCCESS,
                    usage=AiUsage(
                        prompt_tokens=10,
                        response_tokens=5,
                        total_tokens=15,
                        estimated_cost=Decimal("0.001"),
                    ),
                    safety_status=SafetySeverity.LOW,
                    raw_response_reference="fake-response-ref",
                    latency_ms=self.config.latency_ms,
                    retry_count=0,
                ),
                candidate=candidate,
            )

        if self.config.scenario == FakeGeminiScenario.INVALID_SCHEMA:
            candidate = ProviderCandidate(
                candidate_id=request.analysis_run_id,
                schema_version="1.0",
                payload={
                    "market_regime": self.config.market_regime,
                    "recommended_action": self.config.recommended_action,
                    "confidence": str(self.config.confidence),
                },
                provider_code="fake-gemini",
                configured_model="fake-model",
                raw_response_reference="fake-response-ref",
            )
            return ProviderAnalysisResponse(
                attempt=ProviderAttemptResult(
                    attempt_id=attempt_id,
                    provider_code="fake-gemini",
                    configured_model="fake-model",
                    outcome=ProviderOutcome.SUCCESS,
                    usage=AiUsage(
                        prompt_tokens=10,
                        response_tokens=5,
                        total_tokens=15,
                        estimated_cost=Decimal("0.001"),
                    ),
                    safety_status=SafetySeverity.LOW,
                    raw_response_reference="fake-response-ref",
                    latency_ms=self.config.latency_ms,
                    retry_count=0,
                ),
                candidate=candidate,
            )

        if self.config.scenario == FakeGeminiScenario.STALE_SOURCE:
            candidate = ProviderCandidate(
                candidate_id=request.analysis_run_id,
                schema_version="1.0",
                payload={
                    "schema_version": "1.0",
                    "market_regime": self.config.market_regime,
                    "recommended_action": self.config.recommended_action,
                    "confidence": str(self.config.confidence),
                    "evidence": [],
                    "contradictions": [],
                    "risks": ["stale_source"],
                    "missing_information": [],
                    "invalidation_conditions": [],
                    "summary": "Fake Gemini stale source for testing.",
                    "stale_source": True,
                },
                provider_code="fake-gemini",
                configured_model="fake-model",
                raw_response_reference="fake-response-ref",
            )
            return ProviderAnalysisResponse(
                attempt=ProviderAttemptResult(
                    attempt_id=attempt_id,
                    provider_code="fake-gemini",
                    configured_model="fake-model",
                    outcome=ProviderOutcome.SUCCESS,
                    usage=AiUsage(
                        prompt_tokens=10,
                        response_tokens=5,
                        total_tokens=15,
                        estimated_cost=Decimal("0.001"),
                    ),
                    safety_status=SafetySeverity.LOW,
                    raw_response_reference="fake-response-ref",
                    latency_ms=self.config.latency_ms,
                    retry_count=0,
                ),
                candidate=candidate,
            )

        outcome = {
            FakeGeminiScenario.TIMEOUT: ProviderOutcome.TIMEOUT,
            FakeGeminiScenario.RATE_LIMIT: ProviderOutcome.RATE_LIMITED,
            FakeGeminiScenario.REFUSAL: ProviderOutcome.REFUSAL,
            FakeGeminiScenario.SAFETY_BLOCK: ProviderOutcome.SAFETY_BLOCKED,
            FakeGeminiScenario.EMPTY_RESPONSE: ProviderOutcome.EMPTY_CANDIDATE,
            FakeGeminiScenario.MALFORMED: ProviderOutcome.MALFORMED_RESPONSE,
        }[self.config.scenario]
        return ProviderAnalysisResponse(
            attempt=ProviderAttemptResult(
                attempt_id=attempt_id,
                provider_code="fake-gemini",
                configured_model="fake-model",
                outcome=outcome,
                error_message="Fake error",
                latency_ms=self.config.latency_ms,
                retry_count=0,
            )
        )
