# Adapter: deck.json → GF deck-plan.json

`emit-pack.py` performs this deterministic enrichment. Rename and structure fields; never re-chunk after coverage has closed.

## Inputs and output

- Input: `$WORK/deck.json`, `$WORK/pages/p-NNNN.md`, and `$WORK/units.json`
- Output: `$WORK/deck-plan.json`
- Genre: `diagnosis | system | briefing | roadmap | dossier`
- Theme: one of the five Baslide themes; `TIANSIGHT` by default

## Field map

| deck.json | deck-plan.json |
|---|---|
| file `source` | top-level `source` |
| `pages[]` | `pages[]` |
| `role` | `template` |
| `title` | `title` |
| `source` | `source` |
| `takeaway` | `takeaway` |
| selected L3 fill | `visualization` |
| `layout`, `overflow_of`, `units` | same keys |
| density choice | `pack: air | mid | tight` |
| `material.bullets` / `material.table` | typed `content.blocks` |
| `outline_path`, `how_to_read` | `outline_path`, `provenance` |

The public page grammar is the twelve GF jobs: `cover toc chapter readme statement kpi roster chart chart-table matrix compare verdict`. Translate legacy downloaded names only at the boundary: `quote→statement`, `playbook→verdict`, `gallery→roster`, `interactive→chart`.

## Output shape

```json
{
  "contract_version": "1.0.0",
  "title": "Report",
  "mode": "slide",
  "source": "path/to/report.md",
  "genre": "diagnosis",
  "theme": "TIANSIGHT",
  "pages": [{
    "id": "p-0007",
    "template": "roster",
    "title": "口径 A：118 SKU 全量归属",
    "source": "source.md · u-0182 u-0183",
    "takeaway": "Every SKU has one accountable destination.",
    "visualization": null,
    "layout": "table-full",
    "pack": "mid",
    "units": ["u-0182", "u-0183"],
    "overflow_of": null,
    "content": {"blocks": [{"kind": "table", "columns": [], "rows": []}]}
  }]
}
```

## Rules

1. Do not invent a 13th page template or 17th visualization.
2. Do not merge or split pages here; fix pagination upstream and rerun coverage.
3. Preserve `units`, `source`, and `overflow_of`; hop2 depends on deterministic page identity.
4. Run fidelity and schema gates before approval. After approval, render once, measure with Chrome, then run hop2.
5. `deck.json` and `slide-plan.json` remain read-only renderer fallbacks for old work.
