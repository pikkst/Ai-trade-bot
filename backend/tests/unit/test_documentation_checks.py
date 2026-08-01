from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_checker() -> ModuleType:
    checker_path = (
        Path(__file__).parents[3] / "infrastructure" / "scripts" / "check_docs.py"
    )
    spec = importlib.util.spec_from_file_location("check_docs", checker_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_broken_markdown_link_is_rejected(tmp_path: Path) -> None:
    checker = load_checker()
    markdown = tmp_path / "README.md"
    markdown.write_text("[missing](docs/missing.md)\n", encoding="utf-8")

    failures = checker.broken_local_links(tmp_path, [markdown])

    assert failures == ["README.md: missing local link target 'docs/missing.md'"]


def test_malformed_detailed_task_is_rejected() -> None:
    checker = load_checker()
    card = "## [ ] L2.5 — Documentation CI\n\n**Priority:** P0\n"

    failures = checker.malformed_task_cards(card, "TASKS.md")

    assert (
        "TASKS.md: ## [ ] L2.5 — Documentation CI is missing ### References" in failures
    )
