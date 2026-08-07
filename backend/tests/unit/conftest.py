"""Unit-test suite network guard.

Block unexpected outbound network calls in unit tests so provider fakes
remain the only allowed path. Loopback connections are allowed because
Windows asyncio uses them for internal event-loop plumbing.
"""

from __future__ import annotations

import socket
from typing import Any

import pytest


def _is_loopback(address: Any) -> bool:
    try:
        host = address[0] if isinstance(address, tuple) else str(address).split(":")[0]
        return host in ("127.0.0.1", "::1", "localhost")
    except Exception:
        return False


@pytest.fixture(autouse=True)
def _block_unit_test_network(monkeypatch: pytest.MonkeyPatch) -> None:
    original_connect = socket.socket.connect
    original_create_connection = socket.create_connection
    original_sendto = socket.socket.sendto
    original_getaddrinfo = socket.getaddrinfo

    def blocked_connect(self: Any, address: Any) -> None:
        if _is_loopback(address):
            original_connect(self, address)
            return
        raise ConnectionError("Unit tests must not open network connections")

    def blocked_create_connection(
        address: Any,
        timeout: Any = None,
        source_address: Any = None,
        *,
        all_errors: bool = False,
    ) -> None:
        if _is_loopback(address):
            original_create_connection(
                address,
                timeout=timeout,
                source_address=source_address,
                all_errors=all_errors,
            )
            return
        raise ConnectionError("Unit tests must not open network connections")

    def blocked_sendto(self: Any, data: Any, address: Any) -> int:
        if _is_loopback(address):
            return original_sendto(self, data, address)
        raise ConnectionError("Unit tests must not open network connections")

    def blocked_getaddrinfo(
        host: str,
        port: str | int | None = None,
        family: int = 0,
        type: int = 0,
        proto: int = 0,
        flags: int = 0,
    ) -> list[Any]:
        if host in ("127.0.0.1", "::1", "localhost"):
            return original_getaddrinfo(
                host, port, family=family, type=type, proto=proto, flags=flags
            )
        raise ConnectionError("Unit tests must not open network connections")

    monkeypatch.setattr(socket.socket, "connect", blocked_connect)
    monkeypatch.setattr(socket, "create_connection", blocked_create_connection)
    monkeypatch.setattr(socket.socket, "sendto", blocked_sendto)
    monkeypatch.setattr(socket, "getaddrinfo", blocked_getaddrinfo)
