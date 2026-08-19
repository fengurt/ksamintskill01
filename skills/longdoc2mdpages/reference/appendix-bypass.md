# Appendix bypass

## Why this is the highest-leverage rule in the pipeline

In the delivered yun1980 deck, **217 of 382 pages (57%)** were mechanical
slices of four appendix tables. `A.1 老店 全单品明细` alone became 48 pages of
16-column, 10-row tables. Sixteen columns across a 2880px canvas leaves ~180px
per column, which is not enough for a Chinese dish name.

None of it was ever going to be read from a projector, and none of it needed
to be a slide.

## Trigger

A table takes the bypass when **any** holds:

- rows > 40
- columns > 7
- predicted height > 3 × the content band
- it is reached under an outline path containing 附录 / Appendix / 明细 / 全表

## What replaces it

```
appendix table  (468 SKU × 16 cols)
  │
  ├─ 1 slide   type: chart-table
  │            fig: pareto over the ranking column
  │            table: TOP-10, the 4 columns that carry the decision
  │            claim: what the concentration means
  │
  ├─ assets/tables/A1.json     全量 468 行 × 16 列, verbatim
  │
  └─ 1 slide   type: interactive
               embed: sortable / searchable / downloadable HTML table
               fallback_img: static TOP-30 render, used by PDF export
```

48 pages → 2 pages. The full data is still in the pack, still auditable, and
`gate_fidelity.py --assets` counts it as retained, so losslessness holds.

## Column selection for the on-canvas TOP-N

Keep at most 4 of the 16 columns, chosen in this order:

1. the entity name
2. the ranking measure (revenue, count)
3. the share or cumulative share — the column the claim is actually about
4. one diagnostic column, if the claim needs it (return rate, discount rate)

Everything else lives in the asset. A column that no claim on the page refers
to has no business on the canvas.

## The 续 rule for tables that legitimately stay

A table under the bypass threshold that still exceeds 12 rows splits normally:
same `type`, `overflow_of` set to the parent page id, title suffixed ` 续`,
`provenance.source` repeated on every continuation page, `claim` only on the
last one. `overflow_of` was null on all 382 pages of the delivered deck, which
left 48-page continuation runs with no structural relationship at all.
