"""Fail closed on broken local Markdown links and malformed detailed task cards."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FENCED_BLOCK = re.compile(r"```.*?```", re.DOTALL)
TASK_HEADING = re.compile(r"^## \[[^\]]+\] (?:C|L|UX)\d+(?:\.\d+)?\b.*$", re.MULTILINE)
REQUIRED_TASK_FIELDS = (
    "**Priority:**",
    "### Description",
    "### User Story",
    "### Acceptance Criteria",
    "### Definition of Done",
    "### Dependencies",
    "### References",
)
DETAILED_TASK_CATALOGS = (
    "CLOUD_MVP_TASKS.md",
    "LOCAL_AND_PRODUCTION_TASKS.md",
    "UX_DESIGN_TASKS.md",
)
README_INVENTORY = (
    "AGENTS.md",
    "TASKS.md",
    "CONTRIBUTING.md",
    "docs/IMPLEMENTATION_EXECUTION_PLAN.md",
    "docs/TASK_CATALOG_INDEX.md",
    "docs/TESTING.md",
    "docs/SECURITY.md",
)


def markdown_files(root: Path) -> list[Path]:
    """Return tracked-source Markdown candidates without generated dependencies."""
    ignored = {".git", ".venv", "node_modules", "dist", "build", ".pytest-tmp"}
    return sorted(
        path
        for path in root.rglob("*.md")
        if not ignored.intersection(path.relative_to(root).parts)
    )


def broken_local_links(root: Path, files: list[Path] | None = None) -> list[str]:
    """Return local Markdown links whose target path does not exist."""
    failures: list[str] = []
    for markdown in files or markdown_files(root):
        content = FENCED_BLOCK.sub("", markdown.read_text(encoding="utf-8"))
        for raw_target in MARKDOWN_LINK.findall(content):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target_path = unquote(target.split("#", maxsplit=1)[0])
            resolved = (
                root / target_path.lstrip("/")
                if target_path.startswith("/")
                else markdown.parent / target_path
            ).resolve()
            if not resolved.exists():
                relative_markdown = markdown.relative_to(root)
                failures.append(
                    f"{relative_markdown}: missing local link target {target!r}"
                )
    return failures


def malformed_task_cards(content: str, catalog: str) -> list[str]:
    """Return missing required fields for every classic detailed task card."""
    matches = list(TASK_HEADING.finditer(content))
    failures: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        card = content[match.start() : end]
        heading = match.group(0)
        for field in REQUIRED_TASK_FIELDS:
            if field not in card:
                failures.append(f"{catalog}: {heading} is missing {field}")
    if not matches:
        failures.append(f"{catalog}: no detailed task cards found")
    return failures


def repository_failures(root: Path) -> list[str]:
    """Collect every deterministic documentation failure."""
    failures = broken_local_links(root)
    readme = (root / "README.md").read_text(encoding="utf-8")
    for required in README_INVENTORY:
        if f"]({required})" not in readme:
            failures.append(f"README.md: authoritative inventory omits {required}")
    for catalog in DETAILED_TASK_CATALOGS:
        content = (root / catalog).read_text(encoding="utf-8")
        failures.extend(malformed_task_cards(content, catalog))
    return failures


def main() -> int:
    failures = repository_failures(REPOSITORY_ROOT)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Documentation links, inventory, and detailed task cards are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
