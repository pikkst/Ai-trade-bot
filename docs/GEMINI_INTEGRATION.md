# Google Gemini API Integration

Last reviewed: 2026-07-31

## Purpose

This document is the authoritative specification for cloud AI integration in the MVP. Google Gemini API is the primary and only required cloud LLM provider for version 1. Local providers may be added later behind the same provider boundary, but they are not required for the MVP.

## Official SDK

Use the current Google Gen AI Python SDK:

```python
from google import genai
from google.genai import types
```

The implementation must isolate SDK-specific objects inside `backend/app/infrastructure/ai/gemini/`. Domain and application layers depend only on the project-owned `LLMProvider` protocol and typed project models.

## Authentication

- Read the API key from `GEMINI_API_KEY`.
- Never commit or log the key.
- Never return the key through an API response.
- Use separate Google Cloud or AI Studio projects and keys for local, CI, sandbox, and future production environments.
- CI uses a deterministic fake provider by default and must not require a paid Gemini request.
- Rotate a key immediately if exposure is suspected.

## Model Configuration

Models are configuration, not source-code constants.

Required settings:

- `GEMINI_MODEL`
- `GEMINI_API_KEY`
- `GEMINI_REQUEST_TIMEOUT_SECONDS`
- `GEMINI_MAX_RETRIES`
- `GEMINI_MAX_OUTPUT_TOKENS`
- `GEMINI_TEMPERATURE`
- `GEMINI_DAILY_REQUEST_BUDGET`
- `GEMINI_DAILY_TOKEN_BUDGET`
- `GEMINI_MONTHLY_COST_BUDGET_EUR`

A model change creates a new experiment configuration version. Preview models must not be used for a production-facing service unless the current Google terms and model status explicitly permit it.

## Request Contract

Every request contains only the minimum required structured evidence:

- immutable market snapshot identifier;
- exchange and normalized symbol;
- finalized candle interval and analysis timestamp;
- versioned deterministic indicators;
- market-data quality and freshness status;
- versioned system instruction;
- versioned user prompt template;
- output schema version;
- correlation and request identifiers.

Exchange credentials, user secrets, database URLs, authorization tokens, and unrelated personal data must never be included.

## Structured Output

Gemini responses must use structured output with a project-owned JSON Schema or Pydantic model whenever supported by the selected stable model.

Required report fields:

```json
{
  "schema_version": "1.0",
  "market_regime": "bullish|bearish|sideways|uncertain",
  "recommended_action": "hold|enter|exit|reduce",
  "confidence": 0.0,
  "evidence": [],
  "contradictions": [],
  "risks": [],
  "missing_information": [],
  "invalidation_conditions": [],
  "summary": ""
}
```

`confidence` describes confidence in the analytical classification. It must never be displayed or interpreted as probability of profit.

## Generation Rules

- Temperature defaults to `0.1` for analytical consistency.
- Output token limits are configured and enforced.
- The model receives no exchange, database, shell, code-execution, or order-execution tools.
- Function calling is disabled for the MVP analysis flow unless a separate ADR and owner approval define a read-only tool.
- Google Search grounding is disabled for the first technical-analysis MVP. If news analysis is later enabled, grounding must have a dedicated specification, source-citation storage, cost controls, and prompt-injection tests.
- Safety settings must be explicit, versioned, and tested. Do not disable built-in protections merely to avoid handling blocked responses.

## Response Validation

The adapter must:

1. capture provider request metadata;
2. call Gemini with a bounded timeout;
3. distinguish success, timeout, rate limit, provider failure, refusal, safety block, empty candidate, and schema failure;
4. validate the response against the exact schema version;
5. reject unknown or unsupported values;
6. verify each evidence reference exists in the supplied snapshot;
7. persist raw provider metadata and the validated project model separately;
8. publish either a typed success or typed rejection event.

No malformed, blocked, stale, ungrounded, or partially validated response may reach the strategy or risk engine as an approved AI report.

## Retry and Rate-Limit Policy

- Retry only transient failures such as 429 and selected 5xx responses.
- Use exponential backoff with jitter.
- Honor provider retry information where available.
- Do not retry validation errors, safety blocks, invalid requests, or authentication failures.
- Retries must remain idempotent and retain a shared logical request ID plus unique attempt IDs.
- When budgets or retry limits are exhausted, the system degrades to deterministic analysis and `HOLD` for AI-dependent decisions.

## Data Handling and Retention

- Review current Gemini API terms before each production release.
- Store only data required for reproducibility and audit.
- Persist model identifier, request ID, response metadata, prompt version, schema version, token usage, latency, retry count, safety outcome, and estimated cost.
- Do not assume provider-side zero retention. Document the selected service tier and current data-handling terms in the release checklist.
- Users in the EEA require a paid service configuration before the API client is offered to users, according to the current Gemini API terms.

## Safety and Factuality

Gemini output is probabilistic and may be inaccurate. The application must use deterministic post-processing, schema validation, evidence verification, automated evaluation, and human review during the initial experiment.

Untrusted news, social posts, and retrieved text are always data, never instructions. Prompt injection tests must cover attempts to:

- override the system instruction;
- request secrets;
- change risk settings;
- create an order;
- enable live trading;
- fabricate missing indicators;
- suppress contradictory evidence.

## Observability

Required metrics:

- request count by model and outcome;
- latency histogram;
- rate-limit count;
- timeout count;
- safety-block count;
- structured-output validation failure count;
- input and output token totals;
- estimated cost;
- daily and monthly budget utilization.

Logs must use correlation IDs and redact prompt data that could contain sensitive or licensed content.

## Testing

Required tests:

- deterministic fake-provider unit tests;
- Gemini adapter request-construction tests;
- structured-output parsing tests;
- timeout and cancellation tests;
- 429 and 5xx retry tests;
- authentication failure tests;
- safety-block and empty-response tests;
- malformed and unsupported schema tests;
- prompt-injection evaluation cases;
- budget-exhaustion tests;
- contract smoke test against a dedicated non-production Gemini project, excluded from normal CI.

## Definition of Done

Gemini integration is complete only when the provider adapter, fake provider, schemas, prompts, budget controls, audit storage, metrics, documentation, and all required tests exist and no model response can bypass deterministic strategy and risk validation.