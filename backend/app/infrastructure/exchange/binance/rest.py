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
    BinanceMalformedDataError,
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
    """Bounded exponential backoff that honors a Binance Retry-After header.

    Ordinary retries grow exponentially as
    min * multiplier * 2 ** (attempt_number - 1), bounded by max. A Retry-After
    value from a 429 response is honored when it is larger, also bounded, so a
    request is not retried too early (which risks a 418 ban).
    """
    wait_seconds = float(
        _RETRY_WAIT_MIN
        * _RETRY_WAIT_MULTIPLIER
        * (2 ** (retry_state.attempt_number - 1))
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
            # Binance endTime is inclusive, so request through the last
            # millisecond before the exclusive end to avoid pulling the
            # boundary kline that was not requested.
            inclusive_end_ms = int(chunk_end.timestamp() * 1000) - 1
            if inclusive_end_ms < int(current_start.timestamp() * 1000):
                break
            params = {
                "symbol": symbol.upper(),
                "interval": interval.value,
                "startTime": int(current_start.timestamp() * 1000),
                "endTime": inclusive_end_ms,
                "limit": max_candles_per_request,
            }
            response = await self._request("GET", _KLINES_PATH, params=params)
            if not response:
                break
            for row in response:
                candle = _parse_kline(row, interval)
                # Defensively enforce the exclusive range even if the provider
                # returns a row at or after end_time.
                if not (start_time <= candle.time < chunk_end):
                    continue
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
                if response.status_code in (429, 418):
                    retry_after = response.headers.get("Retry-After")
                    wait = float(retry_after) if retry_after else _RETRY_WAIT_MIN
                    # Never shorten a provider-required backoff. If it exceeds
                    # the local execution budget, fail closed without another
                    # request instead of retrying an active ban too early.
                    if wait > _RETRY_AFTER_MAX:
                        raise BinanceProviderUnavailableError(
                            f"Binance requested backoff {wait}s on {path} "
                            f"exceeds configured bound {_RETRY_AFTER_MAX}s; "
                            "failing closed without another request"
                        )
                    retry_after_holder["value"] = wait
                    logger.warning(
                        "binance_rate_limited",
                        extra={
                            "path": path,
                            "status": response.status_code,
                            "retry_after": wait,
                        },
                    )
                    kind = "IP ban" if response.status_code == 418 else "rate limited"
                    raise BinanceRateLimitError(f"Binance {kind} on {path}")
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
    status_str = raw.get("status")
    if status_str is None:
        raise BinanceMalformedDataError("symbol metadata is missing status")
    try:
        status = SymbolStatus(status_str.upper())
    except ValueError as exc:
        raise BinanceMalformedDataError(
            f"unknown symbol status {status_str!r}"
        ) from exc
    filters = raw.get("filters") or []
    price_filter = next(
        (f for f in filters if f.get("filterType") == "PRICE_FILTER"), None
    )
    lot_filter = next((f for f in filters if f.get("filterType") == "LOT_SIZE"), None)
    notional_filter = next(
        (f for f in filters if f.get("filterType") == "MIN_NOTIONAL"), None
    )
    if price_filter is None or lot_filter is None or notional_filter is None:
        raise BinanceMalformedDataError(
            "symbol metadata is missing required filters "
            "(PRICE_FILTER, LOT_SIZE, MIN_NOTIONAL)"
        )
    try:
        tick_size = Decimal(str(price_filter.get("tickSize")))
        price_precision = _decimal_precision(tick_size)
        step_size = Decimal(str(lot_filter.get("stepSize")))
        quantity_precision = _decimal_precision(step_size)
        min_quantity = Decimal(str(lot_filter.get("minQty")))
        max_quantity = Decimal(str(lot_filter.get("maxQty", "9000")))
        min_notional = Decimal(str(notional_filter.get("minNotional")))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise BinanceMalformedDataError(
            f"symbol metadata has invalid filter values: {exc}"
        ) from exc
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
    """Parse a Binance Spot kline row with the exact bounded schema.

    A row shorter than the documented 12 fields is malformed, never coerced
    into zero-volume evidence. Decimal/int conversion failures raise
    BinanceMalformedDataError rather than leaking built-in exceptions.
    """
    if not isinstance(row, list) or len(row) < 12:
        raise BinanceMalformedDataError(
            f"kline row has {len(row) if isinstance(row, list) else 'non-list'} "
            "fields; expected at least 12"
        )
    try:
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
            quote_volume=Decimal(str(row[7])),
            trade_count=int(row[8]),
        )
    except (ValueError, TypeError, InvalidOperation, OverflowError) as exc:
        raise BinanceMalformedDataError(
            f"kline row has invalid numeric/time fields: {exc}"
        ) from exc


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
