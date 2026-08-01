-- M003 local Supabase, Auth mapping, and RLS foundation.
-- This migration is additive and safe to apply to an empty local Supabase database.

create extension if not exists pgcrypto with schema extensions;

create schema if not exists private;
revoke all on schema private from public, anon, authenticated;

do $$
begin
    if not exists (select 1 from pg_roles where rolname = 'app_workflow') then
        create role app_workflow nologin noinherit;
    end if;
    if not exists (select 1 from pg_roles where rolname = 'app_migration') then
        create role app_migration nologin noinherit bypassrls;
    end if;
end
$$;

create table if not exists public.users (
    id uuid primary key default extensions.gen_random_uuid(),
    auth_subject uuid not null unique references auth.users(id) on delete cascade,
    email text not null,
    display_name text not null,
    account_state text not null default 'active' check (account_state in ('active', 'disabled', 'locked')),
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.workspaces (
    id uuid primary key default extensions.gen_random_uuid(),
    name text not null,
    base_currency text not null default 'EUR' check (base_currency ~ '^[A-Z]{3,10}$'),
    lifecycle_state text not null default 'active' check (lifecycle_state in ('active', 'suspended', 'archived')),
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),
    version bigint not null default 1 check (version > 0)
);

create table if not exists public.workspace_memberships (
    id uuid primary key default extensions.gen_random_uuid(),
    workspace_id uuid not null references public.workspaces(id) on delete cascade,
    user_id uuid not null references public.users(id) on delete cascade,
    role text not null check (role in ('owner', 'operator', 'viewer')),
    state text not null default 'active' check (state in ('invited', 'active', 'revoked', 'expired')),
    granted_by uuid references public.users(id),
    grant_reason text,
    accepted_at timestamptz,
    revoked_at timestamptz,
    expires_at timestamptz,
    permission_version bigint not null default 1 check (permission_version > 0),
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),
    unique (workspace_id, user_id)
);

create table if not exists public.workspace_config_versions (
    id uuid primary key default extensions.gen_random_uuid(),
    workspace_id uuid not null references public.workspaces(id) on delete cascade,
    version bigint not null check (version > 0),
    configuration jsonb not null,
    configuration_hash text not null check (length(configuration_hash) = 64),
    lifecycle_state text not null default 'draft' check (lifecycle_state in ('draft', 'active', 'archived')),
    created_by uuid references public.users(id),
    created_at timestamptz not null default timezone('utc', now()),
    activated_at timestamptz,
    archived_at timestamptz,
    unique (workspace_id, version),
    unique (workspace_id, configuration_hash)
);

create table if not exists public.audit_events (
    id uuid primary key default extensions.gen_random_uuid(),
    workspace_id uuid references public.workspaces(id) on delete restrict,
    actor_user_id uuid references public.users(id) on delete set null,
    actor_kind text not null check (actor_kind in ('user', 'workflow', 'service', 'migration', 'system')),
    action text not null,
    resource_type text not null,
    resource_id uuid,
    reason text,
    safe_metadata jsonb not null default '{}'::jsonb,
    occurred_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.exchanges (
    id uuid primary key default extensions.gen_random_uuid(),
    code text not null unique,
    display_name text not null,
    data_capability text not null default 'public_market_data',
    active boolean not null default true,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.exchange_symbol_versions (
    id uuid primary key default extensions.gen_random_uuid(),
    exchange_id uuid not null references public.exchanges(id) on delete restrict,
    native_symbol text not null,
    base_asset text not null,
    quote_asset text not null,
    status text not null default 'trading',
    price_precision integer not null check (price_precision between 0 and 18),
    quantity_precision integer not null check (quantity_precision between 0 and 18),
    tick_size numeric(38, 18) not null check (tick_size > 0),
    step_size numeric(38, 18) not null check (step_size > 0),
    min_quantity numeric(38, 18) not null check (min_quantity >= 0),
    min_notional numeric(38, 18) not null check (min_notional >= 0),
    metadata_hash text not null check (length(metadata_hash) = 64),
    effective_at timestamptz not null,
    created_at timestamptz not null default timezone('utc', now()),
    unique (exchange_id, native_symbol, effective_at)
);

create table if not exists public.candles (
    id uuid primary key default extensions.gen_random_uuid(),
    symbol_version_id uuid not null references public.exchange_symbol_versions(id) on delete restrict,
    interval_code text not null,
    open_time timestamptz not null,
    close_time timestamptz not null,
    open_price numeric(38, 18) not null check (open_price > 0),
    high_price numeric(38, 18) not null check (high_price > 0),
    low_price numeric(38, 18) not null check (low_price > 0),
    close_price numeric(38, 18) not null check (close_price > 0),
    base_volume numeric(38, 18) not null check (base_volume >= 0),
    quote_volume numeric(38, 18) not null check (quote_volume >= 0),
    trade_count bigint not null check (trade_count >= 0),
    finalized boolean not null default true,
    content_hash text not null check (length(content_hash) = 64),
    created_at timestamptz not null default timezone('utc', now()),
    constraint candles_time_order check (close_time > open_time),
    constraint candles_high_bound check (high_price >= greatest(open_price, close_price, low_price)),
    constraint candles_low_bound check (low_price <= least(open_price, close_price, high_price)),
    unique (symbol_version_id, interval_code, open_time)
);

create table if not exists public.virtual_portfolios (
    id uuid primary key default extensions.gen_random_uuid(),
    workspace_id uuid not null references public.workspaces(id) on delete restrict,
    name text not null,
    base_currency text not null check (base_currency ~ '^[A-Z]{3,10}$'),
    cash_balance numeric(38, 18) not null check (cash_balance >= 0),
    reserved_cash numeric(38, 18) not null default 0 check (reserved_cash >= 0),
    lifecycle_state text not null default 'active' check (lifecycle_state in ('active', 'frozen', 'archived')),
    version bigint not null default 1 check (version > 0),
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),
    unique (workspace_id, name),
    constraint virtual_portfolio_reserve_bound check (reserved_cash <= cash_balance)
);

create index if not exists workspace_memberships_user_active_idx
    on public.workspace_memberships (user_id, workspace_id)
    where state = 'active';
create index if not exists audit_events_workspace_time_idx
    on public.audit_events (workspace_id, occurred_at desc);
create index if not exists candles_symbol_interval_time_idx
    on public.candles (symbol_version_id, interval_code, open_time desc);

create or replace function private.current_app_user_id()
returns uuid
language sql
stable
security definer
set search_path = public, auth, pg_temp
as $$
    select u.id
    from public.users u
    where u.auth_subject = auth.uid()
      and u.account_state = 'active'
$$;

create or replace function private.has_workspace_role(target_workspace_id uuid, allowed_roles text[])
returns boolean
language sql
stable
security definer
set search_path = public, auth, pg_temp
as $$
    select exists (
        select 1
        from public.workspace_memberships membership
        where membership.workspace_id = target_workspace_id
          and membership.user_id = private.current_app_user_id()
          and membership.state = 'active'
          and membership.role = any (allowed_roles)
          and (membership.expires_at is null or membership.expires_at > timezone('utc', now()))
    )
$$;

revoke all on function private.current_app_user_id() from public, anon, authenticated;
revoke all on function private.has_workspace_role(uuid, text[]) from public, anon, authenticated;
grant execute on function private.current_app_user_id() to authenticated, app_workflow, app_migration;
grant execute on function private.has_workspace_role(uuid, text[]) to authenticated, app_workflow, app_migration;

alter table public.users enable row level security;
alter table public.users force row level security;
alter table public.workspaces enable row level security;
alter table public.workspaces force row level security;
alter table public.workspace_memberships enable row level security;
alter table public.workspace_memberships force row level security;
alter table public.workspace_config_versions enable row level security;
alter table public.workspace_config_versions force row level security;
alter table public.audit_events enable row level security;
alter table public.audit_events force row level security;
alter table public.exchanges enable row level security;
alter table public.exchanges force row level security;
alter table public.exchange_symbol_versions enable row level security;
alter table public.exchange_symbol_versions force row level security;
alter table public.candles enable row level security;
alter table public.candles force row level security;
alter table public.virtual_portfolios enable row level security;
alter table public.virtual_portfolios force row level security;

create policy users_read_self on public.users
    for select to authenticated
    using (id = private.current_app_user_id());

create policy workspaces_read_member on public.workspaces
    for select to authenticated
    using (private.has_workspace_role(id, array['owner', 'operator', 'viewer']));

create policy memberships_read_self_or_owner on public.workspace_memberships
    for select to authenticated
    using (
        user_id = private.current_app_user_id()
        or private.has_workspace_role(workspace_id, array['owner'])
    );

create policy configuration_read_member on public.workspace_config_versions
    for select to authenticated
    using (private.has_workspace_role(workspace_id, array['owner', 'operator', 'viewer']));

create policy audit_read_privileged on public.audit_events
    for select to authenticated
    using (
        workspace_id is not null
        and private.has_workspace_role(workspace_id, array['owner', 'operator'])
    );

create policy exchanges_read_authenticated on public.exchanges
    for select to authenticated using (true);
create policy symbol_versions_read_authenticated on public.exchange_symbol_versions
    for select to authenticated using (true);
create policy candles_read_authenticated on public.candles
    for select to authenticated using (finalized);

create policy portfolios_read_member on public.virtual_portfolios
    for select to authenticated
    using (private.has_workspace_role(workspace_id, array['owner', 'operator', 'viewer']));

create policy workflow_users_all on public.users for all to app_workflow using (true) with check (true);
create policy workflow_workspaces_all on public.workspaces for all to app_workflow using (true) with check (true);
create policy workflow_memberships_all on public.workspace_memberships for all to app_workflow using (true) with check (true);
create policy workflow_config_all on public.workspace_config_versions for all to app_workflow using (true) with check (true);
create policy workflow_audit_insert on public.audit_events for insert to app_workflow with check (true);
create policy workflow_exchanges_all on public.exchanges for all to app_workflow using (true) with check (true);
create policy workflow_symbols_all on public.exchange_symbol_versions for all to app_workflow using (true) with check (true);
create policy workflow_candles_all on public.candles for all to app_workflow using (true) with check (true);
create policy workflow_portfolios_all on public.virtual_portfolios for all to app_workflow using (true) with check (true);

revoke all on all tables in schema public from anon, authenticated;
grant usage on schema public to authenticated;

create or replace view public.workspace_overview
with (security_invoker = true)
as
select id, name, base_currency, lifecycle_state, created_at, updated_at, version
from public.workspaces;

create or replace view public.current_workspace_memberships
with (security_invoker = true)
as
select membership.id,
       membership.workspace_id,
       membership.user_id,
       membership.role,
       membership.state,
       membership.accepted_at,
       membership.expires_at,
       membership.permission_version
from public.workspace_memberships membership;

create or replace view public.market_candle_read
with (security_invoker = true)
as
select candle.id,
       exchange.code as exchange_code,
       symbol.native_symbol,
       symbol.base_asset,
       symbol.quote_asset,
       candle.interval_code,
       candle.open_time,
       candle.close_time,
       candle.open_price,
       candle.high_price,
       candle.low_price,
       candle.close_price,
       candle.base_volume,
       candle.quote_volume,
       candle.trade_count
from public.candles candle
join public.exchange_symbol_versions symbol on symbol.id = candle.symbol_version_id
join public.exchanges exchange on exchange.id = symbol.exchange_id
where candle.finalized;

create or replace view public.portfolio_summary
with (security_invoker = true)
as
select id, workspace_id, name, base_currency, cash_balance, reserved_cash,
       lifecycle_state, version, updated_at
from public.virtual_portfolios;

grant select on public.workspace_overview to authenticated;
grant select on public.current_workspace_memberships to authenticated;
grant select on public.market_candle_read to authenticated;
grant select on public.portfolio_summary to authenticated;

revoke insert, update, delete, truncate, references, trigger
    on all tables in schema public from anon, authenticated;

grant usage on schema public to app_workflow, app_migration;
grant select, insert, update on public.users,
    public.workspaces,
    public.workspace_memberships,
    public.workspace_config_versions,
    public.exchanges,
    public.exchange_symbol_versions,
    public.candles,
    public.virtual_portfolios to app_workflow;
grant insert, select on public.audit_events to app_workflow;
grant all privileges on all tables in schema public to app_migration;
grant all privileges on all sequences in schema public to app_migration;

comment on schema private is 'Non-Data-API helper functions for M003 authorization.';
comment on table public.audit_events is 'Append-only safe audit evidence. Browser roles have no write grants.';
comment on table public.virtual_portfolios is 'Paper-only portfolio state. Browser roles have no write grants.';
