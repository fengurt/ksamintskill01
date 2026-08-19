#!/usr/bin/env bash
# Load the Alibaba Tongyi / Bailian Token Plan key from 1Password into the env.
# Usage:  source load_key.sh
# The real key is never written to disk; it is read from 1Password each time.
# Requires: 1Password desktop app unlocked + CLI integration enabled (Touch ID).

_ITEM="op://fyg24alzrp23y727yk5n6jt4cu/jrxndmsama43aak6dnas3zfmcm"

DASHSCOPE_API_KEY="$(op read "${_ITEM}/seat_c42a497589b140f381fac82bb69aa201" 2>/dev/null)"
DASHSCOPE_STD_API_KEY="$(op read "${_ITEM}/api-ID-2231532" 2>/dev/null)"
export DASHSCOPE_API_KEY DASHSCOPE_STD_API_KEY
export ALI_TONGYI_BASE_URL="https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
export ALI_TONGYI_ANTHROPIC_URL="https://token-plan.cn-beijing.maas.aliyuncs.com/apps/anthropic"

if [ -n "${DASHSCOPE_API_KEY}" ]; then
  echo "Loaded DASHSCOPE_API_KEY (Token Plan seat key, ${#DASHSCOPE_API_KEY} chars, prefix ${DASHSCOPE_API_KEY:0:6}...)"
else
  echo "ERROR: could not load key from 1Password. Is the desktop app unlocked and CLI integration on?" >&2
fi
