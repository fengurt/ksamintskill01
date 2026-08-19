# Pagination cohesion rules

External reference for **stage c** of `longdoc2mdpages`. Load only when paginating.

## Positive rules (do these)

1. **One decision per page.** Title names the decision or finding; takeaway states it in one sentence.
2. **Table travels with its caption, denominator, and takeaway.** Caption + column headers + body rows + sum/denom + how_to_read stay on the same page family. If rows exceed the role budget, emit overflow pages (`overflow_of`, title suffix `续`) that repeat SOURCE/denom; put TAKEAWAY only on the last overflow page.
3. **Claim travels with its evidence.** A prose claim and the list/table/number-block that supports it stay together. Prefer one page over a claim page plus an orphan evidence page.
4. **Numbered sequences stay whole.** Steps 1…n of a procedure, timeline, or ranked list share a page (or an overflow chain) — never cut between step k and k+1 unless the budget forces overflow at a unit boundary.
5. **Splits land on unit boundaries only.** Never invent a mid-unit cut. Use unit ids from `index.json`.
6. **Heading units set structure.** `kind: heading` becomes chapter/toc scaffolding or `outline_path` crumbs — do not leave heading-only pages unless the heading is a true chapter divider (`role: chapter`).
7. **Same-heading siblings cohere.** Units under the same `heading_path` leaf prefer the same page or a contiguous overflow chain before mixing with a different leaf.

## Fit (use `budgets.json` + `estimate-fit.py`)

- **overfull** — chars/rows/bullets above role max → split at unit boundary or start overflow.
- **starved** — far below role min with leftover sibling units under the same leaf → merge; do not invent filler and do not split a cohesive block into thin pages.
- **ok** — within min/max.

## Role picker (same 12 as mdpages2htmlslides L2 jobs)

| Role | Reach for when |
|------|----------------|
| cover | Title / meta / audience |
| toc | Act or section list |
| chapter | Act divider |
| readme | How to read this deck / calibre |
| statement | Single claim or quote-led beat |
| kpi | 3–6 metric cards |
| roster | Row list that must close (SKU, SKU sum, checklist with total) |
| chart | Viz-led finding |
| chart-table | Viz + side table ≤8 rows |
| matrix | ≤9 cells, state grid |
| compare | Two columns / profiles / before-after |
| verdict | Decision list / falsify quad |

## Overflow convention

Matches `mdpages2htmlslides` pipeline:

- Keep the same `role`
- Set `overflow_of` to the parent page `id`
- Append `续` to `title`
- Repeat SOURCE and denominator; TAKEAWAY only on the last page of the chain
