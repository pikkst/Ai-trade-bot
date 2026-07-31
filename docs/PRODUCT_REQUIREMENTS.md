# Product Requirements

Last reviewed: 2026-07-31
Status: Authoritative MVP specification

## 1. Purpose

AI Trade Bot is a cryptocurrency research, backtesting, paper-trading, and AI decision-support platform. The first version must prove that market data, deterministic features, Google Gemini analysis, deterministic strategy rules, deterministic risk controls, simulated execution, accounting, and reporting can operate together safely and reproducibly.

The MVP is a research system. It is not a live trading product, financial adviser, custody service, exchange, broker, or guarantee of profit.

## 2. Product Vision

Provide a transparent environment where a user can inspect market evidence, compare deterministic and Gemini-assisted analysis, run reproducible backtests, simulate trades with realistic costs, understand every decision, and evaluate whether further sandbox testing is justified.

## 3. Product Principles

1. Safety before automation.
2. Deterministic controls around probabilistic AI output.
3. Explainability before performance claims.
4. Reproducibility before optimization.
5. Complete lineage from source data to report and simulated fill.
6. Conservative assumptions for ambiguous market behavior.
7. Documentation and tests change together with behavior.
8. No hidden manual overrides.

## 4. Target Users

### 4.1 Owner

Configures workspaces, risk policy, experiment settings, AI budgets, and halt controls. May approve future progression to Binance sandbox.

### 4.2 Operator

Runs backfills, analyses, backtests, and paper experiments; investigates failures; cannot weaken owner-approved risk policy.

### 4.3 Viewer

Reads reports, portfolio state, experiment results, and audit history; cannot mutate trading or configuration state.

### 4.4 AI Coding Agent

Implements one task at a time under `/AGENTS.md` and `TASKS.md`. It has no authority to change product scope or enable prohibited capabilities.

## 5. MVP Goals

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
- Expose health, metrics, dashboards, and halt controls.

## 6. Explicit Non-Goals for MVP

The MVP must not include:

- live trading;
- private Binance order placement;
- withdrawals or custody;
- futures, perpetuals, margin, leverage, options, or short selling;
- HFT, latency arbitrage, market making, or cross-exchange arbitrage;
- copy trading or social trading;
- autonomous prompt or strategy self-modification;
- AI-selected credentials, risk policy, or position sizing;
- profitability guarantees or marketing claims based only on backtests;
- multi-tenant billing or public SaaS launch.

## 7. Primary User Journeys

### 7.1 Configure a Research Workspace

The owner creates a workspace, chooses allowed symbols and intervals, selects the Gemini model through configuration, sets AI budgets, selects strategy and risk-policy versions, and defines the virtual starting balance.

### 7.2 Inspect Market Analysis

The operator requests analysis for an immutable market snapshot. The system displays deterministic indicators, data quality, Gemini report, validation result, strategy intent, risk decision, and evidence references.

### 7.3 Run a Backtest

The operator chooses a data range, strategy version, risk-policy version, fee model, slippage model, and starting capital. The system returns metrics, warnings, equity curve, trade ledger, and benchmark comparisons.

### 7.4 Start a Paper Experiment

The owner freezes an experiment configuration. The system verifies readiness, seeds the virtual balance, runs scheduled analysis and simulated execution, and records every state transition.

### 7.5 Investigate a Decision

The user can trace a simulated fill back through order, approved risk evaluation, strategy intent, validated Gemini report, feature-set version, market snapshot, and source candles.

### 7.6 Halt the System

The owner or an automatic safety rule can halt a portfolio or workspace. New entries stop immediately. Existing state remains readable and auditable.

## 8. Functional Requirements

### 8.1 Identity and Authorization

- PRD-AUTH-001: The API must authenticate users before protected operations.
- PRD-AUTH-002: The system must enforce owner, operator, and viewer permissions server-side.
- PRD-AUTH-003: Every state-changing action must record actor, timestamp, correlation ID, and result.
- PRD-AUTH-004: Authorization failures must use stable machine-readable error codes.

### 8.2 Configuration

- PRD-CFG-001: Configuration must be validated at startup.
- PRD-CFG-002: Secrets must come from environment variables or an approved secret manager.
- PRD-CFG-003: Experiment, strategy, risk, prompt, schema, provider, and model configuration must be versioned.
- PRD-CFG-004: A frozen experiment configuration must be immutable.
- PRD-CFG-005: `LIVE_TRADING_ENABLED` must default to `false` and must not activate live execution in the MVP.

### 8.3 Market Data

- PRD-MD-001: Ingest Binance Spot symbol metadata and finalized OHLCV candles.
- PRD-MD-002: Normalize symbols to `BASE/QUOTE` while retaining exchange-native identifiers.
- PRD-MD-003: Detect missing, duplicate, stale, invalid, and out-of-order candles.
- PRD-MD-004: Respect Binance rate limits and retry guidance.
- PRD-MD-005: WebSocket reconnects must detect gaps and trigger idempotent REST backfill.
- PRD-MD-006: Finalized candles must be immutable; corrections create explicit quality and replacement records.
- PRD-MD-007: Strategies and AI may use only data that satisfies freshness and quality policy.

### 8.4 Feature Engineering

- PRD-FEAT-001: Calculate versioned returns, SMA, EMA, RSI, ATR, volatility, and volume features.
- PRD-FEAT-002: Identical inputs and versions must produce identical outputs.
- PRD-FEAT-003: Feature outputs must reference immutable source snapshots.
- PRD-FEAT-004: Feature-set input and output hashes must be stored.

### 8.5 Google Gemini Analysis

- PRD-AI-001: Google Gemini API is the required cloud AI provider for MVP.
- PRD-AI-002: Provider SDK types must remain inside the Gemini infrastructure adapter.
- PRD-AI-003: Gemini must receive only minimum required structured evidence.
- PRD-AI-004: Gemini must return a project-owned structured report schema.
- PRD-AI-005: Malformed, incomplete, stale, unsupported, safety-blocked, or policy-violating output must be rejected.
- PRD-AI-006: Gemini confidence represents analytical classification confidence, not probability of profit.
- PRD-AI-007: The system must record model identifier, prompt version, schema version, request ID, latency, usage, status, retry count, and cost estimate.
- PRD-AI-008: Gemini must not receive execution, shell, database mutation, credential, or risk-policy tools.
- PRD-AI-009: Provider failure degrades to deterministic analysis or HOLD; it must not open a position.
- PRD-AI-010: AI budgets must be enforced before a request is made.

### 8.6 Strategy

- PRD-STRAT-001: Strategies must be deterministic for identical inputs and versions.
- PRD-STRAT-002: Strategy output is a typed intent: HOLD, ENTER, EXIT, or REDUCE.
- PRD-STRAT-003: Strategies must not create orders directly.
- PRD-STRAT-004: Every intent must reference market snapshot, feature-set version, strategy version, and configuration hash.
- PRD-STRAT-005: Backtesting and paper trading must use the same strategy contract.

### 8.7 Risk

- PRD-RISK-001: Every non-HOLD intent must pass the deterministic risk engine.
- PRD-RISK-002: Risk outcomes are approve, approve-with-reduced-size, reject, halt-portfolio, or halt-workspace.
- PRD-RISK-003: Required controls include position, order notional, exposure, daily drawdown, total drawdown, stale data, volatility, cooldown, open-order, duplicate, precision, and minimum-notional checks.
- PRD-RISK-004: Missing or invalid risk configuration must fail closed.
- PRD-RISK-005: Reconciliation mismatch must halt new trading activity.
- PRD-RISK-006: No undocumented bypass switch is permitted.

### 8.8 Paper Execution

- PRD-EXEC-001: Support simulated market and limit orders and cancellation.
- PRD-EXEC-002: Apply explicit versioned fee, spread, slippage, precision, and partial-fill models.
- PRD-EXEC-003: Ambiguous intrabar ordering must resolve conservatively.
- PRD-EXEC-004: One approved risk evaluation may create at most one paper order.
- PRD-EXEC-005: Duplicate commands must return the original result or a deterministic conflict.

### 8.9 Portfolio and Accounting

- PRD-PORT-001: The append-only double-entry ledger is the financial source of truth.
- PRD-PORT-002: Monetary values use decimal arithmetic and explicit currency.
- PRD-PORT-003: Fills and corresponding ledger entries must be committed atomically.
- PRD-PORT-004: Derived cash, reserved funds, positions, fees, P&L, equity, exposure, and drawdown must reconcile to the ledger.
- PRD-PORT-005: Failed reconciliation must create a critical audit event and halt.

### 8.10 Backtesting

- PRD-BT-001: Backtests must prohibit look-ahead and use finalized historical data.
- PRD-BT-002: Fees and slippage are mandatory.
- PRD-BT-003: Results must compare against cash and buy-and-hold benchmarks.
- PRD-BT-004: Runs must store code commit, data hash, strategy version, risk-policy version, configuration hash, dependencies, and random seed.
- PRD-BT-005: Results must include return, drawdown, volatility, Sharpe, Sortino, win rate, profit factor, exposure, turnover, fees, and trade count.

### 8.11 API and Reporting

- PRD-API-001: Public APIs use `/api/v1`.
- PRD-API-002: State-changing commands require idempotency where repetition can duplicate effects.
- PRD-API-003: Lists must be paginated.
- PRD-API-004: Errors must contain stable code and correlation ID without exposing secrets or stack traces.
- PRD-API-005: Users must be able to export experiment results in JSON and CSV.
- PRD-API-006: Audit queries must support filtering by actor, entity, event type, status, and time range.

### 8.12 Operations

- PRD-OPS-001: Expose liveness and readiness health endpoints.
- PRD-OPS-002: Emit structured logs and Prometheus metrics.
- PRD-OPS-003: Critical alerts must have documented runbooks.
- PRD-OPS-004: Background jobs must be retryable, observable, and idempotent.
- PRD-OPS-005: Database or ledger integrity failure must stop side effects.

## 9. Non-Functional Requirements

### 9.1 Reliability

- Restarting API or workers must not duplicate orders, fills, ledger entries, or analysis records.
- No network call may occur inside a database transaction.
- Scheduled work must use deterministic idempotency keys.

### 9.2 Performance

Initial design targets, subject to measurement:

- normal read API p95 below 300 ms in local sandbox conditions;
- command acknowledgement p95 below 500 ms excluding external provider completion;
- completed public candle available internally within 10 seconds under normal exchange conditions;
- readiness fails when PostgreSQL is unavailable or mandatory migrations are missing.

Measured results replace design targets when implementation exists.

### 9.3 Security

- No secret in source, logs, metrics, prompts, responses, or client bundles.
- CI must run secret, dependency, static-code, and container scanning.
- Private exchange credentials are out of MVP scope.
- Gemini API keys must be environment-separated and rotatable.

### 9.4 Privacy

- Do not send personal data or secrets to Gemini.
- Store only data required for operation and audit.
- Retention periods must be configurable where legally necessary.

### 9.5 Maintainability

- Strict typing is required in backend and frontend application code.
- Public behavior requires tests and documentation in the same pull request.
- Provider, exchange, clock, persistence, and queue boundaries use project-owned protocols.

### 9.6 Accessibility

Primary UI workflows must support keyboard navigation, readable contrast, explicit status labels, and non-color-only indication of risk or mode.

## 10. Controlled EUR 20 Experiment

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

## 11. Success Metrics

The MVP is successful when it demonstrates:

- complete and valid market data for the experiment window;
- zero duplicate fills or ledger entries;
- zero unresolved reconciliation mismatches;
- 100% lineage coverage for analysis and trades;
- schema-valid Gemini response rate measured and reported;
- every rejected Gemini output safely handled;
- all risk halts and rejections correctly enforced;
- reproducible backtest results for identical inputs;
- experiment report generated without manual database repair.

Profit is not an MVP acceptance criterion.

## 12. MVP Definition of Done

The MVP is complete only when:

1. all P0 tasks in `TASKS.md` are completed and verified;
2. required P1 experiment tasks are completed;
3. CI quality and security gates pass;
4. migrations and recovery tests pass;
5. all state-changing paths are idempotent;
6. decision and financial lineage are complete;
7. the 30-day paper experiment finishes or halts for a documented safety reason;
8. a final report compares the system with cash and buy-and-hold;
9. documentation reflects the actual implementation;
10. no document or feature implies live trading is enabled.

## 13. Related Documents

- `/AGENTS.md`
- `/TASKS.md`
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
