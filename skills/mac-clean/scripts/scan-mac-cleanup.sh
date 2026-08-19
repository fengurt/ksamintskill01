#!/usr/bin/env bash
# scan-mac-cleanup.sh — inventory Mac apps + cleanup candidates (report only; never deletes)
# Modes: full | apps | leftovers | caches | agents | brew | risk
set -euo pipefail

MODE="${1:-full}"
MIN_CACHE_MB="${MIN_CACHE_MB:-100}"
OUT_DIR="${OUT_DIR:-${TMPDIR:-/tmp}/mac-clean-scan}"
mkdir -p "$OUT_DIR"
REPORT="$OUT_DIR/report.md"
SAFE_LIST="$OUT_DIR/safe_candidates.txt"
BUNDLE_IDS="$OUT_DIR/bundle_ids.txt"
APPS_FILE="$OUT_DIR/apps.txt"
TS="$(date '+%Y-%m-%d %H:%M:%S')"
: > "$SAFE_LIST"
: > "$BUNDLE_IDS"
: > "$APPS_FILE"

have() { command -v "$1" >/dev/null 2>&1; }

bytes_human() {
  local b="${1:-0}"
  if have numfmt; then numfmt --to=iec --suffix=B "$b" 2>/dev/null || echo "${b}B"
  else
    awk -v b="$b" 'BEGIN{
      u[1]="B";u[2]="KB";u[3]="MB";u[4]="GB";u[5]="TB";
      i=1; while (b>=1024 && i<5){b/=1024;i++}
      printf "%.1f%s\n", b, u[i]
    }'
  fi
}

dir_bytes() {
  local p="$1"
  if [[ -d "$p" || -f "$p" ]]; then
    # Bound du so huge trees cannot hang the scan indefinitely
    if have gtimeout; then
      gtimeout 8 du -sk "$p" 2>/dev/null | awk '{print $1*1024}' || echo 0
    elif have timeout; then
      timeout 8 du -sk "$p" 2>/dev/null | awk '{print $1*1024}' || echo 0
    else
      perl -e 'alarm 8; exec @ARGV' du -sk "$p" 2>/dev/null | awk '{print $1*1024}' || echo 0
    fi
  else
    echo 0
  fi
}

scan_app_dirs() {
  local d
  for d in /Applications "$HOME/Applications" /Applications/Utilities; do
    [[ -d "$d" ]] || continue
    find "$d" -maxdepth 2 -name '*.app' -print 2>/dev/null
  done
}

normalize_name() {
  sed -E 's|.*/||; s/\.app$//; s/[[:space:]]+/-/g; s/[^A-Za-z0-9.+_-]//g' \
    | tr '[:upper:]' '[:lower:]'
}

collect_bundle_id() {
  local app="$1" bid=""
  bid="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Contents/Info.plist" 2>/dev/null || true)"
  if [[ -n "$bid" ]]; then
    echo "$bid" >> "$BUNDLE_IDS"
    echo "$bid" | tr '[:upper:]' '[:lower:]' | sed 's/\./-/g' >> "$APPS_FILE"
  fi
}

is_known_app() {
  local token="$1"
  [[ -z "$token" ]] && return 1
  if grep -qxF "$token" "$APPS_FILE" 2>/dev/null; then return 0; fi
  if grep -qiF "$token" "$APPS_FILE" 2>/dev/null; then return 0; fi
  if [[ -s "$BUNDLE_IDS" ]] && grep -qiF "$token" "$BUNDLE_IDS" 2>/dev/null; then return 0; fi
  local k
  while IFS= read -r k; do
    [[ -n "$k" && ${#k} -ge 3 && "$token" == *"$k"* ]] && return 0
  done < "$APPS_FILE"
  return 1
}

is_protected_name() {
  local base="$1"
  echo "$base" | rg -qi '^(com\.apple\.|1[Pp]assword|Bitwarden|LastPass|KeePass|Clash|Surge|Shadowsocks|V2Ray|Tailscale|WireGuard|Cursor|Claude|ChatGPT|Ollama|WhatsApp|WeChat)' && return 0
  return 1
}

risk_for_cache_path() {
  local p="$1"
  case "$p" in
    */.npm/*|*/.npm|*/pnpm/*|*/Library/pnpm*|*/.yarn*|*/Library/Caches/Yarn*|*/.cargo*|*/go/pkg*|*/.cache/pip*|*/Library/Caches/pip*|*/Library/Caches/CocoaPods*|*/Library/Caches/Homebrew*|*/Library/Caches/node-gyp*|*/DerivedData*|*/CoreSimulator*|*/iOS\ DeviceSupport*|*/.gradle*)
      echo "Costly"
      ;;
    */Library/Caches/*|*/Library/Logs/*|*/Saved\ Application\ State/*|/tmp/*|"$TMPDIR"/*|*/.Trash/*)
      echo "Safe"
      ;;
    *)
      echo "UserData"
      ;;
  esac
}

{
  echo "# Mac Clean Scan"
  echo
  echo "- Generated: $TS"
  echo "- Host: $(scutil --get ComputerName 2>/dev/null || hostname)"
  echo "- Mode: \`$MODE\`"
  echo "- Min cache report size: ${MIN_CACHE_MB} MB"
  echo "- Output dir: \`$OUT_DIR\`"
  echo "- Risk tiers: **Safe** (recreatable) · **Costly** (dev artifacts) · **UserData** (confirm per item)"
  echo
  echo "> Report only. Nothing was deleted. See \`references/never_touch.md\`."
  echo
} > "$REPORT"

# Always build app + bundle-id index for matching
while IFS= read -r app; do
  [[ -n "$app" ]] || continue
  basename "$app" .app | normalize_name >> "$APPS_FILE"
  collect_bundle_id "$app"
done < <(scan_app_dirs | sort -u)
if have brew; then
  brew list --cask 2>/dev/null | normalize_name >> "$APPS_FILE" || true
fi
sort -u "$APPS_FILE" -o "$APPS_FILE"
sort -u "$BUNDLE_IDS" -o "$BUNDLE_IDS"

# ========== APPS ==========
if [[ "$MODE" == "full" || "$MODE" == "apps" ]]; then
  {
    echo "## Installed applications"
    echo
    echo "| App | Bundle ID | Path | Size |"
    echo "|---|---|---|---:|"
  } >> "$REPORT"

  while IFS= read -r app; do
    [[ -n "$app" ]] || continue
    name="$(basename "$app" .app)"
    bid="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Contents/Info.plist" 2>/dev/null || echo "-")"
    sz="$(dir_bytes "$app")"
    echo "| $name | \`$bid\` | \`$app\` | $(bytes_human "$sz") |" >> "$REPORT"
  done < <(scan_app_dirs | sort -u)

  echo >> "$REPORT"
  echo "### Package managers" >> "$REPORT"
  echo >> "$REPORT"
  if have brew; then
    echo '```' >> "$REPORT"
    echo "brew casks:" >> "$REPORT"
    brew list --cask 2>/dev/null | sed 's/^/  /' || echo "  (none)"
    echo >> "$REPORT"
    echo "brew leaves (top-level formulas):" >> "$REPORT"
    brew leaves 2>/dev/null | sed 's/^/  /' || true
    echo '```' >> "$REPORT"
  else
    echo "- Homebrew: not installed" >> "$REPORT"
  fi
  if have mas; then
    echo >> "$REPORT"
    echo '```' >> "$REPORT"
    echo "mas apps:" >> "$REPORT"
    mas list 2>/dev/null | sed 's/^/  /' || true
    echo '```' >> "$REPORT"
  else
    echo "- mas: not installed (\`brew install mas\` for App Store CLI)" >> "$REPORT"
  fi
  if have mo; then
    echo >> "$REPORT"
    echo "- Mole (\`mo\`) detected — optional acceleration: \`mo clean --dry-run\`, \`mo uninstall\`" >> "$REPORT"
  fi
  echo >> "$REPORT"
fi

# ========== RISK: APFS + DEV HOTSPOTS ==========
if [[ "$MODE" == "full" || "$MODE" == "risk" || "$MODE" == "caches" ]]; then
  {
    echo "## Risk-tier hotspots"
    echo
    echo "| Risk | Path | Size | Note |"
    echo "|---|---|---:|---|"
  } >> "$REPORT"

  # APFS local snapshots
  if have tmutil; then
    snaps="$(tmutil listlocalsnapshots / 2>/dev/null | rg 'com\.apple\.TimeMachine' || true)"
    if [[ -n "$snaps" ]]; then
      count="$(echo "$snaps" | wc -l | tr -d ' ')"
      echo "| Costly | APFS local snapshots on \`/\` | (hidden) | $count snapshots — thin with \`tmutil thinlocalsnapshots / <bytes> 4\` after confirm |" >> "$REPORT"
      echo >> "$REPORT"
      echo '```' >> "$REPORT"
      echo "$snaps" | head -20 >> "$REPORT"
      echo '```' >> "$REPORT"
      echo >> "$REPORT"
      echo "| Risk | Path | Size | Note |" >> "$REPORT"
      echo "|---|---|---:|---|" >> "$REPORT"
    else
      echo "| Safe | APFS local snapshots | 0 | none listed |" >> "$REPORT"
    fi
  fi

  report_hotspot() {
    local risk="$1" target="$2" note="$3"
    [[ -e "$target" ]] || return 0
    local sz
    sz="$(dir_bytes "$target")"
    [[ "$sz" -ge 1048576 ]] || return 0
    echo "| $risk | \`$target\` | $(bytes_human "$sz") | $note |" >> "$REPORT"
    if [[ "$risk" == "Safe" ]]; then
      echo "$target" >> "$SAFE_LIST"
    fi
  }

  report_hotspot Costly "$HOME/.npm/_cacache" "npm cache"
  report_hotspot Costly "$HOME/Library/pnpm" "pnpm store"
  report_hotspot Costly "$HOME/.yarn" "yarn"
  report_hotspot Costly "$HOME/Library/Caches/Yarn" "yarn caches"
  report_hotspot Costly "$HOME/.cargo/registry" "cargo registry"
  report_hotspot Costly "$HOME/go/pkg" "Go pkg cache"
  report_hotspot Costly "$HOME/.cache/pip" "pip cache"
  report_hotspot Costly "$HOME/Library/Caches/Homebrew" "Homebrew downloads"
  report_hotspot Costly "$HOME/Library/Caches/CocoaPods" "CocoaPods"
  report_hotspot Costly "$HOME/Library/Developer/Xcode/DerivedData" "Xcode DerivedData"
  report_hotspot Costly "$HOME/Library/Developer/CoreSimulator/Caches" "Simulator caches"
  report_hotspot Costly "$HOME/Library/Developer/Xcode/iOS DeviceSupport" "iOS DeviceSupport"
  report_hotspot Costly "$HOME/.gradle/caches" "Gradle caches"
  # Sample known regenerable cache dirs only (full tree du is too slow)
  for name in Spotify Firefox typescript pip \
      playwright ms-playwright node-gyp geoip Cypress Electron \
      com.microsoft.VSCode.ShipIt com.figma.Desktop.ShipIt; do
    report_hotspot Safe "$HOME/Library/Caches/$name" "Library/Caches/$name"
  done
  # Homebrew cache is Costly above; also allow Safe-tier trash via candidate list
  if [[ -d "$HOME/Library/Caches/Homebrew" ]]; then
    echo "$HOME/Library/Caches/Homebrew" >> "$SAFE_LIST"
  fi

  if have docker; then
    echo >> "$REPORT"
    echo "### Docker disk (Costly)" >> "$REPORT"
    echo >> "$REPORT"
    echo '```' >> "$REPORT"
    { docker system df 2>/dev/null | head -20 || echo "docker present but df failed"; } >> "$REPORT"
    echo '```' >> "$REPORT"
  fi
  echo >> "$REPORT"
fi

# ========== LEFTOVERS ==========
if [[ "$MODE" == "full" || "$MODE" == "leftovers" ]]; then
  {
    echo "## Likely orphan leftovers"
    echo
    echo "Names not matching installed apps / brew casks / bundle IDs. Vendor roots often false-positive."
    echo
    echo "| Risk | Confidence | Location | Size | Reason |"
    echo "|---|---|---|---:|---|"
  } >> "$REPORT"

  LEFTOVER_ROOTS=(
    "$HOME/Library/Application Support"
    "$HOME/Library/Caches"
    "$HOME/Library/Logs"
    "$HOME/Library/Preferences"
    "$HOME/Library/Saved Application State"
    "$HOME/Library/LaunchAgents"
    "$HOME/Library/HTTPStorages"
    "$HOME/Library/WebKit"
  )

  SKIP_RE='^(com\.apple\.|Apple|Apple Computer|MobileSync|iCloud|CloudStorage|Keychains|Containers|Group Containers|Preferences|Caches|Logs|Fonts|ColorSync|Keyboard Layouts|Language Modeling|Autosave Information|Application Scripts|Assistant|Assistants|Audio|Cookies|Dictionaries|Favorites|Finance|Google|Mozilla|Microsoft|Adobe|JetBrains|Docker|Homebrew|\.|\.\.)$'

  for root in "${LEFTOVER_ROOTS[@]}"; do
    [[ -d "$root" ]] || continue
    if [[ "$root" == *"/Preferences" ]]; then
      find "$root" -maxdepth 1 \( -type f -o -type l \) -name '*.plist' -print 2>/dev/null \
        | while IFS= read -r f; do
            base="$(basename "$f")"
            [[ "$base" == com.apple.* ]] && continue
            is_protected_name "$base" && continue
            token="$(echo "$base" | sed -E 's/\.plist$//; s/^com\.//; s/\./-/g' | tr '[:upper:]' '[:lower:]')"
            vendor="$(echo "$base" | sed -E 's/\.plist$//; s/^com\.//; s/\..*$//' | tr '[:upper:]' '[:lower:]')"
            bid_raw="$(echo "$base" | sed -E 's/\.plist$//')"
            if ! is_known_app "$token" && ! is_known_app "$vendor" && ! is_known_app "$bid_raw"; then
              sz="$(stat -f%z "$f" 2>/dev/null || echo 0)"
              echo "| UserData | medium | \`$f\` | $(bytes_human "$sz") | prefs without matching app/bundle |" >> "$REPORT"
            fi
          done
      continue
    fi

    find "$root" -maxdepth 1 \( -type d -o -type l \) ! -name '.' ! -name '..' -print 2>/dev/null \
      | while IFS= read -r p; do
          base="$(basename "$p")"
          echo "$base" | rg -q "$SKIP_RE" && continue
          [[ "$base" == com.apple.* || "$base" == Apple* ]] && continue
          is_protected_name "$base" && continue
          token="$(echo "$base" | sed -E 's/\.savedState$//; s/^com\.//; s/\./-/g; s/[[:space:]]+/-/g' | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9.+_-]//g')"
          if ! is_known_app "$token" && ! is_known_app "$base"; then
            sz="$(dir_bytes "$p")"
            if [[ "$root" != *LaunchAgents* && "$sz" -lt 65536 ]]; then
              continue
            fi
            conf="medium"
            risk="UserData"
            if [[ "$root" == *LaunchAgents* ]]; then
              conf="high"
            fi
            if [[ "$root" == *"/Caches"* || "$root" == *"/Logs"* || "$root" == *"Saved Application State"* ]]; then
              risk="Safe"
              echo "$p" >> "$SAFE_LIST"
            fi
            echo "| $risk | $conf | \`$p\` | $(bytes_human "$sz") | no matching installed app/bundle |" >> "$REPORT"
          fi
        done
  done
  echo >> "$REPORT"
fi

# ========== CACHES ==========
if [[ "$MODE" == "full" || "$MODE" == "caches" ]]; then
  {
    echo "## Large caches & temp (≥ ${MIN_CACHE_MB} MB)"
    echo
    echo "| Risk | Path | Size |"
    echo "|---|---|---:|"
  } >> "$REPORT"

  MIN_KB=$((MIN_CACHE_MB * 1024))
  # Prefer bounded roots — avoid full ~/Library/Caches enumeration
  CACHE_TARGETS=(
    "$HOME/Library/Logs"
    "$HOME/Library/Developer/Xcode/DerivedData"
    "$HOME/Library/Developer/CoreSimulator/Caches"
    "$HOME/Library/Developer/Xcode/iOS DeviceSupport"
    "$HOME/.npm"
    "$HOME/.cache"
    "$HOME/Library/Caches/Homebrew"
  )

  for root in "${CACHE_TARGETS[@]}"; do
    [[ -e "$root" ]] || continue
    if [[ -d "$root" ]]; then
      # List immediate children with find + timed du (cap 25 entries)
      find "$root" -maxdepth 1 -mindepth 1 \( -type d -o -type f \) -print 2>/dev/null \
        | head -40 \
        | while IFS= read -r path; do
            base="$(basename "$path")"
            is_protected_name "$base" && continue
            kb="$(dir_bytes "$path")"
            [[ "${kb:-0}" -ge $((MIN_KB * 1024)) ]] || continue
            risk="$(risk_for_cache_path "$path")"
            echo "| $risk | \`$path\` | $(bytes_human "$kb") |" >> "$REPORT"
            if [[ "$risk" == "Safe" ]]; then
              echo "$path" >> "$SAFE_LIST"
            fi
          done
    fi
  done

  if have brew; then
    echo >> "$REPORT"
    echo "### Homebrew cleanup preview" >> "$REPORT"
    echo >> "$REPORT"
    echo '```' >> "$REPORT"
    brew cleanup -n 2>/dev/null | tail -40 || echo "(brew cleanup -n failed)"
    echo '```' >> "$REPORT"
  fi
  echo >> "$REPORT"
fi

# ========== AGENTS ==========
if [[ "$MODE" == "full" || "$MODE" == "agents" ]]; then
  {
    echo "## LaunchAgents / daemons"
    echo
    echo "| Kind | Path | Issue | Risk |"
    echo "|---|---|---|---|"
  } >> "$REPORT"

  check_plist_bin() {
    local plist="$1" kind="$2"
    [[ -f "$plist" ]] || return 0
    local base prog
    base="$(basename "$plist")"
    [[ "$base" == com.apple.* ]] && return 0
    prog="$(/usr/libexec/PlistBuddy -c 'Print :ProgramArguments:0' "$plist" 2>/dev/null \
      || /usr/libexec/PlistBuddy -c 'Print :Program' "$plist" 2>/dev/null || true)"
    if [[ -n "$prog" && ! -e "$prog" ]]; then
      echo "| $kind | \`$plist\` | missing binary: \`$prog\` | Safe |" >> "$REPORT"
      echo "$plist" >> "$SAFE_LIST"
    else
      echo "| $kind | \`$plist\` | present | — |" >> "$REPORT"
    fi
  }

  find "$HOME/Library/LaunchAgents" -maxdepth 1 -name '*.plist' -print 2>/dev/null \
    | while read -r p; do check_plist_bin "$p" "user LaunchAgent"; done
  if [[ -d /Library/LaunchAgents ]]; then
    find /Library/LaunchAgents -maxdepth 1 -name '*.plist' -print 2>/dev/null \
      | while read -r p; do check_plist_bin "$p" "system LaunchAgent"; done
  fi
  if [[ -d /Library/LaunchDaemons ]]; then
    find /Library/LaunchDaemons -maxdepth 1 -name '*.plist' -print 2>/dev/null \
      | while read -r p; do check_plist_bin "$p" "LaunchDaemon"; done
  fi
  echo >> "$REPORT"
fi

# ========== BREW ==========
if [[ "$MODE" == "full" || "$MODE" == "brew" ]]; then
  {
    echo "## Homebrew health"
    echo
  } >> "$REPORT"
  if have brew; then
    echo '```' >> "$REPORT"
    brew doctor 2>&1 | head -60 || true
    echo '```' >> "$REPORT"
    echo >> "$REPORT"
    echo "### Autoremovable formulas" >> "$REPORT"
    echo >> "$REPORT"
    echo '```' >> "$REPORT"
    brew autoremove -n 2>&1 || true
    echo '```' >> "$REPORT"
  else
    echo "- Homebrew not installed" >> "$REPORT"
  fi
  echo >> "$REPORT"
fi

# ========== DISK + ACTIONS ==========
if [[ "$MODE" == "full" ]]; then
  sort -u "$SAFE_LIST" -o "$SAFE_LIST" 2>/dev/null || true
  {
    echo "## Disk snapshot"
    echo
    echo '```'
    df -h / System/Volumes/Data 2>/dev/null || df -h /
    echo
    echo "Top-level home usage:"
    du -sh "$HOME"/* 2>/dev/null | sort -hr | head -20
    echo '```'
    echo
    echo "## Suggested next actions"
    echo
    echo "1. On developer machines: clear **Costly** hotspots (npm/pnpm/Xcode/Docker) after confirm — highest ROI."
    echo "2. Run \`bash scripts/safe_clean.sh\` (dry-run) then \`--apply\` for **Safe** tier only."
    echo "3. Dead LaunchAgents (missing binary): unload + \`trash\` plist."
    echo "4. Named uninstall: \`brew uninstall --cask --zap <token>\` when Homebrew-sourced."
    echo "5. APFS snapshots: \`tmutil thinlocalsnapshots /\` with a byte target — never blind-delete all."
    echo "6. If \`mo\` is installed: \`mo clean --dry-run\` / \`mo uninstall\` as optional acceleration."
    echo "7. Never touch paths in \`references/never_touch.md\`."
    echo
    echo "Safe-tier candidate list: \`$SAFE_LIST\`"
    echo
  } >> "$REPORT"
fi

echo "$REPORT"
