-- M008 immutable snapshots and deterministic feature engineering.
-- Additive migration for feature set versions, feature calculations, and feature values.

create table if not exists public.feature_set_versions (
    id uuid primary key default extensions.gen_random_uuid(),
    workspace_id uuid not null references public.workspaces(id) on delete restrict,
    name text not null,
    semantic_version text not null,
    implementation_reference text not null,
    configuration jsonb not null default '{}'::jsonb,
    configuration_hash text not null check (length(configuration_hash) = 64),
    required_history integer not null check (required_history >= 0),
    warm_up_policy text not null default 'insufficient_history_null' check (warm_up_policy in ('insufficient_history_null', 'partial_warm_up')),
    status text not null default 'draft' check (status in ('draft', 'active', 'archived')),
    created_by uuid references public.users(id) on delete set null,
    created_at timestamptz not null default timezone('utc', now()),
    activated_at timestamptz,
    archived_at timestamptz,
    unique (workspace_id, semantic_version),
    unique (workspace_id, configuration_hash)
);

create table if not exists public.feature_calculations (
    id uuid primary key default extensions.gen_random_uuid(),
    workspace_id uuid not null references public.workspaces(id) on delete restrict,
    snapshot_id uuid not null references public.market_snapshots(id) on delete restrict,
    feature_set_version_id uuid not null references public.feature_set_versions(id) on delete restrict,
    idempotency_key text not null check (length(idempotency_key) between 1 and 200),
    status text not null default 'completed' check (status in ('completed', 'insufficient_history', 'invalid_source', 'division_by_zero', 'calculation_error', 'cancelled')),
    input_hash text not null check (length(input_hash) = 64),
    output_hash text not null check (length(output_hash) = 64),
    calculation_started_at timestamptz not null default timezone('utc', now()),
    calculation_completed_at timestamptz,
    warnings jsonb not null default '[]'::jsonb,
    error_message text,
    creator_cycle_id text,
    created_at timestamptz not null default timezone('utc', now()),
    unique (snapshot_id, feature_set_version_id, input_hash)
);

create table if not exists public.feature_values (
    id uuid primary key default extensions.gen_random_uuid(),
    calculation_id uuid not null references public.feature_calculations(id) on delete cascade,
    feature_code text not null,
    numeric_value numeric(38, 18),
    string_value text,
    boolean_value boolean,
    unit text not null default '',
    sequence bigint not null,
    timestamp timestamptz not null,
    null_reason text,
    created_at timestamptz not null default timezone('utc', now()),
    unique (calculation_id, feature_code, sequence),
    check (
        (numeric_value is not null and string_value is null and boolean_value is null) or
        (numeric_value is null and string_value is not null and boolean_value is null) or
        (numeric_value is null and string_value is null and boolean_value is not null)
    )
);

create index if not exists feature_set_versions_workspace_idx
    on public.feature_set_versions (workspace_id, semantic_version);
create index if not exists feature_calculations_snapshot_idx
    on public.feature_calculations (snapshot_id, feature_set_version_id);
create index if not exists feature_calculations_idempotency_idx
    on public.feature_calculations (idempotency_key);
create index if not exists feature_values_calculation_idx
    on public.feature_values (calculation_id, sequence);
create index if not exists feature_values_code_idx
    on public.feature_values (feature_code, timestamp);

alter table public.feature_set_versions enable row level security;
alter table public.feature_set_versions force row level security;
alter table public.feature_calculations enable row level security;
alter table public.feature_calculations force row level security;
alter table public.feature_values enable row level security;
alter table public.feature_values force row level security;

create policy workflow_feature_set_versions_all on public.feature_set_versions
    for all to app_workflow using (true) with check (true);
create policy workflow_feature_calculations_all on public.feature_calculations
    for all to app_workflow using (true) with check (true);
create policy workflow_feature_values_all on public.feature_values
    for all to app_workflow using (true) with check (true);

revoke all on public.feature_set_versions from public, anon, authenticated;
revoke all on public.feature_calculations from public, anon, authenticated;
revoke all on public.feature_values from public, anon, authenticated;

grant usage on schema public to app_workflow, app_migration;
grant select, insert, update on public.feature_set_versions to app_workflow;
grant select, insert on public.feature_calculations to app_workflow;
grant select, insert on public.feature_values to app_workflow;
grant all privileges on all tables in schema public to app_migration;
grant all privileges on all sequences in schema public to app_migration;
