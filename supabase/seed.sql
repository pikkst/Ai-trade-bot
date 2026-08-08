-- Deterministic local-only seed for M003.
-- Password for all local identities: local-password-only
-- These UUIDs are stable so tests and documentation can reference them.

begin;

insert into auth.users (
    instance_id,
    id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    raw_app_meta_data,
    raw_user_meta_data,
    created_at,
    updated_at,
    confirmation_token,
    recovery_token,
    email_change_token_new,
    email_change
)
values
    (
        '00000000-0000-0000-0000-000000000000',
        '00000000-0000-0000-0000-000000000101',
        'authenticated',
        'authenticated',
        'owner@local.test',
        extensions.crypt('local-password-only', extensions.gen_salt('bf')),
        '2026-01-01T00:00:00Z',
        '{"provider":"email","providers":["email"]}'::jsonb,
        '{"display_name":"Local Owner"}'::jsonb,
        '2026-01-01T00:00:00Z',
        '2026-01-01T00:00:00Z',
        '', '', '', ''
    ),
    (
        '00000000-0000-0000-0000-000000000000',
        '00000000-0000-0000-0000-000000000102',
        'authenticated',
        'authenticated',
        'operator@local.test',
        extensions.crypt('local-password-only', extensions.gen_salt('bf')),
        '2026-01-01T00:00:00Z',
        '{"provider":"email","providers":["email"]}'::jsonb,
        '{"display_name":"Local Operator"}'::jsonb,
        '2026-01-01T00:00:00Z',
        '2026-01-01T00:00:00Z',
        '', '', '', ''
    ),
    (
        '00000000-0000-0000-0000-000000000000',
        '00000000-0000-0000-0000-000000000103',
        'authenticated',
        'authenticated',
        'viewer@local.test',
        extensions.crypt('local-password-only', extensions.gen_salt('bf')),
        '2026-01-01T00:00:00Z',
        '{"provider":"email","providers":["email"]}'::jsonb,
        '{"display_name":"Local Viewer"}'::jsonb,
        '2026-01-01T00:00:00Z',
        '2026-01-01T00:00:00Z',
        '', '', '', ''
    )
on conflict (id) do update
set email = excluded.email,
    encrypted_password = excluded.encrypted_password,
    email_confirmed_at = excluded.email_confirmed_at,
    raw_app_meta_data = excluded.raw_app_meta_data,
    raw_user_meta_data = excluded.raw_user_meta_data,
    updated_at = excluded.updated_at;

-- Supabase Auth requires provider_id for email identities. Keep the stable
-- UUID identity key while using the deterministic email as provider_id.
insert into auth.identities (
    id,
    user_id,
    provider_id,
    identity_data,
    provider,
    last_sign_in_at,
    created_at,
    updated_at
)
select
    user_row.id,
    user_row.id,
    user_row.email,
    jsonb_build_object(
        'sub', user_row.id::text,
        'email', user_row.email,
        'email_verified', true,
        'phone_verified', false
    ),
    'email',
    '2026-01-01T00:00:00Z',
    '2026-01-01T00:00:00Z',
    '2026-01-01T00:00:00Z'
from auth.users user_row
where user_row.id in (
    '00000000-0000-0000-0000-000000000101',
    '00000000-0000-0000-0000-000000000102',
    '00000000-0000-0000-0000-000000000103'
)
on conflict (id) do update
set user_id = excluded.user_id,
    provider_id = excluded.provider_id,
    identity_data = excluded.identity_data,
    provider = excluded.provider,
    updated_at = excluded.updated_at;

insert into public.users (id, auth_subject, email, display_name, account_state, created_at, updated_at)
values
    ('10000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000101', 'owner@local.test', 'Local Owner', 'active', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z'),
    ('10000000-0000-0000-0000-000000000102', '00000000-0000-0000-0000-000000000102', 'operator@local.test', 'Local Operator', 'active', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z'),
    ('10000000-0000-0000-0000-000000000103', '00000000-0000-0000-0000-000000000103', 'viewer@local.test', 'Local Viewer', 'active', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
on conflict (id) do update
set email = excluded.email,
    display_name = excluded.display_name,
    account_state = excluded.account_state,
    updated_at = excluded.updated_at;

insert into public.workspaces (id, name, base_currency, lifecycle_state, created_at, updated_at, version)
values (
    '20000000-0000-0000-0000-000000000001',
    'Local Research Workspace',
    'EUR',
    'active',
    '2026-01-01T00:00:00Z',
    '2026-01-01T00:00:00Z',
    1
)
on conflict (id) do update
set name = excluded.name,
    base_currency = excluded.base_currency,
    lifecycle_state = excluded.lifecycle_state,
    updated_at = excluded.updated_at,
    version = excluded.version;

insert into public.workspace_memberships (
    id, workspace_id, user_id, role, state, granted_by, grant_reason,
    accepted_at, permission_version, created_at, updated_at
)
values
    ('21000000-0000-0000-0000-000000000101', '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000101', 'owner', 'active', '10000000-0000-0000-0000-000000000101', 'deterministic local seed', '2026-01-01T00:00:00Z', 1, '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z'),
    ('21000000-0000-0000-0000-000000000102', '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000102', 'operator', 'active', '10000000-0000-0000-0000-000000000101', 'deterministic local seed', '2026-01-01T00:00:00Z', 1, '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z'),
    ('21000000-0000-0000-0000-000000000103', '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000103', 'viewer', 'active', '10000000-0000-0000-0000-000000000101', 'deterministic local seed', '2026-01-01T00:00:00Z', 1, '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
on conflict (workspace_id, user_id) do update
set role = excluded.role,
    state = excluded.state,
    granted_by = excluded.granted_by,
    grant_reason = excluded.grant_reason,
    accepted_at = excluded.accepted_at,
    permission_version = excluded.permission_version,
    updated_at = excluded.updated_at;

insert into public.workspace_config_versions (
    id, workspace_id, version, configuration, configuration_hash,
    lifecycle_state, created_by, created_at, activated_at
)
values (
    '30000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    1,
    '{"environment":"local","provider":"fake","market":"BTCEUR","interval":"1h","live_trading_enabled":false}'::jsonb,
    encode(extensions.digest('{"environment":"local","provider":"fake","market":"BTCEUR","interval":"1h","live_trading_enabled":false}', 'sha256'), 'hex'),
    'active',
    '10000000-0000-0000-0000-000000000101',
    '2026-01-01T00:00:00Z',
    '2026-01-01T00:00:00Z'
)
on conflict (workspace_id, version) do update
set configuration = excluded.configuration,
    configuration_hash = excluded.configuration_hash,
    lifecycle_state = excluded.lifecycle_state,
    activated_at = excluded.activated_at;

insert into public.exchanges (id, code, display_name, data_capability, active, created_at)
values ('40000000-0000-0000-0000-000000000001', 'BINANCE', 'Binance Spot', 'public_market_data', true, '2026-01-01T00:00:00Z')
on conflict (code) do update
set display_name = excluded.display_name,
    data_capability = excluded.data_capability,
    active = excluded.active;

insert into public.exchange_symbol_versions (
    id, exchange_id, native_symbol, base_asset, quote_asset, status,
    price_precision, quantity_precision, tick_size, step_size,
    min_quantity, min_notional, metadata_hash, effective_at, created_at
)
values (
    '41000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000001',
    'BTCEUR', 'BTC', 'EUR', 'trading',
    2, 6, 0.01, 0.000001, 0.000001, 5,
    encode(extensions.digest('BINANCE:BTCEUR:v1', 'sha256'), 'hex'),
    '2026-01-01T00:00:00Z',
    '2026-01-01T00:00:00Z'
)
on conflict (exchange_id, native_symbol, effective_at) do update
set status = excluded.status,
    price_precision = excluded.price_precision,
    quantity_precision = excluded.quantity_precision,
    tick_size = excluded.tick_size,
    step_size = excluded.step_size,
    min_quantity = excluded.min_quantity,
    min_notional = excluded.min_notional,
    metadata_hash = excluded.metadata_hash;

insert into public.candles (
    id, symbol_version_id, interval_code, open_time, close_time,
    open_price, high_price, low_price, close_price,
    base_volume, quote_volume, trade_count, finalized, content_hash, created_at
)
values
    ('42000000-0000-0000-0000-000000000001', '41000000-0000-0000-0000-000000000001', '1h', '2026-01-01T00:00:00Z', '2026-01-01T00:59:59Z', 90000, 90500, 89500, 90250, 12.5, 1128125, 1000, true, encode(extensions.digest('BTCEUR:2026-01-01T00:00:00Z', 'sha256'), 'hex'), '2026-01-01T01:00:00Z'),
    ('42000000-0000-0000-0000-000000000002', '41000000-0000-0000-0000-000000000001', '1h', '2026-01-01T01:00:00Z', '2026-01-01T01:59:59Z', 90250, 91000, 90100, 90800, 14.0, 1271200, 1200, true, encode(extensions.digest('BTCEUR:2026-01-01T01:00:00Z', 'sha256'), 'hex'), '2026-01-01T02:00:00Z')
on conflict (symbol_version_id, interval_code, open_time) where superseded_by is null do update
set close_time = excluded.close_time,
    open_price = excluded.open_price,
    high_price = excluded.high_price,
    low_price = excluded.low_price,
    close_price = excluded.close_price,
    base_volume = excluded.base_volume,
    quote_volume = excluded.quote_volume,
    trade_count = excluded.trade_count,
    finalized = excluded.finalized,
    content_hash = excluded.content_hash;

insert into public.virtual_portfolios (
    id, workspace_id, name, base_currency, cash_balance, reserved_cash,
    lifecycle_state, version, created_at, updated_at
)
values (
    '50000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    'Local Paper Portfolio',
    'EUR',
    10000,
    0,
    'active',
    1,
    '2026-01-01T00:00:00Z',
    '2026-01-01T00:00:00Z'
)
on conflict (workspace_id, name) do update
set base_currency = excluded.base_currency,
    cash_balance = excluded.cash_balance,
    reserved_cash = excluded.reserved_cash,
    lifecycle_state = excluded.lifecycle_state,
    version = excluded.version,
    updated_at = excluded.updated_at;

insert into public.audit_events (
    id, workspace_id, actor_user_id, actor_kind, action,
    resource_type, resource_id, reason, safe_metadata, occurred_at
)
values (
    '60000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    null,
    'migration',
    'local_seed_applied',
    'workspace',
    '20000000-0000-0000-0000-000000000001',
    'deterministic M003 local seed',
    '{"cloud_credentials_required":false}'::jsonb,
    '2026-01-01T00:00:00Z'
)
on conflict (id) do nothing;

commit;
