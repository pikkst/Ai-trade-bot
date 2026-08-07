"""Typed, fail-closed application settings for The Daily Roast AI."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, model_validator

Environment = Literal[
    "development",
    "test",
    "ci",
    "free_cloud",
    "staging",
    "production",
]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
AIProvider = Literal["fake", "gemini"]


class SettingsError(RuntimeError):
    """Raised when runtime configuration is invalid or unsafe."""


class AppSettings(BaseModel):
    """Validated application settings with paper-only safety invariants."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: Environment = "development"
    service_name: str = "the-daily-roast-api"
    log_level: LogLevel = "INFO"
    database_url: SecretStr = SecretStr(
        "postgresql+psycopg://app_runtime:app-runtime-local-only@127.0.0.1:54322/postgres"
    )
    ai_provider: AIProvider = "fake"
    gemini_enabled: bool = False
    allow_paid_provider_usage: bool = False
    live_trading_enabled: bool = False
    binance_test_trading_enabled: bool = False
    private_binance_api_enabled: bool = False
    exchange_order_execution_enabled: bool = False
    health_database_check: bool = False
    max_request_id_length: int = Field(default=128, ge=16, le=256)

    @model_validator(mode="after")
    def enforce_mvp_safety(self) -> AppSettings:
        """Reject capabilities that are forbidden for the paper-only MVP."""
        prohibited = {
            "LIVE_TRADING_ENABLED": self.live_trading_enabled,
            "BINANCE_TEST_TRADING_ENABLED": self.binance_test_trading_enabled,
            "PRIVATE_BINANCE_API_ENABLED": self.private_binance_api_enabled,
            "EXCHANGE_ORDER_EXECUTION_ENABLED": self.exchange_order_execution_enabled,
        }
        enabled = [name for name, value in prohibited.items() if value]
        if enabled:
            raise ValueError(
                "paper-only MVP prohibits: " + ", ".join(sorted(enabled))
            )
        if self.environment in {"ci", "test"} and (
            self.gemini_enabled
            or self.ai_provider != "fake"
            or self.allow_paid_provider_usage
        ):
            raise ValueError("CI and tests require the fake AI provider with paid usage disabled")
        if self.ai_provider == "gemini" and not self.gemini_enabled:
            raise ValueError("AI_PROVIDER=gemini requires GEMINI_ENABLED=true")
        if self.gemini_enabled and not self.allow_paid_provider_usage:
            raise ValueError("GEMINI_ENABLED=true requires ALLOW_PAID_PROVIDER_USAGE=true")
        return self

    def safe_summary(self) -> dict[str, object]:
        """Return log-safe settings without secret values."""
        return {
            "environment": self.environment,
            "service_name": self.service_name,
            "log_level": self.log_level,
            "ai_provider": self.ai_provider,
            "gemini_enabled": self.gemini_enabled,
            "allow_paid_provider_usage": self.allow_paid_provider_usage,
            "live_trading_enabled": self.live_trading_enabled,
            "binance_test_trading_enabled": self.binance_test_trading_enabled,
            "private_binance_api_enabled": self.private_binance_api_enabled,
            "exchange_order_execution_enabled": self.exchange_order_execution_enabled,
            "health_database_check": self.health_database_check,
        }


_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def _read_bool(value: str, *, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise SettingsError(f"{name} must be one of true/false, 1/0, yes/no, on/off")


def load_settings(environ: Mapping[str, str] | None = None) -> AppSettings:
    """Load only project-owned environment keys and validate them strictly."""
    source = os.environ if environ is None else environ
    data: dict[str, object] = {}
    aliases: dict[str, str] = {
        "APP_ENV": "environment",
        "SERVICE_NAME": "service_name",
        "APP_LOG_LEVEL": "log_level",
        "DATABASE_URL": "database_url",
        "AI_PROVIDER": "ai_provider",
        "MAX_REQUEST_ID_LENGTH": "max_request_id_length",
    }
    bool_aliases: dict[str, str] = {
        "GEMINI_ENABLED": "gemini_enabled",
        "ALLOW_PAID_PROVIDER_USAGE": "allow_paid_provider_usage",
        "LIVE_TRADING_ENABLED": "live_trading_enabled",
        "BINANCE_TEST_TRADING_ENABLED": "binance_test_trading_enabled",
        "PRIVATE_BINANCE_API_ENABLED": "private_binance_api_enabled",
        "EXCHANGE_ORDER_EXECUTION_ENABLED": "exchange_order_execution_enabled",
        "HEALTH_DATABASE_CHECK": "health_database_check",
    }
    for env_name, field_name in aliases.items():
        if env_name in source:
            data[field_name] = source[env_name]
    for env_name, field_name in bool_aliases.items():
        if env_name in source:
            data[field_name] = _read_bool(source[env_name], name=env_name)
    try:
        return AppSettings.model_validate(data)
    except ValidationError as error:
        safe_errors = [
            {"loc": item["loc"], "type": item["type"], "msg": item["msg"]}
            for item in error.errors()
        ]
        raise SettingsError(f"Invalid application configuration: {safe_errors}") from error
