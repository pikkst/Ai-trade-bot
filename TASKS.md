# Implementation Tasks

Legend: **P0** required for MVP; **P1** important; **P2** later.

## Epic 1 — Repository Foundation
- [ ] P0 T1.1 Create Python project and package layout
- [ ] P0 T1.2 Add `pyproject.toml`
- [ ] P0 T1.3 Configure Ruff
- [ ] P0 T1.4 Configure MyPy strict
- [ ] P0 T1.5 Configure Pytest
- [ ] P0 T1.6 Add pre-commit hooks
- [ ] P0 T1.7 Add Docker Compose
- [ ] P0 T1.8 Add `.env.example`
- [ ] P0 T1.9 Add GitHub Actions quality workflow
- [ ] P0 T1.10 Add contribution templates

## Epic 2 — Application Core
- [ ] P0 T2.1 Implement settings model
- [ ] P0 T2.2 Implement structured logging
- [ ] P0 T2.3 Implement correlation IDs
- [ ] P0 T2.4 Implement error taxonomy
- [ ] P0 T2.5 Implement health endpoints
- [ ] P0 T2.6 Implement database session management
- [ ] P0 T2.7 Implement Redis connection
- [ ] P0 T2.8 Implement migration baseline
- [ ] P0 T2.9 Implement idempotency service
- [ ] P0 T2.10 Add application startup validation

## Epic 3 — Market Data
- [ ] P0 T3.1 Define exchange adapter protocol
- [ ] P0 T3.2 Implement Binance public adapter
- [ ] P0 T3.3 Normalize symbols
- [ ] P0 T3.4 Persist exchange precision metadata
- [ ] P0 T3.5 Implement candle ingestion
- [ ] P0 T3.6 Implement backfill checkpoints
- [ ] P0 T3.7 Detect missing candles
- [ ] P0 T3.8 Detect duplicates
- [ ] P0 T3.9 Detect stale data
- [ ] P0 T3.10 Create immutable market snapshots
- [ ] P1 T3.11 Add ticker ingestion
- [ ] P1 T3.12 Add order-book snapshots

## Epic 4 — Feature Engineering
- [ ] P0 T4.1 Define feature-set version model
- [ ] P0 T4.2 Implement returns
- [ ] P0 T4.3 Implement SMA and EMA
- [ ] P0 T4.4 Implement RSI
- [ ] P0 T4.5 Implement ATR
- [ ] P0 T4.6 Implement volatility
- [ ] P0 T4.7 Implement volume features
- [ ] P0 T4.8 Add deterministic feature tests
- [ ] P0 T4.9 Hash feature inputs and outputs
- [ ] P1 T4.10 Add market-regime classifier

## Epic 5 — AI Analysis
- [ ] P0 T5.1 Define provider protocol
- [ ] P0 T5.2 Implement fake provider
- [ ] P0 T5.3 Implement OpenAI-compatible provider
- [ ] P1 T5.4 Implement Ollama provider
- [ ] P1 T5.5 Implement vLLM provider
- [ ] P0 T5.6 Define report JSON schema
- [ ] P0 T5.7 Implement prompt versioning
- [ ] P0 T5.8 Implement output validation
- [ ] P0 T5.9 Implement timeout and retry rules
- [ ] P0 T5.10 Record tokens, latency, and cost
- [ ] P0 T5.11 Add AI budget controls
- [ ] P0 T5.12 Add prompt-injection tests

## Epic 6 — Strategy Engine
- [ ] P0 T6.1 Define strategy protocol
- [ ] P0 T6.2 Define intent schema
- [ ] P0 T6.3 Implement HOLD-only smoke strategy
- [ ] P0 T6.4 Implement BTC/EUR trend baseline
- [ ] P0 T6.5 Add strategy versioning
- [ ] P0 T6.6 Add observation mode
- [ ] P0 T6.7 Add deterministic unit tests
- [ ] P1 T6.8 Add AI agreement feature

## Epic 7 — Risk Engine
- [ ] P0 T7.1 Define policy version model
- [ ] P0 T7.2 Implement position limit
- [ ] P0 T7.3 Implement order-notional limit
- [ ] P0 T7.4 Implement exposure limit
- [ ] P0 T7.5 Implement daily drawdown halt
- [ ] P0 T7.6 Implement total drawdown halt
- [ ] P0 T7.7 Implement stale-data rejection
- [ ] P0 T7.8 Implement duplicate protection
- [ ] P0 T7.9 Implement cooldown
- [ ] P0 T7.10 Implement global kill switch
- [ ] P0 T7.11 Add fail-closed tests
- [ ] P0 T7.12 Add EUR 20 research profile

## Epic 8 — Portfolio and Paper Trading
- [ ] P0 T8.1 Implement portfolio model
- [ ] P0 T8.2 Implement append-only ledger
- [ ] P0 T8.3 Implement double-entry invariants
- [ ] P0 T8.4 Implement market orders
- [ ] P0 T8.5 Implement limit orders
- [ ] P0 T8.6 Implement cancellation
- [ ] P0 T8.7 Implement fee model
- [ ] P0 T8.8 Implement slippage model
- [ ] P0 T8.9 Implement partial fills
- [ ] P0 T8.10 Implement P&L
- [ ] P0 T8.11 Implement drawdown
- [ ] P0 T8.12 Implement reconciliation
- [ ] P0 T8.13 Halt on mismatch

## Epic 9 — Backtesting
- [ ] P0 T9.1 Implement historical event loop
- [ ] P0 T9.2 Reuse strategy contract
- [ ] P0 T9.3 Reuse risk contract
- [ ] P0 T9.4 Reuse paper fill model
- [ ] P0 T9.5 Prevent look-ahead
- [ ] P0 T9.6 Add cash benchmark
- [ ] P0 T9.7 Add buy-and-hold benchmark
- [ ] P0 T9.8 Calculate performance metrics
- [ ] P0 T9.9 Store reproducibility metadata
- [ ] P1 T9.10 Add walk-forward evaluation

## Epic 10 — API
- [ ] P0 T10.1 Implement workspaces API
- [ ] P0 T10.2 Implement market API
- [ ] P0 T10.3 Implement analysis API
- [ ] P0 T10.4 Implement strategy API
- [ ] P0 T10.5 Implement risk API
- [ ] P0 T10.6 Implement paper portfolio API
- [ ] P0 T10.7 Implement paper orders API
- [ ] P0 T10.8 Implement backtest API
- [ ] P0 T10.9 Implement audit API
- [ ] P0 T10.10 Generate OpenAPI
- [ ] P0 T10.11 Add pagination and filters

## Epic 11 — Security
- [ ] P0 T11.1 Implement authentication
- [ ] P0 T11.2 Implement owner/operator/viewer roles
- [ ] P0 T11.3 Add rate limiting
- [ ] P0 T11.4 Add secure headers
- [ ] P0 T11.5 Add CORS allowlist
- [ ] P0 T11.6 Add secret redaction
- [ ] P0 T11.7 Add dependency scanning
- [ ] P0 T11.8 Add Bandit and Semgrep
- [ ] P0 T11.9 Add container scanning
- [ ] P0 T11.10 Document key rotation

## Epic 12 — Observability
- [ ] P0 T12.1 Export Prometheus metrics
- [ ] P0 T12.2 Create platform dashboard
- [ ] P0 T12.3 Create data-quality dashboard
- [ ] P0 T12.4 Create AI dashboard
- [ ] P0 T12.5 Create risk dashboard
- [ ] P0 T12.6 Create portfolio dashboard
- [ ] P0 T12.7 Configure critical alerts
- [ ] P0 T12.8 Configure warning alerts

## Epic 13 — Frontend
- [ ] P1 T13.1 Initialize React and TypeScript
- [ ] P1 T13.2 Add authentication flow
- [ ] P1 T13.3 Add workspace settings
- [ ] P1 T13.4 Add market overview
- [ ] P1 T13.5 Add AI analysis view
- [ ] P1 T13.6 Add paper portfolio view
- [ ] P1 T13.7 Add backtest report
- [ ] P1 T13.8 Add audit timeline
- [ ] P1 T13.9 Add halt controls

## Epic 14 — 30-Day Experiment
- [ ] P0 T14.1 Freeze experiment configuration
- [ ] P0 T14.2 Seed EUR 20 virtual balance
- [ ] P0 T14.3 Enable BTC/EUR
- [ ] P0 T14.4 Verify fee and slippage assumptions
- [ ] P0 T14.5 Run preflight checks
- [ ] P0 T14.6 Start paper experiment
- [ ] P0 T14.7 Monitor data completeness
- [ ] P0 T14.8 Monitor risk events
- [ ] P0 T14.9 Compare benchmarks
- [ ] P0 T14.10 Produce final report
- [ ] P0 T14.11 Review whether sandbox progression is justified
