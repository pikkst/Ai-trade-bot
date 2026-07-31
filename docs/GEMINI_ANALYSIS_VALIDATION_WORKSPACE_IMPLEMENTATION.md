# Gemini Analysis, Validation, Evidence, and Research Narrative Workspace Implementation Specification

Last reviewed: 2026-07-31  
Status: Sprint 11 authoritative Gemini analysis and validation workspace specification

## 1. Purpose

This document defines the implementation contract for the Gemini Analysis, Validation, Evidence, and Research Narrative Workspace of The Daily Roast AI.

The workspace explains which immutable market evidence was sent to the configured Google Gemini model, which prompt, schema, safety, and provider configuration versions governed the request, what provider outcome occurred, whether the structured response passed every application validation gate, which evidence supports or contradicts the report, what uncertainty and missing information remain, how budgets and retries were consumed, and how the validated advisory report relates to later deterministic strategy and risk decisions.

Gemini remains advisory. The workspace must never imply that an AI report is an order, risk approval, probability of profit, guaranteed outcome, or autonomous trading authority.

## 2. Scope

Sprint 11 covers:

- Gemini analysis list, detail, request metadata, validated report, validation, evidence, usage, budget, evaluation, comparison, and export routes;
- provider and configured-model identity;
- immutable prompt, report-schema, validation-policy, safety-setting, and provider-configuration versions;
- minimum structured request evidence and provenance;
- provider status, attempts, retries, timeout, rate limit, refusal, safety block, empty response, and failure states;
- structured-output parsing and strict application validation;
- evidence-reference verification;
- unsupported-claim, false-certainty, prompt-injection, stale-source, and contradiction checks;
- validated market regime, advisory action, analytical confidence, evidence, contradictions, risks, missing information, invalidation conditions, and summary;
- deterministic fallback and HOLD behavior;
- token usage, latency, cost estimate, daily and monthly budgets;
- prompt and model evaluation evidence;
- repeated-run stability and approved version comparison;
- research narrative derived only from validated structured evidence;
- links to market evidence, strategy, risk, experiment cycles, backtests, and audit history;
- responsive, accessible, secure, observable, and testable presentation.

Sprint 11 does not implement:

- execution tools;
- exchange, database, shell, filesystem, code-execution, or order-placement tools for Gemini;
- arbitrary prompt submission from the browser;
- prompt editing inside an active experiment;
- automatic prompt repair loops;
- Google Search grounding or unapproved external retrieval;
- live Gemini calls during ordinary historical backtests;
- browser-side validation authority;
- AI position sizing, order quantity, leverage, stop-loss, take-profit, risk-policy mutation, or experiment lifecycle authority;
- financial advice or probability-of-profit claims.

## 3. User Outcomes

A user should be able to answer:

1. Which analysis run am I viewing?
2. Which provider and configured model handled it?
3. Which immutable market snapshot and feature calculation were supplied?
4. Which prompt, schema, safety, provider, and validation versions governed the request?
5. Was the source evidence fresh, finalized, quality-approved, and complete?
6. Did the provider succeed, time out, rate-limit, refuse, safety-block, return nothing, or fail?
7. How many attempts occurred and why?
8. Did the response parse and validate against the exact project-owned schema?
9. Are every evidence reference and factual statement grounded in supplied inputs?
10. Did the report contain unsupported claims, false certainty, injected instructions, unknown fields, or invalid enums?
11. What validated regime, advisory action, analytical confidence, evidence, contradictions, risks, missing information, and invalidation conditions were produced?
12. Why is confidence not a probability of profit?
13. Which deterministic fallback or HOLD behavior applied when validation failed?
14. How much latency, token usage, and estimated cost did the run consume?
15. Is the daily or monthly budget healthy, near limit, exhausted, or unavailable?
16. How does this prompt or model version compare with an approved baseline?
17. How stable was the output across repeated runs?
18. Did any validated report influence strategy evidence, and did deterministic risk remain authoritative?

## 4. Canonical Routes

```text
/analyses
/analyses/:analysisId
/analyses/:analysisId/request
/analyses/:analysisId/report
/analyses/:analysisId/validation
/analyses/:analysisId/evidence
/analyses/:analysisId/usage
/analyses/:analysisId/compare
/ai/evaluations
/ai/evaluations/:evaluationId
/ai/prompts/:promptVersionId
/ai/schemas/:schemaVersionId
/ai/budgets
```

The workspace must be reachable from Today’s Roast, Market Evidence, experiment cycles, strategy and risk decisions, backtests using precomputed reports, and audit lineage.

All user-facing routes are read-only in Sprint 11.

## 5. Information Architecture

The analysis detail page is ordered as follows:

1. advisory, provider, freshness, validation, safety, budget, and fallback state;
2. analysis identity and immutable version references;
3. source market snapshot and feature evidence;
4. provider request and attempt outcome;
5. structured-output and validation pipeline;
6. validated research report;
7. evidence, contradictions, risks, missing information, and invalidation conditions;
8. unsupported-claim and prompt-injection checks;
9. deterministic fallback and downstream decision linkage;
10. usage, latency, cost, and budget evidence;
11. prompt/model evaluation and comparison;
12. methodology, limitations, audit, and export.

Invalid, blocked, stale, ungrounded, budget-exhausted, or rejected state must visually dominate any generated prose or advisory action.

## 6. Recommended Read Models

Recommended analysis contract:

```ts
interface GeminiAnalysisWorkspaceReadModel {
  schemaVersion: string;
  analysis: AnalysisRunIdentity;
  provider: ProviderExecutionSummary;
  configuration: GeminiConfigurationSummary;
  sourceEvidence: AnalysisSourceEvidenceSummary;
  attempts: ProviderAttemptSummary[];
  validation: AnalysisValidationSummary;
  report: ValidatedAiReportSummary | null;
  grounding: EvidenceGroundingSummary;
  safety: AiSafetySummary;
  fallback: DeterministicFallbackSummary;
  downstream: AiDownstreamLineageSummary;
  usage: AiUsageSummary;
  budget: AiBudgetSummary;
  evaluation: AiEvaluationReference | null;
  diagnostics: DiagnosticSummary[];
  limitations: LimitationSummary[];
  links: AiAnalysisResourceLinks;
}
```

Recommended validated report contract:

```ts
interface ValidatedAiReportSummary {
  reportId: string;
  reportSchemaVersion: string;
  marketRegime: "bullish" | "bearish" | "sideways" | "uncertain";
  recommendedAction: "hold" | "enter" | "exit" | "reduce";
  analyticalConfidence: string;
  evidence: AiEvidenceStatement[];
  contradictions: AiResearchStatement[];
  risks: AiResearchStatement[];
  missingInformation: AiResearchStatement[];
  invalidationConditions: AiResearchStatement[];
  summary: string;
  validationPolicyVersion: string;
  validatedAt: string;
  reportHash: string;
}
```

Recommended validation contract:

```ts
interface AnalysisValidationReadModel {
  schemaVersion: string;
  validation: ValidationRunIdentity;
  providerOutcome: ProviderOutcome;
  parsing: ValidationCheckResult;
  schemaChecks: ValidationCheckResult[];
  evidenceChecks: ValidationCheckResult[];
  unsupportedClaimChecks: ValidationCheckResult[];
  promptInjectionChecks: ValidationCheckResult[];
  sourceValidityChecks: ValidationCheckResult[];
  policyChecks: ValidationCheckResult[];
  outcome: "accepted" | "rejected" | "blocked" | "unavailable";
  reasonCodes: string[];
  reportReference: string | null;
  fallbackReference: string;
}
```

Recommended evaluation contract:

```ts
interface AiEvaluationReadModel {
  schemaVersion: string;
  evaluation: AiEvaluationIdentity;
  candidate: AiBehaviorVersionSet;
  baseline: AiBehaviorVersionSet | null;
  dataset: AiEvaluationDatasetSummary;
  metrics: AiEvaluationMetricSummary[];
  cases: AiEvaluationCaseSummary[];
  repeatedRuns: AiRepeatedRunSummary;
  outcome: "approved" | "rejected" | "needs_review" | "incomplete";
  warnings: AiEvaluationWarning[];
  limitations: LimitationSummary[];
}
```

The frontend must not parse raw model text into authoritative fields, validate schema compatibility, verify grounding, classify safety, calculate budget authority, or decide fallback behavior.

## 7. Analysis Identity

Required fields:

- immutable analysis-run ID;
- workspace ID;
- experiment and cycle IDs where applicable;
- market snapshot ID;
- feature-calculation ID;
- optional backtest and precomputed-dataset references;
- provider-configuration version;
- provider code;
- configured model identifier;
- prompt version;
- report-schema version;
- validation-policy version;
- safety-setting version;
- deterministic request or idempotency key;
- logical request ID;
- provider request and response IDs where safe;
- status;
- creation, start, completion, and rejection timestamps;
- correlation and job references;
- report and validation references.

Historical analysis identity and used versions are immutable.

## 8. Provider and Model Identity

The workspace must distinguish:

- project-owned provider code, such as `google_gemini` or `fake`;
- configured model identifier supplied to the provider;
- provider SDK adapter version;
- provider-configuration version and hash;
- environment;
- stable, preview, deprecated, or unavailable status when persisted;
- service tier and approved data-handling classification where available;
- configuration activation period.

The UI must not claim which underlying model actually served a request beyond provider-returned, persisted evidence.

No API key or secret configuration value may be exposed.

## 9. Source Evidence Contract

Required source evidence includes:

- immutable market snapshot ID and hash;
- exchange and normalized symbol;
- interval;
- analysis timestamp;
- latest finalized candle timestamp;
- freshness status and threshold;
- data-quality status;
- feature-calculation ID and hash;
- feature-set version;
- typed deterministic feature values;
- allowed evidence IDs;
- optional trusted summary references;
- source serialization version.

Only minimum required evidence may be sent.

Credentials, database URLs, tokens, authorization data, unrelated personal data, and unrestricted private payloads are prohibited.

## 10. Prompt Version Contract

Required prompt metadata:

- immutable prompt-version ID;
- purpose or agent;
- semantic version;
- system-instruction hash;
- task-template hash;
- evidence-envelope version;
- output-schema expectation;
- confidence interpretation;
- fallback instruction;
- supported language;
- status: draft, evaluation, approved, archived;
- creator and creation time;
- evaluation-report reference;
- activation and archive timestamps.

Active experiments retain their frozen prompt version.

The browser must not edit a used prompt version or submit arbitrary system instructions.

## 11. Prompt Layer Presentation

The workspace may present authorized, sanitized prompt metadata and templates according to role.

Layers include:

1. trusted system instruction;
2. trusted task instruction;
3. structured evidence envelope;
4. exact output contract.

Untrusted external text, when supported in a future approved phase, must remain inside explicit evidence fields and must be marked as data rather than instructions.

Secrets and sensitive licensed content must remain redacted.

## 12. Report Schema Contract

Required schema metadata:

- immutable schema-version ID;
- semantic version;
- schema hash;
- compatibility status;
- strict or permissive unknown-field policy;
- required fields;
- enum definitions;
- numeric ranges;
- maximum lengths and collection sizes;
- evidence-reference rules;
- activation and archive state;
- migration or compatibility notes.

Provider-side structured output does not replace application validation against this exact schema.

## 13. Provider Request Contract

Every request records or references:

- logical request ID;
- attempt ID;
- provider and configured model;
- prompt version;
- schema version;
- safety and generation configuration versions;
- source snapshot and feature references;
- timeout;
- retry policy;
- maximum output tokens;
- temperature;
- request timestamp;
- minimal request hash;
- idempotency key;
- safe provider metadata.

Raw request bodies must not be exposed by default.

Authorized diagnostics may show a redacted structured envelope, never secrets.

## 14. Provider Outcomes

Supported provider outcomes include:

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
- malformed response;
- budget blocked;
- configuration unavailable.

Every outcome must expose a canonical code, attempt, timestamp, latency, retry eligibility, safe explanation, and evidence reference.

## 15. Retry Contract

Retries are permitted only for approved transient outcomes.

Required retry evidence:

- shared logical request ID;
- unique attempt IDs;
- attempt sequence;
- trigger code;
- retry eligibility;
- configured maximum attempts;
- backoff policy version;
- provider retry guidance where available;
- start and completion timestamps;
- terminal outcome;
- cumulative usage and cost.

Validation errors, safety blocks, refusals, invalid requests, and authentication failures must not be retried as if transient.

The system must not ask Gemini to repair its own report indefinitely.

## 16. Structured Output Parsing

Parsing checks include:

- response candidate existence;
- expected content part existence;
- valid JSON or provider-structured representation;
- exact root type;
- bounded payload size;
- encoding validity;
- prohibited control-character handling;
- duplicate-key policy;
- parser version;
- parsing outcome and safe diagnostics.

A malformed response cannot become a validated report.

## 17. Validation Pipeline

The authoritative validation pipeline is:

1. classify provider outcome;
2. parse structured output;
3. validate exact schema version;
4. reject unknown fields according to policy;
5. validate required fields, enums, ranges, lengths, and collection bounds;
6. verify every evidence reference exists in supplied evidence;
7. detect unsupported factual claims;
8. detect false certainty and prohibited profit-probability language;
9. validate prompt-injection resistance and instruction-following boundaries;
10. verify source snapshot freshness, quality, and validity;
11. apply application policy checks;
12. persist immutable validation evidence;
13. accept a typed report or reject it;
14. publish a typed completion or rejection event;
15. invoke persisted deterministic fallback policy when required.

No individual provider field may bypass the full pipeline.

## 18. Validation Check Contract

Each check exposes:

- canonical check code;
- category;
- validator version;
- severity;
- input reference;
- outcome: passed, failed, warning, not applicable, or unavailable;
- safe explanation;
- affected report field or claim;
- supporting evidence references;
- timestamp.

Critical validation checks must remain expanded or immediately visible.

## 19. Validated Report Contract

A validated report contains:

- immutable report ID;
- exact report-schema version;
- market regime;
- advisory recommended action;
- analytical confidence;
- evidence statements;
- contradictions;
- risks;
- missing information;
- invalidation conditions;
- concise summary;
- validation-policy version;
- validation timestamp;
- source snapshot and feature references;
- report hash;
- limitations.

The report is advisory evidence only.

## 20. Analytical Confidence

Confidence means confidence in the analytical classification under supplied evidence.

The UI must:

- label it `Analytical confidence`;
- explain that it is not probability of profit, success, safety, or price direction;
- display its schema-defined range and precision;
- preserve contradictions and missing information nearby;
- avoid converting it into odds, risk score, position size, or recommendation strength;
- show unavailable or invalid confidence explicitly.

## 21. Evidence Grounding

Every report evidence statement must link to an allowed supplied evidence ID.

Required grounding fields:

- evidence ID;
- feature or source name;
- supplied typed value;
- unit;
- source timestamp;
- observation;
- claimed impact;
- grounding outcome;
- validator version.

The workspace must distinguish direct supplied facts from model interpretation.

An unknown or missing evidence reference rejects the report under strict policy.

## 22. Contradictions, Risks, and Missing Information

The report must preserve:

- contradictory evidence;
- analytical risks;
- unavailable inputs;
- missing or stale information;
- unsupported interpretations avoided;
- invalidation conditions.

These sections must not be collapsed in a way that makes a directional regime or action appear certain.

Empty collections must mean validated absence under the schema, not omitted validation.

## 23. Unsupported Claim Detection

Unsupported claims include assertions not grounded in supplied evidence, such as:

- current news or social sentiment not provided;
- whale activity or on-chain events without approved data;
- exact future price;
- expected return;
- probability of profit;
- guaranteed safety or success;
- hidden exchange activity;
- personal suitability;
- fabricated indicator values;
- fabricated sources.

Each detected claim requires a canonical code, text location or field, category, severity, explanation, and validation outcome.

Unsupported material claims reject the report according to policy.

## 24. Prompt Injection Defense

Validation and evaluation must cover:

- direct instructions inside evidence;
- encoded or obfuscated instructions;
- fake system or developer messages;
- requests to reveal secrets;
- requests to ignore the schema;
- requests to use tools;
- requests to place orders;
- requests to modify risk policy;
- requests to enable live trading;
- malicious HTML, Markdown, JSON strings, Unicode controls, and nested content;
- requests to suppress contradictions or invent evidence.

A report that follows injected evidence instructions is invalid.

The UI must sanitize all model-derived text before rendering.

## 25. Safety, Refusal, and Block State

Required safety fields:

- safety-setting version;
- provider safety outcome;
- refusal status;
- block category where safe;
- candidate availability;
- application safety checks;
- prompt-injection outcome;
- prohibited-authority checks;
- terminal decision;
- fallback reference.

The UI must not encourage disabling provider protections to obtain an answer.

## 26. Deterministic Fallback and HOLD

Fallback is a persisted application decision, not an improvised frontend behavior.

Fallback reasons include:

- provider unavailable;
- timeout or exhausted retries;
- rate limit;
- budget exhausted;
- refusal or safety block;
- empty or malformed response;
- schema failure;
- evidence-grounding failure;
- unsupported claim;
- stale or invalid source snapshot;
- configuration mismatch.

Required fallback fields:

- policy version;
- trigger code;
- resulting AI availability state;
- deterministic analysis reference where applicable;
- HOLD or block-AI-dependent-entry result;
- timestamp;
- strategy and cycle links.

Fallback must not fabricate an AI report.

## 27. Downstream Lineage and Authority Separation

Canonical lineage:

```text
market snapshot
  -> feature calculation
  -> Gemini request
  -> provider attempts
  -> structured response
  -> application validation
  -> validated advisory report or rejection
  -> deterministic strategy evaluation
  -> deterministic risk evaluation
  -> optional permitted paper action
```

The workspace must clearly distinguish:

- AI advisory action;
- deterministic strategy intent;
- deterministic risk outcome;
- permitted paper action;
- paper order;
- fill and reconciliation.

Gemini never directly creates or modifies later entities.

## 28. Usage and Cost Contract

Required usage fields where provider supplies them:

- input tokens or units;
- output tokens or units;
- total usage;
- cached usage where applicable;
- request count;
- retry count;
- latency;
- configured price-reference version;
- estimated cost and currency;
- estimate status;
- period attribution;
- missing-usage reason.

Usage and cost estimates must be labeled estimates when not provider-billed authoritative values.

## 29. Budget Contract

Budget dimensions may include:

- daily request budget;
- daily token budget;
- monthly cost budget in EUR;
- experiment-specific allocation;
- reserved usage;
- committed usage;
- remaining allowance;
- warning threshold;
- exhausted state;
- reset timestamp and timezone;
- policy version.

Possible budget states:

- healthy;
- warning;
- near limit;
- exhausted;
- disabled;
- unavailable;
- inconsistent.

The frontend must not authorize requests based on its own arithmetic.

## 30. Analysis History and Filtering

Analysis history may filter by approved bounded fields:

- date range;
- market and interval;
- experiment and cycle;
- provider;
- configured model;
- prompt version;
- schema version;
- provider outcome;
- validation outcome;
- regime;
- advisory action;
- safety or refusal state;
- fallback state;
- budget state;
- strategy-consumption state;
- correlation ID where authorized.

Filters must be URL-stable where appropriate, server-approved, authorization-aware, and cursor-paginated.

## 31. Prompt and Model Evaluation

Every candidate behavior set must be evaluated against a versioned dataset.

Required evaluation dimensions:

- structured-output success rate;
- schema-validation success rate;
- evidence-grounding rate;
- unsupported-claim rate;
- false-certainty rate;
- action consistency;
- contradiction and missing-information preservation;
- prompt-injection resistance;
- safety-block and refusal behavior;
- latency;
- input and output usage;
- estimated cost;
- stability across repeated runs;
- deterministic fallback behavior.

Every metric requires definition, unit, sample count, and confidence or limitation where appropriate.

## 32. Evaluation Dataset Contract

Required dataset fields:

- immutable dataset ID and version;
- purpose;
- case count;
- market and regime coverage;
- normal, ambiguous, stale, contradictory, malicious, schema-edge, provider-failure, and budget cases;
- source evidence hashes;
- expected invariant outcomes;
- prohibited claims;
- split or holdout status;
- dataset hash;
- creator and approval state.

Evaluation data must not contain secrets.

## 33. Repeated-Run Stability

Repeated-run evaluation must expose:

- candidate behavior version set;
- identical input hash;
- repetition count;
- temperature and seed policy where applicable;
- schema success consistency;
- regime consistency;
- advisory-action consistency;
- evidence-set overlap;
- unsupported-claim variance;
- latency and usage variance;
- report-hash expectations and limitations.

Probabilistic variation must not be hidden.

## 34. Version Comparison

The comparison workspace may compare:

- configured models;
- prompt versions;
- report-schema versions;
- safety-setting versions;
- generation configurations;
- validation-policy versions;
- deterministic fallback policies.

Required comparison dimensions:

- changed and unchanged versions;
- compatible evaluation dataset;
- schema and grounding success;
- unsupported claims;
- false certainty;
- action consistency;
- injection resistance;
- safety behavior;
- latency;
- usage and cost;
- repeated-run stability;
- warnings and limitations.

Comparisons must not silently alter active experiments.

## 35. Activation Evidence Boundary

A prompt, schema, provider configuration, model, validation policy, or safety-setting change is a versioned behavior change.

Activation requires:

- completed evaluation;
- acceptable schema and grounding results;
- prompt-injection checks;
- cost and latency review;
- compatibility assessment;
- owner approval where required;
- immutable activation audit event;
- activation only for new configurations or experiments unless a separately approved migration exists.

Sprint 11 provides read-only activation evidence. It does not add a browser activation command.

## 36. Research Narrative

A research narrative may transform validated structured findings into readable prose.

Requirements:

- use only validated structured report fields and supplied deterministic evidence;
- preserve numbers exactly;
- distinguish observation from model interpretation;
- include contradictions, risks, missing information, invalidation conditions, safety events, and limitations;
- identify paper/simulation context;
- avoid advice, promises, urgency, and certainty inflation;
- cite report sections or evidence IDs;
- record narrative generator version and hash;
- reject narrative output that adds unsupported claims.

The validated JSON report remains authoritative.

## 37. Narrative Validation

Narrative checks include:

- every number matches an authoritative field;
- every evidence claim links to a report or evidence ID;
- no omitted critical contradiction, risk, limitation, or safety state;
- no probability-of-profit reinterpretation;
- no investment advice;
- no live-trading implication;
- no new position sizing or execution instruction;
- no unsupported external context;
- bounded length and sanitized markup.

Invalid narrative is hidden or replaced by a deterministic structured summary.

## 38. Export Contract

Authorized exports may include:

- analysis identity and version package;
- redacted request metadata;
- provider-attempt history;
- validation report;
- validated structured report;
- evidence-grounding package;
- usage and budget package;
- evaluation and comparison report;
- validated research narrative.

Every export must include:

- schema and generation versions;
- analysis and workspace identity;
- provider and configured-model identity;
- prompt, schema, safety, validation, and provider-configuration versions;
- source snapshot and feature references;
- provider and validation outcomes;
- fallback state;
- usage and cost status;
- advisory and simulation disclaimers;
- provenance, report hash, warnings, and limitations;
- authorization context without secrets.

Raw prompts and provider responses require a separate retention, redaction, and authorization policy and are not default exports.

## 39. Page-State Matrix

Explicit states include:

- loading;
- no analyses;
- queued;
- requesting;
- retrying;
- validating;
- accepted;
- rejected;
- timed out;
- rate limited;
- provider failed;
- authentication failed;
- refused;
- safety blocked;
- empty response;
- malformed response;
- schema failed;
- grounding failed;
- unsupported claim;
- prompt injection detected;
- stale source;
- budget warning;
- budget exhausted;
- fallback HOLD;
- validated report unavailable;
- narrative unavailable;
- evaluation incomplete;
- comparison incompatible;
- schema mismatch;
- unauthorized;
- not found;
- backend unavailable;
- export unavailable.

Rejected or blocked output must not render as an ordinary valid report.

## 40. Responsive Behavior

Requirements:

- advisory, validation, safety, freshness, budget, and fallback state remains first;
- version and hash tables provide narrow-layout alternatives;
- evidence statements retain source value, unit, observation, impact, and validation context;
- report sections remain in semantic order;
- contradictions and risks remain visible near directional output;
- validation checks preserve severity and field context;
- usage and budget tables retain period and estimate labels;
- long IDs, hashes, model names, prompt versions, and reason codes wrap or copy safely;
- no critical evidence is hover-only.

## 41. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- keyboard-accessible filters, disclosures, comparisons, evidence links, and definitions;
- semantic tables with captions and headers;
- accessible definitions for provider, model, schema, grounding, confidence, fallback, and budget states;
- visible focus;
- status announcements for material asynchronous changes;
- no reliance on color alone;
- reflow at 200% and relevant cases at 400% zoom;
- reduced-motion support;
- screen-reader-readable decimals, percentages, timestamps, durations, usage, costs, and IDs;
- safe copy controls;
- model-derived text rendered with safe language and markup semantics.

## 42. Security and Authority Boundaries

The workspace must not:

- expose Gemini API keys or secret environment values;
- accept arbitrary browser prompts or system instructions;
- expose unrestricted raw prompt bodies or provider responses;
- grant Gemini web search, shell, code, database, filesystem, exchange, or execution tools;
- permit direct database mutation;
- permit position sizing or risk-policy changes;
- permit order, fill, portfolio, experiment, or halt commands;
- treat model output as authorization;
- trust browser validation, grounding, budget, or fallback calculations;
- render unsanitized model content;
- expose stack traces, SQL, tokens, cookies, authorization headers, or internal infrastructure details.

Application validation and deterministic strategy and risk remain authoritative.

## 43. Privacy and Data Minimization

The request, storage, UI, logs, exports, and telemetry must avoid:

- secrets and credentials;
- unrelated personal data;
- authorization material;
- database and internal service URLs;
- unrestricted licensed or private content;
- full raw prompts when hashes and version references suffice;
- unrestricted raw provider output;
- unnecessary personal identifiers;
- sensitive audit or incident details outside authorized roles.

Provider-side retention and regional eligibility must be reviewed for each production release.

## 44. Observability

Safe telemetry may include:

- requests by provider, configured model, and safe outcome;
- attempt and retry counts;
- latency;
- timeout and rate-limit counts;
- refusal and safety-block counts;
- empty and malformed response counts;
- schema-validation failures;
- evidence-grounding failures;
- unsupported-claim and prompt-injection detections;
- accepted and rejected report counts;
- token or usage totals;
- estimated cost;
- budget utilization and exhausted state;
- deterministic fallback counts;
- evaluation and comparison outcomes;
- narrative validation outcomes;
- approved correlation IDs;
- client build version.

Telemetry must not contain secrets, raw prompts, unrestricted responses, or full private evidence payloads.

## 45. Testing Strategy

### Contract Tests

Validate schemas, enums, decimals, units, timestamps, version references, provider outcomes, validation checks, report fields, fallback states, budget states, links, nullability, and compatibility.

### Provider Adapter Tests

Validate request construction, minimal evidence, official SDK isolation, configured model, timeout, cancellation, response metadata, and safe error mapping using fakes and dedicated smoke tests.

### Retry Tests

Validate transient eligibility, exponential backoff policy, shared logical request ID, unique attempts, maximum attempts, cumulative usage, and no retries for permanent or validation outcomes.

### Parsing and Schema Tests

Validate empty, malformed, oversized, invalid encoding, duplicate keys, unknown fields, missing fields, enums, ranges, lengths, collections, schema versions, and strict-mode behavior.

### Grounding and Factuality Tests

Validate evidence IDs, supplied values, fabricated features, unsupported news, social, on-chain, future-price, return, probability-of-profit, hidden-activity, and personal-suitability claims.

### Prompt-Injection Tests

Validate direct, encoded, nested, fake-system, secret-exfiltration, tool-use, order, risk-change, live-trading, HTML, Markdown, JSON, and Unicode attacks.

### Safety and Fallback Tests

Validate refusal, safety block, provider outage, timeout, rate limit, budget exhaustion, stale source, invalid report, deterministic fallback, HOLD, and AI-dependent-entry blocking.

### Usage and Budget Tests

Validate provider usage mapping, retries, cost estimates, reservation and commitment, concurrent budget limits, reset semantics, unavailable usage, and browser non-authority.

### Evaluation Tests

Validate dataset hashes, case categories, schema success, grounding, unsupported claims, false certainty, action consistency, injection resistance, safety behavior, latency, usage, cost, repeated-run stability, and activation evidence.

### Narrative Tests

Validate exact numbers, evidence citations, contradiction and limitation preservation, no advice, no execution instructions, no added claims, length bounds, and safe markup.

### Authorization and RLS Tests

Validate workspace isolation and role-specific access to prompts, raw metadata, reports, usage, budgets, evaluations, and exports.

### Route and Component Tests

Validate navigation, filters, state hierarchy, provider attempts, validation, report, evidence, fallback, downstream lineage, usage, budgets, evaluation, comparison, narrative, and safe errors.

### Accessibility Tests

Validate keyboard flow, headings, landmarks, tables, definitions, focus, announcements, copy controls, zoom, reflow, contrast, and model-derived content.

### Visual Regression

Capture queued, requesting, retrying, accepted, rejected, timeout, rate-limit, refusal, safety-block, schema-failure, grounding-failure, injection, stale-source, budget-warning, exhausted, fallback, evaluation, and comparison states across themes and viewports.

### Export Tests

Validate provenance, version references, validation, fallback, usage, budget, disclaimers, report hash, warnings, authorization, redaction, and prohibited-field absence.

## 46. Acceptance Criteria

Sprint 11 documentation is accepted when:

1. every analysis identifies provider, configured model, prompt, schema, safety, validation, provider configuration, source snapshot, feature set, and request identity;
2. provider outcome and application validation remain separate;
3. malformed, blocked, stale, ungrounded, unsupported, injected, or budget-blocked output cannot become a validated report;
4. validated output preserves evidence, contradictions, risks, missing information, invalidation conditions, and limitations;
5. analytical confidence is never presented as probability of profit;
6. retries remain bounded, outcome-aware, idempotent, and auditable;
7. fallback and HOLD are persisted deterministic application behavior;
8. usage, estimated cost, and budget state are visible without granting browser authority;
9. prompt and model comparisons use versioned evaluation evidence and repeated-run stability;
10. research narrative cannot alter numbers, omit critical limitations, or add unsupported claims;
11. Gemini remains strictly separate from strategy intent, deterministic risk, paper orders, fills, portfolio state, and experiment commands;
12. no arbitrary prompt, execution tool, live trading, risk mutation, secret exposure, or unsanitized model rendering is introduced;
13. security, privacy, accessibility, observability, evaluation, grounding, injection, fallback, and test gates are explicit.

## 47. Definition of Done

The Sprint 11 specification is complete when:

- this document is committed;
- `SPRINT_11_TASKS.md` is committed;
- terminology matches Gemini integration, AI architecture, prompts, market evidence, strategy, risk, experiment, backtest, API, database, security, testing, and observability documents;
- all provider, request, attempt, validation, report, evidence, factuality, injection, safety, fallback, usage, budget, evaluation, comparison, narrative, export, accessibility, and authority states are explicit;
- both commits are fetched and verified.

## 48. Next Sprint Boundary

Sprint 12 defines the **Authentication, Workspace Administration, Configuration Governance, Security, Privacy, and Release Readiness Workspace**, including Supabase Auth, role and membership evidence, RLS verification, immutable configuration lifecycle, secret and environment status, security findings, privacy and retention controls, deployment and migration readiness, release gates, and auditable owner approvals.
