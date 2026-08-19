# Adapter: deck.json → md-to-html-slides slide-plan

Maps brand-agnostic `longdoc-to-deck` output to the slide-plan schema in `md-to-html-slides` / `pipeline.md`. **Rename and enrich — do not re-chunk.** Coverage already closed upstream.

## Inputs

- `$WORK/deck.json`
- `$WORK/pages/p-NNNN.md` (slot prose)
- User (or genre detection): `genre` ∈ `diagnosis | system | briefing | roadmap | dossier`
- Skin: usually `TIANSIGHT` for those genres

## Field map

| deck.json | slide-plan |
|-----------|------------|
| (file) `source` | `source` |
| — | `genre` (add) |
| — | `skin` (add; default `TIANSIGHT`) |
| `pages[]` | `slides[]` |
| `id` | `id` |
| `role` | `job` |
| — | `shell` from job→shell map below |
| — | `fill` L3 viz id or `null` (only when job is chart / chart-table / matrix needs viz; else `null`) |
| `overflow_of` | `overflow_of` |
| `title` | `title` |
| `outline_path` | optional `kicker` = joined path or last segment |
| `source` / `how_to_read` / `takeaway` | same keys (required on diagnosis data slides) |
| `material.table` | `slots.columns` / `slots.rows` / `slots.sum` |
| `material.bullets` | `slots.bullets` or body text |
| `units` | keep on the slide as `data-units` (space-separated); also optional under `notes` |

## Job → shell

| job (role) | shell |
|------------|-------|
| cover | cover |
| chapter | divider |
| chart / chart-table | fig |
| toc / readme / statement / kpi / roster / matrix / compare / verdict | body |

## Genre bars

From `md-to-html-slides` taxonomy:

- diagnosis: `source`, `how_to_read`, `takeaway`
- system / dossier: `source`, `takeaway`
- briefing / roadmap: `takeaway`

Copy those fields from each page; if missing on a required genre slide, fill from `pages/p-NNNN.md` before handing to the cheap model.

## HTML attributes (required for deck-audit hop2)

On every emitted `<section class="slide …">`:

- `data-page-id="p-NNNN"` — same as slide-plan `id`
- `data-units="u-0001 u-0002"` — space-separated unit ids from `deck.json` (omit when empty)

These let `deck-audit` map slides deterministically instead of falling back to title/order.

## Output shape

```json
{
  "source": "path/to/report.md",
  "genre": "diagnosis",
  "skin": "TIANSIGHT",
  "slides": [
    {
      "id": "p-0007",
      "shell": "body",
      "job": "roster",
      "fill": null,
      "overflow_of": null,
      "kicker": "肆 · ABC 与二八",
      "title": "口径 A：118 SKU 全量归属",
      "source": "…",
      "how_to_read": "…",
      "takeaway": "…",
      "units": ["u-0182", "u-0183"],
      "slots": { "columns": [], "rows": [], "sum": [] }
    }
  ]
}
```

## Rules

1. Do not invent a 13th job or a 17th viz id.
2. Do not merge or split pages here — fix upstream and re-run coverage.
3. Overflow title suffix `续` must already be present from pagination.
4. After emit: `md-to-html-slides` fill → `page-loop` → `deck-audit` hop2 → `page-audit`.
5. Do not drop `units` / `data-page-id` — hop2 needs them.