"""M007 symbol-metadata freshness evidence and raw observation ledger.

Revision ID: 20260809220000
Revises: 20260809000000
Create Date: 2026-08-09 22:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260809220000"
down_revision: str | None = "20260809000000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the freshness-evidence and observation-ledger schema applied."""
    bind = op.get_bind()
    has_last_verified = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_attribute
            where attrelid = 'public.exchange_symbol_versions'::regclass
              and attname = 'last_verified_at'
              and not attisdropped
            """
        )
    ).scalar_one()
    has_source_state = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_attribute
            where attrelid = 'public.exchange_symbol_versions'::regclass
              and attname = 'source_evidence_state'
              and not attisdropped
            """
        )
    ).scalar_one()
    has_observations = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_tables
            where schemaname = 'public'
              and tablename = 'symbol_metadata_observations'
            """
        )
    ).scalar_one()
    has_request_key = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_attribute
            where attrelid = 'public.symbol_metadata_observations'::regclass
              and attname = 'request_key'
              and not attisdropped
            """
        )
    ).scalar_one()
    has_disposition = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_attribute
            where attrelid = 'public.symbol_metadata_observations'::regclass
              and attname = 'disposition'
              and not attisdropped
            """
        )
    ).scalar_one()
    has_current_idx = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_index
            where indrelid = 'public.exchange_symbol_versions'::regclass
              and indpred is not null
              and pg_get_indexdef(indexrelid) ilike '%superseded_by is null%'
            """
        )
    ).scalar_one()
    if not has_last_verified:
        raise RuntimeError(
            "exchange_symbol_versions.last_verified_at is missing; "
            "run the Supabase migration first"
        )
    if not has_source_state:
        raise RuntimeError(
            "exchange_symbol_versions.source_evidence_state is missing; "
            "run the Supabase migration first"
        )
    if not has_observations:
        raise RuntimeError(
            "public.symbol_metadata_observations is missing; "
            "run the Supabase migration first"
        )
    if not has_request_key:
        raise RuntimeError(
            "symbol_metadata_observations.request_key is missing; "
            "run the Supabase migration first"
        )
    if not has_disposition:
        raise RuntimeError(
            "symbol_metadata_observations.disposition is missing; "
            "run the Supabase migration first"
        )
    if not has_current_idx:
        raise RuntimeError(
            "exchange_symbol_versions_current_idx partial unique index is missing; "
            "run the Supabase migration first"
        )


def downgrade() -> None:
    """Prevent destructive rollback of freshness/observation schema."""
    raise RuntimeError(
        "M007 symbol-metadata freshness evidence is additive-only; "
        "create a forward migration instead"
    )
