"""Market data ingestion and quality service for M007."""

from __future__ import annotations

import asyncio
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
    MetadataObservationConflictError,
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

# Explicit terminal transition map: blocker event type -> allowed terminal
# (resolution) type. Only these transitions are legal; anything else fails
# closed. Duplicate_conflict, provider_unavailable, rate_limited, and other
# blocker types NOT listed here are non-resolvable and can never be cleared by
# a terminal child.
_TERMINAL_TRANSITIONS: dict[str, set[str]] = {
    QualityState.GAP_DETECTED.value: {QualityState.GAP_REPAIRED.value},
    QualityState.GAP_UNRESOLVED.value: {QualityState.GAP_REPAIRED.value},
    QualityState.CORRECTION_PENDING.value: {QualityState.CORRECTION_APPLIED.value},
    QualityState.CLOCK_DRIFT_EXCEEDED.value: {QualityState.CLOCK_DRIFT_RECOVERED.value},
    # A valid replacement candle at the same open time resolves invalid
    # evidence; correction_applied is the documented terminal for it.
    QualityState.INVALID_VALUE.value: {QualityState.CORRECTION_APPLIED.value},
    QualityState.INVALID_INTERVAL.value: {QualityState.CORRECTION_APPLIED.value},
}

# Terminal event types permitted in the structured supersedes child role.
_TERMINAL_EVENT_TYPES = frozenset(
    {
        QualityState.GAP_REPAIRED.value,
        QualityState.CORRECTION_APPLIED.value,
        QualityState.CLOCK_DRIFT_RECOVERED.value,
    }
)

_DEFAULT_BACKFILL_MAX_RANGE_DAYS = 30
_DEFAULT_INCREMENTAL_MAX_RANGE_HOURS = 2
_DEFAULT_INCREMENTAL_OVERLAP_HOURS = 1
_DEFAULT_INTERVAL = CandleInterval.ONE_HOUR
_MAX_PAGE_CANDLES = 1000
_SNAPSHOT_SCHEMA_VERSION = "1.0"
_CLOCK_DRIFT_TOLERANCE = timedelta(hours=1)


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
        metadata_max_age_hours: int = 24,
    ) -> None:
        self._session = session
        self._provider = provider
        self._workspace_id = workspace_id
        self._exchange_id = exchange_id
        self._symbol_version_id = symbol_version_id
        self._interval = interval
        self._clock = clock or get_clock()
        self._backfill_max_range_days = backfill_max_range_days
        if incremental_max_range_hours <= 0:
            raise ValueError(
                "incremental_max_range_hours must be positive; "
                f"got {incremental_max_range_hours}"
            )
        self._incremental_max_range_hours = incremental_max_range_hours
        if (
            incremental_overlap_hours < 0
            or incremental_overlap_hours >= incremental_max_range_hours
        ):
            raise ValueError(
                "incremental_overlap_hours must satisfy "
                f"0 <= overlap < max_range; got overlap={incremental_overlap_hours}, "
                f"max_range={incremental_max_range_hours}"
            )
        self._incremental_overlap_hours = incremental_overlap_hours
        self._policy = policy or ValidationPolicy(
            interval_seconds=_INTERVAL_SECONDS[interval]
        )
        self._interval_seconds = _INTERVAL_SECONDS[interval]
        self._snapshot_schema_version = _SNAPSHOT_SCHEMA_VERSION
        if metadata_max_age_hours <= 0:
            raise ValueError(
                f"metadata_max_age_hours must be positive; got {metadata_max_age_hours}"
            )
        self._metadata_max_age_hours = metadata_max_age_hours

    async def load_server_time(self) -> ExchangeTime:
        assert_network_call_allowed()
        return await self._provider.get_server_time()

    async def load_symbol_metadata(self, symbol: str) -> SymbolMetadata:
        assert_network_call_allowed()
        return await self._provider.get_symbol_metadata(symbol)

    def _compute_symbol_metadata_hash(self, metadata: SymbolMetadata) -> str:
        payload = {
            "symbol": metadata.symbol,
            "base_asset": metadata.base_asset,
            "quote_asset": metadata.quote_asset,
            "status": metadata.status.value,
            "price_precision": metadata.price_precision,
            "quantity_precision": metadata.quantity_precision,
            "min_quantity": str(metadata.min_quantity),
            "max_quantity": str(metadata.max_quantity),
            "min_notional": str(metadata.min_notional),
            "max_notional": str(metadata.max_notional)
            if metadata.max_notional is not None
            else None,
            "tick_size": str(metadata.tick_size),
            "step_size": str(metadata.step_size),
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _metadata_request_key(
        self,
        symbol: str,
        request_evidence: dict[str, Any],
        raw_hash: str,
        retrieved_at: datetime,
    ) -> str:
        """Deterministic observation/request identity for idempotent delivery.

        The key binds the bounded canonical request identity to the source
        observation (raw hash + retrieval time) and the exchange identity so
        identical observations on different exchanges remain distinct. Exact
        replay or duplicate delivery of the same request+source observation
        produces the same key, while a genuinely new refresh attempt
        (different retrieval time or raw payload) produces a new key.
        """
        canonical = json.dumps(
            {
                "request": request_evidence,
                "exchange_id": str(self._exchange_id),
                "symbol": symbol.upper(),
                "raw_metadata_hash": raw_hash,
                "retrieved_at": retrieved_at.astimezone(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%f"
                ),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _record_metadata_observation(
        self,
        symbol_version_id: UUID | None,
        symbol: str,
        *,
        metadata_hash: str,
        raw_hash: str,
        retrieved_at: datetime,
        observed_at: datetime,
        disposition: str = "verified",
        request_evidence: dict[str, Any] | None = None,
    ) -> bool:
        """Persist one immutable bounded raw observation.

        Returns True if a new row was inserted, False if the request_key
        collided with an existing observation (duplicate replay).
        """
        evidence = request_evidence or {"provider": type(self._provider).__name__}
        result = self._session.execute(
            text(
                """
                insert into public.symbol_metadata_observations (
                    request_key, symbol_version_id, exchange_id, native_symbol,
                    disposition, metadata_hash, raw_metadata_hash, retrieved_at,
                    observed_at, request_evidence
                ) values (
                    public.compute_metadata_request_key(
                        :exchange_id,
                        :native_symbol,
                        :raw_hash,
                        :retrieved_at,
                        :request_evidence
                    ),
                    :symbol_version_id, :exchange_id, :native_symbol,
                    :disposition, :metadata_hash, :raw_hash, :retrieved_at,
                    :observed_at, :request_evidence
                )
                on conflict (request_key) do nothing
                """
            ),
            {
                "symbol_version_id": symbol_version_id,
                "exchange_id": self._exchange_id,
                "native_symbol": symbol.upper(),
                "disposition": disposition,
                "metadata_hash": metadata_hash,
                "raw_hash": raw_hash,
                "retrieved_at": retrieved_at,
                "observed_at": observed_at,
                "request_evidence": json.dumps(evidence),
            },
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    def _resolve_observation_version(
        self,
        symbol: str,
        metadata_hash: str,
        event_time: datetime,
    ) -> UUID | None:
        """Return the version effective at event_time whose metadata_hash
        matches the observation, or None if no such version exists.

        This proves the matched version was actually authoritative for the
        observation's time window, instead of merely being the latest
        historical version with the same hash.
        """
        effective_id = self._resolve_effective_symbol_version(symbol, event_time)
        if effective_id is None:
            return None
        row = (
            self._session.execute(
                text(
                    """
                    select metadata_hash
                    from public.exchange_symbol_versions
                    where id = :id
                    """
                ),
                {"id": effective_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None or row["metadata_hash"] != metadata_hash:
            return None
        return effective_id

    async def refresh_symbol_metadata(self, symbol: str) -> UUID:
        """Fetch, normalize, hash, and persist/version symbol metadata.

        Returns the canonical symbol_version_id. If the authoritative metadata
        has changed since the last effective version, a new immutable version
        row is inserted and the new ID is returned. The prior effective version
        is linked via superseded_by. Concurrent refresh for the same symbol is
        serialized with a PostgreSQL advisory lock.

        The provider observation happens before the lock, so under the lock the
        incoming observation timestamp is compared with the current version's
        effective time: an observation strictly older than the current version
        is never allowed to supersede a newer verified version (it is retained
        as stale_conflict evidence linked to its matching historical version,
        if any), and an equal-timestamp conflicting payload fails closed.
        Every refresh persists one bounded raw observation row keyed by a
        deterministic request_key.
        """
        assert_network_call_allowed()
        metadata = await self._provider.get_symbol_metadata(symbol, force_refresh=True)
        metadata_hash = self._compute_symbol_metadata_hash(metadata)
        raw_hash = metadata.raw_metadata_hash
        retrieved_at = metadata.retrieved_at or self._clock.now()
        observed_at = self._clock.now()
        request_evidence = dict(metadata.request_evidence) or {
            "provider": type(self._provider).__name__
        }
        symbol_key = int.from_bytes(
            hashlib.sha256(
                f"metadata_refresh:{self._exchange_id}:{symbol.upper()}".encode()
            ).digest()[:8],
            signed=True,
        )
        try:
            self._session.execute(
                text("select pg_advisory_xact_lock(:lock_key)"),
                {"lock_key": symbol_key},
            )
            row = (
                self._session.execute(
                    text(
                        """
                        select id, metadata_hash, effective_at
                        from public.exchange_symbol_versions
                        where exchange_id = :exchange_id
                          and native_symbol = :native_symbol
                          and superseded_by is null
                        order by effective_at desc
                        limit 1
                        """
                    ),
                    {
                        "exchange_id": self._exchange_id,
                        "native_symbol": symbol.upper(),
                    },
                )
                .mappings()
                .one_or_none()
            )
            if (
                row is not None
                and row["metadata_hash"] != metadata_hash
                and retrieved_at < cast(datetime, row["effective_at"])
            ):
                # Observation-order guard: this observation is strictly older
                # than the currently verified version, so a concurrent worker
                # already persisted a newer authoritative observation. Never
                # let the older observation supersede the newer version; retain
                # it as immutable stale_conflict evidence linked to the
                # historical version it describes, if one exists.
                stale_version = self._resolve_observation_version(
                    symbol, metadata_hash, retrieved_at
                )
                self._record_metadata_observation(
                    stale_version,
                    symbol,
                    metadata_hash=metadata_hash,
                    raw_hash=raw_hash,
                    retrieved_at=retrieved_at,
                    observed_at=observed_at,
                    disposition="stale_conflict",
                    request_evidence=request_evidence,
                )
                self._session.commit()
                return cast(UUID, row["id"])
            if (
                row is not None
                and row["metadata_hash"] != metadata_hash
                and retrieved_at == cast(datetime, row["effective_at"])
            ):
                self._record_metadata_observation(
                    row["id"],
                    symbol,
                    metadata_hash=metadata_hash,
                    raw_hash=raw_hash,
                    retrieved_at=retrieved_at,
                    observed_at=observed_at,
                    disposition="equal_timestamp_conflict",
                    request_evidence=request_evidence,
                )
                self._session.commit()
                raise MetadataObservationConflictError(
                    "conflicting symbol metadata observed at the same "
                    f"retrieved_at {retrieved_at.isoformat()} for "
                    f"{symbol.upper()} on exchange {self._exchange_id}; "
                    "no process-independent ordering exists"
                )
            if row is not None and row["metadata_hash"] == metadata_hash:
                inserted = self._record_metadata_observation(
                    row["id"],
                    symbol,
                    metadata_hash=metadata_hash,
                    raw_hash=raw_hash,
                    retrieved_at=retrieved_at,
                    observed_at=observed_at,
                    disposition="verified",
                    request_evidence=request_evidence,
                )
                if inserted:
                    now = self._clock.now()
                    if now - retrieved_at <= timedelta(
                        hours=self._metadata_max_age_hours
                    ):
                        self._session.execute(
                            text(
                                """
                                update public.exchange_symbol_versions
                                set last_verified_at = greatest(last_verified_at, :now)
                                where id = :id
                                """
                            ),
                            {"id": row["id"], "now": retrieved_at},
                        )
                self._session.commit()
                return cast(UUID, row["id"])
            prior_id = row["id"] if row is not None else None
            if prior_id is not None:
                now = self._clock.now()
                is_stale = now - retrieved_at > timedelta(
                    hours=self._metadata_max_age_hours
                )
                new_id = self._session.execute(
                    text(
                        """
                        insert into public.exchange_symbol_versions (
                            exchange_id, native_symbol, base_asset, quote_asset,
                            status, price_precision, quantity_precision,
                            tick_size, step_size, min_quantity, max_quantity,
                            min_notional, max_notional, metadata_hash, effective_at,
                            superseded_by, raw_metadata_hash, retrieved_at,
                            last_verified_at
                        ) values (
                            :exchange_id, :native_symbol, :base_asset, :quote_asset,
                            :status, :price_precision, :quantity_precision,
                            :tick_size, :step_size, :min_quantity, :max_quantity,
                            :min_notional, :max_notional, :metadata_hash, :effective_at,
                            :prior_id, :raw_hash, :retrieved_at,
                            case when :is_stale then null else :retrieved_at end
                        )
                        returning id
                        """
                    ),
                    {
                        "exchange_id": self._exchange_id,
                        "native_symbol": symbol.upper(),
                        "base_asset": metadata.base_asset,
                        "quote_asset": metadata.quote_asset,
                        "status": metadata.status.value,
                        "price_precision": metadata.price_precision,
                        "quantity_precision": metadata.quantity_precision,
                        "tick_size": metadata.tick_size,
                        "step_size": metadata.step_size,
                        "min_quantity": metadata.min_quantity,
                        "max_quantity": metadata.max_quantity,
                        "min_notional": metadata.min_notional,
                        "max_notional": metadata.max_notional,
                        "metadata_hash": metadata_hash,
                        "effective_at": retrieved_at,
                        "prior_id": prior_id,
                        "raw_hash": raw_hash,
                        "retrieved_at": retrieved_at,
                        "is_stale": is_stale,
                    },
                ).scalar_one()
                self._session.execute(
                    text(
                        """
                        update public.exchange_symbol_versions
                        set superseded_by = :new_id
                        where id = :prior_id
                        """
                    ),
                    {"prior_id": prior_id, "new_id": new_id},
                )
                self._session.execute(
                    text(
                        """
                        update public.exchange_symbol_versions
                        set superseded_by = null
                        where id = :new_id
                        """
                    ),
                    {"new_id": new_id},
                )
            else:
                now = self._clock.now()
                is_stale = now - retrieved_at > timedelta(
                    hours=self._metadata_max_age_hours
                )
                new_id = self._session.execute(
                    text(
                        """
                        insert into public.exchange_symbol_versions (
                            exchange_id, native_symbol, base_asset, quote_asset,
                            status, price_precision, quantity_precision,
                            tick_size, step_size, min_quantity, max_quantity,
                            min_notional, max_notional, metadata_hash, effective_at,
                            superseded_by, raw_metadata_hash, retrieved_at,
                            last_verified_at
                        ) values (
                            :exchange_id, :native_symbol, :base_asset, :quote_asset,
                            :status, :price_precision, :quantity_precision,
                            :tick_size, :step_size, :min_quantity, :max_quantity,
                            :min_notional, :max_notional, :metadata_hash, :effective_at,
                            null, :raw_hash, :retrieved_at,
                            case when :is_stale then null else :retrieved_at end
                        )
                        returning id
                        """
                    ),
                    {
                        "exchange_id": self._exchange_id,
                        "native_symbol": symbol.upper(),
                        "base_asset": metadata.base_asset,
                        "quote_asset": metadata.quote_asset,
                        "status": metadata.status.value,
                        "price_precision": metadata.price_precision,
                        "quantity_precision": metadata.quantity_precision,
                        "tick_size": metadata.tick_size,
                        "step_size": metadata.step_size,
                        "min_quantity": metadata.min_quantity,
                        "max_quantity": metadata.max_quantity,
                        "min_notional": metadata.min_notional,
                        "max_notional": metadata.max_notional,
                        "metadata_hash": metadata_hash,
                        "effective_at": retrieved_at,
                        "raw_hash": raw_hash,
                        "retrieved_at": retrieved_at,
                        "is_stale": is_stale,
                    },
                ).scalar_one()
            inserted = self._record_metadata_observation(
                new_id,
                symbol,
                metadata_hash=metadata_hash,
                raw_hash=raw_hash,
                retrieved_at=retrieved_at,
                observed_at=observed_at,
                disposition="verified",
                request_evidence=request_evidence,
            )
            if inserted:
                self._session.execute(
                    text(
                        """
                        update public.exchange_symbol_versions
                        set last_verified_at = greatest(last_verified_at, :now)
                        where id = :id
                        """
                    ),
                    {"id": new_id, "now": self._clock.now()},
                )
            self._session.commit()
            return cast(UUID, new_id)
        except Exception:
            self._session.rollback()
            raise

    async def _validate_symbol_binding(self, symbol: str) -> None:
        """Reject a requested symbol that is not the configured symbol version.

        Canonical candle identity includes exchange + symbol-version +
        interval + open time. This requires the resolved symbol version to
        match BOTH the configured symbol_version_id AND the configured
        exchange, so provider data can never be attributed to a symbol version
        owned by a different exchange.
        """
        row = (
            self._session.execute(
                text(
                    """
                    select native_symbol, exchange_id, superseded_by,
                           retrieved_at, last_verified_at, source_evidence_state
                    from public.exchange_symbol_versions
                    where id = :symbol_version_id
                    """
                ),
                {"symbol_version_id": self._symbol_version_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            self._session.rollback()
            canonical_id = await self.refresh_symbol_metadata(symbol)
            if canonical_id != self._symbol_version_id:
                self._symbol_version_id = canonical_id
            return
        if cast(UUID, row["exchange_id"]) != self._exchange_id:
            raise ValueError(
                f"symbol_version_id {self._symbol_version_id} is owned by "
                f"exchange {row['exchange_id']}, not configured exchange "
                f"{self._exchange_id}"
            )
        native_symbol = cast(str, row["native_symbol"])
        if native_symbol.upper() != symbol.upper():
            raise ValueError(
                f"symbol {symbol!r} does not match configured native symbol "
                f"{native_symbol!r} for symbol_version_id "
                f"{self._symbol_version_id}"
            )
        if row["superseded_by"] is not None:
            self._session.rollback()
            canonical_id = await self.refresh_symbol_metadata(symbol)
            if canonical_id != self._symbol_version_id:
                self._symbol_version_id = canonical_id
            return
        last_verified_at = row.get("last_verified_at") or row.get("retrieved_at")
        now = self._clock.now()
        if (
            last_verified_at is None
            or (now - last_verified_at > timedelta(hours=self._metadata_max_age_hours))
            or (last_verified_at - now > _CLOCK_DRIFT_TOLERANCE)
        ):
            self._session.rollback()
            canonical_id = await self.refresh_symbol_metadata(symbol)
            if canonical_id != self._symbol_version_id:
                self._symbol_version_id = canonical_id

    def _resolve_effective_symbol_version(
        self, symbol: str, event_time: datetime
    ) -> UUID | None:
        """Return the symbol version effective at event_time for the configured
        exchange+symbol, or None if no version covers that time.

        Effective metadata is only proven from its effective time forward.
        Absence of a version at or before event_time must fail closed (or
        require explicit historical evidence) rather than extrapolate
        backwards to a future version.
        """
        native = symbol.upper()
        row = (
            self._session.execute(
                text(
                    """
                    select id
                    from public.exchange_symbol_versions
                    where exchange_id = :exchange_id
                      and native_symbol = :native_symbol
                      and effective_at <= :event_time
                    order by effective_at desc
                    limit 1
                    """
                ),
                {
                    "exchange_id": self._exchange_id,
                    "native_symbol": native,
                    "event_time": event_time,
                },
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return cast(UUID, row["id"])

    async def _validate_symbol_binding_for_backfill(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """Historical binding for backfill.

        Canonical candle identity requires the symbol-version effective at the
        requested event time. Unlike live/incremental binding this method does
        not rotate a superseded configured version to the current version: it
        resolves the version effective for [start_time, end_time) and rejects
        ranges that cross a metadata-version boundary.
        """
        row = (
            self._session.execute(
                text(
                    """
                    select native_symbol, exchange_id
                    from public.exchange_symbol_versions
                    where id = :symbol_version_id
                    """
                ),
                {"symbol_version_id": self._symbol_version_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            # Bootstrap: fetch today's metadata to establish the configured
            # version, then re-run the historical lookup. A fresh observation
            # is not historical evidence and must not label a range that
            # predates every version.
            self._session.commit()
            canonical_id = await self.refresh_symbol_metadata(symbol)
            if canonical_id != self._symbol_version_id:
                self._symbol_version_id = canonical_id
            row = (
                self._session.execute(
                    text(
                        """
                        select native_symbol, exchange_id
                        from public.exchange_symbol_versions
                        where id = :symbol_version_id
                        """
                    ),
                    {"symbol_version_id": self._symbol_version_id},
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise ValueError(
                    f"configured symbol_version_id {self._symbol_version_id} "
                    f"does not exist after metadata bootstrap for {symbol}"
                )
        if cast(UUID, row["exchange_id"]) != self._exchange_id:
            raise ValueError(
                f"symbol_version_id {self._symbol_version_id} is owned by "
                f"exchange {row['exchange_id']}, not configured exchange "
                f"{self._exchange_id}"
            )
        native_symbol = cast(str, row["native_symbol"])
        if native_symbol.upper() != symbol.upper():
            raise ValueError(
                f"symbol {symbol!r} does not match configured native symbol "
                f"{native_symbol!r} for symbol_version_id "
                f"{self._symbol_version_id}"
            )
        effective_id = self._resolve_effective_symbol_version(symbol, start_time)
        if effective_id is None:
            raise ValueError(
                f"no symbol metadata version is effective at or before "
                f"backfill start {start_time.isoformat()} for "
                f"{symbol.upper()} on exchange {self._exchange_id}; "
                "fail closed instead of fabricating historical coverage"
            )
        effective_at = self._session.execute(
            text(
                """
                    select effective_at
                    from public.exchange_symbol_versions
                    where id = :id
                    """
            ),
            {"id": effective_id},
        ).scalar_one()
        next_effective = self._session.execute(
            text(
                """
                    select min(effective_at)
                    from public.exchange_symbol_versions
                    where exchange_id = :exchange_id
                      and native_symbol = :native_symbol
                      and effective_at > :effective_at
                    """
            ),
            {
                "exchange_id": self._exchange_id,
                "native_symbol": symbol.upper(),
                "effective_at": effective_at,
            },
        ).scalar_one()
        if next_effective is not None and end_time > next_effective:
            raise ValueError(
                "backfill range crosses a symbol metadata version boundary at "
                f"{next_effective.isoformat()}; partition the range"
            )
        if effective_id != self._symbol_version_id:
            self._symbol_version_id = effective_id

    async def backfill(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        idempotency_key: str,
    ) -> IngestionResult:
        assert_network_call_allowed()
        start_time, end_time = self._normalize_range(start_time, end_time)
        max_duration = timedelta(days=self._backfill_max_range_days)
        if end_time - start_time > max_duration:
            raise ValueError(
                f"Backfill range exceeds {self._backfill_max_range_days} days"
            )
        await self._validate_symbol_binding_for_backfill(symbol, start_time, end_time)
        # The symbol-binding SELECT autobegan a session transaction; close it
        # before any provider I/O.
        self._session.commit()
        return await self._ingest_pages(
            ingestion_type=IngestionType.BACKFILL,
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            idempotency_key=idempotency_key,
        )

    def _normalize_range(
        self, start_time: datetime, end_time: datetime
    ) -> tuple[datetime, datetime]:
        """Validate a backfill range without widening the requested bounds.

        A missing evidence range must never appear as an empty successful
        dataset: start >= end is invalid. Boundaries must already be aligned
        to interval boundaries — silently widening [start, end) would fetch
        and persist evidence outside the caller's requested bounds and could
        expand into an unfinalized candle near the current interval, so
        non-aligned boundaries are rejected instead of normalized.
        """
        if start_time.tzinfo is None or end_time.tzinfo is None:
            raise ValueError("Backfill boundaries must be timezone-aware UTC")
        start_time = start_time.astimezone(timezone.utc)
        end_time = end_time.astimezone(timezone.utc)
        if start_time >= end_time:
            raise ValueError(
                "Backfill requires start_time < end_time; "
                f"got [{start_time.isoformat()}, {end_time.isoformat()})"
            )
        if start_time != self._align_to_interval(start_time):
            raise ValueError(
                "Backfill start_time must be aligned to an interval boundary; "
                f"got {start_time.isoformat()}"
            )
        if end_time != self._align_to_interval(end_time):
            raise ValueError(
                "Backfill end_time must be aligned to an interval boundary; "
                f"got {end_time.isoformat()}"
            )
        return start_time, end_time

    async def incremental_fetch(
        self,
        symbol: str,
        idempotency_key: str,
    ) -> IngestionResult:
        assert_network_call_allowed()
        await self._validate_symbol_binding(symbol)
        # The symbol-binding SELECT above autobegan a session transaction;
        # close it so the server-time provider I/O runs with no active DB
        # transaction.
        self._session.commit()

        # Preflight provider I/O with attempt/retry telemetry captured so a
        # timeout/429 leaves a durable failed ingestion attempt and retries on
        # a successful preflight are attributed to the resulting ingestion.
        retry_before = getattr(self._provider, "retry_count", 0)
        try:
            st = await self._provider.get_server_time()
        except asyncio.CancelledError:
            self._persist_preflight_cancelled(
                symbol=symbol,
                idempotency_key=idempotency_key,
                retry_before=retry_before,
            )
            raise
        except Exception as exc:
            self._persist_preflight_failure(
                symbol=symbol,
                idempotency_key=idempotency_key,
                retry_before=retry_before,
                error=exc,
            )
            raise
        preflight_retry_count = max(
            0, getattr(self._provider, "retry_count", 0) - retry_before
        )
        start_time, end_time = self._compute_incremental_range(st.server_time)
        if start_time >= end_time:
            latest_candle_time = self._get_latest_finalized_candle_time()
            quality_events = [
                make_quality_event(
                    event_type=QualityState.STALE.value,
                    severity="error",
                    symbol_version_id=self._symbol_version_id,
                    interval_code=self._interval.value,
                    details={
                        "reason": "future_persisted_candle_or_invalid_range",
                        "server_time": st.server_time.isoformat(),
                        "latest_candle": latest_candle_time.isoformat()
                        if latest_candle_time
                        else None,
                    },
                    affected_range_start=start_time,
                    affected_range_end=end_time,
                )
            ]
            self._bulk_insert_quality_events(quality_events)
            provisional_end = self._align_to_interval(st.server_time)
            provisional_start = provisional_end - timedelta(
                hours=self._incremental_max_range_hours
            )
            ingestion_id = self._get_or_create_ingestion(
                ingestion_type=IngestionType.PREFLIGHT_FAILURE,
                start_time=provisional_start,
                end_time=provisional_end,
                idempotency_key=self._derive_child_key(
                    parent_key=idempotency_key,
                    label="incremental-range-impossible",
                    salt=st.server_time.isoformat(),
                ),
            )
            self._update_ingestion(
                ingestion_id=ingestion_id,
                status=IngestionStatus.FAILED,
                inserted=0,
                duplicates=0,
                invalid=0,
                corrected=0,
                request_count=1,
                retry_count=preflight_retry_count,
                provider_latency_ms=None,
                safe_error="future_persisted_candle_or_invalid_range",
                content_hash=self._compute_ingestion_hash(start_time, end_time),
                actual_start_time=start_time,
                actual_end_time=end_time,
                checkpoint=start_time,
            )
            self._session.commit()
            return IngestionResult(
                ingestion_type=IngestionType.INCREMENTAL,
                status=IngestionStatus.FAILED,
                inserted_count=0,
                duplicate_count=0,
                invalid_count=0,
                corrected_count=0,
                gap_count=0,
                retry_count=preflight_retry_count,
                request_count=1,
                provider_latency_ms=None,
                safe_error="future_persisted_candle_or_invalid_range",
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
            preflight_retry_count=preflight_retry_count,
            preflight_request_count=1,
        )

    def _persist_preflight_failure(
        self,
        symbol: str,
        idempotency_key: str,
        retry_before: int,
        error: Exception,
    ) -> None:
        """Persist a durable failed incremental attempt when the preflight
        server-time call itself fails (timeout/429/5xx).

        The ingestion range cannot be derived without exchange time, so a
        provisional clock-aligned range is recorded. The attempt uses the
        dedicated PREFLIGHT_FAILURE ingestion type and a derived delivery key
        so it can never collide with, or rewrite, a canonical completed
        incremental/backfill ingestion row: completed evidence stays
        byte-for-byte immutable while this failure is separately auditable.
        """
        attempt_time = self._clock.now()
        provisional_end = attempt_time
        provisional_start = provisional_end - timedelta(
            hours=self._incremental_max_range_hours
        )
        ingestion_id = self._get_or_create_ingestion(
            ingestion_type=IngestionType.PREFLIGHT_FAILURE,
            start_time=provisional_start,
            end_time=provisional_end,
            idempotency_key=self._derive_child_key(
                parent_key=idempotency_key,
                label="preflight-failure",
                salt=attempt_time.isoformat(),
            ),
        )
        retry_count = max(0, getattr(self._provider, "retry_count", 0) - retry_before)
        self._update_ingestion(
            ingestion_id=ingestion_id,
            status=IngestionStatus.FAILED,
            inserted=0,
            duplicates=0,
            invalid=0,
            corrected=0,
            request_count=1,
            retry_count=retry_count,
            provider_latency_ms=None,
            safe_error=f"server_time_failed: {str(error)[:300]}",
            content_hash=self._compute_ingestion_hash(
                provisional_start, provisional_end
            ),
            actual_start_time=provisional_start,
            actual_end_time=provisional_end,
            checkpoint=provisional_start,
        )
        self._session.commit()

    def _persist_preflight_cancelled(
        self,
        symbol: str,
        idempotency_key: str,
        retry_before: int,
    ) -> None:
        """Persist a durable CANCELLED incremental preflight attempt when the
        server-time call is cancelled before any ingestion row exists.

        Cancellation is a BaseException, so it cannot be caught by the generic
        Exception handler in incremental_fetch. This method creates the
        dedicated preflight-attempt identity and records CANCELLED terminal
        evidence so the cancellation is auditable and never leaves the task
        in an ambiguous 'running' state.
        """
        attempt_time = self._clock.now()
        provisional_end = attempt_time
        provisional_start = provisional_end - timedelta(
            hours=self._incremental_max_range_hours
        )
        ingestion_id = self._get_or_create_ingestion(
            ingestion_type=IngestionType.PREFLIGHT_FAILURE,
            start_time=provisional_start,
            end_time=provisional_end,
            idempotency_key=self._derive_child_key(
                parent_key=idempotency_key,
                label="preflight-cancelled",
                salt=attempt_time.isoformat(),
            ),
        )
        retry_count = max(0, getattr(self._provider, "retry_count", 0) - retry_before)
        self._update_ingestion(
            ingestion_id=ingestion_id,
            status=IngestionStatus.CANCELLED,
            inserted=0,
            duplicates=0,
            invalid=0,
            corrected=0,
            request_count=1,
            retry_count=retry_count,
            provider_latency_ms=None,
            safe_error="cancelled",
            content_hash=self._compute_ingestion_hash(
                provisional_start, provisional_end
            ),
            actual_start_time=provisional_start,
            actual_end_time=provisional_end,
            checkpoint=provisional_start,
        )
        self._session.commit()

    def _align_to_interval(self, dt: datetime) -> datetime:
        """Floor a timestamp to the start of its configured interval."""
        epoch = int(dt.timestamp())
        aligned_epoch = epoch - (epoch % self._interval_seconds)
        return datetime.fromtimestamp(aligned_epoch, tz=timezone.utc)

    def _derive_child_key(self, parent_key: str, label: str, salt: str) -> str:
        """Derive a bounded, deterministic child idempotency key.

        The database CHECK requires 1 <= length <= 200, so naively appending
        labels/timestamps to a near-maximum parent key would violate the
        constraint and mask the underlying failure. A fixed prefix plus a
        truncated hash keeps the key short and deterministic for the same
        parent/label/salt.
        """
        digest = hashlib.sha256(
            f"{parent_key}|{label}|{salt}".encode("utf-8")
        ).hexdigest()
        return f"{label}-{digest[:32]}"

    def _compute_incremental_range(
        self, server_time: datetime
    ) -> tuple[datetime, datetime]:
        """Compute an incremental range aligned to finalized interval
        boundaries using trusted exchange time.

        end_time is the last finalized exclusive boundary (the start of the
        current, not-yet-finalized interval), and the start is floored to an
        interval boundary, so a 1h fetch at 22:28 covers [..., 22:00) and never
        expects a non-finalized candle.

        The configured incremental maximum range is a hard bound: the window
        must never exceed it even when the latest persisted candle is stale.
        Older missing history is routed through explicit backfill/gap evidence
        rather than turning one incremental call into an unbounded catch-up.
        """
        latest = self._get_latest_finalized_candle_time()
        end_time = self._align_to_interval(server_time)
        max_start = end_time - timedelta(hours=self._incremental_max_range_hours)
        if latest is None:
            start_time = max_start
        else:
            overlap = timedelta(hours=self._incremental_overlap_hours)
            candidate = self._align_to_interval(latest - overlap)
            start_time = max(candidate, max_start)
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
        expected_start, expected_end = self._validate_gap_bounds(
            expected_start, expected_end
        )
        existing_times = self._get_existing_candle_times()
        all_expected: list[datetime] = []
        current = expected_start
        # Half-open range convention [expected_start, expected_end): an open
        # time is expected when start <= open < end, matching the ingestion
        # contract so a persisted ingestion's requested end never creates a
        # false tail gap.
        while current < expected_end:
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

    def _validate_gap_bounds(
        self, expected_start: datetime, expected_end: datetime
    ) -> tuple[datetime, datetime]:
        """Validate the half-open gap range [start, end).

        Rejects inverted/zero ranges, requires timezone-aware UTC, and requires
        interval-aligned boundaries so the expected open-time sequence is
        deterministic.
        """
        if expected_start.tzinfo is None or expected_end.tzinfo is None:
            raise ValueError("Gap bounds must be timezone-aware UTC")
        expected_start = expected_start.astimezone(timezone.utc)
        expected_end = expected_end.astimezone(timezone.utc)
        if expected_start >= expected_end:
            raise ValueError(
                "Gap range requires expected_start < expected_end; "
                f"got [{expected_start.isoformat()}, {expected_end.isoformat()})"
            )
        if expected_start != self._align_to_interval(expected_start):
            raise ValueError(
                "Gap expected_start must be aligned to an interval boundary"
            )
        if expected_end != self._align_to_interval(expected_end):
            raise ValueError("Gap expected_end must be aligned to an interval boundary")
        return expected_start, expected_end

    def _validate_gap_report(self, gap_report: GapReport) -> None:
        """Validate a caller-supplied GapReport before any repair work.

        Rejects a foreign symbol/interval, mismatched interval_seconds,
        unaligned/inverted bounds, and a missing_count that disagrees with the
        reported missing ranges. A foreign or internally inconsistent report
        must never drive this service's provider fetches or be certified
        COMPLETED against the service's configured identity.
        """
        if gap_report.symbol_version_id != self._symbol_version_id:
            raise ValueError("GapReport symbol_version_id does not match service scope")
        if gap_report.interval_code != self._interval.value:
            raise ValueError("GapReport interval_code does not match service scope")
        if gap_report.interval_seconds != self._interval_seconds:
            raise ValueError(
                "GapReport interval_seconds does not match service interval"
            )
        self._validate_gap_bounds(gap_report.expected_start, gap_report.expected_end)
        if gap_report.missing_count == 0:
            if gap_report.missing_ranges:
                raise ValueError(
                    "GapReport missing_count=0 but missing_ranges is non-empty"
                )
            return
        if not gap_report.missing_ranges:
            raise ValueError("GapReport missing_count > 0 but missing_ranges is empty")
        covered_count = 0
        previous_end: datetime | None = None
        for range_start, range_end in gap_report.missing_ranges:
            if range_start < gap_report.expected_start or range_end > (
                gap_report.expected_end
            ):
                raise ValueError("GapReport missing range exceeds expected bounds")
            if range_end <= range_start:
                raise ValueError("GapReport missing range is not ordered")
            if range_start != self._align_to_interval(range_start) or (
                range_end != self._align_to_interval(range_end)
            ):
                raise ValueError("GapReport missing range is not interval-aligned")
            # Canonical sequence: strictly ascending and non-adjacent. A
            # contiguous gap must be a single range: splitting it into adjacent
            # ranges would change repair/hash segmentation for the same logical
            # missing set. Duplicated, overlapping, adjacent, or reversed
            # ranges are therefore rejected.
            if previous_end is not None and range_start <= previous_end:
                raise ValueError(
                    "GapReport missing ranges are not strictly ascending/"
                    "disjoint (adjacent or overlapping)"
                )
            previous_end = range_end
            covered_count += int(
                (range_end - range_start).total_seconds() // gap_report.interval_seconds
            )
        if covered_count != gap_report.missing_count:
            raise ValueError(
                "GapReport missing_count disagrees with missing range widths"
            )

    def _build_missing_report(
        self,
        symbol_version_id: UUID,
        interval_code: str,
        expected_start: datetime,
        expected_end: datetime,
        missing: list[datetime],
    ) -> GapReport:
        # Missing ranges are half-open [range_start, range_end) so repair_gaps
        # can feed them straight into the half-open ingestion contract.
        missing_ranges: list[tuple[datetime, datetime]] = []
        range_start = missing[0]
        range_end = missing[0]
        for t in missing[1:]:
            if t == range_end + timedelta(seconds=self._interval_seconds):
                range_end = t
            else:
                missing_ranges.append(
                    (range_start, range_end + timedelta(seconds=self._interval_seconds))
                )
                range_start = t
                range_end = t
        missing_ranges.append(
            (range_start, range_end + timedelta(seconds=self._interval_seconds))
        )
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
        await self._validate_symbol_binding(symbol)
        # Validate the complete caller-supplied report contract BEFORE any
        # short-circuit or provider request: a foreign or internally
        # inconsistent GapReport must never drive this service's fetches or be
        # certified COMPLETED against the service's configured identity.
        self._validate_gap_report(gap_report)
        if gap_report.missing_count == 0:
            # A zero-gap report must never be certified without proving the
            # dataset: GapReport is a public dataclass, so re-derive the gap
            # state against persisted candle coverage over the same range.
            # A forged/empty dataset therefore fails instead of producing an
            # empty successful repair.
            verification = await self.detect_gaps(
                symbol_version_id=self._symbol_version_id,
                interval_code=self._interval.value,
                expected_start=gap_report.expected_start,
                expected_end=gap_report.expected_end,
            )
            if verification.missing_count != 0:
                raise ValueError(
                    "GapReport claims zero gaps but persisted evidence "
                    "still reports missing candles"
                )
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
        child_content_hashes: list[str] = []
        for range_start, range_end in gap_report.missing_ranges:
            result = await self._ingest_pages(
                ingestion_type=IngestionType.GAP_REPAIR,
                symbol=symbol,
                start_time=range_start,
                end_time=range_end,
                idempotency_key=self._derive_child_key(
                    parent_key=idempotency_key,
                    label="gap-repair",
                    salt=range_start.isoformat(),
                ),
            )
            total_inserted += result.inserted_count
            total_duplicates += result.duplicate_count
            total_invalid += result.invalid_count
            total_corrected += result.corrected_count
            total_request_count += result.request_count
            total_retry_count += result.retry_count
            provider_latency_ms = provider_latency_ms or result.provider_latency_ms
            child_content_hashes.append(result.content_hash)
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
            content_hash=self._compute_repair_hash(
                gap_report.expected_start,
                gap_report.expected_end,
                child_content_hashes,
            ),
            idempotency_key=idempotency_key,
            actual_start_time=gap_report.expected_start,
            actual_end_time=gap_report.expected_end,
        )

    def _compute_repair_hash(
        self,
        expected_start: datetime,
        expected_end: datetime,
        child_content_hashes: list[str],
    ) -> str:
        """Repair identity derived from the ordered child ingestion content
        hashes plus stable range metadata, so two repairs over the same range
        with different replacement candles produce different hashes while an
        exact replay preserves the identity."""
        payload = {
            "exchange_id": str(self._exchange_id),
            "symbol_version_id": str(self._symbol_version_id),
            "interval_code": self._interval.value,
            "expected_start": expected_start.isoformat(),
            "expected_end": expected_end.isoformat(),
            "child_content_hashes": child_content_hashes,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def create_snapshot(
        self,
        analysis_time: datetime,
        candle_ids: list[UUID],
        quality_outcome: str,
        freshness_outcome: str,
        ingestion_id: UUID,
        creator_cycle_id: str | None = None,
        creator_job_id: str | None = None,
    ) -> SnapshotResult:
        if not candle_ids:
            raise ValueError("Cannot create snapshot with empty candle membership")
        if ingestion_id is None:
            raise ValueError(
                "Snapshot requires an ingestion_id for exact lineage; "
                "caller-supplied None is not accepted"
            )
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
        self._validate_snapshot_ingestion(
            ingestion_id, first_time, last_time, canonical_ids
        )
        snapshot_hash = self._compute_snapshot_hash(
            candle_ids=canonical_ids,
            analysis_time=analysis_time,
            first_time=first_time,
            last_time=last_time,
            count=count,
            quality_outcome=derived_quality,
            freshness_outcome=derived_freshness,
            ingestion_id=ingestion_id,
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

    def _validate_snapshot_ingestion(
        self,
        ingestion_id: UUID,
        first_time: datetime,
        last_time: datetime,
        candle_ids: list[UUID],
    ) -> None:
        """Validate that a snapshot's ingestion lineage is canonical.

        Snapshot provenance is evidence: the ingestion must belong to this
        exchange/symbol/interval, be terminal/completed, its requested range
        must cover the candidate membership, and every candidate candle must
        be directly traceable to the ingestion's accepted page evidence. A
        foreign, failed, or non-covering ingestion must never be recorded as
        this snapshot's source.
        """
        row = (
            self._session.execute(
                text(
                    """
                    select exchange_id, symbol_version_id, interval_code,
                           status, requested_start_time, requested_end_time,
                           page_hashes
                    from public.market_data_ingestions
                    where id = :ingestion_id
                    """
                ),
                {"ingestion_id": ingestion_id},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise ValueError(f"snapshot ingestion {ingestion_id} does not exist")
        if cast(UUID, row["exchange_id"]) != self._exchange_id:
            raise ValueError("snapshot ingestion exchange does not match service")
        if cast(UUID, row["symbol_version_id"]) != self._symbol_version_id:
            raise ValueError("snapshot ingestion symbol does not match service")
        if cast(str, row["interval_code"]) != self._interval.value:
            raise ValueError("snapshot ingestion interval does not match service")
        if cast(str, row["status"]) != IngestionStatus.COMPLETED.value:
            raise ValueError(
                f"snapshot ingestion {ingestion_id} is not completed "
                f"(status={row['status']})"
            )
        requested_start = cast(datetime, row["requested_start_time"])
        requested_end = cast(datetime, row["requested_end_time"])
        if requested_start > first_time or requested_end < (
            last_time + timedelta(seconds=self._interval_seconds)
        ):
            raise ValueError(
                "snapshot ingestion range does not cover the candidate membership"
            )
        page_hashes_raw = row["page_hashes"]
        if not page_hashes_raw:
            raise ValueError(
                "snapshot ingestion has no accepted page evidence "
                "(page_hashes is empty)"
            )
        if isinstance(page_hashes_raw, str):
            page_hashes = json.loads(page_hashes_raw)
        else:
            page_hashes = list(page_hashes_raw)
        accepted_lineage: dict[datetime, str] = {}
        for pair in page_hashes:
            accepted_lineage[datetime.fromisoformat(pair[0])] = pair[1]
        candidate_times = set(
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
                    """
                ),
                {
                    "ids": candle_ids,
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                },
            ).scalars()
        )
        for open_time in candidate_times:
            expected_hash = accepted_lineage.get(open_time)
            if expected_hash is None:
                raise ValueError(
                    f"snapshot candle at {open_time.isoformat()} is not present "
                    f"in ingestion {ingestion_id} accepted page evidence"
                )
            actual_hash = self._session.execute(
                text(
                    """
                    select candle.content_hash
                    from public.candles candle
                    where candle.symbol_version_id = :symbol_version_id
                      and candle.interval_code = :interval_code
                      and candle.open_time = :open_time
                      and candle.finalized = true
                      and candle.superseded_by is null
                    """
                ),
                {
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                    "open_time": open_time,
                },
            ).scalar_one_or_none()
            if actual_hash != expected_hash:
                raise ValueError(
                    f"snapshot candle at {open_time.isoformat()} has hash "
                    f"{actual_hash!r} but ingestion {ingestion_id} accepted "
                    f"{expected_hash!r}"
                )

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
                          'clock_drift_exceeded', 'duplicate_conflict',
                          'invalid_value', 'invalid_interval'
                      )
                      or blocker.severity in ('error', 'critical')
                  )
                  and (
                      (blocker.affected_range_start is null
                       and blocker.affected_range_end is null
                       and blocker.affected_candle_id is null)
                      or (
                          blocker.affected_range_start is not null
                          and blocker.affected_range_end is not null
                          -- Half-open overlap: blocker [start, end) touches
                          -- the candidate span [first_time, span_end) only
                          -- when start < span_end AND end > first_time.
                          and blocker.affected_range_start < :span_end
                          and blocker.affected_range_end > :first_time
                      )
                      or (
                          blocker.affected_candle_id is not null
                          and blocker.affected_candle_id = any(:candle_ids)
                      )
                  )
                  and not exists (
                      select 1
                      from public.data_quality_events terminal
                      where terminal.symbol_version_id = blocker.symbol_version_id
                        and terminal.interval_code = blocker.interval_code
                        and terminal.event_type = (
                            case blocker.event_type
                                when 'gap_detected' then 'gap_repaired'
                                when 'gap_unresolved' then 'gap_repaired'
                                when 'correction_pending' then 'correction_applied'
                                when 'clock_drift_exceeded' then 'clock_drift_recovered'
                                when 'invalid_value' then 'correction_applied'
                                when 'invalid_interval' then 'correction_applied'
                                else null
                            end
                        )
                        and terminal.supersedes_event_id = blocker.id
                  )
                """
            ),
            {
                "symbol_version_id": self._symbol_version_id,
                "interval_code": self._interval.value,
                "first_time": first_time,
                "span_end": last_time + timedelta(seconds=self._interval_seconds),
                "candle_ids": candle_ids,
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
        """Claim a session-scoped advisory lock serializing all ingestion work
        for this market+interval.

        The lock identity is the market+interval scope (exchange, symbol
        version, interval), NOT the caller-supplied delivery key and NOT the
        exact requested range/type. Two workers whose ranges overlap — even
        with different types (backfill vs incremental vs gap-repair) — contend
        on the same lock, so overlapping writes/counters/corrections can never
        race page persistence.

        Returns the lock key; the caller must release it in a finally block.
        A concurrent worker that cannot acquire the lock fails closed instead
        of racing page persistence.
        """
        lock_key = (
            f"m007:{self._exchange_id}:{self._symbol_version_id}:{self._interval.value}"
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
        # aborted. Roll back first so the unlock executes instead of failing in
        # the aborted transaction. Only the exact lock_key advisory lock is
        # released, never any unrelated session-level advisory locks held by
        # other workflows on the same pooled connection.
        try:
            self._session.rollback()
            self._session.execute(
                text("select pg_advisory_unlock(hashtextextended(:key, 0))"),
                {"key": lock_key},
            )
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
        preflight_retry_count: int = 0,
        preflight_request_count: int = 0,
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
                preflight_retry_count,
                preflight_request_count,
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
        preflight_retry_count: int = 0,
        preflight_request_count: int = 0,
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
        request_count = (row["request_count"] if row else 0) + preflight_request_count
        retry_count = (row["retry_count"] if row else 0) + preflight_retry_count
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
        # When a preflight already fetched server time, its attempt/retry
        # telemetry was seeded into the counters, so no additional request
        # count is recorded for the reuse.
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
            if provider_server_time is None:
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
        except asyncio.CancelledError:
            # Cancellation during the preflight server-time call must leave a
            # durable CANCELLED terminal state (CancelledError is a
            # BaseException and would otherwise skip the handler above).
            logger.warning(
                "ingestion_cancelled",
                extra={"ingestion_id": str(ingestion_id)},
            )
            try:
                content_hash = self._compute_ingestion_hash(
                    start_time, end_time, accepted_by_time
                )
                self._update_ingestion(
                    ingestion_id=ingestion_id,
                    status=IngestionStatus.CANCELLED,
                    inserted=inserted_total,
                    duplicates=duplicates_total,
                    invalid=invalid_total,
                    corrected=corrected_total,
                    request_count=request_count,
                    retry_count=retry_count,
                    provider_latency_ms=provider_latency_ms,
                    safe_error="cancelled",
                    content_hash=content_hash,
                    actual_start_time=start_time,
                    actual_end_time=end_time,
                    checkpoint=current_start,
                    accepted_by_time=accepted_by_time,
                )
                self._session.commit()
            except Exception as cleanup_exc:  # noqa: BLE001
                self._session.rollback()
                logger.error(
                    "ingestion_cancellation_persist_failed",
                    extra={
                        "ingestion_id": str(ingestion_id),
                        "error": str(cleanup_exc),
                    },
                )
            raise
        retry_delta = getattr(self._provider, "retry_count", 0) - retry_before
        retry_count += max(0, retry_delta)
        if provider_server_time is None:
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
                quality_events: list[QualityEvent] = []
                # Pre-scan the ENTIRE page for same-open-time ambiguity BEFORE
                # any insert/correction/invalidation write. Provider ordering
                # must not let an earlier unambiguous-looking row mutate
                # canonical state when a later row in the same page conflicts:
                # reject the whole page when any identity is ambiguous.
                page_conflict = next(
                    (r for r in validated if r.duplicate_conflict), None
                )
                if page_conflict is not None:
                    self._fail_on_duplicate_conflict(
                        result=page_conflict,
                        ingestion_id=ingestion_id,
                        quality_events=quality_events,
                        inserted_total=inserted_total,
                        duplicates_total=duplicates_total,
                        invalid_total=invalid_total,
                        corrected_total=corrected_total,
                        request_count=request_count,
                        retry_count=retry_count,
                        provider_latency_ms=provider_latency_ms,
                        start_time=start_time,
                        end_time=end_time,
                        current_start=current_start,
                        accepted_by_time=accepted_by_time,
                    )
                # Pre-scan the ENTIRE page for out-of-order evidence BEFORE any
                # correction/duplicate/insert mutation. A provider page that is
                # not monotonically ascending by open time is invalid evidence:
                # fail the whole page before canonical state can be mutated.
                page_out_of_order = any(r.out_of_order for r in validated)
                if page_out_of_order:
                    self._fail_on_out_of_order_page(
                        validated=validated,
                        ingestion_id=ingestion_id,
                        quality_events=quality_events,
                        inserted_total=inserted_total,
                        duplicates_total=duplicates_total,
                        invalid_total=invalid_total,
                        corrected_total=corrected_total,
                        request_count=request_count,
                        retry_count=retry_count,
                        provider_latency_ms=provider_latency_ms,
                        start_time=start_time,
                        end_time=end_time,
                        current_start=current_start,
                        accepted_by_time=accepted_by_time,
                    )
                accepted_times: set[datetime] = set()
                page_inserted = 0
                page_duplicates = 0
                page_invalid = 0
                page_corrected = 0
                for result in validated:
                    if not result.is_valid:
                        page_invalid += 1
                        # Scope the invalid evidence to the exact failed
                        # candle identity/interval so one malformed historical
                        # candle can never block unrelated future snapshots.
                        # Use a real half-open [T, T+interval) range: the gate
                        # compares half-open overlap, so a point [T, T] would
                        # never match even its own candle.
                        failed_at = result.candle.time
                        quality_events.append(
                            make_quality_event(
                                event_type=result.quality_state.value,
                                severity="error",
                                symbol_version_id=self._symbol_version_id,
                                interval_code=self._interval.value,
                                details={"reasons": result.invalid_reasons},
                                affected_range_start=failed_at,
                                affected_range_end=failed_at
                                + timedelta(seconds=self._interval_seconds),
                                ingestion_id=ingestion_id,
                            )
                        )
                        continue
                    if result.duplicate_conflict:
                        # Batch ambiguity is rejected BEFORE correction or
                        # duplicate acceptance: an open time that appears twice
                        # with different content within one provider page is
                        # invalid evidence even when one version also matches
                        # (or could correct) an existing database candle.
                        self._fail_on_duplicate_conflict(
                            result=result,
                            ingestion_id=ingestion_id,
                            quality_events=quality_events,
                            inserted_total=inserted_total,
                            duplicates_total=duplicates_total,
                            invalid_total=invalid_total,
                            corrected_total=corrected_total,
                            request_count=request_count,
                            retry_count=retry_count,
                            provider_latency_ms=provider_latency_ms,
                            start_time=start_time,
                            end_time=end_time,
                            current_start=current_start,
                            accepted_by_time=accepted_by_time,
                        )
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
                        accepted_by_time[result.candle.time] = result.content_hash
                        # The corrected/replaced candle at this open time also
                        # supersedes any prior invalid evidence over the same
                        # half-open interval.
                        self._resolve_quality_events(
                            event_types=(
                                QualityState.INVALID_VALUE.value,
                                QualityState.INVALID_INTERVAL.value,
                            ),
                            resolution="correction_applied",
                            range_start=result.candle.time,
                            range_end=result.candle.time
                            + timedelta(seconds=self._interval_seconds),
                            ingestion_id=ingestion_id,
                        )
                        continue
                    if result.is_duplicate and not result.duplicate_conflict:
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
                        accepted_by_time[result.candle.time] = result.content_hash
                        page_duplicates += 1
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
                    accepted_by_time[result.candle.time] = result.content_hash
                    page_inserted += 1
                    # A valid candle at this open time supersedes any prior
                    # invalid evidence scoped to the same interval (append-only
                    # terminal resolution by exact identity/range). Invalid
                    # evidence is persisted as a half-open [T, T+interval)
                    # range, so the resolver must use the same half-open range.
                    self._resolve_quality_events(
                        event_types=(
                            QualityState.INVALID_VALUE.value,
                            QualityState.INVALID_INTERVAL.value,
                        ),
                        resolution="correction_applied",
                        range_start=result.candle.time,
                        range_end=result.candle.time
                        + timedelta(seconds=self._interval_seconds),
                        ingestion_id=ingestion_id,
                    )
                if quality_events:
                    self._bulk_insert_quality_events(quality_events)
                inserted_total += page_inserted
                duplicates_total += page_duplicates
                invalid_total += page_invalid
                corrected_total += page_corrected
                # Accumulate canonical accepted content hashes ordered by open
                # time (not by page segmentation) so the final ingestion hash
                # is identical for an interrupted+resumed run and an
                # accepted_by_time is built only at the exact acceptance points
                # above (inserted row, consistent duplicate, applied
                # correction), so rejected content never participates in the
                # canonical content identity.
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
        except asyncio.CancelledError:
            # Cancellation is a BaseException, not an Exception, so the generic
            # failure handler below never sees it. Persist a durable CANCELLED
            # terminal state with the latest checkpoint/request/retry evidence
            # in a short shielded cleanup transaction, then re-raise.
            logger.warning(
                "ingestion_cancelled",
                extra={"ingestion_id": str(ingestion_id)},
            )
            try:
                content_hash = self._compute_ingestion_hash(
                    start_time, end_time, accepted_by_time
                )
                self._update_ingestion(
                    ingestion_id=ingestion_id,
                    status=IngestionStatus.CANCELLED,
                    inserted=inserted_total,
                    duplicates=duplicates_total,
                    invalid=invalid_total,
                    corrected=corrected_total,
                    request_count=request_count,
                    retry_count=retry_count,
                    provider_latency_ms=provider_latency_ms,
                    safe_error="cancelled",
                    content_hash=content_hash,
                    actual_start_time=start_time,
                    actual_end_time=end_time,
                    checkpoint=current_start,
                    accepted_by_time=accepted_by_time,
                )
                self._session.commit()
            except Exception as cleanup_exc:  # noqa: BLE001
                self._session.rollback()
                logger.error(
                    "ingestion_cancellation_persist_failed",
                    extra={
                        "ingestion_id": str(ingestion_id),
                        "error": str(cleanup_exc),
                    },
                )
            raise
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
        page_out_of_order = any(
            candles[i].time > candles[i + 1].time for i in range(len(candles) - 1)
        )
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
            out_of_order = page_out_of_order
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
            if not page_out_of_order:
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

    def _fail_on_duplicate_conflict(
        self,
        result: Any,
        ingestion_id: UUID,
        quality_events: list[QualityEvent],
        inserted_total: int,
        duplicates_total: int,
        invalid_total: int,
        corrected_total: int,
        request_count: int,
        retry_count: int,
        provider_latency_ms: int | None,
        start_time: datetime,
        end_time: datetime,
        current_start: datetime,
        accepted_by_time: dict[datetime, str],
    ) -> None:
        """Fail the affected page/ingestion on an inconsistent same-open-time
        duplicate (M007 invalid evidence).

        The conflict event is scoped to the exact open time and is an explicit
        snapshot-gate blocker. This is invoked before correction or duplicate
        acceptance so batch ambiguity can never be resolved into a correction
        or advance the durable boundary past a corrupted open time.
        """
        quality_events.append(
            make_quality_event(
                event_type=QualityState.DUPLICATE_CONFLICT.value,
                severity="error",
                symbol_version_id=self._symbol_version_id,
                interval_code=self._interval.value,
                details={
                    "hash": result.content_hash,
                    "open_time": result.candle.time.isoformat(),
                    "reason": "same_page_conflict",
                },
                affected_range_start=result.candle.time,
                affected_range_end=result.candle.time
                + timedelta(seconds=self._interval_seconds),
                ingestion_id=ingestion_id,
            )
        )
        self._bulk_insert_quality_events(quality_events)
        self._persist_page_evidence(
            ingestion_id=ingestion_id,
            checkpoint=current_start,
            inserted=inserted_total,
            duplicates=duplicates_total,
            invalid=invalid_total,
            corrected=corrected_total,
            request_count=request_count,
            retry_count=retry_count,
            accepted_by_time=accepted_by_time,
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
            safe_error=(
                "duplicate_conflict: inconsistent same-open-time "
                "candles within one provider page"
            ),
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
            "duplicate_conflict: inconsistent same-open-time "
            "candles within one provider page"
        )

    def _fail_on_out_of_order_page(
        self,
        validated: list[Any],
        ingestion_id: UUID,
        quality_events: list[QualityEvent],
        inserted_total: int,
        duplicates_total: int,
        invalid_total: int,
        corrected_total: int,
        request_count: int,
        retry_count: int,
        provider_latency_ms: int | None,
        start_time: datetime,
        end_time: datetime,
        current_start: datetime,
        accepted_by_time: dict[datetime, str],
    ) -> None:
        """Fail the affected page/ingestion on an out-of-order provider page.

        A page whose rows are not monotonically ascending by open time is
        invalid evidence. This is invoked before correction/duplicate/insert
        mutation so no canonical state is changed by an unordered page.
        """
        affected = next(r for r in validated if r.out_of_order)
        quality_events.append(
            make_quality_event(
                event_type=QualityState.OUT_OF_ORDER.value,
                severity="error",
                symbol_version_id=self._symbol_version_id,
                interval_code=self._interval.value,
                details={
                    "hash": affected.content_hash,
                    "open_time": affected.candle.time.isoformat(),
                    "reason": "out_of_order_page",
                },
                affected_range_start=current_start,
                affected_range_end=min(
                    current_start
                    + timedelta(seconds=self._interval_seconds) * len(validated),
                    end_time,
                ),
                ingestion_id=ingestion_id,
            )
        )
        self._bulk_insert_quality_events(quality_events)
        self._persist_page_evidence(
            ingestion_id=ingestion_id,
            checkpoint=current_start,
            inserted=inserted_total,
            duplicates=duplicates_total,
            invalid=invalid_total,
            corrected=corrected_total,
            request_count=request_count,
            retry_count=retry_count,
            accepted_by_time=accepted_by_time,
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
            safe_error=(
                "out_of_order: provider page is not monotonically ascending "
                "by open time"
            ),
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
            "out_of_order: provider page is not monotonically ascending by open time"
        )

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
        result = self._session.execute(
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
                  and status <> 'completed'
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
        if result.rowcount == 0:  # type: ignore[attr-defined]
            raise RuntimeError(
                f"refusing to mutate completed ingestion evidence {ingestion_id}"
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
                f":{prefix}_invalidated_candle_id, :{prefix}_supersedes_event_id)"
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
                    f"{prefix}_supersedes_event_id": event.supersedes_event_id,
                }
            )
        sql = (
            "insert into public.data_quality_events ("  # nosec B608: parameterized values
            "exchange_id, symbol_version_id, interval_code, event_type, "
            "severity, details, detection_policy_version, resolution, "
            "ingestion_id, snapshot_id, reviewer_user_id, detected_at, "
            "affected_candle_id, affected_range_start, affected_range_end, "
            "replacement_candle_id, invalidated_candle_id, supersedes_event_id"
            f") values {','.join(values)} "
            "on conflict (supersedes_event_id, event_type) "
            "where supersedes_event_id is not null do nothing"
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
        never rewritten. This inserts a terminal event scoped to the repaired
        range/candle, and effective state is derived from the event chain
        rather than by mutating the original evidence. The requested
        (blocker event_type -> resolution) transition must be in the explicit
        transition map; unknown or non-resolvable combinations fail closed.
        """
        if not event_types:
            return
        for event_type in event_types:
            allowed = _TERMINAL_TRANSITIONS.get(event_type)
            if allowed is None or resolution not in allowed:
                raise ValueError(
                    f"invalid terminal transition: {event_type!r} -> {resolution!r}"
                )
        if resolution not in _TERMINAL_EVENT_TYPES:
            raise ValueError(f"unknown terminal event type {resolution!r}")
        matched = (
            self._session.execute(
                text(
                    """
                    select blocker.id, blocker.affected_candle_id,
                           blocker.affected_range_start, blocker.affected_range_end
                    from public.data_quality_events blocker
                    where blocker.symbol_version_id = :symbol_version_id
                      and blocker.interval_code = :interval_code
                      and blocker.event_type = any(:event_types)
                      and blocker.resolution is null
                      and (
                          (cast(:range_start as timestamptz) is null
                           and cast(:range_end as timestamptz) is null
                           and cast(:candle_id as uuid) is null)
                          or (
                              cast(:range_start as timestamptz) is not null
                              and blocker.affected_range_start is not null
                              and blocker.affected_range_end is not null
                              and blocker.affected_range_start
                                  >= cast(:range_start as timestamptz)
                              and blocker.affected_range_end
                                  <= cast(:range_end as timestamptz)
                          )
                          or (
                              cast(:candle_id as uuid) is not null
                              and blocker.affected_candle_id
                                  = cast(:candle_id as uuid)
                          )
                      )
                      -- Idempotent terminal resolution: only emit a terminal
                      -- event when this exact blocker has not already been
                      -- superseded by the same terminal type (structured
                      -- parent identity).
                      and not exists (
                          select 1
                          from public.data_quality_events terminal
                          where terminal.symbol_version_id
                                    = blocker.symbol_version_id
                            and terminal.interval_code = blocker.interval_code
                            and terminal.event_type = :resolution
                            and terminal.supersedes_event_id = blocker.id
                      )
                    """
                ),
                {
                    "symbol_version_id": self._symbol_version_id,
                    "interval_code": self._interval.value,
                    "event_types": list(event_types),
                    "resolution": resolution,
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
                        supersedes_event_id=event["id"],
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
                    :snapshot_schema_version, :creator_cycle_id, :creator_job_id
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
                "snapshot_schema_version": self._snapshot_schema_version,
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
            "insert into public.market_snapshot_candles "  # nosec B608: parameterized values
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
        ingestion_id: UUID | None = None,
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
            "quality_policy_version": self._policy.policy_version,
            "freshness_policy_version": self._policy.policy_version,
            "snapshot_schema_version": self._snapshot_schema_version,
            "ingestion_id": str(ingestion_id) if ingestion_id else None,
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
