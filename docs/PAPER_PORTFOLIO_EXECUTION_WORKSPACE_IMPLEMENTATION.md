# Paper Portfolio, Execution, Ledger, and Reconciliation Workspace Implementation Specification

Last reviewed: 2026-07-31  
Status: Sprint 8 authoritative paper-portfolio and execution workspace specification

## 1. Purpose

This document defines the implementation contract for the Paper Portfolio, Orders, Fills, Ledger, and Reconciliation Workspace of The Daily Roast AI.

The workspace explains the current simulated financial state, how approved deterministic risk decisions became paper orders, how those orders were filled under a versioned execution model, how each fill posted balanced append-only ledger evidence, and whether the resulting portfolio projection reconciles with the accounting source of truth.

The workspace is evidence-first and read-only in Sprint 8. It must not create orders, modify fills, rewrite ledger entries, bypass risk policy, enable live execution, or permit AI-generated financial commands.

## 2. Scope

Sprint 8 covers:

- paper portfolio overview and history routes;
- versioned portfolio, order, fill, ledger, valuation, and reconciliation read models;
- available and reserved balances;
- positions, cost basis, realized and unrealized P&L;
- equity, exposure, fees, and drawdown;
- market and limit paper-order lifecycle presentation;
- partial fills, cancellations, rejections, and terminal states;
- simulated spread, slippage, fees, precision, and minimum-notional evidence;
- append-only double-entry ledger inspection;
- projection-state and ledger-sequence lineage;
- reconciliation outcomes, mismatches, rebuild comparisons, and halt state;
- portfolio and cash benchmark comparison;
- authorized export;
- responsive, accessible, secure, observable, and testable presentation.

Sprint 8 does not implement:

- real exchange credentials;
- live order placement;
- leverage, margin, futures, or shorting;
- browser-side accounting calculations;
- mutable ledger corrections;
- arbitrary portfolio funding;
- order creation or cancellation controls in the product UI;
- manual reconciliation overrides;
- AI authority over orders, accounting, or halts.

## 3. User Outcomes

A user should be able to answer:

1. Which paper portfolio and experiment am I viewing?
2. Is the portfolio simulated, current, reconciled, stale, or halted?
3. What are the available and reserved balances?
4. Which positions are open, and what are their cost basis and valuation inputs?
5. What are realized P&L, unrealized P&L, fees, equity, exposure, and drawdown?
6. Which deterministic decision authorized each paper order?
7. What requested and approved values were used?
8. Which execution-model version determined fill eligibility, spread, slippage, fees, precision, and partial fills?
9. Which immutable ledger transaction accounts for every financial effect?
10. Does the persisted portfolio projection match the ledger-derived state?
11. What caused any mismatch, halt, stale valuation, or missing lineage?
12. How did the simulated portfolio perform relative to cash and approved buy-and-hold benchmarks?

## 4. Canonical Routes

```text
/portfolio
/portfolio/history
/portfolio/orders
/portfolio/orders/:orderId
/portfolio/fills/:fillId
/portfolio/ledger
/portfolio/ledger/:transactionId
/portfolio/reconciliation
/portfolio/reconciliation/:runId
```

Optional portfolio-scoped canonical forms may be used when multiple portfolios are supported:

```text
/portfolios/:portfolioId
/portfolios/:portfolioId/history
/portfolios/:portfolioId/orders
/portfolios/:portfolioId/ledger
/portfolios/:portfolioId/reconciliation
```

The chosen route family must be consistent, directly addressable, authorization-aware, and documented in the application shell.

The workspace must be reachable from Today’s Roast, strategy and risk decisions, experiment status, backtest comparison, and audit lineage.

## 5. Information Architecture

The portfolio overview is ordered as follows:

1. environment, simulation, reconciliation, freshness, and halt state;
2. portfolio and experiment identity;
3. reconciled equity and benchmark summary;
4. available and reserved balances;
5. positions and valuation evidence;
6. realized and unrealized performance;
7. exposure, drawdown, and active limits;
8. open and recent paper orders;
9. recent fills and simulated execution costs;
10. ledger and projection lineage;
11. reconciliation evidence and diagnostics;
12. methodology, limitations, and export.

A reconciliation mismatch, stale valuation, active halt, or missing required ledger evidence must visually dominate positive performance metrics.

## 6. Recommended Read Models

Recommended portfolio contract:

```ts
interface PaperPortfolioWorkspaceReadModel {
  schemaVersion: string;
  portfolio: PaperPortfolioIdentity;
  experiment: ExperimentIdentity | null;
  safetyState: PortfolioSafetyState;
  stateVersion: PortfolioStateVersionSummary;
  balances: PortfolioBalanceSummary[];
  positions: PaperPositionSummary[];
  performance: PortfolioPerformanceSummary;
  exposure: PortfolioExposureSummary;
  drawdown: PortfolioDrawdownSummary;
  valuation: PortfolioValuationSummary;
  benchmarks: PortfolioBenchmarkSummary[];
  openOrders: PaperOrderSummary[];
  recentFills: PaperFillSummary[];
  ledgerSummary: LedgerSummary;
  reconciliation: ReconciliationSummary;
  diagnostics: DiagnosticSummary[];
  limitations: LimitationSummary[];
  links: PortfolioResourceLinks;
}
```

Recommended order contract:

```ts
interface PaperOrderDetailReadModel {
  schemaVersion: string;
  order: PaperOrderIdentity;
  authorization: ApprovedDecisionReference;
  requestedValues: RequestedOrderValues;
  approvedValues: ApprovedOrderValues;
  executionModel: ExecutionModelReference;
  lifecycle: OrderStateTransition[];
  fills: PaperFillSummary[];
  reservations: ReservationEvidence[];
  totals: OrderAccountingTotals;
  ledgerTransactions: LedgerTransactionReference[];
  reconciliation: ReconciliationReference | null;
  diagnostics: DiagnosticSummary[];
  links: OrderResourceLinks;
}
```

Recommended ledger transaction contract:

```ts
interface LedgerTransactionReadModel {
  schemaVersion: string;
  transaction: LedgerTransactionIdentity;
  entries: LedgerEntrySummary[];
  balanceCheck: LedgerBalanceCheck;
  businessReference: BusinessReference;
  projectionImpact: ProjectionImpactSummary | null;
  reconciliationReferences: ReconciliationReference[];
  correctionLineage: LedgerCorrectionLineage | null;
  diagnostics: DiagnosticSummary[];
}
```

Recommended reconciliation contract:

```ts
interface ReconciliationRunReadModel {
  schemaVersion: string;
  run: ReconciliationRunIdentity;
  comparedState: ComparedPortfolioState;
  ledgerDerivedState: ReconciledFinancialState;
  persistedProjection: ReconciledFinancialState;
  checks: ReconciliationCheckResult[];
  outcome: "matched" | "mismatch" | "unable_to_reconcile";
  mismatchReasons: ReconciliationMismatchReason[];
  halt: TradingHaltReference | null;
  rebuildComparison: RebuildComparisonSummary | null;
  diagnostics: DiagnosticSummary[];
}
```

The frontend must not calculate authoritative balances, cost basis, P&L, equity, exposure, drawdown, ledger balance, fill totals, or reconciliation outcomes.

## 7. Portfolio Identity and Safety State

Required identity fields:

- immutable portfolio ID;
- workspace ID;
- experiment ID when applicable;
- base currency;
- paper execution-model version;
- active frozen risk-policy version;
- creation and start timestamps;
- current portfolio-state version;
- last applied ledger sequence;
- environment;
- simulation mode;
- status;
- active halt reference;
- correlation or trace references where approved.

Required safety fields:

- simulation label;
- reconciliation outcome and timestamp;
- valuation timestamp and freshness;
- state-version timestamp;
- halt status, scope, source, and reason code;
- integrity status;
- projection rebuild status when active;
- supersession or archive state.

Simulation, stale, unreconciled, mismatched, or halted state must remain visible at every viewport width.

## 8. Portfolio State-Version Contract

Every displayed portfolio projection must identify:

- immutable state-version ID;
- version number;
- last applied ledger sequence;
- state hash;
- accounting-policy version;
- valuation reference;
- creation timestamp;
- reconciliation status;
- predecessor state version where applicable.

Risk evaluations and paper orders must link to the exact portfolio-state version they used.

The UI must never silently replace historical values with current projections.

## 9. Balance Contract

Balance categories include:

- available cash by currency;
- reserved cash by currency;
- available asset quantity;
- reserved asset quantity;
- total owned quantity;
- pending release or settlement state only when explicitly modeled.

Every amount must expose:

- decimal string value;
- asset or currency;
- unit;
- state-version reference;
- ledger-sequence reference;
- timestamp;
- status or limitation when unavailable.

Available and reserved values must remain visually and programmatically distinct.

Negative balances are critical integrity failures unless a future explicitly versioned accounting model permits them.

## 10. Position and Cost-Basis Contract

Required position fields:

- asset or normalized symbol;
- available quantity;
- reserved quantity;
- total quantity;
- weighted-average cost or another explicit versioned method;
- remaining cost basis;
- mark price;
- market value;
- realized P&L;
- unrealized P&L;
- cumulative fees;
- valuation source, timestamp, and freshness;
- ledger and fill references;
- accounting-policy version.

The selected cost-basis method must be named. The UI must not infer or recalculate cost basis from displayed fills.

A stale or missing mark price must produce an explicit stale or unavailable valuation state rather than a fabricated current value.

## 11. Performance Contract

The workspace may present:

- initial virtual funding;
- net deposited virtual capital;
- current reconciled equity;
- realized P&L;
- unrealized P&L;
- gross return;
- net return after simulated fees and modeled execution costs;
- cumulative fees;
- modeled spread cost;
- modeled slippage cost;
- turnover;
- high-water mark;
- daily and total drawdown.

Every metric must identify:

- calculation version;
- start and end timestamps;
- valuation reference where applicable;
- currency or percentage unit;
- reconciliation state;
- freshness state;
- limitation or unavailable reason.

Positive return must never suppress active risk, reconciliation, or stale-data warnings.

## 12. Exposure and Drawdown Contract

Required exposure fields:

- gross exposure;
- net exposure;
- current position market value;
- reserved-order exposure;
- projected exposure where persisted;
- applicable maximum position and order limits;
- residual approved capacity where persisted;
- state-version reference.

Required drawdown fields:

- current equity;
- high-water mark;
- daily reference equity;
- daily drawdown;
- total drawdown;
- configured halt thresholds;
- reset timezone and timestamp;
- active halt reference.

The frontend must not calculate final exposure or drawdown values.

## 13. Paper Order Identity and Lifecycle

Required order fields:

- immutable order ID;
- portfolio ID;
- approved risk-evaluation ID;
- strategy-decision ID;
- idempotency or client order ID;
- symbol;
- side;
- order type;
- requested quantity and notional;
- approved quantity and notional;
- limit price where applicable;
- time in force;
- execution-model version;
- current state;
- creation, activation, update, and terminal timestamps;
- cancellation or rejection reason;
- filled and remaining quantity;
- reservation references;
- fill and ledger references.

Supported presentation states include:

- pending;
- open;
- partially filled;
- filled;
- cancelled;
- rejected.

Terminal states are immutable. Historical transitions must not be rewritten.

## 14. Requested, Approved, Filled, and Remaining Values

The UI must present these as separate concepts:

1. strategy-requested exposure or action;
2. risk-approved quantity or notional;
3. paper-order quantity or notional after precision rules;
4. cumulative filled quantity and notional;
5. remaining open or cancelled quantity;
6. ledger-posted financial effect.

Every value must use decimal-safe serialization and explicit units.

A risk approval is not an order. An order is not a fill. A fill is not reconciled accounting until ledger and reconciliation evidence exist.

## 15. Execution-Model Evidence

Every order and fill must reference an immutable execution-model version containing or linking to:

- reference-price rule;
- next-event and no-look-ahead rule;
- market-order fill rule;
- limit-crossing rule;
- spread model;
- slippage model;
- fee schedule;
- volume or participation assumption;
- partial-fill rule;
- intrabar ordering rule;
- precision and rounding rule;
- minimum-quantity and minimum-notional behavior;
- time-in-force behavior;
- deterministic random-seed policy when applicable.

The workspace must expose concise human-readable explanations and links to the complete configuration.

## 16. Fill Contract

Required fill fields:

- immutable fill ID;
- order ID;
- fill sequence;
- quantity;
- reference price;
- fill price;
- gross notional;
- spread adjustment;
- slippage adjustment;
- fee amount and fee asset or currency;
- net cash or asset effect;
- eligible market-event reference;
- execution-model version;
- fill timestamp;
- ledger transaction ID;
- resulting order state;
- reconciliation reference.

Partial fills must preserve deterministic order and must never exceed approved quantity.

Missing ledger evidence for a persisted fill is a critical integrity failure.

## 17. Simulated Execution-Cost Presentation

The workspace must distinguish:

- reference price;
- modeled spread;
- modeled slippage;
- execution price;
- fee;
- total modeled execution cost;
- currency or basis-point unit;
- model version;
- limitations.

Costs must be shown as simulation assumptions, not observed exchange execution quality.

A fill using unavailable or stale source evidence must fail closed or be marked invalid according to the persisted domain result.

## 18. Reservation Evidence

Order detail must expose reservation evidence for:

- cash reserved for approved buy notional;
- estimated fees;
- conservative spread or slippage buffer where modeled;
- asset quantity reserved for sell or reduce actions;
- reservation consumption on fill;
- unused reservation release on cancellation or completion.

Required fields:

- reservation ID;
- asset or currency;
- amount;
- reason code;
- order reference;
- ledger transaction or accounting reference;
- creation and release timestamps;
- current status.

A reservation must never be presented as spent or filled value.

## 19. Ledger Explorer

The ledger is the financial source of truth.

The ledger explorer must support:

- deterministic sequence ordering;
- bounded date and sequence filters;
- account-code filters;
- asset or currency filters;
- business-reference filters;
- transaction and entry detail;
- balanced debit and credit presentation;
- links to order, fill, fee, reservation, funding, reversal, and replacement evidence;
- projection-state references;
- authorized export.

Each ledger transaction must show:

- transaction ID;
- ordered portfolio sequence range;
- effective and creation timestamps;
- account codes;
- asset or currency;
- debit and credit amounts;
- reason code or description;
- business reference type and ID;
- correlation or job references where safe;
- accounting-policy version;
- balance-check result.

Ledger entries must never be editable or deletable from the UI.

## 20. Correction and Reversal Lineage

Corrections use new append-only transactions.

The workspace must distinguish:

- original transaction;
- reversing transaction;
- replacement transaction;
- correction reason;
- actor or system source;
- approval or incident reference where required;
- effective and creation timestamps;
- resulting reconciliation outcome.

A correction must not hide or overwrite original evidence.

## 21. Reconciliation Contract

Reconciliation compares at minimum:

- ledger-derived balances;
- persisted balance projections;
- order approved, filled, and remaining totals;
- reservations and releases;
- positions and cost basis;
- fees;
- realized and unrealized P&L where applicable;
- state-version hash;
- last applied ledger sequence;
- rebuilt and persisted projections.

Possible outcomes:

- matched;
- mismatch;
- unable to reconcile.

Every check must expose:

- check code;
- category;
- expected value or hash;
- actual value or hash;
- unit;
- severity;
- outcome;
- supporting references;
- safe explanation.

An unresolved mismatch or inability to reconcile must activate or reference a halt according to domain policy.

## 22. Rebuild Comparison

A rebuild must create a new projection version or comparison artifact without rewriting evidence.

The workspace must show:

- source ledger sequence range;
- source accounting-policy version;
- source valuation references;
- previous projection state and hash;
- rebuilt projection state and hash;
- field-level differences;
- reconciliation outcome;
- generated timestamp;
- halt or incident references.

A matching rebuild confirms reproducibility. It does not delete the original projection or reconciliation history.

## 23. Halt Presentation

Required halt fields:

- halt ID;
- scope;
- source: manual, risk, reconciliation, or integrity;
- canonical reason code;
- safe explanation;
- activated timestamp;
- portfolio or workspace reference;
- related decision, order, fill, ledger, or reconciliation IDs;
- review state;
- terminal or superseding transition.

The UI must not imply that a halt can be bypassed.

Sprint 8 does not add browser controls to clear or override a halt.

## 24. Portfolio and Benchmark Comparison

The portfolio may be compared with approved persisted benchmarks such as:

- unchanged virtual cash;
- buy-and-hold for the same market, time range, and initial capital;
- another approved deterministic baseline.

Comparison requirements:

- identical or explicitly normalized date range;
- explicit initial capital;
- explicit fee and execution assumptions;
- explicit valuation timestamps;
- benchmark version and data hash;
- return, drawdown, fees, exposure, and volatility where persisted;
- no browser-side authoritative metric calculation;
- limitations and non-investment framing.

Benchmark comparison must not present simulated outperformance as a guarantee or recommendation.

## 25. Filtering and History

Portfolio, order, fill, ledger, and reconciliation history may filter by approved bounded fields:

- date range;
- state version;
- ledger sequence range;
- symbol or asset;
- order side and type;
- order state;
- fill presence;
- reason code;
- reconciliation outcome;
- halt state;
- business-reference type;
- accounting or execution-model version.

Filters must be URL-stable where appropriate, server-approved, authorization-aware, and protected from unbounded queries.

## 26. Export Contract

Authorized exports may include:

- portfolio state package;
- order and fill package;
- ledger transaction package;
- ledger sequence-range package;
- reconciliation report;
- benchmark comparison report.

Every export must include:

- schema and generation version;
- portfolio, experiment, and workspace references;
- state-version and ledger-sequence references;
- accounting and execution-model versions;
- timestamps and units;
- reconciliation state;
- simulation disclaimer;
- provenance and integrity hashes where available;
- limitations;
- authorization context without exposing secrets.

Exports must be generated server-side and must not omit critical mismatch or stale-state warnings.

## 27. Page-State Matrix

Explicit states include:

- loading;
- portfolio available;
- no paper portfolio yet;
- empty but valid ledger after initialization rules;
- no positions;
- no orders;
- no fills;
- order pending;
- order open;
- order partially filled;
- order filled;
- order cancelled;
- order rejected;
- stale valuation;
- missing valuation;
- reconciliation matched;
- reconciliation mismatch;
- unable to reconcile;
- missing required ledger evidence;
- projection hash mismatch;
- active halt;
- rebuild in progress;
- rebuild failed;
- schema mismatch;
- unauthorized;
- not found;
- backend unavailable;
- export unavailable.

Integrity, ledger, reconciliation, and stale-valuation failures must not render as ordinary empty states.

## 28. Responsive Behavior

Requirements:

- safety and reconciliation state remains first;
- portfolio totals retain explicit units;
- available and reserved balances remain distinguishable;
- positions and order tables provide semantic narrow-layout alternatives;
- ledger entries preserve debit, credit, account, asset, sequence, and reference meaning;
- long IDs and hashes wrap or copy safely;
- order lifecycle remains chronological;
- no critical evidence is hover-only;
- dense financial tables support horizontal containment without hiding headers or context.

## 29. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- text labels for every state and outcome;
- semantic tables with captions and headers;
- accessible definitions for accounting and execution terms;
- keyboard-accessible filters, disclosures, tabs, and lineage;
- visible focus;
- status announcements for material asynchronous state changes;
- no reliance on color alone;
- correct reading order at desktop, tablet, mobile, and zoomed layouts;
- reduced-motion support;
- safe copy controls for IDs and hashes;
- screen-reader-readable decimal values and units.

## 30. Security and Authority Boundaries

The workspace must not:

- create, modify, or cancel an order;
- create or modify a fill;
- mutate or delete ledger evidence;
- alter a portfolio projection;
- override reconciliation;
- clear a halt;
- accept arbitrary quantity, notional, price, or accounting expressions;
- expose exchange credentials or private provider payloads;
- enable leverage, margin, futures, shorting, or live trading;
- allow AI output to become an execution or accounting command;
- trust browser-calculated authorization, totals, or reconciliation;
- expose stack traces, SQL, tokens, secrets, or unrestricted private financial payloads.

Application authorization, RLS, immutable records, domain invariants, and server-side calculations remain authoritative.

## 31. Privacy and Data Minimization

The UI and telemetry must avoid:

- credentials;
- tokens;
- unrestricted account or provider payloads;
- raw AI prompts;
- unnecessary personal identifiers;
- full ledger descriptions when a safe reason code is sufficient;
- sensitive incident details outside authorized roles.

Exports and diagnostic views must enforce the same authorization and minimization rules as API responses.

## 32. Observability

Safe telemetry may include:

- portfolio endpoint latency and status;
- order counts by safe state and type;
- fill and partial-fill counts;
- cancellation and rejection counts;
- modeled fee, spread, and slippage aggregates without sensitive identifiers;
- ledger posting and balance-check outcomes;
- reconciliation outcome and duration;
- rebuild duration and result;
- stale valuation count;
- active halt count;
- schema compatibility failures;
- export status;
- approved correlation IDs;
- client build version.

Telemetry must not include secrets, raw private financial records, arbitrary ledger descriptions, or raw AI content.

## 33. Testing Strategy

### Contract Tests

Validate schema versions, enums, decimal strings, units, timestamps, nullability, links, state transitions, reason codes, and compatibility behavior.

### Accounting Integration Tests

Validate initial funding, reservations, fills, fees, balanced postings, cost basis, realized and unrealized P&L, equity, exposure, drawdown, state-version creation, and ledger reconstruction.

### Paper-Execution Integration Tests

Validate market and limit orders, next-event behavior, no look-ahead, partial fills, cancellation, precision, minimum notional, fees, spread, slippage, deterministic replay, and unsupported-order rejection.

### Reconciliation Tests

Validate matched, mismatch, unable-to-reconcile, missing-ledger, projection-hash, reservation, fee, position, fill-total, state-version, halt, and rebuild-comparison outcomes.

### Authorization and RLS Tests

Validate workspace isolation and owner, operator, and viewer read permissions. Verify that no browser route creates execution or accounting authority.

### Route and Component Tests

Validate navigation, filters, URL state, state hierarchy, order lifecycle, ledger tables, reconciliation checks, benchmark comparison, diagnostics, and safe errors.

### Property Tests

Validate conservation, balanced transactions, non-negative balances, no short positions, fill quantities within approval, monotonic ledger sequence, deterministic reconstruction, and idempotent replay.

### Accessibility Tests

Validate keyboard flow, headings, landmarks, table semantics, definitions, focus, announcements, copy controls, zoom, reflow, and contrast.

### Visual Regression

Capture empty, active, open-order, partial-fill, filled, cancelled, rejected, stale, halted, matched, mismatch, unable-to-reconcile, rebuild, and schema-error states across themes and viewports.

### Export Tests

Validate deterministic content, provenance, authorization, reconciliation warnings, simulation labeling, prohibited-field absence, and stable hashes where applicable.

## 34. Acceptance Criteria

Sprint 8 documentation is accepted when:

1. the ledger is explicitly the financial source of truth;
2. balances, positions, P&L, equity, exposure, and drawdown are identified as rebuildable projections;
3. requested, approved, ordered, filled, and ledger-posted values remain separate;
4. available and reserved balances remain separate;
5. every order links to an approved deterministic risk evaluation;
6. every fill links to a versioned execution model and balanced ledger transaction;
7. spread, slippage, fees, precision, and minimum-notional assumptions are visible;
8. partial fills, cancellations, rejections, and terminal states are fully specified;
9. reconciliation mismatch and missing ledger evidence fail closed and reference a halt;
10. rebuild comparison never rewrites evidence;
11. benchmark comparison preserves assumptions and limitations;
12. security, privacy, accessibility, observability, and test gates are explicit;
13. no live-trading or browser-side financial authority is introduced.

## 35. Definition of Done

The Sprint 8 specification is complete when:

- this document is committed;
- `SPRINT_8_TASKS.md` is committed;
- terminology matches portfolio, paper trading, strategy, risk, API, database, architecture, security, testing, and observability documents;
- all portfolio, order, fill, ledger, reconciliation, benchmark, export, accessibility, and security states are explicit;
- both commits are fetched and verified.

## 36. Next Sprint Boundary

Sprint 9 defines the **Backtest, Benchmark, Reproducibility, and Experiment Comparison Workspace**, including immutable run configuration, data and code provenance, equity curves, trade lineage, benchmark comparison, robustness evidence, warnings, and non-promotional interpretation.
