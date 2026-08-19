# Ref audit · MD → HTML slide taxonomy

Source: `/Users/af/cpro01/0thebrain01/baslide01/ref` (7 files, 2026-08-14).
Goal: lock a **small HTML shell set** so a top model can write slot instructions and a cheaper model can fill templates without inventing layouts.

**Recommendation: 4 L1 shells × 12 L2 jobs × 16 L3 viz recipes.**
Do not ask the cheap model to pick among the workshop’s 17 `page-types.json` ids. Map those 17 onto this stack. Do not grow L2 past 12.

Related: [skills/md-to-html-slides](../skills/md-to-html-slides/SKILL.md) · [page-types.json](../page-types.json) · [templates/TIANSIGHT/layouts.html](../templates/TIANSIGHT/layouts.html)

---

## Verdict

| Question | Answer |
|---|---|
| How many **HTML slide types** should exist? | **4 shells** (the only CSS the cheap model copies) |
| How many **L1 / L2 / L3**? | **L1 = 4 shells · L2 = 12 jobs · L3 = 16 viz**. Tables are a mark on `body`, not a parallel fill layer |
| Also needed (not a slide type) | **5 document genres** (picks skin + density + whether SOURCE/HOW TO READ/TAKEAWAY are mandatory) |
| Workshop 17 types | Keep for Guizang/visual decks. For these MD reports, 5 of 17 never appear; 2 jobs are missing (`toc`, `readme`) |
| Gold deck | `清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` = **296 pages**, 4 CSS shells, **47 named figures**, **126 continuations (`续`)** |
| Two-model split | Top model emits a slide-plan JSON. Cheap model only clones `cover` / `divider` / `body` / `fig` and fills slots |

---

## Corpus inventory

| File | Bytes | Lines | H1 / H2 / H3 | MD tables | Role |
|---|---:|---:|---|---:|---|
| `清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` | 1,433,817 | 2,820 | — | 205 HTML tables | **Visual gold** (shells + 47 figs) |
| `清水亭_主辅佐引产品结构诊断报告 (4).md` | 294,234 | 3,696 | 17 / 100 / 73 | 164 | **Diagnosis source of truth** |
| `06_首版汇报报告_V1.0_数据校准版.md` | 130,017 | 2,199 | 15 / 79 / 66 | 118 | Strategy briefing |
| `07_战略方法论体系与分阶段赋能路线图_M1.0.md` | 94,058 | 1,725 | 14 / 59 / 97 | 73 | Method + staged roadmap |
| `侍天TIANSIGHT_分析体系Part1.md` | 84,198 | 1,367 | 9 / 49 / 36 | 74 | Analysis-point bible (A01–A58) |
| `08_北京西式快餐可参考品牌分析专项_B1.0.md` | 66,968 | 1,129 | 10 / 33 / 24 | 47 | Brand dossier |
| `苏帮袁_菜单分析维度体系_第一性原理.md` | 15,896 | 204 | 1 / 6 / 9 | 10 | Dimension-system seed |

No mermaid. No `![](image)` in any MD. Image-grid / image-hero / text-image are unused in this corpus.

---

## L0 · Document genre (5) — not a slide type

Top model picks this first. It sets skin, page budget, and which bars are mandatory.

| Id | When | Skin | Density | Bars |
|---|---|---|---|---|
| `diagnosis` | 清水亭-style product-structure report | TIANSIGHT 1440×810 | High (roster + fig) | SOURCE + HOW TO READ + TAKEAWAY required |
| `system` | 侍天 Part1 / 苏帮袁 method bible | TIANSIGHT | Medium | SOURCE required; takeaway = “what this unlocks” |
| `briefing` | 06 首版汇报 | TIANSIGHT or tableai | Mixed claim + table | TAKEAWAY required on data pages |
| `roadmap` | 07 赋能路线图 | TIANSIGHT or swiss | Statement + timeline + playbook | Gate / death-mode line required |
| `dossier` | 08 品牌专项 | TIANSIGHT | Profile cards + score matrix | Learn / don’t-learn pair required |

---

## L1 · HTML shells (4) — cheap model copies these only

Counted from the gold HTML (`class` on `<section>`):

| Shell | Gold class | n / 296 | Job |
|---|---|---:|---|
| `cover` | `slide cover` | 1 | Deck identity |
| `divider` | `slide divider` | 17 | Chapter cut |
| `body` | `slide` | 231 | Table, KPI, statement, TOC, verdict, continuation |
| `fig` | `slide figslide` | 47 | One named chart, 1320×500 SVG |

Chrome shared by every shell (do not invent): corner ticks `.tk.tl/tr/bl/br`, caption `.cap`, header `.hd` + `.chip`, source `.srcbar`, footer page index.

TIANSIGHT workshop `templates/TIANSIGHT/layouts.html` has **8 layouts**. Those are **L2 jobs bound onto these 4 shells**, not 8 extra CSS files.

| Workshop layout | Bind to L1 |
|---|---|
| `cover` | `cover` (deck) or `divider` (chapter) |
| `viz-full` | `fig` |
| `viz-table` | `fig` with side table **or** `body`+`chart-table` job |
| `viz-duo` | `fig` or `body` with `compare` job |
| `matrix-full` | `body` with `matrix` job (HTML grid, not a new shell) |
| `kpi-grid` | `body` with `kpi` job |
| `roster` | `body` with `roster` job |
| `verdict` | `body` with `verdict` job |

---

## L2 · Page jobs (12) — top model classifies each MD chunk

One job per page. Continuation is a **modifier** (`overflow: true`), not a 13th job. Gold deck: **126 / 296** titles contain `续`.

| Id | L1 shell | Use | Workshop 17 map |
|---|---|---|---|
| `cover` | cover | Who / what / for whom | `cover` |
| `toc` | body | Contents, 2 pages max | **missing** from 17 |
| `chapter` | divider | Act cut, no body text | `chapter` |
| `readme` | body | How to read, dual calibre, confidence | closest: `statement` |
| `statement` | body | One claim, or quote, or question | `statement` `quote` `question` |
| `kpi` | body | 3–6 big numbers | `kpi` |
| `roster` | body | Full list + **sum row** | `roster` |
| `chart` | fig | One decision, one figure | `chart` |
| `chart-table` | fig or body | Shape + executable names | `chart-table` |
| `matrix` | body | 九宫 / unlock / ABC migrate / score | `matrix` |
| `compare` | body | A vs B, dual calibre, stage vs stage, learn/don’t | `compare` `timeline` |
| `verdict` | body | Dispute / fact / handling / falsify, or decision list | `verdict` |

Folded on purpose (do **not** add L2):

- `quote` / `question` → `statement` + L3 variant
- `timeline` / `diagram` / brand profile / playbook stage card → `compare` or `roster` + L3 fill
- `text-image` / `image-grid` / `image-hero` → out of this MD corpus; keep in workshop for Guizang only

---

## L3 · Viz recipes (16) — pick by FT question, then named recipe

Cheap model must **call a named viz recipe**, or `null`. Tables are not recipes.

### Viz recipes (16) — FT Visual Vocabulary × gold 47 figs + 清水亭附录 E

| Id | Gold / appendix examples |
|---|---|
| `sankey` | 数据资产地图；角色错配 |
| `funnel` | 370→118 SKU；复购次数 |
| `waterfall` | 去重伪影；效益汇总 |
| `radar` | 数据完备度；3-4-2-1 达标 |
| `venn` | 框架重合；S1∩S2 |
| `bubble` | 六店定位；生命周期 |
| `hist-cdf` | 人均分布；价格带阶梯 |
| `pareto` | ABC 双轴 |
| `slope` | 双口径排名 |
| `diverging-bar` | 折让率；哑铃对照 |
| `quadrant` | 角色校验；高潜品；行动优先级 |
| `heatmap` | 待下架命中；味型×工艺；时段×品类 |
| `treemap` | 菜单结构树 |
| `network` | 连带图谱 |
| `line-dual` | 开台小时；月度活跃；替换事件 |
| `calendar` | 季节甘特 |

Aliases (do not add ids): violin→`hist-cdf`; boxplot→`hist-cdf`; dumbbell→`diverging-bar`; stacked bar→`hist-cdf` or `compare`; bump→`slope`; gantt→`calendar`; chord→`venn`; architecture tree→`treemap`; ridgeline→`hist-cdf`.

**Never 3D. Never rainbow heatmap.** Matrix cells use ready / degraded / blocked.

Pick `fill` by FT Visual Vocabulary question (Cotgreave / Smith, 2016), then one recipe:

| FT question | Recipes | Absent here |
|---|---|---|
| Magnitude | `bubble` `diverging-bar` | extra bar skins |
| Ranking | `pareto` `slope` | bump → `slope` |
| Distribution | `hist-cdf` `heatmap` | violin/boxplot → `hist-cdf` |
| Change over time | `line-dual` `calendar` | gantt → `calendar` |
| Part-to-whole | `treemap` `funnel` `waterfall` `venn` | pie / 3D |
| Flow | `sankey` `network` | chord → `venn` |
| Correlation | `quadrant` `radar` | — |
| Deviation | `diverging-bar` `waterfall` | dumbbell → `diverging-bar` |
| Spatial | — | maps |

### Tables are not a type layer

Gold: 231/296 pages are `slide` with a table inside. Stephen Few: table = lookup exact values; graph = see a relationship. Once the L2 job is `roster` / `kpi` / `matrix` / `compare` / `verdict`, the cheap model only needs that job’s row budget.

| L2 job | Budget |
|---|---|
| `roster` | 8–12 rows + `.sum` closes (not TOP10-as-all) |
| `kpi` | 3–6 cards |
| `matrix` | ≤9 cells, 3-state ink, zero≠gap footnote |
| `compare` | 2 columns shared unit, or 1–3 profile cards |
| `verdict` | 4 cells (争议/事实/处理/证伪) or a decision list |
| `chart-table` | side table ≤8 rows |
| body prose | ≤8 lines besides takeaway |

Retired as `fill` ids: `sum-roster` `kpi-cards` `state-matrix` `dual-calibre` `profile-card` `falsify-quad`.

---

## Gold HTML page audit

File: [清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html](清水亭_产品结构诊断_TIANSIGHT幻灯片%20(5).html)

Checklist from `skills/page-audit`:

| Code | Result | Note |
|---|---|---|
| ROOT | PASS | `#deck` + `.slide`, canvas 1440×810 |
| TITLE | PASS | `清水亭 主辅佐引产品结构诊断 · TIANSIGHT 侍天` |
| TOKEN | PASS | `--gold:#76551F`, Noto Serif SC, IBM Plex Mono, no Inter, no purple |
| HOME | FAIL* | No `a[href=/]` in file; workshop `serve.py` injects chrome when served |
| JS | WARN | Self-contained, **no** `TIANSIGHT.{registry,schema,viz,demo,app}.js` |
| ASSET | WARN | Google Fonts CDN only; 0 `<img>`, 0 data-URI; 47 inline SVG |
| LAYOUT | WARN | 4 shells, **not** `layout-viz-full` etc. |
| `data-page-type` | FAIL | 0 attributes vs workshop rule |
| SOURCE bar | PASS | 278 / 296 |
| HOW TO READ | FAIL | 6 / 296 |
| TAKEAWAY bar | FAIL | 16 / 296 (`.takebar`) |
| Continuation | WARN | 126 / 296 are `续` — pagination works, decisions fragment |
| Fig index | WARN | Chip order 24/25, 26/27, 37/38, 40/41 swapped |
| Divider | WARN | Appendix divider duplicated (slides 233 and 254) |

**Grade: B as visual gold, C vs current 8-layout + six-element spec.**

Use this file as the **shell and L3 recipe museum**. Do not clone its missing takeaway/how-to-read. New decks must restore the six elements from `demos/TIANSIGHT/docs/01_总纲_报告大纲与页面规范.md`.

Class distribution (L2-guess on gold):

| Guess | n |
|---|---:|
| table (single) | 119 |
| fig-chart | 47 |
| matrix-table | 37 |
| multi-table | 24 |
| text-body | 23 |
| verdict | 21 |
| chapter/divider | 17 |
| statement-short | 7 |
| cover | 1 |

---

## Per-file review

### 1 · `苏帮袁_菜单分析维度体系_第一性原理.md`

**Grade A (seed).** 204 lines. One H1, five dimension families (A 感官 / B 财务 / C 场景 / D 运营 / E 战略), three multi-dimension paradigms (matrix / scalar score / radar), crawl→walk→run roadmap, bibliography.

**Slide plan (~14–18 pages)**

| MD | L2 | L3 |
|---|---|---|
| Title + one-liner | `cover` | — |
| 一道菜 = 五个系统 | `readme` | `state-matrix` 5×3 |
| A–E families (one or two pages each) | `roster` | gap chips P0/P1/P2 |
| 40+ dimension vs 现状 | `matrix` | `heatmap` of coverage |
| 三种范式 | `compare` | three columns |
| 推荐分析 ①–⑤ | `roster` | — |
| Crawl/Walk/Run | `compare` | `calendar` or step list |
| 参考文献 | `roster` overflow | — |

**Audit:** No operating numbers except one seafood×roast example. Correctly refuses to enumerate C(40,2) matrices. This file is the **E-family / 君臣佐使** ancestor of 清水亭 M3 and 侍天 D2. Do not turn citations into quote walls.

---

### 2 · `侍天TIANSIGHT_分析体系Part1.md`

**Grade A (system bible).** 58 analysis points, 15 dimension families (6 live / 9 locked), dual calibre A/B, 13 modules, 7 periods, 8 trade types with 必做集.

This file is **not primarily a customer deck**. It is the instruction-generator’s registry: each A0x already implies L2 job + L3 fill + gate.

**Slide plan if converted (~90–110)**

- Cover + TOC + readme (calibre + three-path reconciling)
- D1–D6 live / D7–D15 locked → `matrix` unlock grid
- A01–A58: one `kpi` or `chart` spec page per ★★★★★ point; pack ★★★ into module summaries
- Part 5 method essays → `statement` + `diagram` fill (`treemap` / `network`)
- Part 6 dependency + forbidden ops → `compare` + `verdict`
- Part 7 calendar → `calendar`
- Part 8 global method map → `matrix` (do not expand L2)

**Audit:** Sample tables are 清水亭 numbers — keep denom on every page. QSR/茶饮 rows already say A06/A21/A28–A30 do not apply: top model must **drop jobs**, not invent a 13th type. Part 2/3 are “待启”; do not emit empty fig shells (gold ch.12 already shows the empty-template anti-pattern).

---

### 3 · `清水亭_主辅佐引产品结构诊断报告 (4).md`

**Grade A+ (diagnosis source).** 13 chapters + 阅读指南 + 附录 A–F. Fixed chapter shape: 数据来源 → 表 → 关键结论 → 推荐图表. Dual calibre. Appendix F is the A58 register (guide says 22 items; body grew to **F.1–F.34**).

**Slide plan:** gold already realized **296**. MD→HTML should land 280–320, not 90. The 90–140 “季报” in `01_总纲` is a **gated product**; this ref MD is the **full dump**.

| Chapter | H2 | Implied L2 mix |
|---|---|---|
| 序 阅读指南 | calibre table | `readme` |
| 0 数据地图 | assets, 370→118, quality | `roster` `funnel` `waterfall` `radar` |
| 1 框架对照 | 苏帮袁 vs 本次 | `compare` `venn` `treemap` |
| 2 基本盘 | 六店, 客单 | `kpi` `bubble` `hist-cdf` |
| 3 角色 | 校验 + 错配名单 | `quadrant` `sankey` `roster` |
| 4 ABC | dual calibre, full 118 | `pareto` `venn` `slope` `sum-roster` |
| 5 四指标 | 四象限 + 下架 | `quadrant` `heatmap` `sum-roster` |
| 6 结构树 | 3-4-2-1 | `treemap` `radar` |
| 7 倾向/价格 | 空档 | `heatmap` `hist-cdf` |
| 8 客单/小票 | 连带, 时段 | `network` `line-dual` `heatmap` |
| 9 复购 | 识别率 3.99% | `funnel` + **proxy watermark** |
| 10 九宫 | 味型×工艺/食材 | `heatmap` `state-matrix` |
| 11 季节 | 龙虾, 藕汤, 日历 | `line-dual` `calendar` |
| 12 商圈 | 空表 + 自身基准 | template `quadrant`, do not fake competitors |
| 13 行动 | P0/P1/P2 + 效益 | `quadrant` `waterfall` |
| 附录 A–E | full SKU lists | `roster` overflow |
| 附录 F | 争议四段 | `verdict` × ~20 (paginate) |

**Audit:** Reading guide and F disagree on controversy count (22 vs 34). Prefer F. Dual period (72d vs 30d) must travel in SOURCE. Full-name appendices are why `roster` + overflow exists — never TOP10 pretending to be 118.

---

### 4 · `清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html`

**Grade B visual / C spec.** See gold audit above.

**Reusable pieces:** 4 shells, corner ticks, caption letter-spacing, chip language (EN smallcaps + 章名), fig viewBox `0 0 1320 500`, compass SVG on cover/divider, continuation chip `.contd`.

**Do not reuse:** missing `data-page-type`, missing how-to-read/takeaway on ~95% of pages, fig number disorder, second appendix divider, inline SVG with no `opts.denom` object (denom is only in prose).

---

### 5 · `06_首版汇报报告_V1.0_数据校准版.md`

**Grade A (briefing).** V1.0 vs V0.1 changelog (6 corrected, 3 overturned, 1 strategic rewrite). Confidence A/B/C (~70/15/15). Beijing western set n=6,052. 12 parts + appendix.

**Slide plan (~140–180)** — more `statement` than diagnosis, fewer 118-row rosters.

| Part | Dominant L2 |
|---|---|
| 版本说明 | `compare` (V0.1 vs V1.0) |
| 阅读说明 | `readme` + `kpi` (data assets) |
| 1 战略全局 | `matrix` 价格带×天花板, `statement` 铁律, `compare` 四阶段 |
| 2 全市赛道 | `hist-cdf` `kpi` |
| 3 合生汇 | `roster` 场内9家, `statement` 定价锚, `verdict` 烤炉三决策 |
| 4 产品结构 | `matrix` 九宫重复, `kpi` 档口 |
| 5 首店菜单 | `roster` 主辅佐引, `verdict` 红绿灯 |
| 6 定价营销 | `compare` Shake Shack, `calendar` 开业 |
| 7 心智视觉 | `statement` + `compare` 品牌架构 (no photos in MD) |
| 8 动线点单 | `compare` 七节点 / 三梯队 (diagram fill) |
| 9 测试证伪 | `verdict` 七假设, `roster` 数据字典 |
| 10 连锁体系 | `compare` 工具包 |
| 11 当场决策 | `verdict` checklist |
| 12 未解 | `verdict` |
| 附录 / 一页纸 | `readme` `statement` |

**Audit:** Gaps listed in-file (no ticket-level POS, no absolute cost, floor unconfirmed). C-grade 人均测算 must watermark. Emoji heading markers (🥇🔴🆕) are MD emphasis — strip in HTML, use chips. Zero images: do not invent `image-hero` for 烤炉.

---

### 6 · `07_战略方法论体系与分阶段赋能路线图_M1.0.md`

**Grade A (roadmap).** Answers “what problem / which tools / what at each scale”. 24 frameworks, data-source layers L0–L5, PESTEL, 8 stages S0–S7 with gates and 典型死法, risk register, Stage-Gate governance.

**Slide plan (~100–140)**

| Part | L2 | L3 |
|---|---|---|
| 问题三层 | `statement` + `readme` | — |
| 24 frameworks | `roster` paginated, one `statement` per layer | — |
| 框架×阶段矩阵 | `matrix` | `state-matrix` |
| 数据源 L0–L5 | `compare` | — |
| PESTEL / 趋势 | `kpi` + `statement` | — |
| 竞争夹击 | `compare` | `quadrant` or `network` |
| Playing to Win 五问 | `verdict` five cells as roster | — |
| S0–S7 each | `compare` (playbook: 命题/动作/交付/死法/Gate) | `calendar` overview once |
| 指标 / 风险 / 治理 | `kpi` `roster` `verdict` | — |

**Audit:** Stage cards repeat. That is a **fill**, not a new L2 (`playbook` rejected). 07 uses “L0–L5” for **data sources** and 08 uses “L1–L3” for **brand filters** — never reuse those letters for slide shells. Keep slide layers named `shell` / `job` / `fill`.

---

### 7 · `08_北京西式快餐可参考品牌分析专项_B1.0.md`

**Grade A (dossier).** Brand-name normalization is the method contribution (Wagas 5 spellings → 53). Five evaluation dimensions including 复制稳定性 (CV% + rating σ). Three **filter** layers (direct / pattern / ceiling) — not slide L1/L2/L3.

**Slide plan (~80–110)**

| Part | L2 | L3 |
|---|---|---|
| 归一化阅读提示 | `readme` | `sum-roster` spellings |
| 五维度 + 三层筛选 | `kpi` `compare` | — |
| 规模总榜 / 价格带天花板 | `roster` `matrix` | `hist-cdf` |
| 六原型 | `statement` | — |
| 规律 1–5 | `chart` or `kpi` each | `hist-cdf` / `quadrant` |
| 标杆档案 C/B/D/E | `compare` | `profile-card` |
| 魏斯理 / 必胜汉堡 | `compare` | `profile-card` + `diverging-bar` |
| 可参考性评分 | `matrix` | `state-matrix` |
| 学 / 不学 / 验证 | `verdict` | `falsify-quad` |
| 监测机制 | `roster` | `calendar` |

**Audit:** 人均 is Dianping display, 5–15% low — SOURCE must say so. Comment counts are cumulative (old stores win). Beijing store count ≠ national. Independent burger table (38 stores) is a roster, not a chart.

---

## Estimated page budgets

| Source | Est. slides | Why |
|---|---:|---|
| 清水亭 MD | 280–320 | Gold = 296 |
| 06 汇报 | 140–180 | More claims, fewer 118-row lists |
| 07 路线图 | 100–140 | Repeating stage cards |
| 08 品牌 | 80–110 | ~12 profile cards + matrices |
| 侍天 Part1 as deck | 90–110 | One page per ★★★★★ A-point |
| 苏帮袁 | 14–18 | Method only |
| 侍天 季报 gated (docs) | 90–140 | Different product, not this dump |

---

## Two-model contract

```
MD
 → TOP MODEL: genre + slide-plan JSON (shell, job, fill, slots, overflow_of, row_budget)
 → CHEAP MODEL: clone L1 HTML, fill slots, no new CSS
 → page-loop (brand.md + type checks) → page-audit
```

Top model **must not** emit HTML.
Cheap model **must not** pick a new job or a new viz id.

Slide-plan fields: `id`, `genre`, `shell` (L1), `job` (L2), `fill` (L3 viz or null), `overflow_of`, `chips[]`, `title`, `source`, `how_to_read`, `takeaway`, `slots`, `falsify_id`.

Pagination: if a table exceeds row budget, emit `job` again with `overflow_of` pointing at the parent id and title suffix `续`. Gold proves this is the dominant pattern (42.6%).

---

## Gaps vs workshop 17

| Workshop id | In this corpus? | Action |
|---|---|---|
| cover chapter statement kpi chart chart-table matrix roster compare timeline diagram verdict | yes | Map into 12 jobs |
| quote question | rare | Fold into `statement` |
| text-image image-grid image-hero | **never** | Keep for Guizang; exclude from MD→HTML diagnosis pipeline |
| toc | yes in gold | **Add** as L2, do not wait for an 18th workshop type before generating |
| readme / how-to-read | yes in every MD | **Add** as L2 |
| overflow / 续 | 126 gold pages | Modifier, not a type |

---

## Original samples (template design)

Verbatim cuts from this corpus, one folder per type: [`skills/md-to-html-slides/samples/INDEX.md`](../skills/md-to-html-slides/samples/INDEX.md).

Complete one-file report (taxonomy + every sample): [`REPORT-md-to-html-slide-types.md`](REPORT-md-to-html-slide-types.md).

Every L2 job × 5 genres has at least one original excerpt. Folded surfaces (quote / question / timeline / diagram / playbook / profile) are in `samples/gaps.md`. Size each 1440×810 shell against the densest cut in `samples/job/<id>.md`.

---

## Do not

- Give the cheap model 17 or 40 layout names
- Treat 07 data-source L0–L5 or 08 filter L1–L3 as slide taxonomy
- Add a parallel L3 table taxonomy (`sum-roster` etc. are L2 jobs)
- Render empty competitor figs (ch.12)
- Hide n-below-threshold cells
- Mix Guizang classes into TIANSIGHT shells
- Let continuation pages drop SOURCE / denom
