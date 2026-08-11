"""Unit tests for the production Binance REST provider (M007)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest

from app.core.clock import FixedClock
from app.infrastructure.exchange.binance.protocol import (
    BinanceInvalidSymbolError,
    BinanceMalformedDataError,
    BinanceServerError,
)
from app.infrastructure.exchange.binance.rest import BinanceRestProvider

FIXED_TIME = datetime(2026, 8, 8, 12, 0, 0, tzinfo=timezone.utc)


def _response(status_code: int, json_body: Any) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=json_body,
        request=httpx.Request("GET", "/api/v3/time"),
    )


def _build_provider(
    responses: list[httpx.Response],
) -> tuple[BinanceRestProvider, AsyncMock]:
    provider = BinanceRestProvider(
        clock=FixedClock(FIXED_TIME),
        max_retries=3,
    )
    request_mock = AsyncMock(side_effect=responses)
    provider._client.request = request_mock  # type: ignore[method-assign]
    return provider, request_mock


@pytest.mark.asyncio
async def test_server_time_ok() -> None:
    provider, request_mock = _build_provider(
        [_response(200, {"serverTime": int(FIXED_TIME.timestamp() * 1000)})]
    )
    try:
        result = await provider.get_server_time()
    finally:
        await provider.close()
    assert request_mock.await_count == 1
    assert result.server_time == FIXED_TIME


@pytest.mark.asyncio
async def test_server_time_missing_field_rejected() -> None:
    provider, _ = _build_provider([_response(200, {"other": 1})])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_server_time()
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_server_time_non_numeric_rejected() -> None:
    provider, _ = _build_provider([_response(200, {"serverTime": "abc"})])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_server_time()
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_server_time_5xx_then_success_retried() -> None:
    provider, request_mock = _build_provider(
        [
            _response(503, {"msg": "busy"}),
            _response(200, {"serverTime": int(FIXED_TIME.timestamp() * 1000)}),
        ]
    )
    try:
        result = await provider.get_server_time()
    finally:
        await provider.close()
    assert request_mock.await_count == 2
    assert provider.retry_count >= 1
    assert result.server_time == FIXED_TIME


@pytest.mark.asyncio
async def test_server_time_5xx_exhausted_fails() -> None:
    provider, request_mock = _build_provider(
        [
            _response(503, {"msg": "busy"}),
            _response(502, {"msg": "bad"}),
            _response(500, {"msg": "boom"}),
        ]
    )
    try:
        with pytest.raises(BinanceServerError):
            await provider.get_server_time()
    finally:
        await provider.close()
    assert request_mock.await_count == 3
    assert provider.retry_count >= 2


@pytest.mark.asyncio
async def test_non_retriable_4xx_not_retried() -> None:
    provider, request_mock = _build_provider([_response(400, {"msg": "bad request"})])
    try:
        with pytest.raises(BinanceInvalidSymbolError):
            await provider.get_server_time()
    finally:
        await provider.close()
    assert request_mock.await_count == 1


@pytest.mark.asyncio
async def test_server_time_out_of_range_rejected() -> None:
    # A syntactically numeric but impossible timestamp must fail through the
    # project-owned malformed-data boundary, not leak OverflowError.
    provider, _ = _build_provider([_response(200, {"serverTime": 10**30})])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_server_time()
    finally:
        await provider.close()


def _exchange_info_response(symbol_info: Any) -> httpx.Response:
    return _response(200, {"symbols": [symbol_info]})


def _valid_symbol_info() -> dict[str, Any]:
    return {
        "symbol": "BTCEUR",
        "status": "TRADING",
        "baseAsset": "BTC",
        "quoteAsset": "EUR",
        "filters": [
            {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
            {
                "filterType": "LOT_SIZE",
                "stepSize": "0.000001",
                "minQty": "0.000001",
                "maxQty": "9000.00000000",
            },
            {"filterType": "MIN_NOTIONAL", "minNotional": "5.00"},
        ],
    }


@pytest.mark.asyncio
async def test_symbol_metadata_ok() -> None:
    provider, _ = _build_provider([_exchange_info_response(_valid_symbol_info())])
    try:
        metadata = await provider.get_symbol_metadata("BTCEUR")
    finally:
        await provider.close()
    assert metadata.symbol == "BTCEUR"
    assert metadata.base_asset == "BTC"
    assert metadata.quote_asset == "EUR"
    assert metadata.max_quantity == 9000


@pytest.mark.asyncio
async def test_symbol_metadata_non_dict_response_rejected() -> None:
    provider, _ = _build_provider([_response(200, [])])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_symbol_metadata("BTCEUR")
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_symbol_metadata_non_object_entry_rejected() -> None:
    provider, _ = _build_provider([_exchange_info_response("BTCEUR")])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_symbol_metadata("BTCEUR")
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_symbol_metadata_missing_identity_rejected() -> None:
    info = _valid_symbol_info()
    info.pop("baseAsset")
    provider, _ = _build_provider([_exchange_info_response(info)])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_symbol_metadata("BTCEUR")
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_symbol_metadata_missing_max_qty_rejected() -> None:
    info = _valid_symbol_info()
    lot = next(f for f in info["filters"] if f["filterType"] == "LOT_SIZE")
    lot.pop("maxQty")
    provider, _ = _build_provider([_exchange_info_response(info)])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_symbol_metadata("BTCEUR")
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_symbol_metadata_non_finite_tick_size_rejected() -> None:
    info = _valid_symbol_info()
    price = next(f for f in info["filters"] if f["filterType"] == "PRICE_FILTER")
    price["tickSize"] = "NaN"
    provider, _ = _build_provider([_exchange_info_response(info)])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_symbol_metadata("BTCEUR")
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_symbol_metadata_inverted_quantity_range_rejected() -> None:
    info = _valid_symbol_info()
    lot = next(f for f in info["filters"] if f["filterType"] == "LOT_SIZE")
    lot["minQty"] = "10.0"
    lot["maxQty"] = "1.0"
    provider, _ = _build_provider([_exchange_info_response(info)])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_symbol_metadata("BTCEUR")
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_kline_invalid_json_classified_as_malformed() -> None:
    provider, _ = _build_provider([_response(200, "not json")])
    try:
        with pytest.raises(BinanceMalformedDataError):
            await provider.get_finalized_candles(
                symbol="BTCEUR",
                interval=__import__(
                    "app.infrastructure.exchange.binance.protocol",
                    fromlist=["CandleInterval"],
                ).CandleInterval.ONE_HOUR,
                start_time=FIXED_TIME - timedelta(hours=1),
                end_time=FIXED_TIME,
            )
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_retry_count_sums_across_sequential_calls() -> None:
    provider, _ = _build_provider(
        [
            _response(503, {"msg": "busy"}),
            _response(200, {"serverTime": int(FIXED_TIME.timestamp() * 1000)}),
            _response(503, {"msg": "busy"}),
            _response(200, {"serverTime": int(FIXED_TIME.timestamp() * 1000)}),
        ]
    )
    try:
        await provider.get_server_time()
        first_count = provider.retry_count
        await provider.get_server_time()
        assert provider.retry_count >= first_count + 1
    finally:
        await provider.close()


def _kline_row(open_time: datetime, close_time: datetime) -> list[Any]:
    return [
        int(open_time.timestamp() * 1000),
        "100.00",
        "105.00",
        "95.00",
        "102.00",
        "1.5",
        int(close_time.timestamp() * 1000),
        "1500.0",
        100,
        "0.75",
        "1125.0",
        "0",
    ]


def _kline_response(rows: list[list[Any]]) -> httpx.Response:
    return httpx.Response(
        status_code=200,
        json=rows,
        request=httpx.Request("GET", "/api/v3/klines"),
    )


@pytest.mark.asyncio
async def test_kline_429_retried_then_succeeds() -> None:
    provider, request_mock = _build_provider(
        [
            httpx.Response(
                status_code=429,
                headers={"Retry-After": "1"},
                request=httpx.Request("GET", "/api/v3/klines"),
            ),
            _kline_response(
                [
                    _kline_row(
                        FIXED_TIME - timedelta(hours=1),
                        FIXED_TIME,
                    )
                ]
            ),
        ]
    )
    try:
        candles = await provider.get_finalized_candles(
            symbol="BTCEUR",
            interval=__import__(
                "app.infrastructure.exchange.binance.protocol",
                fromlist=["CandleInterval"],
            ).CandleInterval.ONE_HOUR,
            start_time=FIXED_TIME - timedelta(hours=1),
            end_time=FIXED_TIME,
        )
    finally:
        await provider.close()
    assert request_mock.await_count == 2
    assert provider.retry_count >= 1
    assert len(candles) == 1
    assert candles[0].time == FIXED_TIME - timedelta(hours=1)


@pytest.mark.asyncio
async def test_kline_429_retry_after_honored() -> None:
    provider, request_mock = _build_provider(
        [
            httpx.Response(
                status_code=429,
                headers={"Retry-After": "5"},
                request=httpx.Request("GET", "/api/v3/klines"),
            ),
            _kline_response(
                [
                    _kline_row(
                        FIXED_TIME - timedelta(hours=1),
                        FIXED_TIME,
                    )
                ]
            ),
        ]
    )
    try:
        candles = await provider.get_finalized_candles(
            symbol="BTCEUR",
            interval=__import__(
                "app.infrastructure.exchange.binance.protocol",
                fromlist=["CandleInterval"],
            ).CandleInterval.ONE_HOUR,
            start_time=FIXED_TIME - timedelta(hours=1),
            end_time=FIXED_TIME,
        )
    finally:
        await provider.close()
    assert request_mock.await_count == 2
    assert provider.retry_count >= 1
    assert provider.last_retry_wait_ms is not None
    assert provider.last_retry_wait_ms >= 5000
    assert len(candles) == 1


@pytest.mark.asyncio
async def test_kline_429_exhausted_retries() -> None:
    provider, request_mock = _build_provider(
        [
            httpx.Response(
                status_code=429,
                request=httpx.Request("GET", "/api/v3/klines"),
            ),
            httpx.Response(
                status_code=429,
                request=httpx.Request("GET", "/api/v3/klines"),
            ),
            httpx.Response(
                status_code=429,
                request=httpx.Request("GET", "/api/v3/klines"),
            ),
        ]
    )
    try:
        from app.infrastructure.exchange.binance.protocol import (
            BinanceRateLimitError,
        )

        with pytest.raises(BinanceRateLimitError):
            await provider.get_finalized_candles(
                symbol="BTCEUR",
                interval=__import__(
                    "app.infrastructure.exchange.binance.protocol",
                    fromlist=["CandleInterval"],
                ).CandleInterval.ONE_HOUR,
                start_time=FIXED_TIME - timedelta(hours=1),
                end_time=FIXED_TIME,
            )
    finally:
        await provider.close()
    assert request_mock.await_count == 3
    assert provider.retry_count >= 2


@pytest.mark.asyncio
async def test_kline_timeout_retried_then_succeeds() -> None:
    provider, request_mock = _build_provider(
        [
            httpx.Response(
                status_code=200,
                request=httpx.Request("GET", "/api/v3/klines"),
            ),
        ]
    )
    request_mock.side_effect = [
        httpx.TimeoutException("timeout"),
        httpx.Response(
            status_code=200,
            json=[
                _kline_row(
                    FIXED_TIME - timedelta(hours=1),
                    FIXED_TIME,
                )
            ],
            request=httpx.Request("GET", "/api/v3/klines"),
        ),
    ]
    try:
        candles = await provider.get_finalized_candles(
            symbol="BTCEUR",
            interval=__import__(
                "app.infrastructure.exchange.binance.protocol",
                fromlist=["CandleInterval"],
            ).CandleInterval.ONE_HOUR,
            start_time=FIXED_TIME - timedelta(hours=1),
            end_time=FIXED_TIME,
        )
    finally:
        await provider.close()
    assert request_mock.await_count == 2
    assert provider.retry_count >= 1
    assert len(candles) == 1


@pytest.mark.asyncio
async def test_kline_timeout_exhausted_fails() -> None:
    provider, request_mock = _build_provider(
        [
            httpx.Response(
                status_code=200,
                request=httpx.Request("GET", "/api/v3/klines"),
            ),
        ]
    )
    request_mock.side_effect = [
        httpx.TimeoutException("timeout"),
        httpx.TimeoutException("timeout"),
        httpx.TimeoutException("timeout"),
    ]
    try:
        from app.infrastructure.exchange.binance.protocol import (
            BinanceTimeoutError,
        )

        with pytest.raises(BinanceTimeoutError):
            await provider.get_finalized_candles(
                symbol="BTCEUR",
                interval=__import__(
                    "app.infrastructure.exchange.binance.protocol",
                    fromlist=["CandleInterval"],
                ).CandleInterval.ONE_HOUR,
                start_time=FIXED_TIME - timedelta(hours=1),
                end_time=FIXED_TIME,
            )
    finally:
        await provider.close()
    assert request_mock.await_count == 3
    assert provider.retry_count >= 2


@pytest.mark.asyncio
async def test_kline_pagination_no_gap_no_duplicate() -> None:
    # Two pages of 1000 candles each with exact 1h boundary; page-2 starts
    # at last.close_time + 1h and must not duplicate or skip.
    page1 = [
        _kline_row(
            FIXED_TIME - timedelta(hours=2000 - i),
            FIXED_TIME - timedelta(hours=1999 - i),
        )
        for i in range(1000)
    ]
    page2 = [
        _kline_row(
            FIXED_TIME - timedelta(hours=1000 - i),
            FIXED_TIME - timedelta(hours=999 - i),
        )
        for i in range(1000)
    ]
    provider = BinanceRestProvider(
        clock=FixedClock(FIXED_TIME),
        max_retries=3,
    )
    request_mock = AsyncMock(
        side_effect=[
            _kline_response(page1),
            _kline_response(page2),
        ]
    )
    provider._client.request = request_mock  # type: ignore[method-assign]
    try:
        candles = await provider.get_finalized_candles(
            symbol="BTCEUR",
            interval=__import__(
                "app.infrastructure.exchange.binance.protocol",
                fromlist=["CandleInterval"],
            ).CandleInterval.ONE_HOUR,
            start_time=FIXED_TIME - timedelta(hours=2000),
            end_time=FIXED_TIME,
        )
    finally:
        await provider.close()
    assert request_mock.await_count == 2
    assert len(candles) == 2000
    times = [c.time for c in candles]
    assert times[0] == FIXED_TIME - timedelta(hours=2000)
    assert times[-1] == FIXED_TIME - timedelta(hours=1)
    assert len(set(times)) == 2000
