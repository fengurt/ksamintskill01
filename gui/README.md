# Skill Hub GUI

Local control panel for this skill monorepo. Zero npm dependencies — Node 20+ `node:http` only.
Pack downloads also require the system `zip` command (included with macOS).

## Start

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/mdpages2htmlslides/requirements.txt
bash scripts/dev-up.sh
# or
bash gui/scripts/dev-up.sh
```

Opens **http://127.0.0.1:7979** (bind loopback only). Override with `PORT=…`.
The launcher automatically uses `.venv/bin/python` when present; `PYTHON=…` remains an explicit override.

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

Every skill detail page includes an overview and its complete file package. A skill can add a combined Guideline workspace plus a Markdown test lab with a `showcase` path in flat `SKILL.md` frontmatter:

```yaml
metadata:
  author: ksamint
  origin: ksamint
  repository: fengurt/ksamintskill01
  showcase: showcase/showcase.json
```

Showcase manifest version 1 can declare an introduction, self-contained demo HTML, samples, semantic theme tokens, a deterministic Markdown lab, and validated generic controls. Demo, samples, and theme controls share the Guideline tab. Presets are keyed by skill under ignored `gui/data/showcase-presets.json`; Export preset JSON is client-side. Referenced files must stay below the manifest directory, use `.html`, `.css`, `.md`, `.json`, or `.txt`, and remain under 2 MB.

HTML previews run in sandboxed `srcdoc` frames with network access disabled. GF4p2slides reads official public themes and canonical raster logos from `https://apuch.art`, then caches them in ignored `gui/data/apuch-themes.json`. An optional root `.env` can hold `APUCH_ADMIN_API_KEY`; the browser receives only a configured/not-configured flag, and public theme sync never sends the key. GF4p2slides can generate a brand adapter ZIP from official brand-source metadata, semantic tokens, and an optional PNG, JPEG, or WebP logo. Generation uses temporary staging only; the GUI still writes runtime artifacts only under `gui/data/` and `.work/`.
