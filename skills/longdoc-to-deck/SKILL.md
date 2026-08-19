---
name: longdoc-to-deck
description: Long document to PPT material — chunk and skim, outline mindmap with zero loss, then page-by-page deck.json. Use when the user has a long MD/DOCX/PDF (tens of thousands of characters), wants 大纲 / mindmap / PPT 素材 / slide plan without HTML, or needs coverage that closes before md-to-html-slides.
---

# Long document → PPT material

Brand-agnostic. **Coverage ledger that closes**: every source unit maps to exactly one page, checked by script.

Do not emit HTML or CSS. Downstream HTML lives in `md-to-html-slides` via [adapters/md-to-html-slides.md](adapters/md-to-html-slides.md).

## Scripts (this skill)

| Script | Role |
|--------|------|
| [scripts/segment.py](scripts/segment.py) | Stage a — units + digest |
| [scripts/check-coverage.py](scripts/check-coverage.py) | Gates: `index` / `outline` / `deck` |
| [scripts/estimate-fit.py](scripts/estimate-fit.py) | Stage c — overfull / starved |
| [scripts/emit-pack.py](scripts/emit-pack.py) | Stage d — slide-plan + MANIFEST (no HTML) |
| [budgets.json](budgets.json) | Role fit budgets |
| [pagination.md](pagination.md) | Cohesion rules (load at stage c) |
| [schema/](schema/) | index + deck JSON schemas |

Work directory convention: `.work/<run-id>/` (or path the user names).

## Stage a — chunk and skim

**Completion criterion:** `index.json` + `index.md` exist; `check-coverage.py --stage index` exits 0; every table, fenced code block, and list run is a single unit (never split mid-structure).

```bash
python3 skills/longdoc-to-deck/scripts/segment.py "$DOC.md" -o "$WORK"
python3 skills/longdoc-to-deck/scripts/check-coverage.py --stage index --work "$WORK"
```

- Skim via `index.md` (one line per unit). Do not load the whole raw document into context when the digest suffices.
- Non-Markdown: convert first (`mineru-api` for PDF; Anthropic `docx` / related skills for Office), then segment the Markdown.
- Unit ids are stable `u-0001`… for this run. Full texts live in `units.json` for material extraction.

## Stage b — outline mindmap

**Completion criterion:** `outline.md` contains every unit id **exactly once**; `check-coverage.py --stage outline` exits 0 (`mapped == total`, zero orphans, zero duplicates). Non-zero exit **blocks** stage c.

Write `outline.md` as:

1. Nested markdown list mirroring the document structure
2. A mermaid `mindmap` (or flowchart) of major branches
3. Each leaf (or node) cites its unit ids inline, e.g. `口径 A（u-0182 u-0183）`

Prefer grouping by `heading_path` from the digest. Heading units may label branches; they still must appear once in the outline text.

```bash
python3 skills/longdoc-to-deck/scripts/check-coverage.py --stage outline --work "$WORK"
```

## Stage c — pagination

**Completion criterion:** Every unit assigned; cohesion rules in [pagination.md](pagination.md) applied; `estimate-fit.py` reports no **overfull** pages (fix starved by merging siblings under the same leaf — do not invent filler).

Read [pagination.md](pagination.md) and [budgets.json](budgets.json). Pick one of the twelve roles: `cover toc chapter readme statement kpi roster chart chart-table matrix compare verdict`.

Overflow: same role, `overflow_of` parent id, title suffix `续`.

## Stage d — emit

**Completion criterion:** `deck.json` validates against [schema/deck.schema.json](schema/deck.schema.json); one `pages/p-NNNN.md` per page; `check-coverage.py --stage deck` exits 0.

Page object shape:

```json
{
  "id": "p-0007",
  "role": "roster",
  "outline_path": ["肆 ABC 与二八", "口径 A"],
  "title": "口径 A：118 SKU 全量归属",
  "units": ["u-0182", "u-0183"],
  "overflow_of": null,
  "fit": { "chars": 780, "rows": 9, "budget": "roster:8-12", "verdict": "ok" },
  "material": { "bullets": [], "table": {}, "numbers": [], "quote": null },
  "source": "",
  "how_to_read": "",
  "takeaway": "",
  "notes": ""
}
```

Each `pages/p-NNNN.md` holds the human-readable material for that page (title, bullets/table markdown, source, takeaway) — complete module, no silent drops.

```bash
python3 skills/longdoc-to-deck/scripts/estimate-fit.py --work "$WORK" --write --fail-on overfull
python3 skills/longdoc-to-deck/scripts/check-coverage.py --stage deck --work "$WORK"
python3 skills/deck-audit/scripts/audit-source.py --work "$WORK"
python3 skills/deck-audit/scripts/audit-report.py --work "$WORK"
```

Hop1 (`deck-audit`) must exit 0 before the adapter. Structural coverage alone is not fidelity.

## After this skill

The **file pack is the completion**. Close it with:

```bash
python3 skills/longdoc-to-deck/scripts/emit-pack.py --work "$WORK"
```

That writes `slide-plan.json` (job + locked L3 `fill`), `pack.json`, and `MANIFEST.md`. Do not emit HTML here.

Later, Baslide01 development (`modules/baslide01`):

1. `md-to-html-slides` + `page-loop` from the slide-plan
2. Hop2: `python3 skills/deck-audit/scripts/audit-html.py --work "$WORK" --html "$DECK.html"` then `audit-report.py`
3. Surface hygiene: `page-audit`