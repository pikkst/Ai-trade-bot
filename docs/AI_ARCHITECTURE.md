# AI Architecture

Last reviewed: 2026-07-31

AI interprets structured evidence and produces explainable research. It has no order-execution authority and cannot modify strategy or risk policy.

## Provider Boundary

All providers implement a common `LLMProvider` protocol with typed request, response, usage, timeout, cancellation, and error contracts.

Supported paths:

- OpenAI Responses API for new cloud integration work
- Ollama for local development
- vLLM for future local high-throughput serving
- Deterministic fake provider for CI and tests

Provider SDK objects must not leak into domain code.

## OpenAI Integration Rules

- Use the Responses API for new work.
- Prefer strict JSON Schema Structured Outputs where the configured model supports them.
- Use pinned model identifiers or snapshots for reproducible experiments.
- Generate a unique client request ID and retain provider response IDs.
- Record model, prompt version, schema version, latency, token usage, cost estimate, status, and retry count.
- Use `store=false` unless a documented requirement explicitly needs provider-side storage.
- Do not grant web, code execution, exchange, database mutation, or other side-effect tools to the market-analysis model in the MVP.

## Input Contract

- Immutable market snapshot ID
- Exchange and normalized symbol
- Candle interval and analysis timestamp
- Feature-set version and typed indicator values
- Market-regime features
- Data-quality status and freshness
- Optional trusted summaries with source references
- Prompt version
- Output schema version
- Provider and pinned model configuration

Untrusted news or social text must be placed in explicit data fields and surrounded by instructions that it is evidence, not executable guidance.

## Output Contract

```json
{
  "schema_version": "1.0",
  "market_regime": "bullish",
  "recommended_action": "hold",
  "confidence": 0.7,
  "evidence": [
    {
      "feature": "ema_50_above_ema_200",
      "observation": "true",
      "impact": "supports_bullish_regime"
    }
  ],
  "contradictions": [],
  "risks": [],
  "missing_information": [],
  "invalidation_conditions": [],
  "summary": "The long-term trend is positive, but no entry is recommended under the current deterministic strategy."
}
```

`confidence` is confidence in the analytical classification, not probability of profit.

## Validation Pipeline

1. Confirm provider request completed successfully.
2. Parse structured output.
3. Validate against the exact JSON Schema version.
4. Reject unknown fields when strict mode is required.
5. Validate ranges, enums, lengths, and references.
6. Verify cited evidence exists in the supplied snapshot.
7. Detect unsupported factual claims.
8. Apply policy checks.
9. Persist raw response, validated report, lineage, usage, and validation result.
10. Publish a typed analysis-completed or analysis-rejected event.

## Failure Behavior

- Timeout: bounded retry, then deterministic fallback or HOLD.
- Refusal: persist status and use deterministic fallback or HOLD.
- Invalid schema: reject; do not auto-trade.
- Unsupported claim: reject or lower trust according to policy.
- Stale source snapshot: reject.
- Provider outage: continue deterministic features and block AI-dependent entries.
- Budget exhausted: disable optional AI calls and continue safe deterministic operation.

## Evaluation

Every prompt and model candidate must be evaluated against a versioned dataset for:

- Schema success rate
- Evidence grounding
- Unsupported claim rate
- Action consistency
- Sensitivity to irrelevant or malicious text
- Latency
- Token use and cost
- Stability across repeated runs

A prompt or model change is a versioned behavior change and must not silently alter an active experiment.

## Safety Invariants

- No execution tools
- No secrets in prompts
- No direct database mutation
- No position sizing authority
- No risk-policy modification
- Prompt injection treated as untrusted content
- Malformed or stale output fails closed
- Complete decision lineage is mandatory