#!/usr/bin/env bash
set -uo pipefail

raw_log="${RUNNER_TEMP:-/tmp}/supabase-start-raw.log"
diagnostic="${RUNNER_TEMP:-/tmp}/supabase-start-diagnostics.txt"

set +e
supabase start --debug 2>&1 | tee "$raw_log"
status=${PIPESTATUS[0]}
set -e

if [[ $status -eq 0 ]]; then
  exit 0
fi

python3 - "$raw_log" "$diagnostic" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
patterns = re.compile(
    r"error|failed|failure|fatal|panic|sqlstate|health|unhealthy|denied|invalid|"
    r"does not exist|constraint|duplicate|syntax|timeout|stopped",
    re.IGNORECASE,
)
selected = [line for line in source if patterns.search(line)]
if not selected:
    selected = source[-160:]
else:
    selected = selected[-240:]

redactions = (
    (re.compile(r"(?i)(anon key|service_role key|jwt secret|api key)(\s*[:=]\s*)\S+"), r"\1\2[REDACTED]"),
    (re.compile(r"postgresql(?:\+psycopg)?://[^\s]+"), "postgresql://[REDACTED]"),
    (re.compile(r"(?i)(password)(\s*[:=]\s*)\S+"), r"\1\2[REDACTED]"),
)
for index, line in enumerate(selected):
    for pattern, replacement in redactions:
        line = pattern.sub(replacement, line)
    selected[index] = line

Path(sys.argv[2]).write_text("\n".join(selected) + "\n", encoding="utf-8")
PY

cat "$diagnostic"
exit "$status"
