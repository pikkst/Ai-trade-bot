"""Project-owned provider composition for local development and tests."""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.clock import DeterministicIdGenerator, IdGenerator
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

FIXTURE_TIME = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)
FIXTURE_VERSION = "2026-08-07-m006-v1"


def create_binance_provider(
    scenario: str | FakeBinanceScenario = FakeBinanceScenario.SUCCESS,
    *,
    fixed_clock_time: datetime | None = FIXTURE_TIME,
) -> FakeBinanceProvider:
    if isinstance(scenario, str):
        scenario = FakeBinanceScenario(scenario)
    return FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=scenario,
            fixed_clock_time=fixed_clock_time,
            fixture_version=FIXTURE_VERSION,
        )
    )


def create_gemini_provider(
    scenario: str | FakeGeminiScenario = FakeGeminiScenario.SUCCESS,
    *,
    fixed_clock_time: datetime | None = FIXTURE_TIME,
    id_generator: IdGenerator | None = None,
) -> FakeGeminiProvider:
    if isinstance(scenario, str):
        scenario = FakeGeminiScenario(scenario)
    if id_generator is None:
        id_generator = DeterministicIdGenerator()
    return FakeGeminiProvider(
        config=FakeGeminiConfig(
            scenario=scenario,
            fixed_clock_time=fixed_clock_time,
            fixture_version=FIXTURE_VERSION,
        ),
        id_generator=id_generator,
    )


def create_providers(
    binance_scenario: str | FakeBinanceScenario = FakeBinanceScenario.SUCCESS,
    gemini_scenario: str | FakeGeminiScenario = FakeGeminiScenario.SUCCESS,
    *,
    fixed_clock_time: datetime | None = FIXTURE_TIME,
) -> tuple[FakeBinanceProvider, FakeGeminiProvider]:
    return (
        create_binance_provider(binance_scenario, fixed_clock_time=fixed_clock_time),
        create_gemini_provider(gemini_scenario, fixed_clock_time=fixed_clock_time),
    )
