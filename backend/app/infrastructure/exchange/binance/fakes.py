"""Deterministic fake Binance provider for tests and local development."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum

from app.core.clock import Clock, FixedClock
from app.infrastructure.exchange.binance.protocol import (
    BinanceInvalidSymbolError,
    BinanceMalformedDataError,
    BinanceProviderUnavailableError,
    BinanceRateLimitError,
    BinanceStaleDataError,
    BinanceTimeoutError,
    Candle,
    CandleInterval,
    ExchangeTime,
    ProviderHealth,
    RateLimitState,
    SymbolMetadata,
    SymbolStatus,
)


class FakeBinanceScenario(str, Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    MALFORMED = "malformed"
    UNAVAILABLE = "unavailable"
    STALE = "stale"
    GAP = "gap"
    INVALID_SYMBOL = "invalid_symbol"


@dataclass(frozen=True, slots=True)
class FakeBinanceConfig:
    scenario: FakeBinanceScenario = FakeBinanceScenario.SUCCESS
    server_time_offset_seconds: int = 0
    rate_limit_remaining: int = 1000
    gap_start: datetime | None = None
    gap_end: datetime | None = None
    stale_threshold_minutes: int = 60
    fixed_clock_time: datetime | None = None
    fixture_version: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.scenario, FakeBinanceScenario):
            raise ValueError(
                f"Invalid FakeBinanceScenario: {self.scenario!r}. "
                f"Valid values: {[s.value for s in FakeBinanceScenario]}"
            )
        if not self.fixture_version:
            raise ValueError("fixture_version must be non-empty")


class FakeBinanceProvider:
    _clock: Clock | None

    def __init__(self, config: FakeBinanceConfig) -> None:
        self.config = config
        if self.config.fixed_clock_time is not None:
            self._clock = FixedClock(self.config.fixed_clock_time)
        else:
            self._clock = None
        self._request_count = 0
        self._symbol_metadata: dict[str, SymbolMetadata] = {
            "BTCEUR": SymbolMetadata(
                symbol="BTCEUR",
                base_asset="BTC",
                quote_asset="EUR",
                status=SymbolStatus.TRADING,
                price_precision=2,
                quantity_precision=6,
                min_quantity=Decimal("0.00001"),
                max_quantity=Decimal("9000.00000"),
                min_notional=Decimal("10.00"),
                tick_size=Decimal("0.01"),
                step_size=Decimal("0.000001"),
            )
        }
        self._base_time = datetime(2026, 8, 1, 0, 0, 0, tzinfo=timezone.utc)

    def _now(self) -> datetime:
        if self._clock is not None:
            return self._clock.now()
        return datetime.now(timezone.utc)

    def _check_scenario(self) -> None:
        self._request_count += 1
        if self.config.scenario == FakeBinanceScenario.TIMEOUT:
            raise BinanceTimeoutError("Fake Binance timeout")
        if self.config.scenario == FakeBinanceScenario.RATE_LIMIT:
            raise BinanceRateLimitError("Fake Binance rate limit")
        if self.config.scenario == FakeBinanceScenario.UNAVAILABLE:
            raise BinanceProviderUnavailableError("Fake Binance unavailable")
        if self.config.scenario == FakeBinanceScenario.INVALID_SYMBOL:
            raise BinanceInvalidSymbolError("Fake Binance invalid symbol")

    async def get_server_time(self) -> ExchangeTime:
        self._check_scenario()
        server_time = self._now() + timedelta(
            seconds=self.config.server_time_offset_seconds
        )
        local_time = self._now()
        drift_ms = int((server_time - local_time).total_seconds() * 1000)
        return ExchangeTime(server_time=server_time, clock_drift_ms=drift_ms)

    async def get_symbol_metadata(self, symbol: str) -> SymbolMetadata:
        self._check_scenario()
        metadata = self._symbol_metadata.get(symbol.upper())
        if metadata is None:
            raise BinanceInvalidSymbolError(f"Unknown symbol {symbol}")
        return metadata

    async def get_finalized_candles(
        self,
        symbol: str,
        interval: CandleInterval,
        start_time: datetime,
        end_time: datetime,
        server_time: datetime | None = None,
    ) -> list[Candle]:
        self._check_scenario()
        if self.config.scenario == FakeBinanceScenario.MALFORMED:
            raise BinanceMalformedDataError("Fake malformed candle data")

        if self.config.scenario == FakeBinanceScenario.STALE:
            raise BinanceStaleDataError("Fake Binance stale data")

        candles: list[Candle] = []
        current = self._base_time
        if start_time > self._base_time:
            current = start_time

        interval_minutes = {
            CandleInterval.ONE_MINUTE: 1,
            CandleInterval.FIVE_MINUTES: 5,
            CandleInterval.FIFTEEN_MINUTES: 15,
            CandleInterval.ONE_HOUR: 60,
            CandleInterval.FOUR_HOURS: 240,
            CandleInterval.ONE_DAY: 1440,
        }[interval]

        price = Decimal("50000.00")
        while current + timedelta(minutes=interval_minutes) <= end_time:
            if (
                self.config.gap_start is not None
                and self.config.gap_end is not None
                and self.config.gap_start <= current < self.config.gap_end
            ):
                current += timedelta(minutes=interval_minutes)
                continue

            open_price = price
            close_price = price + Decimal("100.00")
            high_price = max(open_price, close_price) + Decimal("50.00")
            low_price = min(open_price, close_price) - Decimal("50.00")
            volume = Decimal("1.5")

            candles.append(
                Candle(
                    time=current,
                    close_time=current + timedelta(minutes=interval_minutes),
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume,
                    quote_volume=volume * close_price,
                    trade_count=100,
                )
            )
            price = close_price
            current += timedelta(minutes=interval_minutes)

        if not candles:
            return []

        if self.config.scenario == FakeBinanceScenario.GAP and len(candles) > 2:
            candles = candles[: len(candles) // 2]

        return candles

    async def get_rate_limit_state(self) -> RateLimitState:
        self._check_scenario()
        return RateLimitState(
            remaining_requests=self.config.rate_limit_remaining,
            reset_time=self._now() + timedelta(minutes=1),
        )

    async def get_health(self) -> ProviderHealth:
        self._check_scenario()
        return ProviderHealth(
            healthy=True,
            last_check=self._now(),
            message="Fake Binance is healthy",
        )
