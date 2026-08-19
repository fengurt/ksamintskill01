#!/usr/bin/env bash
# Symlink skills/<name> into ~/.cursor/skills, ~/.claude/skills, and/or ~/.codex/skills
# based on install-map.txt (name<TAB>targets).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAP="${ROOT}/scripts/install-map.txt"
SKILLS="${ROOT}/skills"

if [[ ! -f "$MAP" ]]; then
  echo "missing $MAP" >&2
  exit 1
fi

link_one() {
  local name="$1"
  local dest_root="$2"
  local src="${SKILLS}/${name}"
  local dest="${dest_root}/${name}"
  mkdir -p "$dest_root"
  if [[ ! -d "$src" ]]; then
    echo "skip (no source): $src" >&2
    return 0
  fi
  if [[ -L "$dest" ]]; then
    local cur
    cur="$(readlink "$dest")"
    if [[ "$cur" == "$src" ]]; then
      echo "ok  $dest -> $src"
      return 0
    fi
    rm "$dest"
  elif [[ -e "$dest" ]]; then
    local backup="${dest}.bak-ksamint-$(date +%Y%m%d%H%M%S)"
    echo "backup existing $dest -> $backup"
    mv "$dest" "$backup"
  fi
  ln -s "$src" "$dest"
  echo "link $dest -> $src"
}

while IFS=$'\t' read -r name targets || [[ -n "${name:-}" ]]; do
  [[ -z "${name:-}" || "$name" =~ ^# ]] && continue
  IFS=',' read -ra toks <<< "$targets"
  for t in "${toks[@]}"; do
    case "$t" in
      cursor) link_one "$name" "${HOME}/.cursor/skills" ;;
      claude) link_one "$name" "${HOME}/.claude/skills" ;;
      codex)  link_one "$name" "${HOME}/.codex/skills" ;;
      *) echo "unknown target '$t' for $name" >&2; exit 1 ;;
    esac
  done
done < "$MAP"
