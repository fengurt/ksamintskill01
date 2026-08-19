#!/usr/bin/env bash
# List models a provider/hub exposes (GET /models).
# Usage:  ./list_models.sh <provider>
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PROVIDER="${1:-}"
[ -z "${PROVIDER}" ] && { echo "usage: ./list_models.sh <provider>" >&2; exit 1; }

# shellcheck disable=SC1091
source "${HERE}/load_key.sh" "${PROVIDER}" || exit $?
BASE="${LLM_BASE_URL%/}"

if [ "${LLM_PROTOCOL}" = "anthropic" ]; then
  curl -s -m 30 "${BASE}/v1/models" \
    -H "x-api-key: ${LLM_API_KEY}" -H "anthropic-version: 2023-06-01"
else
  curl -s -m 30 "${BASE}/models" -H "Authorization: Bearer ${LLM_API_KEY}"
fi | { python3 -c "import sys,json; d=json.load(sys.stdin); ids=[m.get('id') for m in d.get('data',d if isinstance(d,list) else [])]; print('\n'.join(sorted(filter(None,ids)))) if ids else print(sys.stdin)" 2>/dev/null || cat; }
