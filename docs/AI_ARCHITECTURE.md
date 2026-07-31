# AI Architecture

AI interprets structured evidence and produces explainable research. It has no execution authority.

## Providers
OpenAI-compatible API, Ollama, vLLM, and fake test provider behind an `LLMProvider` interface.

## Input
Snapshot ID, symbol, interval, indicators, regime features, data quality, optional trusted summaries, prompt version, schema version.

## Output
```json
{
  "schema_version": "1.0",
  "market_regime": "bullish",
  "recommended_action": "hold",
  "confidence": 0.70,
  "evidence": [],
  "contradictions": [],
  "risks": [],
  "missing_information": [],
  "summary": ""
}
```

## Validation
JSON extraction, schema validation, range validation, reference validation, policy validation, persistence.

## Safety
No execution tools, no secrets in prompts, prompt injection treated as data, fail closed on malformed output, cost budgets, and full lineage.
