from __future__ import annotations

import sys

import pytest
from fastapi.testclient import TestClient

from app.cli.run_research_cycle import main as research_cycle_main
from app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "The Daily Roast AI"
    assert response.json()["environment"] in {"local", "development"}


def test_research_cycle_scaffold_is_deterministic(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_research_cycle",
            "--experiment-id",
            "example",
            "--occurrence",
            "2026-01-01T00:00:00Z",
        ],
    )

    assert research_cycle_main() == 0
    assert "deterministic fallback" in capsys.readouterr().out
