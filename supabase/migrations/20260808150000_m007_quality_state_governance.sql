-- M007 quality-state governance (seventh-pass review).
-- Additive migration:
--  - add clock_drift_recovered to the canonical event_type vocabulary;
--  - scope authenticated read policies to workspace membership so the
--    security-invoker views never disclose cross-workspace rows;
--  - revoke the now-unneeded app_workflow UPDATE on data_quality_events
--    because resolution is append-only (terminal events are inserted, the
--    original evidence is never rewritten).

alter table public.data_quality_events
    drop constraint if exists data_quality_events_event_type_check;

alter table public.data_quality_events
    add constraint data_quality_events_event_type_check
    check (event_type in (
        'approved',
        'incomplete',
        'stale',
        'duplicate_consistent',
        'duplicate_conflict',
        'invalid_value',
        'invalid_interval',
        'out_of_order',
        'gap_detected',
        'gap_repair_pending',
        'gap_repaired',
        'gap_unresolved',
        'provider_unavailable',
        'rate_limited',
        'clock_drift_exceeded',
        'clock_drift_recovered',
        'correction_pending',
        'correction_applied',
        'quarantined',
        'invalidated'
    ));

revoke update on public.data_quality_events from app_workflow;

drop policy if exists authenticated_ingestions_select on public.market_data_ingestions;
drop policy if exists authenticated_quality_select on public.data_quality_events;
drop policy if exists authenticated_corrections_select on public.candle_corrections;
drop policy if exists authenticated_snapshots_select on public.market_snapshots;
drop policy if exists authenticated_snapshot_candles_select on public.market_snapshot_candles;

-- market_snapshots is workspace-owned: only members may read a workspace's
-- snapshots (and thereby the security-invoker snapshot view rows).
create policy authenticated_snapshots_select on public.market_snapshots
    for select to authenticated
    using (private.has_workspace_role(workspace_id, array['owner', 'operator', 'viewer']));

-- market_snapshot_candles inherit workspace scope through their parent
-- snapshot, so a user in workspace A cannot read workspace B membership rows.
create policy authenticated_snapshot_candles_select on public.market_snapshot_candles
    for select to authenticated
    using (
        exists (
            select 1
            from public.market_snapshots snapshot
            where snapshot.id = market_snapshot_candles.snapshot_id
              and private.has_workspace_role(
                  snapshot.workspace_id,
                  array['owner', 'operator', 'viewer']
              )
        )
    );

-- Exchange reference data is shared; symbol versions are public reference
-- rows like the M003 exchanges/symbol_versions reads.
create policy authenticated_quality_select on public.data_quality_events
    for select to authenticated
    using (
        exists (
            select 1
            from public.exchange_symbol_versions symbol
            where symbol.id = data_quality_events.symbol_version_id
        )
    );

create policy authenticated_corrections_select on public.candle_corrections
    for select to authenticated
    using (
        exists (
            select 1
            from public.exchange_symbol_versions symbol
            where symbol.id = candle_corrections.symbol_version_id
        )
    );
