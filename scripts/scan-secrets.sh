#!/usr/bin/env bash
# Fail if plaintext secrets look present under skills/ (or given paths).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGETS=("${@:-"$ROOT/skills"}")

# Patterns that strongly suggest committed secrets (not mere 1Password item names).
PATTERNS=(
  'sk-[a-zA-Z0-9]{20,}'
  'sk-ant-[a-zA-Z0-9\-]{20,}'
  'AKIA[0-9A-Z]{16}'
  '-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----'
  'ghp_[a-zA-Z0-9]{20,}'
  'gho_[a-zA-Z0-9]{20,}'
  'xox[baprs]-[a-zA-Z0-9-]{10,}'
)

# Exclude placeholders and gitignored secret trees from match noise.
RG_GLOBS=(
  -g '!.git/**'
  -g '!**/secrets/**'
  -g '!**/.env'
  -g '!**/.env.*'
  -g '!**/deploy.env'
  -g '!**/node_modules/**'
  -g '!**/__pycache__/**'
)

echo "Scanning: ${TARGETS[*]}"
hits=0
TMP_HITS=$(mktemp)
for target in "${TARGETS[@]}"; do
  if [[ ! -e "$target" ]]; then
    echo "skip missing: $target" >&2
    continue
  fi
  for pat in "${PATTERNS[@]}"; do
    if command -v rg >/dev/null 2>&1; then
      rg -n --hidden "${RG_GLOBS[@]}" -e "$pat" "$target" 2>/dev/null >>"$TMP_HITS" || true
    else
      grep -RInE --exclude-dir=.git --exclude-dir=secrets --exclude-dir=node_modules \
        --exclude='.env' --exclude='.env.*' "$pat" "$target" 2>/dev/null >>"$TMP_HITS" || true
    fi
  done
done

# Drop obvious documentation placeholders
if [[ -s "$TMP_HITS" ]]; then
  filtered=$(grep -vE 'YOUR_[A-Z0-9_]+|REPLACE_ME|changeme|example\.com|sk-ant-api03-xxx|<YOUR_|\$\{[A-Z_]+\}' "$TMP_HITS" || true)
  if [[ -n "$filtered" ]]; then
    echo "$filtered"
    hits=1
  fi
fi
rm -f "$TMP_HITS"

if [[ "$hits" -gt 0 ]]; then
  echo "FAIL: possible plaintext secrets matched ($hits pattern hits). Redact before commit." >&2
  exit 1
fi
echo "OK: no plaintext secret patterns matched."
exit 0
