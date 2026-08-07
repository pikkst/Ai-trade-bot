"""Project-owned Binance market-data protocol, models, and errors."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Protocol


class SymbolStatus(str, Enum):
    PRE_TRADING = "PRE_TRADING"
    TRADING = "TRADING"
    POST_TRADING = "POST_TRADING"
    END_OF_DAY = "END_OF_DAY"
    HALT = "HALT"
    AUCTION_MATCH = "AUCTION_MATCH"
    BREAK = "BREAK"


class CandleInterval(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"


@dataclass(frozen=True, slots=True)
class Candle:
    time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def as_sequence(
        self,
    ) -> tuple[datetime, Decimal, Decimal, Decimal, Decimal, Decimal]:
        return (self.time, self.open, self.high, self.low, self.close, self.volume)


@dataclass(frozen=True, slots=True)
class SymbolMetadata:
    symbol: str
    base_asset: str
    quote_asset: str
    status: SymbolStatus
    price_precision: int
    quantity_precision: int
    min_quantity: Decimal
    max_quantity: Decimal
    min_notional: Decimal
    tick_size: Decimal
    step_size: Decimal


@dataclass(frozen=True, slots=True)
class ExchangeTime:
    server_time: datetime
    clock_drift_ms: int


@dataclass(frozen=True, slots=True)
class RateLimitState:
    remaining_requests: int
    reset_time: datetime | None = None


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    healthy: bool
    last_check: datetime
    message: str | None = None


class BinanceProviderError(Exception):
    code = "binance_provider_error"

    def __init__(
        self, message: str, *, details: dict[str, object] | None = None
    ) -> None:
        super().__init__(message)
        self.details = details


class BinanceTimeoutError(BinanceProviderError):
    code = "binance_timeout"


class BinanceRateLimitError(BinanceProviderError):
    code = "binance_rate_limit"


class BinanceMalformedDataError(BinanceProviderError):
    code = "binance_malformed_data"


class BinanceProviderUnavailableError(BinanceProviderError):
    code = "binance_unavailable"


class BinanceDataGapError(BinanceProviderError):
    code = "binance_data_gap"


class BinanceStaleDataError(BinanceProviderError):
    code = "binance_stale_data"


class BinanceInvalidSymbolError(BinanceProviderError):
    code = "binance_invalid_symbol"


class BinanceExchangeError(BinanceProviderError):
    code = "binance_exchange_error"


class MarketDataProvider(Protocol):
    async def get_server_time(self) -> ExchangeTime: ...

    async def get_symbol_metadata(self, symbol: str) -> SymbolMetadata: ...

    async def get_finalized_candles(
        self,
        symbol: str,
        interval: CandleInterval,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Candle]: ...

    async def get_rate_limit_state(self) -> RateLimitState: ...

    async def get_health(self) -> ProviderHealth: ...
