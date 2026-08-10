"""M007 observation-ledger canonicalization and provenance hardening.

Revision ID: 20260810200000
Revises: 20260810120000
Create Date: 2026-08-10 20:00:00 UTC
"""

from __future__ import annotations

from sqlalchemy import text

from alembic import op

revision = "20260810200000"
down_revision: str | None = "20260810120000"
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    """Verify the observation-ledger canonicalization schema applied."""
    bind = op.get_bind()
    has_request_key_func = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_proc
            where proname = 'compute_metadata_request_key'
              and pronamespace = 'public'::regnamespace
            """
        )
    ).scalar_one()
    has_request_key_unique = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_constraint
            where conrelid = 'public.symbol_metadata_observations'::regclass
              and conname = 'symbol_metadata_observations_request_key_key'
              and contype = 'u'
            """
        )
    ).scalar_one()
    has_request_key_not_null = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_attribute
            where attrelid = 'public.symbol_metadata_observations'::regclass
              and attname = 'request_key'
              and attnotnull
              and not attisdropped
            """
        )
    ).scalar_one()
    has_disposition_check = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_constraint
            where conrelid = 'public.symbol_metadata_observations'::regclass
              and conname = 'symbol_metadata_observations_disposition_check'
              and contype = 'c'
              and pg_get_constraintdef(oid) like '%equal_timestamp_conflict%'
            """
        )
    ).scalar_one()
    has_verified_has_version_check = bind.execute(
        text(
            """
            select count(*) > 0
            from pg_constraint
            where conrelid = 'public.symbol_metadata_observations'::regclass
              and conname = 'symbol_metadata_observations_verified_has_version_check'
              and contype = 'c'
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
    if not has_request_key_func:
        raise RuntimeError(
            "public.compute_metadata_request_key function is missing; "
            "run the Supabase migration first"
        )
    if not has_request_key_unique:
        raise RuntimeError(
            "symbol_metadata_observations.request_key UNIQUE constraint is missing; "
            "run the Supabase migration first"
        )
    if not has_request_key_not_null:
        raise RuntimeError(
            "symbol_metadata_observations.request_key NOT NULL constraint is missing; "
            "run the Supabase migration first"
        )
    if not has_disposition_check:
        raise RuntimeError(
            "symbol_metadata_observations.disposition CHECK is missing "
            "or still two-value; run the Supabase migration first"
        )
    if not has_verified_has_version_check:
        raise RuntimeError(
            "symbol_metadata_observations.verified_has_version CHECK is missing; "
            "run the Supabase migration first"
        )
    if not has_trigger:
        raise RuntimeError(
            "symbol_metadata_observations_version_identity_trg is missing; "
            "run the Supabase migration first"
        )


def downgrade() -> None:
    """Prevent destructive rollback of observation-ledger canonicalization."""
    raise RuntimeError(
        "M007 observation-ledger canonicalization is additive-only; "
        "create a forward migration instead"
    )
