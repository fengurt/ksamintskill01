#!/usr/bin/env bash
# Smoke-test any registered provider/hub end to end.
# Usage:  ./smoke_test.sh <provider> [model]
# Loads the key from 1Password, then sends a 1-line chat request.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PROVIDER="${1:-}"
[ -z "${PROVIDER}" ] && { echo "usage: ./smoke_test.sh <provider> [model]" >&2; exit 1; }

# shellcheck disable=SC1091
source "${HERE}/load_key.sh" "${PROVIDER}" || exit $?

MODEL="${2:-${LLM_DEFAULT_MODEL}}"
if [ -z "${MODEL}" ] || [ "${MODEL}" = "-" ]; then
  echo "ERROR: no model. Pass one: ./smoke_test.sh ${PROVIDER} <model>" >&2; exit 1
fi
BASE="${LLM_BASE_URL%/}"
echo "=== ${PROVIDER} smoke test: ${MODEL} ==="

if [ "${LLM_PROTOCOL}" = "anthropic" ]; then
  curl -s -m 40 -w "\nHTTP %{http_code}\n" "${BASE}/v1/messages" \
    -H "x-api-key: ${LLM_API_KEY}" \
    -H "anthropic-version: 2023-06-01" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"${MODEL}\",\"max_tokens\":50,\"messages\":[{\"role\":\"user\",\"content\":\"reply with one word: pong\"}]}"
else
  curl -s -m 40 -w "\nHTTP %{http_code}\n" "${BASE}/chat/completions" \
    -H "Authorization: Bearer ${LLM_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"${MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"reply with one word: pong\"}],\"max_tokens\":50}"
fi
