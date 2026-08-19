# Skill Hub GUI

Local control panel for this skill monorepo. Zero npm dependencies — Node 20+ `node:http` only.

## Start

```bash
bash scripts/dev-up.sh
# or
bash gui/scripts/dev-up.sh
```

Opens **http://127.0.0.1:7979** (bind loopback only). Override with `PORT=…`.

Frees only port 7979 when the listener is this project's `server.js`.

## What it does

| Section | Role |
|---------|------|
| Home | Git branch / ahead-behind / dirty, skill counts, vendor freshness, gate strip |
| Skills | Gallery of authored + vendored skills (source, version, install targets), search, graph |
| Projects | First-class projects in `gui/data/projects.json` + template runner |
| Runs | `.work/<run>/` artifact viewer + audit inspector |
| Registry | `sources.yaml`, upstream drift check, symlink integrity |
| Jobs | Allowlisted pipelines with SSE logs |

## Safety

- Binds `127.0.0.1` only — no auth, no Docker in v1
- **No free-form shell** — every job step is named in `lib/templates.js`
- Path args must resolve under the repo or `ALLOWED_DOC_ROOTS` (default includes `~/cpro01/0thebrain01/baslide01`)
- `GET /api/file` refuses secret-like paths
- Writes only `gui/data/` and `.work/` — skills tree is read-only from the GUI

## Templates

- `longdoc-to-deck` — segment → coverage → **acceptance-bootstrap (mechanical draft)** → fit → hop1 audit
- `deck-audit-hop2` — `audit-html.py --dump-slides` → report
- `repo-sync` — sync-vendor → catalog → lint → scan-secrets
- `install-links` — symlink install map

Stages b (outline) and c (pagination) of `longdoc-to-deck` remain **agent/model stages**. The bootstrap step is labelled mechanical; copy the agent brief from the project/run view into Cursor to curate.

## Data

```
gui/data/projects.json   # gitignored
gui/data/jobs/*.json|log # gitignored
```

Gates in the Python scripts remain authoritative; the GUI is an observability and launch surface.
