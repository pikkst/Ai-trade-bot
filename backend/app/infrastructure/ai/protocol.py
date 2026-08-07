"""Project-owned LLM provider protocol, models, and errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Protocol

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


JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


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
    payload: dict[str, JsonValue]
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


class FreshnessPolicy(str, Enum):
    ACCEPTED = "accepted"
    DEGRADED = "degraded"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class FreshnessQualityOutcome:
    policy_version: str
    outcome: FreshnessPolicy
    latest_candle_time: datetime | None = None
    max_age_minutes: int = 0
    gap_count: int = 0
    notes: str = ""


@dataclass(frozen=True, slots=True)
class FeatureCalculationReference:
    calculation_id: str
    calculation_hash: str
    calculation_version: str
    feature_set_hash: str


@dataclass(frozen=True, slots=True)
class FeatureValue:
    value: JsonValue
    unit: str = ""
    version: str = "1.0"


@dataclass(frozen=True, slots=True)
class TrustedSummaryReference:
    source_id: str
    summary_type: str
    reference: str


@dataclass(frozen=True, slots=True)
class BudgetEvaluationRequest:
    analysis_run_id: str
    snapshot_id: str
    snapshot_hash: str
    exchange: str
    symbol: str
    interval: str
    feature_calculation: FeatureCalculationReference
    prompt_version: str
    schema_version: str
    safety_version: str
    validation_version: str
    provider_config_version: str
    logical_request_id: str
    idempotency_key: str
    context: ExecutionContext


@dataclass(frozen=True, slots=True)
class AnalysisRequest:
    analysis_run_id: str
    snapshot_id: str
    snapshot_hash: str
    exchange: str
    symbol: str
    interval: str
    analysis_time: datetime
    context: ExecutionContext
    latest_candle_time: datetime
    freshness_quality: FreshnessQualityOutcome
    feature_calculation: FeatureCalculationReference
    logical_request_id: str
    idempotency_key: str
    allowed_evidence_ids: list[str] = field(default_factory=list)
    prompt_version: str = "1.0"
    schema_version: str = "1.0"
    safety_version: str = "1.0"
    validation_version: str = "1.0"
    provider_config_version: str = "1.0"
    features: dict[str, FeatureValue] = field(default_factory=dict)
    trusted_summary_references: list[TrustedSummaryReference] = field(
        default_factory=list
    )
    budget_decision: AiBudgetDecision | None = None


class LLMProvider(Protocol):
    async def analyze(self, request: AnalysisRequest) -> ProviderAnalysisResponse: ...

    async def check_budget(
        self, request: BudgetEvaluationRequest
    ) -> AiBudgetDecision: ...


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
