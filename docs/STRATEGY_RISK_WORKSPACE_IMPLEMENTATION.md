# Strategy and Risk Decision Workspace Implementation Specification

Last reviewed: 2026-07-31  
Status: Sprint 7 authoritative strategy-and-risk workspace specification

## 1. Purpose

This document defines the implementation contract for the Strategy and Risk Decision Workspace of The Daily Roast AI.

The workspace explains how deterministic strategy intent was produced, how risk policy evaluated that intent, which constraints bound the result, whether the intent was allowed, reduced, rejected, halted, or not applicable, and how that decision relates to any later paper order or simulated fill.

The workspace is read-only. It must not allow users or AI systems to bypass, edit, or execute strategy and risk decisions.

## 2. Scope

Sprint 7 covers:

- strategy and risk routes;
- versioned decision read models;
- deterministic strategy evidence;
- risk-policy evaluation;
- reason codes and binding constraints;
- requested versus approved exposure;
- rejected, reduced, halted, and not-applicable states;
- policy and strategy version comparison;
- decision lineage;
- links to market evidence, paper orders, fills, ledger, and reconciliation;
- responsive and accessible presentation;
- export, privacy, security, observability, and testing requirements.

Sprint 7 does not implement strategy calculations, position sizing, risk evaluation, policy mutation, order creation, or live execution.

## 3. User Outcomes

A user should be able to answer:

1. Which strategy version produced the intent?
2. Which persisted market and feature evidence was evaluated?
3. What intent was proposed and why?
4. Which risk-policy version evaluated the intent?
5. Which limits and current account state were considered?
6. Was the intent allowed, reduced, rejected, halted, or not applicable?
7. What requested and approved exposure values were involved?
8. Which reason codes and binding constraints explain the result?
9. Did a permitted paper action create an order, fill, and reconciled ledger outcome?
10. How would the result differ under another approved policy or strategy version without rewriting history?

## 4. Canonical Routes

```text
/decisions
/decisions/:decisionId
/decisions/:decisionId/compare
```

The route must be reachable from Today’s Roast, Market Evidence, cycle lineage, paper order detail, and portfolio history.

The workspace remains read-only.

## 5. Information Architecture

The page is ordered as follows:

1. environment, simulation, freshness, reconciliation, and halt state;
2. decision identity and cycle context;
3. deterministic strategy intent;
4. deterministic risk decision;
5. requested and approved exposure;
6. reason codes and binding constraints;
7. evidence inputs;
8. permitted action and simulated execution linkage;
9. decision lineage;
10. version comparison;
11. diagnostics, methodology, limitations, and export.

A rejected, reduced, or halted outcome must never be visually subordinate to a positive strategy signal.

## 6. Decision Read Model

Recommended endpoints:

```http
GET /api/v1/decisions
GET /api/v1/decisions/{decision_id}
GET /api/v1/decisions/{decision_id}/lineage
GET /api/v1/decisions/{decision_id}/compare
GET /api/v1/decisions/{decision_id}/export
```

Recommended contract:

```ts
interface StrategyRiskDecisionReadModel {
  schemaVersion: string;
  decision: DecisionIdentity;
  strategyIntent: StrategyIntentSummary;
  riskEvaluation: RiskEvaluationSummary;
  exposure: ExposureDecisionSummary | null;
  constraints: BindingConstraintSummary[];
  evidence: DecisionEvidenceSummary;
  permittedAction: PermittedPaperActionSummary | null;
  execution: PaperExecutionLinkSummary | null;
  reconciliation: ReconciliationSummary | null;
  lineage: DecisionLineageSummary;
  diagnostics: DiagnosticSummary[];
  limitations: LimitationSummary[];
  links: DecisionResourceLinks;
}
```

The frontend must not recalculate intent, confidence, risk, drawdown, exposure, position size, policy outcome, or execution state.

## 7. Decision Identity

Required fields:

- immutable decision ID;
- cycle ID;
- market snapshot ID;
- feature-set version;
- strategy name and version;
- risk-policy name and version;
- evaluation timestamps;
- environment and simulation mode;
- decision status;
- correlation or trace ID;
- supersession state;
- related order, fill, ledger, and reconciliation IDs.

Historical decisions must remain immutable and inspectable.

## 8. Strategy Intent Contract

Required fields:

- strategy name and version;
- intent category;
- deterministic reason codes;
- input evidence references;
- parameter values or configuration version;
- evaluation timestamp;
- requested exposure or action when applicable;
- not-applicable reason when no intent exists.

The UI must not describe an intent as approved before risk evaluation.

## 9. Risk Evaluation Contract

Required fields:

- policy name and version;
- decision category: allowed, reduced, rejected, halted, or not-applicable;
- deterministic reason codes;
- requested exposure;
- approved exposure;
- binding constraints;
- current reconciled equity;
- open exposure;
- open-order count;
- daily and total drawdown;
- applicable limits;
- reconciliation precondition;
- market-data freshness precondition;
- evaluation timestamp.

A risk result must remain understandable without color.

## 10. Exposure Contract

Exposure values must use decimal-safe serialization and explicit currency or percentage units.

The workspace may show:

- requested order value;
- approved order value;
- requested portfolio percentage;
- approved portfolio percentage;
- current exposure;
- projected post-action exposure;
- maximum order limit;
- maximum position limit;
- residual available capacity.

The frontend must not derive final exposure values from displayed numbers.

## 11. Reason Codes

Reason codes are canonical machine-readable identifiers with human-readable explanations.

Examples include:

- `STRATEGY_SIGNAL_ABSENT`;
- `STRATEGY_ENTRY_CONDITION_MET`;
- `RISK_MAX_ORDER_LIMIT`;
- `RISK_MAX_POSITION_LIMIT`;
- `RISK_DAILY_DRAWDOWN_LIMIT`;
- `RISK_TOTAL_DRAWDOWN_LIMIT`;
- `RISK_OPEN_ORDER_LIMIT`;
- `RISK_RECONCILIATION_REQUIRED`;
- `RISK_MARKET_DATA_STALE`;
- `RISK_SYSTEM_HALTED`;
- `RISK_INSUFFICIENT_SIMULATED_CASH`;
- `RISK_PRECISION_OR_MIN_NOTIONAL`;
- `RISK_POLICY_NOT_APPLICABLE`.

Each reason must expose category, severity, source policy rule, explanation, and supporting evidence.

## 12. Binding Constraints

A binding constraint is a rule that materially changed or blocked the result.

The UI must distinguish:

- evaluated but non-binding rules;
- binding reduction rules;
- rejecting rules;
- halt rules;
- unavailable rule evidence.

The strongest outcome wins according to persisted policy semantics. The frontend must not decide precedence.

## 13. Evidence Inputs

Evidence may include:

- finalized candle references;
- market snapshot checksum;
- indicator values and parameters;
- portfolio and cash state;
- open paper orders;
- drawdown state;
- reconciliation result;
- active halt flags;
- strategy configuration version;
- risk-policy configuration version.

Each evidence item must provide an immutable identifier or stable reference and a link where available.

## 14. Permitted Action and Execution Linkage

The workspace must separate:

1. strategy intent;
2. risk decision;
3. permitted paper action;
4. created paper order;
5. simulated fill;
6. ledger postings;
7. reconciliation.

Absence of a later step must be explained. A permitted action is not equivalent to an executed fill.

## 15. Decision Lineage

Canonical lineage:

```text
market snapshot
  -> feature set
  -> strategy evaluation
  -> strategy intent
  -> risk policy evaluation
  -> risk decision
  -> permitted paper action
  -> paper order
  -> simulated fill
  -> ledger postings
  -> reconciliation
```

Every available step must include type, ID, timestamp, version, status, reason, and detail link.

Missing required lineage is an integrity failure.

## 16. Version Comparison

The workspace may compare a historical decision with an approved alternative strategy or policy version in a non-mutating analytical mode.

Comparison must:

- preserve original decision identity;
- label alternative evaluation as hypothetical or replayed;
- use the same immutable source evidence where required;
- show changed reason codes, constraints, requested exposure, approved exposure, and outcome;
- expose version and parameter differences;
- prohibit execution or automatic policy promotion.

A replay result must never overwrite the historical decision.

## 17. Filtering and Decision History

The decision list may filter by:

- date range;
- market;
- strategy version;
- policy version;
- outcome;
- reason code;
- cycle;
- presence of order or fill;
- reconciliation state.

Filters must be server-approved, bounded, and URL-stable where appropriate.

## 18. Export Contract

Decision export may support structured JSON and human-readable report formats.

Every export must include:

- decision and cycle IDs;
- snapshot and feature versions;
- strategy and policy versions;
- intent and risk outcome;
- reason codes and constraints;
- requested and approved exposure;
- evidence links or identifiers;
- action, order, fill, ledger, and reconciliation references;
- export schema version and generation timestamp;
- limitations and simulation disclaimer.

Exports must be server-generated and authorized.

## 19. Page-State Matrix

Explicit states include:

- loading;
- decision available;
- no decisions yet;
- not found;
- unauthorized;
- stale related evidence;
- missing optional execution;
- missing required lineage;
- unreconciled execution;
- superseded decision;
- schema mismatch;
- backend unavailable;
- halted system;
- comparison incompatible;
- export unavailable.

Integrity and reconciliation failures must not render as ordinary emptiness.

## 20. Responsive Behavior

Requirements:

- decision outcome and critical constraints remain visible first;
- strategy and risk sections stack in semantic order;
- reason-code tables provide narrow-layout alternatives;
- exposure comparisons retain explicit units;
- lineage remains chronological;
- no critical evidence is hover-only;
- long identifiers and policy names remain accessible.

## 21. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- clear text for all outcomes;
- keyboard-accessible filters, disclosures, lineage, and comparison controls;
- table captions and semantic headers;
- accessible definitions for reason codes;
- visible focus;
- status announcements for material state changes;
- reflow at 200% and relevant cases at 400% zoom;
- reduced-motion support;
- no reliance on color alone.

## 22. Security Boundaries

The workspace must not:

- mutate strategy or policy configuration;
- create, cancel, or modify orders;
- enable live trading;
- expose credentials or private provider payloads;
- allow AI output to change decisions;
- trust browser-calculated authorization;
- reveal stack traces, SQL, tokens, or internal infrastructure details;
- accept arbitrary executable policy expressions from the browser.

Server authorization and RLS remain authoritative.

## 23. Observability and Privacy

Safe telemetry may include:

- decision endpoint latency and status;
- outcome counts by safe category;
- reason-code counts;
- comparison compatibility failures;
- lineage-integrity failures;
- export status;
- client build version;
- approved correlation IDs.

Telemetry must not include secrets, raw account payloads, complete private financial records, or raw AI prompts.

## 24. Testing Strategy

### Contract Tests

Validate schema versions, decimal fields, units, enums, reason codes, constraints, and links.

### Domain Integration Tests

Validate deterministic intent and risk projection from persisted records, immutable history, exposure serialization, and lineage integrity.

### Route and Component Tests

Validate filters, outcome hierarchy, reason explanations, comparison state, and safe error mapping.

### Accessibility Tests

Validate keyboard flow, headings, tables, definitions, focus, announcements, zoom, and contrast.

### Visual Regression

Capture allowed, reduced, rejected, halted, not-applicable, unreconciled, integrity-failure, and comparison states across themes and viewports.

### Export Tests

Validate deterministic output, provenance, authorization, simulation labeling, and prohibited-field absence.

## 25. Acceptance Criteria

Sprint 7 documentation is accepted when:

1. strategy intent and risk decision remain separate;
2. requested and approved exposure are explicit;
3. reason codes and binding constraints are traceable;
4. rejected, reduced, halted, and not-applicable outcomes are fully specified;
5. later paper execution is linked but not conflated with permission;
6. historical decisions remain immutable;
7. comparison is labeled hypothetical or replayed and cannot execute;
8. frontend calculations cannot replace deterministic domain outputs;
9. security, privacy, accessibility, and test gates are explicit;
10. no live-trading authority is introduced.

## 26. Definition of Done

The Sprint 7 specification is complete when:

- this document is committed;
- `SPRINT_7_TASKS.md` is committed;
- terminology matches strategy, risk, market evidence, dashboard, API, database, security, and testing documents;
- all outcomes, reason codes, constraints, lineage, comparison, export, accessibility, and security boundaries are explicit;
- both commits are fetched and verified.

## 27. Next Sprint Boundary

Sprint 8 defines the **Paper Portfolio, Orders, Fills, Ledger, and Reconciliation Workspace**, including append-only accounting evidence, simulated execution costs, benchmark comparison, balance lineage, and fail-closed reconciliation presentation.