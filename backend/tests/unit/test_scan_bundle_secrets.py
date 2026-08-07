"""Unit tests for the frontend bundle secret scanner."""

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


def make_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    dist.mkdir()
    return dist


def test_scanner_passes_on_clean_bundle(tmp_path: Path) -> None:
    scanner = load_scanner()
    dist = make_dist(tmp_path)
    (dist / "index.html").write_text("<html>clean content</html>", encoding="utf-8")
    (dist / "app.js").write_text('console.log("hello")', encoding="utf-8")

    assert scanner.scan_bundle(dist) == []


def test_scanner_detects_server_only_name(tmp_path: Path) -> None:
    scanner = load_scanner()
    dist = make_dist(tmp_path)
    (dist / "app.js").write_text("const config = 'VITE_DATABASE_URL';", encoding="utf-8")

    failures = scanner.scan_bundle(dist)
    assert any("DATABASE_URL" in failure for failure in failures)


def test_scanner_detects_build_canary_value(tmp_path: Path) -> None:
    scanner = load_scanner()
    dist = make_dist(tmp_path)
    (dist / "app.js").write_text(
        f'const value = "{scanner.BUNDLE_CANARY_VALUE}";', encoding="utf-8"
    )

    failures = scanner.scan_bundle(dist)
    assert any(scanner.BUNDLE_CANARY_VALUE in failure for failure in failures)


def test_scanner_detects_credential_value_without_variable_name(tmp_path: Path) -> None:
    scanner = load_scanner()
    dist = make_dist(tmp_path)
    (dist / "app.js").write_text(
        'const value = "postgresql://browser_user:unsafe_value@db.example/app";',
        encoding="utf-8",
    )

    failures = scanner.scan_bundle(dist)
    assert any("PostgreSQL connection URL" in failure for failure in failures)


def test_scanner_ignores_non_executable_assets(tmp_path: Path) -> None:
    scanner = load_scanner()
    dist = make_dist(tmp_path)
    (dist / "styles.css").write_text(
        'background-image: url("DATABASE_URL.png");', encoding="utf-8"
    )
    (dist / "app.js.map").write_text("DATABASE_URL", encoding="utf-8")
    (dist / "app.js").write_text('console.log("clean")', encoding="utf-8")

    assert scanner.scan_bundle(dist) == []


def test_scanner_fails_on_missing_dist(tmp_path: Path) -> None:
    scanner = load_scanner()
    failures = scanner.scan_bundle(tmp_path / "nonexistent")
    assert any("does not exist" in failure for failure in failures)
