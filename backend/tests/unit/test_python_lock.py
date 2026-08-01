from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

NORMALIZER = (
    Path(__file__).parents[3]
    / "infrastructure"
    / "scripts"
    / "normalize_python_lock.py"
)
EXPECTED = (
    "click==1.0\n"
    'colorama==0.4.6 ; sys_platform == "win32"\n'
    "    # via the-daily-roast-ai (pyproject.toml)\n"
    "cryptography==2.0\n"
)


@pytest.mark.parametrize(
    "compiled_lock",
    [
        "click==1.0\ncryptography==2.0\n",
        "click==1.0\ncolorama==0.4.6\n    # via click\ncryptography==2.0\n",
        EXPECTED,
    ],
    ids=["linux", "windows", "already-normalized"],
)
def test_lock_normalizer_produces_one_cross_platform_result(
    tmp_path: Path, compiled_lock: str
) -> None:
    lock_file = tmp_path / "requirements.txt"
    lock_file.write_text(compiled_lock, encoding="utf-8")

    subprocess.run([sys.executable, NORMALIZER, lock_file], check=True)

    assert lock_file.read_text(encoding="utf-8") == EXPECTED


@settings(deadline=None)
@given(
    st.sampled_from([EXPECTED, EXPECTED.replace("colorama==0.4.6", "colorama==9.9")])
)
def test_lock_normalizer_is_idempotent(compiled_lock: str) -> None:
    with tempfile.TemporaryDirectory() as directory:
        lock_file = Path(directory) / "requirements.txt"
        lock_file.write_text(compiled_lock, encoding="utf-8")
        subprocess.run([sys.executable, NORMALIZER, lock_file], check=True)
        first_result = lock_file.read_text(encoding="utf-8")

        subprocess.run([sys.executable, NORMALIZER, lock_file], check=True)

        assert lock_file.read_text(encoding="utf-8") == first_result
