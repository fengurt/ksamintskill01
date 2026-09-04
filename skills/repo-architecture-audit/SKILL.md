---
name: repo-architecture-audit
description: Evidence-first architecture audit of any codebase (any language, mono-repo or multi-repo, single or multi-service). Runs a stdlib-only extractor that produces six MECE CSV inventories (structure, page/API/job routes, data models, permission points, audit points, cross-service calls), derived page→API→table links, rule-based P0/P1/P2 findings with file:line evidence, and a single-file offline admin-only HTML review page (dated, commit/PR-stamped, five visual views, editable annotations). Use this skill whenever the user asks to review, audit, map, document, or understand a repo's architecture, its page-to-API-to-table relationships, field/naming consistency, permission or audit-logging coverage, service dependencies, or wants to "see the whole structure" before a refactor or redesign — even if they only say "look at this repo", "list the pages and APIs", or "which endpoints have no auth".
metadata:
  author: ksamint
  origin: ksamint
  repository: fengurt/ksamintskill01
---

# Repo Architecture Audit

Turn a codebase of any size into a reviewable, diff-able, evidence-linked inventory, then a visual
admin page, then (only when asked) cross-service reconciliation and a decision list. "Read the repo
and tell me the architecture" fails on large projects: the model samples, sampling misses, and prose
conclusions cannot be checked. Here every output line traces to `file:line`.

## Core principles (every stage)

1. **Facts before judgment.** Stage 0 records what the code *does*. Opinions are Stage 3 only, and each
   cites Stage 0/2 rows.
2. **Evidence or blank.** Every row carries `file` and `line`. What cannot be located stays empty and is
   counted in `skip_reasons`. Never fill a cell by inference, never hand-write a CSV row.
3. **MECE inventory.** Each code artifact lands in exactly one of six dimensions. If something fits two,
   the pattern is wrong; fix the pattern, not the row.
4. **Visualization first.** The HTML page is the reading surface; the CSVs are the truth behind it.
   Every view is captioned with its source CSV and derivation rule and degrades to its table.
5. **Idempotent and diff-able.** Two runs on one commit give identical CSVs (only `generated_at`
   differs). Human notes live in `annotations.json`, keyed by stable composite keys, merged on rebuild.
6. **No secrets.** `.env*`, key files, credentials are excluded from every artifact.

## The six MECE dimensions

| # | Dimension | Question | Artifact |
|---|---|---|---|
| 1 | Structure | Where does code live, what is each area for | `tree.csv` |
| 2 | Entry points | How is code invoked: page route, API route, scheduled job | `routes.csv` |
| 3 | Data | What is persisted, with which fields/types (DTOs excluded) | `models.csv` |
| 4 | Access control | Who may invoke what | `permissions.csv` |
| 5 | Audit / observability | What gets recorded when something happens | `audit_points.csv` |
| 6 | Boundaries | Who talks to whom across service lines | `cross_calls.csv` |

Derived, not a seventh dimension: `links.csv` (page→API, API→API, API→table), `priorities.csv`,
`manifest.json` (provenance + coverage). Column contracts: `references/schemas.md`.

## Workflow

### Stage 0 — Inventory (scripted; always first)

1. Locate the repo(s). For a multi-repo system, clone/mount them under one parent and pass that as
   root — each repo becomes a service.
2. Run:
   ```bash
   python <skill-path>/scripts/audit.py <root> --out <root>/docs/audit --project-name "<name>"
   ```
   Flags: `--services api=services/api,web=apps/web` (override detection) ·
   `--service-alias api=backend|gateway` (hostnames used in URLs) ·
   `--patterns <root>/docs/audit/patterns.local.json` (auto-loaded if present) ·
   `--rules …/rules.local.json` · `--pr-url-template "https://github.com/org/repo/pull/{pr}"` ·
   `--max-depth 3` · `--no-html`.
3. Read the JSON summary / `manifest.json` and report, in this order, then **stop and wait**:
   - services: name, path, `detected_by`, frameworks; ask the user to confirm the list
   - rows per CSV per service; `files_scanned` / `files_skipped` with top skip reasons
   - count of `cross_calls` with `to_service_confidence = low`
   - services with empty `routes` or `models` and which framework is likely unsupported
   - the known limits that apply (see `references/extractors.md` § Known limits)
4. If a stack is not covered, add regexes to `docs/audit/patterns.local.json` (never edit the bundled
   file), rerun, report the delta. Do not read files by hand to fill gaps.
5. Idempotence check when the user will diff runs: run twice on a clean tree; `diff -r` on the CSVs
   must be empty.

Give no architectural opinion in this stage, even if asked in passing — say it comes in Stage 3.

### Stage 1 — Service cards (from CSVs only)
One card per service, fixed fields (`references/stage-templates.md` §1). Cite row keys; unknown
stays "not in inventory".

### Stage 2 — Cross-service reconciliation
In this order (`references/stage-templates.md` §2): core business chains the user names (hop by hop
through `links.csv` / `cross_calls.csv`, gaps recorded not filled) → field dictionary (from
`models.csv` + P1-2) → permission matrix (role × resource × operation) → audit coverage matrix
(every write route × audit point).

### Stage 3 — Decision list
Only now: findings ranked by severity × change cost, each with evidence keys, blast radius and
2–3 options with trade-offs (`references/stage-templates.md` §3). The owner decides.

## Priority rules — tiers, not weighted scores

A weighted score cannot explain itself; a rule tier can. IDs are fixed; thresholds live in
`scripts/rules.json` (override via `docs/audit/rules.local.json`, committed to git).

| Level | ID | Rule |
|---|---|---|
| P0 | P0-1 | Write-method route (POST/PUT/PATCH/DELETE, ANY) with no guard; explicit `!Public`-style markers are reported as "explicitly public" |
| P0 | P0-2 | Same table declared in ≥2 services (adds `db_shared` rows to `cross_calls`) |
| P0 | P0-3 | Cycle in the service call graph (confidence ≥ medium) |
| P1 | P1-1 | Write-method route whose file contains no audit point |
| P1 | P1-2 | Same normalized field name with ≥2 spellings, or same name with ≥2 declared types |
| P1 | P1-3 | `fk_to` targets a table absent from `models.csv` |
| P1 | P1-4 | `ROLE_*`/`PERM_*` constant defined but never referenced, or referenced but never defined |
| P2 | P2-1 | Cross call with `to_service_confidence = low` |
| P2 | P2-2 | Directory at depth ≤ N in the top X % by LOC with empty `responsibility` |

Each row points to `evidence_file` + `evidence_row`; a hit that cannot be located is not emitted.
P1-2 over-reports on purpose: the reviewer writes `fp …` / `not a conflict` in the note, the next
build marks it `suppressed`.

## The HTML review page (`docs/audit/index.html`)

Built automatically by `scripts/build_html.py`. Check the output against this list instead of
re-specifying it:
- Single file, inline CSS/JS, no CDN, opens offline; `noindex,nofollow`; INTERNAL / ADMIN ONLY banner.
- Header: project, generated (UTC + local), short SHA (click → full), branch, tag/describe, service
  versions, PR number (linked with a template) or `null` with the reason, dirty-tree warning.
- Todo panel: P0 / P1 / P2 counts, services, unresolved cross calls, write routes without guard —
  each click opens the filtered table. A jump bar links to every view.
- Eight views, each captioned "source · rule", each with a `↓ svg` export, each degrading to its
  table when it cannot render (`references/visual-benchmark.md` lists the caps):
  1. **Risk matrix** — services × rule ids, shaded by count, click → filtered priorities.
  2. **Service dependency graph** — layered left→right (cycle-breaking + longest-path + barycenter
     ordering), node = service with LOC / route count and P0 / P1 badges, edge width = log₂ calls,
     red = cycle, dashed = low confidence, shared tables as cylinder nodes; hover isolates neighbours,
     click → routes of that service; > 60 services → sparse adjacency matrix.
  3. **Code structure treemap** — squarified, area = LOC, service → directory (depth ≤ 2), hatched
     red = P2-2; click → Structure tab.
  4. **Page → API → Table flow** — three-column sankey from `links.csv`, node height = links, colour =
     service, red outline = P0-1, orange dot = P1-1, dashed = shared table, grey = no link, api→api
     as dashed arcs; click traces a chain and shows the upstream/downstream list.
  5. **Permission matrix** — API routes × guard mechanisms / role literals; unguarded writes first in
     red; explicit public markers in red; service filter.
  6. **Audit coverage** — stacked bars per service, click lists the unaudited write routes.
  7. **Field naming & type drift** — one block per P1-2 cluster, chips per table coloured by service.
  8. **Extractor coverage** — scanned/skipped bars and rows-per-CSV mini bars (zero in red).
- Tables: sort, filter, service / level / rule / confidence switches, CSV download; `note` and
  `responsibility` cells editable; export / import `annotations.json`; the build merges
  `docs/audit/annotations.json`.

**Visibility** — ask, default A:
- A. Keep `docs/audit/` out of build artifacts and deploy ignore rules; read it from the repo.
- B. Serve at an existing admin route (e.g. `/admin/audit`) behind the existing super-admin guard,
  404 otherwise. Then that route must itself appear in `routes.csv` with its guard.

## Where things go wrong — check before reporting

- Empty `routes.csv` for a service → framework not in `patterns.json`; add a local pattern.
- File-based routers (Next/Nuxt/SvelteKit) are found by path; the service path must contain
  `pages/`, `app/` or `routes/`.
- Route prefixes are composed only within the same file (`APIRouter(prefix=)`, `@Controller`,
  `[Route]`); `include_router(prefix=)` / `app.use("/v1", r)` elsewhere are not — say so.
- Guard detection is keyword-based (`auth`, `role`, `permission`, `depends`, `current_user`, …);
  a project with its own vocabulary needs `guard_keywords` in the local pattern file.
- `to_service` resolves by URL host / package name = service name; otherwise pass `--service-alias`.
- Test directories are counted in `tree.csv` but not extracted; tests calling their own API are not
  cross calls.
- PR number exists only in CI env vars or via `gh pr view`; `null` locally is normal.

## Files
- `references/schemas.md` — column contracts (read before touching scripts or writing Stage 1–3).
- `references/extractors.md` — per-framework coverage, `patterns.local.json` format, known limits.
- `references/stage-templates.md` — Stage 1/2/3 output templates.
- `references/visual-benchmark.md` — the 12-question rubric and scale numbers the page is judged
  against; rerun after changing `build_html.py`.
- `scripts/audit.py` (extractor + rules + manifest) · `scripts/build_html.py` (page) ·
  `scripts/patterns.json` (bundled patterns) · `scripts/rules.json` (thresholds) ·
  `scripts/bench_synth.py` (synthetic audit dir at any scale, for page benchmarks).
