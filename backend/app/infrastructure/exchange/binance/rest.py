"""Real Binance Spot public REST provider using httpx."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Self

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception_type,
    stop_after_attempt,
)

from app.core.clock import Clock, get_clock
from app.infrastructure.exchange.binance.protocol import (
    BinanceExchangeError,
    BinanceInvalidSymbolError,
    BinanceProviderUnavailableError,
    BinanceRateLimitError,
    BinanceTimeoutError,
    Candle,
    CandleInterval,
    ExchangeTime,
    ProviderHealth,
    RateLimitState,
    SymbolMetadata,
    SymbolStatus,
)

logger = logging.getLogger(__name__)

_BINANCE_REST_BASE = "https://api.binance.com"
_SERVER_TIME_PATH = "/api/v3/time"
_EXCHANGE_INFO_PATH = "/api/v3/exchangeInfo"
_KLINES_PATH = "/api/v3/klines"
_REQUEST_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
_MAX_RETRIES = 3
_RETRY_WAIT_MULTIPLIER = 1
_RETRY_WAIT_MIN = 1.0
_RETRY_WAIT_MAX = 10.0
_RETRY_AFTER_MAX = 30.0
_CLOCK_DRIFT_THRESHOLD_MS = 5000


def _bounded_exponential_wait(
    retry_state: RetryCallState,
    retry_after: float,
) -> float:
    """Exponential backoff bounded by the configured window.

    Honors a Binance Retry-After header so a 429 backoff request is respected
    instead of retrying too early (which risks repeated throttling or a 418).
    """
    wait_seconds = float(
        _RETRY_WAIT_MIN * (_RETRY_WAIT_MULTIPLIER ** (retry_state.attempt_number - 1))
    )
    wait_seconds = min(max(wait_seconds, _RETRY_WAIT_MIN), _RETRY_WAIT_MAX)
    if retry_after:
        wait_seconds = max(wait_seconds, min(retry_after, _RETRY_AFTER_MAX))
    return wait_seconds


class BinanceRestProvider:
    """Production Binance Spot public REST provider."""

    def __init__(
        self,
        *,
        base_url: str = _BINANCE_REST_BASE,
        clock: Clock | None = None,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._clock = clock or get_clock()
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=_REQUEST_TIMEOUT,
            headers={"Accept": "application/json"},
        )
        self._last_server_time: datetime | None = None
        self._last_clock_drift_ms: int = 0
        self._symbol_metadata_cache: dict[str, SymbolMetadata] = {}
        self.retry_count = 0
        self.last_retry_wait_ms: int | None = None

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def get_server_time(self) -> ExchangeTime:
        local_time = self._clock.now()
        response = await self._request("GET", _SERVER_TIME_PATH)
        server_time_ms = int(response["serverTime"])
        server_time = datetime.fromtimestamp(server_time_ms / 1000.0, tz=timezone.utc)
        drift_ms = int((server_time - local_time).total_seconds() * 1000)
        self._last_server_time = server_time
        self._last_clock_drift_ms = drift_ms
        if abs(drift_ms) > _CLOCK_DRIFT_THRESHOLD_MS:
            logger.warning(
                "binance_clock_drift_exceeded",
                extra={
                    "drift_ms": drift_ms,
                    "threshold_ms": _CLOCK_DRIFT_THRESHOLD_MS,
                },
            )
        return ExchangeTime(server_time=server_time, clock_drift_ms=drift_ms)

    async def get_symbol_metadata(self, symbol: str) -> SymbolMetadata:
        cache_key = symbol.upper()
        if cache_key in self._symbol_metadata_cache:
            return self._symbol_metadata_cache[cache_key]
        response = await self._request("GET", _EXCHANGE_INFO_PATH)
        symbol_info = None
        for s in response.get("symbols", []):
            if s.get("symbol", "").upper() == cache_key:
                symbol_info = s
                break
        if symbol_info is None:
            raise BinanceInvalidSymbolError(f"Unknown symbol {symbol}")
        metadata = _parse_symbol_metadata(symbol_info)
        self._symbol_metadata_cache[cache_key] = metadata
        return metadata

    async def get_finalized_candles(
        self,
        symbol: str,
        interval: CandleInterval,
        start_time: datetime,
        end_time: datetime,
        server_time: datetime | None = None,
    ) -> list[Candle]:
        if start_time >= end_time:
            return []
        if server_time is None:
            server_time = self._clock.now()
        all_candles: list[Candle] = []
        current_start = start_time
        interval_seconds = _INTERVAL_SECONDS[interval]
        max_candles_per_request = 1000
        max_range_seconds = max_candles_per_request * interval_seconds
        while current_start < end_time:
            chunk_end = min(
                current_start + timedelta(seconds=max_range_seconds),
                end_time,
            )
            params = {
                "symbol": symbol.upper(),
                "interval": interval.value,
                "startTime": int(current_start.timestamp() * 1000),
                "endTime": int(chunk_end.timestamp() * 1000),
                "limit": max_candles_per_request,
            }
            response = await self._request("GET", _KLINES_PATH, params=params)
            if not response:
                break
            for row in response:
                candle = _parse_kline(row, interval)
                if candle.close_time <= server_time:
                    all_candles.append(candle)
            if len(response) < max_candles_per_request:
                break
            last_candle = _parse_kline(response[-1], interval)
            next_start = last_candle.time + timedelta(seconds=interval_seconds)
            if next_start <= current_start:
                break
            current_start = next_start
        return all_candles

    async def get_rate_limit_state(self) -> RateLimitState:
        return RateLimitState(
            remaining_requests=-1,
            reset_time=None,
        )

    async def get_health(self) -> ProviderHealth:
        try:
            await self.get_server_time()
            return ProviderHealth(
                healthy=True,
                last_check=self._clock.now(),
                message="Binance REST healthy",
            )
        except Exception as exc:
            return ProviderHealth(
                healthy=False,
                last_check=self._clock.now(),
                message=f"Binance REST unhealthy: {exc}",
            )

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        retry_after_holder: dict[str, float] = {"value": 0.0}

        def _wait(retry_state: RetryCallState) -> float:
            self.retry_count += 1
            wait_seconds = _bounded_exponential_wait(
                retry_state, retry_after_holder["value"]
            )
            self.last_retry_wait_ms = int(wait_seconds * 1000)
            return wait_seconds

        retrying = AsyncRetrying(
            retry=retry_if_exception_type(
                (
                    BinanceRateLimitError,
                    BinanceTimeoutError,
                    httpx.TimeoutException,
                )
            ),
            wait=_wait,
            stop=stop_after_attempt(self._max_retries),
            reraise=True,
        )

        async def _do_request() -> Any:
            try:
                response = await self._client.request(method, path, params=params)
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    wait = float(retry_after) if retry_after else _RETRY_WAIT_MIN
                    retry_after_holder["value"] = wait
                    logger.warning(
                        "binance_rate_limited",
                        extra={"path": path, "retry_after": wait},
                    )
                    raise BinanceRateLimitError(f"Binance rate limited on {path}")
                if response.status_code == 418:
                    raise BinanceRateLimitError(f"Binance IP ban on {path}")
                if response.status_code >= 500:
                    logger.error(
                        "binance_server_error",
                        extra={
                            "path": path,
                            "status": response.status_code,
                        },
                    )
                    raise BinanceProviderUnavailableError(
                        f"Binance server error {response.status_code} on {path}"
                    )
                if response.status_code == 400:
                    logger.error(
                        "binance_bad_request",
                        extra={
                            "path": path,
                            "body": response.text[:500],
                        },
                    )
                    raise BinanceInvalidSymbolError(
                        f"Binance bad request on {path}: {response.text[:200]}"
                    )
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException as exc:
                logger.warning("binance_timeout", extra={"path": path})
                raise BinanceTimeoutError(
                    f"Binance request timed out on {path}"
                ) from exc
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "binance_http_error",
                    extra={
                        "path": path,
                        "status": exc.response.status_code,
                    },
                )
                raise BinanceExchangeError(
                    f"Binance HTTP error {exc.response.status_code} on {path}"
                ) from exc
            except BinanceProviderUnavailableError:
                raise
            except BinanceRateLimitError:
                raise
            except BinanceInvalidSymbolError:
                raise
            except BinanceTimeoutError:
                raise
            except Exception as exc:
                logger.error(
                    "binance_request_failed",
                    extra={"path": path, "error": str(exc)},
                )
                raise BinanceProviderUnavailableError(
                    f"Binance request failed on {path}: {exc}"
                ) from exc

        try:
            return await retrying(_do_request)
        except BinanceRateLimitError:
            raise
        except BinanceTimeoutError:
            raise
        except BinanceInvalidSymbolError:
            raise
        except Exception as exc:
            raise BinanceProviderUnavailableError(
                f"Binance provider unavailable after retries: {exc}"
            ) from exc


def _parse_symbol_metadata(raw: dict[str, Any]) -> SymbolMetadata:
    status_str = raw.get("status", "TRADING").upper()
    try:
        status = SymbolStatus(status_str)
    except ValueError:
        status = SymbolStatus.TRADING
    price_precision = 0
    quantity_precision = 0
    tick_size = Decimal("0.00000000000000000001")
    step_size = Decimal("0.00000000000000000001")
    min_quantity = Decimal("0")
    max_quantity = Decimal("9000")
    min_notional = Decimal("0")
    for filter_item in raw.get("filters", []):
        filter_type = filter_item.get("filterType", "")
        if filter_type == "PRICE_FILTER":
            tick_size = Decimal(str(filter_item.get("tickSize", "0.00000001")))
            price_precision = _decimal_precision(tick_size)
        elif filter_type == "LOT_SIZE":
            step_size = Decimal(str(filter_item.get("stepSize", "0.00000001")))
            quantity_precision = _decimal_precision(step_size)
            min_quantity = Decimal(str(filter_item.get("minQty", "0")))
            max_quantity = Decimal(str(filter_item.get("maxQty", "9000")))
        elif filter_type == "MIN_NOTIONAL":
            min_notional = Decimal(str(filter_item.get("minNotional", "0")))
    return SymbolMetadata(
        symbol=raw.get("symbol", ""),
        base_asset=raw.get("baseAsset", ""),
        quote_asset=raw.get("quoteAsset", ""),
        status=status,
        price_precision=price_precision,
        quantity_precision=quantity_precision,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        min_notional=min_notional,
        tick_size=tick_size,
        step_size=step_size,
    )


def _parse_kline(row: list[Any], interval: CandleInterval) -> Candle:
    open_time = datetime.fromtimestamp(int(row[0]) / 1000.0, tz=timezone.utc)
    close_time = datetime.fromtimestamp(int(row[6]) / 1000.0, tz=timezone.utc)
    return Candle(
        time=open_time,
        close_time=close_time,
        open=Decimal(str(row[1])),
        high=Decimal(str(row[2])),
        low=Decimal(str(row[3])),
        close=Decimal(str(row[4])),
        volume=Decimal(str(row[5])),
        quote_volume=Decimal(str(row[7])) if len(row) > 7 else Decimal("0"),
        trade_count=int(row[8]) if len(row) > 8 else 0,
    )


def _decimal_precision(value: Decimal) -> int:
    try:
        normalized = value.normalize()
        if normalized == normalized.to_integral_value():
            return 0
        exponent = normalized.as_tuple().exponent
        if isinstance(exponent, int):
            return abs(exponent)
        return 0
    except (InvalidOperation, ArithmeticError):
        return 0


_INTERVAL_SECONDS: dict[CandleInterval, int] = {
    CandleInterval.ONE_MINUTE: 60,
    CandleInterval.FIVE_MINUTES: 300,
    CandleInterval.FIFTEEN_MINUTES: 900,
    CandleInterval.ONE_HOUR: 3600,
    CandleInterval.FOUR_HOURS: 14400,
    CandleInterval.ONE_DAY: 86400,
}
