# Google Gemini API Integration

Last reviewed: 2026-08-01  
Status: Authoritative M009 Gemini provider, validation, budget, evaluation, and fallback contract

## 1. Purpose

Google Gemini is the required cloud AI provider for the first product profile. It transforms approved structured market evidence into a bounded advisory research report.

Gemini is probabilistic and non-authoritative. It cannot:

- access secrets, personal data, database URLs, or exchange credentials;
- call exchange, database, shell, code, filesystem, search, deployment, or workflow tools;
- place or cancel orders;
- choose final position size;
- change strategy, risk, execution, accounting, experiments, releases, or configuration;
- approve research, releases, or behavior changes;
- enable private Binance or live trading.

Deterministic application validation, strategy, risk, paper execution, accounting, reconciliation, incidents, and human approvals remain authoritative.

## 2. Master-Task Ownership

| Capability | Master Tasks |
|---|---|
| provider protocol and deterministic fake | M006 |
| Gemini transport, prompts, schemas, validation, budgets, fallback | M009 |
| API and analysis workspace | M014, M018 |
| cycle/backtest integration | M012–M013, M022 |
| integrated/evaluation tests | M026 |
| cloud experiment | M028–M029 |
| performance/cost, research review, and behavior changes | M030, M032, M034 |

## 3. Official SDK and Adapter Boundary

Use the official Google Gen AI Python SDK:

```python
from google import genai
from google.genai import types
```

SDK-specific objects remain inside `backend/app/infrastructure/ai/gemini/`.

Domain/application code depends on project-owned protocols and models such as:

- `LLMProvider`;
- `AnalysisRequest`;
- `ProviderAttemptResult`;
- `ValidatedAiReport`;
- `AiUsage`;
- `AiBudgetDecision`;
- `DeterministicFallbackResult`.

Provider/model/SDK changes are material behavior changes and follow M034.

## 4. Authentication and Secret Handling

- read the API key from protected server/workflow environment configuration;
- never commit, return, log, trace, screenshot, export, or place it in a browser bundle;
- use separate provider projects/keys for local smoke, cloud experiment, staging, and production research;
- normal local/CI uses the deterministic fake provider and requires no paid credential;
- protected smoke calls never run for untrusted fork code;
- rotate/revoke after suspected exposure and verify dependent services;
- store secret metadata only, never value or usable digest, in ordinary database tables;
- keep `ALLOW_PAID_PROVIDER_USAGE=false` and automatic provider upgrade disabled unless an explicit versioned owner-approved policy changes it.

## 5. Provider Configuration Versions

Provider configuration is immutable after use and includes:

- provider code;
- configured model identifier;
- adapter version;
- environment/service tier classification;
- timeout;
- retry/backoff policy;
- maximum output tokens;
- temperature and approved generation settings;
- structured-output configuration;
- safety-settings version;
- budget-policy reference;
- data-handling/region/terms evidence reference;
- activation/archive state;
- canonical configuration hash.

The UI may report only the configured model and persisted provider-returned metadata. It must not claim an unverifiable underlying serving implementation.

Preview/deprecated models are blocked unless current provider terms/status and M034 approval explicitly permit the target environment.

## 6. Request Eligibility

Before constructing a request, the application verifies:

- exact workspace/experiment configuration and behavior set;
- source snapshot identity/hash;
- source candles finalized;
- quality and freshness approved;
- feature calculation identity/hash/version;
- prompt/schema/safety/validation/provider versions compatible;
- allowed evidence IDs and bounded values;
- budget reservation available;
- provider enabled for the environment;
- no active policy/halt/incident blocker;
- no secret or prohibited data class in the payload.

Failure creates typed rejection/fallback evidence and no provider call where appropriate.

## 7. Minimum Structured Request Contract

Every logical request contains only approved necessary evidence:

- immutable market snapshot ID/hash;
- exchange, normalized symbol, interval, and analysis time;
- latest finalized candle time;
- freshness/quality outcome and policy version;
- feature calculation ID/hash;
- versioned typed deterministic feature values and units;
- allowed evidence IDs;
- optional trusted summary references with source IDs;
- prompt version;
- report-schema version;
- safety/validation/provider configuration versions;
- logical request/idempotency/correlation identifiers.

Prohibited request data:

- API keys, JWTs, cookies, authorization headers, database URLs, connection strings, service-role credentials, private exchange data;
- unrelated user or personal data;
- arbitrary browser prompts;
- unrestricted internal logs, audit records, provider responses, or licensed content;
- executable instructions from external/untrusted evidence.

## 8. Prompt Layering

Requests preserve four layers:

1. trusted versioned system instruction;
2. trusted versioned task instruction;
3. structured evidence envelope;
4. exact project-owned output contract.

Untrusted text is data inside explicit bounded fields and cannot select tools, models, schemas, policies, credentials, or actions.

Prompt versions are immutable after use and include system/task/evidence/schema/fallback/confidence/language hashes and evaluation references.

The system does not let Gemini rewrite its own prompt or repair reports indefinitely.

## 9. Structured Output Contract

Baseline report shape:

```json
{
  "schema_version": "1.0",
  "market_regime": "bullish|bearish|sideways|uncertain",
  "recommended_action": "hold|enter|exit|reduce",
  "confidence": "0.70",
  "evidence": [],
  "contradictions": [],
  "risks": [],
  "missing_information": [],
  "invalidation_conditions": [],
  "summary": ""
}
```

Rules:

- project-owned JSON Schema/Pydantic model is authoritative;
- unknown fields are rejected under strict policy;
- collections, strings, numeric ranges, and payload size are bounded;
- evidence references must match allowed supplied IDs;
- `confidence` is analytical classification confidence, not probability of profit, expected return, position-size multiplier, or advice strength;
- provider-side structured output does not replace application validation;
- no report field directly authorizes execution.

Exact schema versions live in source/registry and require compatibility/version review.

## 10. Request and Attempt Identity

Persist:

- analysis-run ID;
- deterministic logical request/idempotency key;
- shared logical request ID;
- unique attempt ID and sequence;
- provider and configured model;
- source snapshot/features;
- prompt/schema/safety/validation/provider versions;
- request hash over the approved redacted canonical envelope;
- timeout/retry settings;
- start/end/latency;
- provider request/response IDs where safe;
- attempt outcome;
- usage/cost estimate;
- retry eligibility and trigger;
- safe diagnostics.

Retries never create duplicate accepted reports, budget commitments, decisions, or downstream side effects.

## 11. Provider Outcome Taxonomy

Canonical outcomes include:

- success;
- timeout;
- cancelled;
- rate limited;
- transient provider failure;
- permanent provider failure;
- authentication failure;
- invalid request;
- refusal;
- safety blocked;
- empty candidate;
- malformed/oversized/invalidly encoded response;
- budget blocked;
- configuration unavailable;
- provider disabled;
- terms/region/model status blocked.

Every outcome maps to stable safe code, retry eligibility, fallback behavior, audit/metric classification, and user-facing limitation.

Provider success is not report acceptance.

## 12. Retry Policy

- retry only approved transient outcomes such as selected 429/5xx/transport failures;
- use bounded exponential backoff with jitter;
- honor valid provider retry guidance;
- share logical identity and create unique attempt identities;
- cap attempts, duration, cumulative usage, and cost;
- support cancellation and workflow timeout;
- do not retry authentication, invalid request, refusal, safety block, budget block, parsing, schema, grounding, unsupported-claim, injection, stale-source, or application-policy failures as transient;
- do not recursively ask Gemini to repair itself;
- terminal failure invokes the exact frozen fallback policy.

## 13. Parsing and Validation Pipeline

The application performs:

1. classify provider attempt outcome;
2. verify candidate/content existence;
3. enforce response-size/encoding/control-character/duplicate-key policy;
4. parse exact root JSON/structured representation;
5. validate exact schema version;
6. reject unknown fields according to policy;
7. validate required fields, enums, ranges, precision, lengths, and collection bounds;
8. verify each evidence reference exists in the supplied envelope;
9. compare observation/value/unit/timestamp against source evidence;
10. detect unsupported factual claims;
11. detect false certainty, future-price, expected-return, profit-probability, and personal-suitability claims;
12. detect prompt-injection following or instruction/evidence boundary violation;
13. re-verify source freshness, quality, invalidation, and compatibility;
14. apply application policy checks;
15. persist immutable checks and accepted/rejected outcome;
16. persist typed report only on acceptance;
17. publish typed completion/rejection evidence;
18. invoke deterministic fallback/HOLD when required.

Missing required checks fail closed.

## 14. Evidence Grounding

Accepted evidence statements include:

- allowed evidence ID;
- source feature/snapshot name;
- typed source value and unit;
- source timestamp/version/hash;
- model observation and claimed impact;
- grounding validator/version/outcome.

Reports may use only:

- supplied deterministic features;
- supplied snapshot metadata;
- explicitly approved trusted summaries and source IDs;
- relationships inferable from those inputs under the schema/policy.

Unsupported references or material unsupported claims reject the report under strict policy.

## 15. Unsupported-Claim and False-Certainty Policy

Prohibited without exact supplied evidence and an approved schema/use case:

- current news/social/on-chain/whale activity;
- hidden exchange activity;
- exact future price;
- expected return or probability of profit;
- guaranteed safety or profitability;
- personal investment suitability;
- fabricated indicator, source, event, or market fact;
- claim that a provider/model controls orders, risk, or experiment state;
- suppression of contradictory or missing evidence.

User-facing narrative must preserve contradictions, risks, missing information, invalidation conditions, and limitations.

## 16. Prompt-Injection Defense

Evaluation and validation cover:

- direct commands inside evidence;
- encoded/obfuscated/nested commands;
- fake system/developer messages;
- requests for secrets or provider internals;
- schema/validation bypass;
- requests to call tools, place orders, change risk, enable live trading, suppress contradictions, or alter configuration;
- malicious HTML, Markdown, JSON, Unicode control/bidirectional characters;
- requests to invent missing data or cite external sources.

Evidence is treated as data, rendered safely, and never gains instruction authority.

A report that follows injected instructions is rejected.

## 17. Deterministic Fallback

Fallback is a versioned application/domain policy, not Gemini-generated text.

Possible outcomes:

- deterministic features/strategy continue without AI evidence;
- AI-dependent entry is blocked;
- advisory result becomes HOLD with exact reason codes;
- provider is temporarily disabled according to circuit/budget policy;
- incident/warning is created for repeated or critical failure.

Persist:

- trigger;
- fallback policy/version;
- eligible/selected result;
- downstream strategy/risk behavior;
- reason codes;
- cycle/backtest references;
- limitations.

Fallback never weakens deterministic risk or creates an order directly.

## 18. Budget and Cost Enforcement

Versioned budget policy may define:

- request count;
- input/output token limits;
- daily/period totals;
- estimated monetary cost;
- environment/workspace/provider scope;
- warning/stop thresholds;
- reset semantics;
- reservation/commit/release behavior;
- fallback outcome.

Requirements:

- reserve/check before a provider call;
- transaction-safe concurrent accounting;
- attempts/retries consume attributable usage;
- estimated cost is labeled as estimate unless provider-billed evidence exists;
- default formal-experiment monthly cost budget is EUR 0 unless explicitly versioned and owner-approved;
- exhaustion blocks optional calls and degrades safely;
- no automatic provider purchase, plan upgrade, scaling, or budget increase;
- current pricing/quotas/terms use timestamped approved evidence, not frozen prose.

## 19. Data Handling and Retention

Persist only required reproducibility/audit evidence:

- provider/configured model and adapter versions;
- logical request and attempts;
- prompt/schema/safety/validation versions;
- source evidence references/hashes;
- provider outcome and safe metadata;
- accepted structured report/hash;
- validation checks;
- usage, latency, retry, cost estimate;
- fallback and downstream lineage.

Raw request/response content:

- is not exposed by default;
- is never the source of truth for accepted report fields;
- is minimized, protected, classified, and retention-bounded;
- may be disabled by configuration;
- cannot contain secrets/personal data by design;
- follows holds, incident evidence, archive, deletion/anonymization, and provider-term policy.

Review current Gemini API terms, region/service-tier eligibility, data handling, model status, quota, and pricing before M028/M029/M035/M036 or a material model change. Engineering documentation is not legal advice.

## 20. Gemini in Backtests

Allowed modes:

- `disabled`;
- `precomputed` exact immutable accepted reports mapped to exact historical snapshots and versions;
- `sampled_research` in a separately labeled non-baseline experiment with provider drift/cost limitations.

Ordinary deterministic backtests must not make silent live Gemini calls.

A run cannot mix model/prompt/schema/validation versions silently. Missing/incompatible precomputed reports follow exact policy and do not fabricate analysis.

## 21. Evaluations and Activation

Every provider/model/prompt/schema/safety/validation/fallback candidate is evaluated on a versioned dataset for:

- provider and structured-output success separately;
- schema acceptance;
- evidence grounding;
- unsupported claim and false certainty;
- prompt-injection resistance;
- refusal/safety behavior;
- timeout/rate-limit/failure/fallback behavior;
- repeated-run stability;
- action consistency;
- latency, token use, and estimated/billed cost;
- source coverage and limitations;
- backward/historical compatibility.

Activation process:

1. create immutable candidate behavior set;
2. define and approve evidence plan before final staged evaluation;
3. run deterministic fixtures and approved provider smoke/evaluation;
4. compare against baseline without hiding unfavorable cases;
5. complete security/privacy/cost/compatibility review;
6. approve staged paper rollout against immutable snapshot;
7. observe bounded paper canary and stop conditions;
8. owner may approve only future paper configurations;
9. preserve rollback/deprecation/archival evidence.

Tests, scores, AI, CI, or provider changes cannot auto-activate behavior. Running experiments remain frozen.

## 22. Observability

Track with bounded labels and durable evidence:

- logical requests and attempts by provider/model/configuration/outcome;
- provider latency and validation latency separately;
- retry/rate-limit/timeout/auth/refusal/safety/empty/malformed counts;
- parsing/schema/grounding/unsupported/injection/source-policy check outcomes;
- accepted-report rate versus provider-success rate;
- usage and cost estimates/billed classification;
- budget reservation/commit/exhaustion;
- fallback/HOLD and downstream-consumption outcomes;
- evaluation versions/results;
- data handling/retention state;
- incidents or behavior-change references.

Logs never contain keys, raw prompts, unrestricted responses, personal data, or unbounded provider text. Profit is not an AI SLI/SLO.

## 23. Testing

Required tests:

- deterministic fake provider;
- request eligibility/minimum-data construction;
- no-secret/personal-data envelope;
- configured-model/provider metadata;
- timeout, cancellation, authentication, 429, retryable 5xx, permanent failure;
- refusal, safety block, empty candidate, malformed/oversized/encoding/duplicate-key response;
- exact schema parsing and unknown fields;
- enum/range/precision/length/collection bounds;
- evidence grounding and unknown/mismatched references;
- unsupported claims and false certainty;
- injection corpus and safe rendering;
- stale/invalid/invalidated/incompatible source;
- budget reservation, concurrency, exhaustion, reset, and no-auto-upgrade;
- bounded retry/idempotency/cumulative usage;
- deterministic fallback/HOLD and no downstream order bypass;
- precomputed backtest compatibility;
- repeated-run/evaluation comparison;
- retention/redaction/RLS/API authorization;
- behavior-set freeze and M034 approval invalidation.

Protected real-provider smoke tests use a dedicated non-production project, bounded budget, and trusted code only.

## 24. Completion Gate

M009 is verified only when:

- provider protocol/fake and Gemini adapter are implemented;
- prompts/schemas/safety/validation/fallback/budgets are immutable and project-owned;
- all provider and validation failure paths are typed/tested;
- invalid AI cannot reach strategy as accepted evidence;
- deterministic strategy/risk remain authoritative;
- usage/cost/retention/audit evidence exists;
- no tool or execution authority exists;
- API/schema/workspace/docs/tests are synchronized;
- final commit is fetched and inspected.

## 25. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `AI_ARCHITECTURE.md`
- `AI_PROMPTS.md`
- `MARKET_DATA.md`
- `STRATEGY_ENGINE.md`
- `API_SPECIFICATION.md`
- `DATABASE_SCHEMA.md`
- `GEMINI_ANALYSIS_VALIDATION_WORKSPACE_IMPLEMENTATION.md`
- `SECURITY.md`
- `OBSERVABILITY.md`
- `TESTING.md`
