#!/usr/bin/env bash
# Load an LLM provider/hub key from 1Password into the environment.
# Usage:  source load_key.sh <provider>
# Exports: LLM_API_KEY  LLM_BASE_URL  LLM_PROTOCOL  LLM_DEFAULT_MODEL  LLM_PROVIDER
# Secrets are read from 1Password at runtime; nothing is written to disk.
# Requires: 1Password desktop app unlocked + CLI integration (Touch ID).

_llm_src="${BASH_SOURCE[0]:-$0}"
_llm_scripts="$(cd "$(dirname "${_llm_src}")" 2>/dev/null && pwd)"
_LLM_HUB="${LLM_HUB_DIR:-$(dirname "${_llm_scripts}")}"
_REG="${_LLM_HUB}/registry.tsv"
[ -f "${_REG}" ] || _REG="$HOME/.cursor/skills/llm-hub/registry.tsv"

_llm_provider="${1:-}"
if [ -z "${_llm_provider}" ]; then
  echo "usage: source load_key.sh <provider>" >&2
  echo "providers:" >&2
  awk -F'\t' '!/^#/ && NF>=6 {printf "  %-15s %-7s %s\n",$1,$2,($5=="EMPTY"?"[EMPTY]":"")}' "${_REG}" >&2
  return 1 2>/dev/null || exit 1
fi

_row="$(awk -F'\t' -v p="${_llm_provider}" '!/^#/ && $1==p {print; exit}' "${_REG}")"
if [ -z "${_row}" ]; then
  echo "ERROR: unknown provider '${_llm_provider}'. Run 'source load_key.sh' to list." >&2
  return 1 2>/dev/null || exit 1
fi

IFS=$'\t' read -r _p _group _base _proto _ref _model <<< "${_row}"

if [ "${_ref}" = "EMPTY" ]; then
  echo "EMPTY: no API key stored in 1Password for '${_llm_provider}' (group=${_group})." >&2
  echo "       base_url would be: ${_base}" >&2
  echo "       Add the key to its 1Password item, then set its op:// ref in registry.tsv." >&2
  return 2 2>/dev/null || exit 2
fi

_key="$(op read "${_ref}" 2>/dev/null)"
if [ -z "${_key}" ]; then
  echo "ERROR: could not resolve key for '${_llm_provider}' from 1Password." >&2
  echo "       ref: ${_ref} — is the desktop app unlocked with CLI integration on?" >&2
  return 3 2>/dev/null || exit 3
fi

export LLM_PROVIDER="${_p}"
export LLM_API_KEY="${_key}"
export LLM_BASE_URL="${_base}"
export LLM_PROTOCOL="${_proto}"
export LLM_DEFAULT_MODEL="${_model}"

echo "Loaded ${LLM_PROVIDER} (${_group}, ${LLM_PROTOCOL}) -> ${LLM_BASE_URL}"
echo "  LLM_API_KEY: ${#LLM_API_KEY} chars, prefix ${LLM_API_KEY:0:4}...  default model: ${LLM_DEFAULT_MODEL}"
