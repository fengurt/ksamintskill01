# Skill Hub GUI

Local control panel for this skill monorepo. Zero npm dependencies — Node 20+ `node:http` only.
Pack downloads also require the system `zip` command (included with macOS).

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
| Skills | Starred, trending, and complete gallery views; capability map; source, version, search, export, and graph |
| Projects | First-class projects in `gui/data/projects.json` + template runner |
| Runs | `.work/<run>/` artifact viewer + audit inspector |
| Registry | `sources.yaml`, upstream drift check, symlink integrity |
| Jobs | Allowlisted pipelines with SSE logs |

## Safety

- Binds `127.0.0.1` only — no auth, no Docker in v1
- **No free-form shell** — every job step is named in `lib/templates.js`
- Path args must resolve under the repo or `ALLOWED_DOC_ROOTS` (includes `modules/baslide01`)
- `GET /api/file` refuses secret-like paths
- Writes only `gui/data/` and `.work/` — skills tree is read-only from the GUI

## Templates

- `long4hslides` — normalize source → build/audit GF page pack → explicit approval checkpoint → render/measure → hop2. Its internal slides stage is hidden from the template picker; former template ids remain hidden executable compatibility aliases for old projects and job reruns.
- `repo-sync` — sync-vendor → catalog → lint → scan-secrets
- `install-links` — symlink install map

`BASLIDE_ROOT` defaults to `modules/baslide01`.

Project detail shows (1) skills + stages and (2) pack outputs. Stages b (outline) and c (pagination) of `longdoc2mdpages` remain **agent/model stages**; bootstrap is a mechanical draft.

## Data

```
gui/data/projects.json   # gitignored
gui/data/jobs/*.json|log # gitignored
```

Gates in the Python scripts remain authoritative; the GUI is an observability and launch surface.

Starred skills can be exported as one zip. Extract the chosen folders into a
project's `.agents/skills/`, or into `~/.codex/skills/` for all Codex projects.

## Rich skill pages

Every skill detail page includes an overview and its complete file package. A skill can add richer tabs with a `showcase` path in flat `SKILL.md` frontmatter:

```yaml
metadata:
  author: ksamint
  origin: ksamint
  repository: fengurt/ksamintskill01
  showcase: showcase/showcase.json
```

Showcase manifest version 1 can declare an introduction, self-contained demo HTML, samples, semantic theme tokens, a deterministic Markdown lab, and validated generic controls. Presets are keyed by skill under ignored `gui/data/showcase-presets.json`; Export preset JSON is client-side. Referenced files must stay below the manifest directory, use `.html`, `.css`, `.md`, `.json`, or `.txt`, and remain under 2 MB.

HTML previews run in sandboxed `srcdoc` frames with network access disabled. GF4p2slides can generate a brand adapter ZIP from official brand-source metadata, semantic tokens, and an optional PNG, JPEG, or WebP logo. Generation uses temporary staging only; the GUI still writes only `gui/data/` and `.work/`.
