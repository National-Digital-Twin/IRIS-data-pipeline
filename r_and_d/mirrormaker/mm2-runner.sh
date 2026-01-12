#!/usr/bin/env bash
set -euo pipefail

# 1) start MM2
connect-mirror-maker "${MM2_PROPERTIES_PATH:-/etc/mm2.properties}" &
MM2_PID=$!

# 2) run checker loop (blocks)
set +e
python /app/mm2-checker.py
RC=$?
set -e

# 3) if checker exits 0, stop MM2 cleanly
kill -TERM "$MM2_PID" || true
wait "$MM2_PID" || true

exit "$RC"