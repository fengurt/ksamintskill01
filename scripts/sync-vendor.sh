#!/usr/bin/env bash
# Wrapper: refresh pinned upstream skill libraries into VENDOR_ROOT (or vendor/).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/sync-vendor.py" "$@"
