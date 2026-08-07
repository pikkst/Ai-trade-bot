"""Scan the frontend production bundle for server-only data leakage.

This gate enforces the M004 verification requirement that server-only
configuration does not enter browser artifacts. Vite's ``VITE_`` prefix is the
first line of defense; this scanner provides a second bundle-level gate for
forbidden server-only names, obvious credential material, and an explicit
build canary used by tests/CI.

Usage:
    python infrastructure/scripts/scan_bundle_secrets.py frontend/dist
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SERVER_ONLY_NAMES: set[str] = {
    "ALLOW_PAID_PROVIDER_USAGE",
    "ALLOW_AUTOMATIC_PROVIDER_UPGRADE",
    "AI_DATABASE_MUTATION_ENABLED",
    "AI_ORDER_EXECUTION_ENABLED",
    "AI_TOOL_CALLING_ENABLED",
    "ARQ_ENABLED",
    "APP_SECRET",
    "AUTOMATIC_BEHAVIOR_ACTIVATION_ENABLED",
    "AUTOMATIC_PLAN_UPGRADE_ENABLED",
    "AUTOMATIC_PROVIDER_UPGRADE_ENABLED",
    "AUTOMATIC_RELEASE_APPROVAL_ENABLED",
    "AUTOMATIC_SCALING_ENABLED",
    "AUTOMATIC_STRATEGY_PROMOTION_ENABLED",
    "BINANCE_API_KEY",
    "BINANCE_API_SECRET",
    "BINANCE_TEST_TRADING_ENABLED",
    "CORS_ALLOWED_ORIGINS",
    "DATABASE_URL",
    "DB_PASSWORD",
    "EXCHANGE_ORDER_EXECUTION_ENABLED",
    "FUTURES_ENABLED",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "GEMINI_PROMPT_VERSION",
    "GEMINI_REPORT_SCHEMA_VERSION",
    "GEMINI_SAFETY_CONFIG_VERSION",
    "GEMINI_VALIDATION_POLICY_VERSION",
    "HOSTED_GRAFANA_ENABLED",
    "HOSTED_PROMETHEUS_ENABLED",
    "JWT_SECRET",
    "LEVERAGE_ENABLED",
    "LIVE_TRADING_ENABLED",
    "MARGIN_ENABLED",
    "OPTIONS_ENABLED",
    "PERSISTENT_WORKER_ENABLED",
    "PRIVATE_BINANCE_API_ENABLED",
    "REDIS_ENABLED",
    "SCHEDULER_MODE",
    "SECRET_KEY",
    "SHORTING_ENABLED",
    "SUPABASE_JWKS_URL",
    "SUPABASE_JWT_ISSUER",
    "SUPABASE_SERVICE_ROLE_KEY",
    "WEBHOOK_SECRET",
    "WITHDRAWALS_ENABLED",
}

# This is deliberately non-secret test data. A production build can inject it
# into VITE_* variables to prove that accidental client exposure is detected.
BUNDLE_CANARY_VALUE = "BUNDLE_CANARY_DO_NOT_SHIP"

CREDENTIAL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("PostgreSQL connection URL", re.compile(r"postgres(?:ql)?://[^\s\"']+", re.I)),
    ("Bearer token", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I)),
    (
        "JWT-like token",
        re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    ),
)

IGNORED_EXTENSIONS: set[str] = {
    ".map",
    ".css",
    ".woff2",
    ".woff",
    ".ttf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
}


def scan_file(path: Path) -> list[str]:
    """Return bundle-leak findings for one text-like artifact."""
    if path.suffix.lower() in IGNORED_EXTENSIONS:
        return []

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    failures: list[str] = []

    for name in sorted(SERVER_ONLY_NAMES):
        if name in content or f"VITE_{name}" in content:
            failures.append(f"{path}: contains forbidden server-only name '{name}'")

    if BUNDLE_CANARY_VALUE in content:
        failures.append(
            f"{path}: contains frontend leak canary '{BUNDLE_CANARY_VALUE}'"
        )

    for label, pattern in CREDENTIAL_PATTERNS:
        if pattern.search(content):
            failures.append(f"{path}: contains credential-like material ({label})")

    return failures


def scan_bundle(dist_dir: Path) -> list[str]:
    """Scan JavaScript/HTML bundle outputs and return all findings."""
    if not dist_dir.is_dir():
        return [f"Bundle directory does not exist: {dist_dir}"]

    failures: list[str] = []
    for artifact in dist_dir.rglob("*"):
        if artifact.is_file() and artifact.suffix.lower() in {
            ".js",
            ".mjs",
            ".cjs",
            ".html",
            "",
        }:
            failures.extend(scan_file(artifact))
    return failures


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: scan_bundle_secrets.py <frontend/dist>", file=sys.stderr)
        return 2

    failures = scan_bundle(Path(sys.argv[1]))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print("Bundle secret scan passed: no server-only material detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
