# Fidelity rules

External reference for **stage 4** of `deck-audit`. Load only when adjudicating flagged pages.

## What is an anchor

An **anchor** must survive verbatim across hops. Prose may be summarized; anchors may not.

| Kind | Examples | Notes |
|------|----------|-------|
| number | `8720` `8,720` `40.840` | Normalize by stripping commas/spaces before compare; keep original for report |
| percent | `22.5%` `100％` | Fullwidth `％` ≡ `%` |
| currency | `¥12.3` `$4,500` | Keep currency symbol with value |
| ratio | `3:1` `1/4` | |
| date | `2024-03-01` `72 天` | Quantity-with-unit counts |
| quantity | `118 SKU` `6 店` | Digit + unit token |
| table-cell | non-empty cell text | Compare cell set, not layout |
| proper-noun | `颐堤港店` `口径 A` | 2+ CJK chars or Title Case runs not in stop list |

Stop list (not proper nouns): common function words and role labels (`封面` `续` `合计` `占比` `备注` and English `the` `and` `of` …).

## Findings

### Hard fail (script)

| Code | Meaning |
|------|---------|
| `MISS` | Anchor in a claimed source unit absent from page material |
| `ALTER` | Near-miss pair — same shape, different value (e.g. `8,720` vs `8,270`) |
| `INVENT` | Numeric or proper-noun anchor on the page absent from its units |
| `HMISS` | Anchor in page material absent from the mapped HTML slide text |

### Warn → model

| Code | Meaning | Adjudicate by |
|------|---------|---------------|
| `ORDER` | Ranked rows / list items reordered vs source | Confirm if ranking is a claim; accept if order is display-only |
| `DENOM` | Page shows %/ratio but dropped the 口径/denominator line its unit carried | Confirm if the takeaway needs the denom; accept if denom lives on an overflow sibling |
| `PROSE` | Prose drift without anchor loss | Confirm invented claim; accept paraphrase that preserves meaning |
| `HEXTRA` | HTML text not in page material (after chrome strip) | Confirm invented slide copy; accept template chrome / page numbers / skin labels |

## Adjudication checklist

For each flagged page:

1. Open only that page’s `units` texts and `pages/p-NNNN.md` (and the slide text for hop2).
2. For each warn: decide **confirm** (leave / escalate) or **accept**.
3. On accept, append to `accepted.json`:

```json
{ "page": "p-0007", "code": "DENOM", "anchor": "口径 A", "reason": "denom on overflow 续 page p-0008" }
```

4. Re-run the hop script; hard count must drop only via `accepted.json`, never by editing the script thresholds.
5. Do not invent missing anchors into the page to silence a `MISS` — send the producer skill to fix.

## Chrome and boilerplate (hop2)

Strip before comparing:

- `script` `style` `noscript`
- `#baslide-chrome` and `.baslide-chrome`
- Duplicate `.sd-rail` text when identical content appears in `#sd-explain`
- Lone slide indices (`1/296`) and skin watermarks listed in the deck’s template notes
