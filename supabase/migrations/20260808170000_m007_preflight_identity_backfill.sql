-- M007 preflight-failure attempt identity and JSON terminal backfill
-- (ninth-pass review).
-- Additive migration:
--  - allow the dedicated 'preflight_failure' ingestion type so a failed
--    incremental preflight records its own attempt identity and can never
--    collide with, or rewrite, a canonical completed ingestion row;
--  - backfill data_quality_events.supersedes_event_id from the prior
--    append-only implementation's details JSON field before the unique
--    terminal index takes effect, so pre-081600 terminal evidence is
--    recognized by the snapshot gate and the resolver stays idempotent.

alter table public.market_data_ingestions
    drop constraint if exists market_data_ingestions_ingestion_type_check;

alter table public.market_data_ingestions
    add constraint market_data_ingestions_ingestion_type_check
    check (ingestion_type in ('backfill', 'incremental', 'gap_repair', 'preflight_failure'));

-- Backfill supersedes_event_id from the prior JSON field. The old
-- implementation could emit duplicate terminals for one blocker, so first
-- deduplicate by keeping only the earliest terminal per (superseded blocker,
-- terminal type) before the unique index applies.
delete from public.data_quality_events terminal
using public.data_quality_events earlier
where terminal.supersedes_event_id is null
  and terminal.details ? 'supersedes_event_id'
  and earlier.supersedes_event_id is null
  and earlier.details ? 'supersedes_event_id'
  and (terminal.details ->> 'supersedes_event_id')::uuid
        = (earlier.details ->> 'supersedes_event_id')::uuid
  and terminal.event_type = earlier.event_type
  and terminal.id <> earlier.id
  and (earlier.created_at, earlier.id) < (terminal.created_at, terminal.id);

update public.data_quality_events
set supersedes_event_id = (details ->> 'supersedes_event_id')::uuid
where supersedes_event_id is null
  and details ? 'supersedes_event_id'
  and (details ->> 'supersedes_event_id') ~ '^[0-9a-fA-F-]{36}$';

-- Enforce valid terminal transitions at the database boundary: a terminal
-- child (supersedes_event_id not null) must reference a blocker whose
-- event_type legally maps to the child's event_type. Anything else fails
-- closed (insert/update rejected).
create or replace function private.m007_terminal_transition_valid(
    parent_id uuid,
    child_event_type text
)
returns boolean
language sql
stable
as $$
    select case blocker.event_type
        when 'gap_detected' then 'gap_repaired'
        when 'gap_unresolved' then 'gap_repaired'
        when 'correction_pending' then 'correction_applied'
        when 'clock_drift_exceeded' then 'clock_drift_recovered'
        when 'invalid_value' then 'correction_applied'
        when 'invalid_interval' then 'correction_applied'
        else null
    end = child_event_type
    from public.data_quality_events blocker
    where blocker.id = parent_id
$$;

create or replace function private.m007_terminal_transition_check()
returns trigger
language plpgsql
as $$
begin
    if new.supersedes_event_id is not null
       and not private.m007_terminal_transition_valid(
           new.supersedes_event_id, new.event_type
       ) then
        raise exception
            'invalid terminal transition: parent % cannot resolve as %',
            new.supersedes_event_id, new.event_type;
    end if;
    return new;
end;
$$;

drop trigger if exists data_quality_events_terminal_transition_trigger
    on public.data_quality_events;

create trigger data_quality_events_terminal_transition_trigger
    before insert or update of supersedes_event_id, event_type
    on public.data_quality_events
    for each row
    execute function private.m007_terminal_transition_check();
