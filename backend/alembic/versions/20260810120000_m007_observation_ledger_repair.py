"""M007 observation-ledger repair and provenance hardening.

Revision ID: 20260810120000
Revises: 20260809220000
Create Date: 2026-08-10 12:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260810120000"
down_revision: str | None = "20260809220000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the observation-ledger repair schema applied."""
    bind = op.get_bind()
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
    has_trigger = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_trigger
            where tgrelid = 'public.symbol_metadata_observations'::regclass
              and tgname = 'symbol_metadata_observations_version_identity_trg'
            """
        )
    ).scalar_one()
    if not has_source_state:
        raise RuntimeError(
            "exchange_symbol_versions.source_evidence_state is missing; "
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
    if not has_trigger:
        raise RuntimeError(
            "symbol_metadata_observations_version_identity_trg is missing; "
            "run the Supabase migration first"
        )


def downgrade() -> None:
    """Prevent destructive rollback of observation-ledger repair."""
    raise RuntimeError(
        "M007 observation-ledger repair is additive-only; "
        "create a forward migration instead"
    )
