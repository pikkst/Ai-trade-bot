# The Daily Roast AI Product Requirements

Last reviewed: 2026-07-31  
Status: Authoritative MVP product specification

## 1. Purpose

The Daily Roast AI is an evidence-driven market-intelligence, backtesting, paper-trading, and Gemini-assisted decision-support platform.

The first implementation focuses on cryptocurrency markets and must prove that market data, deterministic features, Google Gemini analysis, deterministic strategy rules, deterministic risk controls, simulated execution, accounting, and reporting can operate together safely and reproducibly.

The MVP is a research system. It is not a live-trading product, financial adviser, broker, exchange, custody service, or guarantee of profit.

## 2. Product Identity

- Official product name: **The Daily Roast AI**
- Official tagline: **Evidence-Driven Market Intelligence**
- Primary domain: `thedailyroast.online`
- Application domain: `app.thedailyroast.online`
- API domain: `api.thedailyroast.online`

The repository name `Ai-trade-bot` is a technical legacy identifier. User-facing product content MUST use the official product name.

## 3. Product Vision

Provide a transparent environment where users can inspect market evidence, compare deterministic and Gemini-assisted analysis, test hypotheses, simulate decisions with realistic costs, understand risk, and trace every conclusion back to its source data.

The long-term product vision is broader than cryptocurrency trading. The architecture should support later research expansion to equities, ETFs, foreign exchange, commodities, and macroeconomic data through audited adapters and market-specific requirements.

## 4. Product Principles

1. Evidence over hype.
2. Research before execution.
3. Safety before automation.
4. Deterministic controls around probabilistic AI output.
5. Explainability before performance claims.
6. Reproducibility before optimization.
7. Complete lineage from source data to report and simulated fill.
8. Conservative assumptions for ambiguous market behavior.
9. Human control over material decisions.
10. Documentation, tests, and behavior change together.
11. No hidden manual overrides.
12. No guaranteed-return, urgency, or fear-of-missing-out language.

## 5. Target Users

### 5.1 Owner

Configures workspaces, risk policy, experiment settings, AI budgets, domains, and halt controls. May approve future progression to a Binance test environment.

### 5.2 Operator

Runs backfills, analyses, backtests, and paper experiments; investigates failures; cannot weaken owner-approved risk policy.

### 5.3 Viewer

Reads market reports, portfolio state, experiment results, and audit history; cannot mutate financial or control state.

### 5.4 Future Research User

Uses evidence, scenarios, watchlists, backtests, and paper portfolios without needing direct execution capability.

### 5.5 AI Coding Agent

Implements one task at a time under `/AGENTS.md` and the applicable task file. It has no authority to change product scope, brand identity, or prohibited capabilities.

## 6. MVP Goals

- Ingest and validate Binance Spot public market data.
- Produce immutable market snapshots and versioned deterministic indicators.
- Generate schema-valid Google Gemini market-analysis reports.
- Compare Gemini recommendations with deterministic strategy output.
- Route every actionable strategy intent through deterministic risk evaluation.
- Simulate market and limit orders with fees, spread, slippage, precision, minimum-notional checks, and partial fills.
- Maintain an append-only portfolio ledger and reconcile all derived balances.
- Run reproducible backtests with cash and buy-and-hold benchmarks.
- Execute a controlled 30-day paper experiment starting with EUR 20 virtual capital.
- Preserve audit evidence for every material operation and decision.
- Expose health, freshness, uncertainty, provenance, risk, and halt state clearly.
- Deploy a branded public demo through `thedailyroast.online` without requiring the owner's local computer to remain online.

## 7. Explicit Non-Goals for MVP

The MVP must not include:

- live trading;
- private Binance order placement;
- withdrawals or custody;
- futures, perpetuals, margin, leverage, options, or short selling;
- HFT, latency arbitrage, market making, or cross-exchange arbitrage;
- copy trading or social trading;
- autonomous prompt or strategy self-modification;
- AI-selected credentials, risk policy, or final position sizing;
- profitability guarantees or marketing claims based only on backtests;
- deceptive urgency or get-rich-quick messaging;
- public multi-tenant billing or SaaS launch;
- unsupported non-crypto market adapters.

## 8. Primary User Journeys

### 8.1 Open Today's Roast

The user sees the latest market regime, data freshness, key evidence, contradictions, Gemini analysis status, deterministic strategy intent, risk state, and simulation status.

### 8.2 Configure a Research Workspace

The owner creates a workspace, chooses allowed symbols and intervals, selects the Gemini model through configuration, sets AI budgets, selects strategy and risk-policy versions, and defines the virtual starting balance.

### 8.3 Inspect Market Analysis

The operator requests analysis for an immutable market snapshot. The system displays deterministic indicators, data quality, Gemini report, validation result, strategy intent, risk decision, uncertainty, and evidence references.

### 8.4 Run a Backtest

The operator chooses a data range, strategy version, risk-policy version, fee model, slippage model, and starting capital. The system returns metrics, warnings, equity curve, trade ledger, and benchmark comparisons.

### 8.5 Start a Paper Experiment

The owner freezes an experiment configuration. The system verifies readiness, seeds the virtual balance, runs scheduled analysis and simulated execution, and records every state transition.

### 8.6 Investigate a Decision

The user can trace a simulated fill back through order, approved risk evaluation, strategy intent, validated Gemini report, feature-set version, market snapshot, and source candles.

### 8.7 Halt the System

The owner or an automatic safety rule can halt a portfolio or workspace. New entries stop immediately. Existing state remains readable and auditable.

## 9. Functional Requirements

### 9.1 Identity and Authorization

- PRD-AUTH-001: The API MUST authenticate users before protected operations.
- PRD-AUTH-002: The system MUST enforce owner, operator, and viewer permissions server-side.
- PRD-AUTH-003: Every state-changing action MUST record actor, timestamp, correlation ID, and result.
- PRD-AUTH-004: Authorization failures MUST use stable machine-readable error codes.
- PRD-AUTH-005: Browser access MUST be deny-by-default through RLS and application authorization.

### 9.2 Brand and Content

- PRD-BRAND-001: User-facing content MUST use **The Daily Roast AI**.
- PRD-BRAND-002: The official tagline is **Evidence-Driven Market Intelligence**.
- PRD-BRAND-003: AI confidence MUST NOT be presented as probability of profit.
- PRD-BRAND-004: Paper trades and simulated performance MUST be labeled explicitly.
- PRD-BRAND-005: Product content MUST NOT guarantee profit, create artificial urgency, or use hype-driven financial language.
- PRD-BRAND-006: Risk, uncertainty, data freshness, and provenance MUST remain visible in material decision views.

### 9.3 Configuration

- PRD-CFG-001: Configuration MUST be validated at startup.
- PRD-CFG-002: Secrets MUST come from environment variables or an approved secret manager.
- PRD-CFG-003: Experiment, strategy, risk, prompt, schema, provider, and model configuration MUST be versioned.
- PRD-CFG-004: A frozen experiment configuration MUST be immutable.
- PRD-CFG-005: `LIVE_TRADING_ENABLED` MUST default to `false` and MUST NOT activate live execution in the MVP.

### 9.4 Market Data

- PRD-MD-001: Ingest Binance Spot symbol metadata and finalized OHLCV candles.
- PRD-MD-002: Normalize symbols to `BASE/QUOTE` while retaining exchange-native identifiers.
- PRD-MD-003: Detect missing, duplicate, stale, invalid, and out-of-order candles.
- PRD-MD-004: Respect Binance rate limits and retry guidance.
- PRD-MD-005: The free-cloud MVP MUST use finalized REST polling and idempotent gap repair.
- PRD-MD-006: Finalized candles MUST be immutable; corrections create explicit quality and replacement records.
- PRD-MD-007: Strategies and AI may use only data that satisfies freshness and quality policy.
- PRD-MD-008: Every user-facing report MUST expose its snapshot timestamp and freshness state.

### 9.5 Feature Engineering

- PRD-FEAT-001: Calculate versioned returns, SMA, EMA, RSI, ATR, volatility, and volume features.
- PRD-FEAT-002: Identical inputs and versions MUST produce identical outputs.
- PRD-FEAT-003: Feature outputs MUST reference immutable source snapshots.
- PRD-FEAT-004: Feature-set input and output hashes MUST be stored.

### 9.6 Google Gemini Analysis

- PRD-AI-001: Google Gemini API is the required cloud AI provider for MVP.
- PRD-AI-002: Provider SDK types MUST remain inside the Gemini infrastructure adapter.
- PRD-AI-003: Gemini MUST receive only minimum required structured evidence.
- PRD-AI-004: Gemini MUST return a project-owned structured report schema.
- PRD-AI-005: Malformed, incomplete, stale, unsupported, safety-blocked, or policy-violating output MUST be rejected.
- PRD-AI-006: Gemini confidence represents analytical classification confidence, not probability of profit.
- PRD-AI-007: The system MUST record model identifier, prompt version, schema version, request ID, latency, usage, status, retry count, and cost estimate.
- PRD-AI-008: Gemini MUST NOT receive execution, shell, database mutation, credential, or risk-policy tools.
- PRD-AI-009: Provider failure degrades to deterministic analysis or HOLD; it MUST NOT open a position.
- PRD-AI-010: AI budgets MUST be enforced before a request is made.
- PRD-AI-011: User-facing Gemini summaries MUST follow the brand voice and unsupported-claim policy.

### 9.7 Strategy

- PRD-STRAT-001: Strategies MUST be deterministic for identical inputs and versions.
- PRD-STRAT-002: Strategy output is a typed intent: HOLD, ENTER, EXIT, or REDUCE.
- PRD-STRAT-003: Strategies MUST NOT create orders directly.
- PRD-STRAT-004: Every intent MUST reference market snapshot, feature-set version, strategy version, and configuration hash.
- PRD-STRAT-005: Backtesting and paper trading MUST use the same strategy contract.

### 9.8 Risk

- PRD-RISK-001: Every non-HOLD intent MUST pass the deterministic risk engine.
- PRD-RISK-002: Risk outcomes are approve, approve-with-reduced-size, reject, halt-portfolio, or halt-workspace.
- PRD-RISK-003: Required controls include position, order notional, exposure, daily drawdown, total drawdown, stale data, volatility, cooldown, open-order, duplicate, precision, and minimum-notional checks.
- PRD-RISK-004: Missing or invalid risk configuration MUST fail closed.
- PRD-RISK-005: Reconciliation mismatch MUST halt new simulated trading activity.
- PRD-RISK-006: No undocumented bypass switch is permitted.

### 9.9 Paper Execution

- PRD-EXEC-001: Support simulated market and limit orders and cancellation.
- PRD-EXEC-002: Apply explicit versioned fee, spread, slippage, precision, and partial-fill models.
- PRD-EXEC-003: Ambiguous intrabar ordering MUST resolve conservatively.
- PRD-EXEC-004: One approved risk evaluation may create at most one paper order.
- PRD-EXEC-005: Duplicate commands MUST return the original result or a deterministic conflict.
- PRD-EXEC-006: Every order, fill, P&L value, and report MUST identify itself as simulated.

### 9.10 Portfolio and Accounting

- PRD-PORT-001: The append-only double-entry ledger is the financial source of truth.
- PRD-PORT-002: Monetary values use decimal arithmetic and explicit currency.
- PRD-PORT-003: Fills and corresponding ledger entries MUST be committed atomically.
- PRD-PORT-004: Derived cash, reserved funds, positions, fees, P&L, equity, exposure, and drawdown MUST reconcile to the ledger.
- PRD-PORT-005: Failed reconciliation MUST create a critical audit event and halt.

### 9.11 Backtesting

- PRD-BT-001: Backtests MUST prohibit look-ahead and use finalized historical data.
- PRD-BT-002: Fees and slippage are mandatory.
- PRD-BT-003: Results MUST compare against cash and buy-and-hold benchmarks.
- PRD-BT-004: Runs MUST store code commit, data hash, strategy version, risk-policy version, configuration hash, dependencies, and random seed.
- PRD-BT-005: Results MUST include return, drawdown, volatility, Sharpe, Sortino, win rate, profit factor, exposure, turnover, fees, and trade count.
- PRD-BT-006: Backtest presentation MUST disclose assumptions and MUST NOT imply future performance.

### 9.12 API and Reporting

- PRD-API-001: Public APIs use `/api/v1`.
- PRD-API-002: State-changing commands require idempotency where repetition can duplicate effects.
- PRD-API-003: Lists MUST be paginated.
- PRD-API-004: Errors MUST contain stable code and correlation ID without exposing secrets or stack traces.
- PRD-API-005: Users MUST be able to export experiment results in JSON and CSV.
- PRD-API-006: Audit queries MUST support filtering by actor, entity, event type, status, and time range.

### 9.13 Operations and Cloud Deployment

- PRD-OPS-001: Expose liveness and readiness health endpoints.
- PRD-OPS-002: Emit structured logs and persist cycle, audit, freshness, halt, and reconciliation status.
- PRD-OPS-003: Critical alerts MUST have documented runbooks before production research launch.
- PRD-OPS-004: Scheduled research cycles MUST be retryable, observable, and idempotent.
- PRD-OPS-005: Database or ledger integrity failure MUST stop side effects.
- PRD-OPS-006: The public demo MUST use `thedailyroast.online` and approved subdomains.
- PRD-OPS-007: Free-tier cold starts, pauses, throttling, and schedule delays MUST degrade safely.

## 10. Non-Functional Requirements

### 10.1 Reliability

- Restarting API or scheduled workflows MUST NOT duplicate orders, fills, ledger entries, or analysis records.
- No network call may occur inside a database transaction.
- Scheduled work MUST use deterministic idempotency keys and a database lease or advisory lock.

### 10.2 Performance

Initial design targets, subject to measurement:

- normal read API p95 below 500 ms after warm-up in the demo environment;
- command acknowledgement p95 below 750 ms excluding external provider completion;
- one research cycle completes within the configured GitHub Actions timeout;
- readiness fails when PostgreSQL is unavailable or mandatory migrations are missing.

Free-tier cold-start latency is reported separately and is not hidden.

### 10.3 Security

- No secret in source, logs, metrics, prompts, responses, or client bundles.
- CI MUST run secret, dependency, static-code, and container or filesystem scanning where applicable.
- Private exchange credentials are out of MVP scope.
- Gemini API keys MUST be environment-separated and rotatable.
- Browser roles MUST NOT write directly to financial or control tables.

### 10.4 Privacy

- Do not send personal data or secrets to Gemini.
- Store only data required for operation and audit.
- Retention periods MUST be configurable where legally necessary.

### 10.5 Maintainability

- Strict typing is required in backend and frontend application code.
- Public behavior requires tests and documentation in the same pull request.
- Provider, exchange, clock, persistence, and scheduling boundaries use project-owned protocols.
- Naming follows `NAMING_CONVENTIONS.md`.

### 10.6 Accessibility and Trust

Primary UI workflows MUST support keyboard navigation, readable contrast, explicit status labels, and non-color-only indication of risk or mode.

The interface MUST keep simulation mode, data freshness, uncertainty, evidence provenance, and halt state visible.

## 11. Controlled EUR 20 Experiment

The first formal paper experiment uses:

- virtual starting balance: EUR 20;
- primary symbol: BTC/EUR;
- optional observation-only symbols: ETH/EUR and SOL/EUR;
- no leverage and no shorting;
- maximum position: 25% of equity;
- maximum single order: EUR 5 equivalent, subject to simulation constraints;
- maximum daily drawdown before halt: 5%;
- maximum total drawdown before halt: 15%;
- one open order maximum;
- fees and slippage enabled;
- cash and buy-and-hold benchmarks;
- owner-approved frozen configuration;
- 30 calendar days or a documented early halt.

## 12. Success Metrics

The MVP is successful when it demonstrates:

- complete and valid market data for the experiment window;
- zero duplicate fills or ledger entries;
- zero unresolved reconciliation mismatches;
- 100% lineage coverage for analysis and simulated actions;
- schema-valid Gemini response rate measured and reported;
- every rejected Gemini output safely handled;
- all risk halts and rejections correctly enforced;
- reproducible backtest results for identical inputs;
- experiment report generated without manual database repair;
- users can identify evidence, uncertainty, freshness, risk, and simulation state;
- public product surfaces use the approved brand consistently.

Profit is not an MVP acceptance criterion.

## 13. MVP Definition of Done

The MVP is complete only when:

1. all required P0 tasks are completed and verified;
2. required experiment tasks are completed;
3. CI quality, security, documentation, and brand checks pass;
4. migrations, RLS, export, and recovery tests pass;
5. all state-changing paths are idempotent;
6. decision and financial lineage are complete;
7. the 30-day paper experiment finishes or halts for a documented safety reason;
8. a final report compares the system with cash and buy-and-hold;
9. documentation reflects the actual implementation;
10. no document or feature implies live trading is enabled;
11. public domains, UI, reports, and metadata use The Daily Roast AI identity.

## 14. Related Documents

- `/AGENTS.md`
- `/TASKS.md`
- `/CLOUD_MVP_TASKS.md`
- `/LOCAL_AND_PRODUCTION_TASKS.md`
- `BRAND_GUIDELINES.md`
- `PRODUCT_VISION.md`
- `MISSION_AND_VALUES.md`
- `DESIGN_PRINCIPLES.md`
- `NAMING_CONVENTIONS.md`
- `ARCHITECTURE.md`
- `AI_ARCHITECTURE.md`
- `GEMINI_INTEGRATION.md`
- `STRATEGY_ENGINE.md`
- `RISK_ENGINE.md`
- `PAPER_TRADING.md`
- `PORTFOLIO_ENGINE.md`
- `BACKTEST_ENGINE.md`
- `SECURITY.md`
- `TESTING.md`
