"""Alembic environment for the local PostgreSQL/Supabase database."""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.database import DEFAULT_DATABASE_URL

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

configured_url = config.get_main_option("sqlalchemy.url") or DEFAULT_DATABASE_URL
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", configured_url))
target_metadata = None

_CONTEXT_OPTIONS = {
    "target_metadata": target_metadata,
    "version_table": "alembic_version",
    "version_table_schema": "private",
}


def run_migrations_offline() -> None:
    """Generate SQL without opening a database connection."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **_CONTEXT_OPTIONS,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the configured local PostgreSQL database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, **_CONTEXT_OPTIONS)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()