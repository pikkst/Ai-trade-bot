-- M007 quality-gate fixes.
-- Additive migration:
--  - align data_quality_events.event_type CHECK with the canonical
--    QualityState domain vocabulary (add provider_unavailable, rate_limited,
--    gap_repaired, gap_unresolved; keep stale);
--  - grant app_workflow UPDATE on data_quality_events so resolution evidence
--    can be recorded (snapshot gates must not be permanently blocked);
--  - grant authenticated SELECT on the security-invoker view base tables so
--    the read views are actually readable, matching the M003 pattern.

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
        'correction_pending',
        'correction_applied',
        'quarantined',
        'invalidated'
    ));

grant update on public.data_quality_events to app_workflow;

-- Security-invoker views evaluate base-table privileges/RLS as the caller, so
-- authenticated needs SELECT on the underlying RLS-protected tables (the same
-- pattern M003 uses for its read views).
grant select on public.market_data_ingestions to authenticated;
grant select on public.data_quality_events to authenticated;
grant select on public.candle_corrections to authenticated;
grant select on public.market_snapshots to authenticated;
grant select on public.market_snapshot_candles to authenticated;

create policy authenticated_ingestions_select on public.market_data_ingestions
    for select to authenticated using (true);
create policy authenticated_quality_select on public.data_quality_events
    for select to authenticated using (true);
create policy authenticated_corrections_select on public.candle_corrections
    for select to authenticated using (true);
create policy authenticated_snapshots_select on public.market_snapshots
    for select to authenticated using (true);
create policy authenticated_snapshot_candles_select on public.market_snapshot_candles
    for select to authenticated using (true);
