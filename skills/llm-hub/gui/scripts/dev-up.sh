#!/usr/bin/env bash
# Start the LLM Hub GUI. Documented port: 7878 (override with PORT=...).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-7878}"

# Free only THIS project's documented port, and only if it's our own stale server.
pids="$(lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t 2>/dev/null || true)"
for pid in ${pids}; do
  if ps -p "${pid}" -o command= | grep -q "server.js"; then
    echo "stopping stale llm-hub server (pid ${pid}) on :${PORT}"; kill "${pid}" 2>/dev/null || true
  else
    echo "WARN: port ${PORT} is used by another process (pid ${pid}); set PORT=... to pick another." >&2; exit 1
  fi
done

echo "starting LLM Hub GUI on http://localhost:${PORT}"
cd "${HERE}"
PORT="${PORT}" node server.js
