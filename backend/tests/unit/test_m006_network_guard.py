"""Tests for unit-test network guard."""

from __future__ import annotations

import pytest


def test_network_guard_blocks_non_loopback_connections() -> None:
    socket_module = pytest.importorskip("socket")
    with pytest.raises(
        ConnectionError, match="Unit tests must not open network connections"
    ):
        socket_module.create_connection(("8.8.8.8", 53))


def test_network_guard_blocks_udp_sendto() -> None:
    socket_module = pytest.importorskip("socket")
    sock = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_DGRAM)
    try:
        with pytest.raises(
            ConnectionError, match="Unit tests must not open network connections"
        ):
            sock.sendto(b"ping", ("8.8.8.8", 53))
    finally:
        sock.close()


def test_network_guard_blocks_dns_getaddrinfo() -> None:
    socket_module = pytest.importorskip("socket")
    with pytest.raises(
        ConnectionError, match="Unit tests must not open network connections"
    ):
        socket_module.getaddrinfo("example.com", 80)
