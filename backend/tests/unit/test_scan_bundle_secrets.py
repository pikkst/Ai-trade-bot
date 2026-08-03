"""Unit tests for the frontend bundle secret scanner.

Verifies that the scanner correctly detects server-only environment variable
names and the sentinel secret value when they are present in the bundle output.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_scanner() -> ModuleType:
    scanner_path = (
        Path(__file__).parents[3]
        / "infrastructure"
        / "scripts"
        / "scan_bundle_secrets.py"
    )
    spec = importlib.util.spec_from_file_location("scan_bundle_secrets", scanner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scanner_passes_on_clean_bundle(tmp_path: Path) -> None:
    scanner = load_scanner()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html>clean content</html>", encoding="utf-8")
    (dist / "app.js").write_text('console.log("hello")', encoding="utf-8")

    failures = scanner.scan_bundle(dist)
    assert failures == []


def test_scanner_detects_server_only_name(tmp_path: Path) -> None:
    scanner = load_scanner()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "app.js").write_text(
        'const url = "postgres://user:pass@localhost"; const k = DATABASE_URL;',
        encoding="utf-8",
    )

    failures = scanner.scan_bundle(dist)
    assert any("DATABASE_URL" in f for f in failures)


def test_scanner_detects_sentinel_secret(tmp_path: Path) -> None:
    scanner = load_scanner()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "app.js").write_text(
        f'const secret = "{scanner.SENTINEL_SECRET_VALUE}";',
        encoding="utf-8",
    )

    failures = scanner.scan_bundle(dist)
    assert any(scanner.SENTINEL_SECRET_VALUE in f for f in failures)


def test_scanner_ignores_css_and_maps(tmp_path: Path) -> None:
    scanner = load_scanner()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "styles.css").write_text(
        'background-image: url("DATABASE_URL.png");',
        encoding="utf-8",
    )
    (dist / "app.js").write_text('console.log("clean")', encoding="utf-8")

    failures = scanner.scan_bundle(dist)
    assert failures == []


def test_scanner_fails_on_missing_dist(tmp_path: Path) -> None:
    scanner = load_scanner()
    failures = scanner.scan_bundle(tmp_path / "nonexistent")
    assert any("does not exist" in f for f in failures)
