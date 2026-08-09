"""Normalize platform-conditional entries in the shared Python lock file."""

from __future__ import annotations

import argparse
from pathlib import Path

COLORAMA_PREFIX = "colorama=="
COLORAMA_BLOCK = (
    'colorama==0.4.6 ; sys_platform == "win32"\n'
    "    # via the-daily-roast-ai (pyproject.toml)\n"
)

TZDATA_PREFIX = "tzdata=="


def normalize_lock(content: str) -> str:
    """Return a lock that is identical on Windows and Linux."""
    lines = content.splitlines(keepends=True)
    normalized: list[str] = []
    skipping_colorama = False
    skipping_tzdata = False

    for line in lines:
        if line.startswith(COLORAMA_PREFIX):
            skipping_colorama = True
            continue
        if skipping_colorama and (line.startswith(" ") or not line.strip()):
            continue
        skipping_colorama = False

        if line.startswith(TZDATA_PREFIX):
            skipping_tzdata = True
            continue
        if skipping_tzdata and (line.startswith(" ") or not line.strip()):
            continue
        skipping_tzdata = False

        normalized.append(line)

    insert_at = next(
        (
            index
            for index, line in enumerate(normalized)
            if line.startswith("cryptography==")
        ),
        None,
    )
    if insert_at is None:
        raise ValueError("Could not find the cryptography entry in the compiled lock")

    normalized.insert(insert_at, COLORAMA_BLOCK)
    return "".join(normalized)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lock_file", type=Path)
    args = parser.parse_args()
    content = args.lock_file.read_text(encoding="utf-8")
    args.lock_file.write_text(normalize_lock(content), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
