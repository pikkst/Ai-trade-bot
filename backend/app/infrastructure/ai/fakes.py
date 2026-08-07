"""Deterministic fake Gemini provider for tests and local development."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from app.core.clock import Clock, FixedClock
from app.infrastructure.ai.protocol import (
    AiBudgetDecision,
    AiUsage,
    AnalysisRequest,
    BudgetEvaluationRequest,
    JsonValue,
    LLMEmptyResponseError,
    LLMMalformedResponseError,
    LLMRateLimitError,
    LLMRefusalError,
    LLMSafetyBlockError,
    LLMStaleSourceError,
    LLMTimeoutError,
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

    def __init__(self, config: FakeGeminiConfig) -> None:
        self.config = config
        if self.config.fixed_clock_time is not None:
            self._clock = FixedClock(self.config.fixed_clock_time)
        else:
            self._clock = None
        self._request_count = 0
        self._analyze_counts: dict[str, int] = {}

    def _now(self) -> datetime:
        if self._clock is not None:
            return self._clock.now()
        return datetime.now(timezone.utc)

    def _check_scenario(self, attempt_id: str) -> None:
        self._request_count += 1
        if self.config.scenario == FakeGeminiScenario.TIMEOUT:
            raise LLMTimeoutError(
                "Fake Gemini timeout", details={"attempt_id": attempt_id}
            )
        if self.config.scenario == FakeGeminiScenario.RATE_LIMIT:
            raise LLMRateLimitError(
                "Fake Gemini rate limit", details={"attempt_id": attempt_id}
            )
        if self.config.scenario == FakeGeminiScenario.REFUSAL:
            raise LLMRefusalError(
                "Fake Gemini refusal", details={"attempt_id": attempt_id}
            )
        if self.config.scenario == FakeGeminiScenario.SAFETY_BLOCK:
            raise LLMSafetyBlockError(
                "Fake Gemini safety block", details={"attempt_id": attempt_id}
            )
        if self.config.scenario == FakeGeminiScenario.EMPTY_RESPONSE:
            raise LLMEmptyResponseError(
                "Fake Gemini empty response", details={"attempt_id": attempt_id}
            )
        if self.config.scenario == FakeGeminiScenario.MALFORMED:
            raise LLMMalformedResponseError(
                "Fake Gemini malformed response", details={"attempt_id": attempt_id}
            )
        if self.config.scenario == FakeGeminiScenario.STALE_SOURCE:
            raise LLMStaleSourceError(
                "Fake Gemini stale source", details={"attempt_id": attempt_id}
            )

    def _next_attempt(self, analysis_run_id: str) -> tuple[str, int]:
        count = self._analyze_counts.get(analysis_run_id, 0) + 1
        self._analyze_counts[analysis_run_id] = count
        return f"{analysis_run_id}-attempt-{count:02d}", count - 1

    async def check_budget(self, request: BudgetEvaluationRequest) -> AiBudgetDecision:
        return AiBudgetDecision(
            allowed=True,
            reason="Budget available",
            remaining_requests=100,
            remaining_tokens=10000,
            remaining_cost=Decimal("5.00"),
        )

    async def analyze(self, request: AnalysisRequest) -> ProviderAnalysisResponse:
        attempt_id, retry_count = self._next_attempt(request.analysis_run_id)
        self._check_scenario(attempt_id)

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
                    retry_count=retry_count,
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
                    retry_count=retry_count,
                ),
                candidate=candidate,
            )

        attempt = ProviderAttemptResult(
            attempt_id=attempt_id,
            provider_code="fake-gemini",
            configured_model="fake-model",
            outcome={
                FakeGeminiScenario.TIMEOUT: ProviderOutcome.TIMEOUT,
                FakeGeminiScenario.RATE_LIMIT: ProviderOutcome.RATE_LIMITED,
                FakeGeminiScenario.REFUSAL: ProviderOutcome.REFUSAL,
                FakeGeminiScenario.SAFETY_BLOCK: ProviderOutcome.SAFETY_BLOCKED,
                FakeGeminiScenario.EMPTY_RESPONSE: ProviderOutcome.EMPTY_CANDIDATE,
                FakeGeminiScenario.MALFORMED: ProviderOutcome.MALFORMED_RESPONSE,
                FakeGeminiScenario.STALE_SOURCE: ProviderOutcome.SUCCESS,
            }[self.config.scenario],
            error_message="Fake error",
            latency_ms=self.config.latency_ms,
            retry_count=retry_count,
        )
        return ProviderAnalysisResponse(attempt=attempt)
