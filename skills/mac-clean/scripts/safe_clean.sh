#!/usr/bin/env bash
# safe_clean.sh — dry-run by default; trash Safe-tier candidates only with --apply
set -euo pipefail

APPLY=0
SCAN_MODE="caches"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCAN="$SCRIPT_DIR/scan-mac-cleanup.sh"
OUT_DIR="${OUT_DIR:-${TMPDIR:-/tmp}/mac-clean-scan}"
SAFE_LIST="$OUT_DIR/safe_candidates.txt"
NEVER_TOUCH="$SCRIPT_DIR/../references/never_touch.md"

have() { command -v "$1" >/dev/null 2>&1; }

usage() {
  cat <<EOF
Usage: bash safe_clean.sh [--apply] [--rescan]

  Default: dry-run — list Safe-tier candidates, delete nothing.
  --apply   move candidates to Trash via \`trash\` (or \`rm\` fallback refused).
  --rescan  run scan-mac-cleanup.sh caches first to refresh candidate list.

Requires: prior scan (or --rescan). Respects references/never_touch.md.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --rescan) SCAN_MODE="rescan"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ "$SCAN_MODE" == "rescan" || ! -f "$SAFE_LIST" ]]; then
  bash "$SCAN" caches >/dev/null
fi

if [[ ! -f "$SAFE_LIST" ]]; then
  echo "No safe candidate list at $SAFE_LIST — run scan first." >&2
  exit 1
fi

if ! have trash; then
  echo "error: \`trash\` CLI required (brew install trash). Refusing rm -rf." >&2
  exit 1
fi

blocked() {
  local p="$1"
  # hard blocks even if listed
  [[ "$p" == *"/Keychains"* ]] && return 0
  [[ "$p" == *"/Mobile Documents"* ]] && return 0
  [[ "$p" == *".photoslibrary"* ]] && return 0
  [[ "$p" == *"/Messages/Attachments"* ]] && return 0
  [[ "$p" == *"/MobileSync/Backup"* ]] && return 0
  local base
  base="$(basename "$p")"
  [[ "$base" == com.apple.* ]] && return 0
  echo "$base" | rg -qi '^(1[Pp]assword|Bitwarden|Clash|Surge|Tailscale|Cursor|Claude|ChatGPT|WhatsApp)' && return 0
  return 1
}

echo "# safe_clean $([[ $APPLY -eq 1 ]] && echo APPLY || echo DRY-RUN)"
echo
echo "| Action | Path | Size |"
echo "|---|---|---:|"

freed=0
count=0
while IFS= read -r path; do
  [[ -z "$path" || ! -e "$path" ]] && continue
  if blocked "$path"; then
    echo "| skip-blocked | \`$path\` | — |"
    continue
  fi
  # Never trash entire Library/Caches aggregate — only children from list
  if [[ "$path" == "$HOME/Library/Caches" || "$path" == "$HOME/Library/Logs" ]]; then
    echo "| skip-aggregate | \`$path\` | use child dirs |"
    continue
  fi
  sz="$(du -sk "$path" 2>/dev/null | awk '{print $1*1024}')"
  if have numfmt; then
    human="$(numfmt --to=iec --suffix=B "$sz" 2>/dev/null || echo "${sz}B")"
  else
    human="$(awk -v b="$sz" 'BEGIN{u[1]="B";u[2]="K";u[3]="M";u[4]="G";i=1;while(b>=1024&&i<4){b/=1024;i++}printf "%.1f%s\n",b,u[i]}')"
  fi
  if [[ $APPLY -eq 1 ]]; then
    if trash "$path" 2>/dev/null; then
      echo "| trashed | \`$path\` | $human |"
      freed=$((freed + sz))
      count=$((count + 1))
    else
      echo "| failed | \`$path\` | $human |"
    fi
  else
    echo "| would-trash | \`$path\` | $human |"
    freed=$((freed + sz))
    count=$((count + 1))
  fi
done < "$SAFE_LIST"

echo
if have numfmt; then
  echo "Candidates: $count · $([[ $APPLY -eq 1 ]] && echo Freed || echo Would free): $(numfmt --to=iec --suffix=B "$freed")"
else
  echo "Candidates: $count · bytes: $freed"
fi
echo
df -h / | head -2
echo
echo "Denylist: $NEVER_TOUCH"
[[ $APPLY -eq 0 ]] && echo "Re-run with --apply after user approval."
