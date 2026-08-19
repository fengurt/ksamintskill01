#!/usr/bin/env bash
# Wrapper: shallow-clone / refresh upstream skill libraries into vendor/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/sync-vendor.py" "$@"
