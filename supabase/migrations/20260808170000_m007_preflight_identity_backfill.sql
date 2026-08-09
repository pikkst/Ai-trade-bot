-- M007 preflight-failure attempt identity and JSON terminal backfill
-- (ninth/tenth-pass review).
-- Additive migration:
--  - allow the dedicated 'preflight_failure' ingestion type so a failed
--    incremental preflight records its own attempt identity and can never
--    collide with, or rewrite, a canonical completed ingestion row;
--  - backfill data_quality_events.supersedes_event_id from the prior
--    append-only implementation's details JSON field so pre-081600 terminal
--    evidence is recognized by the snapshot gate and the resolver stays
--    idempotent, WITHOUT deleting any historical evidence;
--  - enforce valid terminal transitions at the database boundary with an
--    explicit fail-closed trigger.

alter table public.market_data_ingestions
    drop constraint if exists market_data_ingestions_ingestion_type_check;

alter table public.market_data_ingestions
    add constraint market_data_ingestions_ingestion_type_check
    check (ingestion_type in ('backfill', 'incremental', 'gap_repair', 'preflight_failure'));

-- Backfill the structured parent identity from the prior JSON field. Every
-- legacy terminal row is preserved as immutable audit/replay evidence: only
-- the canonical (earliest) terminal per (superseded blocker, terminal type)
-- receives the structured supersedes_event_id. Later duplicates keep
-- supersedes_event_id NULL, so the partial unique index
-- (supersedes_event_id, event_type) WHERE supersedes_event_id IS NOT NULL is
-- not violated and the full pre-migration history remains readable.
update public.data_quality_events terminal
set supersedes_event_id = (terminal.details ->> 'supersedes_event_id')::uuid
where terminal.supersedes_event_id is null
  and terminal.details ? 'supersedes_event_id'
  and (terminal.details ->> 'supersedes_event_id') ~ '^[0-9a-fA-F-]{36}$'
  and terminal.id = (
      select earlier.id
      from public.data_quality_events earlier
      where earlier.symbol_version_id = terminal.symbol_version_id
        and earlier.interval_code = terminal.interval_code
        and earlier.event_type = terminal.event_type
        and earlier.supersedes_event_id is null
        and earlier.details ? 'supersedes_event_id'
        and (earlier.details ->> 'supersedes_event_id')::uuid
              = (terminal.details ->> 'supersedes_event_id')::uuid
      order by earlier.created_at, earlier.id
      limit 1
  );

-- Enforce valid terminal transitions at the database boundary: a terminal
-- child (supersedes_event_id not null) must reference a blocker whose
-- event_type legally maps to the child's event_type. Unknown parent types
-- coalesce to false so non-resolvable blockers fail closed (insert/update
-- rejected), never silently accepted.
create or replace function private.m007_terminal_transition_valid(
    parent_id uuid,
    child_event_type text
)
returns boolean
language sql
stable
as $$
    select coalesce(
        case blocker.event_type
            when 'gap_detected' then 'gap_repaired'
            when 'gap_unresolved' then 'gap_repaired'
            when 'correction_pending' then 'correction_applied'
            when 'clock_drift_exceeded' then 'clock_drift_recovered'
            when 'invalid_value' then 'correction_applied'
            when 'invalid_interval' then 'correction_applied'
            else null
        end = child_event_type,
        false
    )
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
