# Taxonomy · 4 × 12 × 16

Machine file: [taxonomy.json](taxonomy.json). Do not add ids without updating both files.

Original content per type: [samples/INDEX.md](samples/INDEX.md). Complete one-file report: [`ref/REPORT-md-to-html-slide-types.md`](../../ref/REPORT-md-to-html-slide-types.md). Size templates against those cuts, not against invented lorem.

**Lock: 5 genres · 4 L1 shells · 12 L2 jobs · 16 L3 viz.** Tables are one mark family on `body`, not a parallel type layer.

## Genre (5)

| Id | MD shape | Bars |
|---|---|---|
| `diagnosis` | 清水亭 13-module dump | source + how_to_read + takeaway |
| `system` | 侍天 A01–A58 / 苏帮袁 dimensions | source + takeaway |
| `briefing` | 06 首版汇报 | takeaway on data pages |
| `roadmap` | 07 stages + gates | takeaway = gate or 死法 |
| `dossier` | 08 brand files | source + learn/don’t |

Skin for this corpus: **TIANSIGHT**, canvas **2880×1620** (v2). v1 gold HTML is 1440×810.

## L1 shells (4)

Copy classes only. Gold HTML n=296.

| Id | Class | n | Workshop layout |
|---|---|---:|---|
| `cover` | `slide cover` | 1 | `cover` (deck) |
| `divider` | `slide divider` | 17 | `cover` as 章扉 |
| `body` | `slide` | 231 | `kpi-grid` `roster` `matrix-full` `verdict` `viz-duo` |
| `fig` | `slide figslide` | 47 | `viz-full` `viz-table` |

Shared chrome: `.tk.tl/.tr/.bl/.br` `.cap` `.hd` `.chip` `.srcbar` `.takebar` footer index.

Fig default viewBox: `0 0 1320 500`.

A `<table>` lives on `body` (or the table half of `chart-table`). It is not a fifth shell.

## L2 jobs (12)

| Id | Shell | Classify when | Table budget | Workshop |
|---|---|---|---|---|
| `cover` | cover | First page | — | cover |
| `toc` | body | Contents (≤2 pages) | act list, no charts | — |
| `chapter` | divider | H1 / 第 N 章 | — | chapter |
| `readme` | body | 阅读指南, calibre, confidence | calibre table OK | statement |
| `statement` | body | One claim, quote, or question | — | statement quote question |
| `kpi` | body | 3–6 numbers | 3–6 cards | kpi |
| `roster` | body | Named list that must sum | 8–12 rows + `.sum` closes | roster |
| `chart` | fig | One figure, one decision | — | chart |
| `chart-table` | fig | Figure + executable names | side table ≤8 rows | chart-table |
| `matrix` | body | 九宫, unlock, score, ABC migrate | ≤9 cells; 3-state ink | matrix |
| `compare` | body | Dual calibre, A vs B, stages, learn/don’t, timeline, diagram | 2 cols or 1–3 profile cards | compare timeline diagram |
| `verdict` | body | 争议四段, 当场决策, 证伪 | 4 cells or a decision list | verdict |

Modifier, not a job: `overflow: true` + `overflow_of` + title `续`. Gold: 126/296.

Retired L3 table ids (do not use as `fill`): `sum-roster` → `roster`; `kpi-cards` → `kpi`; `state-matrix` → `matrix`; `dual-calibre` / `profile-card` → `compare`; `falsify-quad` → `verdict`.

## L3 viz (16) — pick by FT question, then recipe

Source: Financial Times Visual Vocabulary (Cotgreave / Smith, 2016). 附录 E names ~40 图表类型; those collapse here via aliases. `fill` is one of these ids, or `null`.

| FT question | Recipes | Do not add |
|---|---|---|
| Magnitude | `bubble` `diverging-bar` | extra bar skins; bubble area ∝ √size |
| Ranking | `pareto` `slope` | bump (alias → `slope`) |
| Distribution | `hist-cdf` `heatmap` | violin / boxplot / ridgeline (aliases → `hist-cdf`) |
| Change over time | `line-dual` `calendar` | gantt (alias → `calendar`) |
| Part-to-whole | `treemap` `funnel` `waterfall` `venn` | pie / 3D |
| Flow | `sankey` `network` | chord (alias → `venn`) |
| Correlation | `quadrant` `radar` | extra scatter skins; dashed median ≥ |
| Deviation | `diverging-bar` `waterfall` | dumbbell (alias → `diverging-bar`) |
| Spatial | — | maps; none in this MD corpus |

Ids: `sankey` `funnel` `waterfall` `radar` `venn` `bubble` `hist-cdf` `pareto` `slope` `diverging-bar` `quadrant` `heatmap` `treemap` `network` `line-dual` `calendar`

Aliases: violin/boxplot/ridgeline/stacked-bar → `hist-cdf`; dumbbell → `diverging-bar`; bump → `slope`; gantt → `calendar`; chord → `venn`; architecture → `treemap`.

No 3D. No rainbow. Matrix ink = ready / degraded / blocked.

A 3-state HTML grid is `matrix` (L2), not a 17th viz. Infographic surfaces (timeline, playbook, profile, architecture) are L2 `compare` / `roster` plus a viz fill.

## Workshop 17

Keep `text-image` `image-grid` `image-hero` for Guizang. They never appear in `ref/*.md`.
