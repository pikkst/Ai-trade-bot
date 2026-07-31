# Backtest Engine

## Rules
No look-ahead. Use only finalized data. Fees and slippage are mandatory. Train, validation, and test periods remain separate.

## Inputs
Strategy version, risk version, symbol, interval, period, capital, fee model, slippage model, execution model, and data version.

## Outputs
Return, benchmark, drawdown, volatility, Sharpe, Sortino, win rate, profit factor, trades, exposure, turnover, fees, equity curve, ledger, and warnings.

Store code commit, configuration hash, data hash, random seed, library versions, and timestamps for reproducibility.
