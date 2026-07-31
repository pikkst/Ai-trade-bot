# Database Schema

PostgreSQL is the system of record. Use UUID keys, UTC `timestamptz`, `numeric` for monetary values, append-only ledger and audit records, and foreign keys where possible.

## Core Tables
`workspaces`, `workspace_config_versions`, `exchange_symbols`, `candles`, `data_quality_events`, `market_snapshots`, `feature_sets`, `feature_values`, `ai_provider_configs`, `ai_prompt_versions`, `ai_analysis_runs`, `ai_reports`, `strategy_versions`, `strategy_evaluations`, `risk_policy_versions`, `risk_evaluations`, `paper_portfolios`, `paper_orders`, `paper_fills`, `ledger_entries`, `positions`, `backtest_runs`, `audit_events`, `background_jobs`.

## Constraints
Unique candle identity by exchange, symbol, interval, and open time. One paper order per approved risk evaluation. Append-only ledger sequencing per portfolio.

## Retention
Candles and decisions indefinite; AI raw responses 180 days by default; operational logs 30 days; audit records at least one year.
