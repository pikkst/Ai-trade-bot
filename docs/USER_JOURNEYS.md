# User Journeys

Last reviewed: 2026-07-31  
Status: Authoritative user-flow specification

## 1. Purpose

Define the primary end-to-end journeys for owners, operators, viewers, and prospective users of The Daily Roast AI.

## 2. Roles

- Owner: controls workspace, policies, experiments, and privileged settings.
- Operator: runs research, backtests, and paper operations within approved limits.
- Viewer: inspects reports, portfolio state, and audit history.
- Visitor: evaluates the public product before authentication.

## 3. Journey: Discover the Product

Goal: understand what The Daily Roast AI does and what it does not promise.

Flow:

1. Visitor opens `thedailyroast.online`.
2. Hero explains evidence-driven market intelligence.
3. Visitor reviews methodology, safety model, and paper-trading scope.
4. Visitor sees no profit guarantee or live-trading implication.
5. Visitor selects the demo or sign-in CTA.

Success criteria:

- value proposition is understandable within one screen;
- simulation and research positioning are clear;
- privacy, security, and methodology links are visible.

## 4. Journey: Sign In and Enter the Workspace

1. User authenticates through Supabase Auth.
2. Backend validates identity and role.
3. User is routed to Today.
4. Environment, data freshness, and system status are visible.
5. Unauthorized actions are absent and still blocked server-side.

Failure states:

- expired session;
- invalid credentials;
- disabled account;
- workspace access removed;
- provider unavailable.

## 5. Journey: Review Today's Roast

1. User opens Today.
2. User sees latest completed research cycle.
3. User reviews market regime, key evidence, Gemini analysis, contradictions, and risk state.
4. User opens the full research report.
5. User follows lineage to snapshot, features, strategy, and risk evaluation.

Success criteria:

- data freshness is explicit;
- AI and deterministic evidence are visually separated;
- rejected actions remain inspectable.

## 6. Journey: Inspect a Market

1. User opens Markets.
2. User filters or selects BTC/EUR.
3. User reviews finalized price context, indicators, volatility, and data quality.
4. User opens the latest Gemini analysis.
5. User compares current and previous regime assessments.
6. User opens related strategy and risk decisions.

## 7. Journey: Run a Backtest

1. Operator selects a strategy version.
2. Operator selects symbol, interval, date range, risk policy, and execution assumptions.
3. System validates limits and data availability.
4. Backtest runs asynchronously or as a bounded job.
5. User reviews return, drawdown, fees, benchmark, warnings, and reproducibility metadata.
6. User exports or compares results.

The UI must clearly distinguish in-sample, validation, and test periods when available.

## 8. Journey: Start a Paper Experiment

1. Owner reviews experiment configuration.
2. System validates strategy, risk, data, AI budget, portfolio, and recovery readiness.
3. Owner confirms the experiment is simulated.
4. Configuration is frozen and hashed.
5. Experiment enters Running state.
6. Scheduled cycles update evidence, decisions, and portfolio state.
7. User monitors freshness, halts, and reconciliation.

A failed preflight blocks start and lists exact remediation steps.

## 9. Journey: Investigate a Risk Rejection

1. User opens a rejected decision.
2. Risk outcome and reason code are displayed.
3. Requested and allowed exposure are compared.
4. Relevant thresholds and current portfolio state are shown.
5. User follows links to policy version and market evidence.
6. No manual bypass is offered.

## 10. Journey: Respond to a Halt

1. Critical banner identifies halt scope and trigger.
2. New entry actions are disabled.
3. User reviews evidence, reconciliation, and audit events.
4. Owner follows the recovery runbook.
5. System verifies recovery conditions.
6. Owner explicitly resumes or creates a new experiment when permitted.

## 11. Journey: Review Paper Portfolio

1. User opens Paper Portfolio.
2. User sees virtual cash, equity, exposure, P&L, drawdown, fees, and reconciliation.
3. User inspects positions, orders, fills, and ledger.
4. User compares performance with cash and buy-and-hold.
5. User exports a report.

## 12. Journey: Configure Gemini

1. Owner opens Settings > Gemini.
2. Current provider, model, prompt version, schema version, safety policy, and budgets are shown.
3. Owner creates a draft configuration.
4. System validates supported values and safe limits.
5. Activation is audited and may require a new experiment.

Secrets are never displayed after storage.

## 13. Journey: Mobile Review

Mobile users should be able to:

- review system status;
- inspect the latest roast;
- review a risk decision;
- inspect portfolio summary;
- pause or halt when authorized;
- avoid complex configuration that is unsafe on small screens.

## 14. Journey Testing

Every primary journey requires:

- happy path;
- loading state;
- empty state;
- stale state;
- authorization failure;
- provider failure where relevant;
- mobile viewport;
- keyboard navigation;
- audit verification for state changes.

## 15. Related Documents

- `UI_UX_GUIDELINES.md`
- `INFORMATION_ARCHITECTURE.md`
- `COMPONENT_LIBRARY.md`
- `PRODUCT_REQUIREMENTS.md`
- `SECURITY.md`
