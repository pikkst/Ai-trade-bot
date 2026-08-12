-- M008 feature engineering hardening and immutable evidence verification.
-- Additive migration to fix warm-up representation, output_hash boundary,
-- snapshot membership validation, feature-set immutability, and correction lineage.

-- 1. Warm-up rows: allow all typed values NULL when null_reason is present,
--    and require null_reason NULL when any typed value exists.
alter table public.feature_values drop constraint if exists feature_values_check;

alter table public.feature_values
    add constraint feature_values_check check (
        (numeric_value is null and string_value is null and boolean_value is null and null_reason is not null)
        or
        (numeric_value is not null and string_value is null and boolean_value is null and null_reason is null)
        or
        (numeric_value is null and string_value is not null and boolean_value is null and null_reason is null)
        or
        (numeric_value is null and string_value is null and boolean_value is not null and null_reason is null)
    );

-- 2. output_hash: require 64-char canonical hash for every status.
alter table public.feature_calculations drop constraint if exists feature_calculations_output_hash_check;

alter table public.feature_calculations
    add constraint feature_calculations_output_hash_check check (length(output_hash) = 64);

-- 3. Snapshot membership validation function.
--    Ensures every member candle is finalized, unsuperseded, belongs to the
--    snapshot's symbol/interval, is closed by analysis_time, and count matches.
create or replace function public.validate_snapshot_membership(
    p_snapshot_id uuid
)
returns void
language plpgsql
as $$
declare
    v_count int;
    v_expected int;
    v_invalid_count int;
    v_workspace_id uuid;
    v_symbol_version_id uuid;
    v_interval_code text;
    v_analysis_time timestamptz;
begin
    select workspace_id, symbol_version_id, interval_code, analysis_time, candle_count
    into v_workspace_id, v_symbol_version_id, v_interval_code, v_analysis_time, v_expected
    from public.market_snapshots
    where id = p_snapshot_id;

    if v_expected is null then
        raise exception 'snapshot % does not exist', p_snapshot_id;
    end if;

    select count(*) into v_count
    from public.market_snapshot_candles msc
    join public.candles c on c.id = msc.candle_id
    where msc.snapshot_id = p_snapshot_id
      and c.symbol_version_id = v_symbol_version_id
      and c.interval_code = v_interval_code
      and c.finalized = true
      and c.superseded_by is null
      and c.close_time <= v_analysis_time;

    if v_count != v_expected then
        raise exception 'snapshot % membership invalid: expected % candles, found % valid finalized unsuperseded members for symbol/interval',
            p_snapshot_id, v_expected, v_count;
    end if;

    select count(*) into v_invalid_count
    from public.market_snapshot_candles msc
    join public.candles c on c.id = msc.candle_id
    where msc.snapshot_id = p_snapshot_id
      and (c.symbol_version_id != v_symbol_version_id
           or c.interval_code != v_interval_code
           or c.finalized = false
           or c.superseded_by is not null
           or c.close_time > v_analysis_time);

    if v_invalid_count > 0 then
        raise exception 'snapshot % has % invalid member candles (wrong symbol/interval, unfinalized, superseded, or future)',
            p_snapshot_id, v_invalid_count;
    end if;
end;
$$;

-- 4. Feature set version immutability trigger.
--    Active/archived versions cannot be updated except for status transitions
--    from active -> archived.
create or replace function public.enforce_feature_set_version_immutability()
returns trigger
language plpgsql
as $$
begin
    if TG_OP = 'UPDATE' then
        if old.status = 'active' and new.status = 'archived' then
            if old.name != new.name
               or old.semantic_version != new.semantic_version
               or old.implementation_reference != new.implementation_reference
               or old.configuration_hash != new.configuration_hash
               or old.required_history != new.required_history
               or old.warm_up_policy != new.warm_up_policy
               or old.created_by != new.created_by then
                raise exception 'cannot modify fields of active feature_set_version % during archival', old.id;
            end if;
            return new;
        end if;
        if old.status = 'active' or old.status = 'archived' then
            raise exception 'cannot update feature_set_version % with status %', old.id, old.status;
        end if;
        if old.status = 'draft' and new.status != 'draft' then
            raise exception 'draft feature_set_version status transitions must go through activation workflow';
        end if;
    end if;
    return new;
end;
$$;

drop trigger if exists feature_set_version_immutability on public.feature_set_versions;
create trigger feature_set_version_immutability
    before update on public.feature_set_versions
    for each row execute function public.enforce_feature_set_version_immutability();

-- 5. Correction invalidation lineage for feature calculations.
create table if not exists public.feature_calculation_invalidations (
    id uuid primary key default extensions.gen_random_uuid(),
    calculation_id uuid not null references public.feature_calculations(id) on delete restrict,
    invalidated_at timestamptz not null default timezone('utc', now()),
    reason text not null,
    replacement_calculation_id uuid references public.feature_calculations(id) on delete set null,
    created_at timestamptz not null default timezone('utc', now())
);

create index if not exists feature_calculation_invalidations_calc_idx
    on public.feature_calculation_invalidations (calculation_id);

alter table public.feature_calculation_invalidations add constraint feature_calculation_invalidations_calc_unique unique (calculation_id);

alter table public.feature_calculation_invalidations enable row level security;
alter table public.feature_calculation_invalidations force row level security;

create policy workflow_feature_calculation_invalidations_all on public.feature_calculation_invalidations
    for all to app_workflow using (true) with check (true);

-- 6. Read gate: exclude invalidated calculations from normal consumption.
create or replace view public.consumable_feature_calculations as
select fc.*
from public.feature_calculations fc
where not exists (
    select 1
    from public.feature_calculation_invalidations fci
    where fci.calculation_id = fc.id
);

-- 7. Idempotent feature invalidation for snapshot corrections.
create or replace function public.invalidate_feature_calculations_for_snapshot(
    p_snapshot_id uuid,
    p_reason text
)
returns void
language plpgsql
as $$
begin
    insert into public.feature_calculation_invalidations (calculation_id, reason)
    select fc.id, p_reason
    from public.feature_calculations fc
    where fc.snapshot_id = p_snapshot_id
      and fc.status = 'completed'
      and not exists (
          select 1 from public.feature_calculation_invalidations fci
          where fci.calculation_id = fc.id
      );
end;
$$;

revoke all on public.feature_calculation_invalidations from public, anon, authenticated;
grant usage on schema public to app_workflow, app_migration;
grant select, insert on public.feature_calculation_invalidations to app_workflow;
grant select on public.consumable_feature_calculations to app_workflow;
grant all privileges on all tables in schema public to app_migration;
grant all privileges on all sequences in schema public to app_migration;
