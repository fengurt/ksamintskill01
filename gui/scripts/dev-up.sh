#!/usr/bin/env bash
# Start the Skill Hub GUI. Documented port: 7979 (override with PORT=...).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-7979}"

pids="$(lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t 2>/dev/null || true)"
for pid in ${pids}; do
  if ps -p "${pid}" -o command= | grep -qE "server\.js|gui/server"; then
    echo "stopping stale Skill Hub server (pid ${pid}) on :${PORT}"
    kill "${pid}" 2>/dev/null || true
    sleep 0.3
  else
    echo "WARN: port ${PORT} is used by another process (pid ${pid}); set PORT=... to pick another." >&2
    exit 1
  fi
done

echo "starting Skill Hub GUI on http://127.0.0.1:${PORT}"
cd "${HERE}"
PORT="${PORT}" node server.js
