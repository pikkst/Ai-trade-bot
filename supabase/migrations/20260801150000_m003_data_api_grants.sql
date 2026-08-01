-- Complete the M003 Data API exposure model.
-- Authenticated browser identities may read only through RLS and cannot write.

begin;

grant usage on schema private to authenticated, app_workflow, app_migration;

grant select on public.users to authenticated;
grant select on public.workspaces to authenticated;
grant select on public.workspace_memberships to authenticated;
grant select on public.workspace_config_versions to authenticated;
grant select on public.audit_events to authenticated;
grant select on public.exchanges to authenticated;
grant select on public.exchange_symbol_versions to authenticated;
grant select on public.candles to authenticated;
grant select on public.virtual_portfolios to authenticated;

revoke insert, update, delete, truncate, references, trigger
    on public.users,
       public.workspaces,
       public.workspace_memberships,
       public.workspace_config_versions,
       public.audit_events,
       public.exchanges,
       public.exchange_symbol_versions,
       public.candles,
       public.virtual_portfolios
    from anon, authenticated;

create or replace view public.current_user_profile
with (security_invoker = true)
as
select id, auth_subject, email, display_name, account_state, created_at, updated_at
from public.users;

create or replace view public.active_workspace_configuration
with (security_invoker = true)
as
select id,
       workspace_id,
       version,
       configuration_hash,
       lifecycle_state,
       created_at,
       activated_at
from public.workspace_config_versions
where lifecycle_state = 'active';

create or replace view public.workspace_audit_read
with (security_invoker = true)
as
select id,
       workspace_id,
       actor_user_id,
       actor_kind,
       action,
       resource_type,
       resource_id,
       reason,
       safe_metadata,
       occurred_at
from public.audit_events;

grant select on public.current_user_profile to authenticated;
grant select on public.active_workspace_configuration to authenticated;
grant select on public.workspace_audit_read to authenticated;

grant all privileges on public.users,
    public.workspaces,
    public.workspace_memberships,
    public.workspace_config_versions,
    public.audit_events,
    public.exchanges,
    public.exchange_symbol_versions,
    public.candles,
    public.virtual_portfolios to service_role;

grant select on public.workspace_overview,
    public.current_workspace_memberships,
    public.current_user_profile,
    public.active_workspace_configuration,
    public.workspace_audit_read,
    public.market_candle_read,
    public.portfolio_summary to service_role, app_workflow, app_migration;

commit;
