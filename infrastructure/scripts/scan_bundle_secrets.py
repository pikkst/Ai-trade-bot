"""Scan the frontend production bundle for server-only secrets and sentinel values.

This gate enforces the M004/M028 verification requirement that no server-secret
environment variable name or value enters the browser bundle. Vite's default
``VITE_`` prefix provides first-line defense, but this scanner adds explicit,
verifiable bundle-level protection against a server secret incorrectly prefixed
with ``VITE_``.

Usage:
    python infrastructure/scripts/scan_bundle_secrets.py frontend/dist
"""

from __future__ import annotations

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

SENTINEL_SECRET_VALUE = "SENTINEL_SECRET_LEAK_TEST_DO_NOT_USE"

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
    """Return a list of failure messages for a single file."""
    failures: list[str] = []
    ext = path.suffix.lower()
    if ext in IGNORED_EXTENSIONS:
        return failures

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return failures

    for name in SERVER_ONLY_NAMES:
        if name in content:
            failures.append(f"{path}: contains forbidden server-only name '{name}'")

    if SENTINEL_SECRET_VALUE in content:
        failures.append(
            f"{path}: contains sentinel secret value '{SENTINEL_SECRET_VALUE}'"
        )

    return failures


def scan_bundle(dist_dir: Path) -> list[str]:
    failures: list[str] = []
    if not dist_dir.is_dir():
        failures.append(f"Bundle directory does not exist: {dist_dir}")
        return failures

    for js_file in dist_dir.rglob("*"):
        if js_file.is_file() and js_file.suffix in (".js", ".html", ""):
            failures.extend(scan_file(js_file))

    return failures


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: scan_bundle_secrets.py <frontend/dist>", file=sys.stderr)
        return 2

    dist_dir = Path(sys.argv[1])
    failures = scan_bundle(dist_dir)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print("Bundle secret scan passed: no server-only secrets detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
