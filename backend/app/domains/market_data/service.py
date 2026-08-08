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
from app.infrastructure.exchange.binance.protocol import (
    BinanceProviderUnavailableError,
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
_DEFAULT_INCREMENTAL_OVERLAP_HOURS = 1
_DEFAULT_INTERVAL = CandleInterval.ONE_HOUR
_MAX_PAGE_CANDLES = 1000


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
        incremental_overlap_hours: int = _DEFAULT_INCREMENTAL_OVERLAP_HOURS,
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
        self._incremental_overlap_hours = incremental_overlap_hours
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

    def _validate_symbol_binding(self, symbol: str) -> None:
        """Reject a requested symbol that is not the configured symbol version.

        The service hashes/persists every returned candle under
        self._symbol_version_id, so the provider must fetch exactly that
        native symbol or the canonical market identity would be corrupted.
        """
        native_symbol = self._session.execute(
            text(
                """
                    select native_symbol
                    from public.exchange_symbol_versions
                    where id = :symbol_version_id
                    """
            ),
            {"symbol_version_id": self._symbol_version_id},
        ).scalar_one_or_none()
        if native_symbol is None:
            raise ValueError(
                f"symbol_version_id {self._symbol_version_id} does not exist"
            )
        if native_symbol.upper() != symbol.upper():
            raise ValueError(
                f"symbol {symbol!r} does not match configured native symbol "
                f"{native_symbol!r} for symbol_version_id "
                f"{self._symbol_version_id}"
            )

    async def backfill(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        idempotency_key: str,
    ) -> IngestionResult:
        assert_network_call_allowed()
        self._validate_symbol_binding(symbol)
        max_duration = timedelta(days=self._backfill_max_range_days)
        if end_time - start_time > max_duration:
            raise ValueError(
                f"Backfill range exceeds {self._backfill_max_range_days} days"
            )
        return await self._ingest_pages(
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
        self._validate_symbol_binding(symbol)
        # Provider I/O (server time) happens outside any DB transaction.
        st = await self._provider.get_server_time()
        start_time, end_time = self._compute_incremental_range(st.server_time)
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
                content_hash=self._compute_ingestion_hash(start_time, end_time),
                idempotency_key=idempotency_key,
                actual_start_time=start_time,
                actual_end_time=end_time,
            )
        return await self._ingest_pages(
            ingestion_type=IngestionType.INCREMENTAL,
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            idempotency_key=idempotency_key,
            provider_server_time=st,
        )

    def _align_to_interval(self, dt: datetime) -> datetime:
        """Floor a timestamp to the start of its configured interval."""
        epoch = int(dt.timestamp())
        aligned_epoch = epoch - (epoch % self._interval_seconds)
        return datetime.fromtimestamp(aligned_epoch, tz=timezone.utc)

    def _compute_incremental_range(
        self, server_time: datetime
    ) -> tuple[datetime, datetime]:
        """Compute an incremental range aligned to finalized interval
        boundaries using trusted exchange time.

        end_time is the last finalized exclusive boundary (the start of the
        current, not-yet-finalized interval), and the start is floored to an
        interval boundary, so a 1h fetch at 22:28 covers [..., 22:00) and never
        expects a non-finalized candle.
        """
        latest = self._get_latest_finalized_candle_time()
        end_time = self._align_to_interval(server_time)
        if latest is None:
            lookback = timedelta(hours=self._incremental_max_range_hours)
            start_time = self._align_to_interval(server_time - lookback)
        else:
            overlap = timedelta(hours=self._incremental_overlap_hours)
            start_time = self._align_to_interval(latest - overlap)
        return start_time, end_time

    def _check_clock_drift(self, server_time: ExchangeTime) -> None:
        if abs(server_time.clock_drift_ms) > self._policy.max_clock_drift_ms:
            raise BinanceProviderUnavailableError(
                f"clock drift {server_time.clock_drift_ms}ms exceeds policy"
            )

    async def detect_gaps(
        self,
        symbol_version_id: UUID,
        interval_code: str,
        expected_end: datetime | None = None,
        expected_start: datetime | None = None,
    ) -> GapReport:
        """Detect gaps over the requested identity/range.

        Requires an explicit authoritative intended range: a gap proof must
        never infer completeness from whatever data happens to exist, so an
        entirely missing requested range and a missing leading candle are
        reported as gaps rather than an empty success.
        """
        if symbol_version_id != self._symbol_version_id:
            raise ValueError(
                "detect_gaps identity mismatch: requested "
                f"{symbol_version_id} does not match service scope "
                f"{self._symbol_version_id}"
            )
        if interval_code != self._interval.value:
            raise ValueError(
                "detect_gaps identity mismatch: requested interval "
                f"{interval_code!r} does not match service scope "
                f"{self._interval.value!r}"
            )
        if expected_start is None or expected_end is None:
            raise ValueError(
                "detect_gaps requires explicit expected_start and expected_end "
                "boundaries; completeness must never be inferred from existing data"
            )
        existing_times = self._get_existing_candle_times()
        all_expected: list[datetime] = []
        current = expected_start
        while current <= expected_end:
            all_expected.append(current)
            current += timedelta(seconds=self._interval_seconds)
        if not all_expected:
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
        return self._build_missing_report(
            symbol_version_id=symbol_version_id,
            interval_code=interval_code,
            expected_start=expected_start,
            expected_end=expected_end,
            missing=missing,
        )

    def _build_missing_report(
        self,
        symbol_version_id: UUID,
        interval_code: str,
        expected_start: datetime,
        expected_end: datetime,
        missing: list[datetime],
    ) -> GapReport:
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
        self._validate_symbol_binding(symbol)
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
                    gap_report.expected_start, gap_report.expected_end
                ),
                idempotency_key=idempotency_key,
                actual_start_time=gap_report.expected_start,
                actual_end_time=gap_report.expected_end,
            )
        total_inserted = 0
        total_duplicates = 0
        total_invalid = 0
        total_corrected = 0
        total_request_count = 0
        total_retry_count = 0
        provider_latency_ms: int | None = None
        for range_start, range_end in gap_report.missing_ranges:
            result = await self._ingest_pages(
                ingestion_type=IngestionType.GAP_REPAIR,
                symbol=symbol,
                start_time=range_start,
                end_time=range_end + timedelta(seconds=self._interval_seconds),
                idempotency_key=f"{idempotency_key}-{range_start.isoformat()}",
            )
            total_inserted += result.inserted_count
            total_duplicates += result.duplicate_count
            total_invalid += result.invalid_count
            total_corrected += result.corrected_count
            total_request_count += result.request_count
            total_retry_count += result.retry_count
            provider_latency_ms = provider_latency_ms or result.provider_latency_ms
        verification = await self.detect_gaps(
            symbol_version_id=self._symbol_version_id,
            interval_code=self._interval.value,
            expected_start=gap_report.expected_start,
            expected_end=gap_report.expected_end,
        )
        # Append terminal gap_repaired evidence for the repaired range so
        # snapshots are not permanently blocked by a gap that has since been
        # filled (append-only resolution).
        if verification.missing_count == 0:
            self._resolve_quality_events(
                event_types=(QualityState.GAP_DETECTED.value,),
                resolution="gap_repaired",
                range_start=gap_report.expected_start,
                range_end=gap_report.expected_end,
                ingestion_id=None,
            )
            self._session.commit()
        return IngestionResult(
            ingestion_type=IngestionType.GAP_REPAIR,
            status=IngestionStatus.COMPLETED
            if verification.missing_count == 0
            else IngestionStatus.FAILED,
            inserted_count=total_inserted,
            duplicate_count=total_duplicates,
            invalid_count=total_invalid,
            corrected_count=total_corrected,
            gap_count=verification.missing_count,
            retry_count=total_retry_count,
            request_count=total_request_count,
            provider_latency_ms=provider_latency_ms,
            safe_error=None if verification.missing_count == 0 else "incomplete_repair",
            content_hash=self._compute_ingestion_hash(
                gap_report.expected_start, gap_report.expected_end
            ),
            idempotency_key=idempotency_key,
            actual_start_time=gap_report.expected_start,
            actual_end_time=gap_report.expected_end,
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
        # Canonicalize membership chronologically so identical input always
        # resolves to the same identity and hash.
        canonical_ids = self._canonicalize_candle_ids(candle_ids)
        first_time, last_time, count = self._get_snapshot_candle_range(canonical_ids)
        if count != len(canonical_ids) or first_time is None or last_time is None:
            raise ValueError(
                "Snapshot membership must match exactly the provided candle IDs "
                "for this symbol and interval"
            )
        # Derive quality/freshness from persisted evidence rather than trusting
        # caller-supplied labels. Downstream reads are gated on the derived
        # values, so a caller cannot certify incomplete/stale data as approved.
        derived_quality = self._derive_quality_outcome(
            canonical_ids, first_time, last_time
        )
        derived_freshness = self._derive_freshness_outcome(
            analysis_time, canonical_ids, last_time
        )
        if derived_quality != "approved" or derived_freshness != "fresh":
            raise ValueError(
                f"Snapshot gate failed: quality={derived_quality}, "
                f"freshness={derived_freshness}"
            )
        snapshot_hash = self._compute_snapshot_hash(
            candle_ids=canonical_ids,
            analysis_time=analysis_time,
            first_time=first_time,
            last_time=last_time,
            count=count,
            quality_outcome=derived_quality,
            freshness_outcome=derived_freshness,
        )
        # Atomic idempotent creation: ON CONFLICT (snapshot_hash) resolves a
        # concurrent identical request to the same persisted identity instead
        # of racing a check-then-insert. Membership rows are (snapshot_id,
        # candle_id) unique, so re-inserting for an existing snapshot is a
        # no-op conflict.
        snapshot_id = self._insert_snapshot(
            analysis_time=analysis_time,
            first_event_time=first_time,
            last_event_time=last_time,
            candle_count=count,
            quality_outcome=derived_quality,
            freshness_outcome=derived_freshness,
            snapshot_hash=snapshot_hash,
            ingestion_id=ingestion_id,
            creator_cycle_id=creator_cycle_id,
            creator_job_id=creator_job_id,
        )
        self._insert_snapshot_candles(snapshot_id, canonical_ids)
        return SnapshotResult(
            snapshot_id=snapshot_id,
            snapshot_hash=snapshot_hash,
            candle_count=count,
            quality_outcome=derived_quality,
            freshness_outcome=derived_freshness,
            first_event_time=first_time,
            last_event_time=last_time,
            analysis_time=analysis_time,
        )

    def _canonicalize_candle_ids(self, candle_ids: list[UUID]) -> list[UUID]:
        """Return the membership in chronological open-time order.

        Exact membership is proven later by _get_snapshot_candle_range, which
        requires count == len(candle_ids); this only orders the provided set so
        hashing and persistence are canonical and idempotent.
        """
        rows = (
            self._session.execute(
                text(
                    """
                    select candle.id as id, candle.open_time as open_time
                    from public.candles candle
                    where candle.id = any(:ids)
                      and candle.symbol_version_id = :symbol_version_id
                      and candle.interval_code = :interval_code
                      and candle.finalized = true
                      and candle.superseded_by is null
                    """
                ),
                {
                    "ids": candle_ids,
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                },
            )
            .mappings()
            .all()
        )
        by_id = {row["id"]: row["open_time"] for row in rows}
        # Canonicalization may only reorder, never shrink or replace: the
        # caller's exact multiset of IDs must be present and valid for this
        # symbol/interval, otherwise the request is rejected rather than
        # silently downgraded to a subset.
        found = [cid for cid in candle_ids if cid in by_id]
        if len(found) != len(candle_ids) or len(set(found)) != len(candle_ids):
            raise ValueError(
                "Snapshot membership must be an exact set of valid finalized "
                "candles for this symbol and interval; received "
                f"{len(candle_ids)} ids, resolved {len(found)}"
            )
        ordered = [cid for cid in candle_ids if cid in by_id]
        ordered.sort(key=lambda cid: by_id[cid])
        return ordered

    def _derive_quality_outcome(
        self,
        candle_ids: list[UUID],
        first_time: datetime,
        last_time: datetime,
    ) -> str:
        """Return 'approved' only when the exact membership is contiguous and
        free of blocking evidence.

        Proves interval-by-interval coverage of the candidate membership and
        rejects when unresolved gap/correction/invalidation evidence or
        error/critical events overlap the range.
        """
        membership_times = (
            self._session.execute(
                text(
                    """
                    select candle.open_time
                    from public.candles candle
                    where candle.id = any(:ids)
                      and candle.symbol_version_id = :symbol_version_id
                      and candle.interval_code = :interval_code
                      and candle.finalized = true
                      and candle.superseded_by is null
                    order by candle.open_time
                    """
                ),
                {
                    "ids": candle_ids,
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                },
            )
            .scalars()
            .all()
        )
        if len(membership_times) != len(candle_ids):
            return "incomplete"
        expected_count = (
            int((last_time - first_time).total_seconds() // self._interval_seconds) + 1
        )
        if len(membership_times) != expected_count:
            return "incomplete"
        if len(membership_times) > 1:
            for earlier, later in zip(
                membership_times, membership_times[1:], strict=True
            ):
                if (later - earlier).total_seconds() != self._interval_seconds:
                    return "incomplete"
        blocking = self._session.execute(
            text(
                """
                select count(*) as cnt
                from public.data_quality_events blocker
                where blocker.symbol_version_id = :symbol_version_id
                  and blocker.interval_code = :interval_code
                  and (
                      blocker.event_type in (
                          'gap_detected', 'gap_unresolved',
                          'correction_pending', 'invalidated', 'quarantined',
                          'provider_unavailable', 'rate_limited',
                          'clock_drift_exceeded'
                      )
                      or blocker.severity in ('error', 'critical')
                  )
                  and (
                      (blocker.affected_range_start is null
                       and blocker.affected_range_end is null)
                      or (
                          blocker.affected_range_start is not null
                          and blocker.affected_range_end is not null
                          and blocker.affected_range_start <= :last_time
                          and blocker.affected_range_end >= :first_time
                      )
                  )
                  and not exists (
                      select 1
                      from public.data_quality_events terminal
                      where terminal.symbol_version_id = blocker.symbol_version_id
                        and terminal.interval_code = blocker.interval_code
                        and terminal.event_type in (
                            'gap_repaired', 'correction_applied',
                            'clock_drift_recovered'
                        )
                        and terminal.detected_at >= blocker.detected_at
                        and (
                            (blocker.affected_range_start is null
                             and blocker.affected_range_end is null
                             and blocker.affected_candle_id is null)
                            or (
                                terminal.affected_range_start
                                    = blocker.affected_range_start
                                and terminal.affected_range_end
                                    = blocker.affected_range_end
                            )
                            or (
                                blocker.affected_candle_id is not null
                                and terminal.affected_candle_id
                                    = blocker.affected_candle_id
                            )
                        )
                  )
                """
            ),
            {
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
                "first_time": first_time,
                "last_time": last_time,
            },
        ).scalar_one()
        if blocking > 0:
            return "incomplete"
        return "approved"

    def _derive_freshness_outcome(
        self,
        analysis_time: datetime,
        candle_ids: list[UUID],
        last_event_time: datetime,
    ) -> str:
        """Return 'fresh' only when the latest finalized close is within policy.

        The M007 freshness contract measures from the latest finalized close /
        expected interval boundary, not the open time, so a 1h candle that
        closed one minute ago is fresh.
        """
        latest_close = self._session.execute(
            text(
                """
                    select max(candle.close_time) as max_close
                    from public.candles candle
                    where candle.id = any(:ids)
                      and candle.symbol_version_id = :symbol_version_id
                      and candle.interval_code = :interval_code
                      and candle.finalized = true
                      and candle.superseded_by is null
                    """
            ),
            {
                "ids": candle_ids,
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
            },
        ).scalar_one()
        boundary = latest_close or (
            last_event_time + timedelta(seconds=self._interval_seconds)
        )
        age_seconds = (analysis_time - boundary).total_seconds()
        if age_seconds > self._policy.stale_threshold_seconds:
            return "stale"
        if age_seconds < 0:
            return "clock_drift_exceeded"
        return "fresh"

    def _acquire_ingestion_lock(
        self,
        ingestion_type: IngestionType,
        start_time: datetime,
        end_time: datetime,
    ) -> str:
        """Claim a session-scoped advisory lock so overlapping duplicate
        deliveries run a single ingestion owner.

        The lock identity is exactly the canonical ingestion identity used by
        the database conflict key (exchange, symbol version, interval,
        requested range, ingestion type) — NOT the caller-supplied delivery
        key — so two workers requesting the same canonical range/type with
        different idempotency keys contend on the same lock.

        Returns the lock key; the caller must release it in a finally block.
        A concurrent worker that cannot acquire the lock fails closed instead
        of racing page persistence.
        """
        lock_key = (
            f"m007:{self._exchange_id}:{self._symbol_version_id}:"
            f"{self._interval.value}:{start_time.isoformat()}:"
            f"{end_time.isoformat()}:{ingestion_type.value}"
        )
        acquired = self._session.execute(
            text("select pg_try_advisory_lock(hashtextextended(:key, 0))"),
            {"key": lock_key},
        ).scalar_one()
        if not acquired:
            raise BinanceProviderUnavailableError(
                "ingestion already owned by a concurrent worker; "
                "overlapping duplicate delivery rejected"
            )
        return lock_key

    def _release_ingestion_lock(self, lock_key: str) -> None:
        # The owning run may have raised, leaving the session transaction
        # aborted. Roll back first so pg_advisory_unlock_all() executes
        # instead of failing in the aborted transaction; otherwise the
        # session-level advisory lock would survive and poison the pooled
        # connection for a later canonical-identical run.
        try:
            self._session.rollback()
            self._session.execute(text("select pg_advisory_unlock_all()"))
            self._session.commit()
        except Exception:
            logger.warning("ingestion_lock_release_failed", extra={"key": lock_key})

    async def _ingest_pages(
        self,
        ingestion_type: IngestionType,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        idempotency_key: str,
        provider_server_time: ExchangeTime | None = None,
    ) -> IngestionResult:
        lock_key = self._acquire_ingestion_lock(ingestion_type, start_time, end_time)
        try:
            return await self._ingest_pages_locked(
                ingestion_type,
                symbol,
                start_time,
                end_time,
                idempotency_key,
                provider_server_time,
            )
        finally:
            self._release_ingestion_lock(lock_key)

    async def _ingest_pages_locked(
        self,
        ingestion_type: IngestionType,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        idempotency_key: str,
        provider_server_time: ExchangeTime | None = None,
    ) -> IngestionResult:
        # Short DB transaction: create/commit the attempt FIRST so even a
        # server-time transport failure leaves a durable, auditable attempt.
        ingestion_id = self._get_or_create_ingestion(
            ingestion_type=ingestion_type,
            start_time=start_time,
            end_time=end_time,
            idempotency_key=idempotency_key,
        )
        self._session.commit()

        # Short DB transaction: load ingestion state and any durable cumulative
        # page evidence, then commit to close the read transaction so no
        # network call happens inside it.
        row = (
            self._session.execute(
                text(
                    "select status, actual_start_time, actual_end_time, checkpoint, "
                    "inserted_count, duplicate_count, invalid_count, corrected_count, "
                    "request_count, retry_count, provider_latency_ms, safe_error, "
                    "content_hash, page_hashes "
                    "from public.market_data_ingestions where id = :id"
                ),
                {"id": ingestion_id},
            )
            .mappings()
            .one_or_none()
        )
        self._session.commit()
        if row and row["status"] == IngestionStatus.COMPLETED.value:
            return IngestionResult(
                ingestion_type=ingestion_type,
                status=IngestionStatus.COMPLETED,
                inserted_count=row["inserted_count"],
                duplicate_count=row["duplicate_count"],
                invalid_count=row["invalid_count"],
                corrected_count=row["corrected_count"],
                gap_count=0,
                retry_count=row["retry_count"],
                request_count=row["request_count"],
                provider_latency_ms=row["provider_latency_ms"],
                safe_error=row["safe_error"],
                content_hash=row["content_hash"],
                idempotency_key=idempotency_key,
                actual_start_time=row["actual_start_time"],
                actual_end_time=row["actual_end_time"],
            )
        checkpoint = row["checkpoint"] if row else None
        current_start = checkpoint if checkpoint is not None else start_time
        inserted_total = row["inserted_count"] if row else 0
        duplicates_total = row["duplicate_count"] if row else 0
        invalid_total = row["invalid_count"] if row else 0
        corrected_total = row["corrected_count"] if row else 0
        request_count = row["request_count"] if row else 0
        retry_count = row["retry_count"] if row else 0
        provider_latency_ms = row["provider_latency_ms"] if row else None
        safe_error = row["safe_error"] if row else None
        stored_page_hashes = row["page_hashes"] if row and row["page_hashes"] else []
        raw_pairs = (
            json.loads(stored_page_hashes)
            if isinstance(stored_page_hashes, str)
            else list(stored_page_hashes)
        )
        # Canonical accepted-content evidence: ordered [open_time, content_hash]
        # pairs so resume reproduces the same content identity independent of
        # how the run was interrupted.
        accepted_by_time: dict[datetime, str] = {}
        for pair in raw_pairs:
            accepted_by_time[datetime.fromisoformat(pair[0])] = pair[1]

        # Provider I/O - no active DB transaction. Server-time failures are
        # persisted as a failed ingestion outcome in a short follow-up tx.
        retry_before = getattr(self._provider, "retry_count", 0)
        try:
            if provider_server_time is not None:
                st = provider_server_time
            else:
                st = await self._provider.get_server_time()
            server_time = st.server_time
            clock_drift_ms = st.clock_drift_ms
        except Exception as exc:
            retry_delta = getattr(self._provider, "retry_count", 0) - retry_before
            retry_count += max(0, retry_delta)
            request_count += 1
            self._update_ingestion(
                ingestion_id=ingestion_id,
                status=IngestionStatus.FAILED,
                inserted=inserted_total,
                duplicates=duplicates_total,
                invalid=invalid_total,
                corrected=corrected_total,
                request_count=request_count,
                retry_count=retry_count,
                provider_latency_ms=provider_latency_ms,
                safe_error=f"server_time_failed: {str(exc)[:300]}",
                content_hash=self._compute_ingestion_hash(
                    start_time, end_time, accepted_by_time
                ),
                actual_start_time=start_time,
                actual_end_time=end_time,
                checkpoint=current_start,
                accepted_by_time=accepted_by_time,
            )
            self._session.commit()
            raise
        retry_delta = getattr(self._provider, "retry_count", 0) - retry_before
        retry_count += max(0, retry_delta)
        request_count += 1

        # Clock-drift evidence: persist a quality event scoped to the attempted
        # range and a failed outcome before returning failure. A later healthy
        # server-time check over the same range appends a clock_drift_recovered
        # terminal event, so an unrelated fresh range is never permanently
        # blocked by a single transient drift failure.
        if abs(clock_drift_ms) > self._policy.max_clock_drift_ms:
            quality_event = make_quality_event(
                event_type=QualityState.CLOCK_DRIFT_EXCEEDED.value,
                severity="error",
                symbol_version_id=self._symbol_version_id,
                interval_code=self._interval.value,
                details={"drift_ms": clock_drift_ms},
                affected_range_start=start_time,
                affected_range_end=end_time,
                ingestion_id=ingestion_id,
            )
            self._bulk_insert_quality_events([quality_event])
            self._update_ingestion(
                ingestion_id=ingestion_id,
                status=IngestionStatus.FAILED,
                inserted=inserted_total,
                duplicates=duplicates_total,
                invalid=invalid_total,
                corrected=corrected_total,
                request_count=request_count,
                retry_count=retry_count,
                provider_latency_ms=provider_latency_ms,
                safe_error="clock_drift_exceeded",
                content_hash=self._compute_ingestion_hash(
                    start_time, end_time, accepted_by_time
                ),
                actual_start_time=start_time,
                actual_end_time=end_time,
                checkpoint=current_start,
                accepted_by_time=accepted_by_time,
            )
            self._session.commit()
            raise BinanceProviderUnavailableError(
                f"clock drift {clock_drift_ms}ms exceeds policy"
            )

        # A healthy server-time check is recovery evidence: append terminal
        # clock_drift_recovered events for any prior drift failures scoped to
        # this attempted range, so future fresh snapshots are not permanently
        # blocked by a transient incident (append-only recovery).
        self._resolve_quality_events(
            event_types=(QualityState.CLOCK_DRIFT_EXCEEDED.value,),
            resolution=QualityState.CLOCK_DRIFT_RECOVERED.value,
            range_start=start_time,
            range_end=end_time,
            ingestion_id=ingestion_id,
        )

        # Short DB transaction: load active existing candles, then commit to
        # close the read transaction before the first provider call.
        existing_hashes = self._get_existing_candle_hashes()
        existing_times = self._get_existing_candle_times()
        self._session.commit()

        page_size = timedelta(seconds=_MAX_PAGE_CANDLES * self._interval_seconds)
        batch_by_time: dict[datetime, str] = {}
        try:
            while current_start < end_time:
                page_end = min(current_start + page_size, end_time)
                page_start_ns = self._clock.now()
                # Provider I/O - no DB transaction is open. Retry/attempt
                # metadata is captured even when the call ultimately raises so
                # the failed provider work is present in ingestion evidence.
                retry_before = getattr(self._provider, "retry_count", 0)
                try:
                    raw_candles = await self._provider.get_finalized_candles(
                        symbol=symbol,
                        interval=self._interval,
                        start_time=current_start,
                        end_time=page_end,
                        server_time=server_time,
                    )
                finally:
                    retry_delta = (
                        getattr(self._provider, "retry_count", 0) - retry_before
                    )
                    retry_count += max(0, retry_delta)
                    request_count += 1
                page_end_ns = self._clock.now()
                page_latency = int((page_end_ns - page_start_ns).total_seconds() * 1000)
                provider_latency_ms = provider_latency_ms or page_latency

                if not raw_candles:
                    gap_event = make_quality_event(
                        event_type=QualityState.GAP_DETECTED.value,
                        severity="warning",
                        symbol_version_id=self._symbol_version_id,
                        interval_code=self._interval.value,
                        details={
                            "range_start": current_start.isoformat(),
                            "range_end": page_end.isoformat(),
                            "reason": "empty_page",
                        },
                        affected_range_start=current_start,
                        affected_range_end=page_end,
                        ingestion_id=ingestion_id,
                    )
                    self._bulk_insert_quality_events([gap_event])
                    self._update_ingestion(
                        ingestion_id=ingestion_id,
                        status=IngestionStatus.FAILED,
                        inserted=inserted_total,
                        duplicates=duplicates_total,
                        invalid=invalid_total,
                        corrected=corrected_total,
                        request_count=request_count,
                        retry_count=retry_count,
                        provider_latency_ms=provider_latency_ms,
                        safe_error="incomplete_range: empty page from provider",
                        content_hash=self._compute_ingestion_hash(
                            start_time, end_time, accepted_by_time
                        ),
                        actual_start_time=start_time,
                        actual_end_time=end_time,
                        checkpoint=current_start,
                        accepted_by_time=accepted_by_time,
                    )
                    self._session.commit()
                    raise BinanceProviderUnavailableError(
                        "incomplete_range: empty page from provider"
                    )

                # Validate every candle. Repeated identities pass through
                # classification (duplicate_consistent / duplicate_conflict)
                # while exactly one accepted candle is required per expected
                # timestamp to advance the durable boundary.
                validated = self._validate_candles(
                    raw_candles,
                    existing_hashes=existing_hashes,
                    existing_times=existing_times,
                    batch_by_time=batch_by_time,
                    clock_drift_ms=clock_drift_ms,
                )
                accepted_times: set[datetime] = set()
                page_inserted = 0
                page_duplicates = 0
                page_invalid = 0
                page_corrected = 0
                quality_events: list[QualityEvent] = []
                for result in validated:
                    if not result.is_valid:
                        page_invalid += 1
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
                    if result.is_correction:
                        page_corrected += 1
                        self._apply_correction(
                            result=result,
                            ingestion_id=ingestion_id,
                            quality_events=quality_events,
                        )
                        existing_hashes.add(result.content_hash)
                        existing_times.add(result.candle.time)
                        batch_by_time[result.candle.time] = result.content_hash
                        accepted_times.add(result.candle.time)
                        continue
                    if result.is_duplicate:
                        if result.duplicate_conflict:
                            quality_events.append(
                                make_quality_event(
                                    event_type=QualityState.DUPLICATE_CONFLICT.value,
                                    severity="warning",
                                    symbol_version_id=self._symbol_version_id,
                                    interval_code=self._interval.value,
                                    details={
                                        "hash": result.content_hash,
                                        "open_time": result.candle.time.isoformat(),
                                    },
                                    ingestion_id=ingestion_id,
                                )
                            )
                        else:
                            quality_events.append(
                                make_quality_event(
                                    event_type=QualityState.DUPLICATE_CONSISTENT.value,
                                    severity="info",
                                    symbol_version_id=self._symbol_version_id,
                                    interval_code=self._interval.value,
                                    details={
                                        "hash": result.content_hash,
                                        "open_time": result.candle.time.isoformat(),
                                    },
                                    ingestion_id=ingestion_id,
                                )
                            )
                            accepted_times.add(result.candle.time)
                        page_duplicates += 1
                        continue
                    if result.duplicate_conflict:
                        quality_events.append(
                            make_quality_event(
                                event_type=QualityState.DUPLICATE_CONFLICT.value,
                                severity="warning",
                                symbol_version_id=self._symbol_version_id,
                                interval_code=self._interval.value,
                                details={
                                    "hash": result.content_hash,
                                    "open_time": result.candle.time.isoformat(),
                                    "reason": "same_page_conflict",
                                },
                                ingestion_id=ingestion_id,
                            )
                        )
                        page_invalid += 1
                        continue
                    if result.out_of_order:
                        quality_events.append(
                            make_quality_event(
                                event_type=QualityState.OUT_OF_ORDER.value,
                                severity="warning",
                                symbol_version_id=self._symbol_version_id,
                                interval_code=self._interval.value,
                                details={
                                    "hash": result.content_hash,
                                    "open_time": result.candle.time.isoformat(),
                                },
                                ingestion_id=ingestion_id,
                            )
                        )
                        page_invalid += 1
                        continue
                    if result.content_hash in existing_hashes:
                        accepted_times.add(result.candle.time)
                        page_duplicates += 1
                        continue
                    self._insert_candle(result.candle, result.content_hash)
                    existing_hashes.add(result.content_hash)
                    existing_times.add(result.candle.time)
                    batch_by_time[result.candle.time] = result.content_hash
                    accepted_times.add(result.candle.time)
                    page_inserted += 1
                if quality_events:
                    self._bulk_insert_quality_events(quality_events)
                inserted_total += page_inserted
                duplicates_total += page_duplicates
                invalid_total += page_invalid
                corrected_total += page_corrected
                # Accumulate canonical accepted content hashes ordered by open
                # time (not by page segmentation) so the final ingestion hash
                # is identical for an interrupted+resumed run and an
                # uninterrupted run over the same logical range.
                for r in validated:
                    if not r.is_duplicate and not r.out_of_order:
                        accepted_by_time[r.candle.time] = r.content_hash
                proven_boundary = self._compute_accepted_boundary(
                    accepted_times, current_start, page_end
                )
                if proven_boundary < page_end:
                    missing_range = (
                        proven_boundary,
                        page_end,
                    )
                    gap_event = make_quality_event(
                        event_type=QualityState.GAP_DETECTED.value,
                        severity="warning",
                        symbol_version_id=self._symbol_version_id,
                        interval_code=self._interval.value,
                        details={
                            "range_start": missing_range[0].isoformat(),
                            "range_end": missing_range[1].isoformat(),
                            "reason": "partial_page",
                        },
                        affected_range_start=missing_range[0],
                        affected_range_end=missing_range[1],
                        ingestion_id=ingestion_id,
                    )
                    self._bulk_insert_quality_events([gap_event])
                # Persist cumulative counters + canonical accepted-content
                # pairs + checkpoint atomically so a restarted run resumes with
                # the same evidence and content identity.
                self._persist_page_evidence(
                    ingestion_id=ingestion_id,
                    checkpoint=proven_boundary,
                    inserted=inserted_total,
                    duplicates=duplicates_total,
                    invalid=invalid_total,
                    corrected=corrected_total,
                    request_count=request_count,
                    retry_count=retry_count,
                    accepted_by_time=accepted_by_time,
                )
                self._session.commit()
                current_start = proven_boundary
                if proven_boundary < page_end:
                    self._update_ingestion(
                        ingestion_id=ingestion_id,
                        status=IngestionStatus.FAILED,
                        inserted=inserted_total,
                        duplicates=duplicates_total,
                        invalid=invalid_total,
                        corrected=corrected_total,
                        request_count=request_count,
                        retry_count=retry_count,
                        provider_latency_ms=provider_latency_ms,
                        safe_error="incomplete_range: non-contiguous page",
                        content_hash=self._compute_ingestion_hash(
                            start_time, end_time, accepted_by_time
                        ),
                        actual_start_time=start_time,
                        actual_end_time=end_time,
                        checkpoint=current_start,
                        accepted_by_time=accepted_by_time,
                    )
                    self._session.commit()
                    raise BinanceProviderUnavailableError(
                        "incomplete_range: non-contiguous page"
                    )
            content_hash = self._compute_ingestion_hash(
                start_time, end_time, accepted_by_time
            )
            self._update_ingestion(
                ingestion_id=ingestion_id,
                status=IngestionStatus.COMPLETED,
                inserted=inserted_total,
                duplicates=duplicates_total,
                invalid=invalid_total,
                corrected=corrected_total,
                request_count=request_count,
                retry_count=retry_count,
                provider_latency_ms=provider_latency_ms,
                safe_error=safe_error,
                content_hash=content_hash,
                actual_start_time=start_time,
                actual_end_time=end_time,
                checkpoint=current_start,
                accepted_by_time=accepted_by_time,
            )
            self._session.commit()
            return IngestionResult(
                ingestion_type=ingestion_type,
                status=IngestionStatus.COMPLETED,
                inserted_count=inserted_total,
                duplicate_count=duplicates_total,
                invalid_count=invalid_total,
                corrected_count=corrected_total,
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
                start_time, end_time, accepted_by_time
            )
            self._update_ingestion(
                ingestion_id=ingestion_id,
                status=IngestionStatus.FAILED,
                inserted=inserted_total,
                duplicates=duplicates_total,
                invalid=invalid_total,
                corrected=corrected_total,
                request_count=request_count,
                retry_count=retry_count,
                provider_latency_ms=provider_latency_ms,
                safe_error=str(exc)[:500],
                content_hash=content_hash,
                actual_start_time=start_time,
                actual_end_time=end_time,
                checkpoint=current_start,
                accepted_by_time=accepted_by_time,
            )
            self._session.commit()
            raise

    async def _ingest(
        self,
        ingestion_type: IngestionType,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        idempotency_key: str,
    ) -> IngestionResult:
        return await self._ingest_pages(
            ingestion_type=ingestion_type,
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            idempotency_key=idempotency_key,
        )

    def _validate_candles(
        self,
        candles: list[Candle],
        *,
        existing_hashes: set[str],
        existing_times: set[datetime],
        batch_by_time: dict[datetime, str],
        clock_drift_ms: int,
    ) -> list[Any]:
        results = []
        previous_open_time: datetime | None = None
        for candle in candles:
            ohlc_valid, ohlc_reasons = validate_candle_ohlc(
                candle.open, candle.high, candle.low, candle.close
            )
            time_valid, time_reasons = validate_candle_times(
                candle.time, candle.close_time, self._interval_seconds
            )
            vol_valid, vol_reasons = validate_candle_volumes(
                candle.volume, candle.quote_volume, candle.trade_count
            )
            all_reasons = ohlc_reasons + time_reasons + vol_reasons
            is_valid = ohlc_valid and time_valid and vol_valid
            content_hash = compute_candle_content_hash(
                symbol_version_id=self._symbol_version_id,
                interval_code=self._interval.value,
                open_time=candle.time,
                close_time=candle.close_time,
                open_price=candle.open,
                high_price=candle.high,
                low_price=candle.low,
                close_price=candle.close,
                base_volume=candle.volume,
                quote_volume=candle.quote_volume,
                trade_count=candle.trade_count,
            )
            existing_row = self._get_existing_candle_by_time(candle.time)
            is_duplicate = content_hash in existing_hashes
            is_correction = False
            existing_id: UUID | None = None
            existing_hash = ""
            duplicate_conflict = False
            out_of_order = False
            # Same-page identity: an identical repeat is a consistent duplicate;
            # a changed content at the same open time is a same-page conflict.
            batch_hash = batch_by_time.get(candle.time)
            if batch_hash is not None:
                if batch_hash == content_hash:
                    is_duplicate = True
                else:
                    duplicate_conflict = True
            if existing_row and existing_row.get("content_hash") != content_hash:
                is_correction = True
                existing_id = existing_row.get("id")
                existing_hash = existing_row.get("content_hash", "")
            if previous_open_time is not None and candle.time < previous_open_time:
                out_of_order = True
            previous_open_time = candle.time
            quality_state, _ = assess_quality(
                candle=candle,
                is_duplicate=is_duplicate,
                duplicate_conflict=duplicate_conflict,
                out_of_order=out_of_order,
                invalid_reasons=all_reasons,
                content_hash=content_hash,
                policy=self._policy,
                clock_drift_ms=clock_drift_ms,
            )
            results.append(
                type(
                    "CandleValidationResult",
                    (),
                    {
                        "candle": candle,
                        "quality_state": quality_state,
                        "is_valid": is_valid,
                        "is_duplicate": is_duplicate,
                        "is_correction": is_correction,
                        "existing_id": existing_id,
                        "existing_hash": existing_hash,
                        "duplicate_conflict": duplicate_conflict,
                        "out_of_order": out_of_order,
                        "invalid_reasons": tuple(all_reasons),
                        "content_hash": content_hash,
                    },
                )
            )
            batch_by_time[candle.time] = content_hash
        return results

    def _compute_accepted_boundary(
        self,
        accepted_times: set[datetime],
        current_start: datetime,
        page_end: datetime,
    ) -> datetime:
        """Return the boundary across identities with accepted evidence.

        Only identities that were successfully accepted (inserted, exact
        duplicate, or applied correction) may prove coverage. The durable
        boundary advances interval by interval while the expected open time is
        in accepted_times; the first missing/invalid identity stops it so a
        checkpoint never advances past a hole.
        """
        expected_time = current_start
        while expected_time < page_end:
            if expected_time in accepted_times:
                expected_time += timedelta(seconds=self._interval_seconds)
            else:
                break
        return min(expected_time, page_end)

    def _compute_page_hash(self, content_hashes: list[str]) -> str:
        payload = {
            "symbol_version_id": str(self._symbol_version_id),
            "interval_code": self._interval.value,
            "content_hashes": content_hashes,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _apply_correction(
        self,
        result: Any,
        ingestion_id: UUID,
        quality_events: list[QualityEvent],
    ) -> None:
        """Preserve the immutable original and persist a replacement version.

        The original candle row is never mutated: it is first linked to a new
        replacement row via candle_corrections, then marked superseded so only
        the replacement remains active under the partial unique index.
        """
        if result.existing_id is None:
            quality_events.append(
                make_quality_event(
                    event_type=QualityState.CORRECTION_PENDING.value,
                    severity="warning",
                    symbol_version_id=self._symbol_version_id,
                    interval_code=self._interval.value,
                    details={
                        "original_hash": result.existing_hash,
                        "replacement_hash": result.content_hash,
                        "open_time": result.candle.time.isoformat(),
                    },
                    ingestion_id=ingestion_id,
                )
            )
            return
        replacement_id = self._insert_replacement_candle(
            result.candle, result.content_hash, superseded_by=result.existing_id
        )
        self._session.execute(
            text(
                """
                update public.candles
                set superseded_by = :replacement_id
                where id = :original_id
                  and superseded_by is null
                """
            ),
            {
                "replacement_id": replacement_id,
                "original_id": result.existing_id,
            },
        )
        self._session.execute(
            text(
                """
                update public.candles
                set superseded_by = null
                where id = :replacement_id
                """
            ),
            {"replacement_id": replacement_id},
        )
        self._session.execute(
            text(
                """
                insert into public.candle_corrections (
                    exchange_id, symbol_version_id, interval_code, open_time,
                    original_candle_id, replacement_candle_id, reason,
                    source_evidence
                ) values (
                    :exchange_id, :symbol_version_id, :interval_code, :open_time,
                    :original_candle_id, :replacement_candle_id, :reason,
                    :source_evidence
                )
                """
            ),
            {
                "exchange_id": self._exchange_id,
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
                "open_time": result.candle.time,
                "original_candle_id": result.existing_id,
                "replacement_candle_id": replacement_id,
                "reason": "binance_correction",
                "source_evidence": json.dumps(
                    {
                        "ingestion_id": str(ingestion_id),
                        "original_hash": result.existing_hash,
                    }
                ),
            },
        )
        # Invalidate dependent snapshots whose membership references the
        # superseded original so corrected-out evidence is never exposed as
        # approved/fresh downstream.
        invalidated_snapshots = (
            self._session.execute(
                text(
                    """
                update public.market_snapshots
                set state = 'invalidated',
                    invalidation_reason = 'candle_correction'
                where state = 'active'
                  and id in (
                      select snapshot_id
                      from public.market_snapshot_candles
                      where candle_id = :original_candle_id
                  )
                returning id
                """
                ),
                {"original_candle_id": result.existing_id},
            )
            .scalars()
            .all()
        )
        # Append terminal correction_applied evidence for this candle so
        # snapshots built from the replacement are not blocked forever
        # (append-only resolution).
        self._resolve_quality_events(
            event_types=(QualityState.CORRECTION_PENDING.value,),
            resolution="correction_applied",
            candle_id=result.existing_id,
            ingestion_id=ingestion_id,
        )
        quality_events.append(
            make_quality_event(
                event_type=QualityState.CORRECTION_APPLIED.value,
                severity="warning",
                symbol_version_id=self._symbol_version_id,
                interval_code=self._interval.value,
                details={
                    "original_hash": result.existing_hash,
                    "replacement_hash": result.content_hash,
                    "open_time": result.candle.time.isoformat(),
                    "replacement_candle_id": str(replacement_id),
                    "invalidated_snapshot_ids": [str(s) for s in invalidated_snapshots],
                },
                affected_candle_id=result.existing_id,
                replacement_candle_id=replacement_id,
                invalidated_candle_id=result.existing_id,
                resolution="correction_applied",
                ingestion_id=ingestion_id,
            )
        )

    def _insert_replacement_candle(
        self, candle: Candle, content_hash: str, superseded_by: UUID | None
    ) -> UUID:
        row = self._session.execute(
            text(
                """
                insert into public.candles (
                    symbol_version_id, interval_code, open_time, close_time,
                    open_price, high_price, low_price, close_price,
                    base_volume, quote_volume, trade_count, finalized, content_hash,
                    superseded_by
                ) values (
                    :symbol_version_id, :interval_code, :open_time, :close_time,
                    :open_price, :high_price, :low_price, :close_price,
                    :base_volume, :quote_volume, :trade_count, true, :content_hash,
                    :superseded_by
                )
                returning id
                """
            ),
            {
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
                "open_time": candle.time,
                "close_time": candle.close_time,
                "open_price": candle.open,
                "high_price": candle.high,
                "low_price": candle.low,
                "close_price": candle.close,
                "base_volume": candle.volume,
                "quote_volume": candle.quote_volume,
                "trade_count": candle.trade_count,
                "content_hash": content_hash,
                "superseded_by": superseded_by,
            },
        ).scalar_one()
        return cast(UUID, row)

    def _get_latest_finalized_candle_time(self) -> datetime | None:
        row = (
            self._session.execute(
                text(
                    """
                select max(candle.open_time) as max_time
                from public.candles candle
                where candle.symbol_version_id = :symbol_version_id
                  and candle.interval_code = :interval_code
                  and candle.finalized = true
                  and candle.superseded_by is null
                """
                ),
                {
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                },
            )
            .mappings()
            .one_or_none()
        )
        return row["max_time"] if row and row["max_time"] is not None else None

    def _get_existing_candle_times(self) -> set[datetime]:
        rows = (
            self._session.execute(
                text(
                    """
                select candle.open_time
                from public.candles candle
                where candle.symbol_version_id = :symbol_version_id
                  and candle.interval_code = :interval_code
                  and candle.finalized = true
                  and candle.superseded_by is null
                """
                ),
                {
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                },
            )
            .scalars()
            .all()
        )
        return set(rows)

    def _get_existing_candle_hashes(self) -> set[str]:
        rows = (
            self._session.execute(
                text(
                    """
                select candle.content_hash
                from public.candles candle
                where candle.symbol_version_id = :symbol_version_id
                  and candle.interval_code = :interval_code
                  and candle.finalized = true
                  and candle.superseded_by is null
                """
                ),
                {
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                },
            )
            .scalars()
            .all()
        )
        return set(rows)

    def _get_existing_candle_by_time(
        self, open_time: datetime
    ) -> dict[str, Any] | None:
        row = (
            self._session.execute(
                text(
                    """
                select id, content_hash, open_time
                from public.candles
                where symbol_version_id = :symbol_version_id
                  and interval_code = :interval_code
                  and open_time = :open_time
                  and finalized = true
                  and superseded_by is null
                limit 1
                """
                ),
                {
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                    "open_time": open_time,
                },
            )
            .mappings()
            .one_or_none()
        )
        return dict(row) if row else None

    def _get_snapshot_candle_range(
        self, candle_ids: list[UUID]
    ) -> tuple[datetime, datetime, int]:
        rows = (
            self._session.execute(
                text(
                    """
                select min(candle.open_time) as min_time,
                       max(candle.open_time) as max_time,
                       count(*) as cnt
                from public.candles candle
                where candle.id = any(:ids)
                  and candle.symbol_version_id = :symbol_version_id
                  and candle.interval_code = :interval_code
                  and candle.finalized = true
                  and candle.superseded_by is null
                """
                ),
                {
                    "ids": candle_ids,
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                },
            )
            .mappings()
            .one()
        )
        min_time = cast(datetime, rows["min_time"])
        max_time = cast(datetime, rows["max_time"])
        return min_time, max_time, int(rows["cnt"])

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
                on conflict (symbol_version_id, interval_code, open_time)
                where superseded_by is null do nothing
                """
            ),
            {
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
                "open_time": candle.time,
                "close_time": candle.close_time,
                "open_price": candle.open,
                "high_price": candle.high,
                "low_price": candle.low,
                "close_price": candle.close,
                "base_volume": candle.volume,
                "quote_volume": candle.quote_volume,
                "trade_count": candle.trade_count,
                "content_hash": content_hash,
            },
        )

    def _get_or_create_ingestion(
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
                    status, idempotency_key, content_hash, checkpoint
                ) values (
                    :exchange_id, :symbol_version_id, :ingestion_type,
                    :interval_code, :start_time, :end_time, 'running',
                    :idempotency_key, :content_hash, :start_time
                )
                on conflict (exchange_id, symbol_version_id, interval_code,
                             requested_start_time, requested_end_time, ingestion_type)
                do update set updated_at = timezone('utc', now())
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
                "content_hash": self._compute_ingestion_hash(start_time, end_time),
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
        checkpoint: datetime | None = None,
        accepted_by_time: dict[datetime, str] | None = None,
    ) -> None:
        accepted = accepted_by_time or {}
        pairs = [[t.isoformat(), accepted[t]] for t in sorted(accepted)]
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
                    checkpoint = coalesce(:checkpoint, checkpoint),
                    page_hashes = :page_hashes,
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
                "checkpoint": checkpoint,
                "page_hashes": json.dumps(pairs),
            },
        )

    def _persist_page_evidence(
        self,
        ingestion_id: UUID,
        checkpoint: datetime,
        inserted: int,
        duplicates: int,
        invalid: int,
        corrected: int,
        request_count: int,
        retry_count: int,
        accepted_by_time: dict[datetime, str],
    ) -> None:
        """Persist cumulative counters + canonical accepted-content pairs
        atomically with the checkpoint so a restarted run resumes with the
        same evidence and content identity."""
        pairs = [[t.isoformat(), accepted_by_time[t]] for t in sorted(accepted_by_time)]
        self._session.execute(
            text(
                """
                update public.market_data_ingestions
                set checkpoint = :checkpoint,
                    inserted_count = :inserted,
                    duplicate_count = :duplicates,
                    invalid_count = :invalid,
                    corrected_count = :corrected,
                    request_count = :request_count,
                    retry_count = :retry_count,
                    page_hashes = :page_hashes,
                    updated_at = timezone('utc', now())
                where id = :id
                """
            ),
            {
                "id": ingestion_id,
                "checkpoint": checkpoint,
                "inserted": inserted,
                "duplicates": duplicates,
                "invalid": invalid,
                "corrected": corrected,
                "request_count": request_count,
                "retry_count": retry_count,
                "page_hashes": json.dumps(pairs),
            },
        )

    def _bulk_insert_quality_events(self, events: list[QualityEvent]) -> None:
        if not events:
            return
        detected_at = self._clock.now()
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
                f":{prefix}_reviewer_user_id, :{prefix}_detected_at, "
                f":{prefix}_affected_candle_id, :{prefix}_affected_range_start, "
                f":{prefix}_affected_range_end, :{prefix}_replacement_candle_id, "
                f":{prefix}_invalidated_candle_id)"
            )
            params.update(
                {
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
                    f"{prefix}_detected_at": detected_at,
                    f"{prefix}_affected_candle_id": event.affected_candle_id,
                    f"{prefix}_affected_range_start": event.affected_range_start,
                    f"{prefix}_affected_range_end": event.affected_range_end,
                    f"{prefix}_replacement_candle_id": event.replacement_candle_id,
                    f"{prefix}_invalidated_candle_id": event.invalidated_candle_id,
                }
            )
        sql = (
            "insert into public.data_quality_events ("
            "exchange_id, symbol_version_id, interval_code, event_type, "
            "severity, details, detection_policy_version, resolution, "
            "ingestion_id, snapshot_id, reviewer_user_id, detected_at, "
            "affected_candle_id, affected_range_start, affected_range_end, "
            "replacement_candle_id, invalidated_candle_id"
            f") values {','.join(values)}"
        )
        self._session.execute(text(sql), params)

    def _resolve_quality_events(
        self,
        event_types: tuple[str, ...],
        resolution: str,
        range_start: datetime | None = None,
        range_end: datetime | None = None,
        candle_id: UUID | None = None,
        ingestion_id: UUID | None = None,
    ) -> None:
        """Append terminal quality evidence (append-only resolution).

        M007 quality/correction evidence is append-only: historical rows are
        never rewritten. This inserts a terminal event (e.g. gap_repaired or
        correction_applied) scoped to the repaired range/candle, and effective
        state is derived from the event chain rather than by mutating the
        original evidence.
        """
        if not event_types:
            return
        placeholders = ", ".join(f":et{idx}" for idx in range(len(event_types)))
        matched = (
            self._session.execute(
                text(
                    f"""
                    select id, affected_candle_id, affected_range_start,
                           affected_range_end
                    from public.data_quality_events
                    where symbol_version_id = :symbol_version_id
                      and interval_code = :interval_code
                      and event_type in ({placeholders})
                      and resolution is null
                      and (
                          (cast(:range_start as timestamptz) is null
                           and cast(:range_end as timestamptz) is null
                           and cast(:candle_id as uuid) is null)
                          or (
                              cast(:range_start as timestamptz) is not null
                              and affected_range_start is not null
                              and affected_range_end is not null
                              and affected_range_start
                                  >= cast(:range_start as timestamptz)
                              and affected_range_end
                                  <= cast(:range_end as timestamptz)
                          )
                          or (
                              cast(:candle_id as uuid) is not null
                              and affected_candle_id = cast(:candle_id as uuid)
                          )
                      )
                    """
                ),
                {
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                    **{f"et{idx}": et for idx, et in enumerate(event_types)},
                    "range_start": range_start,
                    "range_end": range_end,
                    "candle_id": candle_id,
                },
            )
            .mappings()
            .all()
        )
        if not matched:
            return
        for event in matched:
            self._bulk_insert_quality_events(
                [
                    make_quality_event(
                        event_type=resolution,
                        severity="info",
                        symbol_version_id=self._symbol_version_id,
                        interval_code=self._interval.value,
                        details={
                            "supersedes_event_id": str(event["id"]),
                            "event_types": list(event_types),
                            "resolution": resolution,
                        },
                        affected_candle_id=event["affected_candle_id"],
                        affected_range_start=event["affected_range_start"],
                        affected_range_end=event["affected_range_end"],
                        resolution=resolution,
                        ingestion_id=ingestion_id,
                    )
                ]
            )

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
                on conflict (snapshot_hash) do nothing
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
        ).scalar_one_or_none()
        if row is None:
            return cast(
                UUID,
                self._session.execute(
                    text(
                        """
                        select id
                        from public.market_snapshots
                        where snapshot_hash = :snapshot_hash
                        limit 1
                        """
                    ),
                    {"snapshot_hash": snapshot_hash},
                ).scalar_one(),
            )
        return cast(UUID, row)

    def _insert_snapshot_candles(
        self, snapshot_id: UUID, candle_ids: list[UUID]
    ) -> None:
        values = []
        params: dict[str, Any] = {"snapshot_id": snapshot_id}
        for idx, candle_id in enumerate(candle_ids):
            prefix = f"c{idx}"
            values.append(
                f"(:{prefix}_snapshot_id, :{prefix}_candle_id, :{prefix}_sequence)"
            )
            params.update(
                {
                    f"{prefix}_snapshot_id": snapshot_id,
                    f"{prefix}_candle_id": candle_id,
                    f"{prefix}_sequence": idx + 1,
                }
            )
        sql = (
            "insert into public.market_snapshot_candles "
            "(snapshot_id, candle_id, sequence) "
            f"values {','.join(values)} "
            "on conflict (snapshot_id, candle_id) do nothing"
        )
        self._session.execute(text(sql), params)

    def _compute_ingestion_hash(
        self,
        start_time: datetime,
        end_time: datetime,
        accepted_by_time: dict[datetime, str] | None = None,
    ) -> str:
        """Content-based ingestion identity.

        Derived from the canonical ordered accepted-content pairs plus stable
        metadata (exchange, symbol version, interval, requested range). It
        deliberately excludes operational counters and retry/restart history,
        so identical final candles yield the same hash whether the run was
        uninterrupted or resumed after a checkpoint.
        """
        accepted = accepted_by_time or {}
        ordered_pairs = [[t.isoformat(), accepted[t]] for t in sorted(accepted)]
        payload = {
            "exchange_id": str(self._exchange_id),
            "symbol_version_id": str(self._symbol_version_id),
            "interval_code": self._interval.value,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "accepted_content": ordered_pairs,
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
