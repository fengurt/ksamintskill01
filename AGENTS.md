# Agent notes for ksamintskill01

## Source of truth

- Authored skills live under `skills/<name>/` with a `SKILL.md`.
- Do not edit copies under `~/.cursor/skills`, `~/.claude/skills`, or `~/.codex/skills` when those paths are symlinks into this repo. Edit here, then re-run `scripts/install-links.sh` if needed.
- Never commit `vendor/` — it is produced by `scripts/sync-vendor.sh`.

## longdoc-to-deck

Zero-loss is enforced by a **coverage ledger that closes**:

1. `segment.py` → `index.json` + `index.md`
2. Agent writes `outline.md` (every unit id once) → `check-coverage.py --stage outline`
3. Agent paginates into `deck.json` + `pages/` → `check-coverage.py --stage deck` and `estimate-fit.py`
4. Optional adapter → `md-to-html-slides` slide-plan JSON

Do not emit HTML or CSS from `longdoc-to-deck`.

## Secrets

Before committing skills that mention 1Password, private hosts, or API keys, run:

```bash
bash scripts/scan-secrets.sh skills/
```

Any plaintext key blocks the commit.

## Catalog

After adding or renaming a skill:

```bash
python3 scripts/build-catalog.py
```
