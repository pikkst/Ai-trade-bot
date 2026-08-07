"""Versioned provider fixtures and scenario configurations."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.core.clock import DeterministicIdGenerator, FixedClock
from app.infrastructure.ai.fakes import FakeGeminiConfig, FakeGeminiProvider
from app.infrastructure.ai.protocol import (
    AiBudgetDecision,
    AnalysisRequest,
)
from app.infrastructure.exchange.binance.fakes import (
    FakeBinanceConfig,
    FakeBinanceProvider,
)
from app.request_context import ExecutionContext

FIXED_TIME = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)


def make_fixed_clock() -> FixedClock:
    return FixedClock(FIXED_TIME)


def make_deterministic_id_generator() -> DeterministicIdGenerator:
    return DeterministicIdGenerator(prefix="test-")


def make_binance_provider(
    scenario: str = "success",
) -> FakeBinanceProvider:
    return FakeBinanceProvider(
        config=FakeBinanceConfig(
            scenario=scenario,
            fixed_clock_time=FIXED_TIME,
        )
    )


def make_gemini_provider(
    scenario: str = "success",
) -> FakeGeminiProvider:
    return FakeGeminiProvider(
        config=FakeGeminiConfig(
            scenario=scenario,
            fixed_clock_time=FIXED_TIME,
        )
    )


def make_analysis_request(
    analysis_run_id: str = "run-00000001",
    snapshot_id: str = "snap-00000001",
    snapshot_hash: str = "a" * 64,
) -> AnalysisRequest:
    return AnalysisRequest(
        analysis_run_id=analysis_run_id,
        snapshot_id=snapshot_id,
        snapshot_hash=snapshot_hash,
        symbol="BTCEUR",
        interval="1h",
        analysis_time=FIXED_TIME,
        features={
            "ema_50": Decimal("50000.00"),
            "ema_200": Decimal("49000.00"),
            "rsi_14": Decimal("55.0"),
            "atr_14": Decimal("500.00"),
        },
        prompt_version="1.0",
        schema_version="1.0",
        provider_config_version="1.0",
        budget_decision=AiBudgetDecision(
            allowed=True,
            reason="Fixture budget",
            remaining_requests=100,
            remaining_tokens=10000,
            remaining_cost=Decimal("5.00"),
        ),
        context=ExecutionContext(
            correlation_id="corr-fixture",
            request_id="req-fixture",
            job_id="job-fixture",
            cycle_id="cycle-fixture",
        ),
    )
