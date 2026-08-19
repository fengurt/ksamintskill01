# Sample library · original content per slide type

Cuts from `ref/` only. Prose is verbatim. SVG paths omitted. HTML tables truncated to 8 rows. Inline SVG omitted.

Regenerate: `python3 skills/mdpages2htmlslides/scripts/extract-samples.py`

## MECE map

| Layer | Ids | Folder |
|---|---|---|
| L2 jobs (12) + overflow | cover … verdict + overflow | `job/` |
| L3 viz (16) by FT question | sankey … calendar | `fill-viz/` |
| tables | not a type; row budget on L2 | `job/` Budget · headings; `fill-table/README.md` |
| folded / image-* empties | quote question timeline diagram playbook profile | `gaps.md` |

Lock: **5 genres · 4 L1 shells · 12 L2 jobs · 16 L3 viz**. `fill` is a viz id or `null`.

## Genre coverage of L2 jobs

| Job | n | diagnosis | system | briefing | roadmap | dossier |
|---|---:|---|---|---|---|---|
| `cover` | 7 | 1 md+1 html | 2 md | 1 md | 1 md | 1 md |
| `toc` | 6 | 1 md+1 html | 1 md | 1 md | 1 md | 1 md |
| `chapter` | 6 | 1 md+1 html | 1 md | 1 md | 1 md | 1 md |
| `readme` | 7 | 1 md+2 html | 1 md | 1 md | 1 md | 1 md |
| `statement` | 12 | 1 md+2 html | 2 md | 3 md | 2 md | 2 md |
| `kpi` | 12 | 4 md+2 html | 1 md | 2 md | 2 md | 1 md |
| `roster` | 11 | 4 md+2 html | 1 md | 2 md | 1 md | 1 md |
| `chart` | 9 | 1 md+3 html | 1 md | 2 md | 1 md | 1 md |
| `chart-table` | 8 | 2 md+2 html | 1 md | 1 md | 1 md | 1 md |
| `matrix` | 13 | 5 md+2 html | 2 md | 2 md | 1 md | 1 md |
| `compare` | 15 | 3 md+2 html | 2 md | 1 md | 3 md | 4 md |
| `verdict` | 15 | 5 md+3 html | 1 md | 2 md | 2 md | 2 md |

Every job × genre cell has at least one original cut. Gold HTML is tagged `diagnosis` because the 296-page file is the 清水亭 deck.

## How to use for template design

1. Open `job/<id>.md`. Every sample is one real page-worth of content.
2. Size the shell so the **densest** sample still fits 1440×810 with SOURCE + HOW TO READ + TAKEAWAY.
3. Open `fill-viz/<id>.md` for chart recipes. Pick FT question first, then one viz id per fig shell.
4. If a sample overflows, that is an `overflow` page, not a new type. See `job/overflow.md`.
5. Do not add an L2 because a sample looks unique (`playbook`, `profile`). Map it with `gaps.md`.
6. Do not add L3 table ids. Row budgets are on `kpi` `roster` `matrix` `compare` `verdict`.
7. Folded originals (quote / question / timeline / diagram / playbook / profile) are in `gaps.md`.
8. Complete one-file report: [`ref/REPORT-md-to-html-slide-types.md`](../../../ref/REPORT-md-to-html-slide-types.md).
