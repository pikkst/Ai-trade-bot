"""Integration test configuration for M007 market data service."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.database import build_engine


def _ensure_m007_migration_columns(engine: Engine) -> None:
    """Apply the M007 observation-ledger repair migration if the columns
    are missing.
    """
    with engine.begin() as connection:
        row = connection.execute(
            text(
                """
                select count(*)
                from information_schema.columns
                where table_schema = 'public'
                  and table_name = 'symbol_metadata_observations'
                  and column_name = 'request_key'
                """
            )
        ).scalar_one()
        if row > 0:
            return

        repo_root = Path(__file__).resolve().parents[3]
        migration_path = (
            repo_root
            / "supabase"
            / "migrations"
            / "20260810120000_m007_observation_ledger_repair.sql"
        )
        sql = migration_path.read_text(encoding="utf-8")
        statements: list[str] = []
        current: list[str] = []
        in_dollar = False
        i = 0
        while i < len(sql):
            char = sql[i]
            if char == "$" and not in_dollar and sql[i : i + 2] == "$$":
                in_dollar = True
                current.append("$$")
                i += 2
                continue
            if char == "$" and in_dollar and sql[i : i + 2] == "$$":
                in_dollar = False
                current.append("$$")
                i += 2
                continue
            current.append(char)
            if char == ";" and not in_dollar:
                stmt = "".join(current).strip()
                if stmt:
                    non_comment_lines = [
                        line
                        for line in stmt.splitlines()
                        if not line.strip().startswith("--")
                    ]
                    if non_comment_lines:
                        statements.append(stmt)
                current = []
            i += 1
        if current:
            stmt = "".join(current).strip()
            if stmt:
                non_comment_lines = [
                    line
                    for line in stmt.splitlines()
                    if not line.strip().startswith("--")
                ]
                if non_comment_lines:
                    statements.append(stmt)

        for stmt in statements:
            connection.execute(text(stmt))


@pytest.fixture(scope="session")
def database_engine() -> Iterator[Engine]:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for M007 integration tests")
    engine = build_engine(url)
    yield engine
    engine.dispose()
