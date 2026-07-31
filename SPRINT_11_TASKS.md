# Sprint 11 Tasks — Gemini Analysis, Validation, Evidence, and Research Narrative Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a read-only Gemini research workspace that exposes immutable provider, model, prompt, schema, safety, validation, market-evidence, usage, budget, evaluation, fallback, and downstream lineage while ensuring malformed, stale, ungrounded, unsafe, injected, unsupported, or budget-blocked model output cannot become authoritative or gain strategy, risk, execution, portfolio, or experiment authority.

## Authoritative References

- `docs/GEMINI_ANALYSIS_VALIDATION_WORKSPACE_IMPLEMENTATION.md`
- `docs/GEMINI_INTEGRATION.md`
- `docs/AI_ARCHITECTURE.md`
- `docs/AI_PROMPTS.md`
- `docs/MARKET_EVIDENCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`
- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `docs/BACKTEST_EXPERIMENT_COMPARISON_WORKSPACE_IMPLEMENTATION.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `docs/OBSERVABILITY.md`
- `AGENTS.md`

## S11.1 Define Versioned Gemini Workspace Schemas

### Objective

Create explicit read contracts for analysis identity, provider execution, immutable configuration, source evidence, attempts, validation, report, grounding, safety, fallback, downstream lineage, usage, budget, evaluation, diagnostics, limitations, and links.

### Work

- define `GeminiAnalysisWorkspaceReadModel` and nested schemas;
- define validated-report, validation, evaluation, comparison, and narrative read models;
- define provider, validation, safety, fallback, budget, evaluation, and narrative states;
- use explicit decimal, usage, cost, duration, and timestamp representations;
- define compatibility, nullability, redaction, stale, warning, and unavailable rules;
- publish schemas in OpenAPI.

### Acceptance Criteria

- every analysis state is machine-readable;
- analytical confidence has an explicit contract;
- rejected output cannot satisfy the validated-report schema;
- redaction and role behavior are documented;
- contract tests pass.

## S11.2 Implement Analysis List Endpoint

### Objective

Expose bounded, filterable Gemini analysis history.

### Work

- implement `GET /api/v1/analyses` or the approved workspace-scoped equivalent;
- support filters for date, market, experiment, cycle, provider, configured model, prompt, schema, provider outcome, validation outcome, regime, advisory action, safety, fallback, budget, and strategy-consumption state;
- use cursor pagination and safe sort options;
- include freshness, validation, fallback, usage, and downstream summaries;
- enforce authorization and RLS;
- add safe telemetry.

### Acceptance Criteria

- accepted, rejected, blocked, failed, and fallback runs remain discoverable;
- filters are bounded and server-approved;
- unauthorized analyses are not exposed;
- pagination does not fabricate totals;
- API tests pass.

## S11.3 Implement Analysis Detail Endpoint

### Objective

Return the complete persisted analysis projection.

### Work

- implement `GET /api/v1/analyses/{analysis_id}`;
- return identity, provider, configuration, source evidence, attempts, validation, report, grounding, safety, fallback, downstream lineage, usage, budget, evaluation, diagnostics, limitations, and links;
- classify missing required provenance;
- map safe errors and correlation IDs;
- enforce role-specific redaction.

### Acceptance Criteria

- identical evidence produces the same response;
- provider success and validation acceptance remain separate;
- missing required lineage fails closed;
- secrets and unrestricted raw content are absent;
- integration tests pass.

## S11.4 Implement Gemini Workspace Routes

### Objective

Add analysis, request metadata, report, validation, evidence, usage, comparison, evaluation, prompt, schema, and budget routes.

### Work

- implement the approved canonical route family;
- add navigation and cross-links from dashboard, market evidence, cycles, decisions, backtests, and audit;
- preserve approved filters and comparison selections in URL state;
- add route-level error boundaries;
- ensure all Sprint 11 routes are read-only.

### Acceptance Criteria

- routes are directly addressable and keyboard reachable;
- invalid IDs and filters fail safely;
- refresh preserves stable read state;
- no arbitrary prompt or activation control exists;
- route tests pass.

## S11.5 Implement Analysis Identity and Advisory Header

### Objective

Present advisory, provider, freshness, validation, safety, budget, and fallback state before generated content.

### Work

- render analysis, workspace, cycle, snapshot, feature, provider, model, prompt, schema, validation, safety, request, report, and timestamps;
- render canonical advisory, simulation, freshness, validation, safety, budget, and fallback components;
- expose local time with accessible UTC;
- preserve critical state at narrow widths;
- prohibit execution or profit-probability language.

### Acceptance Criteria

- rejected, blocked, stale, unsafe, or exhausted state cannot appear valid;
- AI advisory status is always explicit;
- version and evidence references are inspectable;
- generated prose never dominates validation state;
- responsive and accessibility tests pass.

## S11.6 Implement Provider and Configured-Model Panel

### Objective

Expose provider identity and the exact configured behavior version without secrets.

### Work

- render provider code, configured model identifier, adapter version, provider-configuration version and hash, environment, persisted status, service-tier classification, and activation period;
- distinguish project configuration from provider-returned metadata;
- render unavailable or deprecated status when persisted;
- link to immutable configuration;
- redact secret values.

### Acceptance Criteria

- configured model is not presented as an unverifiable underlying serving guarantee;
- API keys and secret settings are absent;
- configuration version is immutable after use;
- provider and fake-provider identities remain distinct;
- component tests pass.

## S11.7 Implement Source Evidence Panel

### Objective

Show exactly which finalized market and feature evidence was supplied.

### Work

- render snapshot ID and hash, market, interval, analysis time, latest candle, freshness, quality, feature calculation, feature-set version, typed values, allowed evidence IDs, trusted summaries, and serialization version;
- link to Market Evidence;
- distinguish supplied facts from model interpretation;
- classify stale, invalid, incomplete, or unavailable inputs;
- preserve decimal precision and units.

### Acceptance Criteria

- every grounded statement can trace to supplied evidence;
- stale or invalid evidence is prominent;
- secrets and unrelated data are absent;
- browser does not calculate freshness authority;
- integration tests pass.

## S11.8 Implement Prompt Version Metadata View

### Objective

Expose immutable prompt behavior and evaluation lineage without allowing prompt mutation.

### Work

- render purpose, semantic version, hashes, evidence-envelope version, output-schema expectation, confidence interpretation, fallback instruction, supported language, lifecycle status, creator, timestamps, evaluation, and activation references;
- provide authorized sanitized template views by role;
- link to comparison and audit evidence;
- classify archived or incompatible prompts;
- prohibit browser editing.

### Acceptance Criteria

- used prompt versions remain immutable;
- trusted instructions and evidence layers remain separate;
- raw secrets or sensitive content are absent;
- active experiments retain frozen versions;
- authorization tests pass.

## S11.9 Implement Report Schema Metadata View

### Objective

Make the project-owned structured-output contract inspectable and versioned.

### Work

- render schema ID, semantic version, hash, compatibility, strictness, required fields, enums, ranges, lengths, collection bounds, evidence rules, status, and migration notes;
- validate examples against schema;
- link to validation results;
- expose compatibility failures;
- prevent browser modification.

### Acceptance Criteria

- provider structured output is not treated as sufficient validation;
- strict unknown-field behavior is explicit;
- breaking schema changes require versioning;
- examples validate automatically;
- schema tests pass.

## S11.10 Implement Request Metadata and Redacted Envelope View

### Objective

Expose request provenance and minimum-data behavior safely.

### Work

- render logical request, attempt, provider, model, prompt, schema, safety, generation configuration, source references, timeout, retry policy, output limit, temperature, request time, request hash, and idempotency key;
- provide an authorized redacted structured envelope;
- omit raw secret-bearing request bodies;
- classify missing request metadata;
- add safe copy controls.

### Acceptance Criteria

- request provenance is complete;
- secret or authorization data is absent;
- redaction is role-aware and deterministic;
- minimum-data policy is verifiable;
- privacy tests pass.

## S11.11 Implement Provider Attempt History

### Objective

Present every attempt, retry trigger, latency, and terminal outcome.

### Work

- render shared logical request, unique attempt IDs, sequence, outcome, timestamps, latency, retry eligibility, backoff policy, provider guidance, usage, cost, and terminal result;
- distinguish timeout, cancellation, rate limit, transient, permanent, authentication, invalid request, refusal, safety block, empty, malformed, budget, and configuration outcomes;
- support accessible timeline presentation;
- sanitize diagnostics.

### Acceptance Criteria

- attempt sequence is deterministic;
- permanent and validation failures are not shown as retryable;
- cumulative usage includes retries;
- terminal outcome is explicit;
- retry tests pass.

## S11.12 Implement Retry Policy Verification

### Objective

Prove retries are bounded, idempotent, and outcome-aware.

### Work

- verify transient-only eligibility;
- verify maximum attempts and backoff policy;
- verify shared logical identity and unique attempts;
- verify provider retry guidance handling;
- verify no retries for safety, refusal, authentication, invalid request, schema, or grounding failures;
- detect automatic repair-loop behavior.

### Acceptance Criteria

- retries terminate deterministically;
- duplicate provider side effects are not introduced;
- invalid output is not repeatedly self-repaired by Gemini;
- usage and cost remain attributable;
- policy tests pass.

## S11.13 Implement Structured Output Parsing Evidence

### Objective

Expose parser-level acceptance or failure before schema validation.

### Work

- render candidate existence, content existence, JSON validity, root type, payload size, encoding, control characters, duplicate-key policy, parser version, outcome, and diagnostics;
- reject empty, malformed, oversized, or invalidly encoded output;
- preserve safe raw hashes where appropriate;
- prevent raw unsanitized rendering;
- add parser fixtures.

### Acceptance Criteria

- malformed output cannot become a report;
- parser diagnostics are safe;
- duplicate-key behavior is deterministic;
- payload bounds are enforced;
- parser tests pass.

## S11.14 Implement Validation Pipeline Endpoint and Workspace

### Objective

Expose every application validation gate and final outcome.

### Work

- implement analysis validation detail;
- render provider, parsing, schema, evidence, unsupported-claim, false-certainty, prompt-injection, source-validity, application-policy, and fallback checks;
- render validator versions, severities, outcomes, fields, evidence, and timestamps;
- keep critical failures visible;
- publish accepted, rejected, blocked, or unavailable outcome.

### Acceptance Criteria

- all required checks are present before acceptance;
- one provider success cannot bypass failed application checks;
- critical validation failures remain expanded;
- missing checks fail closed;
- validation integration tests pass.

## S11.15 Implement Validated Report View

### Objective

Present only accepted structured advisory reports.

### Work

- render report ID, schema version, regime, advisory action, analytical confidence, evidence, contradictions, risks, missing information, invalidation conditions, summary, validation policy, source references, timestamp, hash, and limitations;
- sanitize all model text;
- distinguish observation from interpretation;
- link to validation and downstream decisions;
- render rejection state instead of invalid report content.

### Acceptance Criteria

- only accepted reports use the validated-report view;
- every section required by schema is present;
- report hash and provenance are inspectable;
- model-derived text is sanitized;
- component and E2E tests pass.

## S11.16 Implement Analytical Confidence Semantics

### Objective

Prevent confidence from being interpreted as profit probability or position authority.

### Work

- label the field `Analytical confidence`;
- render schema range and precision;
- place explanation, contradictions, and missing information nearby;
- prohibit odds, expected return, strength multiplier, position size, and recommendation certainty transformations;
- handle invalid and unavailable values.

### Acceptance Criteria

- probability-of-profit wording never appears;
- confidence cannot affect browser sizing or risk logic;
- invalid ranges fail validation;
- accessible definitions are present;
- content tests pass.

## S11.17 Implement Evidence Grounding Explorer

### Objective

Trace each model evidence statement to supplied deterministic values.

### Work

- render evidence ID, source name, typed value, unit, timestamp, observation, impact, grounding outcome, and validator version;
- distinguish source fact from interpretation;
- link to snapshot and feature detail;
- classify unknown, missing, or mismatched references;
- support bounded filtering.

### Acceptance Criteria

- every accepted evidence statement has an allowed source ID;
- unknown references reject the report under strict policy;
- values preserve authoritative precision;
- source and interpretation remain distinct;
- grounding tests pass.

## S11.18 Implement Contradiction, Risk, Missing Information, and Invalidation Sections

### Objective

Preserve uncertainty and opposing evidence alongside directional analysis.

### Work

- render contradictions, risks, missing inputs, stale or unavailable context, and invalidation conditions;
- include category, severity, evidence, and explanation where modeled;
- distinguish validated empty collections from omitted validation;
- prevent default collapse of critical items;
- sanitize model text.

### Acceptance Criteria

- directional output cannot hide contradictory evidence;
- empty state is semantically explicit;
- critical risks remain visible;
- missing information links to source status;
- accessibility tests pass.

## S11.19 Implement Unsupported-Claim Detection View

### Objective

Expose claims that exceed supplied evidence.

### Work

- detect and render unsupported news, social, on-chain, whale, future-price, expected-return, profit-probability, hidden-activity, personal-suitability, fabricated-feature, and fabricated-source claims;
- render canonical code, field, category, severity, explanation, evidence, and outcome;
- reject material unsupported claims according to policy;
- link to evaluation cases;
- sanitize excerpts.

### Acceptance Criteria

- unsupported material claims cannot survive acceptance;
- claim locations are traceable;
- detection rules are versioned;
- false-certainty language is covered;
- factuality tests pass.

## S11.20 Implement Prompt-Injection Defense View and Tests

### Objective

Prove evidence is treated as data rather than instructions.

### Work

- cover direct, encoded, obfuscated, nested, fake-system, secret, schema-bypass, tool-use, order, risk-change, live-trading, contradiction-suppression, HTML, Markdown, JSON, and Unicode attacks;
- render detection outcome and affected fields;
- invalidate reports that follow injected instructions;
- sanitize all displayed payloads;
- link to evaluation cases.

### Acceptance Criteria

- injected instructions cannot change report authority;
- secret requests never reveal values;
- tool, order, and risk-change requests fail;
- malicious markup is inert;
- security tests pass.

## S11.21 Implement Safety, Refusal, and Block Presentation

### Objective

Expose provider and application safety state without encouraging protection bypass.

### Work

- render safety-setting version, provider outcome, refusal, safe block category, candidate availability, application checks, injection outcome, prohibited-authority checks, terminal decision, and fallback;
- distinguish refusal from provider failure;
- preserve safe diagnostics;
- prohibit disable-safety guidance;
- add accessible definitions.

### Acceptance Criteria

- safety block never appears as empty success;
- refusal and block remain auditable;
- protections are not weakened through UI;
- fallback is linked;
- safety tests pass.

## S11.22 Implement Deterministic Fallback and HOLD View

### Objective

Explain safe application behavior when AI is unavailable or rejected.

### Work

- render fallback policy version, trigger, AI availability, deterministic analysis, HOLD or entry-block result, timestamp, cycle, strategy, and audit links;
- cover provider, timeout, retry, rate, budget, refusal, safety, empty, malformed, schema, grounding, unsupported, stale, and configuration failures;
- prevent fabricated report display;
- distinguish fallback from successful analysis.

### Acceptance Criteria

- every terminal rejected or unavailable case has fallback evidence;
- fallback is server-provided;
- HOLD is not presented as Gemini advice when no valid report exists;
- downstream behavior remains deterministic;
- fallback tests pass.

## S11.23 Implement Downstream Authority Lineage

### Objective

Keep AI advisory output separate from deterministic strategy, risk, and paper execution.

### Work

- render snapshot, features, request, attempts, validation, report or rejection, strategy, risk, action, order, fill, and reconciliation links;
- label advisory action, strategy intent, risk outcome, permitted action, order, and fill distinctly;
- render non-consumption reasons;
- classify direct AI-to-order or missing-risk lineage as critical;
- preserve chronological order.

### Acceptance Criteria

- Gemini never appears to create an order;
- deterministic risk remains authoritative;
- missing required downstream boundaries fail closed;
- non-consumed reports are explainable;
- lineage tests pass.

## S11.24 Implement Usage and Cost Endpoint and View

### Objective

Expose provider usage, latency, retries, and cost estimates with provenance.

### Work

- render input, output, total, cached usage, request and retry counts, latency, price-reference version, estimated cost, currency, estimate state, period, and missing reason;
- aggregate retries correctly;
- label estimates distinctly from billed values;
- enforce authorization and minimization;
- add safe telemetry.

### Acceptance Criteria

- usage is attributable to attempts and analysis;
- cost estimates identify pricing version;
- missing provider usage is explicit;
- browser does not calculate spending authority;
- usage tests pass.

## S11.25 Implement Budget Endpoint and View

### Objective

Present daily, monthly, and experiment allowance without browser request authority.

### Work

- render request, token, monthly EUR, experiment allocation, reserved, committed, remaining, warning, exhausted, reset, timezone, policy, and consistency state;
- implement concurrency-safe server summaries;
- render healthy, warning, near-limit, exhausted, disabled, unavailable, and inconsistent states;
- link to cycle fallback;
- protect private financial configuration by role.

### Acceptance Criteria

- concurrent usage cannot overrun policy through UI race;
- exhausted state blocks optional AI calls server-side;
- reset semantics are explicit;
- inconsistent state is critical;
- budget tests pass.

## S11.26 Implement AI Evaluation Dataset and Run Views

### Objective

Expose versioned evaluation evidence for prompt and model candidates.

### Work

- render dataset identity, purpose, case count, regime coverage, normal, ambiguous, stale, contradictory, malicious, schema-edge, provider-failure, budget, holdout, source hashes, expected invariants, prohibited claims, creator, approval, and hash;
- render candidate behavior versions;
- render status and completeness;
- link cases and artifacts;
- preserve failed evaluations.

### Acceptance Criteria

- every evaluation maps to an immutable dataset;
- malicious and failure cases are included;
- secrets are absent;
- incomplete evaluations cannot approve a candidate;
- evaluation integration tests pass.

## S11.27 Implement Evaluation Metrics and Case Explorer

### Objective

Present schema, grounding, factuality, consistency, safety, cost, and stability evidence.

### Work

- render structured-output, schema, grounding, unsupported-claim, false-certainty, action-consistency, contradiction, injection, safety, latency, usage, cost, stability, and fallback metrics;
- include definitions, units, sample counts, thresholds, warnings, and limitations;
- render case-level inputs, expected invariants, outcomes, and differences safely;
- support bounded filters;
- prohibit cherry-picked default views.

### Acceptance Criteria

- metric definitions are versioned;
- sample counts are visible;
- failed and unfavorable cases remain discoverable;
- thresholds and approval logic are explicit;
- metric tests pass.

## S11.28 Implement Repeated-Run Stability View

### Objective

Show probabilistic variation under identical evidence and configuration.

### Work

- render input hash, repetition count, temperature, seed policy, schema consistency, regime consistency, action consistency, evidence overlap, unsupported-claim variance, latency, usage, and report-hash expectations;
- preserve every repetition reference;
- distinguish expected variation from critical instability;
- add accessible summaries;
- avoid false determinism claims.

### Acceptance Criteria

- probabilistic variation is visible;
- identical inputs and versions are verified;
- critical schema or safety instability is prominent;
- insufficient repetitions remain explicit;
- stability tests pass.

## S11.29 Implement Prompt, Model, Schema, Safety, and Policy Comparison

### Objective

Compare versioned AI behavior without altering active experiments.

### Work

- validate evaluation-dataset compatibility;
- compare configured models, prompt, schema, safety, generation, validation, and fallback versions;
- render changed and unchanged inputs;
- compare schema success, grounding, unsupported claims, certainty, action consistency, injection, safety, latency, usage, cost, stability, warnings, and limitations;
- preserve source identities.

### Acceptance Criteria

- incompatible comparisons fail closed;
- changed behavior is traceable to version differences;
- active experiments are not modified;
- source evaluations remain immutable;
- comparison tests pass.

## S11.30 Implement Activation Evidence Boundary

### Objective

Show whether a behavior version set is eligible for manual activation review.

### Work

- render evaluation completeness, schema and grounding results, injection checks, cost, latency, compatibility, owner approval, audit, and target configuration eligibility;
- render missing gates;
- prohibit browser activation;
- preserve activation only for new configurations or approved migrations;
- link to configuration governance.

### Acceptance Criteria

- no single metric triggers activation;
- missing gates remain visible;
- active experiments retain frozen behavior;
- owner approval remains separate;
- authority tests pass.

## S11.31 Implement Validated Research Narrative

### Objective

Create readable prose only from validated structured evidence.

### Work

- render or generate narrative from validated report and deterministic evidence;
- preserve numbers exactly;
- cite evidence and report sections;
- include contradictions, risks, missing information, invalidation conditions, safety state, limitations, and simulation context;
- record generator version and hash;
- reject added claims, advice, urgency, certainty inflation, sizing, or execution instructions.

### Acceptance Criteria

- JSON remains authoritative;
- every material claim is traceable;
- no number changes;
- invalid narrative falls back to deterministic structured summary;
- narrative tests pass.

## S11.32 Implement Authorized Analysis Export

### Objective

Generate provenance-preserving analysis, validation, evidence, usage, budget, evaluation, and narrative packages.

### Work

- support approved JSON and human-readable formats;
- include identity, provider, configured model, prompt, schema, safety, validation, configuration, source, attempts, outcomes, report, grounding, fallback, usage, budget, evaluation, narrative, disclaimers, hashes, warnings, and limitations;
- generate server-side;
- enforce authorization and redaction;
- exclude raw prompts and responses by default.

### Acceptance Criteria

- rejected or blocked state cannot be omitted;
- provenance and fallback remain explicit;
- secrets and unrestricted raw content are absent;
- report hashes are verified where required;
- export tests pass.

## S11.33 Add Explicit State Handling

### Objective

Define safe rendering for every provider, validation, safety, budget, evaluation, and narrative state.

### Work

- implement loading, empty, queued, requesting, retrying, validating, accepted, rejected, timeout, rate limit, provider failure, authentication failure, refusal, safety block, empty, malformed, schema failure, grounding failure, unsupported claim, injection, stale source, budget warning, exhausted, fallback HOLD, report unavailable, narrative unavailable, evaluation incomplete, incompatible comparison, schema mismatch, unauthorized, not found, backend unavailable, and export failure states;
- define bounded retry policy;
- prevent infinite UI retries;
- label cached data stale.

### Acceptance Criteria

- rejected and blocked output never renders as valid report content;
- loading fabricates no report;
- retry is offered only when safe;
- cached state is visibly stale;
- state-matrix tests pass.

## S11.34 Add Responsive and Accessibility Verification

### Objective

Ensure AI evidence, validation, and limitations remain usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom layouts;
- test headings, landmarks, focus, keyboard operation, tables, timelines, definitions, evidence links, validation checks, comparisons, and copy controls;
- verify model-derived text semantics and sanitization;
- test reduced motion and contrast;
- record screen-reader spot checks;
- test long IDs, model names, versions, hashes, claims, and reason codes.

### Acceptance Criteria

- no critical evidence is hover-only;
- no outcome relies only on color;
- contradictions and failures remain accessible;
- table and timeline context survives narrow widths;
- no critical automated violation remains;
- manual evidence is recorded.

## S11.35 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make validation, grounding, injection resistance, budget control, advisory authority, and redaction release-blocking.

### Work

- add contract, provider, retry, parsing, schema, grounding, factuality, injection, safety, fallback, usage, budget, evaluation, stability, comparison, narrative, route, E2E, accessibility, visual, authorization, and RLS tests;
- add hostile-content, secret, prompt, response, log-redaction, markup, and prohibited-tool checks;
- verify no browser prompt, activation, strategy, risk, order, portfolio, experiment, shell, database, or live-trading authority exists;
- instrument safe provider, attempt, latency, failure, safety, validation, grounding, claim, injection, usage, cost, budget, fallback, evaluation, comparison, narrative, and export metrics;
- test prohibited telemetry fields;
- verify normal CI uses deterministic fake provider and no paid request.

### Acceptance Criteria

- malformed, unsafe, stale, unsupported, injected, and ungrounded output fails closed;
- unauthorized access fails closed;
- no AI or browser path gains execution or policy authority;
- telemetry contains no prohibited fields;
- visual changes require review;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| API contracts | OpenAPI, schema, enum, decimal, unit, timestamp, version, null, redaction, state, link, and compatibility tests |
| Provider | Request construction, model configuration, timeout, cancellation, attempts, retry eligibility, metadata, and safe error tests |
| Validation | Parsing, schema, unknown field, enum, range, length, evidence, source freshness, policy, and rejection tests |
| Factuality and safety | Unsupported claim, false certainty, prompt injection, refusal, safety block, prohibited authority, sanitization, and fallback tests |
| Report | Regime, action, analytical confidence, evidence, contradictions, risks, missing information, invalidation, summary, hash, and limitation tests |
| Usage and budget | Tokens, retries, latency, estimates, pricing version, reservation, commitment, concurrency, warning, exhausted, and reset tests |
| Evaluation | Dataset, cases, schema success, grounding, claims, consistency, injection, safety, latency, usage, cost, repeated runs, and comparison tests |
| Narrative | Exact numbers, evidence citations, preserved warnings, no advice, no execution, no added claims, safe markup, and deterministic fallback tests |
| Accessibility | Keyboard, tables, timelines, definitions, model text, evidence, validation, comparison, zoom, reflow, and manual review |
| Security and privacy | RLS, authorization, redaction, secret scan, prompt/response minimization, no tools, no mutation, no execution, no live trading, and telemetry tests |

## Sprint Exit Gate

Sprint 11 is complete only when:

- S11.1 through S11.35 are implemented and verified;
- every analysis identifies immutable provider, configured model, prompt, schema, safety, validation, provider configuration, snapshot, feature, request, and attempt evidence;
- provider success and application validation remain separate;
- malformed, blocked, stale, ungrounded, unsupported, injected, or budget-blocked output cannot become a validated report;
- analytical confidence is explicitly not probability of profit;
- evidence statements trace to allowed supplied evidence;
- contradictions, risks, missing information, invalidation conditions, and limitations remain visible;
- retries are bounded, idempotent, outcome-aware, and fully attributed;
- fallback and HOLD are persisted deterministic behavior;
- usage, cost estimates, and budgets are server-authoritative and traceable;
- evaluation, repeated-run stability, and comparison evidence is versioned and complete;
- narrative preserves authoritative numbers and cannot add claims or execution instructions;
- Gemini remains strictly advisory and separate from strategy, risk, orders, fills, portfolio, halts, and experiment commands;
- no arbitrary prompt, secret exposure, tool use, database mutation, policy mutation, private exchange order, testnet, or live-trading authority exists;
- accessibility, responsive, security, privacy, contract, provider, validation, grounding, factuality, injection, fallback, usage, budget, evaluation, stability, comparison, narrative, E2E, export, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 12 defines and implements the Authentication, Workspace Administration, Configuration Governance, Security, Privacy, and Release Readiness Workspace.
