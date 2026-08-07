"""Project-owned provider composition for local development and tests."""

from __future__ import annotations

from app.infrastructure.ai.fakes import (
    FakeGeminiConfig,
    FakeGeminiProvider,
    FakeGeminiScenario,
)
from app.infrastructure.exchange.binance.fakes import (
    FakeBinanceConfig,
    FakeBinanceProvider,
    FakeBinanceScenario,
)


def create_binance_provider(
    scenario: str | FakeBinanceScenario = FakeBinanceScenario.SUCCESS,
) -> FakeBinanceProvider:
    if isinstance(scenario, str):
        scenario = FakeBinanceScenario(scenario)
    return FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=scenario,
            fixture_version="2026-08-07-m006-v1",
        )
    )


def create_gemini_provider(
    scenario: str | FakeGeminiScenario = FakeGeminiScenario.SUCCESS,
) -> FakeGeminiProvider:
    if isinstance(scenario, str):
        scenario = FakeGeminiScenario(scenario)
    return FakeGeminiProvider(
        config=FakeGeminiConfig(
            scenario=scenario,
            fixture_version="2026-08-07-m006-v1",
        )
    )


def create_providers(
    binance_scenario: str | FakeBinanceScenario = FakeBinanceScenario.SUCCESS,
    gemini_scenario: str | FakeGeminiScenario = FakeGeminiScenario.SUCCESS,
) -> tuple[FakeBinanceProvider, FakeGeminiProvider]:
    return (
        create_binance_provider(binance_scenario),
        create_gemini_provider(gemini_scenario),
    )
