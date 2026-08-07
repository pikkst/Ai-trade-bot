"""Project-owned LLM provider protocol, models, and errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from app.request_context import ExecutionContext


class ProviderOutcome(str, Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    RATE_LIMITED = "rate_limited"
    TRANSIENT_FAILURE = "transient_failure"
    PERMANENT_FAILURE = "permanent_failure"
    AUTHENTICATION_FAILURE = "authentication_failure"
    INVALID_REQUEST = "invalid_request"
    REFUSAL = "refusal"
    SAFETY_BLOCKED = "safety_blocked"
    EMPTY_CANDIDATE = "empty_candidate"
    MALFORMED_RESPONSE = "malformed_response"
    BUDGET_BLOCKED = "budget_blocked"
    CONFIGURATION_UNAVAILABLE = "configuration_unavailable"
    PROVIDER_DISABLED = "provider_disabled"
    TERMS_BLOCKED = "terms_blocked"


class SafetySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class AiUsage:
    prompt_tokens: int = 0
    response_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: Decimal = Decimal("0.00")
    currency: str = "USD"


@dataclass(frozen=True, slots=True)
class ProviderAttemptResult:
    attempt_id: str
    provider_code: str
    configured_model: str
    outcome: ProviderOutcome
    usage: AiUsage | None = None
    safety_status: SafetySeverity | None = None
    raw_response_reference: str | None = None
    error_message: str | None = None
    latency_ms: int | None = None
    retry_count: int = 0


@dataclass(frozen=True, slots=True)
class ProviderCandidate:
    candidate_id: str
    schema_version: str
    payload: dict[str, Any]
    provider_code: str
    configured_model: str
    raw_response_reference: str | None = None


@dataclass(frozen=True, slots=True)
class ProviderAnalysisResponse:
    attempt: ProviderAttemptResult
    candidate: ProviderCandidate | None = None


@dataclass(frozen=True, slots=True)
class AiBudgetDecision:
    allowed: bool
    reason: str
    remaining_requests: int = 0
    remaining_tokens: int = 0
    remaining_cost: Decimal = Decimal("0.00")


class ValidatedAiReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str
    market_regime: str
    recommended_action: str
    confidence: Decimal
    evidence: list[dict[str, Any]]
    contradictions: list[str]
    risks: list[str]
    missing_information: list[str]
    invalidation_conditions: list[str]
    summary: str


class DeterministicFallbackResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: str = "1.0"
    market_regime: str = "uncertain"
    recommended_action: str = "hold"
    confidence: Decimal = Decimal("0.0")
    evidence: list[dict[str, Any]] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=lambda: ["ai_provider_unavailable"])
    missing_information: list[str] = field(
        default_factory=lambda: ["ai_analysis_unavailable"]
    )
    invalidation_conditions: list[str] = field(default_factory=list)
    summary: str = "Deterministic fallback: AI analysis is unavailable."


@dataclass(frozen=True, slots=True)
class AnalysisRequest:
    analysis_run_id: str
    snapshot_id: str
    snapshot_hash: str
    symbol: str
    interval: str
    analysis_time: datetime
    features: dict[str, Any]
    prompt_version: str
    schema_version: str
    provider_config_version: str
    budget_decision: AiBudgetDecision
    context: ExecutionContext


class LLMProvider(Protocol):
    async def analyze(self, request: AnalysisRequest) -> ProviderAnalysisResponse: ...

    async def check_budget(self, request: AnalysisRequest) -> AiBudgetDecision: ...


class LLMProviderError(Exception):
    code = "llm_provider_error"

    def __init__(
        self, message: str, *, details: dict[str, object] | None = None
    ) -> None:
        super().__init__(message)
        self.details = details


class LLMTimeoutError(LLMProviderError):
    code = "llm_timeout"


class LLMRateLimitError(LLMProviderError):
    code = "llm_rate_limit"


class LLMRefusalError(LLMProviderError):
    code = "llm_refusal"


class LLMSafetyBlockError(LLMProviderError):
    code = "llm_safety_blocked"


class LLMMalformedResponseError(LLMProviderError):
    code = "llm_malformed_response"


class LLMEmptyResponseError(LLMProviderError):
    code = "llm_empty_response"


class LLMStaleSourceError(LLMProviderError):
    code = "llm_stale_source"


class LLMBudgetExhaustedError(LLMProviderError):
    code = "llm_budget_exhausted"
