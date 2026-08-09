"""Unit tests for the production Binance REST provider (M007)."""

from __future__ import annotations

from datetime import datetime, timezone
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
