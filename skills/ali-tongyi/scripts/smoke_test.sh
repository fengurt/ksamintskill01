#!/usr/bin/env bash
# Smoke-test the Alibaba Tongyi / Bailian Token Plan API end to end.
# Loads the key from 1Password, then calls qwen3.7-max on the Token Plan endpoint.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${HERE}/load_key.sh"

MODEL="${1:-qwen3.7-max}"
echo "=== Token Plan smoke test: ${MODEL} ==="
curl -s -w "\nHTTP %{http_code}\n" \
  "${ALI_TONGYI_BASE_URL}/chat/completions" \
  -H "Authorization: Bearer ${DASHSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"reply with one word: pong\"}],\"max_tokens\":300}"
