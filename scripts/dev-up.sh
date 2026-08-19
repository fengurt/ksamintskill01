#!/usr/bin/env bash
# Repo entrypoint — delegates to gui/scripts/dev-up.sh (port 7979).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$ROOT/gui/scripts/dev-up.sh" "$@"
