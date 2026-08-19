---
name: mac-clean
description: Scans macOS for apps, orphan leftovers, large caches, broken LaunchAgents, and Homebrew cruft; uninstalls apps the clean CLI way. Use when cleaning Mac storage, uninstalling apps, removing leftovers, or scanning junk.
---

# Mac Clean

macOS hygiene skill: **scan → classify by risk → propose → confirm → trash**. Learned from [macleanse](https://github.com/igornumeriano/macleanse) (risk tiers, denylist, dry-run) and [Mole](https://github.com/tw93/mole) (`--zap`, optional `mo` acceleration).

## Resolve scripts

```bash
SKILL_ROOT="${MAC_CLEAN_ROOT:-$HOME/.cursor/skills/mac-clean}"
# plugin install path (repo or ~/.cursor/plugins/local/mac-clean):
#   .../skills/mac-clean/
SCAN="$SKILL_ROOT/scripts/scan-mac-cleanup.sh"
SAFE="$SKILL_ROOT/scripts/safe_clean.sh"
if [[ ! -f "$SCAN" ]]; then
  SCAN="$(find "$HOME/.cursor/plugins/local/mac-clean" "$HOME/.cursor/skills/mac-clean" \
    -path '*/scripts/scan-mac-cleanup.sh' 2>/dev/null | head -1)"
fi
if [[ ! -f "$SCAN" ]]; then
  curl -fsSL "https://raw.githubusercontent.com/fengurt/mac-clean-skill/main/plugins/mac-clean/skills/mac-clean/scripts/scan-mac-cleanup.sh" \
    -o /tmp/scan-mac-cleanup.sh && chmod +x /tmp/scan-mac-cleanup.sh
  SCAN=/tmp/scan-mac-cleanup.sh
fi
```

Agent shortcuts:

```bash
bash plugins/mac-clean/skills/mac-clean/scripts/scan-mac-cleanup.sh full
bash plugins/mac-clean/skills/mac-clean/scripts/safe_clean.sh          # dry-run
bash plugins/mac-clean/skills/mac-clean/scripts/safe_clean.sh --apply  # after approval
```

## Risk tiers

| Tier | Meaning | Confirmation |
|---|---|---|
| **Safe** | Recreatable caches/logs/dead agents | One batch OK after dry-run |
| **Costly** | Dev artifacts (npm, Xcode, Docker, APFS snapshots) | Confirm per category — high ROI on developer Macs |
| **UserData** | Orphan prefs, media, vendor roots | Confirm per path; prefer archive over delete |

Denylist: [references/never_touch.md](references/never_touch.md)

## Hard rules

1. Scan before delete; show sizes; wait for approval.
2. Prefer **`trash`** over `rm -rf`. Never empty Trash unless asked.
3. Destructive scripts default to **dry-run**; require `--apply` or named paths.
4. Do not kill apps to force cache delete — skip in-use dirs or ask user to quit.
5. Never batch-delete denylist paths (Keychains, Photos libraries, iCloud Drive, VPN, password managers).
6. Close every cleanup with **space freed** + `df -h /`.

## Workflow A — Full scan

```bash
bash "$SCAN" full
# modes: full | apps | leftovers | caches | agents | brew | risk
```

Report: `$TMPDIR/mac-clean-scan/report.md`  
Safe candidates: `$TMPDIR/mac-clean-scan/safe_candidates.txt`

**ROI:** On developer machines, after one Safe batch, prioritize **Costly** (npm/pnpm/DerivedData/Docker/APFS) before chasing tiny prefs.

## Workflow B — Safe-tier clean

```bash
bash "$SAFE" --rescan     # dry-run list
# show table to user
bash "$SAFE" --apply      # only after explicit OK
```

## Workflow C — Uninstall one app

1. Detect source (`brew` / `mas` / `.app`).
2. Uninstall:

| Source | Command |
|---|---|
| Homebrew cask | `brew uninstall --cask --zap <token>` then `brew cleanup` |
| Homebrew formula | `brew uninstall <token> && brew autoremove` |
| Mac App Store | `mas uninstall <id>` |
| Drag-installed | `trash "/Applications/<Name>.app"` + Library sweep |

3. Leftover sweep with bundle ID from `Info.plist` + `mdfind`; unload dead LaunchAgents before `trash`.

## Workflow D — Optional Mole acceleration

Only if `command -v mo` succeeds — **do not install Mole unless the user asks**:

```bash
mo clean --dry-run
mo uninstall
```

## APFS snapshots (Costly)

```bash
tmutil listlocalsnapshots /
# after confirm — thin, do not delete all blindly:
tmutil thinlocalsnapshots / <bytes> 4
```

## Output format

```markdown
## Mac clean report
- Disk before: …
- Safe / Costly / UserData top items…

### Proposed deletions
| Tier | Path | Size | Why |

### After (if applied)
- Freed: …
- Disk after: `df -h /`
```

## Do not

- Third-party “Mac cleaner” junkware
- `sudo rm -rf` on Library trees
- Claim orphan detection is perfect — say “candidate”
- Delete WhatsApp/iMessage/Photos media with `rm`
