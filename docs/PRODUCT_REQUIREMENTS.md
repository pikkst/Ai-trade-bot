# Product Requirements

## Purpose
Define the requirements for the first production-quality version.

## Goals
- Explainable market analysis from measurable inputs
- AI recommendations compared with deterministic strategies and benchmarks
- Realistic simulation including fees, spread, and slippage
- Complete lineage from data snapshot to simulated fill
- Safe progression from local research to exchange sandbox
- Cloud and local LLM support
- Fail-closed behavior

## Non-Goals
Live trading, custody, leverage, futures, margin, HFT, arbitrage, copy trading, self-modifying strategies, and guaranteed returns.

## Functional Requirements
- Ingest Binance Spot OHLCV
- Detect missing, duplicate, stale, invalid, and out-of-order data
- Calculate versioned indicators
- Generate schema-valid AI reports
- Reject malformed or stale AI output
- Produce deterministic HOLD, ENTER, EXIT, or REDUCE intents
- Route every intent through deterministic risk validation
- Simulate market and limit orders with fees and slippage
- Track balances, positions, equity, P&L, exposure, and drawdown
- Preserve immutable decision lineage
- Alert on data, AI, risk, reconciliation, and health failures
- Support pause, cancel, and global halt controls

## MVP Definition of Done
All P0 tasks complete, tests pass, security controls implemented, and a 30-day paper experiment runs without manual database repair.
