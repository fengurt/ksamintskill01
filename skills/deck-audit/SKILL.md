---
name: deck-audit
description: Proofread content fidelity across long-document → page material and page material → HTML slides. Use when the user asks to 校对 / audit a deck against its source, check for dropped numbers or invented claims, verify HTML slides match pages, or gate before publishing slides.
---

# Deck audit

Dedicated fidelity auditor. Do not produce decks or HTML in this skill; only inspect and report.

Boundaries:

- `longdoc-to-deck` / `check-coverage.py` — **structural** coverage (every `u-` id on exactly one page)
- **this skill** — **content fidelity** (anchors survive verbatim across hops)
- `page-audit` — HTML surface hygiene (assets, home nav, tokens). No content checks.

## Modes

| Mode | Inputs | Script |
|------|--------|--------|
| hop1 | `--work .work/<run>` (`units.json` + `deck.json` + `pages/`) | `audit-source.py` |
| hop2 | `--work … --html <deck.html>` | `audit-html.py` |
| degraded | `--source doc.md --html deck.html` (no unit ids; title/order map) | `audit-html.py` |

Work convention: write findings under `$WORK/` (or `--out`).

## Scripts

| Script | Role |
|--------|------|
| [scripts/extract-anchors.py](scripts/extract-anchors.py) | Stage 1 — `anchors.json` |
| [scripts/audit-source.py](scripts/audit-source.py) | Stage 2 — hop1 |
| [scripts/audit-html.py](scripts/audit-html.py) | Stage 3 — hop2 |
| [scripts/audit-report.py](scripts/audit-report.py) | Stage 5 — `audit.md` |
| [fidelity.md](fidelity.md) | Stage 4 — load only when adjudicating |
| [accepted.json](accepted.json) | Accepted drifts (page id + anchor) |
| [schema/audit.schema.json](schema/audit.schema.json) | Finding shape |

## Stage 1 — extract anchors

**Completion criterion:** `anchors.json` exists with `source` (per unit id) and `material` (per page id) sides; every page in `deck.json` has a material entry.

```bash
python3 skills/deck-audit/scripts/extract-anchors.py --work "$WORK"
```

## Stage 2 — hop1 (source → pages)

**Completion criterion:** `audit-source.json` written; exit 0 only when there are zero hard findings (`MISS` `ALTER` `INVENT`) after applying `accepted.json`.

```bash
python3 skills/deck-audit/scripts/audit-source.py --work "$WORK"
```

Hard fails block the adapter. Warns (`ORDER` `DENOM` `PROSE`) go to stage 4.

## Stage 3 — hop2 (pages → HTML)

**Completion criterion:** `audit-html.json` written; every `section.slide` mapped to a page (or listed under `unmapped`); exit 0 only when zero `HMISS` after `accepted.json`.

```bash
python3 skills/deck-audit/scripts/audit-html.py --work "$WORK" --html "$DECK.html"
```

Slide→page map: `data-page-id` → element `id` → title match → document order. Ambiguities are reported, never guessed silently.

## Stage 4 — model adjudication

**Completion criterion:** Every warn finding in `audit-source.json` / `audit-html.json` is either confirmed (promote to hard / leave as fail) or accepted into `accepted.json` with a one-line reason. Load [fidelity.md](fidelity.md) for this stage only. Do not re-read the whole source — open only the flagged page’s units and material.

## Stage 5 — report

**Completion criterion:** `audit.md` exists; failures first; counts match the JSON files.

```bash
python3 skills/deck-audit/scripts/audit-report.py --work "$WORK"
```

## After this skill

- hop1 pass → continue `longdoc-to-deck` adapter → `md-to-html-slides`
- hop2 pass → continue `page-audit` for surface hygiene
