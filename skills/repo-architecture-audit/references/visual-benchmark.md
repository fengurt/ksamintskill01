# Visualization benchmark — how the review page is judged, and current numbers

The page is judged on two axes: **task coverage** (can a reviewer answer a concrete question from
the page without opening a CSV) and **scale behaviour** (does every view stay readable and
error-free as services/routes grow). Both are re-runnable; rerun after any change to
`scripts/build_html.py` and update the table below.

## A. Task rubric (12 reviewer questions)

Score per question: **2** = answered by a visual in ≤ 2 clicks · **1** = answerable only from a
table tab with filters · **0** = needs the CSV or the source.

| # | Reviewer question | Answering view (v2) | v1 | v2 |
|---|---|---|---|---|
| 1 | Which services call which, in which direction, how heavily | dependency graph (layered, width = log₂ calls) / adjacency matrix > 60 | 1 | 2 |
| 2 | Where are the call cycles | red edges + P0-3 badge | 2 | 2 |
| 3 | Which service / directory holds most code | LOC treemap | 0 | 2 |
| 4 | Which heavy directories have no stated responsibility | hatched cells (P2-2) | 1 | 2 |
| 5 | What does page X touch — which APIs, which tables | flow view, click a page | 1 | 2 |
| 6 | Who writes table Y, is it shared across services | flow view (dashed table) + cylinder node in graph | 1 | 2 |
| 7 | Which write routes have no guard | permission matrix (red rows first) + red outline in flow | 1 | 2 |
| 8 | Which guard / role sits on which route | permission matrix | 1 | 2 |
| 9 | Audit coverage per service, which routes are missing | stacked bars, click → list | 2 | 2 |
| 10 | Which fields drift in spelling / type, where exactly | naming clusters (chips per table, coloured by service) | 1 | 2 |
| 11 | How findings distribute over services × rules | risk matrix, click → filtered rows | 0 | 2 |
| 12 | What did the extractor miss, per service | coverage bars (scanned/skipped, rows per CSV, zero bars in red) | 1 | 2 |
| | **Total** | | **12 / 24** | **24 / 24** |

v1 = the first page (circle graph, three list columns, HTML heatmap, one bar chart). Scores are
self-assessed against the rubric definitions, not user-tested; treat them as a checklist, not as
evidence of usability.

## B. Scale benchmark

Data: `scripts/bench_synth.py <dir> --services N` (seeded, deterministic); render check with a
headless DOM (jsdom) — the numbers below are jsdom timings on one machine and only comparable
between rows of the same run. Real repos: the skill's synthetic 4-service repo and
`fastapi/full-stack-fastapi-template`.

| dataset | services | routes | links | page KB v1 → v2 | DOM nodes v1 → v2 | graph | flow nodes/ribbons | node overlaps | JS errors |
|---|---|---|---|---|---|---|---|---|---|
| synthetic 8 | 9 | 300 | 383 | 368 → 400 | 777 → 4248 | layered, 9 nodes / 14 edges, 1180 px | 60/71/64 · 308 | 0 | 0 |
| synthetic 40 | 41 | 1260 | 1355 | 1565 → 1597 | 2473 → 6684 | layered, 41 / 89, 2280 px (scrolls) | 60/71/71 · 303 | 0 | 0 |
| synthetic 120 | 121 | 3660 | 3752 | 4526 → 4558 | 6604 → 10624 | adjacency matrix (sparse: 318 cells) | 60/71/71 · 263 | 0 | 0 |
| demo repo | 4 | 15 | 15 | 51 → 83 | — | 4 / 5 + 1 shared table | 3/15/5 · 15 | 0 | 0 |
| fastapi template | 3 | 31 | 26 | 66 → 98 | — | 3 nodes, 0 resolved edges (stated on the page) | 8/23/2 · 26 | 0 | 0 |

Readability limits built into v2 (each is a deliberate cap, stated in the view caption or legend):
- dependency graph → adjacency matrix above 60 services; columns capped at ⌈√(1.4 n)⌉ ≤ 9,
  same-column calls drawn as side arcs, cycle-breaking back edges drawn above the row
- flow view → 70 nodes per column, rest aggregated into one "… N more" node by degree
- permission matrix → 200 rows (service filter) × 40 columns
- treemap → directories drawn to depth 2 only when the cell has ≥ 3600 px²; labels only when they fit
- tables → 3000 rows per draw

## C. How to rerun

```bash
python scripts/bench_synth.py /tmp/b40 --services 40 && python scripts/build_html.py /tmp/b40
# then open /tmp/b40/index.html; with node + jsdom available:
#   node geom.js /tmp/b40/index.html   (a ~30-line jsdom script that counts overlaps/errors per view)
```
For a visual check without a browser: serialise each `#content .view svg` from the jsdom DOM,
rasterise with cairosvg, and look at the PNGs — this is how v2 was reviewed.
