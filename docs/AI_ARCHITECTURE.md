# AI Architecture

Last reviewed: 2026-07-31

AI interprets structured evidence and produces explainable research. It has no order-execution authority and cannot modify strategy or risk policy.

## Provider Boundary

All providers implement a common `LLMProvider` protocol with typed request, response, usage, timeout, cancellation, safety, and error contracts.

Version 1 providers:

- Google Gemini API as the required cloud provider
- Deterministic fake provider for CI and tests

Future local providers such as Ollama or vLLM require an ADR. Provider SDK objects must not leak into domain code.

## Gemini Integration Rules

The authoritative provider-specific specification is [GEMINI_INTEGRATION.md](GEMINI_INTEGRATION.md).

- Use the official `google-genai` Python SDK.
- Use structured output with a project-owned JSON Schema or Pydantic model where supported by the selected stable model.
- Configure the model through environment and experiment configuration; do not hardcode it in domain logic.
- Persist provider request metadata, model identifier, prompt version, schema version, safety outcome, latency, token usage, estimated cost, status, and retry count.
- Apply explicit timeout, retry, rate-limit, and budget policies.
- Do not grant web search, code execution, exchange, database mutation, shell, or order-execution tools to the market-analysis model in the MVP.
- Do not use preview models for production-facing deployments unless current Google documentation and terms explicitly allow it.

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
- Provider and model configuration version

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

1. Confirm the provider request completed successfully.
2. Classify timeout, rate limit, provider error, refusal, safety block, or empty response.
3. Parse structured output.
4. Validate against the exact JSON Schema version.
5. Reject unknown fields when strict mode is required.
6. Validate ranges, enums, lengths, and references.
7. Verify cited evidence exists in the supplied snapshot.
8. Detect unsupported factual claims.
9. Apply application policy checks.
10. Persist raw provider metadata, validated report, lineage, usage, safety result, and validation result.
11. Publish a typed analysis-completed or analysis-rejected event.

## Failure Behavior

- Timeout: bounded retry with jitter, then deterministic fallback or HOLD.
- Rate limit: bounded retry, budget accounting, then deterministic fallback or HOLD.
- Safety block or refusal: persist status and use deterministic fallback or HOLD.
- Invalid schema: reject; do not auto-trade.
- Unsupported claim: reject or lower trust according to policy.
- Stale source snapshot: reject.
- Provider outage: continue deterministic features and block AI-dependent entries.
- Budget exhausted: disable optional AI calls and continue safe deterministic operation.

## Evaluation

Every prompt and model candidate must be evaluated against a versioned dataset for:

- schema success rate;
- evidence grounding;
- unsupported claim rate;
- action consistency;
- sensitivity to irrelevant or malicious text;
- safety-block behavior;
- latency;
- token use and cost;
- stability across repeated runs.

A prompt, schema, safety-setting, or model change is a versioned behavior change and must not silently alter an active experiment.

## Safety Invariants

- No execution tools
- No secrets in prompts
- No direct database mutation
- No position-sizing authority
- No risk-policy modification
- Prompt injection treated as untrusted content
- Malformed, blocked, or stale output fails closed
- Complete decision lineage is mandatory
