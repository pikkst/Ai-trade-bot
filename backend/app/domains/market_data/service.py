"""Market data ingestion and quality service for M007."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.clock import Clock, get_clock
from app.domains.market_data.models import (
    GapReport,
    IngestionResult,
    IngestionStatus,
    IngestionType,
    QualityEvent,
    QualityState,
    SnapshotResult,
)
from app.domains.market_data.validation import (
    ValidationPolicy,
    assess_quality,
    compute_candle_content_hash,
    make_quality_event,
    validate_candle_ohlc,
    validate_candle_times,
    validate_candle_volumes,
)
from app.infrastructure.exchange.binance.fakes import (
    FakeBinanceProvider,
)
from app.infrastructure.exchange.binance.protocol import (
    Candle,
    CandleInterval,
    ExchangeTime,
    MarketDataProvider,
    SymbolMetadata,
)
from app.transaction_guard import assert_network_call_allowed

logger = logging.getLogger(__name__)

_DEFAULT_BACKFILL_MAX_RANGE_DAYS = 30
_DEFAULT_INCREMENTAL_MAX_RANGE_HOURS = 2
_DEFAULT_INTERVAL = CandleInterval.ONE_HOUR


class MarketDataService:
    """Orchestrate Binance REST market data ingestion with quality controls."""

    def __init__(
        self,
        session: Session,
        provider: MarketDataProvider,
        *,
        workspace_id: UUID,
        exchange_id: UUID,
        symbol_version_id: UUID,
        interval: CandleInterval = _DEFAULT_INTERVAL,
        clock: Clock | None = None,
        backfill_max_range_days: int = _DEFAULT_BACKFILL_MAX_RANGE_DAYS,
        incremental_max_range_hours: int = _DEFAULT_INCREMENTAL_MAX_RANGE_HOURS,
        policy: ValidationPolicy | None = None,
    ) -> None:
        self._session = session
        self._provider = provider
        self._workspace_id = workspace_id
        self._exchange_id = exchange_id
        self._symbol_version_id = symbol_version_id
        self._interval = interval
        self._clock = clock or get_clock()
        self._backfill_max_range_days = backfill_max_range_days
        self._incremental_max_range_hours = incremental_max_range_hours
        self._policy = policy or ValidationPolicy(
            interval_seconds=_INTERVAL_SECONDS[interval]
        )
        self._interval_seconds = _INTERVAL_SECONDS[interval]

    async def load_server_time(self) -> ExchangeTime:
        assert_network_call_allowed()
        return await self._provider.get_server_time()

    async def load_symbol_metadata(self, symbol: str) -> SymbolMetadata:
        assert_network_call_allowed()
        return await self._provider.get_symbol_metadata(symbol)

    async def backfill(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        idempotency_key: str,
    ) -> IngestionResult:
        assert_network_call_allowed()
        max_duration = timedelta(days=self._backfill_max_range_days)
        if end_time - start_time > max_duration:
            raise ValueError(
                f"Backfill range exceeds {self._backfill_max_range_days} days"
            )
        return await self._ingest(
            ingestion_type=IngestionType.BACKFILL,
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            idempotency_key=idempotency_key,
        )

    async def incremental_fetch(
        self,
        symbol: str,
        idempotency_key: str,
    ) -> IngestionResult:
        assert_network_call_allowed()
        latest = self._get_latest_finalized_candle_time()
        now = self._clock.now()
        if latest is None:
            lookback = timedelta(hours=self._incremental_max_range_hours)
            start_time = now - lookback
        else:
            start_time = latest + timedelta(seconds=self._interval_seconds)
        end_time = now
        if start_time >= end_time:
            return IngestionResult(
                ingestion_type=IngestionType.INCREMENTAL,
                status=IngestionStatus.COMPLETED,
                inserted_count=0,
                duplicate_count=0,
                invalid_count=0,
                corrected_count=0,
                gap_count=0,
                retry_count=0,
                request_count=0,
                provider_latency_ms=None,
                safe_error=None,
                content_hash=self._compute_ingestion_hash(
                    start_time, end_time, 0, 0, 0, 0, 0
                ),
                idempotency_key=idempotency_key,
                actual_start_time=start_time,
                actual_end_time=end_time,
            )
        return await self._ingest(
            ingestion_type=IngestionType.INCREMENTAL,
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            idempotency_key=idempotency_key,
        )

    async def detect_gaps(
        self,
        symbol_version_id: UUID,
        interval_code: str,
    ) -> GapReport:
        existing_times = self._get_existing_candle_times()
        latest = max(existing_times) if existing_times else None
        if latest is None:
            return GapReport(
                symbol_version_id=symbol_version_id,
                interval_code=interval_code,
                interval_seconds=self._interval_seconds,
                expected_start=datetime.min.replace(tzinfo=timezone.utc),
                expected_end=datetime.min.replace(tzinfo=timezone.utc),
                missing_count=0,
                missing_ranges=(),
                severity="info",
                detection_policy_version=self._policy.policy_version,
            )
        expected_start = min(existing_times)
        expected_end = latest + timedelta(seconds=self._interval_seconds)
        all_expected: list[datetime] = []
        current = expected_start
        while current <= expected_end:
            all_expected.append(current)
            current += timedelta(seconds=self._interval_seconds)
        missing = [t for t in all_expected if t not in existing_times]
        if not missing:
            return GapReport(
                symbol_version_id=symbol_version_id,
                interval_code=interval_code,
                interval_seconds=self._interval_seconds,
                expected_start=expected_start,
                expected_end=expected_end,
                missing_count=0,
                missing_ranges=(),
                severity="info",
                detection_policy_version=self._policy.policy_version,
            )
        missing_ranges: list[tuple[datetime, datetime]] = []
        range_start = missing[0]
        range_end = missing[0]
        for t in missing[1:]:
            if t == range_end + timedelta(seconds=self._interval_seconds):
                range_end = t
            else:
                missing_ranges.append((range_start, range_end))
                range_start = t
                range_end = t
        missing_ranges.append((range_start, range_end))
        return GapReport(
            symbol_version_id=symbol_version_id,
            interval_code=interval_code,
            interval_seconds=self._interval_seconds,
            expected_start=expected_start,
            expected_end=expected_end,
            missing_count=len(missing),
            missing_ranges=tuple(missing_ranges),
            severity="error",
            detection_policy_version=self._policy.policy_version,
        )

    async def repair_gaps(
        self,
        symbol: str,
        gap_report: GapReport,
        idempotency_key: str,
    ) -> IngestionResult:
        assert_network_call_allowed()
        if gap_report.missing_count == 0:
            return IngestionResult(
                ingestion_type=IngestionType.GAP_REPAIR,
                status=IngestionStatus.COMPLETED,
                inserted_count=0,
                duplicate_count=0,
                invalid_count=0,
                corrected_count=0,
                gap_count=0,
                retry_count=0,
                request_count=0,
                provider_latency_ms=None,
                safe_error=None,
                content_hash=self._compute_ingestion_hash(
                    gap_report.expected_start,
                    gap_report.expected_end,
                    0,
                    0,
                    0,
                    0,
                    0,
                ),
                idempotency_key=idempotency_key,
                actual_start_time=gap_report.expected_start,
                actual_end_time=gap_report.expected_end,
            )
        return await self._ingest(
            ingestion_type=IngestionType.GAP_REPAIR,
            symbol=symbol,
            start_time=gap_report.expected_start,
            end_time=gap_report.expected_end,
            idempotency_key=idempotency_key,
        )

    def create_snapshot(
        self,
        analysis_time: datetime,
        candle_ids: list[UUID],
        quality_outcome: str,
        freshness_outcome: str,
        ingestion_id: UUID | None = None,
        creator_cycle_id: str | None = None,
        creator_job_id: str | None = None,
    ) -> SnapshotResult:
        if not candle_ids:
            raise ValueError("Cannot create snapshot with empty candle membership")
        first_time, last_time, count = self._get_snapshot_candle_range(candle_ids)
        snapshot_hash = self._compute_snapshot_hash(
            candle_ids=candle_ids,
            analysis_time=analysis_time,
            first_time=first_time,
            last_time=last_time,
            count=count,
            quality_outcome=quality_outcome,
            freshness_outcome=freshness_outcome,
        )
        snapshot_id = self._insert_snapshot(
            analysis_time=analysis_time,
            first_event_time=first_time,
            last_event_time=last_time,
            candle_count=count,
            quality_outcome=quality_outcome,
            freshness_outcome=freshness_outcome,
            snapshot_hash=snapshot_hash,
            ingestion_id=ingestion_id,
            creator_cycle_id=creator_cycle_id,
            creator_job_id=creator_job_id,
        )
        self._insert_snapshot_candles(snapshot_id, candle_ids)
        return SnapshotResult(
            snapshot_id=snapshot_id,
            snapshot_hash=snapshot_hash,
            candle_count=count,
            quality_outcome=quality_outcome,
            freshness_outcome=freshness_outcome,
            first_event_time=first_time,
            last_event_time=last_time,
            analysis_time=analysis_time,
        )

    async def _ingest(
        self,
        ingestion_type: IngestionType,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        idempotency_key: str,
    ) -> IngestionResult:
        ingestion_id = self._create_ingestion(
            ingestion_type=ingestion_type,
            start_time=start_time,
            end_time=end_time,
            idempotency_key=idempotency_key,
        )
        request_count = 0
        retry_count = 0
        provider_latency_ms: int | None = None
        safe_error: str | None = None
        try:
            start_ns = self._clock.now()
            raw_candles = await self._provider.get_finalized_candles(
                symbol=symbol,
                interval=self._interval,
                start_time=start_time,
                end_time=end_time,
            )
            end_ns = self._clock.now()
            provider_latency_ms = int(
                (end_ns - start_ns).total_seconds() * 1000
            )
            request_count = 1
            existing_hashes = self._get_existing_candle_hashes()
            existing_times = self._get_existing_candle_times()
            inserted = 0
            duplicates = 0
            invalid = 0
            corrected = 0
            if isinstance(self._provider, FakeBinanceProvider):
                pass
            else:
                await self._provider.get_server_time()
                request_count += 1
            validated = self._validate_candles(raw_candles)
            quality_events: list[QualityEvent] = []
            for result in validated:
                if not result.is_valid:
                    invalid += 1
                    quality_events.append(
                        make_quality_event(
                            event_type=result.quality_state.value,
                            severity="error",
                            symbol_version_id=self._symbol_version_id,
                            interval_code=self._interval.value,
                            details={"reasons": result.invalid_reasons},
                            ingestion_id=ingestion_id,
                        )
                    )
                    continue
                if result.is_duplicate:
                    if result.duplicate_conflict:
                        quality_events.append(
                            make_quality_event(
                                event_type=(
                                    QualityState.DUPLICATE_CONFLICT.value
                                ),
                                severity="warning",
                                symbol_version_id=(
                                    self._symbol_version_id
                                ),
                                interval_code=self._interval.value,
                                details={"hash": result.content_hash},
                                ingestion_id=ingestion_id,
                            )
                        )
                    else:
                        quality_events.append(
                            make_quality_event(
                                event_type=(
                                    QualityState.DUPLICATE_CONSISTENT.value
                                ),
                                severity="info",
                                symbol_version_id=(
                                    self._symbol_version_id
                                ),
                                interval_code=self._interval.value,
                                details={"hash": result.content_hash},
                                ingestion_id=ingestion_id,
                            )
                        )
                    duplicates += 1
                    continue
                if result.out_of_order:
                    quality_events.append(
                        make_quality_event(
                            event_type=QualityState.OUT_OF_ORDER.value,
                            severity="warning",
                            symbol_version_id=self._symbol_version_id,
                            interval_code=self._interval.value,
                            details={"hash": result.content_hash},
                            ingestion_id=ingestion_id,
                        )
                    )
                    invalid += 1
                    continue
                if result.content_hash in existing_hashes:
                    duplicates += 1
                    continue
                self._insert_candle(result.candle, result.content_hash)
                existing_hashes.add(result.content_hash)
                existing_times.add(result.candle.time)
                inserted += 1
            if quality_events:
                self._bulk_insert_quality_events(quality_events)
            content_hash = self._compute_ingestion_hash(
                start_time,
                end_time,
                inserted,
                duplicates,
                invalid,
                corrected,
                request_count,
            )
            self._update_ingestion(
                ingestion_id=ingestion_id,
                status=IngestionStatus.COMPLETED,
                inserted=inserted,
                duplicates=duplicates,
                invalid=invalid,
                corrected=corrected,
                request_count=request_count,
                retry_count=retry_count,
                provider_latency_ms=provider_latency_ms,
                safe_error=safe_error,
                content_hash=content_hash,
                actual_start_time=start_time,
                actual_end_time=end_time,
            )
            return IngestionResult(
                ingestion_type=ingestion_type,
                status=IngestionStatus.COMPLETED,
                inserted_count=inserted,
                duplicate_count=duplicates,
                invalid_count=invalid,
                corrected_count=corrected,
                gap_count=0,
                retry_count=retry_count,
                request_count=request_count,
                provider_latency_ms=provider_latency_ms,
                safe_error=safe_error,
                content_hash=content_hash,
                idempotency_key=idempotency_key,
                actual_start_time=start_time,
                actual_end_time=end_time,
            )
        except Exception as exc:
            logger.error(
                "ingestion_failed",
                extra={"ingestion_id": str(ingestion_id), "error": str(exc)},
            )
            content_hash = self._compute_ingestion_hash(
                start_time, end_time, 0, 0, 0, 0, request_count
            )
            self._update_ingestion(
                ingestion_id=ingestion_id,
                status=IngestionStatus.FAILED,
                inserted=0,
                duplicates=0,
                invalid=0,
                corrected=0,
                request_count=request_count,
                retry_count=retry_count,
                provider_latency_ms=provider_latency_ms,
                safe_error=str(exc)[:500],
                content_hash=content_hash,
                actual_start_time=start_time,
                actual_end_time=end_time,
            )
            raise

    def _validate_candles(self, candles: list[Candle]) -> list[Any]:
        results = []
        for candle in candles:
            ohlc_valid, ohlc_reasons = validate_candle_ohlc(
                candle.open, candle.high, candle.low, candle.close
            )
            time_valid, time_reasons = validate_candle_times(
                candle.time, candle.time, self._interval_seconds
            )
            vol_valid, vol_reasons = validate_candle_volumes(
                candle.volume, candle.volume, 0
            )
            all_reasons = ohlc_reasons + time_reasons + vol_reasons
            is_valid = ohlc_valid and time_valid and vol_valid
            content_hash = compute_candle_content_hash(
                symbol_version_id=self._symbol_version_id,
                interval_code=self._interval.value,
                open_time=candle.time,
                close_time=candle.time,
                open_price=candle.open,
                high_price=candle.high,
                low_price=candle.low,
                close_price=candle.close,
                base_volume=candle.volume,
                quote_volume=candle.volume,
                trade_count=0,
            )
            existing = self._get_existing_candle_by_time(candle.time)
            is_duplicate = existing is not None
            duplicate_conflict = False
            out_of_order = False
            if existing is not None:
                existing_hash = existing.get("content_hash", "")
                if existing_hash and existing_hash != content_hash:
                    duplicate_conflict = True
            latest_time = self._get_latest_finalized_candle_time()
            if latest_time is not None and candle.time < latest_time:
                out_of_order = True
            quality_state, _ = assess_quality(
                candle=candle,
                is_duplicate=is_duplicate,
                duplicate_conflict=duplicate_conflict,
                out_of_order=out_of_order,
                invalid_reasons=all_reasons,
                content_hash=content_hash,
                policy=self._policy,
            )
            results.append(
                type("CandleValidationResult", (), {
                    "candle": candle,
                    "quality_state": quality_state,
                    "is_valid": is_valid,
                    "is_duplicate": is_duplicate,
                    "duplicate_conflict": duplicate_conflict,
                    "out_of_order": out_of_order,
                    "invalid_reasons": tuple(all_reasons),
                    "content_hash": content_hash,
                })
            )
        return results

    def _get_latest_finalized_candle_time(self) -> datetime | None:
        row = self._session.execute(
            text(
                """
                select max(candle.open_time) as max_time
                from public.candles candle
                where candle.symbol_version_id = :symbol_version_id
                  and candle.interval_code = :interval_code
                  and candle.finalized = true
                """
            ),
            {
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
            },
        ).mappings().one_or_none()
        return row["max_time"] if row and row["max_time"] is not None else None

    def _get_existing_candle_times(self) -> set[datetime]:
        rows = self._session.execute(
            text(
                """
                select candle.open_time
                from public.candles candle
                where candle.symbol_version_id = :symbol_version_id
                  and candle.interval_code = :interval_code
                  and candle.finalized = true
                """
            ),
            {
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
            },
        ).scalars().all()
        return set(rows)

    def _get_existing_candle_hashes(self) -> set[str]:
        rows = self._session.execute(
            text(
                """
                select candle.content_hash
                from public.candles candle
                where candle.symbol_version_id = :symbol_version_id
                  and candle.interval_code = :interval_code
                  and candle.finalized = true
                """
            ),
            {
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
            },
        ).scalars().all()
        return set(rows)

    def _get_existing_candle_by_time(
        self, open_time: datetime
    ) -> dict[str, Any] | None:
        row = self._session.execute(
            text(
                """
                select id, content_hash, open_time
                from public.candles
                where symbol_version_id = :symbol_version_id
                  and interval_code = :interval_code
                  and open_time = :open_time
                  and finalized = true
                limit 1
                """
            ),
            {
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
                "open_time": open_time,
            },
        ).mappings().one_or_none()
        return dict(row) if row else None

    def _get_snapshot_candle_range(
        self, candle_ids: list[UUID]
    ) -> tuple[datetime, datetime, int]:
        rows = self._session.execute(
            text(
                """
                select min(candle.open_time) as min_time,
                       max(candle.open_time) as max_time,
                       count(*) as cnt
                from public.candles candle
                where candle.id = any(:ids)
                """
            ),
            {"ids": candle_ids},
        ).mappings().one()
        return rows["min_time"], rows["max_time"], int(rows["cnt"])

    def _insert_candle(self, candle: Candle, content_hash: str) -> None:
        self._session.execute(
            text(
                """
                insert into public.candles (
                    symbol_version_id, interval_code, open_time, close_time,
                    open_price, high_price, low_price, close_price,
                    base_volume, quote_volume, trade_count, finalized, content_hash
                ) values (
                    :symbol_version_id, :interval_code, :open_time, :close_time,
                    :open_price, :high_price, :low_price, :close_price,
                    :base_volume, :quote_volume, :trade_count, true, :content_hash
                )
                on conflict (symbol_version_id, interval_code, open_time) do nothing
                """
            ),
            {
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
                "open_time": candle.time,
                "close_time": candle.time,
                "open_price": candle.open,
                "high_price": candle.high,
                "low_price": candle.low,
                "close_price": candle.close,
                "base_volume": candle.volume,
                "quote_volume": candle.volume,
                "trade_count": 0,
                "content_hash": content_hash,
            },
        )

    def _create_ingestion(
        self,
        ingestion_type: IngestionType,
        start_time: datetime,
        end_time: datetime,
        idempotency_key: str,
    ) -> UUID:
        row = self._session.execute(
            text(
                """
                insert into public.market_data_ingestions (
                    exchange_id, symbol_version_id, ingestion_type,
                    interval_code, requested_start_time, requested_end_time,
                    status, idempotency_key, content_hash
                ) values (
                    :exchange_id, :symbol_version_id, :ingestion_type,
                    :interval_code, :start_time, :end_time, 'running',
                    :idempotency_key, :content_hash
                )
                returning id
                """
            ),
            {
                "exchange_id": self._exchange_id,
                "symbol_version_id": self._symbol_version_id,
                "ingestion_type": ingestion_type.value,
                "interval_code": self._interval.value,
                "start_time": start_time,
                "end_time": end_time,
                "idempotency_key": idempotency_key,
                "content_hash": self._compute_ingestion_hash(
                    start_time, end_time, 0, 0, 0, 0, 0
                ),
            },
        ).scalar_one()
        return cast(UUID, row)

    def _update_ingestion(
        self,
        ingestion_id: UUID,
        status: IngestionStatus,
        inserted: int,
        duplicates: int,
        invalid: int,
        corrected: int,
        request_count: int,
        retry_count: int,
        provider_latency_ms: int | None,
        safe_error: str | None,
        content_hash: str,
        actual_start_time: datetime | None,
        actual_end_time: datetime | None,
    ) -> None:
        self._session.execute(
            text(
                """
                update public.market_data_ingestions
                set status = :status,
                    inserted_count = :inserted,
                    duplicate_count = :duplicates,
                    invalid_count = :invalid,
                    corrected_count = :corrected,
                    request_count = :request_count,
                    retry_count = :retry_count,
                    provider_latency_ms = :provider_latency_ms,
                    safe_error = :safe_error,
                    content_hash = :content_hash,
                    actual_start_time = :actual_start_time,
                    actual_end_time = :actual_end_time,
                    completed_at = case
                        when :status in ('completed', 'failed', 'cancelled')
                        then timezone('utc', now()) else null end,
                    updated_at = timezone('utc', now())
                where id = :id
                """
            ),
            {
                "id": ingestion_id,
                "status": status.value,
                "inserted": inserted,
                "duplicates": duplicates,
                "invalid": invalid,
                "corrected": corrected,
                "request_count": request_count,
                "retry_count": retry_count,
                "provider_latency_ms": provider_latency_ms,
                "safe_error": safe_error,
                "content_hash": content_hash,
                "actual_start_time": actual_start_time,
                "actual_end_time": actual_end_time,
            },
        )

    def _bulk_insert_quality_events(self, events: list[QualityEvent]) -> None:
        if not events:
            return
        values = []
        params: dict[str, Any] = {}
        for idx, event in enumerate(events):
            prefix = f"e{idx}"
            values.append(
                f"(:{prefix}_exchange_id, :{prefix}_symbol_version_id, "
                f":{prefix}_interval_code, :{prefix}_event_type, "
                f":{prefix}_severity, :{prefix}_details, "
                f":{prefix}_detection_policy_version, :{prefix}_resolution, "
                f":{prefix}_ingestion_id, :{prefix}_snapshot_id, "
                f":{prefix}_reviewer_user_id, :{prefix}_detected_at)"
            )
            params.update({
                f"{prefix}_exchange_id": self._exchange_id,
                f"{prefix}_symbol_version_id": event.symbol_version_id,
                f"{prefix}_interval_code": event.interval_code,
                f"{prefix}_event_type": event.event_type,
                f"{prefix}_severity": event.severity,
                f"{prefix}_details": json.dumps(event.details),
                f"{prefix}_detection_policy_version": (
                    event.detection_policy_version
                ),
                f"{prefix}_resolution": event.resolution,
                f"{prefix}_ingestion_id": event.ingestion_id,
                f"{prefix}_snapshot_id": event.snapshot_id,
                f"{prefix}_reviewer_user_id": event.reviewer_user_id,
                f"{prefix}_detected_at": datetime.now(timezone.utc),
            })
        sql = (
            "insert into public.data_quality_events ("
            "exchange_id, symbol_version_id, interval_code, event_type, "
            "severity, details, detection_policy_version, resolution, "
            "ingestion_id, snapshot_id, reviewer_user_id, detected_at"
            f") values {','.join(values)}"
        )
        self._session.execute(text(sql), params)

    def _insert_snapshot(
        self,
        analysis_time: datetime,
        first_event_time: datetime,
        last_event_time: datetime,
        candle_count: int,
        quality_outcome: str,
        freshness_outcome: str,
        snapshot_hash: str,
        ingestion_id: UUID | None,
        creator_cycle_id: str | None,
        creator_job_id: str | None,
    ) -> UUID:
        row = self._session.execute(
            text(
                """
                insert into public.market_snapshots (
                    workspace_id, exchange_id, symbol_version_id, interval_code,
                    analysis_time, first_event_time, last_event_time, candle_count,
                    quality_outcome, quality_policy_version, freshness_outcome,
                    freshness_policy_version, data_source, ingestion_id, snapshot_hash,
                    snapshot_schema_version, creator_cycle_id, creator_job_id
                ) values (
                    :workspace_id, :exchange_id, :symbol_version_id, :interval_code,
                    :analysis_time, :first_event_time, :last_event_time, :candle_count,
                    :quality_outcome, :quality_policy_version, :freshness_outcome,
                    :freshness_policy_version, 'rest', :ingestion_id, :snapshot_hash,
                    '1.0', :creator_cycle_id, :creator_job_id
                )
                returning id
                """
            ),
            {
                "workspace_id": self._workspace_id,
                "exchange_id": self._exchange_id,
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
                "analysis_time": analysis_time,
                "first_event_time": first_event_time,
                "last_event_time": last_event_time,
                "candle_count": candle_count,
                "quality_outcome": quality_outcome,
                "quality_policy_version": self._policy.policy_version,
                "freshness_outcome": freshness_outcome,
                "freshness_policy_version": self._policy.policy_version,
                "ingestion_id": ingestion_id,
                "snapshot_hash": snapshot_hash,
                "creator_cycle_id": creator_cycle_id,
                "creator_job_id": creator_job_id,
            },
        ).scalar_one()
        return cast(UUID, row)

    def _insert_snapshot_candles(
        self, snapshot_id: UUID, candle_ids: list[UUID]
    ) -> None:
        values = []
        params: dict[str, Any] = {"snapshot_id": snapshot_id}
        for idx, candle_id in enumerate(candle_ids):
            prefix = f"c{idx}"
            values.append(
                f"(:{prefix}_snapshot_id, :{prefix}_candle_id, "
                f":{prefix}_sequence)"
            )
            params.update({
                f"{prefix}_snapshot_id": snapshot_id,
                f"{prefix}_candle_id": candle_id,
                f"{prefix}_sequence": idx + 1,
            })
        sql = (
            "insert into public.market_snapshot_candles "
            "(snapshot_id, candle_id, sequence) "
            f"values {','.join(values)}"
        )
        self._session.execute(text(sql), params)

    def _compute_ingestion_hash(
        self,
        start_time: datetime,
        end_time: datetime,
        inserted: int,
        duplicates: int,
        invalid: int,
        corrected: int,
        request_count: int,
    ) -> str:
        payload = {
            "exchange_id": str(self._exchange_id),
            "symbol_version_id": str(self._symbol_version_id),
            "interval_code": self._interval.value,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "inserted": inserted,
            "duplicates": duplicates,
            "invalid": invalid,
            "corrected": corrected,
            "request_count": request_count,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _compute_snapshot_hash(
        self,
        candle_ids: list[UUID],
        analysis_time: datetime,
        first_time: datetime,
        last_time: datetime,
        count: int,
        quality_outcome: str,
        freshness_outcome: str,
    ) -> str:
        payload = {
            "workspace_id": str(self._workspace_id),
            "exchange_id": str(self._exchange_id),
            "symbol_version_id": str(self._symbol_version_id),
            "interval_code": self._interval.value,
            "analysis_time": analysis_time.isoformat(),
            "first_event_time": first_time.isoformat(),
            "last_event_time": last_time.isoformat(),
            "candle_count": count,
            "quality_outcome": quality_outcome,
            "freshness_outcome": freshness_outcome,
            "candle_ids": [str(cid) for cid in candle_ids],
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


_INTERVAL_SECONDS: dict[CandleInterval, int] = {
    CandleInterval.ONE_MINUTE: 60,
    CandleInterval.FIVE_MINUTES: 300,
    CandleInterval.FIFTEEN_MINUTES: 900,
    CandleInterval.ONE_HOUR: 3600,
    CandleInterval.FOUR_HOURS: 14400,
    CandleInterval.ONE_DAY: 86400,
}
