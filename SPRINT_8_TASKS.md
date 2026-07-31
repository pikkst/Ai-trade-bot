# Sprint 8 Tasks — Paper Portfolio, Orders, Fills, Ledger, and Reconciliation Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a read-only, evidence-first workspace that presents the simulated portfolio, paper-order lifecycle, fills, execution assumptions, append-only accounting ledger, projection lineage, benchmark context, and fail-closed reconciliation state without adding live-trading or browser-side financial authority.

## Authoritative References

- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`
- `docs/PORTFOLIO_ENGINE.md`
- `docs/PAPER_TRADING.md`
- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`
- `docs/TODAYS_ROAST_DASHBOARD_IMPLEMENTATION.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `docs/OBSERVABILITY.md`
- `AGENTS.md`

## S8.1 Define Versioned Portfolio Workspace Schemas

### Objective

Create explicit read contracts for portfolio identity, safety state, state versions, balances, positions, performance, exposure, drawdown, valuation, benchmarks, orders, fills, ledger, reconciliation, diagnostics, limitations, and links.

### Work

- define `PaperPortfolioWorkspaceReadModel` and nested schemas;
- define order, fill, ledger-transaction, reconciliation, and rebuild-comparison read models;
- use decimal strings and explicit units for all financial values;
- include schema, accounting-policy, execution-model, valuation, and state versions;
- define compatibility, nullability, freshness, and unavailable-value rules;
- publish schemas in OpenAPI.

### Acceptance Criteria

- no authoritative financial value uses JSON floating point;
- every metric includes unit and relevant version context;
- unavailable, stale, and not-applicable values are distinct;
- compatibility behavior is explicit;
- contract tests pass.

## S8.2 Implement Portfolio Overview Endpoint

### Objective

Expose the complete reconciled portfolio workspace projection.

### Work

- implement `GET /api/v1/paper-portfolios/{portfolio_id}` or the approved workspace projection endpoint;
- return identity, safety state, current state version, balances, positions, performance, exposure, drawdown, valuation, benchmark summaries, open orders, recent fills, ledger summary, and reconciliation;
- enforce application authorization and RLS;
- classify stale, mismatched, halted, and integrity-failure states;
- add safe correlation IDs and latency telemetry.

### Acceptance Criteria

- the same persisted state version produces the same response;
- current and historical state versions cannot be confused;
- reconciliation and freshness state are visible in the contract;
- unauthorized access fails closed;
- integration and abuse tests pass.

## S8.3 Implement Portfolio State History Endpoint

### Objective

Expose immutable portfolio-state versions and their accounting lineage.

### Work

- implement a bounded state-version history endpoint;
- return version, last ledger sequence, state hash, valuation reference, accounting-policy version, timestamp, reconciliation state, and predecessor link;
- support cursor pagination and approved filters;
- preserve historical values;
- expose supersession without mutation.

### Acceptance Criteria

- history is deterministically ordered;
- ledger sequence and state hash are present;
- historical projections remain immutable;
- pagination does not fabricate totals;
- history integration tests pass.

## S8.4 Implement Portfolio Routes and Navigation

### Objective

Add portfolio, order, fill, ledger, and reconciliation routes to the application shell.

### Work

- implement the approved canonical route family;
- add portfolio overview and history routes;
- add order list and detail routes;
- add fill detail route;
- add ledger list and transaction detail routes;
- add reconciliation list and detail routes;
- add cross-links from Today’s Roast, decisions, experiments, backtests, and audit lineage;
- add route-level error boundaries.

### Acceptance Criteria

- routes are directly addressable and keyboard reachable;
- URL state survives refresh where appropriate;
- invalid IDs and filters fail safely;
- no order-creation, cancellation, ledger-edit, or halt-override controls exist;
- route tests pass.

## S8.5 Implement Portfolio Identity and Safety Header

### Objective

Present portfolio, experiment, environment, simulation, state-version, reconciliation, valuation, and halt context before performance interpretation.

### Work

- render portfolio and workspace IDs;
- render experiment reference when applicable;
- render base currency, execution-model version, risk-policy version, state version, and ledger sequence;
- render canonical simulation, freshness, reconciliation, integrity, and halt components;
- expose timestamps in local time with accessible UTC;
- preserve critical state at narrow widths.

### Acceptance Criteria

- simulation is always explicit;
- stale, mismatched, unreconciled, or halted state cannot appear normal;
- state-version and ledger-sequence references are inspectable;
- no positive metric visually overrides critical state;
- responsive and accessibility tests pass.

## S8.6 Implement Reconciled Equity and Benchmark Summary

### Objective

Present high-level portfolio performance with provenance and non-promotional benchmark context.

### Work

- render initial virtual capital and current reconciled equity;
- render gross and net return where persisted;
- render realized and unrealized P&L;
- render cumulative fees, modeled spread, and modeled slippage costs;
- render cash and approved buy-and-hold benchmarks;
- expose period, data hash, version, valuation timestamp, and limitations;
- avoid browser-side authoritative calculations.

### Acceptance Criteria

- every amount and percentage has explicit units;
- benchmark periods and assumptions are comparable or explicitly normalized;
- stale or unreconciled data is labeled;
- outperformance is not framed as a guarantee or recommendation;
- precision and content tests pass.

## S8.7 Implement Available and Reserved Balance Panel

### Objective

Make cash and asset availability, reservation, and ownership state explicit.

### Work

- render available cash by currency;
- render reserved cash by currency;
- render available, reserved, and total asset quantities;
- include state-version, ledger-sequence, and timestamp references;
- explain reservation categories;
- classify negative or inconsistent balances as integrity failures.

### Acceptance Criteria

- available and reserved values cannot be confused;
- totals are server-provided;
- negative balances are critical unless explicitly permitted by versioned policy;
- units and decimal precision are preserved;
- component and integration tests pass.

## S8.8 Implement Position and Cost-Basis Table

### Objective

Present open simulated positions with authoritative accounting and valuation evidence.

### Work

- render asset or symbol, quantity, reserved quantity, cost basis, average cost, mark price, market value, realized P&L, unrealized P&L, and fees;
- display accounting-policy method and version;
- display valuation source, timestamp, and freshness;
- link to fills and ledger transactions;
- provide semantic mobile row details.

### Acceptance Criteria

- the cost-basis method is named;
- frontend performs no cost-basis or P&L calculation;
- stale or missing valuation is explicit;
- no short or negative quantity appears as normal;
- table accessibility tests pass.

## S8.9 Implement Exposure and Drawdown Section

### Objective

Show reconciled exposure and drawdown against active policy limits.

### Work

- render gross and net exposure;
- render current position and reserved-order exposure;
- render persisted projected exposure when available;
- render high-water mark, daily reference equity, daily drawdown, and total drawdown;
- render applicable maximums and halt thresholds;
- render reset timezone and timestamp;
- link to risk policy and active halt.

### Acceptance Criteria

- frontend performs no final exposure or drawdown calculation;
- current values and thresholds remain distinct;
- breached or unavailable limits fail closed;
- division-by-zero or missing-reference states are explicit;
- unit and state-matrix tests pass.

## S8.10 Implement Paper Order List Endpoint

### Objective

Expose bounded, filterable paper-order history.

### Work

- implement a portfolio-scoped order list endpoint;
- support approved filters for date, symbol, side, type, state, fill presence, reason code, decision, execution model, and reconciliation;
- use cursor pagination;
- include requested, approved, filled, and remaining summaries;
- enforce authorization and safe sort options;
- add result-count and latency telemetry.

### Acceptance Criteria

- order history is deterministically ordered;
- requested, approved, filled, and remaining values remain separate;
- filters are bounded and server-approved;
- unauthorized orders are not exposed;
- endpoint tests pass.

## S8.11 Implement Paper Order Detail Endpoint

### Objective

Return the complete persisted order lifecycle and accounting linkage.

### Work

- implement `GET /api/v1/paper-orders/{order_id}` or the approved projection endpoint;
- return identity, approved decision, requested and approved values, precision-adjusted values, lifecycle, execution model, fills, reservations, totals, ledger references, reconciliation, diagnostics, and links;
- classify missing required decision, fill, or ledger lineage;
- map errors safely;
- add correlation IDs.

### Acceptance Criteria

- a risk approval is not presented as an order or fill;
- terminal order history remains immutable;
- missing optional fill evidence is distinct from missing required ledger evidence;
- duplicate identities are rejected by the domain;
- integration tests cover every order state.

## S8.12 Implement Order Lifecycle Timeline

### Objective

Present deterministic order state transitions and reasons.

### Work

- render pending, open, partially filled, filled, cancelled, and rejected transitions;
- render timestamps, actors or system source, reason codes, and evidence links;
- distinguish current and terminal state;
- show remaining quantity after partial fills or cancellation;
- sanitize all reason text.

### Acceptance Criteria

- transitions remain chronological;
- terminal states cannot appear mutable;
- partial-fill progression is understandable without color;
- cancellation never appears to reverse completed fills;
- lifecycle accessibility tests pass.

## S8.13 Implement Requested, Approved, Ordered, Filled, and Remaining Comparison

### Objective

Prevent value conflation across strategy, risk, execution, and accounting stages.

### Work

- render strategy-requested exposure;
- render risk-approved quantity and notional;
- render order values after precision and minimum-notional rules;
- render cumulative filled and remaining values;
- render ledger-posted cash and asset effects;
- render explicit units, statuses, and reason codes.

### Acceptance Criteria

- each stage is visually and programmatically distinct;
- reductions and rejections identify their cause;
- filled quantity never exceeds approved quantity;
- frontend derives no authoritative totals;
- precision and boundary tests pass.

## S8.14 Implement Execution-Model Evidence Panel

### Objective

Expose the assumptions that produced simulated execution.

### Work

- render execution-model name, version, and hash;
- render reference-price and next-event rules;
- render market and limit fill rules;
- render spread, slippage, fee, participation, partial-fill, intrabar, precision, minimum-notional, and time-in-force assumptions;
- render deterministic seed policy where applicable;
- link to complete immutable configuration.

### Acceptance Criteria

- no execution assumption is implicit;
- same-candle look-ahead is explicitly prohibited;
- unavailable model evidence is critical;
- assumptions are labeled simulated rather than observed;
- contract and content tests pass.

## S8.15 Implement Fill Detail and Cost Breakdown

### Objective

Present each simulated fill and its complete financial effect.

### Work

- render fill ID, sequence, quantity, reference price, fill price, notional, spread, slippage, fee, net effect, eligible market event, model version, timestamp, order result, ledger transaction, and reconciliation;
- distinguish fee asset or currency;
- expose partial-fill sequence;
- link to market evidence and accounting evidence;
- classify missing ledger evidence as critical.

### Acceptance Criteria

- fill sequence is deterministic;
- spread, slippage, fee, and total modeled cost remain separate;
- partial fills never exceed remaining approval;
- missing required accounting evidence fails closed;
- fill integration tests pass.

## S8.16 Implement Reservation Evidence Panel

### Objective

Show how cash or asset quantities were reserved, consumed, and released.

### Work

- render reservation ID, asset or currency, amount, reason, order, status, creation, consumption, and release timestamps;
- distinguish notional, fee, buffer, and asset reservations;
- link to ledger or accounting references;
- explain unused release on completion or cancellation;
- classify orphaned reservations.

### Acceptance Criteria

- reservation is never presented as a fill or expense;
- every active reservation links to an eligible order;
- released and consumed amounts are explicit;
- orphaned or over-reserved state is critical;
- accounting tests pass.

## S8.17 Implement Ledger List Endpoint and Explorer

### Objective

Expose immutable, deterministically ordered financial evidence.

### Work

- implement `GET /api/v1/paper-portfolios/{portfolio_id}/ledger` with approved filters;
- support cursor pagination by ledger sequence;
- implement transaction detail projection;
- render account code, asset or currency, debit, credit, reason, business reference, effective time, creation time, sequence, policy version, and balance-check result;
- link to orders, fills, fees, reservations, funding, reversals, replacements, projections, and reconciliations;
- enforce authorization and RLS.

### Acceptance Criteria

- ledger sequence is unique and monotonic per portfolio;
- each entry has exactly one positive debit or credit according to the contract;
- every transaction exposes a balance-check result;
- entries cannot be edited or deleted;
- API, integration, and table tests pass.

## S8.18 Implement Ledger Transaction and Correction Lineage

### Objective

Present balanced transactions and append-only correction evidence.

### Work

- group ledger entries by transaction ID;
- render debit and credit totals by accounting unit;
- render original, reversing, and replacement transaction links;
- render correction reason, source, timestamps, and incident or approval reference where applicable;
- render resulting projection and reconciliation references;
- sanitize descriptions.

### Acceptance Criteria

- every displayed transaction balances or is marked as a critical invariant failure;
- original evidence is never hidden;
- reversal and replacement remain separate transactions;
- corrections never mutate prior entries;
- lineage and invariant tests pass.

## S8.19 Implement Reconciliation Endpoints and Workspace

### Objective

Expose matched, mismatch, and unable-to-reconcile outcomes with complete evidence.

### Work

- implement reconciliation list and detail endpoints;
- return run identity, compared state, ledger-derived state, persisted projection, check results, mismatch reasons, halt, rebuild comparison, diagnostics, and links;
- compare balances, orders, fills, reservations, positions, cost basis, fees, P&L, state hash, and ledger sequence;
- classify unavailable or corrupted evidence;
- add safe telemetry.

### Acceptance Criteria

- matched, mismatch, and unable-to-reconcile are distinct;
- every mismatch has machine-readable reason codes;
- unresolved mismatch references a halt;
- missing evidence does not appear as matched or empty;
- reconciliation integration tests pass.

## S8.20 Implement Rebuild Comparison

### Objective

Demonstrate deterministic reconstruction without rewriting financial evidence.

### Work

- render source ledger range, accounting-policy version, valuation references, prior projection, rebuilt projection, hashes, differences, timestamp, and outcome;
- preserve original projection and reconciliation history;
- label rebuild as comparison or new projection version;
- classify incompatible or incomplete rebuild inputs;
- link to halt and incident evidence.

### Acceptance Criteria

- rebuild never overwrites the original state;
- equal input evidence produces deterministic results;
- field differences are explicit;
- incomplete evidence fails closed;
- reconstruction and comparison tests pass.

## S8.21 Implement Benchmark Comparison

### Objective

Compare the simulated portfolio with approved persisted baselines without promotional claims.

### Work

- render cash, buy-and-hold, and approved deterministic benchmarks;
- expose initial capital, period, data hash, fee and execution assumptions, valuation timestamps, metric versions, and limitations;
- render return, drawdown, fees, exposure, turnover, and volatility where persisted;
- support direct links to backtest or experiment evidence;
- prohibit browser-side authoritative calculations.

### Acceptance Criteria

- benchmark assumptions are visible;
- periods are identical or explicitly normalized;
- simulated outperformance is not framed as expected future performance;
- stale or incomparable benchmarks are labeled;
- comparison tests pass.

## S8.22 Implement Authorized Export

### Objective

Generate provenance-preserving portfolio, order, fill, ledger, reconciliation, and benchmark packages.

### Work

- support approved structured JSON and human-readable formats;
- generate exports server-side;
- include schema, portfolio, experiment, state-version, ledger-sequence, accounting-policy, execution-model, valuation, timestamps, units, reconciliation, provenance, limitations, and simulation disclaimer;
- preserve mismatch and stale-state warnings;
- enforce authorization and RLS;
- record safe telemetry.

### Acceptance Criteria

- the same resource and format produce deterministic content where required;
- provenance and reconciliation state cannot be omitted;
- no secret or unrestricted private payload appears;
- simulation labeling remains explicit;
- export tests pass.

## S8.23 Add Explicit State Handling

### Objective

Define safe rendering for every portfolio and execution state.

### Work

- implement loading, no portfolio, initialized empty ledger, no positions, no orders, no fills, every order state, stale valuation, missing valuation, reconciliation matched, mismatch, unable to reconcile, missing ledger evidence, projection mismatch, halt, rebuild, schema mismatch, unauthorized, not found, backend unavailable, and export failure states;
- define bounded retry policy;
- prevent infinite retries;
- preserve safe cached data only when policy allows and label it stale.

### Acceptance Criteria

- integrity and reconciliation failures never appear empty;
- loading fabricates no balances or performance;
- retry is offered only when safe;
- cached data is visibly stale;
- state-matrix tests pass.

## S8.24 Add Responsive and Accessibility Verification

### Objective

Ensure dense financial evidence remains usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom layouts;
- test headings, landmarks, focus, keyboard operation, tables, definitions, lifecycle, ledger grouping, reconciliation checks, benchmarks, and copy controls;
- verify decimal and unit announcements;
- test reduced motion and contrast;
- record screen-reader spot checks;
- test long IDs, hashes, account codes, and reason codes.

### Acceptance Criteria

- no critical evidence is hover-only;
- no state relies only on color;
- table context remains available at narrow widths;
- critical content is not clipped;
- no critical automated violation remains;
- manual evidence is recorded.

## S8.25 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make ledger integrity, reconciliation, and read-only authority release-blocking.

### Work

- add contract, accounting, execution, reconciliation, property, route, E2E, accessibility, visual, export, authorization, and RLS tests;
- add hostile-text sanitization and secret scans;
- verify no browser mutation, execution, ledger-edit, reconciliation-override, or halt-clear path exists;
- instrument safe portfolio, order, fill, ledger, reconciliation, rebuild, stale-valuation, halt, schema, and export metrics;
- test prohibited telemetry fields;
- verify normal CI uses deterministic fixtures and no private exchange credentials.

### Acceptance Criteria

- accounting invariants and deterministic reconstruction pass;
- unauthorized access fails closed;
- no AI or browser path can mutate execution or accounting state;
- telemetry contains no prohibited fields;
- visual changes require review;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| API contracts | OpenAPI, schema, enum, decimal, unit, timestamp, link, and compatibility tests |
| Portfolio | State-version, balance, position, cost-basis, P&L, equity, exposure, drawdown, and valuation tests |
| Orders | Requested, approved, ordered, filled, remaining, lifecycle, idempotency, and terminal-state tests |
| Execution | Next-event, no-look-ahead, spread, slippage, fee, precision, minimum-notional, partial-fill, and model-version tests |
| Ledger | Balanced transaction, monotonic sequence, append-only, reservation, fee, funding, reversal, and replacement tests |
| Reconciliation | Matched, mismatch, unable, missing-evidence, state-hash, ledger-sequence, halt, and rebuild tests |
| Benchmarks | Period, data hash, assumptions, metric version, limitation, and non-promotional content tests |
| Accessibility | Keyboard, tables, definitions, lifecycle, ledger, reconciliation, zoom, reflow, and manual review |
| Security and privacy | RLS, authorization, sanitization, no-mutation, no-live-trading, secret scan, and telemetry-field tests |

## Sprint Exit Gate

Sprint 8 is complete only when:

- S8.1 through S8.25 are implemented and verified;
- ledger evidence is the explicit financial source of truth;
- balances, positions, P&L, equity, exposure, and drawdown remain rebuildable projections;
- requested, approved, ordered, filled, remaining, reserved, and ledger-posted values remain separate;
- every order links to an approved deterministic risk evaluation;
- every fill links to immutable market evidence, an execution-model version, and balanced ledger evidence;
- every state version identifies its last ledger sequence and state hash;
- reconciliation mismatches, missing evidence, and stale valuations fail closed;
- rebuild comparison preserves original evidence;
- benchmarks preserve assumptions, provenance, limitations, and non-promotional framing;
- no browser or AI execution, accounting, reconciliation-override, ledger-edit, halt-clear, or live-trading authority exists;
- accessibility, responsive, security, privacy, contract, accounting, execution, reconciliation, property, E2E, export, benchmark, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 9 defines and implements the Backtest, Benchmark, Reproducibility, and Experiment Comparison Workspace.
