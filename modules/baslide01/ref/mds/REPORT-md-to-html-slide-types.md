# MD → HTML slide types · complete sample report

One file. Taxonomy lock + original content per type. Prose is verbatim from `ref/`. SVG omitted. HTML tables truncated to 8 rows.

- Date: 2026-08-14
- Canvas: **1440×810** · skin **TIANSIGHT**
- Lock: **5 genres · 4 L1 shells · 12 L2 jobs · 16 L3 viz**
- Tables: one mark family on `body` (row budget lives on the L2 job, not a parallel type layer)
- Viz pick: FT Visual Vocabulary question → one of 16 recipes (or `null`)
- Per-type files (regenerable): `skills/mdpages2htmlslides/samples/`
- Regenerator: `python3 skills/mdpages2htmlslides/scripts/extract-samples.py`
- Audit companion: [`AUDIT-md-to-html-taxonomy.md`](AUDIT-md-to-html-taxonomy.md)

Size each template so the **densest** sample in that type still fits SOURCE + HOW TO READ + TAKEAWAY. Do not add a 13th L2 job.

## Contents

1. [How to use](#1-how-to-use)
2. [Corpus](#2-corpus)
3. [Locked taxonomy](#3-locked-taxonomy)
4. [Two-model pipeline](#4-two-model-pipeline)
5. [Coverage matrix](#5-coverage-matrix)
6. [L2 jobs](#6-l2-jobs)
   - [`cover`](#l2-cover)
   - [`toc`](#l2-toc)
   - [`chapter`](#l2-chapter)
   - [`readme`](#l2-readme)
   - [`statement`](#l2-statement)
   - [`kpi`](#l2-kpi)
   - [`roster`](#l2-roster)
   - [`chart`](#l2-chart)
   - [`chart-table`](#l2-chart-table)
   - [`matrix`](#l2-matrix)
   - [`compare`](#l2-compare)
   - [`verdict`](#l2-verdict)
7. [Overflow (`续`)](#7-overflow-续)
8. [L3 viz recipes](#8-l3-viz-recipes)
   - [`sankey`](#l3-viz-sankey)
   - [`funnel`](#l3-viz-funnel)
   - [`waterfall`](#l3-viz-waterfall)
   - [`radar`](#l3-viz-radar)
   - [`venn`](#l3-viz-venn)
   - [`bubble`](#l3-viz-bubble)
   - [`hist-cdf`](#l3-viz-hist-cdf)
   - [`pareto`](#l3-viz-pareto)
   - [`slope`](#l3-viz-slope)
   - [`diverging-bar`](#l3-viz-diverging-bar)
   - [`quadrant`](#l3-viz-quadrant)
   - [`heatmap`](#l3-viz-heatmap)
   - [`treemap`](#l3-viz-treemap)
   - [`network`](#l3-viz-network)
   - [`line-dual`](#l3-viz-line-dual)
   - [`calendar`](#l3-viz-calendar)
9. [Appendix E chart menu](#9-appendix-e-chart-menu)
10. [Folded types and empties](#10-folded-types-and-empties)
11. [Do not](#11-do-not)

---

## 1 How to use

1. Pick **genre** from the source MD (`diagnosis` `system` `briefing` `roadmap` `dossier`).
2. Classify each chunk as one **L2 job**. Bind the **L1 shell**. Name the **L3 viz** `fill` (or `null`). Table row budget comes from the L2 job.
3. Design / fill the HTML so the densest original sample below still fits 1440×810.
4. If a table exceeds the row budget, emit the **same job** with `overflow_of` and title suffix `续`.
5. Quote, question, timeline, diagram, playbook, and brand profile fold into existing L2 jobs — see §10.
6. `text-image` `image-grid` `image-hero` never appear in this MD corpus. Keep them for Guizang only.

---

## 2 Corpus

| File | Role | Grade | Est. pages |
|---|---|---|---|
| `清水亭_主辅佐引产品结构诊断报告 (4).md` | diagnosis SoT | A+ | 280–320 |
| `清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` | visual gold (shells + 47 figs) | B visual / C spec | **296 real** |
| `侍天TIANSIGHT_分析体系Part1.md` | system bible A01–A58 | A | 90–110 |
| `苏帮袁_菜单分析维度体系_第一性原理.md` | system seed | A | 14–18 |
| `06_首版汇报报告_V1.0_数据校准版.md` | briefing | A | 140–180 |
| `07_战略方法论体系与分阶段赋能路线图_M1.0.md` | roadmap | A | 100–140 |
| `08_北京西式快餐可参考品牌分析专项_B1.0.md` | dossier | A | 80–110 |

Gold HTML: 4 CSS classes (`slide cover` 1, `slide divider` 17, `slide` 231, `slide figslide` 47). Tokens pass (`#76551F`, Noto Serif SC, IBM Plex Mono). Failures vs workshop spec: no `data-page-type`; HOW TO READ 6/296; TAKEAWAY 16/296; 126/296 titles contain `续`.

No mermaid. No `![](image)` in any of the seven files.

---

## 3 Locked taxonomy

### 3.1 Genre (5) — not a slide type

| Id | MD shape | Bars |
|---|---|---|
| `diagnosis` | 清水亭 13-module dump | SOURCE + HOW TO READ + TAKEAWAY |
| `system` | 侍天 A01–A58 / 苏帮袁 dimensions | SOURCE + takeaway |
| `briefing` | 06 首版汇报 | TAKEAWAY on data pages |
| `roadmap` | 07 stages + gates | takeaway = gate or 死法 |
| `dossier` | 08 brand files | SOURCE + learn/don’t |

### 3.2 L1 shells (4) — cheap model copies these only

| Id | Class | n / 296 | Workshop layout |
|---|---|---:|---|
| `cover` | `slide cover` | 1 | `cover` (deck) |
| `divider` | `slide divider` | 17 | `cover` as 章扉 |
| `body` | `slide` | 231 | `kpi-grid` `roster` `matrix-full` `verdict` `viz-duo` |
| `fig` | `slide figslide` | 47 | `viz-full` `viz-table` |

Shared chrome: `.tk.tl/.tr/.bl/.br` `.cap` `.hd` `.chip` `.srcbar` `.takebar` footer index. Fig default viewBox: `0 0 1320 500`.

### 3.3 L2 jobs (12)

| Id | Shell | Classify when | Table budget | Workshop |
|---|---|---|---|---|
| `cover` | cover | First page | — | cover |
| `toc` | body | Contents (≤2 pages) | act list | — |
| `chapter` | divider | H1 / 第 N 章 | — | chapter |
| `readme` | body | 阅读指南, calibre, confidence | calibre table OK | statement |
| `statement` | body | One claim, quote, or question | — | statement quote question |
| `kpi` | body | 3–6 numbers | 3–6 cards | kpi |
| `roster` | body | Named list that must sum | 8–12 rows + `.sum` | roster |
| `chart` | fig | One figure, one decision | — | chart |
| `chart-table` | fig | Figure + executable names | side table ≤8 rows | chart-table |
| `matrix` | body | 九宫, unlock, score, ABC migrate | ≤9 cells, 3-state | matrix |
| `compare` | body | Dual calibre, A vs B, stages, learn/don’t, timeline, diagram | 2 cols or 1–3 profiles | compare timeline diagram |
| `verdict` | body | 争议四段, 当场决策, 证伪 | 4 cells or decision list | verdict |

Modifier, not a job: `overflow: true` + `overflow_of` + title `续`. Gold: 126/296.

A `<table>` is a mark on `body`, not a fifth shell and not a sixth type layer. Stephen Few: table = lookup exact values; graph = see a relationship.

Retired as `fill` ids: `sum-roster` → `roster`; `kpi-cards` → `kpi`; `state-matrix` → `matrix`; `dual-calibre` / `profile-card` → `compare`; `falsify-quad` → `verdict`.

### 3.4 L3 viz (16) — FT Visual Vocabulary

Pick the **question**, then one recipe. Source: Financial Times Visual Vocabulary (Cotgreave / Smith, 2016). 附录 E lists ~40 图表类型; they collapse here via aliases.

| FT question | Recipes | Do not add |
|---|---|---|
| Magnitude | `bubble` `diverging-bar` | extra bar skins |
| Ranking | `pareto` `slope` | bump → `slope` |
| Distribution | `hist-cdf` `heatmap` | violin/boxplot/ridgeline → `hist-cdf` |
| Change over time | `line-dual` `calendar` | gantt → `calendar` |
| Part-to-whole | `treemap` `funnel` `waterfall` `venn` | pie / 3D |
| Flow | `sankey` `network` | chord → `venn` |
| Correlation | `quadrant` `radar` | extra scatter skins |
| Deviation | `diverging-bar` `waterfall` | dumbbell → `diverging-bar` |
| Spatial | — | maps; none in this MD corpus |

`sankey` `funnel` `waterfall` `radar` `venn` `bubble` `hist-cdf` `pareto` `slope` `diverging-bar` `quadrant` `heatmap` `treemap` `network` `line-dual` `calendar`

Aliases: violin/boxplot/ridgeline/stacked-bar → `hist-cdf`; dumbbell → `diverging-bar`; bump → `slope`; gantt → `calendar`; chord → `venn`; architecture → `treemap`.

No 3D. No rainbow. Matrix ink = ready / degraded / blocked. A 3-state HTML grid is L2 `matrix`, not a 17th viz.

---

## 4 Two-model pipeline

```
MD
 → TOP MODEL: genre + slide-plan JSON (shell, job, fill, slots, overflow_of)
 → CHEAP MODEL: clone L1 HTML, fill slots, no new CSS
 → page-loop (brand.md + type checks) → page-audit
```

Top model must not emit HTML. Cheap model must not pick a new job or viz id.

Required on every slide object: `id` `shell` `job` `title`.
Required on diagnosis data slides: `source` `how_to_read` `takeaway`.
`fill` is an L3 viz id or `null`. Do not put retired table ids in `fill`.

---

## 5 Coverage matrix

Every job × genre cell has at least one original cut. Gold HTML is tagged `diagnosis` because the 296-page file is the 清水亭 deck.

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

---

## 6 L2 jobs

Original excerpts. Use these to size type, row budget, and chrome. Do not invent extra slots.

<a id="l2-cover"></a>

### L2 `cover`

- L1 shell: `cover`
- workshop map: cover
- slots: kicker · title ≤3 lines · one-line decision · meta chips
- table budget: —
- samples: 7 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 diagnosis · 清水亭 title block

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L1–L8
- genre: `diagnosis`

```
# 清水亭「主辅佐引」产品结构诊断报告

**分析期间**：2026/05/01–2026/07/10（品项汇总，72 天）｜2026/06/01–2026/06/30（账单明细，30 天）
**分析范围**：清水亭 6 家门店（国贸、DT51 大屯、世纪金源、五棵松万达、祥云小镇、颐堤港）
**分类基准**：`品项汇总_20260501-20260710_国贸加五店_xlsx_清水亭_新版.xlsx` → 索引表「主辅佐引」字段
**方法论参照**：苏帮袁《君臣佐使落地形态创意探讨（2602）》239 页框架
**生成日期**：2026-07-27
```


#### S2 system · 侍天 title + one-liner

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L1–L16
- genre: `system`

```
# 侍天 TIANSIGHT 分析体系 · Part 1
## 产品结构与经营诊断｜方法论手册

> **一句话**：土金为骨、玄墨为底——**58 个分析点、15 个维度族、2 套口径、7 类周期**，每一条都可被真实数据证伪并修订。

**版本** v2.0 · 2026-07-27　|　**验证案例** 清水亭 6 店 · 118 SKU · 24,752 单 · 40,840 台
**配套** 《产品结构诊断报告》（结论）｜附录 F（争议点与证伪登记）｜本手册（方法与排期）

### Part 1 / 2 / 3 的分工

| 分册 | 主题 | 覆盖 | 状态 |
|---|---|---|---|
| **Part 1（本册）** | **产品结构与经营诊断** | 卖什么、怎么卖、往哪走 | ✅ v2.0 |
| Part 2 | 顾客资产与增长 | 获客、留存、LTV、私域、会员体系 | 待启（需识别率 ≥30%） |
| Part 3 | 供应链与单店经济模型 | 成本卡、损耗、坪效人效、开店模型 | 待启（需成本与台账数据） |
```


#### S3 briefing · 06 title block

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L1–L8
- genre: `briefing`

```
# 石头先生的汉堡 · 北京首店
# 首版汇报报告 V1.0（数据校准版）

**提报日期：** 2026 年 8 月 15 日
**阶段：** 第一阶段 · 品牌模型调研 + 产品模型模块（含竞争数据回填）
**版本：** V1.0，替代 V0.1 初稿
**目标框架：** 以「全国连锁 1000 家」为终局倒推首店决策
```


#### S4 roadmap · 07 title + nature

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1–L8
- genre: `roadmap`

```
# 石头先生的汉堡
# 战略方法论体系与分阶段赋能路线图

**版本：** M1.0
**日期：** 2026 年 8 月 13 日
**性质：** 方法论框架文件 —— 定义问题、选择工具、建立数据基础、给出 1→200 家的分阶段赋能路径
**与既有报告的关系：** 《06 首版汇报报告 V1.0》回答"北京首店怎么开"；**本报告回答"这件事本质上是什么问题、用什么方法解、每个规模阶段该做什么"**
```


#### S5 dossier · 08 title + purpose

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L1–L8
- genre: `dossier`

```
# 北京西式快餐 · 可参考品牌分析专项报告

**版本：** B1.0
**日期：** 2026 年 8 月 13 日
**数据基础：** 北京点评门店库 2026-06 快照（源库 163,210 家）→ 西式参考集 6,052 家，经**品牌名归一化**处理
**外部补充：** 全国西式快餐赛道公开数据（魏斯理、必胜汉堡、手工汉堡加盟赛道等）
**目的：** 为石头先生的汉堡建立一份"该学谁、学什么、学到什么程度、什么不能学"的可执行参照系
```


#### S6 system-seed · 苏帮袁 H1 + lede

- source: `ref/苏帮袁_菜单分析维度体系_第一性原理.md` · L1–L5
- genre: `system`

```
# 苏帮袁菜单分析维度体系 · 第一性原理 + 学术框架（v2）

> 你问的「食材×工艺×味型×毛利×场景，还有其他维度吗」——有，而且很多。但与其再列字段，不如先回到第一性原理：**一道菜本质上是什么？** 想清楚这个，所有维度（和所有矩阵）都会自动长出来。本文档把维度体系从「经验罗列」升级为「按学术框架推导」。

---
```


#### S7 gold HTML slide 1

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 1 / 296
- genre: `diagnosis`
- note: SVG compass omitted

```
class: slide cover
h1: 清水亭
主辅佐引 · 产品结构诊断

[SVG omitted]

TIANSIGHT · WISDOM NAVIGATOR FOR PREMIUM F&B CHAINS

清水亭
主辅佐引 · 产品结构诊断 

智 慧 领 航 者

六店 · 双口径 · 十三模块 —— 先把账算清，再谈策略

分析期间 / PERIOD 2026.05.01 – 07.10 品项汇总 72 天 

账单口径 / RECEIPTS 2026.06.01 – 06.30 24,752 单 · 30 天 

分类基准 / BASIS 118 SKU 82 唯一品项 

出具日期 / ISSUED 2026.07.27 v1.0 

侍
天
```


<a id="l2-toc"></a>

### L2 `toc`

- L1 shell: `body`
- workshop map: —
- slots: act list · bilingual labels · no charts
- table budget: act list, no charts
- samples: 6 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 roadmap · 07 目录表

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L11–L25
- genre: `roadmap`

```
## 目录

| 部分 | 内容 | 回答什么问题 |
|---|---|---|
| **第一部分** | 问题定义 | 我们到底在解什么问题？ |
| **第二部分** | 方法论体系 | 用什么框架解？为什么是这些？ |
| **第三部分** | 数据源体系 | 结论从哪来？怎么保证不是拍脑袋？ |
| **第四部分** | 宏观环境 | 大盘给了什么约束和红利？ |
| **第五部分** | 中国消费趋势 | 消费者正在往哪走？哪些趋势不能跟？ |
| **第六部分** | 竞争格局的结构性变化 | 🔴 谁在动？窗口还有多久？ |
| **第七部分** | 北京落地的战略选择 | 五个必须做出的选择 |
| **第八部分** | 分阶段赋能路线图 | 1 / 5 / 15 / 30 / 50 / 100 / 200 家分别做什么 |
| **第九部分** | 指标体系 | 每个阶段看什么数？ |
| **第十部分** | 风险登记册 | 什么会杀死这个项目？ |
| **第十一部分** | 治理机制 | 谁在什么时候拍什么板？ |
```


#### S2 diagnosis · 清水亭 H1 章目录 (implicit TOC)

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · all H1
- genre: `diagnosis`
- note: gold HTML paginates this into slides 2–3

```
# 清水亭「主辅佐引」产品结构诊断报告
# 第 0 章　数据地图、口径定义与数据质量
# 第 1 章　两套分析框架的对照与合并
# 第 2 章　经营基本盘
# 第 3 章　主辅佐引角色分类结果与数据校验
# 第 4 章　ABC 贡献与二八分析（双口径）
# 第 5 章　四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率
# 第 6 章　菜单结构树与 3-4-2-1 理想结构
# 第 7 章　品类倾向系数、价格带与价格空档
# 第 8 章　客单组合逻辑与小票分析
# 第 9 章　复购分析与客户资产
# 第 10 章　九宫格：味型 × 工艺 / 味型 × 食材
# 第 11 章　季节性产品矩阵与产品生命周期
# 第 12 章　商圈、竞品与对标（数据待补充）
# 第 13 章　结论与行动清单
# 附录
# 附录 F｜争议点审查与方法说明
```


#### S3 system · Part 1/2/3 分工 + 本册 H1

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L9–L16 + all H1
- genre: `system`

```
### Part 1 / 2 / 3 的分工

| 分册 | 主题 | 覆盖 | 状态 |
|---|---|---|---|
| **Part 1（本册）** | **产品结构与经营诊断** | 卖什么、怎么卖、往哪走 | ✅ v2.0 |
| Part 2 | 顾客资产与增长 | 获客、留存、LTV、私域、会员体系 | 待启（需识别率 ≥30%） |
| Part 3 | 供应链与单店经济模型 | 成本卡、损耗、坪效人效、开店模型 | 待启（需成本与台账数据） |

# 侍天 TIANSIGHT 分析体系 · Part 1
# 第一部分　维度体系
# 第二部分　口径体系
# 第三部分　58 个分析点总表
# 第四部分　分析点详解（含样例数据）
# 第五部分　方法论深解
# 第六部分　相互关系
# 第七部分　周期日历
# 第八部分　全球经营管理与产品运营分析方法论体系框架（参考）
```


#### S4 briefing · 06 部分 H1 (implicit TOC)

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · all H1
- genre: `briefing`

```
# 石头先生的汉堡 · 北京首店
# 首版汇报报告 V1.0（数据校准版）
# 第一部分 · 战略全局：从 1 到 1000
# 第二部分 · 北京西式赛道结构（全量数据）
# 第三部分 · 合生汇竞争分析（全量数据 · 本报告核心）
# 第四部分 · 产品结构诊断（数据驱动）
# 第五部分 · 首店菜单结构（8.15 交付核心）
# 第六部分 · 定价、套餐与开业营销
# 第七部分 · 品牌心智与视觉（深化）
# 第八部分 · 点单与经营动线（深化）
# 第九部分 · 数据测试与验证体系（本次大幅扩写）
# 第十部分 · 全国连锁的体系建设
# 第十一部分 · 需当场决策清单
# 第十二部分 · 未解问题与二期路线
# 附录
```


#### S5 dossier · 08 部分 H1 (implicit TOC)

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · all H1
- genre: `dossier`

```
# 北京西式快餐 · 可参考品牌分析专项报告
# 第一部分 · 方法与评估框架
# 第二部分 · 北京西式品牌全景
# 第三部分 · 跨品牌规律（从数据里提炼）
# 第四部分 · 标杆品牌深度档案
# 第五部分 · 全国维度：北京数据库里看不到的品牌
# 第六部分 · 可参考性评分矩阵
# 第七部分 · 可迁移清单：学什么 / 不学什么 / 怎么验证
# 第八部分 · 建议的持续监测机制
# 附录
```


#### S6 gold HTML slides 2–3

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slides 2–3
- genre: `diagnosis`

```
class: slide
h2: 目录

CONTENTS
目录

序 阅读指南 HOW TO READ · CALIBRE & STRUCTURE 
零 数据地图、口径定义与数据质量 DATA MAP · CALIBRE · QUALITY 
壹 两套分析框架的对照与合并 FRAMEWORK RECONCILIATION 
贰 经营基本盘 OPERATING BASELINE 
叁 主辅佐引角色分类结果与数据校验 ROLE TAXONOMY & AUDIT 
肆 ABC 贡献与二八分析（双口径） ABC & PARETO · DUAL CALIBRE 
伍 四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率 FOUR ITEM METRICS 
陆 菜单结构树与 3-4-2-1 理想结构 MENU STRUCTURE TREE 
柒 品类倾向系数、价格带与价格空档 CATEGORY BIAS & PRICE BANDS 

清水亭 · 产品结构诊断 2 / 296

--- slide 3 ---
class: slide
h2: 目录

CONTENTS
目录

捌 客单组合逻辑与小票分析 BASKET LOGIC & RECEIPTS 
玖 复购分析与客户资产 REPURCHASE & CUSTOMER ASSET 
拾 九宫格：味型 × 工艺 / 味型 × 食材 NINE-GRID MATRIX 
拾壹 季节性产品矩阵与产品生命周期 SEASONALITY & LIFECYCLE 
拾贰 商圈、竞品与对标（数据待补充） TRADE AREA & COMPETITORS 
拾叁 结论与行动清单 CONCLUSIONS & ACTIONS 
附 附录 APPENDIX 
附 附录 APPENDIX 

清水亭 · 产品结构诊断 3 / 296
```


<a id="l2-chapter"></a>

### L2 `chapter`

- L1 shell: `divider`
- workshop map: chapter
- slots: act number · chapter title · one-line promise
- table budget: —
- samples: 6 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 diagnosis · chapter H1s

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · all H1
- genre: `diagnosis`

```
# 清水亭「主辅佐引」产品结构诊断报告
# 第 0 章　数据地图、口径定义与数据质量
# 第 1 章　两套分析框架的对照与合并
# 第 2 章　经营基本盘
# 第 3 章　主辅佐引角色分类结果与数据校验
# 第 4 章　ABC 贡献与二八分析（双口径）
# 第 5 章　四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率
# 第 6 章　菜单结构树与 3-4-2-1 理想结构
# 第 7 章　品类倾向系数、价格带与价格空档
# 第 8 章　客单组合逻辑与小票分析
# 第 9 章　复购分析与客户资产
# 第 10 章　九宫格：味型 × 工艺 / 味型 × 食材
# 第 11 章　季节性产品矩阵与产品生命周期
# 第 12 章　商圈、竞品与对标（数据待补充）
# 第 13 章　结论与行动清单
# 附录
# 附录 F｜争议点审查与方法说明
```


#### S2 system · 侍天 八部分扉页

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L19, L73, L92, L188, L833, L1105, L1169, L1220
- genre: `system`

```
# 第一部分　维度体系
# 第二部分　口径体系
# 第三部分　58 个分析点总表
# 第四部分　分析点详解（含样例数据）
# 第五部分　方法论深解
# 第六部分　相互关系
# 第七部分　周期日历
# 第八部分　全球经营管理与产品运营分析方法论体系框架（参考）
```


#### S3 briefing · 06 部分扉页

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · all H1
- genre: `briefing`

```
# 石头先生的汉堡 · 北京首店
# 首版汇报报告 V1.0（数据校准版）
# 第一部分 · 战略全局：从 1 到 1000
# 第二部分 · 北京西式赛道结构（全量数据）
# 第三部分 · 合生汇竞争分析（全量数据 · 本报告核心）
# 第四部分 · 产品结构诊断（数据驱动）
# 第五部分 · 首店菜单结构（8.15 交付核心）
# 第六部分 · 定价、套餐与开业营销
# 第七部分 · 品牌心智与视觉（深化）
# 第八部分 · 点单与经营动线（深化）
# 第九部分 · 数据测试与验证体系（本次大幅扩写）
# 第十部分 · 全国连锁的体系建设
# 第十一部分 · 需当场决策清单
# 第十二部分 · 未解问题与二期路线
# 附录
```


#### S4 roadmap · 07 部分扉页

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · all H1
- genre: `roadmap`

```
# 石头先生的汉堡
# 战略方法论体系与分阶段赋能路线图
# 第一部分 · 问题定义
# 第二部分 · 方法论体系
# 第三部分 · 高质量数据源体系
# 第四部分 · 宏观环境（PESTEL 裁剪版）
# 第五部分 · 中国消费趋势
# 第六部分 · 竞争格局的结构性变化 🔴
# 第七部分 · 北京落地的战略选择
# 第八部分 · 分阶段赋能路线图（1 → 200 家）
# 第九部分 · 指标体系
# 第十部分 · 风险登记册
# 第十一部分 · 治理机制
# 附录
```


#### S5 dossier · 08 部分扉页

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · all H1
- genre: `dossier`

```
# 北京西式快餐 · 可参考品牌分析专项报告
# 第一部分 · 方法与评估框架
# 第二部分 · 北京西式品牌全景
# 第三部分 · 跨品牌规律（从数据里提炼）
# 第四部分 · 标杆品牌深度档案
# 第五部分 · 全国维度：北京数据库里看不到的品牌
# 第六部分 · 可参考性评分矩阵
# 第七部分 · 可迁移清单：学什么 / 不学什么 / 怎么验证
# 第八部分 · 建议的持续监测机制
# 附录
```


#### S6 gold HTML divider · 序 / 第0章 / 经营基本盘 / 结论

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slides 4, 7, 30, 225
- genre: `diagnosis`

```
class: slide divider
h2: 阅读指南

[SVG omitted]

序

HOW TO READ · CALIBRE & STRUCTURE

阅读指南

清水亭「主辅佐引」产品结构诊断报告

清水亭 · 产品结构诊断 4 / 296
--- slide 7 ---
class: slide divider
h2: 数据地图、口径定义与数据质量

[SVG omitted]

零

DATA MAP · CALIBRE · QUALITY

数据地图、口径定义与数据质量

第 0 章

清水亭 · 产品结构诊断 7 / 296
--- slide 30 ---
class: slide divider
h2: 经营基本盘

[SVG omitted]

贰

OPERATING BASELINE

经营基本盘

第 2 章

清水亭 · 产品结构诊断 30 / 296
--- slide 225 ---
class: slide divider
h2: 结论与行动清单

[SVG omitted]

拾叁

CONCLUSIONS & ACTIONS

结论与行动清单

第 13 章

清水亭 · 产品结构诊断 225 / 296
```


<a id="l2-readme"></a>

### L2 `readme`

- L1 shell: `body`
- workshop map: statement
- slots: calibre table · confidence · how to read
- table budget: calibre table OK
- samples: 7 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 diagnosis · 双口径阅读指南

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L11–L24
- genre: `diagnosis`

```
## 阅读指南

本报告全程采用**双口径并行**：

| 口径 | 定义 | 数据源 | 覆盖 | 用途 |
|---|---|---|---|---|
| **口径 A：标准价口径** | 销售额 = 标准售价 × 销量 | 品项汇总新版·索引表 | 6 店 72 天，40,840 台 | 菜单定价逻辑、结构诊断、跨期可比 |
| **口径 B：账单实收口径** | 销售额 = 账单行「小计金额」 | 账单明细 6 店 6 月 | 6 店 30 天，24,752 单 | 真实收入贡献、折让识别、渗透率 |

两个口径的差额来自四类因素：折扣与优惠券、按斤计价商品的实际重量、规格差异、赠送品。全文凡出现金额，均标注所属口径。

每一章的结构固定为：**📂 数据来源 → 数据表 → 🔑 关键结论 → 📊 推荐图表**。

> **先读附录 F**。报告中每一处需要分析师做判断（而非数据直接给出答案）的地方——删除了哪些数据、为什么删、哪些结论是推断而非事实、哪些测算取了乐观值——全部逐条列在**附录 F｜争议点审查与方法说明**，共 22 条，含 3 条对正文结论的更正。有争议的数字请以附录 F 为准。
```


#### S2 briefing · 数据基础与置信度

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L30–L69
- genre: `briefing`

```
## 阅读说明 · 数据基础与置信度

### 本报告的数据资产

| 数据源 | 内容 | 规模 | 用途 |
|---|---|---|---|
| **北京点评门店库 2026-06** | 原始 163,210 家，全部有效坐标 | 客单样本 136,846，评分样本 113,008 | 竞争分析底稿 |
| ↳ 西式参考集 | 西餐 / 西式快餐 / 比萨 / 牛排 / 意大利菜等 | **6,052 家** | 全市大盘 |
| ↳ 朝阳区 | 同口径 | **1,698 家** | 区域对比 |
| ↳ 合生汇 5km 内 | 同口径，四层环带 | **684 家** | 商圈竞争 |
| ↳ 合生汇场内全餐饮 | 不限西式，含中餐/茶饮/火锅 | **275 家** | 场内画像 |
| ↳ 合生汇场内西式 | 场内西式参考店 | **9 家** | 直接对手 |
| **客户产品结构表 0812** | 6 个品类 39 个食品 SKU + 19 饮品 | 含售价/毛利率/点单率/口味/档口 | 产品诊断 |
| **品牌手册 2026** | 定位、VI、卖点、RTB | 25 页 | 心智诊断 |
| **产品策略文档** | 君臣佐使、备料、动线 | — | 交叉验证 |
| **首店施工图 A1.02** | 平面布置图，2026/06 版 | 20.21m × 10.20m | 后厨与动线校验 |
| **餐品顾问简历** | 朱利亚诺·达卡斯托 | — | RTB 可核实性 |

### 锚点与口径

- **合生汇锚点：** 116.480004, 39.8938（由 277 个点评 POI 均值确定，排除昌平超极合生汇）
- **环带定义：** 0–500m / 500m–1km / 1–3km / 3–5km
- **汉堡门店识别：** 已按 V0.1 第十部分方案执行——品牌白名单 + 店名关键词 + 反向补入（分类错但店名是汉堡/披萨/牛排的）+ 排除规则（点评误标西餐的中式牛肉饭/拌饭/减脂餐等 97 家，见 `excluded_not_western.csv`；反向补入 205 家，见 `included_despite_wrong_category.csv`）

### 置信度分级

| 等级 | 含义 | V0.1 占比 | V1.0 占比 |
|---|---|---|---|
| **A · 数据支撑** | 基于客户数据表、竞争数据集、施工图测算 | 约 40% | **约 70%** |
| **B · 外部佐证** | 公开行业报告、商圈研究 | 约 40% | 约 15% |
| **C · 待验证假设** | 需开业后小票数据或实地踩点验证 | 约 20% | 约 15% |

### 仍然存在的数据缺口

1. **订单级小票数据**（泰安/北京烘焙店）→ 连带率、订单渗透率、真实人均仍无法测算（V0.1 提出，未解决）
2. **成本明细**（仅有毛利率百分比，无绝对成本值）
3. **首店最终楼层与铺位**（施工图已有，但楼层未明确）→ 直接影响 §4.2 的楼层判断
4. **点评客单为平台展示值**，非实收客单，存在系统性偏差（一般偏低 5–15%），横向对比有效，绝对值需谨慎
5. **物业硬件条件**（明火/排烟/电容/窑炉可行性）未确认
```


#### S3 dossier · 品牌归一化阅读提示

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L11–L49
- genre: `dossier`

```
## 阅读提示 · 本报告先修正了一个方法问题

**在做任何品牌分析之前，必须先做品牌名归一化。否则所有规模数字都是错的。**

以 Wagas 为例，同一个品牌在点评库中有 **5 种写法**：

| 库中品牌字段 | 门店数 |
|---|---|
| `Wagas沃歌斯` | 48 |
| `wagas` | 3 |
| `WAGAS` | 1 |
| `Wagas` | 1 |
| `wagas沃歌斯` | 1 |
| **归一化后真实规模** | **53** |

同类问题存在于：华莱士（`华莱士·全鸡汉堡`/`华莱士全鸡汉堡`/`华莱士·炸鸡汉堡`/`华莱士` → 合计 **210** 家）、赛百味（`赛百味SUBWAY`/`SUBWAY赛百味`/`赛百味` → **190** 家）、棒约翰（4 种写法 → **43** 家）、麦当劳（**623**）、肯德基（**610**）等。

> **本报告所有品牌规模数字，均为归一化后的结果。**
> 未归一化的分析会系统性低估连锁品牌的真实密度——**尤其低估的是那些"多店型、多命名"的品牌，而这恰恰是石头先生未来要走的路。**

---

# 第一部分 · 方法与评估框架

## 1.1 数据基础

| 数据集 | 规模 | 字段 |
|---|---|---|
| 北京西式参考集 | **6,052 家** | 店名、品牌、行政区、商圈、地址、品类三级、评分、人均、评论数、坐标 |
| 有人均数据 | 5,145 家 | — |
| 有评分数据 | 5,173 家 | — |
| 归一化后可识别品牌（≥3 店） | **约 130 个** | — |
| 合生汇场内全餐饮 | 275 家 | 用于同场对照 |

**口径声明（三条，贯穿全报告）：**

1. **人均是点评展示值**，为消费者填报花费均值，通常低于实收 5–15%。**横向比较有效，绝对值需谨慎。**
2. **评论数是累计值**，老店天然占优。**新店对标应看"开业同期"，不看绝对值。**
3. **门店数为北京市范围**，不代表全国规模。全国数据另见第四部分。
```


#### S4 system · 口径 A/B + 三路对账

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L73–L88
- genre: `system`

```
# 第二部分　口径体系

| 口径 | 定义 | 数据源 | 覆盖 | 适用 | 禁用 |
|---|---|---|---|---|---|
| **A 标准价** | 销售额 = 标准售价 × 销量 | 索引表 | 6 店 · 72 天 · 40,840 台 | 菜单结构、定价、跨期可比 | 真实收入、折让分析 |
| **B 账单实收** | 销售额 = 账单行 `小计金额` | 账单明细 | 6 店 · 30 天 · 24,752 单 | 真实贡献、渗透、连带、时段 | 跨期趋势（仅 1 月） |

**三路对账（每日必跑）**

```
路径1  账单表头 Σ实收金额  = ¥7,842,874  ┐
路径2  账单明细 Σ小计金额  = ¥7,842,874  ┘ 必须相等（差额 = 0）
路径3  索引表 Σ标准售价×销量 = ¥15,533,304  差额 = 折让 + 期间差 + SKU 覆盖差
```

> 清水亭案例：去重前路径 2 = ¥8,673,763，比路径 1 高 ¥830,889（+10.6%）。**正是这个 ¥0 vs ¥830,889 的差额，暴露了 5,597 行系统伪影。**
```


#### S5 roadmap · 数据源分层 + 五条纪律

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L495–L575
- genre: `roadmap`

```
# 第三部分 · 高质量数据源体系

> **一份战略报告的可信度，等于它最弱的那个数据源的可信度。**

## 3.1 数据源分层模型

按**可信度 × 时效性 × 获取成本**分五层。原则：**结论必须能追溯到 L1–L3；L4–L5 只用于形成假设，不用于支撑结论。**

| 层级 | 类型 | 可信度 | 时效 | 成本 | 用途 |
|---|---|---|---|---|---|
| **L1** | 官方统计 | ★★★★★ | 月/季 | 免费 | 大盘基准、宏观约束 |
| **L2** | 行业协会与权威研究机构 | ★★★★☆ | 季/年 | 免费–中 | 结构判断、连锁化趋势 |
| **L3** | 平台与实测数据 | ★★★★☆ | 实时 | 中 | 竞争分析、选址、定价 |
| **L4** | 商业研究与券商报告 | ★★★☆☆ | 不定 | 免费–高 | 交叉验证、案例参考 |
| **L5** | 媒体报道与自媒体 | ★★☆☆☆ | 实时 | 免费 | 线索发现、竞对动态 |
| **L0** | **自有一手数据** | ★★★★★ | 实时 | 高 | 🔴 **最高优先级** |

## 3.2 各层的具体来源清单

### L0 · 自有一手数据（最高优先级，别人拿不到的）

| 来源 | 内容 | 用途 | 状态 |
|---|---|---|---|
| **POS 订单级明细** | 每单每 SKU | 订单渗透率、连带率、共现率 | 🔴 **首店 D1 必须启动** |
| 会员系统 | 消费频次、RFM | 队列分析、复购 | 待建 |
| 出餐屏数据 | 单品出餐时长 | TOC 瓶颈识别 | 待建 |
| 点评/抖音后台 | 评分、差评文本、曝光 | 口碑归因 | 待建 |
| 供应链数据 | 进货、损耗、成本 | UE 校准 | 待建 |
| **门店实地观察** | 动线、停留、视线 | 明档有效性 | 可立即做 |
| **顾客访谈与盲测** | 定性洞察 | JTBD 验证 | 建议开业前做 |

### L1 · 官方统计

| 来源 | 关键指标 | 频率 | 用法 |
|---|---|---|---|
| 国家统计局 | 社零总额、餐饮收入及增速 | 月度 | 大盘景气度基准 |
| 统计局 CPI 分项 | 食品/餐饮价格指数 | 月度 | 涨价决策依据 |
| 北京市统计局 | 北京社零与餐饮 | 月/季 | 区域基准 |
| 市场监管总局 | 食安与预制菜相关规定 | 不定 | 🔴 合规红线 |

### L2 · 行业协会与权威研究机构

| 来源 | 核心产出 | 频率 | 本项目用法 |
|---|---|---|---|
| **中国连锁经营协会 CCFA** | 《中国餐饮连锁化发展白皮书》、TOP300 榜单 | 年度 | **连锁化率、规模分层、扩张节奏的权威基准** |
| **红餐产业研究院** | 《中国餐饮发展报告》、季度观察报告、品类报告 | 季/年 | 西式快餐赛道、人均消费、新品趋势 |
| 中国饭店协会 | 年度报告、成本结构调研 | 年度 | 成本结构对标 |
| 美团研究院 | 品类与城市数据 | 不定 | 门店规模分层 |

### L3 · 平台与实测数据（本项目的核心竞争力）

| 来源 | 内容 | 用法 |
|---|---|---|
| **点评/POI 门店库** | 店名、品类、人均、评分、评论数、坐标、商圈 | 🔴 **竞争集构建、价格带直方图、选址评分卡** |
| 外卖平台 | 品类销量、价格、配送范围 | 外卖策略 |
| 商场官方数据 | 客流、租金、品牌结构 | 选址谈判 |
| 地图 POI 与人流热力 | 商圈客流时段分布 | 选址与排班 |

> **本项目已建立的核心资产：** 北京 6,052 家西式门店参考集（源库 163,210 家，2026-06 快照），含四层环带切片、商圈聚合、品牌规模分层。**这套数据的复用价值远超一次分析——它应作为季度刷新的常设资产。**

### L4 · 商业研究与券商报告

| 来源 | 用法 | 注意 |
|---|---|---|
| 券商餐饮行业深度报告 | 上市公司单店模型、行业结构 | 数字口径需核对 |
| 咨询机构消费趋势报告 | 消费者心态 | 定性为主，不作定量依据 |
| 上市公司财报与业绩会 | **最可靠的单店模型来源** | 🔴 强烈推荐：百胜中国、达势股份等季报中的单店投资、客单、利润率是免费的高质量对标 |

### L5 · 媒体与社媒（只用于发现线索）

行业媒体、财经媒体、小红书/抖音的顾客真实反馈、竞品门店的点评差评文本。

**纪律：L5 的任何数字，在进入报告前必须找到 L1–L3 的交叉印证。**

## 3.3 数据源使用的五条纪律

1. **单一来源不下结论。** 任何关键结论至少两个独立来源交叉。
2. **区分"平台展示值"与"实收值"。** 点评人均是消费者填报值，一般低于实收 5–15%；横向比较有效，绝对值需谨慎。
3. **区分"累计"与"当期"。** 评论数是累计值，新店对标必须用"开业同期"。
4. **标注快照时间。** 所有 POI 数据必须记录抓取时间，跨期比较才有意义。
5. **给每个结论标置信度。** A（自有数据/官方统计）、B（行业报告/平台数据）、C（推演/假设）。
```


#### S6 gold HTML 阅读指南

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slides 5–6
- genre: `diagnosis`

```
class: slide
chips: 序 · 阅读指南
h2: 
SOURCE: 清水亭六店经营数据（品项汇总 72

HOW TO READ · CALIBRE & STRUCTURE 
序 · 阅读指南 

数据来源 / SOURCE 清水亭六店经营数据（品项汇总 72 天 · 账单明细 6 月 · 会员消费 1 – 6 月） 

分析期间 ： 2026 / 05 / 01 – 2026 / 07 / 10 （品项汇总， 72 天）｜ 2026 / 06 / 01 – 2026 / 06 / 30 （账单明细， 30 天） 分析范围 ：清水亭 6 家门店（国贸、DT51 大屯、世纪金源、五棵松万达、祥云小镇、颐堤港） 分类基准 ： 品项汇总_20260501- 20260710 _国贸加五店_xlsx_清水亭_新版.xlsx → 索引表「主辅佐引」字段 方法论参照 ：苏帮袁《君臣佐使落地形态创意探讨（ 2602 ）》 239 页框架 生成日期 ： 2026 - 07 - 27 

清水亭 · 产品结构诊断 · TIANSIGHT 5 / 296

--- slide 6 ---
class: slide
chips: 序 · 阅读指南
h2: 阅读指南
SOURCE: 清水亭六店经营数据（品项汇总 72

HOW TO READ · CALIBRE & STRUCTURE 
序 · 阅读指南 

阅读指南

数据来源 / SOURCE 清水亭六店经营数据（品项汇总 72 天 · 账单明细 6 月 · 会员消费 1 – 6 月） 

本报告全程采用 双口径并行 ：
口径 定义 数据源 覆盖 用途 
口径 A：标准价口径 销售额 = 标准售价 × 销量 品项汇总新版·索引表 6 店 72 天， 40,840 台 菜单定价逻辑、结构诊断、跨期可比 
口径 B：账单实收口径 销售额 = 账单行「小计金额」 账单明细 6 店 6 月 6 店 30 天， 24,752 单 真实收入贡献、折让识别、渗透率 
两个口径的差额来自四类因素：折扣与优惠券、按斤计价商品的实际重量、规格差异、赠送品。全文凡出现金额，均标注所属口径。
每一章的结构固定为： 📂 数据来源 → 数据表 → 🔑 关键结论 → 📊 推荐图表 。
先读附录 F 。报告中每一处需要分析师做判断（而非数据直接给出答案）的地方——删除了哪些数据、为什么删、哪些结论是推断而非事实、哪些测算取了乐观值——全部逐条列在 附录 F｜争议点审查与方法说明 ，共 22 条，含 3 条对正文结论的更正。有争议的数字请以附录 F 为准。

清水亭 · 产品结构诊断 · TIANSIGHT 6 / 296

--- tables (first rows) ---

| 口径 | 定义 | 数据源 | 覆盖 | 用途 |
|---|---|---|---|---|
| 口径 A：标准价口径 | 销售额 = 标准售价 × 销量 | 品项汇总新版·索引表 | 6 店 72 天， 40,840 台 | 菜单定价逻辑、结构诊断、跨期可比 |
| 口径 B：账单实收口径 | 销售额 = 账单行「小计金额」 | 账单明细 6 店 6 月 | 6 店 30 天， 24,752 单 | 真实收入贡献、折让识别、渗透率 |
```


#### S7 gold HTML 数据资产表 (calibre companion)

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 8
- genre: `diagnosis`

```
class: slide
chips: 零 · 数据地图、口径定义与数据质量
h2: 0.1 本次分析实际使用的数据资产
SOURCE: /mnt/user-data/uploads/

DATA MAP · CALIBRE · QUALITY 
零 · 数据地图、口径定义与数据质量 

0.1 本次分析实际使用的数据资产

数据来源 / SOURCE /mnt/user-data/uploads/ 全部 12 个文件 

# 文件 体量 关键字段 支撑的分析模块 
1 品项汇总…国贸加五店_新版.xlsx 370 行 × 20 列， 6 个 sheet 门店来源、 主辅佐引 、系列、品项、规格、标准售价、销量、实际成本、实际毛利、千次、开台数、档口、食材分类、味型、工艺、烹饪时间、设备、就餐场景、备注 ABC/二八、额量比、千单点击、毛利率、九宫格、价格带、结构树 
2 品项汇总…六店.xlsx 8 行 门店、有效营业天数、开台数 千单点击与倾向系数的分母 
3 – 8 账单明细 × 6 店 .xls 159,086 行 × 59 列 营业流水号、就餐人数、市别、消费区域、客位名称、开台时间、结算时间、会员手机号、大类/小类、品项名称、规格、数量、标准单价、销售单价、小计金额、成本价 渗透率、连带分析、时段、座位、RevPASH、客单组合、实收口径 
9 – 10 会员消费 × 2 （国贸 / 五店） 4,345 行 × 24 列 会员手机号、账单金额、操作时间、交易门店、消费品项 复购率、复购间隔、复购贡献 
11 账单明细…世纪金源_xlsx 3 KB — 文件损坏（缺 [Content_Types].xml），未使用 ；同店 .xls 版本完整，已替代 
12 苏帮袁君臣佐使…内容分析与大纲.md 239 页解构 七大板块目录 + 逐页速览 方法论对照（第 1 章） 

推荐图表 / CHARTS 数据资产地图（Sankey：文件 → 字段 → 分析模块），门店开台数堆叠条形图。 

清水亭 · 产品结构诊断 · TIANSIGHT 8 / 296

--- tables (first rows) ---

| # | 文件 | 体量 | 关键字段 | 支撑的分析模块 |
|---|---|---|---|---|
| 1 | 品项汇总…国贸加五店_新版.xlsx | 370 行 × 20 列， 6 个 sheet | 门店来源、 主辅佐引 、系列、品项、规格、标准售价、销量、实际成本、实际毛利、千次、开台数、档口、食材分类、味型、工艺、烹饪时间、设备、就餐场景、备注 | ABC/二八、额量比、千单点击、毛利率、九宫格、价格带、结构树 |
| 2 | 品项汇总…六店.xlsx | 8 行 | 门店、有效营业天数、开台数 | 千单点击与倾向系数的分母 |
| 3 – 8 | 账单明细 × 6 店 .xls | 159,086 行 × 59 列 | 营业流水号、就餐人数、市别、消费区域、客位名称、开台时间、结算时间、会员手机号、大类/小类、品项名称、规格、数量、标准单价、销售单价、小计金额、成本价 | 渗透率、连带分析、时段、座位、RevPASH、客单组合、实收口径 |
| 9 – 10 | 会员消费 × 2 （国贸 / 五店） | 4,345 行 × 24 列 | 会员手机号、账单金额、操作时间、交易门店、消费品项 | 复购率、复购间隔、复购贡献 |
| 11 | 账单明细…世纪金源_xlsx | 3 KB | — | 文件损坏（缺 [Content_Types].xml），未使用 ；同店 .xls 版本完整，已替代 |
| 12 | 苏帮袁君臣佐使…内容分析与大纲.md | 239 页解构 | 七大板块目录 + 逐页速览 | 方法论对照（第 1 章） |
```


<a id="l2-statement"></a>

### L2 `statement`

- L1 shell: `body`
- workshop map: statement / quote / question
- slots: one claim · optional supporting line
- table budget: —
- samples: 12 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 system-seed · 一道菜是五个系统的交点

- source: `ref/苏帮袁_菜单分析维度体系_第一性原理.md` · L7–L18
- genre: `system`

```
## 〇、第一性原理：一道菜不是一个东西，而是五个系统的交点

一道菜看起来是「一盘食物」，但作为分析对象，它同时属于五个相互独立的系统。任何分析维度，本质都是从其中某个系统里抽出的一个测量轴。问五个最根本的问题：

| 根本问题 | 维度族 | 它决定 |
|---|---|---|
| 它**是什么**？ | **A 产品·感官** | 顾客的味觉体验、辨识度 |
| 它**值多少 / 赚多少**？ | **B 经济·财务** | 单品盈利、现金流 |
| **谁、何时、为何**吃它？ | **C 需求·场景** | 销量、客单、复购 |
| 它**怎么被做出来、端上桌**？ | **D 运营·生产** | 出餐效率、人力、损耗 |
| 它在菜单上**扮演什么角色**？ | **E 战略·角色** | 引流、利润、菜单结构 |
```


#### S2 system · 侍天一句话

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L4–L7
- genre: `system`

```
> **一句话**：土金为骨、玄墨为底——**58 个分析点、15 个维度族、2 套口径、7 类周期**，每一条都可被真实数据证伪并修订。

**版本** v2.0 · 2026-07-27　|　**验证案例** 清水亭 6 店 · 118 SKU · 24,752 单 · 40,840 台
**配套** 《产品结构诊断报告》（结论）｜附录 F（争议点与证伪登记）｜本手册（方法与排期）
```


#### S3 briefing · 三条铁律

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L91–L120
- genre: `briefing`

```
**三条铁律浮出水面：**

### 铁律一：25–35 元是唯一的"万店带"，也是唯一有 11 个品牌能开过 20 家店的价格带

麦当劳 617 家、肯德基 600 家、汉堡王 112 家、赛百味 88+79 家、塔斯汀 123 家、华莱士 132+46+14 家。**这个带的平均评分只有 3.78——规模与口碑在此处是替代关系。**

### 铁律二：35–45 元是一道断崖

12 个品牌，只有 2 个开过 20 家（超级碗 55 家、TITI 超级牛扒 9 家不算）。**这个价格带的规模化难度反而高于 45–55 元。**原因很清楚：35–45 元既失去了快餐的价格优势，又没有获得"值得坐下来"的体验溢价，是最尴尬的中间地带。

> **对石头先生的直接含义：如果为了"日常化"把主力款压到 38–42 元，你落入的不是安全区，是北京数据里最难规模化的一格。**

### 铁律三：45 元以上还能开到 20 家店的西式品牌，全北京只有 8 个

| 品牌 | 北京门店 | 中位客单 | 评分 | 本质是什么 |
|---|---|---|---|---|
| 必胜客 | **281** | 58 | 4.34 | 披萨 + 意面 + 简餐 |
| 达美乐比萨 | **186** | 55 | 4.25 | 披萨（外送为主） |
| 比格比萨自助 | 84 | 74 | 4.17 | 披萨自助 |
| 萨莉亚意式餐厅 | 65 | 50 | 3.98 | 意式简餐 |
| Wagas 沃歌斯 | 47 | 78 | 4.50 | 轻食 + 咖啡 + 简餐 |
| BAKER&SPICE | 27 | 75 | **4.56** | **烘焙 + 咖啡 + 简餐** |
| Tubestation 站点比萨 | 24 | 79 | **4.62** | 披萨 |
| 棒约翰比萨·意面 | 22 | 55 | 4.40 | 披萨 + 意面 |

**8 个品牌里，6 个是披萨/意式，2 个是烘焙咖啡简餐。**

**一个汉堡品牌都没有。**

45 元以上的汉堡品牌里，北京规模最大的是 Shake Shack——**7 家**。
```


#### S4 briefing · 战略级重构主张

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L122–L126
- genre: `briefing`

```
## 1.2 战略级重构：披萨与烘焙不是负担，是石头先生唯一被验证过的规模载体

V0.1 的判断是："披萨窑炉是当前最不可复制的产线，建议首店验证、二店起收敛。"

**数据回填后，这个判断需要推翻。**
```


#### S5 briefing · 一页纸五句话

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L2182–L2194
- genre: `briefing`

```
## 一页纸总结

**如果这份报告只能留下五句话：**

1. **在北京，人均 45 元以上还能开到 20 家店的西式品牌只有 8 个，其中 6 个是披萨、2 个是烘焙咖啡，一个汉堡品牌都没有。** 石头先生的规模化路径，可能不在汉堡本身，而在它已经拥有的窑炉与烤炉。

2. **97.8% 的北京汉堡门店客单在 55 元以下。** 石头先生要做的是这个赛道的第 95–97 百分位——不是填补空档，是开辟无人区。

3. **合生汇不会逼你降价**（同品牌跨场客单差 −0.5 元），**但你必须选对楼层**（B1/B2 中位 35.5 元，楼上 55 元），**并且必须做到 4.5 分**（场内 45% 商户不到 4.0 分，但 55–60 元带的评分门槛是 4.35）。

4. **你的对手不是蓝蛙（136 元），是楼下的 Shake Shack（62 元 / 4.3 分 / 6,305 条评论）。** 它已经替你验证了"合生汇的人愿意为一个 62 元的汉堡排队"。你要回答的唯一问题是：凭什么是你。

5. **你在这个商场里已经有一家 13,831 条评论的店（石头先生的烤炉，B2 层，3.9 分）。** 它是你最便宜的启动流量，也是你最需要在开业前修好的口碑。
```


#### S6 roadmap · 北极星

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L38–L48
- genre: `roadmap`

```
### 第一层 · 北极星（10 年不变）

> **成为中国"精品西式简餐"这个品类的定义者与规模领导者。**

拆解为三个必须同时成立的条件：

| 条件 | 含义 | 为什么缺一不可 |
|---|---|---|
| **品类** | 不是"一家好吃的汉堡店"，是**开创并占据一个品类** | 单店的好吃不可复制；品类的定义可复制 |
| **规模领导** | 不是"开了很多店"，是**在该品类中门店数第一** | 品类第二名的价值不到第一名的三分之一 |
| **可持续** | 单店模型健康、组织能承重、供应链能支撑 | 规模不健康就是负债 |
```


#### S7 roadmap · 一页纸六句话

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1706–L1720
- genre: `roadmap`

```
## 附录 D · 一页纸总结

**如果这份方法论报告只能留下六句话：**

1. **本项目是一个"双重难题"：跨价格带的心智迁移 + 可复制的单店模型。而这两者的要求相反——信任状要更手工，可复制要更标准。全部战术选择都是在这个张力里做平衡。**

2. **解法是把"必须现做"压缩到三件事：现绞肉、现烤堡胚、现煎组装。其余全部标准化。**

3. **🔴 竞争格局已变：百胜中国的必胜汉堡用"西餐级汉堡 + 现场烤制汉堡坯"占位，客单 33 元，正在全国铺开。石头先生的第一信任状必须从"现烤堡胚"迁移到"现绞原切牛肉"——因为堡胚的战场已经有人了，肉的战场还空着。差异化窗口约 12–18 个月。**

4. **🔴 3–10 家门店是行业死亡带（门店数同比 −18.5%）。扩张节奏的核心不是"稳"，是"验证透了再走，走就快速穿过"。**

5. **西餐是当前唯一人均连续上涨的主流赛道（79.4→80.5→81.4 元），预制菜监管趋严是结构性红利。定位方向正确，但硬顶是 65 元——因为只有不到 5% 的中国消费者接受 70 元以上的西式快餐。**

6. **治理机制比战略更重要：Stage Gate（不达标不开新店）+ 红绿灯（数据优先于偏好）+ 不可谈判清单（现绞、现烤、现煎、8 分钟、4.5 分）。在近六成新店两年内退出的行业里，闸门是唯一的结构性保护。**
```


#### S8 diagnosis · 三个必须先修的问题 (claim cluster)

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L95–L119
- genre: `diagnosis`

```
## 0.3 数据质量：三个必须先修的问题

### 问题一｜账单明细存在规格标签重复行（已修正）

📂 **数据来源**：账单明细 6 店，`营业流水号 + 品项代码 + 数量 + 销售单价 + 小计金额` 分组检测

小龙虾类品项的每一笔实际销售在账单中被写入两行：一行使用完整规格名（`招牌虾99/（1斤起点）`），另一行使用简写（`招牌虾`），金额与数量完全一致。

| 检测项 | 结果 |
|---|---:|
| 重复组总数 | 8,209 组 |
| 组内规格不同（标签重复，属系统伪影） | 5,562 组 / 11,308 行 |
| 组内规格相同（真实多次下单，保留） | 2,647 组 / 5,627 行 |
| 受影响品项 | 金奖麻辣油焖小龙虾、黄金蒜蓉小龙虾（合计 11,194 行） |
| 删除的伪影行 | 5,597 行 |
| **虚增金额** | **¥830,889** |

**验证**：删除伪影行后，账单行「小计金额」合计 = ¥7,842,874，与账单表头「实收金额」合计 ¥7,842,874 **完全吻合**；删除前为 ¥8,673,763，虚高 10.6%。

| 指标 | 去重前 | 去重后 | 偏差 |
|---|---:|---:|---:|
| 6 月全渠道实收 | ¥8,673,763 | ¥7,842,874 | +10.6% |
| 堂食桌均 | ¥456.1 | ¥408.2 | +11.7% |
| 时令小龙虾品类实收 | ¥1,945,537 | ¥1,114,648 | +74.5% |
| 小龙虾品类占比 | 22.6% | 14.2% | +8.4pt |
```


#### S9 dossier · 三个必须记住的结论

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L153–L185
- genre: `dossier`

```
### 三个必须记住的结论

**结论一：35–45 元是全北京西式最难长出品牌的价格带。**

11 个品牌、总共 135 家门店、单品牌最大只有 60 家（超级碗 FOODBOWL）。**相比之下，45–55 元有 324 家、55–65 元有 295 家、65–80 元有 241 家。**

> **35–45 元既失去了快餐的价格优势，又没有获得"值得坐下来"的体验溢价。**
> 对石头先生的直接含义：**主力款定在 36–42 元没问题（单品定价），但门店人均不要落在 35–45 元这一格**（人均定位）。这是两件事，不能混淆。

**结论二：55–65 元这一格，是"必胜客一家的格子"。**

该带 3 个品牌 295 家门店，必胜客独占 283 家（96%），另两个是 Shake Shack（8 家）和呼伦贝尔·黄膘牛排（4 家）。

> **石头先生若定位人均 58–62 元，进入的是一个北京只有两个玩家、且其中一个占 96% 份额的格子。**
> **好处：几乎无同价位竞争。坏处：这个格子的"品类教育"全部由必胜客完成，顾客的参照系就是必胜客。**

**结论三：65–80 元反而是品质连锁最能活的带。**

| 品牌 | 门店 | 人均 | 评分 | ≥4.5 店占比 |
|---|---|---|---|---|
| 比格比萨自助 | 84 | 74 | 4.17 | 6% |
| **Wagas 沃歌斯** | **53** | 78 | **4.50** | **62%** |
| **Tubestation 站点比萨** | **29** | 78 | **4.63** | **89%** |
| **BAKER&SPICE** | **28** | 75 | **4.56** | **74%** |
| 好伦哥 | 20 | 74 | 3.78 | 5% |

> **11 个品牌 241 家门店，且四个品牌的评分在 4.5 以上。**
> **这说明：75–80 元的西式简餐，在北京是一个被验证过的、可以既做规模又做口碑的位置。**
>
> 🔴 **这对石头先生是一个需要严肃对待的战略信息：**
> 你选的 58–62 元，规模天花板由必胜客（283）定义；
> 而 75–80 元，有三个品牌（Wagas 53 / Tubestation 29 / BAKER&SPICE 28）证明了"品质型连锁"可以在这个价位做到 30–50 家且评分 4.5+。
> **58–62 元不是唯一的选择，它是一个假设。第七部分会给出判定它的方法。**
```


#### S10 dossier · 一页纸七句话

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L1108–L1124
- genre: `dossier`

```
## 附录 C · 一页纸总结

**这份报告如果只留下七句话：**

1. **做品牌分析前必须归一化品牌名——Wagas 是 53 家不是 47 家，赛百味是 190 家不是 88 家。**

2. **35–45 元是全北京西式最难长出品牌的价格带（11 个品牌、135 家门店）。而 65–80 元反而有 4 个品牌做到了评分 4.5+ 和 28–84 家店。**

3. **55–65 元这一格是"必胜客一家的格子"——283 家占该带 96%。石头先生进入的是一个几乎没有同价位竞争、但品类教育全由必胜客完成的位置。**

4. **BAKER&SPICE（28 家 / 75 元 / 4.56 分 / 单店 2,036 条评论）是北京唯一跑通"烘焙 × 简餐"规模化的品牌，也是与石头先生资产结构最匹配的学习对象。**

5. **全北京没有一个独立精品汉堡品牌超过 2 家店。石头先生若做到 5 家店且指标一致，就是这个细分的第一。**

6. **魏斯理汉堡是全国相似度最高的参照：同样的产品结构、同样的现制话语、全直营、80+ 家店——但人均只有 40 元，且已经建成日产 10 万个堡胚的中央工厂。它验证了路线，也压缩了窗口。**

7. **门店数是给外人看的。客单变异 CV（目标 ≤8%）和评分标准差（目标 ≤0.18）才是"这个模型能不能再复制 100 次"的真实答案——在这两项上，BAKER&SPICE 和 Wagas 都优于麦当劳和必胜客。**
```


#### S11 gold HTML · 额量比是价格指数

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 265
- genre: `diagnosis`

```
class: slide
chips: 附 · 附录
h2: F.5 额量比是价格指数，不是销售表现指数
SOURCE: 清水亭六店经营数据（品项汇总 72

APPENDIX 
附 · 附录 

F.5 额量比是价格指数，不是销售表现指数

数据来源 / SOURCE 清水亭六店经营数据（品项汇总 72 天 · 账单明细 6 月 · 会员消费 1 – 6 月） 

争议点 ：苏帮袁框架把额量比作为单品评价指标之一。本报告指出它在数学上等价于「售价 ÷ 全店单品均价」，是价格定位指数。这与常见用法冲突。
事实 ：额量比 = 销售额占比 ÷ 销量占比 = (售价×销量 ÷ 总额) ÷ (销量 ÷ 总量) = 售价 × (总量 ÷ 总额) = 售价 ÷ 全店单品均价 。销量在分子分母中约掉，因此额量比 与该单品卖得好不好完全无关 ，只反映它相对全店的价格位置。本报告全店单品均价 = ¥15,533,304 ÷ 260,856 = ¥59.55 ，故额量比 1.0 对应售价 ¥59.55 。
处理 ：保留该指标（框架要求），但在第 5.1 节明确标注其数学本质，并在待下架筛选中把它定位为「客单支撑力」而非「销售表现」。评价销售表现使用千单点击与渗透率。
证伪条件 ：无——这是恒等式。但若门店希望保留「额量比 = 表现指标」的旧解读，需要改用其他定义（如销售额占比 ÷ 铺位数占比）。

清水亭 · 产品结构诊断 · TIANSIGHT 265 / 296
```


#### S12 gold HTML · 三个必须先修

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 14
- genre: `diagnosis`

```
class: slide
chips: 零 · 数据地图、口径定义与数据质量
h2: 0.3 数据质量：三个必须先修的问题
SOURCE: 账单明细「会员手机号」字段 + 会员消费文件
TAKEAWAY: 任何未做该去重的历史分析，都会把小龙虾品类的贡献高估约 75%

DATA MAP · CALIBRE · QUALITY 
零 · 数据地图、口径定义与数据质量 

0.3 数据质量：三个必须先修的问题

数据来源 / SOURCE 账单明细「会员手机号」字段 + 会员消费文件 

问题一｜账单明细存在规格标签重复行（已修正）
小龙虾类品项的每一笔实际销售在账单中被写入两行：一行使用完整规格名（ 招牌虾99/（ 1 斤起点） ），另一行使用简写（ 招牌虾 ），金额与数量完全一致。
检测项 结果 
重复组总数 8,209 组 
组内规格不同（标签重复，属系统伪影） 5,562 组 / 11,308 行 
组内规格相同（真实多次下单，保留） 2,647 组 / 5,627 行 
受影响品项 金奖麻辣油焖小龙虾、黄金蒜蓉小龙虾（合计 11,194 行） 
删除的伪影行 5,597 行 
虚增金额 ¥830,889 
验证 ：删除伪影行后，账单行「小计金额」合计 = ¥7,842,874 ，与账单表头「实收金额」合计 ¥7,842,874 完全吻合 ；删除前为 ¥8,673,763 ，虚高 10.6% 。
指标 去重前 去重后 偏差 
6 月全渠道实收 ¥8,673,763 ¥7,842,874 +10.6% 
堂食桌均 ¥456.1 ¥408.2 +11.7% 
时令小龙虾品类实收 ¥1,945,537 ¥1,114,648 +74.5% 
小龙虾品类占比 22.6% 14.2% +8.4pt 
本节要点 / KEY INSIGHT 任何未做该去重的历史分析，都会把小龙虾品类的贡献高估约 75% ，并把全店桌均高估约 ¥48 。本报告全部账单口径数字均为去重后结果。 

推荐图表 / CHARTS 数据质量记分卡（Bullet chart，实际 vs 目标），去重前后瀑布图。 

清水亭 · 产品结构诊断 · TIANSIGHT 14 / 296

--- tables (first rows) ---

| 检测项 | 结果 |
|---|---|
| 重复组总数 | 8,209 组 |
| 组内规格不同（标签重复，属系统伪影） | 5,562 组 / 11,308 行 |
| 组内规格相同（真实多次下单，保留） | 2,647 组 / 5,627 行 |
| 受影响品项 | 金奖麻辣油焖小龙虾、黄金蒜蓉小龙虾（合计 11,194 行） |
| 删除的伪影行 | 5,597 行 |
| 虚增金额 | ¥830,889 |

| 指标 | 去重前 | 去重后 | 偏差 |
|---|---|---|---|
| 6 月全渠道实收 | ¥8,673,763 | ¥7,842,874 | +10.6% |
| 堂食桌均 | ¥456.1 | ¥408.2 | +11.7% |
| 时令小龙虾品类实收 | ¥1,945,537 | ¥1,114,648 | +74.5% |
| 小龙虾品类占比 | 22.6% | 14.2% | +8.4pt |
```


<a id="l2-kpi"></a>

### L2 `kpi`

- L1 shell: `body`
- workshop map: kpi
- slots: 3–6 cards: value · label · delta
- table budget: 3–6 cards
- samples: 12 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 diagnosis · 六店经营对比 (sum row = KPI tower source)

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L303–L337
- genre: `diagnosis`

```
## 2.1 六店经营对比（口径 B，2026 年 6 月）

📂 **数据来源**：账单明细 6 店（去重后 153,483 行）→ 账单头聚合 24,752 单

| 门店 | 总账单 | 总实收 | 堂食单 | 堂食实收 | 桌均 | 人均 | 件/桌 | 中位时长 | 外卖单 | 外卖实收 | 外卖占比 | 日均堂食桌 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 颐堤港店 | 5,613 | ¥1,648,839 | 3,754 | ¥1,424,497 | ¥379.5 | ¥136.4 | 8.4 | 54.6 min | 1,689 | ¥205,615 | 12.5% | 125.1 |
| 国贸店 | 3,690 | ¥1,558,884 | 3,690 | ¥1,558,884 | **¥422.5** | **¥153.8** | **9.8** | 61.0 min | 0 | ¥0 | **0.0%** | 123.0 |
| 世纪金源店 | 4,227 | ¥1,311,274 | 2,859 | ¥1,147,342 | ¥401.3 | ¥138.5 | 8.2 | 57.9 min | 1,206 | ¥153,041 | 11.7% | 95.3 |
| 祥云小镇店 | 4,343 | ¥1,312,330 | 2,505 | ¥1,089,016 | **¥434.7** | ¥147.0 | 9.3 | 58.1 min | 1,728 | ¥202,939 | 15.5% | 83.5 |
| DT51 店 | 3,916 | ¥1,185,986 | 2,218 | ¥958,255 | ¥432.0 | ¥151.8 | 8.5 | 60.8 min | 1,620 | ¥212,420 | **17.9%** | 73.9 |
| 五棵松万达店 | 2,963 | ¥825,562 | 1,841 | ¥706,385 | ¥383.7 | ¥129.9 | 8.1 | 57.5 min | 1,119 | ¥118,964 | 14.4% | 61.4 |
| **合计 / 均值** | **24,752** | **¥7,842,874** | **16,867** | **¥6,884,379** | **¥408.2** | **¥139.2** | **8.8** | **57.9 min** | **7,362** | **¥892,979** | **11.4%** | **93.7** |

**六店 6 月日均实收：¥261,429**

> **口径说明（勘误）**：本表「总账单」列与「堂食单 + 外卖单」相差 523 单。原因是账单的 `销售类型` 实际有 **4 类**，本表只列了其中 2 类：
>
> | 销售类型 | 单数 | 占比 | 本表是否单列 |
> |---|---:|---:|---|
> | 堂食 | 16,867 | 68.1% | ✅ |
> | 外卖 | 7,362 | 29.7% | ✅ |
> | **外带** | **512** | **2.1%** | ❌ 计入总账单，未单列 |
> | **自提** | **11** | **0.0%** | ❌ 计入总账单，未单列 |
>
> 外带分布：颐堤港 170、世纪金源 159、祥云小镇 108、DT51 75、五棵松 0、国贸 0。外带与自提合计 523 单，本报告未做单独分析，其金额已包含在「总实收」中。

🔑 **关键结论**

1. 祥云小镇（¥434.7）、DT51（¥432.0）、国贸（¥422.5）三店桌均领先，颐堤港（¥379.5）最低，极差 ¥55.2（14.5%）。
2. 国贸店 6 月外卖收入为 0，其余五店外卖占比 11.7%–17.9%。国贸同时拥有最高的件/桌（9.8）与最长的中位用餐时长（61.0 分钟），呈现纯堂食、重体验的结构。
3. 颐堤港日均堂食 125.1 桌（全司最高），桌均却最低，属于典型的「高流量低客单」组合，提升空间在客单而非流量。
4. 五棵松万达日均 61.4 桌、人均 ¥129.9，双低，需要单独判断是商圈问题还是执行问题。

📊 **推荐图表**：六店气泡图（X = 日均堂食桌数，Y = 桌均，气泡 = 总实收，颜色 = 外卖占比）；桌均/人均并列条形图 + 全店均值参考线。
```


#### S2 diagnosis · 主辅佐引四格总览

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L386–L395
- genre: `diagnosis`

```
## 3.1 分类结果总览（口径 A，全六店 118 SKU）

📂 **数据来源**：索引表「主辅佐引」字段，销量加权多数规则

| 角色 | SKU | SKU 占比 | 均价 | 中位价 | 均毛利率 | 销售额 | 额占比 | 销量 | 量占比 | 毛利额 | 利占比 | 中位千单点击 | 均额量比 | 均渗透率 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **主** | 13 | 11.0% | ¥142.8 | ¥139 | 64.0% | ¥3,052,266 | 19.6% | 23,054 | 8.8% | ¥1,850,942 | 17.3% | 30.9 | 2.40 | 6.8% |
| **辅** | 29 | 24.6% | ¥95.8 | ¥69 | 74.2% | ¥4,593,852 | 29.6% | 61,894 | 23.7% | ¥3,263,542 | 30.4% | 36.4 | 1.61 | 10.0% |
| **佐** | 56 | 47.5% | ¥50.8 | ¥49 | 78.8% | ¥4,580,247 | 29.5% | 151,094 | 57.9% | ¥3,478,549 | 32.4% | 20.6 | 0.85 | 6.8% |
| **引** | 20 | 16.9% | ¥105.9 | ¥49 | 73.7% | ¥3,306,940 | 21.3% | 24,815 | 9.5% | ¥2,129,825 | 19.9% | 24.6 | 1.78 | 10.0% |
```


#### S3 diagnosis · 四指标分布

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L807–L811
- genre: `diagnosis`

```

| 指标 | 最小值 | P25 | 中位数 | P75 | 最大值 | 均值 |
|---|---:|---:|---:|---:|---:|---:|
| 千单点击 | 0.34 | 9.35 | **27.20** | 71.62 | 610.90 | 54.13 |
| 额量比 | 0.08 | 0.50 | **0.99** | 1.66 | 9.22 | 1.37 |
```


#### S4 system · A04 样例门店卡

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L251–L264
- genre: `system`

```
### A04 门店经营对比　★★★★☆
**方法** 桌均 = Σ实收 ÷ 堂食账单数；人均 = Σ实收 ÷ Σ就餐人数；件/桌 = Σ数量 ÷ 账单数；时长 = `结算时间` − `开台时间`（中位）

**样例数据**

| 门店 | 堂食桌 | 桌均 | 人均 | 件/桌 | 时长 | 外卖占比 | 日均桌 | 定位 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 祥云小镇 | 2,505 | **¥434.7** | ¥147.0 | 9.3 | 58.1' | 15.5% | 83.5 | 低流量高客单 |
| DT51 | 2,218 | ¥432.0 | ¥151.8 | 8.5 | 60.8' | 17.9% | 73.9 | 低流量高客单 |
| 国贸 | 3,690 | ¥422.5 | **¥153.8** | **9.8** | **61.0'** | **0%** | 123.0 | 纯堂食重体验 |
| 颐堤港 | 3,754 | **¥379.5** | ¥136.4 | 8.4 | 54.6' | 12.5% | **125.1** | **高流量低客单** |
| 全司 | 16,867 | ¥408.2 | ¥139.2 | 8.8 | 57.9' | 11.4% | 93.7 | — |

**价值** 区分「流量问题」与「客单问题」——两者的解法完全不同　**周期** 月
```


#### S5 briefing · 全市大盘 KPI

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L226–L250
- genre: `briefing`

```
## 2.1 全市大盘

**北京西式参考集：6,052 家门店**（含西餐、西式快餐、比萨、牛排、意大利菜、轻食沙拉等）

| 指标 | 数值 |
|---|---|
| 有客单价样本 | 5,145 家 |
| 客单中位数 | **38 元** |
| 客单平均数 | 67.7 元（被高端正餐拉高） |
| 平均评分 | 4.04 |
| 评论数中位 | 276 |

**按细分品类：**

| 品类 | 门店数 | 客单中位 | 平均评分 | 评论中位 |
|---|---|---|---|---|
| 西式快餐 | 2,490 | **30** | 3.87 | 321 |
| 西餐 | 1,205 | 89 | 4.29 | 578 |
| 比萨 | 752 | **56** | 4.23 | 500 |
| 意大利菜 | 210 | 107 | 4.36 | 1,200 |
| 牛排 | 199 | 109 | 4.20 | 221 |
| 披萨自助 | 86 | 74 | 4.17 | 3,600 |
| 轻食沙拉 | 35 | 30 | 3.60 | 4 |

**⚠️ 注意"比萨"这一行：752 家门店，中位客单 56 元，平均评分 4.23。** 这正是石头先生目标价格带里门店数最多、且已被市场充分教育的品类。石头先生 55–60 元的定价，在北京消费者心中最接近的参照系不是汉堡店，**是必胜客。**
```


#### S6 roadmap · Gate 指标总表

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1032–L1044
- genre: `roadmap`

```
### 全阶段 Gate 指标总表（不达标不进下一阶段）

| Gate | 单店月利润率 | 回本期 | 点评评分 | 人均 | 8min出餐率 | 30天复购 | 新店指标偏离 |
|---|---|---|---|---|---|---|---|
| S1→S2 | ≥12% | 测算 ≤24 月 | ≥4.5 | 55–65 | ≥85% | ≥18% | — |
| S2→S3 | ≥13% | 实测 ≤22 月 | ≥4.5 | 55–65 | ≥85% | ≥20% | ≤15% |
| S3→S4 | ≥14% | ≤20 月 | ≥4.5 | 55–68 | ≥88% | ≥22% | ≤12% |
| S4→S5 | ≥15% | ≤18 月 | ≥4.5 | 55–68 | ≥88% | ≥25% | ≤10% |
| S5→S6 | ≥15% | ≤16 月 | ≥4.5 | 55–70 | ≥90% | ≥25% | ≤10% |
| S6→S7 | ≥15% | ≤15 月 | ≥4.5 | — | ≥90% | ≥25% | ≤8% |

> **这张表是本报告最重要的治理工具。**
> **它把"什么时候可以开下一家店"从一个感觉问题，变成一个查表问题。**
```


#### S7 roadmap · 宏观三数字

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L591–L600
- genre: `roadmap`

```
## 4.1 大盘：增速换挡，存量博弈

<cite index="5-1">国家统计局数据显示，2025 年全国餐饮收入达 5.79 万亿元，同比增长 3.2%，餐饮大盘与过去十年高速增长相比虽保持正向增长，但增速明显放缓</cite>。<cite index="13-1">2026 年第一季度全国餐饮收入为 14,623 亿元，同比增长 4.2%，其中 1—2 月同比增速达 4.8%，较 2025 年同期提高 0.5 个百分点</cite>。

| 指标 | 数值 | 对本项目的含义 |
|---|---|---|
| 2025 餐饮收入 | 5.79 万亿，+3.2% | 大盘微增，增长必须来自抢份额而非行业红利 |
| 2026 Q1 | 14,623 亿，+4.2% | 有回暖迹象，但不构成"顺风" |
| 餐厅总数 | <cite index="5-1">2025 年餐厅总数达 747 万家</cite> | 供给极度充裕 |
```


#### S8 dossier · Wagas 指标卡原料

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L373–L386
- genre: `dossier`

```
### 🥇 C1 · Wagas 沃歌斯 —— "品质西式简餐能开多大"的天花板样本

| 指标 | 数值 |
|---|---|
| **北京门店** | **53 家**（归一化后；未归一化会误计为 47） |
| 人均中位 | **78 元**（区间 67–88） |
| 平均评分 | **4.50** |
| ≥4.5 分门店占比 | **62%** |
| 客单变异 CV | **5.6%**（极稳定） |
| 评分标准差 | 0.20 |
| 单店评论中位 | **1,619** |
| 评论总量 | 95,244 |
| 覆盖 | 9 个行政区 / 43 个商圈 |
| 空间形态 | **商场 15 家 vs 非商场 38 家** |
```


#### S9 gold HTML · 六店经营对比

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 31
- genre: `diagnosis`

```
class: slide
chips: 贰 · 经营基本盘
h2: 2.1 六店经营对比（口径 B， 2026 年 6 月）
SOURCE: 账单明细 6

OPERATING BASELINE 
贰 · 经营基本盘 

2.1 六店经营对比（口径 B， 2026 年 6 月）

数据来源 / SOURCE 账单明细 6 店（去重后 153,483 行） → 账单头聚合 24,752 单 

门店 总账单 总实收 堂食单 堂食实收 桌均 人均 件/桌 中位时长 外卖单 外卖实收 外卖占比 日均堂食桌 
颐堤港店 5,613 ¥1,648,839 3,754 ¥1,424,497 ¥379.5 ¥136.4 8.4 54.6 min 1,689 ¥205,615 12.5% 125.1 
国贸店 3,690 ¥1,558,884 3,690 ¥1,558,884 ¥422.5 ¥153.8 9.8 61.0 min 0 ¥0 0.0% 123.0 
世纪金源店 4,227 ¥1,311,274 2,859 ¥1,147,342 ¥401.3 ¥138.5 8.2 57.9 min 1,206 ¥153,041 11.7% 95.3 
祥云小镇店 4,343 ¥1,312,330 2,505 ¥1,089,016 ¥434.7 ¥147.0 9.3 58.1 min 1,728 ¥202,939 15.5% 83.5 
DT51 店 3,916 ¥1,185,986 2,218 ¥958,255 ¥432.0 ¥151.8 8.5 60.8 min 1,620 ¥212,420 17.9% 73.9 
五棵松万达店 2,963 ¥825,562 1,841 ¥706,385 ¥383.7 ¥129.9 8.1 57.5 min 1,119 ¥118,964 14.4% 61.4 
合计 / 均值 24,752 ¥7,842,874 16,867 ¥6,884,379 ¥408.2 ¥139.2 8.8 57.9 min 7,362 ¥892,979 11.4% 93.7 
口径说明（勘误） ：本表「总账单」列与「堂食单 + 外卖单」相差 523 单。原因是账单的 销售类型 实际有 4 类 ，本表只列了其中 2 类： | 销售类型 | 单数 | 占比 | 本表是否单列 | |---|---:|---:|---| | 堂食 | 16,867 | 68.1% | ✅ | | 外卖 | 7,362 | 29.7% | ✅ | | 外带 | 512 | 2.1% | ❌ 计入总账单，未单列 | | 自提 | 11 | 0.0% | ❌ 计入总账单，未单列 | 外带分布：颐堤港 170 、世纪金源 159 、祥云小镇 108 、DT51 75 、五棵松 0 、国贸 0 。外带与自提合计 523 单，本报告未做单独分析，其金额已包含在「总实收」中。
关键结论 / KEY INSIGHTS 

推荐图表 / CHARTS 六店气泡图（X = 日均堂食桌数，Y = 桌均，气泡 = 总实收，颜色 = 外卖占比）；桌均/人均并列条形图 + 全店均值参考线。 

清水亭 · 产品结构诊断 · TIANSIGHT 31 / 296

--- tables (first rows) ---

| 门店 | 总账单 | 总实收 | 堂食单 | 堂食实收 | 桌均 | 人均 | 件/桌 | 中位时长 | 外卖单 | 外卖实收 | 外卖占比 | 日均堂食桌 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 颐堤港店 | 5,613 | ¥1,648,839 | 3,754 | ¥1,424,497 | ¥379.5 | ¥136.4 | 8.4 | 54.6 min | 1,689 | ¥205,615 | 12.5% | 125.1 |
| 国贸店 | 3,690 | ¥1,558,884 | 3,690 | ¥1,558,884 | ¥422.5 | ¥153.8 | 9.8 | 61.0 min | 0 | ¥0 | 0.0% | 123.0 |
| 世纪金源店 | 4,227 | ¥1,311,274 | 2,859 | ¥1,147,342 | ¥401.3 | ¥138.5 | 8.2 | 57.9 min | 1,206 | ¥153,041 | 11.7% | 95.3 |
| 祥云小镇店 | 4,343 | ¥1,312,330 | 2,505 | ¥1,089,016 | ¥434.7 | ¥147.0 | 9.3 | 58.1 min | 1,728 | ¥202,939 | 15.5% | 83.5 |
| DT51 店 | 3,916 | ¥1,185,986 | 2,218 | ¥958,255 | ¥432.0 | ¥151.8 | 8.5 | 60.8 min | 1,620 | ¥212,420 | 17.9% | 73.9 |
| 五棵松万达店 | 2,963 | ¥825,562 | 1,841 | ¥706,385 | ¥383.7 | ¥129.9 | 8.1 | 57.5 min | 1,119 | ¥118,964 | 14.4% | 61.4 |
| 合计 / 均值 | 24,752 | ¥7,842,874 | 16,867 | ¥6,884,379 | ¥408.2 | ¥139.2 | 8.8 | 57.9 min | 7,362 | ¥892,979 | 11.4% | 93.7 |
```


#### S10 gold HTML · 角色总览四格

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 38
- genre: `diagnosis`

```
class: slide
chips: 叁 · 主辅佐引角色分类结果与数据校验
h2: 3.1 分类结果总览（口径 A，全六店 118 SKU）
SOURCE: 索引表「主辅佐引」字段，销量加权多数规则

ROLE TAXONOMY & AUDIT 
叁 · 主辅佐引角色分类结果与数据校验 

3.1 分类结果总览（口径 A，全六店 118 SKU）

数据来源 / SOURCE 索引表「主辅佐引」字段，销量加权多数规则 

角色 SKU SKU 占比 均价 中位价 均毛利率 销售额 额占比 销量 量占比 毛利额 利占比 中位千单点击 均额量比 均渗透率 
主 13 11.0% ¥142.8 ¥139 64.0% ¥3,052,266 19.6% 23,054 8.8% ¥1,850,942 17.3% 30.9 2.40 6.8% 
辅 29 24.6% ¥95.8 ¥69 74.2% ¥4,593,852 29.6% 61,894 23.7% ¥3,263,542 30.4% 36.4 1.61 10.0% 
佐 56 47.5% ¥50.8 ¥49 78.8% ¥4,580,247 29.5% 151,094 57.9% ¥3,478,549 32.4% 20.6 0.85 6.8% 
引 20 16.9% ¥105.9 ¥49 73.7% ¥3,306,940 21.3% 24,815 9.5% ¥2,129,825 19.9% 24.6 1.78 10.0% 

清水亭 · 产品结构诊断 · TIANSIGHT 38 / 296

--- tables (first rows) ---

| 角色 | SKU | SKU 占比 | 均价 | 中位价 | 均毛利率 | 销售额 | 额占比 | 销量 | 量占比 | 毛利额 | 利占比 | 中位千单点击 | 均额量比 | 均渗透率 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 主 | 13 | 11.0% | ¥142.8 | ¥139 | 64.0% | ¥3,052,266 | 19.6% | 23,054 | 8.8% | ¥1,850,942 | 17.3% | 30.9 | 2.40 | 6.8% |
| 辅 | 29 | 24.6% | ¥95.8 | ¥69 | 74.2% | ¥4,593,852 | 29.6% | 61,894 | 23.7% | ¥3,263,542 | 30.4% | 36.4 | 1.61 | 10.0% |
| 佐 | 56 | 47.5% | ¥50.8 | ¥49 | 78.8% | ¥4,580,247 | 29.5% | 151,094 | 57.9% | ¥3,478,549 | 32.4% | 20.6 | 0.85 | 6.8% |
| 引 | 20 | 16.9% | ¥105.9 | ¥49 | 73.7% | ¥3,306,940 | 21.3% | 24,815 | 9.5% | ¥2,129,825 | 19.9% | 24.6 | 1.78 | 10.0% |
```


#### Budget · 主辅佐引四格

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L390–L395
- genre: `diagnosis`
- note: retired fill id kpi-cards

```
| 角色 | SKU | SKU 占比 | 均价 | 中位价 | 均毛利率 | 销售额 | 额占比 | 销量 | 量占比 | 毛利额 | 利占比 | 中位千单点击 | 均额量比 | 均渗透率 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **主** | 13 | 11.0% | ¥142.8 | ¥139 | 64.0% | ¥3,052,266 | 19.6% | 23,054 | 8.8% | ¥1,850,942 | 17.3% | 30.9 | 2.40 | 6.8% |
| **辅** | 29 | 24.6% | ¥95.8 | ¥69 | 74.2% | ¥4,593,852 | 29.6% | 61,894 | 23.7% | ¥3,263,542 | 30.4% | 36.4 | 1.61 | 10.0% |
| **佐** | 56 | 47.5% | ¥50.8 | ¥49 | 78.8% | ¥4,580,247 | 29.5% | 151,094 | 57.9% | ¥3,478,549 | 32.4% | 20.6 | 0.85 | 6.8% |
| **引** | 20 | 16.9% | ¥105.9 | ¥49 | 73.7% | ¥3,306,940 | 21.3% | 24,815 | 9.5% | ¥2,129,825 | 19.9% | 24.6 | 1.78 | 10.0% |
```


#### Budget · 全市大盘 4 指标

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L226–L237
- genre: `briefing`
- note: retired fill id kpi-cards

```
## 2.1 全市大盘

**北京西式参考集：6,052 家门店**（含西餐、西式快餐、比萨、牛排、意大利菜、轻食沙拉等）

| 指标 | 数值 |
|---|---|
| 有客单价样本 | 5,145 家 |
| 客单中位数 | **38 元** |
| 客单平均数 | 67.7 元（被高端正餐拉高） |
| 平均评分 | 4.04 |
| 评论数中位 | 276 |
```


<a id="l2-roster"></a>

### L2 `roster`

- L1 shell: `body`
- workshop map: roster
- slots: full names · sum row · not TOP10-as-all
- table budget: 8–12 rows + .sum closes
- samples: 11 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 diagnosis · 附录 A 全量名录 (first 12 + header)

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L2644–L2658
- genre: `diagnosis`
- note: 118 rows in source; paginate 8–12 / page

```
## 附录 A｜全六店 118 SKU 全量分析明细（口径 A：标准价，72 天）

|   序 | 品项            | 规格       | 系列       | 角色   |   售价 |    销量 |     销售额 |   额占比% |    累计% |   毛利率% |   千单点击 |   额量比 |   渗透率% | 二八分类   |
|----:|:--------------|:---------|:---------|:-----|-----:|------:|--------:|-------:|-------:|-------:|-------:|------:|-------:|:-------|
|   1 | 【鱼头+藕汤】招牌双人餐  | 套        | 套餐       | 引    |  316 |  4374 | 1382184 |   8.90 |   8.90 |  60.40 | 107.10 |  5.31 |   7.90 | 首选品    |
|   2 | 山茶油丹江大鱼头      | 例        | 招牌淡水鱼鲜   | 主    |  199 |  5231 | 1040969 |   6.70 |  15.60 |  58.50 | 128.10 |  3.34 |  15.90 | 首选品    |
|   3 | 【鱼头+藕汤】经典四人餐  | 套        | 套餐       | 引    |  549 |  1203 |  660447 |   4.25 |  19.90 |  62.00 |  29.50 |  9.22 |   2.20 | 必售品    |
|   4 | 铫子煨排骨莲藕汤      | 迷你份      | 湖北煨汤     | 辅    |   89 |  6338 |  564082 |   3.63 |  23.50 |  80.30 | 155.20 |  1.49 |  17.70 | 首选品    |
|   5 | 金奖麻辣油焖小龙虾     | 招牌虾99/斤  | 时令小龙虾    | 辅    |   99 |  4517 |  447183 |   2.88 |  26.40 |  56.20 | 110.60 |  1.66 |  16.00 | 首选品    |
|   6 | 山茶油宜昌肥鱼       | 例        | 招牌淡水鱼鲜   | 主    |  169 |  2587 |  437203 |   2.81 |  29.20 |  61.30 |  63.30 |  2.84 |   5.50 | 首选品    |
|   7 | 黄金蒜蓉小龙虾       | 招牌虾99/斤  | 时令小龙虾    | 辅    |   99 |  4143 |  410157 |   2.64 |  31.80 |  56.20 | 101.40 |  1.66 |  15.20 | 首选品    |
|   8 | 【小龙虾节】撮虾快乐双人餐 | 套        | 套餐       | 引    |  299 |  1356 |  405444 |   2.61 |  34.40 |  69.30 |  33.20 |  5.02 |   3.70 | 必售品    |
|   9 | 铫子煨排骨莲藕汤      | 小份       | 湖北煨汤     | 辅    |  169 |  2378 |  401882 |   2.59 |  37.00 |  79.30 |  58.20 |  2.84 |  17.70 | 首选品    |
|  10 | 金奖麻辣油焖小龙虾     | 精品虾159/斤 | 时令小龙虾    | 辅    |  159 |  2494 |  396626 |   2.55 |  39.60 |  63.00 |  61.10 |  2.67 |  16.00 | 首选品    |
|  11 | 公安鱼杂煲         | 例        | 招牌淡水鱼鲜   | 主    |   89 |  4340 |  386260 |   2.49 |  42.10 |  53.40 | 106.30 |  1.49 |  12.10 | 首选品    |
```


#### S2 diagnosis · 13 个「主」SKU 逐项

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L414–L427
- genre: `diagnosis`

```
|---|---:|---:|---:|---:|---|
| 山茶油丹江大鱼头（例） | ¥199 | 5,231 | 128.1 | 15.9% | 首选品 |
| 公安鱼杂煲（例） | ¥89 | 4,340 | 106.3 | 12.1% | 首选品 |
| 油爆丹江活青虾（例） | ¥69 | 3,965 | 97.1 | 10.7% | 首选品 |
| 山茶油宜昌肥鱼（例） | ¥169 | 2,587 | 63.3 | 5.5% | 首选品 |
| 山茶葱油蒸武昌鱼（例） | ¥139 | 1,402 | 34.3 | 4.6% | 必售品 |
| 油焖罗氏虾烧年糕（例） | ¥89 | 1,662 | 40.7 | 4.7% | 必售品 |
| 楚地炒鱼泡（例） | ¥69 | 1,107 | 27.1 | 2.8% | 观察品 |
| 清蒸鲜活丹江口翘嘴鲌（斤） | ¥199 | 1,263 | 30.9 | **1.5%** | 必售品 |
| 荆沙甲鱼（斤） | ¥299 | 237 | 5.8 | **0.2%** | 观察品 |
| 公安鱼杂煲（大份） | ¥139 | 424 | 10.4 | — | 观察品 |
| 油焖罗氏虾烧年糕（大份） | ¥159 | 247 | 6.0 | — | 观察品 |
| 楚地炒鱼泡（大份） | ¥109 | 61 | 1.5 | — | 长尾品 |
| 山茶油丹江大鱼头（大份） | ¥299 | 0 | 0.0 | — | 长尾品 |
```


#### S3 system · A01–A20 分析点总表 (paginate)

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L110–L133
- genre: `system`
- note: 58 rows in source

```
## 总表

| # | 分析点 | 模块 | 主维度 | 口径 | 周期 | 重要度 | ZC | HG | QSR | SK | CY | ZZ | XC | WM |
|---|---|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| A01 | 数据资产盘点 | M1 | — | — | 季 | ★★★★☆ | ● | ● | ● | ● | ● | ● | ● | ● |
| A02 | 口径定义与三路对账 | M1 | D5 | A+B | 日 | ★★★★★ | ● | ● | ● | ● | ● | ● | ● | ● |
| A03 | 数据质量检测 | M1 | D5 | B | 日 | ★★★★★ | ● | ● | ● | ● | ● | ● | ● | ● |
| A04 | 门店经营对比 | M2 | D4×D5 | B | 月 | ★★★★☆ | ● | ● | ● | ● | ● | ● | ● | ◐ |
| A05 | 客单价分布 | M2 | D5 | B | 月 | ★★★★☆ | ● | ● | ● | ● | ◐ | ○ | ● | ● |
| A06 | 桌型结构 | M2 | D5 | B | 月 | ★★★★☆ | ● | ● | ◐ | ● | ○ | ● | ◐ | ○ |
| A07 | 角色分类与一致性校验 | M3 | D1×D2 | A | 季 | ★★★★★ | ● | ● | ◐ | ● | ◐ | ◐ | ● | ◐ |
| A08 | 角色画像 | M3 | D2 | A+B | 月 | ★★★★☆ | ● | ● | ◐ | ● | ◐ | ◐ | ● | ◐ |
| A09 | 角色错配识别 | M3 | D2 | A+B | 季 | ★★★★★ | ● | ● | ◐ | ● | ◐ | ○ | ● | ◐ |
| A10 | ABC 贡献分析 | M4 | D1 | A | 月 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A11 | S1/S2 与四分类 | M4 | D1 | A | 月 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A12 | 双口径迁移矩阵 | M4 | D1 | A+B | 月 | ★★★★☆ | ● | ● | ● | ● | ● | ○ | ● | ● |
| A13 | 额量比 | M5 | D1 | A | 月 | ★★★☆☆ | ● | ● | ● | ● | ● | ○ | ● | ● |
| A14 | 千单点击 | M5 | D1 | A | 月 | ★★★★☆ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A15 | 毛利率 | M5 | D1 | A | 月 | ★★★★★ | ● | ● | ● | ● | ● | ● | ● | ● |
| A16 | 渗透率 | M5 | D1×D5 | B | 月 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A17 | 四象限矩阵 | M5 | D1 | A+B | 月 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A18 | 待下架筛选 | M5 | D1 | A+B | 季 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A19 | 高潜品识别 | M5 | D1 | A+B | 季 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A20 | 菜单结构树 | M6 | D1×D2 | A | 季 | ★★★★☆ | ● | ● | ● | ● | ● | ◐ | ● | ● |
```


#### S4 briefing · 45 元以上能开到 20 家的 8 个品牌

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L103–L120
- genre: `briefing`

```
### 铁律三：45 元以上还能开到 20 家店的西式品牌，全北京只有 8 个

| 品牌 | 北京门店 | 中位客单 | 评分 | 本质是什么 |
|---|---|---|---|---|
| 必胜客 | **281** | 58 | 4.34 | 披萨 + 意面 + 简餐 |
| 达美乐比萨 | **186** | 55 | 4.25 | 披萨（外送为主） |
| 比格比萨自助 | 84 | 74 | 4.17 | 披萨自助 |
| 萨莉亚意式餐厅 | 65 | 50 | 3.98 | 意式简餐 |
| Wagas 沃歌斯 | 47 | 78 | 4.50 | 轻食 + 咖啡 + 简餐 |
| BAKER&SPICE | 27 | 75 | **4.56** | **烘焙 + 咖啡 + 简餐** |
| Tubestation 站点比萨 | 24 | 79 | **4.62** | 披萨 |
| 棒约翰比萨·意面 | 22 | 55 | 4.40 | 披萨 + 意面 |

**8 个品牌里，6 个是披萨/意式，2 个是烘焙咖啡简餐。**

**一个汉堡品牌都没有。**

45 元以上的汉堡品牌里，北京规模最大的是 Shake Shack——**7 家**。
```


#### S5 briefing · 首版汉堡 5 款名录

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L1086–L1096
- genre: `briefing`

```
### 🥇 主 · 汉堡 5 款 —— 品牌记忆必须集中在这一格

| 产品 | 定价 | 毛利率 | 品类份额 | 角色 | 保留理由 |
|---|---|---|---|---|---|
| **经典澳牛芝士堡** | **36** | 62.6% | 45% | 🥇 绝对王牌 | 一切传播的中心；对标 Shake Shack 单堡，价格优势明确 |
| **蒜香烟熏鸡腿堡** | **22** | **74.7%** | 20% | 价格入口 | 全菜单唯一"低价×高毛利×高份额"三重交叉点，团购与外卖引流主力 |
| 🆕 **小份经典堡（原"苗堡"）** | **26** | 待测算 | — | 第二入口 | 见 §5.4。同产线、无新增食材、无新增工艺 |
| **川味椒麻牛肉堡** | **38** | 63.8% | 8% | 差异化 | 唯一辣味牛肉堡；国风融合是可讲的故事 |
| **炙烤凤梨澳牛芝士堡** | **42** | 61.9% | 5% | 酸甜解腻 | 唯一清爽系，女性向；填补九宫格口味空白 |

> **鸡腿堡值得特别强调：22 元、毛利 74.7%、品类份额 20%。** 它是整个菜单里唯一的"低价高毛利高份额"交叉点。V0.1 已指出，V1.0 进一步强化：**在北京汉堡中位客单 30 元的现实下（§2.3），22 元的鸡腿堡是石头先生唯一一款符合大众价格心理的汉堡。它应该是团购主体、外卖首屏第一位、儿童套餐的主角。**
```


#### S6 dossier · 北京西式规模总榜 (first 15)

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L88–L106
- genre: `dossier`
- note: 32 rows in source

```
## 2.1 品牌规模总榜（归一化后，北京门店数 ≥ 15 家）

| 排名 | 品牌 | 北京门店 | 人均中位 | 平均评分 | ≥4.5店占比 | 单店评论中位 | 评论总量 | 覆盖商圈 | 主品类 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 麦当劳 | **623** | 31 | 4.00 | 0% | 799 | 610,863 | **204** | 西式快餐 |
| 2 | 肯德基 | **610** | 33 | 3.75 | 0% | 252 | 264,455 | 199 | 西式快餐 |
| 3 | **必胜客** | **283** | **58** | **4.34** | **38%** | 951 | 363,552 | 165 | 比萨 |
| 4 | 华莱士 | 210 | 20 | 3.72 | 0% | 238 | 53,011 | 130 | 西式快餐 |
| 5 | 赛百味 SUBWAY | 190 | 30 | 3.94 | 1% | 347 | 93,222 | 106 | 西式快餐 |
| 6 | **达美乐比萨** | **186** | **55** | 4.25 | 23% | 338 | 85,579 | 130 | 比萨 |
| 7 | 塔斯汀 | 125 | 21 | 3.96 | 0% | 324 | 50,336 | 90 | 西式快餐 |
| 8 | 汉堡王 | 112 | 30 | 4.03 | 0% | **1,476** | 193,874 | 84 | 西式快餐 |
| 9 | **比格比萨自助** | **84** | **74** | 4.17 | 6% | **3,600** | 354,605 | 71 | 披萨自助 |
| 10 | **萨莉亚** | **65** | **50** | 3.98 | 2% | 1,051 | 87,193 | 55 | 意大利菜 |
| 11 | 牛约堡 | 61 | 26 | 3.66 | 0% | 37 | 3,748 | 53 | 西式快餐 |
| 12 | **超级碗 FOODBOWL** | **60** | **37** | **4.52** | **73%** | 547 | 37,635 | 42 | 西餐 |
| 13 | **Wagas 沃歌斯** | **53** | **78** | **4.50** | **62%** | 1,619 | 95,244 | 43 | 西餐 |
| 14 | MURVEY 蔓味轻食 | 51 | 26 | 3.54 | 0% | 20 | 1,281 | 47 | 西餐 |
| 15 | **棒约翰** | **43** | **54** | **4.38** | 33% | 503 | 30,759 | 41 | 比萨 |
```


#### S7 roadmap · 方法论速查表 (first 12)

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1643–L1656
- genre: `roadmap`
- note: paginate; rest in overflow

```
## 附录 A · 方法论速查表

| 框架 | 一句话 | 回答什么 | 失效边界 |
|---|---|---|---|
| Playing to Win | 战略是五个互相约束的选择 | 战略是什么 | 需先知道市场边界 |
| JTBD | 顾客雇佣产品完成任务 | 真实竞争对手是谁 | 难量化 |
| ERRC | 剔除/减少/增加/创造 | 我们不做什么 | 需已知行业标准 |
| Porter 五力 | 结构决定盈利 | 赛道好不好赚钱 | 静态、忽略生态 |
| 定位理论 | 占一个词，做第一 | 心智占位 | 假设空位存在 |
| Byron Sharp | 增长来自渗透率与显著性 | 增长机制 | 弱化差异化价值 |
| CBBE | 显著性→绩效形象→感受评判→共鸣 | 品牌工作排序 | 周期长 |
| 菜单工程矩阵 | 渗透率 × 毛利 四象限 | 菜品去留 | 需订单级数据 |
| 主辅佐引 | 每个 SKU 的角色 | 无数据时的菜单设计 | 主观 |
| 九宫格 | 口味×食材×工艺 | 新品方向与重复度 | 不判断好吃 |
```


#### S8 gold HTML body table + 续

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slides 8–9
- genre: `diagnosis`

```
class: slide
chips: 零 · 数据地图、口径定义与数据质量
h2: 0.1 本次分析实际使用的数据资产
SOURCE: /mnt/user-data/uploads/

DATA MAP · CALIBRE · QUALITY 
零 · 数据地图、口径定义与数据质量 

0.1 本次分析实际使用的数据资产

数据来源 / SOURCE /mnt/user-data/uploads/ 全部 12 个文件 

# 文件 体量 关键字段 支撑的分析模块 
1 品项汇总…国贸加五店_新版.xlsx 370 行 × 20 列， 6 个 sheet 门店来源、 主辅佐引 、系列、品项、规格、标准售价、销量、实际成本、实际毛利、千次、开台数、档口、食材分类、味型、工艺、烹饪时间、设备、就餐场景、备注 ABC/二八、额量比、千单点击、毛利率、九宫格、价格带、结构树 
2 品项汇总…六店.xlsx 8 行 门店、有效营业天数、开台数 千单点击与倾向系数的分母 
3 – 8 账单明细 × 6 店 .xls 159,086 行 × 59 列 营业流水号、就餐人数、市别、消费区域、客位名称、开台时间、结算时间、会员手机号、大类/小类、品项名称、规格、数量、标准单价、销售单价、小计金额、成本价 渗透率、连带分析、时段、座位、RevPASH、客单组合、实收口径 
9 – 10 会员消费 × 2 （国贸 / 五店） 4,345 行 × 24 列 会员手机号、账单金额、操作时间、交易门店、消费品项 复购率、复购间隔、复购贡献 
11 账单明细…世纪金源_xlsx 3 KB — 文件损坏（缺 [Content_Types].xml），未使用 ；同店 .xls 版本完整，已替代 
12 苏帮袁君臣佐使…内容分析与大纲.md 239 页解构 七大板块目录 + 逐页速览 方法论对照（第 1 章） 

推荐图表 / CHARTS 数据资产地图（Sankey：文件 → 字段 → 分析模块），门店开台数堆叠条形图。 

清水亭 · 产品结构诊断 · TIANSIGHT 8 / 296

--- tables (first rows) ---

| # | 文件 | 体量 | 关键字段 | 支撑的分析模块 |
|---|---|---|---|---|
| 1 | 品项汇总…国贸加五店_新版.xlsx | 370 行 × 20 列， 6 个 sheet | 门店来源、 主辅佐引 、系列、品项、规格、标准售价、销量、实际成本、实际毛利、千次、开台数、档口、食材分类、味型、工艺、烹饪时间、设备、就餐场景、备注 | ABC/二八、额量比、千单点击、毛利率、九宫格、价格带、结构树 |
| 2 | 品项汇总…六店.xlsx | 8 行 | 门店、有效营业天数、开台数 | 千单点击与倾向系数的分母 |
| 3 – 8 | 账单明细 × 6 店 .xls | 159,086 行 × 59 列 | 营业流水号、就餐人数、市别、消费区域、客位名称、开台时间、结算时间、会员手机号、大类/小类、品项名称、规格、数量、标准单价、销售单价、小计金额、成本价 | 渗透率、连带分析、时段、座位、RevPASH、客单组合、实收口径 |
| 9 – 10 | 会员消费 × 2 （国贸 / 五店） | 4,345 行 × 24 列 | 会员手机号、账单金额、操作时间、交易门店、消费品项 | 复购率、复购间隔、复购贡献 |
| 11 | 账单明细…世纪金源_xlsx | 3 KB | — | 文件损坏（缺 [Content_Types].xml），未使用 ；同店 .xls 版本完整，已替代 |
| 12 | 苏帮袁君臣佐使…内容分析与大纲.md | 239 页解构 | 七大板块目录 + 逐页速览 | 方法论对照（第 1 章） |

--- slide 9 续 ---
class: slide
chips: 零 · 数据地图、口径定义与数据质量
h2: 0.1 本次分析实际使用的数据资产 续
SOURCE: /mnt/user-data/uploads/

DATA MAP · CALIBRE · QUALITY 
零 · 数据地图、口径定义与数据质量 

0.1 本次分析实际使用的数据资产 续 

数据来源 / SOURCE /mnt/user-data/uploads/ 全部 12 个文件 

门店 有效营业天数 开台数 占比 
颐堤港店 72 9,170 22.5% 
国贸店（国兴） 72 8,720 21.4% 
世纪金源店 72 7,024 17.2% 
祥云小镇店 72 6,006 14.7% 
DT51 店 72 5,328 13.0% 
五棵松万达店 72 4,592 11.2% 
合计 72 40,840 100% 
其中国贸 8,720 台，其余五店合计 32,120 台（ 78.6% ）。全文「国贸 / 五店」两分组即以此为界。

推荐图表 / CHARTS 数据资产地图（Sankey：文件 → 字段 → 分析模块），门店开台数堆叠条形图。 

清水亭 · 产品结构诊断 · TIANSIGHT 9 / 296

--- tables (first rows) ---

| 门店 | 有效营业天数 | 开台数 | 占比 |
|---|---|---|---|
| 颐堤港店 | 72 | 9,170 | 22.5% |
| 国贸店（国兴） | 72 | 8,720 | 21.4% |
| 世纪金源店 | 72 | 7,024 | 17.2% |
| 祥云小镇店 | 72 | 6,006 | 14.7% |
| DT51 店 | 72 | 5,328 | 13.0% |
| 五棵松万达店 | 72 | 4,592 | 11.2% |
| 合计 | 72 | 40,840 | 100% |
```


#### S9 gold HTML · 口径 A 结果 (roster density)

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 50
- genre: `diagnosis`

```
class: slide
chips: 肆 · ABC 贡献与二八分析（双口径）
h2: 4.2 口径 A（标准价， 72 天）结果
SOURCE: 口径 A = 品项汇总（ 118

ABC & PARETO · DUAL CALIBRE 
肆 · ABC 贡献与二八分析（双口径） 

4.2 口径 A（标准价， 72 天）结果

数据来源 / SOURCE 口径 A = 品项汇总（ 118 SKU / 72 天）；口径 B = 账单明细（ 154 品项 / 30 天） 

全六店
分类 SKU SKU 占比 销售额 额占比 销量 量占比 毛利额 利占比 
首选品 30 25.4% ¥9,817,242 63.2% 150,029 57.5% ¥6,617,412 61.7% 
必售品 21 17.8% ¥3,642,614 23.5% 72,891 27.9% ¥2,567,778 23.9% 
观察品 29 24.6% ¥1,595,649 10.3% 22,988 8.8% ¥1,175,157 11.0% 
长尾品 38 32.2% ¥477,799 3.1% 14,948 5.7% ¥362,512 3.4% 
合计 118 100% ¥15,533,304 100% 260,856 100% ¥10,722,859 100% 
集合规模 ：S1（销售额 80% ）= 40 个 SKU｜S2（销量 80% ）= 41 个 SKU｜ 交集 = 30 个 ｜并集 = 51 个
二八验证 ： 25.4% 的 SKU 贡献 63.2% 的销售额； 43.2% 的 SKU（首选 + 必售）贡献 86.7% 的销售额。二八法则成立，且比经典 20 / 80 更集中。
二八四分类全名录（全六店 118 个 SKU 逐一归属）

清水亭 · 产品结构诊断 · TIANSIGHT 50 / 296

--- tables (first rows) ---

| 分类 | SKU | SKU 占比 | 销售额 | 额占比 | 销量 | 量占比 | 毛利额 | 利占比 |
|---|---|---|---|---|---|---|---|---|
| 首选品 | 30 | 25.4% | ¥9,817,242 | 63.2% | 150,029 | 57.5% | ¥6,617,412 | 61.7% |
| 必售品 | 21 | 17.8% | ¥3,642,614 | 23.5% | 72,891 | 27.9% | ¥2,567,778 | 23.9% |
| 观察品 | 29 | 24.6% | ¥1,595,649 | 10.3% | 22,988 | 8.8% | ¥1,175,157 | 11.0% |
| 长尾品 | 38 | 32.2% | ¥477,799 | 3.1% | 14,948 | 5.7% | ¥362,512 | 3.4% |
| 合计 | 118 | 100% | ¥15,533,304 | 100% | 260,856 | 100% | ¥10,722,859 | 100% |
```


#### Budget · 六店合计行

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L307–L315
- genre: `diagnosis`
- note: retired fill id sum-roster

```
| 门店 | 总账单 | 总实收 | 堂食单 | 堂食实收 | 桌均 | 人均 | 件/桌 | 中位时长 | 外卖单 | 外卖实收 | 外卖占比 | 日均堂食桌 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 颐堤港店 | 5,613 | ¥1,648,839 | 3,754 | ¥1,424,497 | ¥379.5 | ¥136.4 | 8.4 | 54.6 min | 1,689 | ¥205,615 | 12.5% | 125.1 |
| 国贸店 | 3,690 | ¥1,558,884 | 3,690 | ¥1,558,884 | **¥422.5** | **¥153.8** | **9.8** | 61.0 min | 0 | ¥0 | **0.0%** | 123.0 |
| 世纪金源店 | 4,227 | ¥1,311,274 | 2,859 | ¥1,147,342 | ¥401.3 | ¥138.5 | 8.2 | 57.9 min | 1,206 | ¥153,041 | 11.7% | 95.3 |
| 祥云小镇店 | 4,343 | ¥1,312,330 | 2,505 | ¥1,089,016 | **¥434.7** | ¥147.0 | 9.3 | 58.1 min | 1,728 | ¥202,939 | 15.5% | 83.5 |
| DT51 店 | 3,916 | ¥1,185,986 | 2,218 | ¥958,255 | ¥432.0 | ¥151.8 | 8.5 | 60.8 min | 1,620 | ¥212,420 | **17.9%** | 73.9 |
| 五棵松万达店 | 2,963 | ¥825,562 | 1,841 | ¥706,385 | ¥383.7 | ¥129.9 | 8.1 | 57.5 min | 1,119 | ¥118,964 | 14.4% | 61.4 |
| **合计 / 均值** | **24,752** | **¥7,842,874** | **16,867** | **¥6,884,379** | **¥408.2** | **¥139.2** | **8.8** | **57.9 min** | **7,362** | **¥892,979** | **11.4%** | **93.7** |
```


#### Budget · 附录 A 累计%

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L2644–L2658
- genre: `diagnosis`
- note: retired fill id sum-roster

```
## 附录 A｜全六店 118 SKU 全量分析明细（口径 A：标准价，72 天）

|   序 | 品项            | 规格       | 系列       | 角色   |   售价 |    销量 |     销售额 |   额占比% |    累计% |   毛利率% |   千单点击 |   额量比 |   渗透率% | 二八分类   |
|----:|:--------------|:---------|:---------|:-----|-----:|------:|--------:|-------:|-------:|-------:|-------:|------:|-------:|:-------|
|   1 | 【鱼头+藕汤】招牌双人餐  | 套        | 套餐       | 引    |  316 |  4374 | 1382184 |   8.90 |   8.90 |  60.40 | 107.10 |  5.31 |   7.90 | 首选品    |
|   2 | 山茶油丹江大鱼头      | 例        | 招牌淡水鱼鲜   | 主    |  199 |  5231 | 1040969 |   6.70 |  15.60 |  58.50 | 128.10 |  3.34 |  15.90 | 首选品    |
|   3 | 【鱼头+藕汤】经典四人餐  | 套        | 套餐       | 引    |  549 |  1203 |  660447 |   4.25 |  19.90 |  62.00 |  29.50 |  9.22 |   2.20 | 必售品    |
|   4 | 铫子煨排骨莲藕汤      | 迷你份      | 湖北煨汤     | 辅    |   89 |  6338 |  564082 |   3.63 |  23.50 |  80.30 | 155.20 |  1.49 |  17.70 | 首选品    |
|   5 | 金奖麻辣油焖小龙虾     | 招牌虾99/斤  | 时令小龙虾    | 辅    |   99 |  4517 |  447183 |   2.88 |  26.40 |  56.20 | 110.60 |  1.66 |  16.00 | 首选品    |
|   6 | 山茶油宜昌肥鱼       | 例        | 招牌淡水鱼鲜   | 主    |  169 |  2587 |  437203 |   2.81 |  29.20 |  61.30 |  63.30 |  2.84 |   5.50 | 首选品    |
|   7 | 黄金蒜蓉小龙虾       | 招牌虾99/斤  | 时令小龙虾    | 辅    |   99 |  4143 |  410157 |   2.64 |  31.80 |  56.20 | 101.40 |  1.66 |  15.20 | 首选品    |
|   8 | 【小龙虾节】撮虾快乐双人餐 | 套        | 套餐       | 引    |  299 |  1356 |  405444 |   2.61 |  34.40 |  69.30 |  33.20 |  5.02 |   3.70 | 必售品    |
|   9 | 铫子煨排骨莲藕汤      | 小份       | 湖北煨汤     | 辅    |  169 |  2378 |  401882 |   2.59 |  37.00 |  79.30 |  58.20 |  2.84 |  17.70 | 首选品    |
|  10 | 金奖麻辣油焖小龙虾     | 精品虾159/斤 | 时令小龙虾    | 辅    |  159 |  2494 |  396626 |   2.55 |  39.60 |  63.00 |  61.10 |  2.67 |  16.00 | 首选品    |
|  11 | 公安鱼杂煲         | 例        | 招牌淡水鱼鲜   | 主    |   89 |  4340 |  386260 |   2.49 |  42.10 |  53.40 | 106.30 |  1.49 |  12.10 | 首选品    |
```


<a id="l2-chart"></a>

### L2 `chart`

- L1 shell: `fig`
- workshop map: chart
- slots: one figure · SOURCE · HOW TO READ · TAKEAWAY
- table budget: —
- samples: 9 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 diagnosis · 推荐图表纪律 (章结构)

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L11–L22
- genre: `diagnosis`
- note: every diagnosis chapter ends with 推荐图表 — see fill-viz/

```
## 阅读指南

本报告全程采用**双口径并行**：

| 口径 | 定义 | 数据源 | 覆盖 | 用途 |
|---|---|---|---|---|
| **口径 A：标准价口径** | 销售额 = 标准售价 × 销量 | 品项汇总新版·索引表 | 6 店 72 天，40,840 台 | 菜单定价逻辑、结构诊断、跨期可比 |
| **口径 B：账单实收口径** | 销售额 = 账单行「小计金额」 | 账单明细 6 店 6 月 | 6 店 30 天，24,752 单 | 真实收入贡献、折让识别、渗透率 |

两个口径的差额来自四类因素：折扣与优惠券、按斤计价商品的实际重量、规格差异、赠送品。全文凡出现金额，均标注所属口径。

每一章的结构固定为：**📂 数据来源 → 数据表 → 🔑 关键结论 → 📊 推荐图表**。
```


#### S2 system · 洛伦兹 / 基尼 / 帕累托配方

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L837–L847
- genre: `system`

```
## 5.1 M4 二八与 ABC：帕累托法则及其量化延伸

**源头** Vilfredo Pareto（1896）观察意大利土地分配的 80/20 现象 → Joseph Juran（1951）引入质量管理，命名「关键少数」（Vital Few）→ 库存管理演化为 ABC 分类（Dickie, 1951）。

**数学基础** 销售额的分布通常近似**对数正态**或**幂律**。集中度可用两个正式指标度量：

```
洛伦兹曲线（Lorenz Curve）：横轴 = 累计 SKU 占比，纵轴 = 累计销售额占比
基尼系数 Gini = 1 − 2∫L(x)dx  ← 0 = 完全均匀，1 = 完全集中
清水亭：25.4% SKU → 63.2% 额，集中度高于经典 20/80
```
```


#### S3 briefing · 价格带直方图表 (chart data, no image)

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L252–L283
- genre: `briefing`

```
## 2.2 价格带直方图 —— 核心假设的验证结果

### 全市西式（n=5,145）

| 价格带 | 门店数 | 占比 | 累计 |
|---|---|---|---|
| <15 | 34 | 0.7% | 0.7% |
| 15–20 | 177 | 3.4% | 4.1% |
| 20–25 | 358 | 7.0% | 11.1% |
| 25–30 | 711 | 13.8% | 24.9% |
| **30–35** | **960** | **18.7%** | 43.6% |
| 35–40 | 440 | 8.6% | 52.2% |
| 40–45 | 173 | 3.4% | 55.6% |
| 45–50 | 179 | 3.5% | 59.1% |
| 50–55 | 235 | 4.6% | 63.7% |
| **55–60** | **197** | **3.8%** | 67.5% |
| 60–70 | 279 | 5.4% | 72.9% |
| 70–80 | 253 | 4.9% | 77.8% |
| 80–100 | 255 | 5.0% | 82.8% |
| 100–150 | 525 | 10.2% | 93.0% |
| 150+ | 369 | 7.2% | 100% |

### 关键区间精算

| 区间 | 全市 | 朝阳区 | 合生汇 5km |
|---|---|---|---|
| 45–55 元 | 414 家（8.0%） | 91 家（6.3%） | 33 家（5.7%） |
| **55–60 元** | **197 家（3.8%）** | **53 家（3.7%）** | **19 家（3.3%）** |
| 55–70 元 | 476 家（9.3%） | 128 家（8.8%） | 56 家（9.6%） |
| 50–70 元 | 711 家（13.8%） | 182 家（12.6%） | 74 家（12.7%） |

**结论一：55–60 元确实是一个稀薄带，但它不是"没人做"，而是"这是一条窄缝"。** 全市 3.8%、朝阳 3.7%、5km 内 3.3%——三个尺度高度一致，说明这不是抽样噪声，是稳定的市场结构。
```


#### S4 briefing · 竞争力雷达表

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L854–L871
- genre: `briefing`

```
## 3.10 竞争力雷达（数据校准版）

| 维度 | 石头先生 | Shake Shack | 蓝蛙 | 21街区均值 | 西式快餐巨头 | 数据依据 |
|---|---|---|---|---|---|---|
| 产品力（食材/工艺） | ★★★★★ | ★★★★ | ★★★★ | ★★ | ★★ | 现绞现煎现烤 |
| 价格力 | ★★★ | ★★★ | ★★ | ★★★★★ | ★★★★★ | 58–62 vs 62 vs 136 vs 35.5 |
| 品牌认知（北京） | ★ | ★★★★★ | ★★★★ | ★★ | ★★★★★ | Shake Shack 北京 7 店/6.3万评论 |
| **同场既有客群** | **★★★★** | ★★★ | ★★ | ★★★ | ★★ | 🆕 烤炉店 13,831 评论 |
| 视觉表现 | ★★★★★ | ★★★★ | ★★★ | ★★ | ★★★ | 品牌手册完成度高 |
| 出品效率 | ★★（待验证） | ★★★★ | ★★ | ★★★★ | ★★★★★ | 🔴 五档口结构风险 |
| 线上运营 | ★（新店） | ★★★★ | ★★★ | ★★★ | ★★★★★ | 需从 0 起 |
| 供应链标准化 | ★★（跨省首店） | ★★★★★ | ★★★★ | ★★ | ★★★★★ | 跨省风险 |

**短板排序（按紧迫度）：**
1. 🔴 **出品效率**——开业前必须压测，见 §8.4
2. 🔴 **线上运营**——开业前 14 天必须完成点评/抖音/外卖三平台建档，见 §6.5
3. 🟡 **品牌认知**——靠烤炉导流 + 内容，见 §6.2、§7.7
4. 🟡 **供应链**——跨省首店，见 §5.7 的 SKU 删减逻辑
```


#### S5 dossier · 单店评论中位 vs 门店数

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L204–L233
- genre: `dossier`

```
## 3.1 规律一：评论中位数暴露了"真实客流"，而门店数不暴露

**同样是连锁，单店人气差 100 倍。**

| 品牌 | 北京门店 | 单店评论中位 | 说明 |
|---|---|---|---|
| 西堤牛排 | 9 | **14,100** | 单店客流之王 |
| Shake Shack | 8 | **5,954** | 少而重 |
| 西十二街牛排 | 18 | 5,348 | — |
| bluefrog 蓝蛙 | 17 | 4,990 | — |
| 比格比萨自助 | 84 | **3,600** | 84 家店都是大店 |
| BAKER&SPICE | 28 | 2,036 | — |
| Wagas 沃歌斯 | 53 | 1,619 | — |
| 汉堡王 | 112 | 1,476 | — |
| Tubestation | 29 | 1,159 | — |
| 萨莉亚 | 65 | 1,051 | — |
| 必胜客 | 283 | 951 | — |
| 麦当劳 | 623 | 799 | 门店多但单店人气中等 |
| 超级碗 FOODBOWL | 60 | 547 | 小店型 |
| 达美乐比萨 | 186 | 338 | 外送为主，堂食弱 |
| 肯德基 | 610 | 252 | — |
| 牛约堡 | 61 | **37** | 🔴 有店无人 |
| 犇犇堡 | 29 | **3** | 🔴 有店无人 |
| 轻遇三明治 | 41 | **0** | 🔴 41 家店，评论中位为 0 |

> 🔴 **"轻遇三明治 41 家店、单店评论中位 0"是一个必须警惕的样本。**
> **它证明了：门店数可以靠加盟和低成本店型堆出来，但客流不能。**
>
> **对石头先生的含义：不要用门店数作为阶段目标，要用"单店评论中位数"作为品牌健康的外部代理指标。**
> **建议基准：开业 12 个月内单店评论 ≥1,500（对标 Wagas 的 1,619）。**
```


#### S6 roadmap · 死亡带规模柱 (chart data)

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L610–L627
- genre: `roadmap`

```
## 4.3 连锁化：中等规模是最佳生态位，小连锁是死亡带

<cite index="5-1">我国餐饮连锁化率从 2023 年的 21% 逐年提升，2025 年已达到 25%，年均增长 2 个百分点</cite>。<cite index="4-1">城市层级分化明显，一线城市连锁化率达 33.2%，五线城市升至 21%</cite>。

**最关键的一组数据 —— 不同规模连锁的分化：**

| 规模区间 | 门店数同比变化 | 含义 |
|---|---|---|
| **3–10 家** | <cite index="5-1">同比减少 18.5%</cite> | 🔴 **死亡带**：抗风险能力弱、供应链不完善 |
| **101–500 家** | <cite index="5-1">成为行业增长主力，凭借灵活运营与完善供应链稳步扩张</cite> | 🟢 最佳生态位 |
| **501–1000 家** | <cite index="5-1">门店数同比增长高达 32.6%</cite> | 🟢 快速扩张期 |
| 万店级 | <cite index="5-1">数量持续增加，占据行业主导</cite> | — |

> **推论 3（本报告最重要的宏观结论）：3–10 家是统计意义上的死亡带，门店数同比萎缩 18.5%。**
>
> **这直接改变了扩张节奏的设计逻辑：**
> **不要在 3–10 家这个区间停留太久。** 要么维持 1–2 家精耕直到模型完全跑通，要么一旦跑通就快速穿过 3–10 家进入 15 家以上的规模区。
> **在死亡带里"稳一稳"，是最危险的策略——因为你已经承担了多店的管理成本，却还没获得规模的采购与品牌红利。**
```


#### S7 gold HTML fig chrome · sankey 图01

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 10
- genre: `diagnosis`

```
class: slide figslide
chips: 图 01 / 47 · 零 · 数据地图、口径定义与数据质量
h2: 数据资产地图： 12 个文件如何支撑 13 个分析模块
SOURCE: /mnt/user-data/uploads 全部 12

DATA ASSET SANKEY 
图 01 / 47 · 零 · 数据地图、口径定义与数据质量 

数据资产地图： 12 个文件如何支撑 13 个分析模块

数据来源 / SOURCE /mnt/user-data/uploads 全部 12 个文件 · 字段清单 vs 模块输入需求 

[SVG omitted]

关键结论 / KEY INSIGHTS 品项汇总新版一份文件独立支撑 6 个模块；账单明细 6 店合计 159,086 行支撑 5 个模块；会员消费仅够支撑复购一个模块，且识别率只有 3.99% 。 

清水亭 · 产品结构诊断 · TIANSIGHT 10 / 296
```


#### S8 gold HTML fig chrome · pareto

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 62
- genre: `diagnosis`

```
class: slide figslide
chips: 图 11 / 47 · 肆 · ABC 贡献与二八分析（双口径）
h2: 帕累托双轴图： 25.4% 的 SKU 贡献 63.2% 的销售额
SOURCE: 口径 A 标准价，全六店 118

PARETO · DUAL AXIS 
图 11 / 47 · 肆 · ABC 贡献与二八分析（双口径） 

帕累托双轴图： 25.4% 的 SKU 贡献 63.2% 的销售额

数据来源 / SOURCE 口径 A 标准价，全六店 118 SKU / 72 天 / 40,840 台 

[SVG omitted]

关键结论 / KEY INSIGHTS S1（销售额 80% ）= 40 个 SKU，S2（销量 80% ）= 41 个，交集 30 个即首选品； 43.2% 的 SKU 贡献 86.7% 销售额，比经典 20 / 80 更集中。 

清水亭 · 产品结构诊断 · TIANSIGHT 62 / 296
```


#### S9 gold HTML fig chrome · hist-cdf

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 124
- genre: `diagnosis`

```
class: slide figslide
chips: 图 25 / 47 · 柒 · 品类倾向系数、价格带与价格空档
h2: 各系列价格分布箱线图：跨度与集中度
SOURCE: 口径 A 118

PRICE DISTRIBUTION BOXPLOT 
图 25 / 47 · 柒 · 品类倾向系数、价格带与价格空档 

各系列价格分布箱线图：跨度与集中度

数据来源 / SOURCE 口径 A 118 SKU 标准售价，按系列分组 

[SVG omitted]

关键结论 / KEY INSIGHTS 套餐（ ¥239 – 549 ）与招牌淡水鱼鲜（ ¥69 – 299 ）跨度最大；小龙虾配菜 4 个 SKU 全部 ¥13 单一价格点，缺乏价格梯度设计。 

清水亭 · 产品结构诊断 · TIANSIGHT 124 / 296
```


<a id="l2-chart-table"></a>

### L2 `chart-table`

- L1 shell: `fig`
- workshop map: chart-table
- slots: chart 58% + table 42% · shared takeaway
- table budget: side table ≤8 rows
- samples: 8 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 diagnosis · 人均分档表 + 推荐直方图

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L339–L380
- genre: `diagnosis`

```
## 2.2 客单结构

📂 **数据来源**：账单头（堂食 16,867 单）

### 按人均消费分档

| 人均档 | 桌数 | 桌占比 | 实收额 | 额占比 | 桌均 | 平均人数 |
|---|---:|---:|---:|---:|---:|---:|
| ≤¥50 | 506 | 3.0% | ¥35,154 | 0.5% | ¥69.5 | 2.9 |
| ¥50–80 | 1,106 | 6.6% | ¥222,815 | 3.2% | ¥201.5 | 2.9 |
| ¥80–100 | 1,615 | 9.7% | ¥452,155 | 6.6% | ¥280.0 | 3.1 |
| ¥100–120 | 2,629 | 15.8% | ¥856,807 | 12.4% | ¥325.9 | 2.9 |
| **¥120–150** | **3,734** | **22.4%** | **¥1,490,678** | **21.7%** | ¥399.2 | 2.9 |
| **¥150–180** | **3,248** | **19.5%** | **¥1,431,373** | **20.8%** | ¥440.7 | 2.7 |
| ¥180–220 | 2,068 | 12.4% | ¥1,127,429 | 16.4% | ¥545.2 | 2.8 |
| ¥220–300 | 1,324 | 8.0% | ¥897,331 | 13.0% | ¥677.7 | 2.7 |
| >¥300 | 412 | 2.5% | ¥370,638 | 5.4% | ¥899.6 | 2.4 |

**人均中位数 ¥139.2，均值 ¥146.1**。分店人均中位：国贸 ¥149.5 = DT51 ¥149.5 > 祥云 ¥140.0 > 世纪金源 ¥134.5 > 颐堤港 ¥132.4 > 五棵松 ¥131.5。

> **口径说明**：上表桌数合计 16,642，比堂食总桌数 16,867 少 **225 桌**。这 225 张账单的实收金额为 **¥0**（全额赠送或全免），人均无法计算，故不进入分档。它们仍计入桌均分母：¥6,884,379 ÷ 16,867 = ¥408.2；若剔除这 225 桌，桌均为 **¥413.7**（+1.3%）。全报告桌均统一采用含零值桌的 ¥408.2 口径。

### 按桌型（就餐人数）

| 桌型 | 桌数 | 桌占比 | 实收额 | 额占比 | 桌均 | 件/桌 |
|---|---:|---:|---:|---:|---:|---:|
| 1 人 | 1,182 | 7.0% | ¥167,413 | 2.4% | ¥141.6 | 4.5 |
| **2 人** | **8,359** | **49.6%** | **¥2,600,398** | **37.8%** | ¥311.1 | 7.1 |
| 3 人 | 3,423 | 20.3% | ¥1,399,167 | 20.3% | ¥408.8 | 9.1 |
| 4 人 | 2,092 | 12.4% | ¥1,079,903 | 15.7% | ¥516.2 | 10.8 |
| 5–6 人 | 1,292 | 7.7% | ¥981,131 | 14.3% | ¥759.4 | 14.4 |
| 7–8 人 | 372 | 2.2% | ¥419,003 | 6.1% | ¥1,126.4 | 20.1 |
| 9 人+ | 147 | 0.9% | ¥237,365 | 3.4% | ¥1,614.7 | 26.7 |

🔑 **关键结论**

1. **2 人桌占据半壁江山**（49.6% 桌数、37.8% 收入），加上 3 人桌，2–3 人合计 69.9% 桌数、58.1% 收入。菜单设计的第一优先级客群是 2–3 人。
2. 人均 ¥120–180 区间贡献 41.9% 桌数与 42.5% 收入，是清水亭的**核心价格心智带**。
3. 人均 ≤¥100 的低值桌占 19.3%，仅贡献 10.3% 收入；这批桌的件/桌与桌均都显著偏低，是「主菜渗透率」提升的主要目标群（见第 8 章）。
4. 5 人以上大桌仅占 10.8% 桌数，却贡献 23.8% 收入，桌均是 2 人桌的 2.4–5.2 倍。宴请/家庭聚餐场景的产品配置（大份规格、套餐）具备明确的经济价值。

📊 **推荐图表**：人均消费直方图 + 累计曲线（标注中位数 ¥139.2）；桌型双轴图（桌数占比柱 + 桌均折线）。
```


#### S2 diagnosis · 角色错配规则 + 名单头

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L439–L456
- genre: `diagnosis`

```
## 3.3 角色错配清单

📂 **数据来源**：口径 A 指标 + 口径 B 渗透率，按四条规则筛选

| 判定规则 | 触发条件 | 命中数 |
|---|---|---:|
| 引 → 应升为主/辅 | 角色 = 引 且 额量比 > 2 | 5 |
| 主 → 名不副实 | 角色 = 主 且 渗透率 < 5% | 6 |
| 佐 → 实为主力 | 角色 = 佐 且 销售额占比 > 2% | 4 |
| 辅 → 可升为主 | 角色 = 辅 且 渗透率 > 14% | 6 |

| 品项 | 规格 | 系列 | 现角色 | 售价 | 销售额（口径A） | 额量比 | 渗透率 | 建议角色 | 理由 |
|---|---|---|---|---:|---:|---:|---:|---|---|
| 【鱼头+藕汤】招牌双人餐 | 套 | 套餐 | 引 | ¥316 | ¥1,382,184 | 5.31 | 7.9% | **主** | 全店销售额第一，额量比 5.3 |
| 【鱼头+藕汤】经典四人餐 | 套 | 套餐 | 引 | ¥549 | ¥660,447 | 9.22 | 2.2% | **主** | 额量比 9.2，宴请型主力 |
| 【小龙虾节】撮虾快乐双人餐 | 套 | 套餐 | 引 | ¥299 | ¥405,444 | 5.02 | 3.7% | **主（季节）** | 季节性主力套餐 |
| 【工作日超值】双人餐 | 套 | 套餐 | 引 | ¥239 | ¥156,545 | 4.01 | 1.8% | **引（保留）** | 唯一真正的引流套餐，但渗透率仅 1.8% |
| 秦巴热卤黄牛肉 | 大份 | 湖北烟火热菜 | 引 | ¥139 | ¥83,400 | 2.33 | 9.0% | **辅** | 大份高价，非引流形态 |
```


#### S3 system · A04 样例表 (pairs with bubble)

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L251–L264
- genre: `system`

```
### A04 门店经营对比　★★★★☆
**方法** 桌均 = Σ实收 ÷ 堂食账单数；人均 = Σ实收 ÷ Σ就餐人数；件/桌 = Σ数量 ÷ 账单数；时长 = `结算时间` − `开台时间`（中位）

**样例数据**

| 门店 | 堂食桌 | 桌均 | 人均 | 件/桌 | 时长 | 外卖占比 | 日均桌 | 定位 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 祥云小镇 | 2,505 | **¥434.7** | ¥147.0 | 9.3 | 58.1' | 15.5% | 83.5 | 低流量高客单 |
| DT51 | 2,218 | ¥432.0 | ¥151.8 | 8.5 | 60.8' | 17.9% | 73.9 | 低流量高客单 |
| 国贸 | 3,690 | ¥422.5 | **¥153.8** | **9.8** | **61.0'** | **0%** | 123.0 | 纯堂食重体验 |
| 颐堤港 | 3,754 | **¥379.5** | ¥136.4 | 8.4 | 54.6' | 12.5% | **125.1** | **高流量低客单** |
| 全司 | 16,867 | ¥408.2 | ¥139.2 | 8.8 | 57.9' | 11.4% | 93.7 | — |

**价值** 区分「流量问题」与「客单问题」——两者的解法完全不同　**周期** 月
```


#### S4 briefing · 竞争定位矩阵 (pairs with radar)

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L841–L852
- genre: `briefing`

```
## 3.9 竞争定位矩阵（数据版）

| 维度 | 石头先生（目标） | Shake Shack 合生汇 | 萨莉亚 合生汇 | 蓝蛙 合生汇 | 21 街区均值 | 必胜客 大郊亭桥 |
|---|---|---|---|---|---|---|
| 人均 | **58–62** | 62 | 52 | 136 | 35.5 | 63 |
| 评分 | **目标 ≥4.5** | 4.3 | 4.1 | 4.8 | 4.01 | 4.5 |
| 评论量级 | 目标 90 天 ≥2,000 | 6,305 | 1,310 | 2,475 | 中位 2,153 | 1,560 |
| 品类心智 | 现做西式简餐 | 美式汉堡 | 意式平价 | 美式休闲西餐 | 重口中餐+小吃 | 披萨简餐 |
| 出餐速度 | 待压测 | 快 | 中 | 慢 | 快 | 中 |
| 明档 | **✅ 三大明档** | 半开放 | 无 | 无 | 部分 | 无 |
| 北京规模 | 1 | 7 | 65 | 17 | — | 281 |
| 全时段 | 午/晚/下午茶 | 全天 | 全天 | 晚市为主 | 晚市为主 | 全天 |
```


#### S5 roadmap · Gate 表 (pairs with stage waterfall)

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1032–L1044
- genre: `roadmap`

```
### 全阶段 Gate 指标总表（不达标不进下一阶段）

| Gate | 单店月利润率 | 回本期 | 点评评分 | 人均 | 8min出餐率 | 30天复购 | 新店指标偏离 |
|---|---|---|---|---|---|---|---|
| S1→S2 | ≥12% | 测算 ≤24 月 | ≥4.5 | 55–65 | ≥85% | ≥18% | — |
| S2→S3 | ≥13% | 实测 ≤22 月 | ≥4.5 | 55–65 | ≥85% | ≥20% | ≤15% |
| S3→S4 | ≥14% | ≤20 月 | ≥4.5 | 55–68 | ≥88% | ≥22% | ≤12% |
| S4→S5 | ≥15% | ≤18 月 | ≥4.5 | 55–68 | ≥88% | ≥25% | ≤10% |
| S5→S6 | ≥15% | ≤16 月 | ≥4.5 | 55–70 | ≥90% | ≥25% | ≤10% |
| S6→S7 | ≥15% | ≤15 月 | ≥4.5 | — | ≥90% | ≥25% | ≤8% |

> **这张表是本报告最重要的治理工具。**
> **它把"什么时候可以开下一家店"从一个感觉问题，变成一个查表问题。**
```


#### S6 dossier · 价格带 × 规模 + 读法

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L138–L160
- genre: `dossier`

```
## 2.2 价格带 × 规模天花板（归一化后重算）

**这是本报告最重要的结构表。它用归一化后的数据，重新确认了"哪些价格带能长出大品牌"。**

| 价格带 | 品牌数 | **单品牌最大规模** | 门店数中位 | 该带总门店 | 平均评分 | 判断 |
|---|---|---|---|---|---|---|
| **< 25 元** | 21 | 210（华莱士） | 3 | 418 | 3.60 | 万店级母体，但北京密度不高 |
| **25–35 元** | 40 | **623（麦当劳）** | 7.5 | **2,000** | 3.77 | 🟢 **绝对主战场** |
| **35–45 元** | **11** | **60（超级碗 FOODBOWL）** | 4 | **135** | 3.81 | 🔴 **断崖** |
| **45–55 元** | 7 | 186（达美乐） | 17 | 324 | 4.24 | 🟢 披萨主导 |
| **55–65 元** | **3** | **283（必胜客）** | 8 | 295 | 3.97 | 🟡 **必胜客一家占 96%** |
| **65–80 元** | 11 | 84（比格比萨自助） | 9 | 241 | 4.08 | 🟢 品质连锁带 |
| **80–100 元** | 8 | 16（THE WOODS） | 3.5 | 46 | 4.29 | 🔴 规模天花板出现 |
| **100 元以上** | 34 | 18（西十二街牛排） | 4 | 199 | 4.62 | 🔴 高分但开不大 |

### 三个必须记住的结论

**结论一：35–45 元是全北京西式最难长出品牌的价格带。**

11 个品牌、总共 135 家门店、单品牌最大只有 60 家（超级碗 FOODBOWL）。**相比之下，45–55 元有 324 家、55–65 元有 295 家、65–80 元有 241 家。**

> **35–45 元既失去了快餐的价格优势，又没有获得"值得坐下来"的体验溢价。**
> 对石头先生的直接含义：**主力款定在 36–42 元没问题（单品定价），但门店人均不要落在 35–45 元这一格**（人均定位）。这是两件事，不能混淆。
```


#### S7 gold HTML 四象限页 chrome

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 42
- genre: `diagnosis`

```
class: slide figslide
chips: 图 09 / 47 · 叁 · 主辅佐引角色分类结果与数据校验
h2: 角色校验四象限： 13 个「主」品的渗透率只有 6.8%
SOURCE: 口径 A 额量比（ 118

ROLE AUDIT QUADRANT 
图 09 / 47 · 叁 · 主辅佐引角色分类结果与数据校验 

角色校验四象限： 13 个「主」品的渗透率只有 6.8% 

数据来源 / SOURCE 口径 A 额量比（ 118 SKU）+ 口径 B 堂食渗透率（ 6 月 16,867 桌） 

[SVG omitted]

关键结论 / KEY INSIGHTS 「主」（朱红）本应落在右上高渗透高价区，实际大量散布在左侧低渗透区；渗透率第一的是「辅」类的铫子煨排骨莲藕汤 17.7% ，高于所有主品。 

清水亭 · 产品结构诊断 · TIANSIGHT 42 / 296
```


#### S8 gold HTML 高潜品四象限

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 83
- genre: `diagnosis`

```
class: slide figslide
chips: 图 16 / 47 · 伍 · 四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率
h2: 高潜品四象限： 31 款「利润黑马」等待强制曝光
SOURCE: 口径 A，千单点击中位 27.20

HIGH-POTENTIAL QUADRANT 
图 16 / 47 · 伍 · 四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率 

高潜品四象限： 31 款「利润黑马」等待强制曝光

数据来源 / SOURCE 口径 A，千单点击中位 27.20 / 毛利率中位 75.9% 

[SVG omitted]

关键结论 / KEY INSIGHTS 左上朱红区 31 款高毛利低曝光品中有 9 款是「大份」规格，毛利率比例份高 3 – 8pt 、千单点击只有例份的 1 / 5 – 1 / 10 ，是最容易兑现的毛利增量。 

清水亭 · 产品结构诊断 · TIANSIGHT 83 / 296
```


<a id="l2-matrix"></a>

### L2 `matrix`

- L1 shell: `body`
- workshop map: matrix
- slots: row × col · cell state · zero≠gap footnote
- table budget: ≤9 cells, 3-state ink
- samples: 13 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 diagnosis · 味型 × 工艺九宫

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L1938–L1976
- genre: `diagnosis`

```
## 10.2 味型 × 工艺九宫格

**分组规则**
- 味型组：辣/麻（含辣、麻字样）｜甜/酸（含甜、酸、甘字样）｜咸鲜/本味/香（其余）
- 工艺组：快工艺（炒、油爆、炕炒、炕、干煸、煎、凉拌、搓、浇汁）｜慢工艺（炖、烧、煮、浸煮、卤、热卤、烩、熟醉、浸泡）｜特殊工艺（蒸、清蒸、烤、炸等）

### SKU 数分布

| 味型 ＼ 工艺 | 快工艺 | 慢工艺 | 特殊工艺 | 合计 |
|---|---:|---:|---:|---:|
| 咸鲜/本味/香 | 16 | **24** | 17 | **57** |
| 甜/酸 | 4 | 3 | 5 | 12 |
| 辣/麻 | 8 | 13 | **0** | 21 |
| **合计** | **28** | **40** | **22** | **90** |

### 销售额分布（万元，口径 A）

| 味型 ＼ 工艺 | 快工艺 | 慢工艺 | 特殊工艺 | 合计 |
|---|---:|---:|---:|---:|
| 咸鲜/本味/香 | ¥181.5 | **¥402.1** | ¥164.3 | ¥747.9 |
| 甜/酸 | ¥27.5 | ¥10.5 | ¥42.3 | ¥80.3 |
| 辣/麻 | ¥74.6 | **¥347.0** | **¥0.0** | ¥421.6 |
| **合计** | **¥283.6** | **¥759.6** | **¥206.6** | **¥1,249.8** |

### 销量分布

| 味型 ＼ 工艺 | 快工艺 | 慢工艺 | 特殊工艺 |
|---|---:|---:|---:|
| 咸鲜/本味/香 | 31,451 | 45,495 | **51,743** |
| 甜/酸 | 28,776 | 3,556 | 13,842 |
| 辣/麻 | 17,602 | 43,911 | **0** |

🔑 **关键结论**

1. **最强集群：咸鲜 × 慢工艺**（24 款，¥402.1 万，32.2% 销售额）。铫子煨汤、鱼头、鱼杂煲等核心产品全部落在这一格，构成清水亭的技术护城河。
2. **第二集群：辣/麻 × 慢工艺**（13 款，¥347.0 万，27.8% 销售额）。小龙虾、椒麻馋嘴蛙、秦巴热卤黄牛肉等。两个慢工艺格合计贡献 **60.0% 的销售额**。
3. **唯一空白格：辣/麻 × 特殊工艺 = 0 款**。全九宫格中唯一的完全空缺。蒸/烤/炸类的辣味产品完全缺失。参照湖北菜谱系，这一格可开发：**剁椒蒸鱼头、香辣烤鱼、干锅辣味蒸菜、油炸辣味小吃**。
4. **甜/酸 × 慢工艺仅 3 款、¥10.5 万（0.8%）**，是第二薄弱格。甜酸味型整体仅 12 款、¥80.3 万（6.4%），在以「藕、鱼、腊味」为核心的菜单里，甜品与甜口菜的开发严重不足。
5. **咸鲜 × 特殊工艺销量最高（51,743 件）但销售额仅 ¥164.3 万**，均价偏低——蒸菜、米粑粑、热干面等高频低价产品集中于此。
```


#### S2 diagnosis · 双口径分类迁移矩阵

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L732–L744
- genre: `diagnosis`

```
## 4.4 双口径对照

### 分类迁移矩阵（79 个可比品项）

| 标准价口径 ＼ 实收口径 | 必售品 | 观察品 | 长尾品 | 首选品 | 合计 |
|---|---:|---:|---:|---:|---:|
| **必售品** | 15 | 0 | 0 | 4 | 19 |
| **观察品** | 2 | 12 | 0 | 1 | 15 |
| **长尾品** | 0 | 7 | 15 | 0 | 22 |
| **首选品** | 0 | 0 | 0 | 23 | 23 |
| **合计** | 17 | 19 | 15 | 28 | 79 |

**一致率 82.3%**（65/79）。14 个品项发生跨级迁移，全部为「上升 1 级」或「下降 1 级」，无跨两级的剧烈变动。
```


#### S3 diagnosis · 价格空档扫描

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L1403–L1432
- genre: `diagnosis`

```
## 7.3 全店价格空档扫描

📂 **方法**：10 元步长，扫描 **114 个 SKU（118 减去 4 个套餐）** 的价格分布，覆盖销售额 ¥12,928,685（占口径 A 的 83.2%）。套餐单列于第 7.2 节，理由见附录 F.18

| 价格带 | SKU | 销量 | 销售额 | 额占比 | 状态 |
|---|---:|---:|---:|---:|---|
| ¥0–10 | 4 | 56,711 | ¥361,244 | 2.8% | 密集 |
| ¥10–20 | 11 | 33,363 | ¥512,712 | 4.0% | 密集 |
| ¥20–30 | 15 | 18,922 | ¥494,300 | 3.8% | 密集 |
| ¥30–40 | 12 | 24,467 | ¥930,012 | 7.2% | 密集 |
| ¥40–50 | 13 | 29,496 | ¥1,423,464 | **11.0%** | 密集 |
| ¥50–60 | 8 | 16,454 | ¥970,786 | 7.5% | 正常 |
| ¥60–70 | 12 | 19,266 | ¥1,329,320 | **10.3%** | 密集 |
| ¥70–80 | 4 | 1,410 | ¥111,390 | 0.9% | ⚠️ 稀薄 |
| ¥80–90 | 8 | 16,310 | ¥1,451,590 | **11.2%** | 密集 |
| ¥90–100 | 4 | 12,542 | ¥1,241,658 | **9.6%** | 正常 |
| ¥100–110 | 4 | 914 | ¥99,626 | 0.8% | ⚠️ 稀薄 |
| ¥110–120 | 1 | 1,944 | ¥231,336 | 1.8% | ⚠️ 稀薄 |
| ¥120–130 | 1 | 528 | ¥68,112 | 0.5% | ⚠️ 稀薄 |
| ¥130–140 | 4 | 3,023 | ¥420,197 | 3.2% | 正常 |
| **¥140–150** | **0** | 0 | ¥0 | 0.0% | ❌ **空档** |
| ¥150–160 | 4 | 5,125 | ¥814,875 | 6.3% | 正常 |
| ¥160–170 | 3 | 5,122 | ¥865,534 | 6.7% | 正常 |
| **¥170–190** | **0** | 0 | ¥0 | 0.0% | ❌ **空档（2 段）** |
| ¥190–200 | 2 | 6,494 | ¥1,292,326 | **10.0%** | 密集 |
| **¥200–220** | **0** | 0 | ¥0 | 0.0% | ❌ **空档（2 段）** |
| ¥220–230 | 2 | 335 | ¥76,715 | 0.6% | 稀薄 |
| **¥230–260** | **0** | 0 | ¥0 | 0.0% | ❌ **空档（3 段）** |
| ¥260–270 | 1 | 605 | ¥162,745 | 1.3% | 稀薄 |
| **¥270–290** | **0** | 0 | ¥0 | 0.0% | ❌ **空档（2 段）** |
```


#### S4 system-seed · 五族根本问题表

- source: `ref/苏帮袁_菜单分析维度体系_第一性原理.md` · L7–L18
- genre: `system`

```
## 〇、第一性原理：一道菜不是一个东西，而是五个系统的交点

一道菜看起来是「一盘食物」，但作为分析对象，它同时属于五个相互独立的系统。任何分析维度，本质都是从其中某个系统里抽出的一个测量轴。问五个最根本的问题：

| 根本问题 | 维度族 | 它决定 |
|---|---|---|
| 它**是什么**？ | **A 产品·感官** | 顾客的味觉体验、辨识度 |
| 它**值多少 / 赚多少**？ | **B 经济·财务** | 单品盈利、现金流 |
| **谁、何时、为何**吃它？ | **C 需求·场景** | 销量、客单、复购 |
| 它**怎么被做出来、端上桌**？ | **D 运营·生产** | 出餐效率、人力、损耗 |
| 它在菜单上**扮演什么角色**？ | **E 战略·角色** | 引流、利润、菜单结构 |
```


#### S5 system · 维度组合三条约束

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L61–L69
- genre: `system`

```
## 1.3 维度组合规则

不是任意两个维度都能交叉。三条约束：

| 约束 | 规则 | 反例 |
|---|---|---|
| **口径一致** | 交叉的两个维度必须来自同一口径 | ❌ 索引表 `销量`（72 天）× 账单 `渗透率`（30 天）→ 分母期间不同 |
| **粒度可达** | 细粒度维度不能凭空细化 | ❌ 品项级动能 × 规格维度 → 账单规格多为 `-`，无法映射 |
| **样本充足** | 交叉后每格样本量须支撑判断 | ❌ 味型 × 食材的「辣/麻 × 海鲜」仅 1 个 SKU 基数，零值无意义 |
```


#### S6 briefing · 价格带 × 规模天花板

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L74–L89
- genre: `briefing`

```
## 1.1 本报告最重要的一张表：价格带 × 规模天花板

**这是全国连锁目标下，一切菜单与定价决策的硬约束。**

我们统计了北京 6052 家西式门店中所有拥有 ≥3 家北京门店的连锁品牌，按其中位客单价分组：

| 价格带 | 品牌数 | 门店数中位 | **单品牌最大规模** | 该带总门店 | 平均评分 | ≥20 店的品牌数 |
|---|---|---|---|---|---|---|
| < 25 元 | 19 | 5 | 131（华莱士·全鸡汉堡） | 385 | 3.66 | 3 |
| **25–35 元** | 38 | 9 | **617（麦当劳）** | **1,894** | 3.78 | **11** |
| **35–45 元** | 12 | 5 | 55（超级碗 FOODBOWL） | 134 | 3.94 | **2** ⬅️ 断崖 |
| 45–55 元 | 8 | 11 | 186（达美乐比萨） | 307 | 4.18 | 3 |
| **55–65 元** | 4 | 7 | **281（必胜客）** | 299 | 4.09 | 1 |
| 65–80 元 | 8 | 14.5 | 84（比格比萨自助） | 198 | 4.25 | 4 |
| 80–100 元 | 8 | 3.5 | 11（THE WOODS） | 43 | 4.36 | **0** |
| 100 元以上 | 32 | 4 | 18（西十二街牛排） | 172 | 4.64 | **0** |
```


#### S7 briefing · 九宫格重复度

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L928–L942
- genre: `briefing`

```
## 4.3 九宫格重复度诊断

**严重重复的三条线：**

| 重复元素 | 出现次数 | 涉及产品 | 问题 |
|---|---|---|---|
| **黑松露** | **5 处** | 火柴薯条、芝士熔岩球、黑松露蘑菇牛肉堡、黑松露什锦蘑菇披萨、硬币堡酱料 | 高级感被稀释成日常调味，顾客感知不到"贵"。**且北京 6052 家西式门店中，店名含"黑松露"的：0 家——这个词从来不是一个能被顾客搜索到的记忆点** |
| **川味/香辣** | **7 处** | 香辣鸡翅、川味椒麻堡、辣肉酱堡、蜀香辣肉酱披萨、麻辣小龙虾披萨、川味腊肠意面、泰式酸辣沙拉 | 国风融合是真差异点，但 7 处过载，分散在 5 个档口 |
| **海鲜** | **7 处** | 西班牙鱿鱼煎蛋、墨鱼肠、那不勒斯海鲜披萨、蒜香白酒海鲜面、日式海胆拌饭、小龙虾披萨、大虾沙拉 | 🔴 **海鲜是损耗最高、备货最难、跨省供应链最脆弱的一类。首店是跨省首店，这条线风险最高** |

**九宫格空白区（值得补的方向）：**
- 工艺：**烘焙 × 汉堡的深度结合**——现烤堡胚已是资产，但没有一款产品把"烘焙"讲成主角
- 口味：**清爽/酸香系**——现有汉堡以咸香、重口为主，缺夏季/女性向轻口味（凤梨堡是唯一一款）
- 场景：**35 元以下的日常入口款**——目前只有鸡腿堡 22 元一款承担，过于单薄
- 品类：**基础款披萨**（见 4.2 第 4 点）
```


#### S8 roadmap · 框架 × 阶段使用矩阵

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L468–L491
- genre: `roadmap`

```
## 2.9 框架 × 阶段的使用矩阵

| 框架 | 1家 | 5家 | 15家 | 30家 | 50家 | 100家 | 200家 |
|---|---|---|---|---|---|---|---|
| Playing to Win | ●●● | ● | ● | ●● | ● | ●● | ●●● |
| JTBD | ●●● | ●● | ● | ● | ● | ●● | ●● |
| ERRC | ●●● | ●● | ● | ● | ●● | ●● | ● |
| 定位 + Byron Sharp | ●●● | ●●● | ●●● | ●●● | ●● | ●●● | ●●● |
| CBBE 金字塔 | ●（显著性） | ●● | ●●（绩效形象） | ●● | ●●● | ●●●（共鸣） | ●●● |
| **菜单工程矩阵** | ●●（D15起） | ●●● | ●●● | ●●● | ●●● | ●●● | ●●● |
| 主辅佐引 | ●●● | ●●● | ●● | ●● | ●● | ●● | ●● |
| 九宫格 | ●● | ●●● | ●●● | ●●● | ●●● | ●●● | ●●● |
| Kano | ●●● | ●●● | ●● | ●● | ●● | ●● | ●● |
| **单位经济学 UE** | ●●● | ●●● | ●●● | ●●● | ●●● | ●●● | ●●● |
| TOC 约束 | ●●● | ●●● | ●● | ●● | ●● | ● | ● |
| 精益 + SOP | ●● | ●●● | ●●● | ●●● | ●●● | ●●● | ●●● |
| AARRR | ●● | ●●● | ●●● | ●●● | ●● | ●● | ●● |
| 队列 + RFM | ● | ●● | ●●● | ●●● | ●●● | ●●● | ●●● |
| **Greiner 组织** | — | ●● | ●●● | ●●● | ●●● | ●●● | ●●● |
| 蓝图化手册 | ●● | ●●● | ●●● | ●●● | ●● | ●● | ●● |
| Stage Gate 治理 | ●●● | ●●● | ●●● | ●●● | ●●● | ●●● | ●●● |
| 实验设计 | ●● | ●●● | ●●● | ●●● | ●●● | ●●● | ●●● |

●●● = 主导框架　●● = 重要辅助　● = 保持关注
```


#### S9 dossier · 可参考性评分矩阵 TOP12

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L951–L980
- genre: `dossier`

```
# 第六部分 · 可参考性评分矩阵

## 6.1 打分模型

对每个候选品牌，按五个维度打分（各 1–5 分），加权得出"可参考性总分"：

| 维度 | 权重 | 含义 |
|---|---|---|
| **价格带贴近度** | 25% | 人均与 55–65 元的接近程度 |
| **模式贴近度** | 30% | 现制/明档/多品类/堂食为主 |
| **规模验证度** | 20% | 该模型被验证到多少家店 |
| **口碑水平** | 15% | 评分与稳定性 |
| **数据可得性** | 10% | 我们能持续观测到多少信息 |

## 6.2 TOP 12 学习对象排序

| 排名 | 品牌 | 规模 | 人均 | 评分 | 价格 | 模式 | 规模 | 口碑 | 数据 | **总分** | 一句话 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 🥇 1 | **魏斯理汉堡** | 全国 80+ | 40 | — | 3 | **5** | 4 | 4 | 3 | **4.05** | 同一条路，走在前面 |
| 🥈 2 | **BAKER&SPICE** | 京 28 | 75 | 4.56 | 4 | **5** | 4 | **5** | **5** | **4.65** | 烘焙×简餐唯一规模样本 |
| 🥉 3 | **Wagas 沃歌斯** | 京 53 | 78 | 4.50 | 4 | 4 | **5** | **5** | **5** | **4.55** | 品质简餐的规模天花板 |
| 4 | **必胜客（含WOW）** | 京 283 | 58 | 4.34 | **5** | 3 | **5** | 4 | **5** | **4.35** | 我们价格带的定义者 |
| 5 | **Tubestation** | 京 29 | 78 | 4.63 | 4 | 4 | 4 | **5** | **5** | **4.35** | 披萨可规模化的正面证据 |
| 6 | **超级碗 FOODBOWL** | 京 60 | 37 | 4.52 | 3 | 4 | **5** | **5** | **5** | **4.30** | 轻量店型的最佳模仿对象 |
| 7 | **Shake Shack** | 京 8 | 63.5 | 4.18 | **5** | 4 | 2 | 3 | **5** | **3.90** | 同场同价的直接对标 |
| 8 | **THE WOODS** | 京 16 | 65–138 | 4.66 | 4 | 3 | 3 | **5** | **5** | **3.85** | 双店型策略的最佳样本 |
| 9 | **必胜汉堡** | 全国扩张中 | 33 | — | 2 | **5** | 3 | 3 | 3 | **3.45** | 撞位者，必须持续监测 |
| 10 | **The Daily Bagel** | 京 2 | 66 | 4.75 | **5** | 4 | 1 | **5** | 4 | **3.85** | 烘焙×简餐的高分单店 |
| 11 | **油梨树** | 京 17 | 47 | 4.29 | 4 | 3 | 3 | 4 | **5** | **3.65** | 极窄选址+中价的样本 |
| 12 | **萨莉亚** | 京 65 | 50 | 3.98 | 4 | 2 | **5** | 3 | **5** | **3.55** | 客单刚性的极致 |
```


#### S10 gold HTML · 互补关系矩阵

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 24
- genre: `diagnosis`

```
class: slide
chips: 壹 · 两套分析框架的对照与合并
h2: 1.2 互补关系矩阵
SOURCE: 苏帮袁 PPT 239

FRAMEWORK RECONCILIATION 
壹 · 两套分析框架的对照与合并 

1.2 互补关系矩阵

数据来源 / SOURCE 苏帮袁 PPT 239 页内容解构（七大板块）vs 本次分析要求的 5 大类 12 小项 

分析模块 苏帮袁框架 本次要求 关系 处理方式 
ABC + 二八 S1/S2 交集 ✅ ✅ 完全重合 沿用苏帮袁口径，第 4 章 
首选/必售/长尾三分类 ✅ ✅（加「观察品」） 本次更细 扩展为四分类，第 4 章 
额量比 / 千单点击 / 渗透率 ✅ ✅ 重合 沿用定义，第 5 章 
待下架三条标准 ✅ 隐含 苏帮袁独有 吸收为第 5 章筛选器，并加第 4 条（渗透率） 
3 - 4 - 2 - 1 结构树 ✅ ✅ 重合 第 6 章 
品类倾向指数 ✅ ✅ 重合 第 7 章，并补渗透率双指标 
价格带梯度 ✅ ✅（加「价格空档」） 本次更细 第 7 章，增加 10 元步长空档扫描 
小票 / 时段 / 区域 / RevPASH ✅ ✅ 重合 第 8 章 
连带与组合点单 ✅ ✅ 重合 第 8 章，增加提升度（lift）指标 
九宫格 味型×工艺 ✅ ✅ 重合 第 10 章 
九宫格 味型× 食材 ❌ ✅ 本次补强 第 10 章新增 
表续 1 / 2

清水亭 · 产品结构诊断 · TIANSIGHT 24 / 296

--- tables (first rows) ---

| 分析模块 | 苏帮袁框架 | 本次要求 | 关系 | 处理方式 |
|---|---|---|---|---|
| ABC + 二八 S1/S2 交集 | ✅ | ✅ | 完全重合 | 沿用苏帮袁口径，第 4 章 |
| 首选/必售/长尾三分类 | ✅ | ✅（加「观察品」） | 本次更细 | 扩展为四分类，第 4 章 |
| 额量比 / 千单点击 / 渗透率 | ✅ | ✅ | 重合 | 沿用定义，第 5 章 |
| 待下架三条标准 | ✅ | 隐含 | 苏帮袁独有 | 吸收为第 5 章筛选器，并加第 4 条（渗透率） |
| 3 - 4 - 2 - 1 结构树 | ✅ | ✅ | 重合 | 第 6 章 |
| 品类倾向指数 | ✅ | ✅ | 重合 | 第 7 章，并补渗透率双指标 |
| 价格带梯度 | ✅ | ✅（加「价格空档」） | 本次更细 | 第 7 章，增加 10 元步长空档扫描 |
| 小票 / 时段 / 区域 / RevPASH | ✅ | ✅ | 重合 | 第 8 章 |
| … | (3 more rows omitted) |
```


#### S11 gold HTML · 味型×工艺九宫页

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 172
- genre: `diagnosis`

```
class: slide
chips: 拾 · 九宫格：味型 × 工艺 / 味型 × 食材
h2: 10.2 味型 × 工艺九宫格
SOURCE: 品项汇总新版·索引表的味型、工艺、食材分类字段
TAKEAWAY: 最强集群：咸鲜 × 慢工艺

NINE-GRID MATRIX 
拾 · 九宫格：味型 × 工艺 / 味型 × 食材 

10.2 味型 × 工艺九宫格

数据来源 / SOURCE 品项汇总新版·索引表的味型、工艺、食材分类字段 

味型组：辣/麻（含辣、麻字样）｜甜/酸（含甜、酸、甘字样）｜咸鲜/本味/香（其余）
工艺组：快工艺（炒、油爆、炕炒、炕、干煸、煎、凉拌、搓、浇汁）｜慢工艺（炖、烧、煮、浸煮、卤、热卤、烩、熟醉、浸泡）｜特殊工艺（蒸、清蒸、烤、炸等）
SKU 数分布
味型 ＼ 工艺 快工艺 慢工艺 特殊工艺 合计 
咸鲜/本味/香 16 24 17 57 
甜/酸 4 3 5 12 
辣/麻 8 13 0 21 
合计 28 40 22 90 
销售额分布（万元，口径 A）
味型 ＼ 工艺 快工艺 慢工艺 特殊工艺 合计 
咸鲜/本味/香 ¥181.5 ¥402.1 ¥164.3 ¥747.9 
甜/酸 ¥27.5 ¥10.5 ¥42.3 ¥80.3 
辣/麻 ¥74.6 ¥347.0 ¥0.0 ¥421.6 
合计 ¥283.6 ¥759.6 ¥206.6 ¥1,249.8 
销量分布
本节要点 / KEY INSIGHT 最强集群：咸鲜 × 慢工艺 （ 24 款， ¥402.1 万， 32.2% 销售额）。铫子煨汤、鱼头、鱼杂煲等核心产品全部落在这一格，构成清水亭的技术护城河。 

清水亭 · 产品结构诊断 · TIANSIGHT 172 / 296

--- tables (first rows) ---

| 味型 ＼ 工艺 | 快工艺 | 慢工艺 | 特殊工艺 | 合计 |
|---|---|---|---|---|
| 咸鲜/本味/香 | 16 | 24 | 17 | 57 |
| 甜/酸 | 4 | 3 | 5 | 12 |
| 辣/麻 | 8 | 13 | 0 | 21 |
| 合计 | 28 | 40 | 22 | 90 |

| 味型 ＼ 工艺 | 快工艺 | 慢工艺 | 特殊工艺 | 合计 |
|---|---|---|---|---|
| 咸鲜/本味/香 | ¥181.5 | ¥402.1 | ¥164.3 | ¥747.9 |
| 甜/酸 | ¥27.5 | ¥10.5 | ¥42.3 | ¥80.3 |
| 辣/麻 | ¥74.6 | ¥347.0 | ¥0.0 | ¥421.6 |
| 合计 | ¥283.6 | ¥759.6 | ¥206.6 | ¥1,249.8 |
```


#### Budget · 九宫 SKU 数

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L1944–L1951
- genre: `diagnosis`
- note: retired fill id state-matrix

```
### SKU 数分布

| 味型 ＼ 工艺 | 快工艺 | 慢工艺 | 特殊工艺 | 合计 |
|---|---:|---:|---:|---:|
| 咸鲜/本味/香 | 16 | **24** | 17 | **57** |
| 甜/酸 | 4 | 3 | 5 | 12 |
| 辣/麻 | 8 | 13 | **0** | 21 |
| **合计** | **28** | **40** | **22** | **90** |
```


#### Budget · 迁移矩阵 4×4

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L736–L742
- genre: `diagnosis`
- note: retired fill id state-matrix

```
| 标准价口径 ＼ 实收口径 | 必售品 | 观察品 | 长尾品 | 首选品 | 合计 |
|---|---:|---:|---:|---:|---:|
| **必售品** | 15 | 0 | 0 | 4 | 19 |
| **观察品** | 2 | 12 | 0 | 1 | 15 |
| **长尾品** | 0 | 7 | 15 | 0 | 22 |
| **首选品** | 0 | 0 | 0 | 23 | 23 |
| **合计** | 17 | 19 | 15 | 28 | 79 |
```


<a id="l2-compare"></a>

### L2 `compare`

- L1 shell: `body`
- workshop map: compare / timeline / diagram
- slots: left · therefore · right (or stage playbook / learn-don't)
- table budget: 2 cols or 1–3 profile cards
- samples: 15 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 briefing · V0.1 vs V1.0 对照

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L11–L26
- genre: `briefing`

```
## 版本说明 · 本次更新了什么

V0.1 提交时，第十部分只给出了"北京 16 万家餐厅数据该怎么用"的**方案**。本次该方案已完整执行，形成 6052 家北京西式门店的参考集，并按合生汇锚点切出四层竞争环带。**数据回填后，初稿中有 6 处结论被修正、3 处被推翻、1 处发生战略级重构。**

| # | V0.1 的说法 | V1.0 的结论 | 性质 |
|---|---|---|---|
| 1 | "55–60 元是价格空档，需数据证伪" | ✅ 空档成立，但**性质完全不同**：在西餐大盘是稀薄带，在汉堡品类是无人区（97.8% 的汉堡门店在 55 元以下） | 修正 |
| 2 | "同一品牌在合生汇人均只有其他商场一半" | ❌ **数据不支持**。8 个可比品牌的合生汇店 vs 同品牌北京其他门店，客单中位数差 **−0.5 元** | 推翻 |
| 3 | "合生汇是高流量×中低客单的商场" | ⚠️ **需分层**：B1/B2/21 街区中位 35.5 元，楼上中位 55 元。是两个商场，不是一个 | 修正 |
| 4 | "披萨窑炉是最不可复制的产线，建议二店起收敛" | 🔴 **战略级重构**。北京数据显示：人均 45 元以上还能开到 20 家店的西式品牌，**8 个里有 6 个是披萨/意式，0 个是汉堡** | 推翻 |
| 5 | "档口 17–19 人需客户澄清口径" | ✅ **施工图已给出答案**：后厨总面积约 63㎡、热厨房 33.5㎡，物理上不可能同时站 18 人 | 已解决 |
| 6 | "蓝蛙是最直接的场内对手" | ⚠️ 蓝蛙人均 136 元，不构成价格竞争。**真正的对手是 Shake Shack 合生汇店（62 元 / 4.3 分 / 6305 评论）** | 修正 |
| 7 | — | 🆕 **新发现：客户在合生汇 B2 层已有一家门店**——石头先生的烤炉（朝阳合生汇旗舰店），13831 条评论、评分 3.9 | 新增 |
| 8 | "精品汉堡赛道退潮" | ✅ 成立，并找到机理：**60 元以上的独立汉堡店，40% 靠酒饮支撑**，不做酒的汉堡店天花板就在 55–60 | 深化 |
| 9 | "人均不过 70" | ✅ 数据支持，且给出更硬的锚：**Shake Shack 合生汇店 62 元**，这是场内消费者已经验证过的价格 | 深化 |
| 10 | 竞争分析为定性描述 | 🆕 全部替换为量化：分环、分楼层、分价格带、分品牌规模 | 升级 |
```


#### S2 diagnosis · 系列级双口径 + 折让率

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L762–L787
- genre: `diagnosis`

```
### 系列级双口径对比

| 系列 | 标准价额（72天） | 标准占比 | 实收额（30天） | 实收占比 | 差异 | 折让率 |
|---|---:|---:|---:|---:|---:|---:|
| 湖北烟火热菜 | ¥3,225,838 | 20.8% | ¥1,619,000 | 20.7% | −0.1pt | 0.4% |
| 招牌淡水鱼鲜 | ¥3,052,266 | 19.6% | ¥1,417,055 | 18.1% | −1.5pt | 2.1% |
| 套餐 | ¥2,604,620 | 16.8% | ¥1,218,189 | 15.6% | −1.2pt | −1.3% |
| 时令小龙虾 | ¥1,884,474 | 12.1% | ¥1,114,648 | **14.2%** | **+2.1pt** | **−49.9%** |
| 湖北煨汤 | ¥1,737,754 | 11.2% | ¥718,168 | 9.2% | −2.0pt | −16.0% |
| 小吃点心主食 | ¥795,692 | 5.1% | ¥383,069 | 4.9% | −0.2pt | 9.1% |
| 凉菜/卤味 | ¥699,216 | 4.5% | ¥366,878 | 4.7% | +0.2pt | 10.5% |
| 自制饮品甜品 | ¥558,716 | 3.6% | ¥240,037 | 3.1% | −0.5pt | −35.8% |
| 蒸菜 | ¥476,836 | 3.1% | ¥225,681 | 2.9% | −0.2pt | 1.6% |
| 洪湖莲藕系列 | ¥395,728 | 2.5% | ¥198,182 | 2.5% | 0.0pt | 1.2% |
| 酒水（口径A已排除） | — | — | ¥131,326 | 1.7% | — | 2.8% |
| 时令小龙虾/配菜 | ¥99,060 | 0.6% | ¥64,481 | 0.8% | +0.2pt | 1.5% |

🔑 **关键结论**

1. **双口径一致率 82.3%**，结构性结论稳健。以标准价口径做菜单结构决策，误差在可接受范围。
2. **两个口径必须分开看的品类是时令小龙虾**：按斤计价使实收比标准价高出 49.9%，实收口径下它是全店第一大单品（¥548,781，7.02%），标准价口径下排第四。任何按标准价评估小龙虾贡献的做法都会低估约一半。
3. **凉菜/卤味折让率 10.5%、小吃点心主食 9.1%** 为全店最高，说明这两个品类的优惠券/团购核销集中。武汉卤鸭拼盘单品折让率 25.5%（标准价 ¥59 → 实收均价 ¥43.9），是全店折让最重的正价菜。
4. **外婆巧手火烧馍折让率 31.9%**（标准价 ¥19 → 实收均价 ¥15.5），结合第 8 章国贸店 99.7% 的鱼头连带率，判断该品在国贸以搭赠形式随鱼头出品。
5. 自制饮品甜品折让率 −35.8% 属于规格聚合伪影（杯/扎混合），需在品项 + 规格级重算，本报告不作单独结论。

📊 **推荐图表**：帕累托双轴图（柱 = 各 SKU 销售额，折线 = 累计占比，标注 80% 与 97% 分界）；S1/S2 韦恩图（40 / 41 / 交集 30）；双口径排名变动斜率图（Slope chart，左轴标准价排名，右轴实收排名）；系列折让率条形图（正负双向）。
```


#### S3 diagnosis · 框架对照 苏帮袁 vs 本次要求

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L210–L237
- genre: `diagnosis`

```
## 1.1 框架对照

📂 **数据来源**：苏帮袁 PPT 239 页内容解构（七大板块）vs 本次分析要求的 5 大类 12 小项

### 苏帮袁框架（方法论供给方）

| 板块 | 页码 | 核心内容 |
|---|---|---|
| 一、方法论与门店认知诊断 | p.1–34 | 君臣佐使六步法、ABC 表、二八原则、S1/S2 集合、待下架三条标准、核心记忆点剥离 |
| 二、现状与产品矩阵 | p.35–73 | 87 SKU 品类分布、产品结构树、3-4-2-1 理想结构、板块价格带梯度、单品深度分析 |
| 三、产品呈现与经营数据 | p.74–99 | 汤品呈现、小票单据汇总、区域运营效率、午晚市差异、连带与组合点单 |
| 四、市场趋势与竞品对标 | p.100–138 | 外出就餐趋势、九宫格味型贡献、商圈格局、黑珍珠米其林、竞对矩阵 |
| 五、核心产品落地形态创意 | p.139–173 | 品类热度、时令稀缺体系、特色类工艺/规格策略、行动清单优先级矩阵 |
| 六、点心与价格带延展 | p.174–204 | 四季点心选品、166–200 元价格带菜单对标 |
| 七、落地与客单验证 | p.205–239 | 需求思维、产品规划、对标店客单反证、品牌生命周期四阶段 |

### 本次分析要求（问题定义方）

| 编号 | 分析项 | 苏帮袁对应页 |
|---|---|---|
| 1 | ABC 贡献 + 二八排序，S1/S2 及交集 → 首选/必售/观察/长尾 + 主辅佐引 | p.13–21、p.33、p.36 |
| 1b | 额量比、千单点击、毛利率、渗透率 | p.21、p.24、p.25、p.43–45 |
| 2 | 菜单结构树 + 3-4-2-1 理想结构 | p.37、p.39、p.40 |
| 3 | 品类倾向系数、价格带、价格空档、客单组合、小票时间与座位、复购率 | p.42、p.48、p.55、p.58、p.82、p.94、p.99、p.108–109 |
| 4 | 味型×工艺、味型×食材九宫格、季节性矩阵、生命周期 | p.110–114、p.142–148 |
| 5 | 商圈、竞品菜单低中高对比、品类/区域榜单、门店品牌对标 | p.117–138、p.184–199 |

## 1.2 互补关系矩阵
```


#### S4 system · 君臣佐使 vs Menu Engineering

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L853–L877
- genre: `system`

```
## 5.2 M3+M5 君臣佐使与 Menu Engineering：两套体系的对撞与融合

**中式源头** 《黄帝内经·素问》「主病之谓君，佐君之谓臣，应臣之谓使」——方剂配伍的四种功能角色。餐饮借用后，「君臣佐使」/「主辅佐引」成为**功能定位**框架：不问单品好坏，问它在整桌中承担什么职能。

**西式源头** **Kasavana & Smith（1982）Menu Engineering**——康奈尔学派，用两个轴切四象限：

| Kasavana-Smith 原名 | 直译 | 定义 | 本体系对应 |
|---|---|---|---|
| **Stars** | 明星 | 高人气 + 高贡献毛利 | A17 明星品 |
| **Plowhorses** | 犁马 | 高人气 + 低贡献毛利 | A17 流量品 |
| **Puzzles** | 谜题 | 低人气 + 高贡献毛利 | A17 利润黑马 |
| **Dogs** | 瘦狗 | 低人气 + 低贡献毛利 | A17 淘汰候选 |

**两套体系的根本差异**

| | 君臣佐使（主辅佐引） | Menu Engineering |
|---|---|---|
| 视角 | **组合视角**——一桌菜是一个整体 | **单品视角**——每道菜独立评分 |
| 问题 | 这道菜在整桌里干什么？ | 这道菜赚不赚钱、卖不卖得动？ |
| 强项 | 指导**点单引导**与**菜单叙事** | 指导**保留/淘汰/调价** |
| 盲点 | 无法量化，易主观漂移（本次 28% 分歧） | 忽略连带效应——低毛利的「引」可能带动高毛利的「主」 |

**融合方式（本体系的做法）** 用 Menu Engineering 的量化指标去**校验**君臣佐使的定性判断（A08 → A09）。角色是「应该是什么」，四象限是「实际是什么」，两者的差就是错配清单。这一步是本体系相对两个原始框架的增量。

**关键修正** Kasavana-Smith 原版用「贡献毛利额」（Contribution Margin = 售价 − 变动成本）而非「毛利率」。本次因缺动态成本卡而用毛利率替代——**这是「大份高毛利」误判的根源**，因为毛利率忽略了大份的绝对毛利额更高。补齐 D7 成本维度后应切回 CM。
```


#### S5 dossier · Wagas 该学 / 不该学

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L373–L405
- genre: `dossier`

```
### 🥇 C1 · Wagas 沃歌斯 —— "品质西式简餐能开多大"的天花板样本

| 指标 | 数值 |
|---|---|
| **北京门店** | **53 家**（归一化后；未归一化会误计为 47） |
| 人均中位 | **78 元**（区间 67–88） |
| 平均评分 | **4.50** |
| ≥4.5 分门店占比 | **62%** |
| 客单变异 CV | **5.6%**（极稳定） |
| 评分标准差 | 0.20 |
| 单店评论中位 | **1,619** |
| 评论总量 | 95,244 |
| 覆盖 | 9 个行政区 / 43 个商圈 |
| 空间形态 | **商场 15 家 vs 非商场 38 家** |

**门店分布：** 朝阳 18、海淀 10、东城 6、西城 6、大兴 5、昌平 3、丰台 3、石景山 1

**TOP 门店：** 来福士（78/4.6/5,338）、国瑞城（84/4.7/4,742）、富力广场双井（82/4.6/4,211）、五道口购物中心（78/4.2/3,878）、君太百货（79/4.7/3,413）

#### ✅ 该学什么

| 学什么 | 具体 |
|---|---|
| **写字楼底商模型** | 38/53 家不在商场。工作日午餐刚需 > 周末逛街偶发 |
| **客单一致性** | CV 5.6%——53 家店人均全部落在 67–88 元，说明产品结构与套餐设计高度标准化 |
| **全时段结构** | 早餐/午餐/下午茶/晚餐都有产品，摊薄租金 |
| **"健康"作为品类词而非形容词** | Wagas 把"健康"做成了品类（沙拉碗、三明治、意面），不是贴在汉堡上的标签 |
| **单店评论 1,619 的量级** | 这是"品质连锁"单店客流的合理基准，建议作为石头先生 12 个月目标 |

#### ❌ 不该学什么

- **不要学它的品类结构。** Wagas 的核心是沙拉/意面/三明治，与"汉堡"心智相冲突（且北京"轻食沙拉"品类评分仅 3.60）
- **不要学它 78 元的定价。** 它靠的是全时段与轻食心智，不是单一重餐
```


#### S6 dossier · 分阶段该看谁

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L982–L990
- genre: `dossier`

```
## 6.3 分阶段的"该看谁"

| 石头先生所处阶段 | 首要研究对象 | 研究什么 |
|---|---|---|
| **1 家（首店）** | Shake Shack 合生汇店、必胜客大郊亭桥店、萨莉亚合生汇店 | 出餐速度、套餐结构、菜单版位、明档可见性 |
| **2–5 家** | **BAKER&SPICE、油梨树** | 极窄选址逻辑、单店评论爬坡曲线、客单一致性 |
| **6–15 家** | **Wagas、Tubestation** | 商圈覆盖策略（一商圈一店）、品控标准差控制 |
| **16–30 家** | **魏斯理、必胜客 WOW** | 中央工厂堡胚方案、店型分化、跨城打法 |
| **31–50 家** | **超级碗 FOODBOWL、THE WOODS** | 轻量店型、双店型品牌复用 |
```


#### S7 dossier · 六大品牌原型

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L187–L199
- genre: `dossier`

```
## 2.3 六大品牌原型

把 130 个可识别品牌按"商业模式"而非"品类"分类，得到六个原型。**石头先生的路径，实际上是在其中三个原型之间做选择。**

| 原型 | 定义 | 代表 | 规模能力 | 与石头先生的关系 |
|---|---|---|---|---|
| **A · 效率规模型** | 标准化到极致，低价高频，加盟为主 | 麦当劳、肯德基、华莱士、塔斯汀、赛百味 | ★★★★★ 万店 | 学供应链与 SOP，不学定位 |
| **B · 中价连锁型** | 品类清晰、堂食为主、直营+特许 | 必胜客、达美乐、萨莉亚、棒约翰 | ★★★★ 百至千店 | 🔴 **人均最接近，学产品结构与店型分化** |
| **C · 品质简餐型** | 中高价、高分、只在高线商圈 | **Wagas、BAKER&SPICE、Tubestation、超级碗、油梨树** | ★★★ 30–60 店 | 🔴🔴 **模式最接近，是本报告的核心参照组** |
| **D · 精品单品型** | 单一强产品、店数少、高话题 | Shake Shack、和牛怪物汉堡、He BURGER、Take A Bite | ★★ 2–10 店 | 学产品与内容，不学规模路径 |
| **E · 场景体验型** | 高客单、空间与氛围为核心 | gaga、蓝蛙、THE WOODS、叫板比萨、Lily's | ★★ 3–17 店 | 学空间与出片，不学定价 |
| **F · 流量自助型** | 自助/高性价比、极高单店客流 | 比格比萨自助、好伦哥、西堤牛排 | ★★★ 9–84 店 | 学单店客流的做法 |
```


#### S8 roadmap · S0 阶段卡片 (命题/不可逆/死法/Gate)

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1048–L1108
- genre: `roadmap`

```
## 8.1 S0 · 开业前 90 天：把不可逆的事做对

### 阶段命题
> **开业前能改的东西，开业后大多改不了。这 90 天的价值高于之后的 12 个月。**

### 不可逆事项清单（按不可逆程度排序）

| 事项 | 不可逆程度 | 现状 | 截止 |
|---|---|---|---|
| **后厨布局与明档落位** | 🔴🔴🔴 极高（拆改成本巨大） | 施工图未落实烘焙展示区与窑炉 | 施工前 |
| **品牌名与主视觉** | 🔴🔴🔴 | 已定 | — |
| **英文口号与包材文案** | 🔴🔴 印刷后不可逆 | 手册内部有两套英文口号 | 出图前 |
| **物业硬件（电容/排烟/明火）** | 🔴🔴🔴 | 未确认 | 签约前 |
| 菜单结构 | 🔴 可改但成本高 | 已给建议 | 8.15 |
| 定价 | 🟡 可改（涨价难，降价易） | 已给建议 | 8.15 |
| POS 与数据字典 | 🔴 后补极痛苦 | 待建 | 开业前 |

### 关键动作（按问题域）

**D2 产品与菜单**
- 菜单收敛至 28 款（食品 20 + 饮品 8）
- 补三款：小份经典堡 26、基础披萨 38–42、堡胚零售
- 冻结沙拉研发管线 7 款
- 完成 39 款产品的标准配方卡（克重、SOP、出品标准图）

**D3 单店经济模型**
- 🔴 **澄清毛利率口径**（是否含包材与损耗）
- 建立完整 UE 模型：投资额、月度 P&L、坪效人效、回本进度、现金流五张表
- 设定盈亏平衡点：日均客次 ×、日均营业额 ×

**D4 运营效率**
- 🔴 **出餐压测**：60 分钟 80 单，8 分钟出餐率 ≥85%，无单超 15 分钟
- SOP 验收：新员工照 SOP 独立操作合格率 ≥90%
- TOC 首轮瓶颈识别与配置调整

**D1 品牌心智**
- 统一英文口号为 BURGER, DONE RIGHT.
- 修正 RTB 表述（"米其林三星厨房出身 · 前 GUCCI 1921 上海行政总厨"）
- 🔴 **第一信任状从"现烤堡胚"迁移至"现绞原切牛肉"**（§6.1）
- 门头副标定为「现绞 · 现烤 · 现煎」

**D5 增长**
- 烤炉店口碑修复启动（目标 3.9 → 4.2）
- 三平台建档：点评、抖音、外卖（外卖 D15 后上线）
- 5 个套餐上线，含 39 元入门套餐

**数据基础**
- 🔴 **数据字典定稿**
- POS 配置：确保能导出订单级明细
- 看板 V1 模板就位

### 我方赋能交付物
菜单结构定稿 · 定价方案 · 五套餐设计 · 数据字典 · 看板 V1 · 出餐压测方案与执行 · 口味盲测报告 · 明档落位建议 · 品牌话语体系修订 · 开业营销日历

### 典型死法
- 后厨按"什么都能做"设计，开业后发现出餐慢，且改不了
- 包材已印，发现口号有错别字
- 开业后才发现 POS 导不出订单级明细，第一个月数据全废

### 进入 S1 的准入条件
✅ 压测达标　✅ 数据字典定稿　✅ 菜单定稿　✅ SOP 验收通过　✅ 明档三件事落位
```


#### S9 roadmap · Playing to Win 五问

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L177–L190
- genre: `roadmap`

```
### ① Playing to Win 五问级联（Lafley & Martin）

**回答：** 战略到底是什么？
**为什么选它：** 它强制把战略变成五个**互相约束**的选择，而不是一堆愿景词。

| 五问 | 本项目的答案（第七部分详述） |
|---|---|
| 1. 制胜抱负是什么 | 成为"精品西式简餐"品类的定义者与规模第一 |
| 2. 在哪里竞争 | 一线/新一线核心商圈 × 人均 55–65 元 × 全时段简餐 |
| 3. 如何取胜 | 用"看得见的现做"建立信任状，用披萨与烘焙承载规模 |
| 4. 需要什么能力 | 明档运营力、堡胚烘焙力、菜单收敛力、数据决策力 |
| 5. 需要什么管理系统 | 三大智能体系 + Stage Gate 治理 |

**失效边界：** 它假设你知道市场边界。在品类未定义时（本项目正是），需先用 JTBD 补充。
```


#### S10 roadmap · JTBD 四任务

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L192–L207
- genre: `roadmap`

```
### ② Jobs-to-be-Done（Christensen）

**回答：** 顾客"雇佣"我们去完成什么任务？
**为什么选它：** 它把竞争对手的定义从"同品类"扩展到"同任务"——这对本项目至关重要。

**本项目的四个核心 Job：**

| Job | 场景 | 真实竞争对手 | 胜出条件 |
|---|---|---|---|
| **J1 一个人的工作日午餐** | 工作日 11:30–13:30 | 不是别的汉堡店，是**便利店、米饭快餐、外卖** | 快 + 不难吃 + 不贵 |
| **J2 和朋友吃点好的但不隆重** | 周末、下班后 | 烤鱼、日料、茶餐厅 | 氛围 + 分享性 + 出片 |
| **J3 带孩子吃一顿西餐** | 周末家庭 | 必胜客、萨莉亚 | 儿童友好 + 家长不心疼 |
| **J4 犒赏自己/尝个鲜** | 随机 | 网红餐厅、探店清单 | 话题性 + 内容 |

> **JTBD 给出的最重要洞察：J1（工作日午餐）的对手是便利店和米饭快餐，不是 Shake Shack。**
> **这意味着"日常入口款"和"出餐速度"的战略地位，高于"招牌款"和"食材等级"。**
```


#### S11 gold HTML 框架对照页

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 22
- genre: `diagnosis`

```
class: slide
chips: 壹 · 两套分析框架的对照与合并
h2: 1.1 框架对照
SOURCE: 苏帮袁 PPT 239

FRAMEWORK RECONCILIATION 
壹 · 两套分析框架的对照与合并 

1.1 框架对照

数据来源 / SOURCE 苏帮袁 PPT 239 页内容解构（七大板块）vs 本次分析要求的 5 大类 12 小项 

苏帮袁框架（方法论供给方）
板块 页码 核心内容 
一、方法论与门店认知诊断 p.1– 34 君臣佐使六步法、ABC 表、二八原则、S1/S2 集合、待下架三条标准、核心记忆点剥离 
二、现状与产品矩阵 p.35– 73 87 SKU 品类分布、产品结构树、 3 - 4 - 2 - 1 理想结构、板块价格带梯度、单品深度分析 
三、产品呈现与经营数据 p.74– 99 汤品呈现、小票单据汇总、区域运营效率、午晚市差异、连带与组合点单 
四、市场趋势与竞品对标 p.100– 138 外出就餐趋势、九宫格味型贡献、商圈格局、黑珍珠米其林、竞对矩阵 
五、核心产品落地形态创意 p.139– 173 品类热度、时令稀缺体系、特色类工艺/规格策略、行动清单优先级矩阵 
六、点心与价格带延展 p.174– 204 四季点心选品、 166 – 200 元价格带菜单对标 
七、落地与客单验证 p.205– 239 需求思维、产品规划、对标店客单反证、品牌生命周期四阶段 
本次分析要求（问题定义方）

清水亭 · 产品结构诊断 · TIANSIGHT 22 / 296

--- tables (first rows) ---

| 板块 | 页码 | 核心内容 |
|---|---|---|
| 一、方法论与门店认知诊断 | p.1– 34 | 君臣佐使六步法、ABC 表、二八原则、S1/S2 集合、待下架三条标准、核心记忆点剥离 |
| 二、现状与产品矩阵 | p.35– 73 | 87 SKU 品类分布、产品结构树、 3 - 4 - 2 - 1 理想结构、板块价格带梯度、单品深度分析 |
| 三、产品呈现与经营数据 | p.74– 99 | 汤品呈现、小票单据汇总、区域运营效率、午晚市差异、连带与组合点单 |
| 四、市场趋势与竞品对标 | p.100– 138 | 外出就餐趋势、九宫格味型贡献、商圈格局、黑珍珠米其林、竞对矩阵 |
| 五、核心产品落地形态创意 | p.139– 173 | 品类热度、时令稀缺体系、特色类工艺/规格策略、行动清单优先级矩阵 |
| 六、点心与价格带延展 | p.174– 204 | 四季点心选品、 166 – 200 元价格带菜单对标 |
| 七、落地与客单验证 | p.205– 239 | 需求思维、产品规划、对标店客单反证、品牌生命周期四阶段 |
```


#### S12 gold HTML 合并体系

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 27
- genre: `diagnosis`

```
class: slide
chips: 壹 · 两套分析框架的对照与合并
h2: 1.3 合并后的分析体系
SOURCE: 苏帮袁 PPT 239

FRAMEWORK RECONCILIATION 
壹 · 两套分析框架的对照与合并 

1.3 合并后的分析体系

数据来源 / SOURCE 苏帮袁 PPT 239 页内容解构（七大板块）vs 本次分析要求的 5 大类 12 小项 

两套框架合并后形成 13 个模块、 4 个层级 ：
L1 认知层（我是谁）
├── M1 数据地图与口径 ← 本次新增
├── M2 经营基本盘（六店对比）
└── M3 主辅佐引角色定义与校验 ← 苏帮袁「君臣佐使」+ 本次数据校验

L2 结构层（卖什么）
├── M4 ABC + 二八 S1/S2 交集 ← 两套重合
├── M5 四大单品指标 + 待下架/高潜 ← 苏帮袁三条标准 + 本次渗透率
├── M6 菜单结构树 3-4-2-1 ← 两套重合
└── M7 品类倾向 + 价格带 + 空档 ← 苏帮袁 + 本次空档扫描

L3 行为层（怎么卖）
├── M8 客单组合 + 小票 + 时段座位 ← 两套重合 + 提升度
├── M9 复购与客户资产 ← 本次补强
└── M10 九宫格 味型×工艺/食材 ← 苏帮袁 + 本次食材维度

L4 战略层（往哪走）
├── M11 季节性矩阵 + 生命周期 ← 本次补强
├── M12 商圈 + 竞品 + 榜单 + 对标 ← 苏帮袁强项（本次数据待补）
└── M13 行动清单 + 效益预测 ← 苏帮袁 + 本次量化 关键结论 / KEY INSIGHTS 

推荐图表 / CHARTS 框架对照韦恩图（两圆重叠 + 各自独有清单）， 13 模块四层级架构图，模块 × 数据源依赖矩阵热力图。 

清水亭 · 产品结构诊断 · TIANSIGHT 27 / 296
```


#### Budget · 系列双口径

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L762–L777
- genre: `diagnosis`
- note: retired fill id dual-calibre

```
### 系列级双口径对比

| 系列 | 标准价额（72天） | 标准占比 | 实收额（30天） | 实收占比 | 差异 | 折让率 |
|---|---:|---:|---:|---:|---:|---:|
| 湖北烟火热菜 | ¥3,225,838 | 20.8% | ¥1,619,000 | 20.7% | −0.1pt | 0.4% |
| 招牌淡水鱼鲜 | ¥3,052,266 | 19.6% | ¥1,417,055 | 18.1% | −1.5pt | 2.1% |
| 套餐 | ¥2,604,620 | 16.8% | ¥1,218,189 | 15.6% | −1.2pt | −1.3% |
| 时令小龙虾 | ¥1,884,474 | 12.1% | ¥1,114,648 | **14.2%** | **+2.1pt** | **−49.9%** |
| 湖北煨汤 | ¥1,737,754 | 11.2% | ¥718,168 | 9.2% | −2.0pt | −16.0% |
| 小吃点心主食 | ¥795,692 | 5.1% | ¥383,069 | 4.9% | −0.2pt | 9.1% |
| 凉菜/卤味 | ¥699,216 | 4.5% | ¥366,878 | 4.7% | +0.2pt | 10.5% |
| 自制饮品甜品 | ¥558,716 | 3.6% | ¥240,037 | 3.1% | −0.5pt | −35.8% |
| 蒸菜 | ¥476,836 | 3.1% | ¥225,681 | 2.9% | −0.2pt | 1.6% |
| 洪湖莲藕系列 | ¥395,728 | 2.5% | ¥198,182 | 2.5% | 0.0pt | 1.2% |
| 酒水（口径A已排除） | — | — | ¥131,326 | 1.7% | — | 2.8% |
| 时令小龙虾/配菜 | ¥99,060 | 0.6% | ¥64,481 | 0.8% | +0.2pt | 1.5% |
```


#### Budget · 侍天口径 A/B

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L73–L86
- genre: `system`
- note: retired fill id dual-calibre

```
# 第二部分　口径体系

| 口径 | 定义 | 数据源 | 覆盖 | 适用 | 禁用 |
|---|---|---|---|---|---|
| **A 标准价** | 销售额 = 标准售价 × 销量 | 索引表 | 6 店 · 72 天 · 40,840 台 | 菜单结构、定价、跨期可比 | 真实收入、折让分析 |
| **B 账单实收** | 销售额 = 账单行 `小计金额` | 账单明细 | 6 店 · 30 天 · 24,752 单 | 真实贡献、渗透、连带、时段 | 跨期趋势（仅 1 月） |

**三路对账（每日必跑）**

```
路径1  账单表头 Σ实收金额  = ¥7,842,874  ┐
路径2  账单明细 Σ小计金额  = ¥7,842,874  ┘ 必须相等（差额 = 0）
路径3  索引表 Σ标准售价×销量 = ¥15,533,304  差额 = 折让 + 期间差 + SKU 覆盖差
```
```


#### Budget · Wagas 档案

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L373–L405
- genre: `dossier`
- note: retired fill id profile-card

```
### 🥇 C1 · Wagas 沃歌斯 —— "品质西式简餐能开多大"的天花板样本

| 指标 | 数值 |
|---|---|
| **北京门店** | **53 家**（归一化后；未归一化会误计为 47） |
| 人均中位 | **78 元**（区间 67–88） |
| 平均评分 | **4.50** |
| ≥4.5 分门店占比 | **62%** |
| 客单变异 CV | **5.6%**（极稳定） |
| 评分标准差 | 0.20 |
| 单店评论中位 | **1,619** |
| 评论总量 | 95,244 |
| 覆盖 | 9 个行政区 / 43 个商圈 |
| 空间形态 | **商场 15 家 vs 非商场 38 家** |

**门店分布：** 朝阳 18、海淀 10、东城 6、西城 6、大兴 5、昌平 3、丰台 3、石景山 1

**TOP 门店：** 来福士（78/4.6/5,338）、国瑞城（84/4.7/4,742）、富力广场双井（82/4.6/4,211）、五道口购物中心（78/4.2/3,878）、君太百货（79/4.7/3,413）

#### ✅ 该学什么

| 学什么 | 具体 |
|---|---|
| **写字楼底商模型** | 38/53 家不在商场。工作日午餐刚需 > 周末逛街偶发 |
| **客单一致性** | CV 5.6%——53 家店人均全部落在 67–88 元，说明产品结构与套餐设计高度标准化 |
| **全时段结构** | 早餐/午餐/下午茶/晚餐都有产品，摊薄租金 |
| **"健康"作为品类词而非形容词** | Wagas 把"健康"做成了品类（沙拉碗、三明治、意面），不是贴在汉堡上的标签 |
| **单店评论 1,619 的量级** | 这是"品质连锁"单店客流的合理基准，建议作为石头先生 12 个月目标 |

#### ❌ 不该学什么

- **不要学它的品类结构。** Wagas 的核心是沙拉/意面/三明治，与"汉堡"心智相冲突（且北京"轻食沙拉"品类评分仅 3.60）
- **不要学它 78 元的定价。** 它靠的是全时段与轻食心智，不是单一重餐
```


<a id="l2-verdict"></a>

### L2 `verdict`

- L1 shell: `body`
- workshop map: verdict
- slots: 争议 / 事实 / 处理 / 证伪  or decision list
- table budget: 4 cells or decision list
- samples: 15 original excerpts (verbatim; not rewritten)

Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.

#### S1 diagnosis · F.1 争议四段 (gold A58)

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L3071–L3122
- genre: `diagnosis`

```
## F.1 删除 5,597 行小龙虾账单行（本报告争议最大的一次数据处理）

### 争议点

本报告从账单明细中**删除了 5,597 行、涉及 ¥830,889** 的数据，占删除前行合计的 9.6%。删除后小龙虾品类的销售额从 ¥1,945,537 降到 ¥1,114,648（−42.7%），全店堂食桌均从 ¥456.1 降到 ¥408.2（−10.5%）。

删数据是分析中最需要被质疑的动作。任何人都有理由问：**凭什么认为这 5,597 行是系统伪影，而不是真实销售？**

### 事实

**第一步：发现异常。** 按 `营业流水号 + 品项代码 + 数量 + 销售单价 + 小计金额` 五字段分组，全量 159,086 行中出现 8,209 个「一组多行」。若这些都是真实销售，意味着同一张账单在同一价格、同一数量下重复点了同一个品项——在正餐场景可能发生（比如加点一份米饭），因此不能直接删。

**第二步：把异常分成两类。** 关键的分辨依据是**组内 `规格` 字段是否相同**：

| 类型 | 组数 | 行数 | 涉及金额 | 组内规格 | 判定 |
|---|---:|---:|---:|---|---|
| A 类 | 5,562 | 11,308 | ¥1,665,134 | **互不相同** | 系统伪影 → 删 |
| B 类 | 2,647 | 5,627 | ¥113,331 | **完全相同** | 真实重复下单 → 留 |

**第三步：A 类为什么是伪影。** A 类只出现在三个品项上，其中小龙虾两款的规格取值呈现严格的成对镜像：

| 规格写法 | 全量行数 | 配对规格 | 全量行数 |
|---|---:|---|---:|
| `招牌虾99/（1斤起点）` | 3,716 | `招牌虾` | 3,716 |
| `精品虾159/斤（1斤起点）` | 1,717 | `精品虾` | 1,717 |
| `霸王虾229/（1斤起点）` | 164 | `霸王虾` | 164 |

三组数量**逐一精确相等**，且成对的两行在原始文件中**行号连续**（如第 96 / 97 行）、数量与金额完全一致、`单位` 字段同为 `招牌虾99/斤（1斤起点）`。这是 POS 导出时把同一条销售记录按「完整规格名」和「简写规格名」各写一次的典型特征，而非两次点单——真实的两次点单不会让全店三组规格的计数分毫不差。

**第四步：为什么 A 类里的武汉卤鸭拼盘不删。** 武汉卤鸭拼盘也有 114 行落入 A 类，但它的组内规格是 `九九卤鸭头` / `九九卤鸭脖` / `九九卤素拼`——这是**三种不同的实物**，同价同量，客人同时点两种完全合理。因此本报告只删除小龙虾两款的简写规格行，卤鸭拼盘全部保留。**判定依据不是「组内规格不同」这条机械规则，而是规格值本身是否指向同一实物。**

**第五步：独立验证。** 这是本处理成立与否的决定性证据：

| 口径 | 金额 | 与账单表头「实收金额」合计比较 |
|---|---:|---|
| 账单表头 `实收金额` 合计（独立字段，未参与清洗） | **¥7,842,874** | — |
| 删除前，账单行 `小计金额` 合计 | ¥8,673,763 | **虚高 ¥830,889（+10.6%）** |
| 删除后，账单行 `小计金额` 合计 | **¥7,842,874** | **完全吻合，差额 ¥0** |

账单表头的「实收金额」是收银系统在结账时写入的单据级金额，与明细行的写入路径相互独立。删除 5,597 行之后，两条独立路径的合计**精确对齐到个位数**。若这些行是真实销售，删除后行合计必然低于表头合计 ¥830,889。

### 本报告的处理

删除 `规格 ∈ {招牌虾, 精品虾, 霸王虾}` 的 5,597 行；保留全部 B 类同规格重复行与武汉卤鸭拼盘的多规格行。全报告口径 B 的所有数字均基于去重后数据。

### 证伪条件

出现以下任一情况，本处理即被推翻，需重新计算全部口径 B 数字：

1. 门店确认 POS 中「招牌虾」与「招牌虾99/（1斤起点）」是**两个独立可售 SKU**（例如一个是堂食、一个是外带）；
2. 收银系统供应商说明账单表头「实收金额」本身也存在同源重复，导致两条路径并非独立验证；
3. 提供任一张实体小票，其上小龙虾以两行分别打印且金额分别计入实收。
```


#### S2 diagnosis · 十条核心结论

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L2569–L2582
- genre: `diagnosis`

```
## 13.1 十条核心结论

| # | 结论 | 数据支撑 | 影响量级 |
|---|---|---|---|
| 1 | **主菜渗透率 46.7%，过半的桌不点招牌鱼鲜** | 8,731/16,867 桌零主菜，桌均低 ¥88.9 | 渗透率 +13.3pt ≈ 月增 ¥199,400 |
| 2 | **国贸店 6 月套餐销售为零，五店套餐桌均贡献 ¥74.1** | 套餐渗透率 国贸 0% vs 五店 27.4% | 国贸上线套餐 ≈ 月增 ¥100,000+ |
| 3 | **火烧馍-鱼头连带模型在国贸跑通（99.7%），五店仅 10.6%–17.0%** | 提升度 3.03，共现 1,281 桌 | 五店复制 ≈ 月增 ¥190,000+ |
| 4 | **长尾 SKU 占 32.2%，只贡献 3.1% 销售额** | 38 款长尾，其中 18 款为饮品甜品 | 精简 25 款，SKU −21.2%，损失 2.3% 销售额 |
| 5 | **6 月 17 日藕汤替换损失煨汤桌均 ¥13.4** | ¥115.7 → ¥38.3 均价，件数 +92.6% | 年化影响约 ¥272 万 |
| 6 | **同一菜品在两个门店组角色定义不一致（28.0%）** | 23/82 个品项 | 服务话术与陈列无法统一复制 |
| 7 | **¥200–260 存在 60 元价格空档** | ¥199 卖出 6,494 份，向上无承接 | 补 2 款宴请型主菜 |
| 8 | **辣/麻 × 特殊工艺 = 0 款；辣/麻 × 猪 = 0 款** | 九宫格唯一空白格 | 猪肉占 18.8% 销售额却无辣味做法 |
| 9 | **会员识别率 3.99%，复购率 17.6%** | 会员桌均比非会员高 52.9% | 识别率提升至 30% 是客户资产分析前提 |
| 10 | **大份规格曝光严重不足；毛利优势集中在三款鱼鲜** | 大份千单点击仅为例份的 12.1%；20 组配对中大份毛利更高仅 7 组（中位 −0.7pt），但油爆丹江活青虾 +14.1pt、油焖罗氏虾烧年糕 +7.2pt、公安鱼杂煲 +7.1pt | 定向推荐，非全菜单铺开（附录 F.19） |
```


#### S3 diagnosis · P0 行动清单

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L2584–L2596
- genre: `diagnosis`

```
## 13.2 行动清单（优先级矩阵）

### P0｜立即执行（0–30 天，低成本高确定性）

| # | 行动 | 责任 | 预期效益 | 验证指标 |
|---|---|---|---|---|
| 1 | **国贸店上线套餐**（复制五店的 ¥239/¥299/¥316 三档） | 运营 + 产品 | 月增 ¥100,000+ | 国贸套餐渗透率 → 20% |
| 2 | **五店复制火烧馍-鱼头捆绑机制**（点鱼头默认配馍，服务员话术 + POS 提示） | 运营 | 月增 ¥190,000+ | 五店鱼头桌带馍率 → 60% |
| 3 | **恢复藕汤多规格**（在 ¥39 按位基础上补回 ¥99 小份 / ¥169 大份） | 产品 | 挽回煨汤桌均 ¥13.4 | 煨汤桌均贡献 → ¥46 |
| 4 | **统一主辅佐引角色定义**（23 个分歧品项由产品委员会裁定，全司一套） | 产品委员会 | 执行一致性 | 分歧品项数 → 0 |
| 5 | **建立 SKU 上下架台账**（每次变更记录日期、原因、替代品） | 产品 | 生命周期可追踪 | 台账覆盖率 100% |
| 6 | **下架 17 款命中 3 条标准的产品**（保留孝感米酒脆粑冰淇淋做曝光测试） | 产品 | SKU −14.4%，损失 2.3% 销售额 | 厨房出品时长下降 |
| 7 | **会员识别率提升**（扫码点餐强制绑定手机号 + 首单立减权益） | 数字化 | 样本量 ×7.5 | 识别率 → 30% |
```


#### S4 system · A58 证伪登记 + 三轮战果

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L804–L829
- genre: `system`

```
### A58 结论审查与证伪登记　★★★★★
每处「分析师判断」而非「数据直出」的结论，登记四段：**争议点 / 事实 / 处理 / 证伪条件**

**强制检查清单（每次出报告前）**

```
□ 所有表格的行合计 = 表内标注的合计？
□ 所有分类的 SKU 数之和 = 全量？
□ 文中出现「约」「大致」的地方，是否真算过？
□ 只给了计数的结论，是否列了名录？
□ 同一指标在不同章节的分母是否一致？
□ 图表数值是否逐一回溯源数据（而非从正文抄或区间插值）？
□ 枚举型字段是否穷举了全部取值？
□ 多源合并时是否用「取非空值」而非「取第一条」？
```

**样例：清水亭三轮审查战果**

| 轮次 | 触发 | 发现 | 其中方向性错误 |
|---|---|---:|---:|
| 一 | 主动审查争议点 | 3 | 3（大份毛利、2 人桌口径、小龙虾退潮） |
| 二 | 客户追问「还有其他错误吗」 | 8 | 5（食材覆盖率、矩阵缺列、明细漏行…） |
| 三 | 客户指出某页省略过度 | 3 | 2（生命周期未实算、四象限边界） |
| **合计** | — | **14** | **10** |

**价值** 这 8 条清单能拦住上述 14 处错误中的全部
```


#### S5 briefing · 需当场决策清单

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L2069–L2089
- genre: `briefing`

```
# 第十一部分 · 需当场决策清单

| # | 决策事项 | 我方建议 | 不决策的后果 | 截止 |
|---|---|---|---|---|
| **1** | 🔴 **战略路径：汉堡单核 vs 汉堡心智+披萨烘焙双载体** | **双载体**（§1.2），以 D60 披萨渗透率 25% 为判定线 | 菜单结构、窑炉投资、二店方案全部无依据 | **8.15** |
| **2** | 🔴 **三大明档的施工落位**（烘焙展示区与窑炉位置） | 烘焙展示区放入口右侧；窑炉需物业硬件确认 | 品牌承诺落空，58 元定价失去支撑物 | **8.15** |
| **3** | 首店楼层 | **L1（与 Shake Shack/gaga/蓝蛙同层）** | 选 B1/B2 将面临 35.5 元客单参照系 | 8.15 |
| **4** | 预售第一刀范围 | 按 §5.3 执行，砍 18 款食品 + 11 款饮品 | 预售无法出图 | 8.15 |
| **5** | 🆕 **补位三款**：小份经典堡 26、基础披萨 38–42、堡胚零售 | 全部执行（§5.4/5.5/5.6） | 人均落在 62 而非 58–60 | 8.15 |
| **6** | 主力款定价（经典堡 36） | 维持 36，不上调 | 影响成本测算与套餐设计 | 8.15 |
| **7** | 套餐结构（5 套，含新增 39 元入门餐） | 按 §6.3 执行 | 团购无法上线 | 8.19 |
| **8** | 🆕 **烤炉店口碑修复启动** | 开业前 60 天启动，目标 3.9 → 4.2 | 母品牌口碑连坐 | **本周** |
| **9** | 🆕 **品牌架构：母品牌 + 子品牌** | 采纳，但视觉强关联需等烤炉评分 ≥4.2 | 两店关系混乱 | 8.15 |
| **10** | 🆕 **英文主口号统一** | 统一为 BURGER, DONE RIGHT.；校对"BReal"拼写 | 包材印错不可逆 | 出图前 |
| **11** | 🆕 **RTB 表述修正**（"前万豪"改为可核实表述） | 改为"米其林三星厨房出身 · 前 GUCCI 1921 上海行政总厨" | 合规与可信度风险 | 出图前 |
| **12** | 巴斯克赠送成本上限 | 中性情景 5.8 万元 | 无法核算 ROI | 8.15 |
| **13** | 红绿灯阈值确认 | 按 §5.7 建议值 | 60 天后删减无依据 | 8.15 |
| **14** | 饮品线收敛至 8 款 | 立即执行 | 出图与备货浪费 | 8.15 |
| **15** | 🔴 **毛利率口径澄清**（是否含包材与损耗） | 需客户当场说明 | 65% 毛利红线需重算 | 8.15 |
| **16** | 🔴 **开业前出餐压测** | 必做，8 分钟出餐率 ≥85% | 出餐慢是新店差评第一来源 | 开业前 |
| **17** | 数据回传机制启动时间 | **开业日 D1** | 闭环断裂 | 开业日 |
```


#### S6 briefing · 未解问题

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L2093–L2109
- genre: `briefing`

```
# 第十二部分 · 未解问题与二期路线

## 12.1 本次仍未能回答的问题

| 问题 | 需要什么 | 何时有答案 | 优先级 |
|---|---|---|---|
| 真实连带率与订单渗透率 | 订单级小票数据 | 开业 +15 天 | 🔴 |
| 实际人均落点 | 小票数据 | 开业 +15 天 | 🔴 |
| 高峰出餐能力上限 | 开业前压测 | **开业前** | 🔴 |
| 窑炉物业可行性 | 物业硬件确认函 | **本周** | 🔴 |
| 毛利率是否含包材损耗 | 客户确认 | **8.15** | 🔴 |
| 北京消费者对国风融合汉堡的接受度 | 上市后销量 | 开业 +15 天 | 🟡 |
| 披萨能否承担规模载体 | 披萨订单渗透率 | 开业 +60 天 | 🔴 |
| 烤炉店客群与汉堡店的重叠度 | 双店互通券核销 | 开业 +30 天 | 🟡 |
| 外卖真实占比与品质衰减 | 平台数据 + 差评归因 | 开业 +30 天 | 🟡 |
| 跨省供应链稳定性 | 供货方案 + 到货记录 | 开业 +30 天 | 🟡 |
| 二店选址最终确认 | 首店模型验证 + 物业 | 开业 +90 天 | 🟡 |
```


#### S7 dossier · 十条可迁移 + 六条不该学

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L995–L1021
- genre: `dossier`

```
# 第七部分 · 可迁移清单：学什么 / 不学什么 / 怎么验证

## 7.1 十条可直接迁移的做法

| # | 做法 | 来源 | 数据依据 | 落地建议 | 验证方式 |
|---|---|---|---|---|---|
| **1** | **中央工厂做面团，门店做最后烘烤** | 魏斯理 | 杨凌基地日产 10 万个堡胚，门店仅完成最后烘烤 | 30 家店前完成技术验证 | 盲测：中央面团 vs 全店制作，口感差异 <10% |
| **2** | **写字楼底商 > 购物中心** | Wagas | 53 家中 38 家非商场 | 二店起测试写字楼型店 | 对比两种店型的坪效与复购 |
| **3** | **一商圈一店，不做密度覆盖** | BAKER&SPICE / Wagas / 油梨树 | 28 店/26 商圈、53 店/43 商圈、17 店/15 商圈 | 前 15 家店严格执行 | 商圈重叠度 <10% |
| **4** | **同品牌双店型并行** | THE WOODS / 棒约翰 | THE WOODS 餐厅 90–138 元 vs 简餐 65 元，评分均 4.5+ | 50 家前完成轻量店型验证 | 两店型评分均 ≥4.5 |
| **5** | **套餐锁客单，降低 CV** | 比格（CV 1.9%）、萨莉亚（CV 5.6%） | 自助与固定组合天然锁死客单 | 提高套餐订单占比至 50%+ | 客单 CV ≤8% |
| **6** | **单店评论 1,500–2,000 作为 12 个月目标** | Wagas 1,619 / BAKER&SPICE 2,036 | 品质连锁的单店客流基准 | 纳入门店 KPI | 12 个月评论数 |
| **7** | **稀缺性开店（每城 1–2 家）造势能** | 魏斯理 | 省外每城 1–2 家，排队 2 小时 | 跨城阶段采用 | 新城首店排队时长与评论爬坡速度 |
| **8** | **烘焙作为可带走的产品线** | BAKER&SPICE / The Daily Bagel | 66–75 元人均，4.56–4.75 分 | 堡胚零售，18–22 元 | 堡胚零售订单渗透率 ≥8% |
| **9** | **明档手工拍打肉饼可视化** | 美州汉堡等手工汉堡赛道 | 已成为该赛道通行做法 | 🔴 **必须做得比 30 元品牌更狠**（原切+现绞+可追溯） | 明档可见性测试 ≥40% |
| **10** | **全直营直到模型稳定** | 魏斯理 | 全直营 80+ 家 | 50 家前不开放加盟 | 五条加盟前提（见方法论报告 §8.6） |

## 7.2 六条明确不该学的

| # | 不学 | 为什么 | 数据依据 |
|---|---|---|---|
| 1 | **不学 Shake Shack 的评分水平** | 4.18 分、仅 12% 门店 ≥4.5。它靠全球品牌势能弥补，石头先生没有这个资源 | §3.3：4.4 分是流量阀门 |
| 2 | **不学必胜客的客单离散** | CV 12.5%、评分标准差 0.29，稳定性排名倒数第 2。那是 283 家店的代价，不是 15 家店该有的状态 | §3.2 |
| 3 | **不学好伦哥的扩张方式** | CV 39.7%、评分标准差 0.33、均分 3.78——规模跑在体系前面的典型 | §3.2 |
| 4 | **不学轻遇三明治的门店堆砌** | 41 家店，单店评论中位 **0** | §3.1 |
| 5 | **不学 Wagas 的品类结构** | 轻食沙拉品类在北京：35 家门店、30 元客单、**3.60 分（全品类最低）**、单店评论中位 4 条 | §3.5 |
| 6 | **不学达美乐的外送优先** | 现绞现煎现烤的产品在配送后损耗最大；达美乐单店评论中位仅 338 | §3.4 |
```


#### S8 dossier · 三个开放问题 (falsify timing)

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L1023–L1029
- genre: `dossier`

```
## 7.3 三个需要用数据回答的开放问题

| 问题 | 现有证据 | 判据 | 何时有答案 |
|---|---|---|---|
| **Q1：58–62 元 还是 72–78 元？** | 55–65 带只有必胜客一家有规模（283）；65–80 带有 4 个品牌评分 4.5+（Wagas 53 / Tubestation 29 / BAKER&SPICE 28 / 比格 84） | 首店 D90 人均实际落点 + 差评中"贵"的占比 | 首店 +90 天 |
| **Q2：披萨能否作为规模载体？** | Tubestation 29 家 × 78 元 × 4.63 分（正面证据）；必胜客 283 家（正面证据） | D60 披萨订单渗透率 ≥25% | 首店 +60 天 |
| **Q3：烘焙能否成为第二曲线？** | BAKER&SPICE 28 家 × 75 元 × 4.56 分（唯一规模样本）；北京无"烘焙×汉堡"成功先例 | 堡胚零售订单渗透率 ≥8% + 烤炉店评分修复至 ≥4.2 | 首店 +90 天 |
```


#### S9 roadmap · 宏观六条推论

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L671–L680
- genre: `roadmap`

```
## 4.7 宏观结论：六条推论汇总

| # | 推论 | 战略含义 |
|---|---|---|
| 1 | 大盘微增，存量博弈 | 增长靠抢份额，不靠行业红利 |
| 2 | 近六成新店两年内退出 | Stage Gate 是必须，不是保守 |
| 3 | **3–10 家是死亡带（−18.5%）** | 🔴 **不要在这个区间停留；要么精耕 1–2 家，要么快速穿过** |
| 4 | 西式快餐增速 10.3%，但被中式汉堡低价分流 | 向上走是唯一方向 |
| 5 | 西餐人均连续两季上涨，涨价窗口打开 | 55–65 元定位有宏观支撑 |
| 6 | 预制菜监管趋严 | "现做"从卖点变成结构性优势 |
```


#### S10 roadmap · 风险登记册

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1581–L1600
- genre: `roadmap`

```
# 第十部分 · 风险登记册

| # | 风险 | 概率 | 影响 | 早期信号 | 预案 |
|---|---|---|---|---|---|
| **R1** | 🔴 **必胜汉堡等巨头子品牌占领"西餐级汉堡"心智** | 高 | 极高 | 目标城市出现其门店；顾客提及率上升 | 信任状迁移至"现绞原切"；加速首店验证 |
| **R2** | 🔴 **出餐效率不达标导致评分卡在 4.2** | 中高 | 极高 | 压测未达标；首周差评含"慢" | 开业前削减 SKU；不达标不开业 |
| **R3** | 人均被团购压至 50 元以下 | 中 | 高 | 团购订单占比 >40% | 收缩折扣；提高套餐门槛 |
| **R4** | 披萨渗透率不足，双载体路径不成立 | 中 | 高 | D60 披萨渗透 <15% | 退回汉堡单核；二店不装窑炉 |
| **R5** | 店长跟不上开店速度 | 高 | 高 | 储备店长 < 计划开店数 | 储备永远 +2；不够就不开 |
| **R6** | 在 3–10 家死亡带停留过久 | 中 | 高 | 6–10 家阶段超过 12 个月 | Gate 达标即加速；不达标即停 |
| **R7** | 跨省供应链品质波动 | 中 | 中高 | 到货合格率下降 | 双供应商；关键品项本地化 |
| **R8** | 澳牛/芝士的汇率与关税波动 | 中 | 中 | 采购成本环比 +8% | 长约锁价；配方备选方案 |
| **R9** | 中央厨房自建过早，产能闲置 | 中 | 高 | 产能利用率 <50% | 50 家前用第三方 |
| **R10** | 加盟开放过早导致品控失控 | 中 | 极高 | 五条前提未满足即启动 | 五条全满足才谈 |
| **R11** | 创始人偏好凌驾数据 | 中高 | 中高 | 红灯 SKU 连续两轮未下架 | 红绿灯规则提前签字；Gate 由第三方评审 |
| **R12** | 品牌与"石头先生的烤炉"口碑连坐 | 中 | 中 | 烤炉店评分持续 <4.0 | 口碑修复前置；视觉弱关联 |
| **R13** | 食安事故 | 低 | 极高 | 温控/留样不合规 | 现绞肉品的温控 SOP 与留样是最高优先级 |

> **R13 需要单独强调：现绞肉是本项目的核心差异化，也是最大的食安暴露面。**
> **明档让工艺被看见，也让问题被看见。这个决定必须配套最严格的温控与记录制度。**
```


#### S11 gold HTML 十条结论

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 226
- genre: `diagnosis`

```
class: slide
chips: 拾叁 · 结论与行动清单
h2: 13.1 十条核心结论
SOURCE: 清水亭六店经营数据（品项汇总 72

CONCLUSIONS & ACTIONS 
拾叁 · 结论与行动清单 

13.1 十条核心结论

数据来源 / SOURCE 清水亭六店经营数据（品项汇总 72 天 · 账单明细 6 月 · 会员消费 1 – 6 月） 

# 结论 数据支撑 影响量级 
1 主菜渗透率 46.7% ，过半的桌不点招牌鱼鲜 8,731 / 16,867 桌零主菜，桌均低 ¥88.9 渗透率 +13.3pt ≈ 月增 ¥199,400 
2 国贸店 6 月套餐销售为零，五店套餐桌均贡献 ¥74.1 套餐渗透率 国贸 0% vs 五店 27.4% 国贸上线套餐 ≈ 月增 ¥100,000 + 
3 火烧馍-鱼头连带模型在国贸跑通（ 99.7% ），五店仅 10.6% – 17.0% 提升度 3.03 ，共现 1,281 桌 五店复制 ≈ 月增 ¥190,000 + 
4 长尾 SKU 占 32.2% ，只贡献 3.1% 销售额 38 款长尾，其中 18 款为饮品甜品 精简 25 款，SKU −21.2% ，损失 2.3% 销售额 
5 6 月 17 日藕汤替换损失煨汤桌均 ¥13.4 ¥115.7 → ¥38.3 均价，件数 +92.6% 年化影响约 ¥272 万 
6 同一菜品在两个门店组角色定义不一致（ 28.0% ） 23 / 82 个品项 服务话术与陈列无法统一复制 
7 ¥200 – 260 存在 60 元价格空档 ¥199 卖出 6,494 份，向上无承接 补 2 款宴请型主菜 
8 辣/麻 × 特殊工艺 = 0 款；辣/麻 × 猪 = 0 款 九宫格唯一空白格 猪肉占 18.8% 销售额却无辣味做法 
9 会员识别率 3.99% ，复购率 17.6% 会员桌均比非会员高 52.9% 识别率提升至 30% 是客户资产分析前提 
10 大份规格曝光严重不足；毛利优势集中在三款鱼鲜 大份千单点击仅为例份的 12.1% ； 20 组配对中大份毛利更高仅 7 组（中位 −0.7pt ），但油爆丹江活青虾 +14.1pt 、油焖罗氏虾烧年糕 +7.2pt 、公安鱼杂煲 +7.1pt 定向推荐，非全菜单铺开（附录 F.19） 

清水亭 · 产品结构诊断 · TIANSIGHT 226 / 296

--- tables (first rows) ---

| # | 结论 | 数据支撑 | 影响量级 |
|---|---|---|---|
| 1 | 主菜渗透率 46.7% ，过半的桌不点招牌鱼鲜 | 8,731 / 16,867 桌零主菜，桌均低 ¥88.9 | 渗透率 +13.3pt ≈ 月增 ¥199,400 |
| 2 | 国贸店 6 月套餐销售为零，五店套餐桌均贡献 ¥74.1 | 套餐渗透率 国贸 0% vs 五店 27.4% | 国贸上线套餐 ≈ 月增 ¥100,000 + |
| 3 | 火烧馍-鱼头连带模型在国贸跑通（ 99.7% ），五店仅 10.6% – 17.0% | 提升度 3.03 ，共现 1,281 桌 | 五店复制 ≈ 月增 ¥190,000 + |
| 4 | 长尾 SKU 占 32.2% ，只贡献 3.1% 销售额 | 38 款长尾，其中 18 款为饮品甜品 | 精简 25 款，SKU −21.2% ，损失 2.3% 销售额 |
| 5 | 6 月 17 日藕汤替换损失煨汤桌均 ¥13.4 | ¥115.7 → ¥38.3 均价，件数 +92.6% | 年化影响约 ¥272 万 |
| 6 | 同一菜品在两个门店组角色定义不一致（ 28.0% ） | 23 / 82 个品项 | 服务话术与陈列无法统一复制 |
| 7 | ¥200 – 260 存在 60 元价格空档 | ¥199 卖出 6,494 份，向上无承接 | 补 2 款宴请型主菜 |
| 8 | 辣/麻 × 特殊工艺 = 0 款；辣/麻 × 猪 = 0 款 | 九宫格唯一空白格 | 猪肉占 18.8% 销售额却无辣味做法 |
| … | (2 more rows omitted) |
```


#### S12 gold HTML F.1 证伪页

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 261
- genre: `diagnosis`

```
class: slide
chips: 附 · 附录
h2: F.1 删除 5,597 行小龙虾账单行（本报告争议最大的一次数据处理） 续
SOURCE: 清水亭六店经营数据（品项汇总 72

APPENDIX 
附 · 附录 

F.1 删除 5,597 行小龙虾账单行（本报告争议最大的一次数据处理） 续 

数据来源 / SOURCE 清水亭六店经营数据（品项汇总 72 天 · 账单明细 6 月 · 会员消费 1 – 6 月） 

证伪条件
出现以下任一情况，本处理即被推翻，需重新计算全部口径 B 数字：
门店确认 POS 中「招牌虾」与「招牌虾99/（ 1 斤起点）」是 两个独立可售 SKU （例如一个是堂食、一个是外带）；
收银系统供应商说明账单表头「实收金额」本身也存在同源重复，导致两条路径并非独立验证；
提供任一张实体小票，其上小龙虾以两行分别打印且金额分别计入实收。
附带影响（必须同步修正的历史口径）
任何 未做此项去重 的历史分析或报表，都会：小龙虾品类贡献高估约 74.5% 、全店堂食桌均高估约 ¥48 、 6 月总实收高估 ¥830,889 。若门店此前依据未去重数据判断「小龙虾是第一大品类且占比超过 22% 」，该判断需要重做。

清水亭 · 产品结构诊断 · TIANSIGHT 261 / 296
```


#### S13 gold HTML F.0 审查索引

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 256
- genre: `diagnosis`

```
class: slide
chips: 附 · 附录
h2: F.0 审查结果索引
SOURCE: 清水亭六店经营数据（品项汇总 72

APPENDIX 
附 · 附录 

F.0 审查结果索引

数据来源 / SOURCE 清水亭六店经营数据（品项汇总 72 天 · 账单明细 6 月 · 会员消费 1 – 6 月） 

# 争议点 类型 影响范围 结论状态 
F.1 删除 5,597 行小龙虾账单行 数据清洗 全报告实收口径 已验证，处理成立 
F.2 保留 2,647 组同规格重复行 数据清洗 实收额 ¥113,331 已验证，处理成立 
F.3 剔除 162 行「排除 / 下架」项目 数据清洗 销售额 4.9% 按指令执行，已披露 
F.4 全六店角色采用销量加权多数 口径定义 23 个品项 规则明示，需客户裁定 
F.5 额量比是价格指数而非表现指数 口径定义 第 5 章全章 数学推导，结论确定 
F.6 双口径期间不同，不可直接换算 口径定义 全报告 已隔离标注 
F.7 折让率为负 ≠ 加价 口径定义 小龙虾 / 煨汤 已说明成因 
F.8 渗透率与千单点击分母不同 口径定义 第 5 章指标表 已在本附录澄清 
F.9 「元/桌/小时」不是 RevPASH 口径定义 第 8.7 节 代理指标，禁止外部对标 
F.10 复购率建立在 3.99% 样本上 统计推断 第 9 章全章 存在选择性偏差 
F.11 国贸套餐为零的真实性 统计推断 结论 # 2 、行动 P0- 1 数据层为真，业务层待确认 
表续 1 / 3

清水亭 · 产品结构诊断 · TIANSIGHT 256 / 296

--- tables (first rows) ---

| # | 争议点 | 类型 | 影响范围 | 结论状态 |
|---|---|---|---|---|
| F.1 | 删除 5,597 行小龙虾账单行 | 数据清洗 | 全报告实收口径 | 已验证，处理成立 |
| F.2 | 保留 2,647 组同规格重复行 | 数据清洗 | 实收额 ¥113,331 | 已验证，处理成立 |
| F.3 | 剔除 162 行「排除 / 下架」项目 | 数据清洗 | 销售额 4.9% | 按指令执行，已披露 |
| F.4 | 全六店角色采用销量加权多数 | 口径定义 | 23 个品项 | 规则明示，需客户裁定 |
| F.5 | 额量比是价格指数而非表现指数 | 口径定义 | 第 5 章全章 | 数学推导，结论确定 |
| F.6 | 双口径期间不同，不可直接换算 | 口径定义 | 全报告 | 已隔离标注 |
| F.7 | 折让率为负 ≠ 加价 | 口径定义 | 小龙虾 / 煨汤 | 已说明成因 |
| F.8 | 渗透率与千单点击分母不同 | 口径定义 | 第 5 章指标表 | 已在本附录澄清 |
| … | (3 more rows omitted) |
```


#### Budget · F.1 四段

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L3071–L3122
- genre: `diagnosis`
- note: retired fill id falsify-quad

```
## F.1 删除 5,597 行小龙虾账单行（本报告争议最大的一次数据处理）

### 争议点

本报告从账单明细中**删除了 5,597 行、涉及 ¥830,889** 的数据，占删除前行合计的 9.6%。删除后小龙虾品类的销售额从 ¥1,945,537 降到 ¥1,114,648（−42.7%），全店堂食桌均从 ¥456.1 降到 ¥408.2（−10.5%）。

删数据是分析中最需要被质疑的动作。任何人都有理由问：**凭什么认为这 5,597 行是系统伪影，而不是真实销售？**

### 事实

**第一步：发现异常。** 按 `营业流水号 + 品项代码 + 数量 + 销售单价 + 小计金额` 五字段分组，全量 159,086 行中出现 8,209 个「一组多行」。若这些都是真实销售，意味着同一张账单在同一价格、同一数量下重复点了同一个品项——在正餐场景可能发生（比如加点一份米饭），因此不能直接删。

**第二步：把异常分成两类。** 关键的分辨依据是**组内 `规格` 字段是否相同**：

| 类型 | 组数 | 行数 | 涉及金额 | 组内规格 | 判定 |
|---|---:|---:|---:|---|---|
| A 类 | 5,562 | 11,308 | ¥1,665,134 | **互不相同** | 系统伪影 → 删 |
| B 类 | 2,647 | 5,627 | ¥113,331 | **完全相同** | 真实重复下单 → 留 |

**第三步：A 类为什么是伪影。** A 类只出现在三个品项上，其中小龙虾两款的规格取值呈现严格的成对镜像：

| 规格写法 | 全量行数 | 配对规格 | 全量行数 |
|---|---:|---|---:|
| `招牌虾99/（1斤起点）` | 3,716 | `招牌虾` | 3,716 |
| `精品虾159/斤（1斤起点）` | 1,717 | `精品虾` | 1,717 |
| `霸王虾229/（1斤起点）` | 164 | `霸王虾` | 164 |

三组数量**逐一精确相等**，且成对的两行在原始文件中**行号连续**（如第 96 / 97 行）、数量与金额完全一致、`单位` 字段同为 `招牌虾99/斤（1斤起点）`。这是 POS 导出时把同一条销售记录按「完整规格名」和「简写规格名」各写一次的典型特征，而非两次点单——真实的两次点单不会让全店三组规格的计数分毫不差。

**第四步：为什么 A 类里的武汉卤鸭拼盘不删。** 武汉卤鸭拼盘也有 114 行落入 A 类，但它的组内规格是 `九九卤鸭头` / `九九卤鸭脖` / `九九卤素拼`——这是**三种不同的实物**，同价同量，客人同时点两种完全合理。因此本报告只删除小龙虾两款的简写规格行，卤鸭拼盘全部保留。**判定依据不是「组内规格不同」这条机械规则，而是规格值本身是否指向同一实物。**

**第五步：独立验证。** 这是本处理成立与否的决定性证据：

| 口径 | 金额 | 与账单表头「实收金额」合计比较 |
|---|---:|---|
| 账单表头 `实收金额` 合计（独立字段，未参与清洗） | **¥7,842,874** | — |
| 删除前，账单行 `小计金额` 合计 | ¥8,673,763 | **虚高 ¥830,889（+10.6%）** |
| 删除后，账单行 `小计金额` 合计 | **¥7,842,874** | **完全吻合，差额 ¥0** |

账单表头的「实收金额」是收银系统在结账时写入的单据级金额，与明细行的写入路径相互独立。删除 5,597 行之后，两条独立路径的合计**精确对齐到个位数**。若这些行是真实销售，删除后行合计必然低于表头合计 ¥830,889。

### 本报告的处理

删除 `规格 ∈ {招牌虾, 精品虾, 霸王虾}` 的 5,597 行；保留全部 B 类同规格重复行与武汉卤鸭拼盘的多规格行。全报告口径 B 的所有数字均基于去重后数据。

### 证伪条件

出现以下任一情况，本处理即被推翻，需重新计算全部口径 B 数字：

1. 门店确认 POS 中「招牌虾」与「招牌虾99/（1斤起点）」是**两个独立可售 SKU**（例如一个是堂食、一个是外带）；
2. 收银系统供应商说明账单表头「实收金额」本身也存在同源重复，导致两条路径并非独立验证；
3. 提供任一张实体小票，其上小龙虾以两行分别打印且金额分别计入实收。
```


#### Budget · 附录 F 体例

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L3023–L3029
- genre: `diagnosis`
- note: retired fill id falsify-quad

```
# 附录 F｜争议点审查与方法说明

> **本附录的性质**：报告里每一处需要「分析师做判断」而非「数据直接给出答案」的地方，都在此逐条列出。
> 每条包含四段：**争议点 → 事实 → 本报告的处理 → 证伪条件**。
> 「证伪条件」写明什么样的新证据会推翻该处理——凡判断皆可被真实数据证伪并修订。
>
> 审查覆盖：数据清洗 3 项、口径定义 6 项、统计推断 7 项、结论更正 3 项、数据源缺陷 3 项，共 **22 条**。
```


---

## 7 Overflow (`续`)

### Modifier `overflow`

- rule: same job + fill; `overflow_of` parent id; title suffix `续`; repeat SOURCE; TAKEAWAY only on last page
- gold: 126 / 296 titles contain 续

#### S1 gold HTML 续 · 数据资产表

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 9
- genre: `diagnosis`

```
class: slide
chips: 零 · 数据地图、口径定义与数据质量
h2: 0.1 本次分析实际使用的数据资产 续
SOURCE: /mnt/user-data/uploads/

DATA MAP · CALIBRE · QUALITY 
零 · 数据地图、口径定义与数据质量 

0.1 本次分析实际使用的数据资产 续 

数据来源 / SOURCE /mnt/user-data/uploads/ 全部 12 个文件 

门店 有效营业天数 开台数 占比 
颐堤港店 72 9,170 22.5% 
国贸店（国兴） 72 8,720 21.4% 
世纪金源店 72 7,024 17.2% 
祥云小镇店 72 6,006 14.7% 
DT51 店 72 5,328 13.0% 
五棵松万达店 72 4,592 11.2% 
合计 72 40,840 100% 
其中国贸 8,720 台，其余五店合计 32,120 台（ 78.6% ）。全文「国贸 / 五店」两分组即以此为界。

推荐图表 / CHARTS 数据资产地图（Sankey：文件 → 字段 → 分析模块），门店开台数堆叠条形图。 

清水亭 · 产品结构诊断 · TIANSIGHT 9 / 296

--- tables (first rows) ---

| 门店 | 有效营业天数 | 开台数 | 占比 |
|---|---|---|---|
| 颐堤港店 | 72 | 9,170 | 22.5% |
| 国贸店（国兴） | 72 | 8,720 | 21.4% |
| 世纪金源店 | 72 | 7,024 | 17.2% |
| 祥云小镇店 | 72 | 6,006 | 14.7% |
| DT51 店 | 72 | 5,328 | 13.0% |
| 五棵松万达店 | 72 | 4,592 | 11.2% |
| 合计 | 72 | 40,840 | 100% |
```


#### S2 gold HTML 续 · 分类基数

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 11 then 12
- genre: `diagnosis`

```
class: slide
chips: 零 · 数据地图、口径定义与数据质量
h2: 0.2 分类基数：从 370 行到 118 个 SKU
SOURCE: 品项汇总新版·索引表（ 370

DATA MAP · CALIBRE · QUALITY 
零 · 数据地图、口径定义与数据质量 

0.2 分类基数：从 370 行到 118 个 SKU

数据来源 / SOURCE 品项汇总新版·索引表（ 370 行） 

按用户指令，以「主辅佐引」字段为分类基准，并将下架与不参与分析的项目剔除：
处理步骤 行数 说明 
索引表总行数 370 国贸 184 行 + 非国贸 186 行 
减：主辅佐引 = 「排除」 −90 瓶装酒水 53 、瓶装饮品 16 、茶水 8 、收藏打卡产品 4 、外卖应删除 3 、品牌无此套餐 4 、赠送水果 2 
减：备注含「下架」 −72 「下架」 48 行 + 「备注（下架）」 24 行 
进入分析 243 国贸 121 行 + 非国贸 122 行 
去重后 SKU（品项 × 规格） 118 唯一品项 82 个 
被剔除项目的规模 （口径 A）
分组 剔除销量 剔除销售额 占该组总额 
国贸 6,332 ¥185,004 5.0% 
非国贸五店 19,084 ¥612,910 4.9% 
合计 25,416 ¥797,914 4.9% 
被剔除项目按系列分布 ：瓶装酒水 53 款、瓶装饮品 16 款、茶水 8 款、自制饮品 6 款、湖北煨汤 6 款、自制饮品甜品 6 款、湖北烟火热菜 5 款、凉菜/卤味 5 款、甜品 4 款、套餐 4 款、招牌淡水鱼鲜 4 款、收藏打卡产品 4 款、外卖应删除 3 款、凉菜 2 款、小吃点心主食 1 款。
关键结论 / KEY INSIGHTS 

推荐图表 / CHARTS 漏斗图（ 370 → 243 → 118 ），剔除项目系列分布树状图。 

清水亭 · 产品结构诊断 · TIANSIGHT 11 / 296

--- tables (first rows) ---

| 处理步骤 | 行数 | 说明 |
|---|---|---|
| 索引表总行数 | 370 | 国贸 184 行 + 非国贸 186 行 |
| 减：主辅佐引 = 「排除」 | −90 | 瓶装酒水 53 、瓶装饮品 16 、茶水 8 、收藏打卡产品 4 、外卖应删除 3 、品牌无此套餐 4 、赠送水果 2 |
| 减：备注含「下架」 | −72 | 「下架」 48 行 + 「备注（下架）」 24 行 |
| 进入分析 | 243 | 国贸 121 行 + 非国贸 122 行 |
| 去重后 SKU（品项 × 规格） | 118 | 唯一品项 82 个 |

| 分组 | 剔除销量 | 剔除销售额 | 占该组总额 |
|---|---|---|---|
| 国贸 | 6,332 | ¥185,004 | 5.0% |
| 非国贸五店 | 19,084 | ¥612,910 | 4.9% |
| 合计 | 25,416 | ¥797,914 | 4.9% |

--- slide 12 续 ---
class: slide
chips: 零 · 数据地图、口径定义与数据质量
h2: 0.2 分类基数：从 370 行到 118 个 SKU 续
SOURCE: 品项汇总新版·索引表（ 370

DATA MAP · CALIBRE · QUALITY 
零 · 数据地图、口径定义与数据质量 

0.2 分类基数：从 370 行到 118 个 SKU 续 

数据来源 / SOURCE 品项汇总新版·索引表（ 370 行） 

下架与排除项目合计吃掉 4.9% 的销售额，其中 69 款为瓶装酒水饮品与茶水（纯供应链品，无产品结构意义）， 22 款为真实下架菜品。
招牌淡水鱼鲜有 4 行进入下架名单（山茶油丹江鲈鱼、孝感米酒熟醉罗氏虾等），主力系列出现下架动作，需在第 11 章生命周期部分单独追踪。
118 个 SKU 中，多规格品项（例/大份/小份/迷你份）共 36 个，占 30.5% ，规格策略是本次结构分析必须单列的维度。

推荐图表 / CHARTS 漏斗图（ 370 → 243 → 118 ），剔除项目系列分布树状图。 

清水亭 · 产品结构诊断 · TIANSIGHT 12 / 296
```


#### S3 gold HTML 长续链 · 口径 A 二八名录

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 50
- genre: `diagnosis`
- note: slides 51–61 continue the same roster — 11 overflow pages, one job

```
class: slide
chips: 肆 · ABC 贡献与二八分析（双口径）
h2: 4.2 口径 A（标准价， 72 天）结果
SOURCE: 口径 A = 品项汇总（ 118

ABC & PARETO · DUAL CALIBRE 
肆 · ABC 贡献与二八分析（双口径） 

4.2 口径 A（标准价， 72 天）结果

数据来源 / SOURCE 口径 A = 品项汇总（ 118 SKU / 72 天）；口径 B = 账单明细（ 154 品项 / 30 天） 

全六店
分类 SKU SKU 占比 销售额 额占比 销量 量占比 毛利额 利占比 
首选品 30 25.4% ¥9,817,242 63.2% 150,029 57.5% ¥6,617,412 61.7% 
必售品 21 17.8% ¥3,642,614 23.5% 72,891 27.9% ¥2,567,778 23.9% 
观察品 29 24.6% ¥1,595,649 10.3% 22,988 8.8% ¥1,175,157 11.0% 
长尾品 38 32.2% ¥477,799 3.1% 14,948 5.7% ¥362,512 3.4% 
合计 118 100% ¥15,533,304 100% 260,856 100% ¥10,722,859 100% 
集合规模 ：S1（销售额 80% ）= 40 个 SKU｜S2（销量 80% ）= 41 个 SKU｜ 交集 = 30 个 ｜并集 = 51 个
二八验证 ： 25.4% 的 SKU 贡献 63.2% 的销售额； 43.2% 的 SKU（首选 + 必售）贡献 86.7% 的销售额。二八法则成立，且比经典 20 / 80 更集中。
二八四分类全名录（全六店 118 个 SKU 逐一归属）

清水亭 · 产品结构诊断 · TIANSIGHT 50 / 296

--- tables (first rows) ---

| 分类 | SKU | SKU 占比 | 销售额 | 额占比 | 销量 | 量占比 | 毛利额 | 利占比 |
|---|---|---|---|---|---|---|---|---|
| 首选品 | 30 | 25.4% | ¥9,817,242 | 63.2% | 150,029 | 57.5% | ¥6,617,412 | 61.7% |
| 必售品 | 21 | 17.8% | ¥3,642,614 | 23.5% | 72,891 | 27.9% | ¥2,567,778 | 23.9% |
| 观察品 | 29 | 24.6% | ¥1,595,649 | 10.3% | 22,988 | 8.8% | ¥1,175,157 | 11.0% |
| 长尾品 | 38 | 32.2% | ¥477,799 | 3.1% | 14,948 | 5.7% | ¥362,512 | 3.4% |
| 合计 | 118 | 100% | ¥15,533,304 | 100% | 260,856 | 100% | ¥10,722,859 | 100% |
```


#### S4 diagnosis · 附录 A 必须分页

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L2644–L2658
- genre: `diagnosis`
- note: source has 118 SKU rows

```
## 附录 A｜全六店 118 SKU 全量分析明细（口径 A：标准价，72 天）

|   序 | 品项            | 规格       | 系列       | 角色   |   售价 |    销量 |     销售额 |   额占比% |    累计% |   毛利率% |   千单点击 |   额量比 |   渗透率% | 二八分类   |
|----:|:--------------|:---------|:---------|:-----|-----:|------:|--------:|-------:|-------:|-------:|-------:|------:|-------:|:-------|
|   1 | 【鱼头+藕汤】招牌双人餐  | 套        | 套餐       | 引    |  316 |  4374 | 1382184 |   8.90 |   8.90 |  60.40 | 107.10 |  5.31 |   7.90 | 首选品    |
|   2 | 山茶油丹江大鱼头      | 例        | 招牌淡水鱼鲜   | 主    |  199 |  5231 | 1040969 |   6.70 |  15.60 |  58.50 | 128.10 |  3.34 |  15.90 | 首选品    |
|   3 | 【鱼头+藕汤】经典四人餐  | 套        | 套餐       | 引    |  549 |  1203 |  660447 |   4.25 |  19.90 |  62.00 |  29.50 |  9.22 |   2.20 | 必售品    |
|   4 | 铫子煨排骨莲藕汤      | 迷你份      | 湖北煨汤     | 辅    |   89 |  6338 |  564082 |   3.63 |  23.50 |  80.30 | 155.20 |  1.49 |  17.70 | 首选品    |
|   5 | 金奖麻辣油焖小龙虾     | 招牌虾99/斤  | 时令小龙虾    | 辅    |   99 |  4517 |  447183 |   2.88 |  26.40 |  56.20 | 110.60 |  1.66 |  16.00 | 首选品    |
|   6 | 山茶油宜昌肥鱼       | 例        | 招牌淡水鱼鲜   | 主    |  169 |  2587 |  437203 |   2.81 |  29.20 |  61.30 |  63.30 |  2.84 |   5.50 | 首选品    |
|   7 | 黄金蒜蓉小龙虾       | 招牌虾99/斤  | 时令小龙虾    | 辅    |   99 |  4143 |  410157 |   2.64 |  31.80 |  56.20 | 101.40 |  1.66 |  15.20 | 首选品    |
|   8 | 【小龙虾节】撮虾快乐双人餐 | 套        | 套餐       | 引    |  299 |  1356 |  405444 |   2.61 |  34.40 |  69.30 |  33.20 |  5.02 |   3.70 | 必售品    |
|   9 | 铫子煨排骨莲藕汤      | 小份       | 湖北煨汤     | 辅    |  169 |  2378 |  401882 |   2.59 |  37.00 |  79.30 |  58.20 |  2.84 |  17.70 | 首选品    |
|  10 | 金奖麻辣油焖小龙虾     | 精品虾159/斤 | 时令小龙虾    | 辅    |  159 |  2494 |  396626 |   2.55 |  39.60 |  63.00 |  61.10 |  2.67 |  16.00 | 首选品    |
|  11 | 公安鱼杂煲         | 例        | 招牌淡水鱼鲜   | 主    |   89 |  4340 |  386260 |   2.49 |  42.10 |  53.40 | 106.30 |  1.49 |  12.10 | 首选品    |
```


#### S5 system · A01–A58 总表必须分页

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L110–L133
- genre: `system`
- note: 58 analysis-point rows

```
## 总表

| # | 分析点 | 模块 | 主维度 | 口径 | 周期 | 重要度 | ZC | HG | QSR | SK | CY | ZZ | XC | WM |
|---|---|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| A01 | 数据资产盘点 | M1 | — | — | 季 | ★★★★☆ | ● | ● | ● | ● | ● | ● | ● | ● |
| A02 | 口径定义与三路对账 | M1 | D5 | A+B | 日 | ★★★★★ | ● | ● | ● | ● | ● | ● | ● | ● |
| A03 | 数据质量检测 | M1 | D5 | B | 日 | ★★★★★ | ● | ● | ● | ● | ● | ● | ● | ● |
| A04 | 门店经营对比 | M2 | D4×D5 | B | 月 | ★★★★☆ | ● | ● | ● | ● | ● | ● | ● | ◐ |
| A05 | 客单价分布 | M2 | D5 | B | 月 | ★★★★☆ | ● | ● | ● | ● | ◐ | ○ | ● | ● |
| A06 | 桌型结构 | M2 | D5 | B | 月 | ★★★★☆ | ● | ● | ◐ | ● | ○ | ● | ◐ | ○ |
| A07 | 角色分类与一致性校验 | M3 | D1×D2 | A | 季 | ★★★★★ | ● | ● | ◐ | ● | ◐ | ◐ | ● | ◐ |
| A08 | 角色画像 | M3 | D2 | A+B | 月 | ★★★★☆ | ● | ● | ◐ | ● | ◐ | ◐ | ● | ◐ |
| A09 | 角色错配识别 | M3 | D2 | A+B | 季 | ★★★★★ | ● | ● | ◐ | ● | ◐ | ○ | ● | ◐ |
| A10 | ABC 贡献分析 | M4 | D1 | A | 月 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A11 | S1/S2 与四分类 | M4 | D1 | A | 月 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A12 | 双口径迁移矩阵 | M4 | D1 | A+B | 月 | ★★★★☆ | ● | ● | ● | ● | ● | ○ | ● | ● |
| A13 | 额量比 | M5 | D1 | A | 月 | ★★★☆☆ | ● | ● | ● | ● | ● | ○ | ● | ● |
| A14 | 千单点击 | M5 | D1 | A | 月 | ★★★★☆ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A15 | 毛利率 | M5 | D1 | A | 月 | ★★★★★ | ● | ● | ● | ● | ● | ● | ● | ● |
| A16 | 渗透率 | M5 | D1×D5 | B | 月 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A17 | 四象限矩阵 | M5 | D1 | A+B | 月 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A18 | 待下架筛选 | M5 | D1 | A+B | 季 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A19 | 高潜品识别 | M5 | D1 | A+B | 季 | ★★★★★ | ● | ● | ● | ● | ● | ◐ | ● | ● |
| A20 | 菜单结构树 | M6 | D1×D2 | A | 季 | ★★★★☆ | ● | ● | ● | ● | ● | ◐ | ● | ● |
```


#### S6 dossier · 规模总榜必须分页

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L88–L106
- genre: `dossier`
- note: 32 brand rows

```
## 2.1 品牌规模总榜（归一化后，北京门店数 ≥ 15 家）

| 排名 | 品牌 | 北京门店 | 人均中位 | 平均评分 | ≥4.5店占比 | 单店评论中位 | 评论总量 | 覆盖商圈 | 主品类 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 麦当劳 | **623** | 31 | 4.00 | 0% | 799 | 610,863 | **204** | 西式快餐 |
| 2 | 肯德基 | **610** | 33 | 3.75 | 0% | 252 | 264,455 | 199 | 西式快餐 |
| 3 | **必胜客** | **283** | **58** | **4.34** | **38%** | 951 | 363,552 | 165 | 比萨 |
| 4 | 华莱士 | 210 | 20 | 3.72 | 0% | 238 | 53,011 | 130 | 西式快餐 |
| 5 | 赛百味 SUBWAY | 190 | 30 | 3.94 | 1% | 347 | 93,222 | 106 | 西式快餐 |
| 6 | **达美乐比萨** | **186** | **55** | 4.25 | 23% | 338 | 85,579 | 130 | 比萨 |
| 7 | 塔斯汀 | 125 | 21 | 3.96 | 0% | 324 | 50,336 | 90 | 西式快餐 |
| 8 | 汉堡王 | 112 | 30 | 4.03 | 0% | **1,476** | 193,874 | 84 | 西式快餐 |
| 9 | **比格比萨自助** | **84** | **74** | 4.17 | 6% | **3,600** | 354,605 | 71 | 披萨自助 |
| 10 | **萨莉亚** | **65** | **50** | 3.98 | 2% | 1,051 | 87,193 | 55 | 意大利菜 |
| 11 | 牛约堡 | 61 | 26 | 3.66 | 0% | 37 | 3,748 | 53 | 西式快餐 |
| 12 | **超级碗 FOODBOWL** | **60** | **37** | **4.52** | **73%** | 547 | 37,635 | 42 | 西餐 |
| 13 | **Wagas 沃歌斯** | **53** | **78** | **4.50** | **62%** | 1,619 | 95,244 | 43 | 西餐 |
| 14 | MURVEY 蔓味轻食 | 51 | 26 | 3.54 | 0% | 20 | 1,281 | 47 | 西餐 |
| 15 | **棒约翰** | **43** | **54** | **4.38** | 33% | 503 | 30,759 | 41 | 比萨 |
```


---

## 8 L3 viz recipes

One viz id per fig shell. Pick FT question first, then the recipe. Copy SVG geometry from the gold HTML.

<a id="l3-viz-sankey"></a>

### L3 viz `sankey`

- FT question: `flow`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 10, 47
- samples: 3

#### MD data behind `sankey` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L30–L58
- genre: `diagnosis`
- note: 0.1 数据资产 + 推荐 Sankey

```
## 0.1 本次分析实际使用的数据资产

📂 **数据来源**：`/mnt/user-data/uploads/` 全部 12 个文件

| # | 文件 | 体量 | 关键字段 | 支撑的分析模块 |
|---|---|---|---|---|
| 1 | 品项汇总…国贸加五店_新版.xlsx | 370 行 × 20 列，6 个 sheet | 门店来源、**主辅佐引**、系列、品项、规格、标准售价、销量、实际成本、实际毛利、千次、开台数、档口、食材分类、味型、工艺、烹饪时间、设备、就餐场景、备注 | ABC/二八、额量比、千单点击、毛利率、九宫格、价格带、结构树 |
| 2 | 品项汇总…六店.xlsx | 8 行 | 门店、有效营业天数、开台数 | 千单点击与倾向系数的分母 |
| 3–8 | 账单明细 × 6 店 .xls | 159,086 行 × 59 列 | 营业流水号、就餐人数、市别、消费区域、客位名称、开台时间、结算时间、会员手机号、大类/小类、品项名称、规格、数量、标准单价、销售单价、小计金额、成本价 | 渗透率、连带分析、时段、座位、RevPASH、客单组合、实收口径 |
| 9–10 | 会员消费 × 2（国贸 / 五店） | 4,345 行 × 24 列 | 会员手机号、账单金额、操作时间、交易门店、消费品项 | 复购率、复购间隔、复购贡献 |
| 11 | 账单明细…世纪金源_xlsx | 3 KB | — | **文件损坏（缺 [Content_Types].xml），未使用**；同店 .xls 版本完整，已替代 |
| 12 | 苏帮袁君臣佐使…内容分析与大纲.md | 239 页解构 | 七大板块目录 + 逐页速览 | 方法论对照（第 1 章） |

**开台数基准（72 天）**

| 门店 | 有效营业天数 | 开台数 | 占比 |
|---|---:|---:|---:|
| 颐堤港店 | 72 | 9,170 | 22.5% |
| 国贸店（国兴） | 72 | 8,720 | 21.4% |
| 世纪金源店 | 72 | 7,024 | 17.2% |
| 祥云小镇店 | 72 | 6,006 | 14.7% |
| DT51 店 | 72 | 5,328 | 13.0% |
| 五棵松万达店 | 72 | 4,592 | 11.2% |
| **合计** | 72 | **40,840** | 100% |

其中国贸 8,720 台，其余五店合计 32,120 台（78.6%）。全文「国贸 / 五店」两分组即以此为界。

📊 **推荐图表**：数据资产地图（Sankey：文件 → 字段 → 分析模块），门店开台数堆叠条形图。
```


#### gold HTML 图 slide 10

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 10 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 01 / 47 · 零 · 数据地图、口径定义与数据质量
h2: 数据资产地图： 12 个文件如何支撑 13 个分析模块
SOURCE: /mnt/user-data/uploads 全部 12

DATA ASSET SANKEY 
图 01 / 47 · 零 · 数据地图、口径定义与数据质量 

数据资产地图： 12 个文件如何支撑 13 个分析模块

数据来源 / SOURCE /mnt/user-data/uploads 全部 12 个文件 · 字段清单 vs 模块输入需求 

[SVG omitted]

关键结论 / KEY INSIGHTS 品项汇总新版一份文件独立支撑 6 个模块；账单明细 6 店合计 159,086 行支撑 5 个模块；会员消费仅够支撑复购一个模块，且识别率只有 3.99% 。 

清水亭 · 产品结构诊断 · TIANSIGHT 10 / 296
```


#### gold HTML 图 slide 47

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 47 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 10 / 47 · 叁 · 主辅佐引角色分类结果与数据校验
h2: 角色错配桑基图： 22 项错配涉及 38.3% 销售额
SOURCE: 口径 A 指标 + 口径 B 渗透率，按四条规则筛选

ROLE REASSIGNMENT SANKEY 
图 10 / 47 · 叁 · 主辅佐引角色分类结果与数据校验 

角色错配桑基图： 22 项错配涉及 38.3% 销售额

数据来源 / SOURCE 口径 A 指标 + 口径 B 渗透率，按四条规则筛选 

[SVG omitted]

关键结论 / KEY INSIGHTS 套餐被当引流品（ 4 项）、煨汤与小龙虾被当辅助品（ 6 项）、低渗透鱼鲜仍挂主品（ 6 项）；重排后「主」收敛为鱼头 + 藕汤 + 小龙虾三条主线。 

清水亭 · 产品结构诊断 · TIANSIGHT 47 / 296
```


<a id="l3-viz-funnel"></a>

### L3 viz `funnel`

- FT question: `part-to-whole`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 13, 164
- samples: 4

#### MD data behind `funnel` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L61–L73
- genre: `diagnosis`
- note: 0.2 370→118 漏斗表

```
## 0.2 分类基数：从 370 行到 118 个 SKU

📂 **数据来源**：品项汇总新版·索引表（370 行）

按用户指令，以「主辅佐引」字段为分类基准，并将下架与不参与分析的项目剔除：

| 处理步骤 | 行数 | 说明 |
|---|---:|---|
| 索引表总行数 | 370 | 国贸 184 行 + 非国贸 186 行 |
| 减：主辅佐引 = 「排除」 | −90 | 瓶装酒水 53、瓶装饮品 16、茶水 8、收藏打卡产品 4、外卖应删除 3、品牌无此套餐 4、赠送水果 2 |
| 减：备注含「下架」 | −72 | 「下架」48 行 + 「备注（下架）」24 行 |
| **进入分析** | **243** | 国贸 121 行 + 非国贸 122 行 |
| 去重后 SKU（品项 × 规格） | **118** | 唯一品项 82 个 |
```


#### MD data behind `funnel` · system

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L1171–L1181
- genre: `system`
- note: 周期漏斗：日→周→月→季→年→事件

```
## 7.1 按周期归类

| 周期 | 分析点 | 产出物 | 责任 |
|---|---|---|---|
| **日** | A02、A03 | 数据质量记分卡（自动化，异常告警） | IT / 数据 |
| **周** | A39、A45、A48 | 周度动能简报（1 页） | 运营 |
| **月** | A04–A06、A08、A10–A17、A24、A28–A29、A31–A38 | 月度经营与产品结构月报 | 产品 + 运营 |
| **季** | A07、A09、A18–A23、A25–A27、A30、A40–A44、A49–A53、A55–A57 | 季度产品结构诊断（完整版） | 产品委员会 |
| **年** | A01 重盘、A54、角色体系重定、品牌生命周期定位 | 年度产品战略 | 品牌 |
| **事件触发** | A46、A47 | 上下架 30 天复盘 | 产品 |
| **每次出报告** | A58 | 争议点与证伪登记 | 分析师 |
```


#### gold HTML 图 slide 13

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 13 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 02 / 47 · 零 · 数据地图、口径定义与数据质量
h2: 分类基数漏斗： 370 行索引如何收敛到 118 个 SKU
SOURCE: 品项汇总新版·索引表 370

CLASSIFICATION FUNNEL 
图 02 / 47 · 零 · 数据地图、口径定义与数据质量 

分类基数漏斗： 370 行索引如何收敛到 118 个 SKU

数据来源 / SOURCE 品项汇总新版·索引表 370 行（国贸 184 + 非国贸 186 ） 

[SVG omitted]

关键结论 / KEY INSIGHTS 剔除的 162 行里， 69 款是瓶装酒水饮品茶水（纯供应链品）， 22 款是真实下架菜品；合计吃掉 ¥797,914 销售额，占全店 4.9% 。 

清水亭 · 产品结构诊断 · TIANSIGHT 13 / 296
```


#### gold HTML 图 slide 164

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 164 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 33 / 47 · 玖 · 复购分析与客户资产
h2: 复购次数漏斗： 82.4% 的会员半年只来一次
SOURCE: 会员消费文件 2026

REPURCHASE FUNNEL 
图 33 / 47 · 玖 · 复购分析与客户资产 

复购次数漏斗： 82.4% 的会员半年只来一次

数据来源 / SOURCE 会员消费文件 2026 / 01 – 06 ， 3,017 名会员 / 4,334 笔 

[SVG omitted]

关键结论 / KEY INSIGHTS 复购率 17.6% ，这 17.6% 的会员贡献 40.7% 的消费额，人均价值是单次会员的 2.31 倍；五店复购率 19.2% 显著高于国贸 12.7% 。 

清水亭 · 产品结构诊断 · TIANSIGHT 164 / 296
```


<a id="l3-viz-waterfall"></a>

### L3 viz `waterfall`

- FT question: `deviation`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 17, 232
- samples: 4

#### MD data behind `waterfall` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L3071–L3110
- genre: `diagnosis`
- note: F.1 对账瀑布数字

```
## F.1 删除 5,597 行小龙虾账单行（本报告争议最大的一次数据处理）

### 争议点

本报告从账单明细中**删除了 5,597 行、涉及 ¥830,889** 的数据，占删除前行合计的 9.6%。删除后小龙虾品类的销售额从 ¥1,945,537 降到 ¥1,114,648（−42.7%），全店堂食桌均从 ¥456.1 降到 ¥408.2（−10.5%）。

删数据是分析中最需要被质疑的动作。任何人都有理由问：**凭什么认为这 5,597 行是系统伪影，而不是真实销售？**

### 事实

**第一步：发现异常。** 按 `营业流水号 + 品项代码 + 数量 + 销售单价 + 小计金额` 五字段分组，全量 159,086 行中出现 8,209 个「一组多行」。若这些都是真实销售，意味着同一张账单在同一价格、同一数量下重复点了同一个品项——在正餐场景可能发生（比如加点一份米饭），因此不能直接删。

**第二步：把异常分成两类。** 关键的分辨依据是**组内 `规格` 字段是否相同**：

| 类型 | 组数 | 行数 | 涉及金额 | 组内规格 | 判定 |
|---|---:|---:|---:|---|---|
| A 类 | 5,562 | 11,308 | ¥1,665,134 | **互不相同** | 系统伪影 → 删 |
| B 类 | 2,647 | 5,627 | ¥113,331 | **完全相同** | 真实重复下单 → 留 |

**第三步：A 类为什么是伪影。** A 类只出现在三个品项上，其中小龙虾两款的规格取值呈现严格的成对镜像：

| 规格写法 | 全量行数 | 配对规格 | 全量行数 |
|---|---:|---|---:|
| `招牌虾99/（1斤起点）` | 3,716 | `招牌虾` | 3,716 |
| `精品虾159/斤（1斤起点）` | 1,717 | `精品虾` | 1,717 |
| `霸王虾229/（1斤起点）` | 164 | `霸王虾` | 164 |

三组数量**逐一精确相等**，且成对的两行在原始文件中**行号连续**（如第 96 / 97 行）、数量与金额完全一致、`单位` 字段同为 `招牌虾99/斤（1斤起点）`。这是 POS 导出时把同一条销售记录按「完整规格名」和「简写规格名」各写一次的典型特征，而非两次点单——真实的两次点单不会让全店三组规格的计数分毫不差。

**第四步：为什么 A 类里的武汉卤鸭拼盘不删。** 武汉卤鸭拼盘也有 114 行落入 A 类，但它的组内规格是 `九九卤鸭头` / `九九卤鸭脖` / `九九卤素拼`——这是**三种不同的实物**，同价同量，客人同时点两种完全合理。因此本报告只删除小龙虾两款的简写规格行，卤鸭拼盘全部保留。**判定依据不是「组内规格不同」这条机械规则，而是规格值本身是否指向同一实物。**

**第五步：独立验证。** 这是本处理成立与否的决定性证据：

| 口径 | 金额 | 与账单表头「实收金额」合计比较 |
|---|---:|---|
| 账单表头 `实收金额` 合计（独立字段，未参与清洗） | **¥7,842,874** | — |
| 删除前，账单行 `小计金额` 合计 | ¥8,673,763 | **虚高 ¥830,889（+10.6%）** |
| 删除后，账单行 `小计金额` 合计 | **¥7,842,874** | **完全吻合，差额 ¥0** |

账单表头的「实收金额」是收银系统在结账时写入的单据级金额，与明细行的写入路径相互独立。删除 5,597 行之后，两条独立路径的合计**精确对齐到个位数**。若这些行是真实销售，删除后行合计必然低于表头合计 ¥830,889。
```


#### MD data behind `waterfall` · roadmap

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L610–L627
- genre: `roadmap`
- note: 死亡带规模变化 → 柱/瀑布

```
## 4.3 连锁化：中等规模是最佳生态位，小连锁是死亡带

<cite index="5-1">我国餐饮连锁化率从 2023 年的 21% 逐年提升，2025 年已达到 25%，年均增长 2 个百分点</cite>。<cite index="4-1">城市层级分化明显，一线城市连锁化率达 33.2%，五线城市升至 21%</cite>。

**最关键的一组数据 —— 不同规模连锁的分化：**

| 规模区间 | 门店数同比变化 | 含义 |
|---|---|---|
| **3–10 家** | <cite index="5-1">同比减少 18.5%</cite> | 🔴 **死亡带**：抗风险能力弱、供应链不完善 |
| **101–500 家** | <cite index="5-1">成为行业增长主力，凭借灵活运营与完善供应链稳步扩张</cite> | 🟢 最佳生态位 |
| **501–1000 家** | <cite index="5-1">门店数同比增长高达 32.6%</cite> | 🟢 快速扩张期 |
| 万店级 | <cite index="5-1">数量持续增加，占据行业主导</cite> | — |

> **推论 3（本报告最重要的宏观结论）：3–10 家是统计意义上的死亡带，门店数同比萎缩 18.5%。**
>
> **这直接改变了扩张节奏的设计逻辑：**
> **不要在 3–10 家这个区间停留太久。** 要么维持 1–2 家精耕直到模型完全跑通，要么一旦跑通就快速穿过 3–10 家进入 15 家以上的规模区。
> **在死亡带里"稳一稳"，是最危险的策略——因为你已经承担了多店的管理成本，却还没获得规模的采购与品牌红利。**
```


#### gold HTML 图 slide 17

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 17 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 03 / 47 · 零 · 数据地图、口径定义与数据质量
h2: 账单去重瀑布：删掉 5,597 行伪影，行合计与账单头精确对齐
SOURCE: 账单明细 6

DEDUPLICATION WATERFALL 
图 03 / 47 · 零 · 数据地图、口径定义与数据质量 

账单去重瀑布：删掉 5,597 行伪影，行合计与账单头精确对齐

数据来源 / SOURCE 账单明细 6 店，按「营业流水号+品项代码+数量+销售单价+小计金额」分组检测 

[SVG omitted]

关键结论 / KEY INSIGHTS 删除前行合计 ¥8,673,763 ，比账单头实收虚高 10.6% ；删除小龙虾规格标签重复行后，行合计 ¥7,842,874 与账单头实收 ¥7,842,874 完全吻合，验证通过。 

清水亭 · 产品结构诊断 · TIANSIGHT 17 / 296
```


#### gold HTML 图 slide 232

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 232 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 47 / 47 · 拾叁 · 结论与行动清单
h2: 效益汇总瀑布：月度净增 ¥799,200 ，相当于 +10.2%
SOURCE: 以 6

BENEFIT WATERFALL 
图 47 / 47 · 拾叁 · 结论与行动清单 

效益汇总瀑布：月度净增 ¥799,200 ，相当于 +10.2% 

数据来源 / SOURCE 以 6 月实收 ¥7,842,874 / 月为基数，各项保守估算 

[SVG omitted]

关键结论 / KEY INSIGHTS 五项增量合计 ¥828,400 ，减去下架 17 款损失 ¥29,200 ，净效益 ¥799,200 ，年化 ¥959 万；各项之间存在部分重叠（主菜渗透率与火烧馍连带部分重合），落地时需做归因去重。 

清水亭 · 产品结构诊断 · TIANSIGHT 232 / 296
```


<a id="l3-viz-radar"></a>

### L3 viz `radar`

- FT question: `correlation`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 20, 105
- samples: 4

#### MD data behind `radar` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L1161–L1183
- genre: `diagnosis`
- note: 6.2 3-4-2-1 达标

```
## 6.2 3-4-2-1 理想结构达标检查

📂 **参照**：苏帮袁 p.40「3 成首选品 · 4 成必售品 · 2 成观察品 · 1 成替换品」

### 全六店

| 分类 | 理想占比 | 实际 SKU | 实际占比 | 差距 | 理想 SKU 数 | 缺口 |
|---|---:|---:|---:|---:|---:|---:|
| 首选品 | 30% | 30 | 25.4% | **−4.6pt** | 35 | −5 款 |
| 必售品 | 40% | 21 | 17.8% | **−22.2pt** | 47 | **−26 款** |
| 观察品 | 20% | 29 | 24.6% | +4.6pt | 24 | +5 款 |
| 长尾品 | 10% | 38 | 32.2% | **+22.2pt** | 12 | **+26 款** |

### 国贸店

| 分类 | 理想 | 实际 SKU | 实际占比 | 差距 |
|---|---:|---:|---:|---:|
| 首选品 | 30% | 35 | 29.9% | −0.1pt ✅ |
| 必售品 | 40% | 16 | 13.7% | −26.3pt |
| 观察品 | 20% | 32 | 27.4% | +7.4pt |
| 长尾品 | 10% | 34 | 29.1% | +19.1pt |

### 五店
```


#### MD data behind `radar` · briefing

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L854–L866
- genre: `briefing`
- note: 竞争力雷达表

```
## 3.10 竞争力雷达（数据校准版）

| 维度 | 石头先生 | Shake Shack | 蓝蛙 | 21街区均值 | 西式快餐巨头 | 数据依据 |
|---|---|---|---|---|---|---|
| 产品力（食材/工艺） | ★★★★★ | ★★★★ | ★★★★ | ★★ | ★★ | 现绞现煎现烤 |
| 价格力 | ★★★ | ★★★ | ★★ | ★★★★★ | ★★★★★ | 58–62 vs 62 vs 136 vs 35.5 |
| 品牌认知（北京） | ★ | ★★★★★ | ★★★★ | ★★ | ★★★★★ | Shake Shack 北京 7 店/6.3万评论 |
| **同场既有客群** | **★★★★** | ★★★ | ★★ | ★★★ | ★★ | 🆕 烤炉店 13,831 评论 |
| 视觉表现 | ★★★★★ | ★★★★ | ★★★ | ★★ | ★★★ | 品牌手册完成度高 |
| 出品效率 | ★★（待验证） | ★★★★ | ★★ | ★★★★ | ★★★★★ | 🔴 五档口结构风险 |
| 线上运营 | ★（新店） | ★★★★ | ★★★ | ★★★ | ★★★★★ | 需从 0 起 |
| 供应链标准化 | ★★（跨省首店） | ★★★★★ | ★★★★ | ★★ | ★★★★★ | 跨省风险 |
```


#### gold HTML 图 slide 20

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 20 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 04 / 47 · 零 · 数据地图、口径定义与数据质量
h2: 数据完备度雷达： 12 个维度里 4 个为零
SOURCE: 本次 12

DATA READINESS RADAR 
图 04 / 47 · 零 · 数据地图、口径定义与数据质量 

数据完备度雷达： 12 个维度里 4 个为零

数据来源 / SOURCE 本次 12 个文件的字段清单 vs 13 个分析模块的输入需求 

[SVG omitted]

关键结论 / KEY INSIGHTS A 类 4 项完备度 74 – 100% ，足以支撑 11 个模块；B 类 P0 四项（品项级实收、动态成本卡、餐位数、会员识别率）是精度瓶颈；C 类外部数据 4 项全部为 0 。 

清水亭 · 产品结构诊断 · TIANSIGHT 20 / 296
```


#### gold HTML 图 slide 105

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 105 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 20 / 47 · 陆 · 菜单结构树与 3-4-2-1 理想结构
h2: 3 - 4 - 2 - 1 达标雷达：必售品缺 26 款，长尾多 26 款
SOURCE: 苏帮袁 p.40 理想结构 3

IDEAL STRUCTURE RADAR 
图 20 / 47 · 陆 · 菜单结构树与 3-4-2-1 理想结构 

3 - 4 - 2 - 1 达标雷达：必售品缺 26 款，长尾多 26 款

数据来源 / SOURCE 苏帮袁 p.40 理想结构 3 成首选 / 4 成必售 / 2 成观察 / 1 成替换 

[SVG omitted]

关键结论 / KEY INSIGHTS 必售品塌陷与长尾膨胀数量完全对称，说明存在一批「本该培养成必售品、实际掉进长尾」的产品；国贸首选品占比 29.9% 几乎精准达标。 

清水亭 · 产品结构诊断 · TIANSIGHT 105 / 296
```


<a id="l3-viz-venn"></a>

### L3 viz `venn`

- FT question: `part-to-whole`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 26, 63
- samples: 3

#### MD data behind `venn` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L210–L237
- genre: `diagnosis`
- note: 1.1 框架对照

```
## 1.1 框架对照

📂 **数据来源**：苏帮袁 PPT 239 页内容解构（七大板块）vs 本次分析要求的 5 大类 12 小项

### 苏帮袁框架（方法论供给方）

| 板块 | 页码 | 核心内容 |
|---|---|---|
| 一、方法论与门店认知诊断 | p.1–34 | 君臣佐使六步法、ABC 表、二八原则、S1/S2 集合、待下架三条标准、核心记忆点剥离 |
| 二、现状与产品矩阵 | p.35–73 | 87 SKU 品类分布、产品结构树、3-4-2-1 理想结构、板块价格带梯度、单品深度分析 |
| 三、产品呈现与经营数据 | p.74–99 | 汤品呈现、小票单据汇总、区域运营效率、午晚市差异、连带与组合点单 |
| 四、市场趋势与竞品对标 | p.100–138 | 外出就餐趋势、九宫格味型贡献、商圈格局、黑珍珠米其林、竞对矩阵 |
| 五、核心产品落地形态创意 | p.139–173 | 品类热度、时令稀缺体系、特色类工艺/规格策略、行动清单优先级矩阵 |
| 六、点心与价格带延展 | p.174–204 | 四季点心选品、166–200 元价格带菜单对标 |
| 七、落地与客单验证 | p.205–239 | 需求思维、产品规划、对标店客单反证、品牌生命周期四阶段 |

### 本次分析要求（问题定义方）

| 编号 | 分析项 | 苏帮袁对应页 |
|---|---|---|
| 1 | ABC 贡献 + 二八排序，S1/S2 及交集 → 首选/必售/观察/长尾 + 主辅佐引 | p.13–21、p.33、p.36 |
| 1b | 额量比、千单点击、毛利率、渗透率 | p.21、p.24、p.25、p.43–45 |
| 2 | 菜单结构树 + 3-4-2-1 理想结构 | p.37、p.39、p.40 |
| 3 | 品类倾向系数、价格带、价格空档、客单组合、小票时间与座位、复购率 | p.42、p.48、p.55、p.58、p.82、p.94、p.99、p.108–109 |
| 4 | 味型×工艺、味型×食材九宫格、季节性矩阵、生命周期 | p.110–114、p.142–148 |
| 5 | 商圈、竞品菜单低中高对比、品类/区域榜单、门店品牌对标 | p.117–138、p.184–199 |

## 1.2 互补关系矩阵
```


#### gold HTML 图 slide 26

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 26 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 05 / 47 · 壹 · 两套分析框架的对照与合并
h2: 两套框架的重合与互补： 8 个模块完全一致
SOURCE: 苏帮袁 PPT 239

FRAMEWORK VENN 
图 05 / 47 · 壹 · 两套分析框架的对照与合并 

两套框架的重合与互补： 8 个模块完全一致

数据来源 / SOURCE 苏帮袁 PPT 239 页七大板块 vs 本次分析要求 5 大类 12 小项 

[SVG omitted]

关键结论 / KEY INSIGHTS 结构层高度重合；本次补强了复购率、产品生命周期、味型×食材三个盲点，苏帮袁补强了核心记忆点剥离、点单公式、下架效益预测等五项。 

清水亭 · 产品结构诊断 · TIANSIGHT 26 / 296
```


#### gold HTML 图 slide 63

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 63 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 12 / 47 · 肆 · ABC 贡献与二八分析（双口径）
h2: S1 / S2 集合韦恩图：交集 30 个 SKU 即「首选品」
SOURCE: 口径 A，S1 = 销售额累计 80%

S1 / S2 SET VENN 
图 12 / 47 · 肆 · ABC 贡献与二八分析（双口径） 

S1 / S2 集合韦恩图：交集 30 个 SKU 即「首选品」

数据来源 / SOURCE 口径 A，S1 = 销售额累计 80% ，S2 = 销量累计 80% 

[SVG omitted]

关键结论 / KEY INSIGHTS 并集 51 个 SKU 构成「有效菜单」，其余 67 个 SKU 只贡献 13.3% 销售额；国贸与五店的并集都恰好是 51 个，规模高度稳定。 

清水亭 · 产品结构诊断 · TIANSIGHT 63 / 296
```


<a id="l3-viz-bubble"></a>

### L3 viz `bubble`

- FT question: `magnitude`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 33
- samples: 3

#### MD data behind `bubble` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L303–L337
- genre: `diagnosis`
- note: 2.1 六店 → 气泡图推荐

```
## 2.1 六店经营对比（口径 B，2026 年 6 月）

📂 **数据来源**：账单明细 6 店（去重后 153,483 行）→ 账单头聚合 24,752 单

| 门店 | 总账单 | 总实收 | 堂食单 | 堂食实收 | 桌均 | 人均 | 件/桌 | 中位时长 | 外卖单 | 外卖实收 | 外卖占比 | 日均堂食桌 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 颐堤港店 | 5,613 | ¥1,648,839 | 3,754 | ¥1,424,497 | ¥379.5 | ¥136.4 | 8.4 | 54.6 min | 1,689 | ¥205,615 | 12.5% | 125.1 |
| 国贸店 | 3,690 | ¥1,558,884 | 3,690 | ¥1,558,884 | **¥422.5** | **¥153.8** | **9.8** | 61.0 min | 0 | ¥0 | **0.0%** | 123.0 |
| 世纪金源店 | 4,227 | ¥1,311,274 | 2,859 | ¥1,147,342 | ¥401.3 | ¥138.5 | 8.2 | 57.9 min | 1,206 | ¥153,041 | 11.7% | 95.3 |
| 祥云小镇店 | 4,343 | ¥1,312,330 | 2,505 | ¥1,089,016 | **¥434.7** | ¥147.0 | 9.3 | 58.1 min | 1,728 | ¥202,939 | 15.5% | 83.5 |
| DT51 店 | 3,916 | ¥1,185,986 | 2,218 | ¥958,255 | ¥432.0 | ¥151.8 | 8.5 | 60.8 min | 1,620 | ¥212,420 | **17.9%** | 73.9 |
| 五棵松万达店 | 2,963 | ¥825,562 | 1,841 | ¥706,385 | ¥383.7 | ¥129.9 | 8.1 | 57.5 min | 1,119 | ¥118,964 | 14.4% | 61.4 |
| **合计 / 均值** | **24,752** | **¥7,842,874** | **16,867** | **¥6,884,379** | **¥408.2** | **¥139.2** | **8.8** | **57.9 min** | **7,362** | **¥892,979** | **11.4%** | **93.7** |

**六店 6 月日均实收：¥261,429**

> **口径说明（勘误）**：本表「总账单」列与「堂食单 + 外卖单」相差 523 单。原因是账单的 `销售类型` 实际有 **4 类**，本表只列了其中 2 类：
>
> | 销售类型 | 单数 | 占比 | 本表是否单列 |
> |---|---:|---:|---|
> | 堂食 | 16,867 | 68.1% | ✅ |
> | 外卖 | 7,362 | 29.7% | ✅ |
> | **外带** | **512** | **2.1%** | ❌ 计入总账单，未单列 |
> | **自提** | **11** | **0.0%** | ❌ 计入总账单，未单列 |
>
> 外带分布：颐堤港 170、世纪金源 159、祥云小镇 108、DT51 75、五棵松 0、国贸 0。外带与自提合计 523 单，本报告未做单独分析，其金额已包含在「总实收」中。

🔑 **关键结论**

1. 祥云小镇（¥434.7）、DT51（¥432.0）、国贸（¥422.5）三店桌均领先，颐堤港（¥379.5）最低，极差 ¥55.2（14.5%）。
2. 国贸店 6 月外卖收入为 0，其余五店外卖占比 11.7%–17.9%。国贸同时拥有最高的件/桌（9.8）与最长的中位用餐时长（61.0 分钟），呈现纯堂食、重体验的结构。
3. 颐堤港日均堂食 125.1 桌（全司最高），桌均却最低，属于典型的「高流量低客单」组合，提升空间在客单而非流量。
4. 五棵松万达日均 61.4 桌、人均 ¥129.9，双低，需要单独判断是商圈问题还是执行问题。

📊 **推荐图表**：六店气泡图（X = 日均堂食桌数，Y = 桌均，气泡 = 总实收，颜色 = 外卖占比）；桌均/人均并列条形图 + 全店均值参考线。
```


#### MD data behind `bubble` · dossier

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L204–L227
- genre: `dossier`
- note: 门店数 × 单店评论中位

```
## 3.1 规律一：评论中位数暴露了"真实客流"，而门店数不暴露

**同样是连锁，单店人气差 100 倍。**

| 品牌 | 北京门店 | 单店评论中位 | 说明 |
|---|---|---|---|
| 西堤牛排 | 9 | **14,100** | 单店客流之王 |
| Shake Shack | 8 | **5,954** | 少而重 |
| 西十二街牛排 | 18 | 5,348 | — |
| bluefrog 蓝蛙 | 17 | 4,990 | — |
| 比格比萨自助 | 84 | **3,600** | 84 家店都是大店 |
| BAKER&SPICE | 28 | 2,036 | — |
| Wagas 沃歌斯 | 53 | 1,619 | — |
| 汉堡王 | 112 | 1,476 | — |
| Tubestation | 29 | 1,159 | — |
| 萨莉亚 | 65 | 1,051 | — |
| 必胜客 | 283 | 951 | — |
| 麦当劳 | 623 | 799 | 门店多但单店人气中等 |
| 超级碗 FOODBOWL | 60 | 547 | 小店型 |
| 达美乐比萨 | 186 | 338 | 外送为主，堂食弱 |
| 肯德基 | 610 | 252 | — |
| 牛约堡 | 61 | **37** | 🔴 有店无人 |
| 犇犇堡 | 29 | **3** | 🔴 有店无人 |
| 轻遇三明治 | 41 | **0** | 🔴 41 家店，评论中位为 0 |
```


#### gold HTML 图 slide 33

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 33 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 07 / 47 · 贰 · 经营基本盘
h2: 六店定位气泡图：流量与客单的两难
SOURCE: 账单明细 6

SIX-STORE POSITIONING 
图 07 / 47 · 贰 · 经营基本盘 

六店定位气泡图：流量与客单的两难

数据来源 / SOURCE 账单明细 6 店， 2026 年 6 月，堂食 16,867 桌 

[SVG omitted]

关键结论 / KEY INSIGHTS 颐堤港日均 125.1 桌全司最高、桌均 ¥379.5 最低，属高流量低客单；祥云小镇与 DT51 桌均领先但日均桌数垫底；国贸是唯一纯堂食门店。 

清水亭 · 产品结构诊断 · TIANSIGHT 33 / 296
```


<a id="l3-viz-hist-cdf"></a>

### L3 viz `hist-cdf`

- FT question: `distribution`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 36, 124, 129
- samples: 5

#### MD data behind `hist-cdf` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L343–L380
- genre: `diagnosis`
- note: 2.2 人均分档 + 推荐直方图

```
### 按人均消费分档

| 人均档 | 桌数 | 桌占比 | 实收额 | 额占比 | 桌均 | 平均人数 |
|---|---:|---:|---:|---:|---:|---:|
| ≤¥50 | 506 | 3.0% | ¥35,154 | 0.5% | ¥69.5 | 2.9 |
| ¥50–80 | 1,106 | 6.6% | ¥222,815 | 3.2% | ¥201.5 | 2.9 |
| ¥80–100 | 1,615 | 9.7% | ¥452,155 | 6.6% | ¥280.0 | 3.1 |
| ¥100–120 | 2,629 | 15.8% | ¥856,807 | 12.4% | ¥325.9 | 2.9 |
| **¥120–150** | **3,734** | **22.4%** | **¥1,490,678** | **21.7%** | ¥399.2 | 2.9 |
| **¥150–180** | **3,248** | **19.5%** | **¥1,431,373** | **20.8%** | ¥440.7 | 2.7 |
| ¥180–220 | 2,068 | 12.4% | ¥1,127,429 | 16.4% | ¥545.2 | 2.8 |
| ¥220–300 | 1,324 | 8.0% | ¥897,331 | 13.0% | ¥677.7 | 2.7 |
| >¥300 | 412 | 2.5% | ¥370,638 | 5.4% | ¥899.6 | 2.4 |

**人均中位数 ¥139.2，均值 ¥146.1**。分店人均中位：国贸 ¥149.5 = DT51 ¥149.5 > 祥云 ¥140.0 > 世纪金源 ¥134.5 > 颐堤港 ¥132.4 > 五棵松 ¥131.5。

> **口径说明**：上表桌数合计 16,642，比堂食总桌数 16,867 少 **225 桌**。这 225 张账单的实收金额为 **¥0**（全额赠送或全免），人均无法计算，故不进入分档。它们仍计入桌均分母：¥6,884,379 ÷ 16,867 = ¥408.2；若剔除这 225 桌，桌均为 **¥413.7**（+1.3%）。全报告桌均统一采用含零值桌的 ¥408.2 口径。

### 按桌型（就餐人数）

| 桌型 | 桌数 | 桌占比 | 实收额 | 额占比 | 桌均 | 件/桌 |
|---|---:|---:|---:|---:|---:|---:|
| 1 人 | 1,182 | 7.0% | ¥167,413 | 2.4% | ¥141.6 | 4.5 |
| **2 人** | **8,359** | **49.6%** | **¥2,600,398** | **37.8%** | ¥311.1 | 7.1 |
| 3 人 | 3,423 | 20.3% | ¥1,399,167 | 20.3% | ¥408.8 | 9.1 |
| 4 人 | 2,092 | 12.4% | ¥1,079,903 | 15.7% | ¥516.2 | 10.8 |
| 5–6 人 | 1,292 | 7.7% | ¥981,131 | 14.3% | ¥759.4 | 14.4 |
| 7–8 人 | 372 | 2.2% | ¥419,003 | 6.1% | ¥1,126.4 | 20.1 |
| 9 人+ | 147 | 0.9% | ¥237,365 | 3.4% | ¥1,614.7 | 26.7 |

🔑 **关键结论**

1. **2 人桌占据半壁江山**（49.6% 桌数、37.8% 收入），加上 3 人桌，2–3 人合计 69.9% 桌数、58.1% 收入。菜单设计的第一优先级客群是 2–3 人。
2. 人均 ¥120–180 区间贡献 41.9% 桌数与 42.5% 收入，是清水亭的**核心价格心智带**。
3. 人均 ≤¥100 的低值桌占 19.3%，仅贡献 10.3% 收入；这批桌的件/桌与桌均都显著偏低，是「主菜渗透率」提升的主要目标群（见第 8 章）。
4. 5 人以上大桌仅占 10.8% 桌数，却贡献 23.8% 收入，桌均是 2 人桌的 2.4–5.2 倍。宴请/家庭聚餐场景的产品配置（大份规格、套餐）具备明确的经济价值。

📊 **推荐图表**：人均消费直方图 + 累计曲线（标注中位数 ¥139.2）；桌型双轴图（桌数占比柱 + 桌均折线）。
```


#### MD data behind `hist-cdf` · briefing

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L252–L272
- genre: `briefing`
- note: 全市西式价格带直方图

```
## 2.2 价格带直方图 —— 核心假设的验证结果

### 全市西式（n=5,145）

| 价格带 | 门店数 | 占比 | 累计 |
|---|---|---|---|
| <15 | 34 | 0.7% | 0.7% |
| 15–20 | 177 | 3.4% | 4.1% |
| 20–25 | 358 | 7.0% | 11.1% |
| 25–30 | 711 | 13.8% | 24.9% |
| **30–35** | **960** | **18.7%** | 43.6% |
| 35–40 | 440 | 8.6% | 52.2% |
| 40–45 | 173 | 3.4% | 55.6% |
| 45–50 | 179 | 3.5% | 59.1% |
| 50–55 | 235 | 4.6% | 63.7% |
| **55–60** | **197** | **3.8%** | 67.5% |
| 60–70 | 279 | 5.4% | 72.9% |
| 70–80 | 253 | 4.9% | 77.8% |
| 80–100 | 255 | 5.0% | 82.8% |
| 100–150 | 525 | 10.2% | 93.0% |
| 150+ | 369 | 7.2% | 100% |
```


#### gold HTML 图 slide 36

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 36 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 08 / 47 · 贰 · 经营基本盘
h2: 人均消费分布：核心心智带在 ¥120 – 180
SOURCE: 账单头，堂食 16,867

PER-CAPITA HISTOGRAM 
图 08 / 47 · 贰 · 经营基本盘 

人均消费分布：核心心智带在 ¥120 – 180 

数据来源 / SOURCE 账单头，堂食 16,867 单，人均 = 实收 ÷ 就餐人数 

[SVG omitted]

关键结论 / KEY INSIGHTS ¥120 – 180 区间贡献 41.9% 桌数与 42.5% 收入；人均 ≤ ¥100 的低值桌占 19.3% 却只贡献 10.3% 收入，是主菜渗透率提升的主要目标群。 

清水亭 · 产品结构诊断 · TIANSIGHT 36 / 296
```


#### gold HTML 图 slide 124

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 124 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 25 / 47 · 柒 · 品类倾向系数、价格带与价格空档
h2: 各系列价格分布箱线图：跨度与集中度
SOURCE: 口径 A 118

PRICE DISTRIBUTION BOXPLOT 
图 25 / 47 · 柒 · 品类倾向系数、价格带与价格空档 

各系列价格分布箱线图：跨度与集中度

数据来源 / SOURCE 口径 A 118 SKU 标准售价，按系列分组 

[SVG omitted]

关键结论 / KEY INSIGHTS 套餐（ ¥239 – 549 ）与招牌淡水鱼鲜（ ¥69 – 299 ）跨度最大；小龙虾配菜 4 个 SKU 全部 ¥13 单一价格点，缺乏价格梯度设计。 

清水亭 · 产品结构诊断 · TIANSIGHT 124 / 296
```


#### gold HTML 图 slide 129

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 129 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 24 / 47 · 柒 · 品类倾向系数、价格带与价格空档
h2: 价格带阶梯图： ¥200 – 260 是最大的 60 元空档
SOURCE: 口径 A 118

PRICE BAND LADDER 
图 24 / 47 · 柒 · 品类倾向系数、价格带与价格空档 

价格带阶梯图： ¥200 – 260 是最大的 60 元空档

数据来源 / SOURCE 口径 A 118 SKU 标准售价， 10 元步长扫描 

[SVG omitted]

关键结论 / KEY INSIGHTS ¥199 的丹江大鱼头卖出 6,494 份（销量第 8 、销售额第 2 ），向上完全没有承接产品，直接跳到 ¥269 ； 5 人以上大桌桌均 ¥759 – 1,615 ，正缺 ¥200 – 260 的宴请型主菜。 

清水亭 · 产品结构诊断 · TIANSIGHT 129 / 296
```


<a id="l3-viz-pareto"></a>

### L3 viz `pareto`

- FT question: `ranking`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 62
- samples: 2

#### MD data behind `pareto` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L505–L519
- genre: `diagnosis`
- note: 4.2 口径 A 二八结果

```
## 4.2 口径 A（标准价，72 天）结果

### 全六店

| 分类 | SKU | SKU 占比 | 销售额 | 额占比 | 销量 | 量占比 | 毛利额 | 利占比 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **首选品** | 30 | 25.4% | ¥9,817,242 | **63.2%** | 150,029 | 57.5% | ¥6,617,412 | 61.7% |
| **必售品** | 21 | 17.8% | ¥3,642,614 | 23.5% | 72,891 | 27.9% | ¥2,567,778 | 23.9% |
| **观察品** | 29 | 24.6% | ¥1,595,649 | 10.3% | 22,988 | 8.8% | ¥1,175,157 | 11.0% |
| **长尾品** | 38 | 32.2% | ¥477,799 | 3.1% | 14,948 | 5.7% | ¥362,512 | 3.4% |
| **合计** | **118** | 100% | **¥15,533,304** | 100% | **260,856** | 100% | **¥10,722,859** | 100% |

**集合规模**：S1（销售额 80%）= 40 个 SKU｜S2（销量 80%）= 41 个 SKU｜**交集 = 30 个**｜并集 = 51 个

**二八验证**：25.4% 的 SKU 贡献 63.2% 的销售额；43.2% 的 SKU（首选 + 必售）贡献 86.7% 的销售额。二八法则成立，且比经典 20/80 更集中。
```


#### gold HTML 图 slide 62

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 62 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 11 / 47 · 肆 · ABC 贡献与二八分析（双口径）
h2: 帕累托双轴图： 25.4% 的 SKU 贡献 63.2% 的销售额
SOURCE: 口径 A 标准价，全六店 118

PARETO · DUAL AXIS 
图 11 / 47 · 肆 · ABC 贡献与二八分析（双口径） 

帕累托双轴图： 25.4% 的 SKU 贡献 63.2% 的销售额

数据来源 / SOURCE 口径 A 标准价，全六店 118 SKU / 72 天 / 40,840 台 

[SVG omitted]

关键结论 / KEY INSIGHTS S1（销售额 80% ）= 40 个 SKU，S2（销量 80% ）= 41 个，交集 30 个即首选品； 43.2% 的 SKU 贡献 86.7% 销售额，比经典 20 / 80 更集中。 

清水亭 · 产品结构诊断 · TIANSIGHT 62 / 296
```


<a id="l3-viz-slope"></a>

### L3 viz `slope`

- FT question: `ranking`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 71
- samples: 2

#### MD data behind `slope` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L746–L760
- genre: `diagnosis`
- note: 双口径排名变动

```
### 排名变动最大的品项

| 品项 | 系列 | 角色 | 标准价排名 | 实收排名 | 变化 | 标准价额 | 实收额 | 标准价分类 → 实收分类 |
|---|---|---|---:|---:|---:|---:|---:|---|
| 武当山笋牛杂煲 | 湖北烟火热菜 | 佐 | 32 | 11 | **+21** | ¥163,404 | ¥170,571 | 观察品 → **首选品** |
| 洪湖脆藕排骨汤 | 湖北煨汤 | 辅 | 16 | 7 | +9 | ¥294,216 | ¥213,763 | 首选品 → 首选品 |
| 手撕椒炒黑猪肉 | 湖北烟火热菜 | 佐 | 29 | 21 | +8 | ¥182,643 | ¥111,533 | 必售品 → **首选品** |
| 武汉卤鸭拼盘 | 凉菜/卤味 | 引 | 28 | 22 | +6 | ¥186,015 | ¥110,989 | 首选品 → 首选品 |
| 豆米烧丝瓜 | 湖北烟火热菜 | 佐 | 30 | 26 | +4 | ¥180,941 | ¥96,898 | 首选品 → 首选品 |
| 金奖麻辣油焖小龙虾 | 时令小龙虾 | 辅 | 4 | **1** | +3 | ¥887,433 | ¥548,781 | 首选品 → 首选品 |
| 活动-三鲜豆皮春卷 | 小吃点心主食 | 佐 | 82 | 145 | **−63** | ¥126 | ¥54 | 长尾品 → 长尾品 |
| 鲜榨秭归橙子雪梨汁 | 自制饮品甜品 | 佐 | 73 | 128 | −55 | ¥10,947 | ¥943 | 长尾品 → 长尾品 |
| 时令水果拼盘 | 凉菜 | 引 | 78 | 117 | −39 | ¥2,553 | ¥1,714 | 长尾品 → 长尾品 |
| 手工碱水面 | 小吃点心主食 | 佐 | 77 | 113 | −36 | ¥4,836 | ¥2,065 | 长尾品 → 长尾品 |
| 鲜榨玉米汁 | 自制饮品甜品 | 佐 | 75 | 108 | −33 | ¥9,717 | ¥2,757 | 长尾品 → 长尾品 |
```


#### gold HTML 图 slide 71

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 71 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 13 / 47 · 肆 · ABC 贡献与二八分析（双口径）
h2: 双口径排名斜率图：小龙虾按斤计价，实收口径跃居第一
SOURCE: 口径 A 标准价 72

DUAL-CALIBRE SLOPE 
图 13 / 47 · 肆 · ABC 贡献与二八分析（双口径） 

双口径排名斜率图：小龙虾按斤计价，实收口径跃居第一

数据来源 / SOURCE 口径 A 标准价 72 天 vs 口径 B 账单实收 6 月， 79 个可比品项 

[SVG omitted]

关键结论 / KEY INSIGHTS 分类迁移一致率 82.3% ，结构性结论稳健；武当山笋牛杂煲上升 21 位（观察品 → 首选品），鲜榨类饮品在实收口径下全线下沉。 

清水亭 · 产品结构诊断 · TIANSIGHT 71 / 296
```


<a id="l3-viz-diverging-bar"></a>

### L3 viz `diverging-bar`

- FT question: `deviation`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 72, 84, 121
- samples: 4

#### MD data behind `diverging-bar` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L762–L777
- genre: `diagnosis`
- note: 系列折让率正负双向

```
### 系列级双口径对比

| 系列 | 标准价额（72天） | 标准占比 | 实收额（30天） | 实收占比 | 差异 | 折让率 |
|---|---:|---:|---:|---:|---:|---:|
| 湖北烟火热菜 | ¥3,225,838 | 20.8% | ¥1,619,000 | 20.7% | −0.1pt | 0.4% |
| 招牌淡水鱼鲜 | ¥3,052,266 | 19.6% | ¥1,417,055 | 18.1% | −1.5pt | 2.1% |
| 套餐 | ¥2,604,620 | 16.8% | ¥1,218,189 | 15.6% | −1.2pt | −1.3% |
| 时令小龙虾 | ¥1,884,474 | 12.1% | ¥1,114,648 | **14.2%** | **+2.1pt** | **−49.9%** |
| 湖北煨汤 | ¥1,737,754 | 11.2% | ¥718,168 | 9.2% | −2.0pt | −16.0% |
| 小吃点心主食 | ¥795,692 | 5.1% | ¥383,069 | 4.9% | −0.2pt | 9.1% |
| 凉菜/卤味 | ¥699,216 | 4.5% | ¥366,878 | 4.7% | +0.2pt | 10.5% |
| 自制饮品甜品 | ¥558,716 | 3.6% | ¥240,037 | 3.1% | −0.5pt | −35.8% |
| 蒸菜 | ¥476,836 | 3.1% | ¥225,681 | 2.9% | −0.2pt | 1.6% |
| 洪湖莲藕系列 | ¥395,728 | 2.5% | ¥198,182 | 2.5% | 0.0pt | 1.2% |
| 酒水（口径A已排除） | — | — | ¥131,326 | 1.7% | — | 2.8% |
| 时令小龙虾/配菜 | ¥99,060 | 0.6% | ¥64,481 | 0.8% | +0.2pt | 1.5% |
```


#### gold HTML 图 slide 72

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 72 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 14 / 47 · 肆 · ABC 贡献与二八分析（双口径）
h2: 系列折让率双向条形图：负值来自按斤计价与规格结构
SOURCE: 口径 A 标准价额 vs 口径 B 实收额，同为 6

DISCOUNT RATE DIVERGING BAR 
图 14 / 47 · 肆 · ABC 贡献与二八分析（双口径） 

系列折让率双向条形图：负值来自按斤计价与规格结构

数据来源 / SOURCE 口径 A 标准价额 vs 口径 B 实收额，同为 6 月六店 

[SVG omitted]

关键结论 / KEY INSIGHTS 凉菜/卤味 10.5% 与小吃点心主食 9.1% 折让最重，团购券核销集中于此；小龙虾 −49.9% 属按斤计价的重量溢价，不是优惠。 

清水亭 · 产品结构诊断 · TIANSIGHT 72 / 296
```


#### gold HTML 图 slide 84

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 84 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 17 / 47 · 伍 · 四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率
h2: 大份 vs 例份：整体无毛利优势，优势只集中在三款鱼鲜
SOURCE: 口径 A， 20

LARGE-PORTION MARGIN DELTA 
图 17 / 47 · 伍 · 四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率 

大份 vs 例份：整体无毛利优势，优势只集中在三款鱼鲜

数据来源 / SOURCE 口径 A， 20 组「例/迷你份 — 大份」同品项配对的毛利率与千单点击 

[SVG omitted]

关键结论 / KEY INSIGHTS 20 组配对中大份毛利率更高的只有 7 组、更低的 13 组，中位差 −0.7pt ——「大份普遍高毛利」不成立。真正的优势集中在招牌淡水鱼鲜三款（ +7.1 ~ 14.1pt ），而它们恰是全店毛利最低的主力菜（该系列 60.64% ，低于全店 8.4pt ）。大份曝光不足则确凿：千单点击中位仅为例份的 12.1% 。 

清水亭 · 产品结构诊断 · TIANSIGHT 84 / 296
```


#### gold HTML 图 slide 121

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 121 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 23 / 47 · 柒 · 品类倾向系数、价格带与价格空档
h2: 国贸 vs 五店品类渗透率：套餐是唯一的反向缺口
SOURCE: 账单明细 6

GUOMAO VS FIVE-STORE DUMBBELL 
图 23 / 47 · 柒 · 品类倾向系数、价格带与价格空档 

国贸 vs 五店品类渗透率：套餐是唯一的反向缺口

数据来源 / SOURCE 账单明细 6 月堂食，国贸 3,690 桌 / 五店 13,177 桌 

[SVG omitted]

关键结论 / KEY INSIGHTS 国贸在除套餐外的所有品类上渗透率与桌均贡献全面领先；国贸 6 月套餐销售为零，五店套餐桌均贡献 ¥74.1 ，这是国贸桌均的最大机会缺口。 

清水亭 · 产品结构诊断 · TIANSIGHT 121 / 296
```


<a id="l3-viz-quadrant"></a>

### L3 viz `quadrant`

- FT question: `correlation`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 42, 83, 230
- samples: 5

#### MD data behind `quadrant` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L399–L407
- genre: `diagnosis`
- note: 角色理论 vs 实际

```
理论上「主辅佐引」应呈现如下特征梯度：

| 角色 | 理论定位 | 应有特征 | 实际表现 | 判定 |
|---|---|---|---|---|
| 主（君） | 品牌认知锚点 | 高价、高渗透、高额量比、SKU 少 | 均价 ¥142.8（最高）、额量比 2.40（最高）、SKU 11%（最少） | ✅ 价格与稀缺性达标 |
| — | — | 渗透率应最高 | **渗透率 6.8%（垫底，与「佐」并列）** | ❌ **认知锚点未落地** |
| 辅（臣） | 撑收入的主力 | 中高价、高销量、高毛利 | 额占比 29.6%（第一）、利占比 30.4%（第一）、中位千单点击 36.4（最高） | ✅ 达标，实为收入第一支柱 |
| 佐（佐） | 高频连带、拉动件数 | 低价、高销量、高毛利率 | 均价 ¥50.8（最低）、量占比 57.9%（最高）、毛利率 78.8%（最高） | ✅ 完全达标 |
| 引（使） | 引流、低门槛 | **低价**、高渗透、低额量比 | **均价 ¥105.9（第二高）、额量比 1.78（第二高）** | ❌ **引流品被高价化** |
```


#### MD data behind `quadrant` · briefing

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L841–L852
- genre: `briefing`
- note: 竞争定位矩阵

```
## 3.9 竞争定位矩阵（数据版）

| 维度 | 石头先生（目标） | Shake Shack 合生汇 | 萨莉亚 合生汇 | 蓝蛙 合生汇 | 21 街区均值 | 必胜客 大郊亭桥 |
|---|---|---|---|---|---|---|
| 人均 | **58–62** | 62 | 52 | 136 | 35.5 | 63 |
| 评分 | **目标 ≥4.5** | 4.3 | 4.1 | 4.8 | 4.01 | 4.5 |
| 评论量级 | 目标 90 天 ≥2,000 | 6,305 | 1,310 | 2,475 | 中位 2,153 | 1,560 |
| 品类心智 | 现做西式简餐 | 美式汉堡 | 意式平价 | 美式休闲西餐 | 重口中餐+小吃 | 披萨简餐 |
| 出餐速度 | 待压测 | 快 | 中 | 慢 | 快 | 中 |
| 明档 | **✅ 三大明档** | 半开放 | 无 | 无 | 部分 | 无 |
| 北京规模 | 1 | 7 | 65 | 17 | — | 281 |
| 全时段 | 午/晚/下午茶 | 全天 | 全天 | 晚市为主 | 晚市为主 | 全天 |
```


#### gold HTML 图 slide 42

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 42 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 09 / 47 · 叁 · 主辅佐引角色分类结果与数据校验
h2: 角色校验四象限： 13 个「主」品的渗透率只有 6.8%
SOURCE: 口径 A 额量比（ 118

ROLE AUDIT QUADRANT 
图 09 / 47 · 叁 · 主辅佐引角色分类结果与数据校验 

角色校验四象限： 13 个「主」品的渗透率只有 6.8% 

数据来源 / SOURCE 口径 A 额量比（ 118 SKU）+ 口径 B 堂食渗透率（ 6 月 16,867 桌） 

[SVG omitted]

关键结论 / KEY INSIGHTS 「主」（朱红）本应落在右上高渗透高价区，实际大量散布在左侧低渗透区；渗透率第一的是「辅」类的铫子煨排骨莲藕汤 17.7% ，高于所有主品。 

清水亭 · 产品结构诊断 · TIANSIGHT 42 / 296
```


#### gold HTML 图 slide 83

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 83 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 16 / 47 · 伍 · 四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率
h2: 高潜品四象限： 31 款「利润黑马」等待强制曝光
SOURCE: 口径 A，千单点击中位 27.20

HIGH-POTENTIAL QUADRANT 
图 16 / 47 · 伍 · 四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率 

高潜品四象限： 31 款「利润黑马」等待强制曝光

数据来源 / SOURCE 口径 A，千单点击中位 27.20 / 毛利率中位 75.9% 

[SVG omitted]

关键结论 / KEY INSIGHTS 左上朱红区 31 款高毛利低曝光品中有 9 款是「大份」规格，毛利率比例份高 3 – 8pt 、千单点击只有例份的 1 / 5 – 1 / 10 ，是最容易兑现的毛利增量。 

清水亭 · 产品结构诊断 · TIANSIGHT 83 / 296
```


#### gold HTML 图 slide 230

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 230 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 46 / 47 · 拾叁 · 结论与行动清单
h2: 行动清单优先级矩阵：P0 七项全在低难度高效益区
SOURCE: 第 13.2

ACTION PRIORITY MATRIX 
图 46 / 47 · 拾叁 · 结论与行动清单 

行动清单优先级矩阵：P0 七项全在低难度高效益区

数据来源 / SOURCE 第 13.2 节 20 项行动，按落地难度 × 月度效益量级定位 

[SVG omitted]

关键结论 / KEY INSIGHTS P0 七项 0 – 30 天可落地，合计月增效益约 ¥829,000 ；P1 七项需产品开发，P2 六项属战略层，不带直接效益测算但决定长期结构。 

清水亭 · 产品结构诊断 · TIANSIGHT 230 / 296
```


<a id="l3-viz-heatmap"></a>

### L3 viz `heatmap`

- FT question: `distribution`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 93, 151, 174, 184
- samples: 6

#### MD data behind `heatmap` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L1938–L1960
- genre: `diagnosis`
- note: 九宫销售额

```
## 10.2 味型 × 工艺九宫格

**分组规则**
- 味型组：辣/麻（含辣、麻字样）｜甜/酸（含甜、酸、甘字样）｜咸鲜/本味/香（其余）
- 工艺组：快工艺（炒、油爆、炕炒、炕、干煸、煎、凉拌、搓、浇汁）｜慢工艺（炖、烧、煮、浸煮、卤、热卤、烩、熟醉、浸泡）｜特殊工艺（蒸、清蒸、烤、炸等）

### SKU 数分布

| 味型 ＼ 工艺 | 快工艺 | 慢工艺 | 特殊工艺 | 合计 |
|---|---:|---:|---:|---:|
| 咸鲜/本味/香 | 16 | **24** | 17 | **57** |
| 甜/酸 | 4 | 3 | 5 | 12 |
| 辣/麻 | 8 | 13 | **0** | 21 |
| **合计** | **28** | **40** | **22** | **90** |

### 销售额分布（万元，口径 A）

| 味型 ＼ 工艺 | 快工艺 | 慢工艺 | 特殊工艺 | 合计 |
|---|---:|---:|---:|---:|
| 咸鲜/本味/香 | ¥181.5 | **¥402.1** | ¥164.3 | ¥747.9 |
| 甜/酸 | ¥27.5 | ¥10.5 | ¥42.3 | ¥80.3 |
| 辣/麻 | ¥74.6 | **¥347.0** | **¥0.0** | ¥421.6 |
| **合计** | **¥283.6** | **¥759.6** | **¥206.6** | **¥1,249.8** |
```


#### MD data behind `heatmap` · briefing

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L928–L936
- genre: `briefing`
- note: 九宫重复三条线

```
## 4.3 九宫格重复度诊断

**严重重复的三条线：**

| 重复元素 | 出现次数 | 涉及产品 | 问题 |
|---|---|---|---|
| **黑松露** | **5 处** | 火柴薯条、芝士熔岩球、黑松露蘑菇牛肉堡、黑松露什锦蘑菇披萨、硬币堡酱料 | 高级感被稀释成日常调味，顾客感知不到"贵"。**且北京 6052 家西式门店中，店名含"黑松露"的：0 家——这个词从来不是一个能被顾客搜索到的记忆点** |
| **川味/香辣** | **7 处** | 香辣鸡翅、川味椒麻堡、辣肉酱堡、蜀香辣肉酱披萨、麻辣小龙虾披萨、川味腊肠意面、泰式酸辣沙拉 | 国风融合是真差异点，但 7 处过载，分散在 5 个档口 |
| **海鲜** | **7 处** | 西班牙鱿鱼煎蛋、墨鱼肠、那不勒斯海鲜披萨、蒜香白酒海鲜面、日式海胆拌饭、小龙虾披萨、大虾沙拉 | 🔴 **海鲜是损耗最高、备货最难、跨省供应链最脆弱的一类。首店是跨省首店，这条线风险最高** |
```


#### gold HTML 图 slide 93

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 93 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 18 / 47 · 伍 · 四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率
h2: 待下架条件命中热力图： 17 款命中 3 条， 11 款是自制饮品甜品
SOURCE: 口径 A 四条标准：千单点击< 20

DELIST CRITERIA HEATMAP 
图 18 / 47 · 伍 · 四大单品指标：额量比 · 千单点击 · 毛利率 · 渗透率 

待下架条件命中热力图： 17 款命中 3 条， 11 款是自制饮品甜品

数据来源 / SOURCE 口径 A 四条标准：千单点击< 20 / 额量比< 0.7 / 毛利率< 65% / 渗透率< 2% 

[SVG omitted]

关键结论 / KEY INSIGHTS 精简 17 款释放 14.4% 的 SKU 数，只损失 2.3% 销售额；【工作日超值】双人餐 ¥239 虽命中 3 条但属必售品，建议下调至 ¥169 – 199 重测而非直接砍掉。 

清水亭 · 产品结构诊断 · TIANSIGHT 93 / 296
```


#### gold HTML 图 slide 151

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 151 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 31 / 47 · 捌 · 客单组合逻辑与小票分析
h2: 时段 × 品类桌均贡献热力图：小龙虾是唯一的晚市品类
SOURCE: 账单明细 6

DAYPART × CATEGORY HEATMAP 
图 31 / 47 · 捌 · 客单组合逻辑与小票分析 

时段 × 品类桌均贡献热力图：小龙虾是唯一的晚市品类

数据来源 / SOURCE 账单明细 6 月堂食，午市 7,969 桌 / 晚市 8,898 桌 

[SVG omitted]

关键结论 / KEY INSIGHTS 小龙虾晚市溢价 +53.9% ，套餐 −16.8% 、招牌鱼鲜 −8.5% 反而是午市品类；午晚市桌均仅差 3.1% ，清水亭是少见的强午市正餐品牌。 

清水亭 · 产品结构诊断 · TIANSIGHT 151 / 296
```


#### gold HTML 图 slide 174

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 174 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 36 / 47 · 拾 · 九宫格：味型 × 工艺 / 味型 × 食材
h2: 味型 × 工艺九宫格：唯一空白格是辣/麻 × 特殊工艺
SOURCE: 品项汇总新版·索引表， 90

FLAVOUR × TECHNIQUE NINE-GRID 
图 36 / 47 · 拾 · 九宫格：味型 × 工艺 / 味型 × 食材 

味型 × 工艺九宫格：唯一空白格是辣/麻 × 特殊工艺

数据来源 / SOURCE 品项汇总新版·索引表， 90 个同时有味型与工艺标注的 SKU（味型覆盖 92 / 118 、工艺 91 / 118 ） 

[SVG omitted]

关键结论 / KEY INSIGHTS 咸鲜×慢工艺（ 24 款 ¥402.1 万）与辣/麻×慢工艺（ 13 款 ¥347.0 万）两格合计贡献 60.0% 销售额，构成技术护城河；辣/麻×特殊工艺完全空缺，剁椒蒸鱼头、香辣烤鱼是最自然的补位。 

清水亭 · 产品结构诊断 · TIANSIGHT 174 / 296
```


#### gold HTML 图 slide 184

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 184 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 37 / 47 · 拾 · 九宫格：味型 × 工艺 / 味型 × 食材
h2: 味型 × 食材矩阵：辣/麻 × 猪、辣/麻 × 绿叶是仅有的两个结构性缺口
SOURCE: 品项汇总新版·索引表， 92

FLAVOUR × INGREDIENT MATRIX 
图 37 / 47 · 拾 · 九宫格：味型 × 工艺 / 味型 × 食材 

味型 × 食材矩阵：辣/麻 × 猪、辣/麻 × 绿叶是仅有的两个结构性缺口

数据来源 / SOURCE 品项汇总新版·索引表， 92 个同时有味型与食材标注的 SKU（食材维度实际覆盖 114 / 118 = 96.6% ） 

[SVG omitted]

关键结论 / KEY INSIGHTS 辣/麻 行共 7 个零值格，但只有猪（ 15 SKU、 18.8% 销售额）与素-绿叶类（ 7 SKU）基数足够大、零值才构成结构性判断；其余 5 格（蛋类 3 、甜品 5 、水果 1 、海鲜 1 、饮品 3 ）基数过小不作判断。猪肉是第一大食材却无任何辣味做法——剁椒蒸腊肉、香辣猪蹄、辣炒回锅肉全部缺失。 

清水亭 · 产品结构诊断 · TIANSIGHT 184 / 296
```


<a id="l3-viz-treemap"></a>

### L3 viz `treemap`

- FT question: `part-to-whole`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 29, 102
- samples: 4

#### MD data behind `treemap` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L1133–L1161
- genre: `diagnosis`
- note: 6.1 现状结构树

```
## 6.1 现状结构树（口径 A，全六店）

```
清水亭 全六店 118 SKU / ¥15,533,304（72天标准价口径）
│
├── 主（13 SKU, 11.0%）── ¥3,052,266 (19.6%) ── 均价¥142.8 ── 毛利64.0%
│    └── 招牌淡水鱼鲜 13 款：山茶油丹江大鱼头 / 公安鱼杂煲 / 山茶油宜昌肥鱼 /
│         油爆丹江活青虾 / 山茶葱油蒸武昌鱼 / 清蒸翘嘴鲌 / 油焖罗氏虾烧年糕 /
│         楚地炒鱼泡 / 荆沙甲鱼 + 4 个大份规格
│
├── 辅（29 SKU, 24.6%）── ¥4,593,852 (29.6%) ── 均价¥95.8 ── 毛利74.2%
│    ├── 湖北煨汤 7 款  ¥1,737,754 (11.2%)  ← 渗透率第一 17.7%
│    ├── 时令小龙虾 10 款 ¥1,884,474 (12.1%) ← 季节性主力
│    ├── 蒸菜 4 款      ¥476,836 (3.1%)
│    ├── 洪湖莲藕系列 4 款 ¥395,728 (2.5%)
│    └── 小龙虾配菜 4 款  ¥99,060 (0.6%)
│
├── 佐（56 SKU, 47.5%）── ¥4,580,247 (29.5%) ── 均价¥50.8 ── 毛利78.8%
│    ├── 湖北烟火热菜 23 款 ¥3,225,838 (20.8%) ← 五店定义为佐
│    ├── 自制饮品甜品 25 款 ¥558,716 (3.6%)   ← 18 款长尾
│    └── 小吃点心主食 8 款  ¥795,692 (5.1%)   ← 销量第一梯队
│
└── 引（20 SKU, 16.9%）── ¥3,306,940 (21.3%) ── 均价¥105.9 ── 毛利73.7%
     ├── 套餐 4 款      ¥2,604,620 (16.8%)  ← 角色错配，实为主
     ├── 凉菜/卤味 14 款 ¥699,216 (4.5%)
     └── 凉菜 2 款      ¥3,104 (0.0%)
```

## 6.2 3-4-2-1 理想结构达标检查
```


#### MD data behind `treemap` · system

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L1107–L1131
- genre: `system`
- note: 依赖层级 L0–L6

```
## 6.1 依赖层级

```
L0 地基 ── A01 资产盘点 → A02 三路对账 → A03 质量检测
                 ├─→ 口径 A（索引表）
                 └─→ 口径 B（账单明细）
                          │
L1 基础指标 ── A10 ABC ─ A13 额量比 ─ A14 千单点击 ─ A15 毛利率 ─ A16 渗透率
                 │           └────────┬──────────────┘             │
L2 合成分析 ── A11 四分类              ▼                            │
                 │            A17 四象限 → A18 待下架 → A19 高潜品   │
                 ├─→ A20 结构树 ← A07 角色校验 ←────────────────────┤
                 ├─→ A21 3-4-2-1 ─ A22 效率指数 ─→ A23 目标结构     │
                 └─→ A49 生命周期 ← A48 动能榜 ← A45 季节走势 ←─────┤
                                                                    │
L3 行为分析 ── A28 角色组合 → A29 主菜杠杆 → A30 点单公式            │
               A31 连带 ─ A32 时段 ─ A33 星期 ─ A34 区域 ─ A35 外卖 ─┤
               A39 识别率 → A36 复购 → A37 间隔 → A38 会员价值 → A40 │
                                                                    │
L4 属性分析 ── A41 味型×工艺 ─ A42 味型×食材 ─ A43 工艺毛利 → A44 补漏
                                                                    │
L5 外部对照 ── A51 商圈 ─ A52/A53 竞品 ─ A54 榜单 ─ A55 客单反证 ───┤
                                                                    ▼
L6 收敛 ─────────────── A56 优先级矩阵 → A57 效益测算 → A58 结论审查
```
```


#### gold HTML 图 slide 29

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 29 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 06 / 47 · 壹 · 两套分析框架的对照与合并
h2: 合并后的分析体系： 13 个模块、 4 个层级
SOURCE: 苏帮袁七大板块 + 本次 5

THIRTEEN-MODULE ARCHITECTURE 
图 06 / 47 · 壹 · 两套分析框架的对照与合并 

合并后的分析体系： 13 个模块、 4 个层级

数据来源 / SOURCE 苏帮袁七大板块 + 本次 5 大类要求合并去重 

[SVG omitted]

关键结论 / KEY INSIGHTS 红框为本次补强的模块（M1 数据地图、M9 复购、M11 生命周期），这三项恰好回答「口径可信吗」「客人回来吗」「产品老化吗」三个长期问题。 

清水亭 · 产品结构诊断 · TIANSIGHT 29 / 296
```


#### gold HTML 图 slide 102

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 102 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 19 / 47 · 陆 · 菜单结构树与 3-4-2-1 理想结构
h2: 菜单结构树状图：面积 = 销售额，颜色 = 角色
SOURCE: 口径 A，全六店 118

MENU STRUCTURE TREEMAP 
图 19 / 47 · 陆 · 菜单结构树与 3-4-2-1 理想结构 

菜单结构树状图：面积 = 销售额，颜色 = 角色

数据来源 / SOURCE 口径 A，全六店 118 SKU / ¥15,533,304 / 72 天 

[SVG omitted]

关键结论 / KEY INSIGHTS 「佐」占 47.5% 的 SKU 数却只产出 29.5% 销售额；套餐 4 个 SKU 撑起 16.8% 销售额，效率指数 4.94 全店最高。 

清水亭 · 产品结构诊断 · TIANSIGHT 102 / 296
```


<a id="l3-viz-network"></a>

### L3 viz `network`

- FT question: `flow`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 142
- samples: 3

#### MD data behind `network` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L1531–L1553
- genre: `diagnosis`
- note: 8.4 连带提升度 TOP15

```
## 8.4 连带分析（同桌组合）

📂 **数据来源**：16,726 张堂食账单的品项两两共现（剔除赠品），共现 ≥100 桌的组合

### 提升度 TOP 15（Lift = 实际共现率 ÷ 独立共现率）

| A 品项 | B 品项 | 角色A | 角色B | 共现桌 | 支持度 | A→B | B→A | **提升度** |
|---|---|---|---|---:|---:|---:|---:|---:|
| 小龙虾手工魔芋 | 小龙虾洪湖藕片 | 辅 | 辅 | 313 | 1.9% | 44.2% | 34.9% | **8.24** |
| 【湖北特色】三鲜豆皮春卷 | 洪湖滋味糖水&甜品 | — | — | 223 | 1.3% | 36.3% | 24.2% | 6.58 |
| 小龙虾洪湖藕片 | 小龙虾臭豆腐 | 辅 | 辅 | 258 | 1.5% | 28.8% | 34.4% | 6.41 |
| 小龙虾手工魔芋 | 小龙虾臭豆腐 | 辅 | 辅 | 203 | 1.2% | 28.7% | 27.1% | 6.39 |
| 山茶油丹江大鱼头 | 时令蔬菜 | 主 | — | 125 | 0.7% | 4.7% | 85.0% | 5.30 |
| 外婆巧手火烧馍 | 时令蔬菜 | 佐 | — | 123 | 0.7% | 4.7% | 83.7% | 5.30 |
| 小龙虾手工碱水面 | 小龙虾洪湖藕片 | 辅 | 辅 | 453 | 2.7% | 27.9% | 50.5% | 5.20 |
| 小龙虾手工碱水面 | 小龙虾臭豆腐 | 辅 | 辅 | 342 | 2.0% | 21.0% | 45.6% | 4.69 |
| 小龙虾手工碱水面 | 小龙虾手工魔芋 | 辅 | 辅 | 302 | 1.8% | 18.6% | 42.7% | 4.39 |
| 小龙虾臭豆腐 | 金奖麻辣油焖小龙虾 | 辅 | 辅 | 523 | 3.1% | **69.7%** | 19.3% | 4.32 |
| 小龙虾手工魔芋 | 金奖麻辣油焖小龙虾 | 辅 | 辅 | 455 | 2.7% | 64.3% | 16.8% | 3.98 |
| 小龙虾洪湖藕片 | 金奖麻辣油焖小龙虾 | 辅 | 辅 | 575 | 3.4% | 64.1% | 21.3% | 3.97 |
| 小龙虾手工碱水面 | 黄金蒜蓉小龙虾 | 辅 | 辅 | 924 | 5.5% | 56.9% | 36.1% | 3.71 |
| 山茶油丹江大鱼头 | 荆楚卤水拼盘 | 主 | 引 | 110 | 0.7% | 4.1% | 58.5% | 3.65 |
| **外婆巧手火烧馍** | **山茶油丹江大鱼头** | 佐 | 主 | **1,281** | **7.7%** | **48.5%** | **47.8%** | **3.03** |
```


#### MD data behind `network` · system

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L1107–L1131
- genre: `system`
- note: 依赖层级 ASCII → network/treemap

```
## 6.1 依赖层级

```
L0 地基 ── A01 资产盘点 → A02 三路对账 → A03 质量检测
                 ├─→ 口径 A（索引表）
                 └─→ 口径 B（账单明细）
                          │
L1 基础指标 ── A10 ABC ─ A13 额量比 ─ A14 千单点击 ─ A15 毛利率 ─ A16 渗透率
                 │           └────────┬──────────────┘             │
L2 合成分析 ── A11 四分类              ▼                            │
                 │            A17 四象限 → A18 待下架 → A19 高潜品   │
                 ├─→ A20 结构树 ← A07 角色校验 ←────────────────────┤
                 ├─→ A21 3-4-2-1 ─ A22 效率指数 ─→ A23 目标结构     │
                 └─→ A49 生命周期 ← A48 动能榜 ← A45 季节走势 ←─────┤
                                                                    │
L3 行为分析 ── A28 角色组合 → A29 主菜杠杆 → A30 点单公式            │
               A31 连带 ─ A32 时段 ─ A33 星期 ─ A34 区域 ─ A35 外卖 ─┤
               A39 识别率 → A36 复购 → A37 间隔 → A38 会员价值 → A40 │
                                                                    │
L4 属性分析 ── A41 味型×工艺 ─ A42 味型×食材 ─ A43 工艺毛利 → A44 补漏
                                                                    │
L5 外部对照 ── A51 商圈 ─ A52/A53 竞品 ─ A54 榜单 ─ A55 客单反证 ───┤
                                                                    ▼
L6 收敛 ─────────────── A56 优先级矩阵 → A57 效益测算 → A58 结论审查
```
```


#### gold HTML 图 slide 142

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 142 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 28 / 47 · 捌 · 客单组合逻辑与小票分析
h2: 连带网络图：三个锚点、三套独立的组合逻辑
SOURCE: 16,726

BASKET NETWORK 
图 28 / 47 · 捌 · 客单组合逻辑与小票分析 

连带网络图：三个锚点、三套独立的组合逻辑

数据来源 / SOURCE 16,726 张堂食账单的品项两两共现，共现 ≥ 100 桌 

[SVG omitted]

关键结论 / KEY INSIGHTS 火烧馍×鱼头共现 1,281 桌、提升度 3.03 ，是全店最强的正价连带；小龙虾配菜提升度 3.7 – 8.2 属自然发生的组合，可直接产品化为「小龙虾伴侣三件套」。 

清水亭 · 产品结构诊断 · TIANSIGHT 142 / 296
```


<a id="l3-viz-line-dual"></a>

### L3 viz `line-dual`

- FT question: `change over time`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 150, 165, 189, 193
- samples: 5

#### MD data behind `line-dual` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L2096–L2117
- genre: `diagnosis`
- note: 11.1 小龙虾旬度

```
## 11.1 季节性主力：小龙虾

📂 **数据来源**：口径 A（72 天）+ 口径 B（6 月账单）

| 指标 | 数值 |
|---|---:|
| SKU 数（含配菜） | 14 款（时令小龙虾 10 + 配菜 4） |
| 标准价销售额（72 天） | ¥1,983,534（12.8%） |
| **实收额（6 月）** | **¥1,179,129（15.1%）** |
| 堂食渗透率 | 28.5% |
| 晚市溢价 | **+53.9%** |
| 加权毛利率 | 62–63%（全店最低食材类之一） |

### 6 月旬度走势

| 旬 | 堂食总实收 | 小龙虾实收 | 占比 | 桌数 | 桌均 |
|---|---:|---:|---:|---:|---:|
| 上旬（1–10 日） | ¥2,152,254 | ¥314,304 | **15.0%** | 5,236 | ¥411.0 |
| 中旬（11–20 日） | ¥2,595,808 | ¥365,405 | 14.0% | 6,235 | ¥416.0 |
| 下旬（21–30 日） | ¥2,136,041 | ¥285,935 | **13.0%** | 5,255 | ¥406.0 |

### 周度走势（件/千桌，堂食）
```


#### gold HTML 图 slide 150

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 150 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 30 / 47 · 捌 · 客单组合逻辑与小票分析
h2: 开台小时双轴图： 11 时与 18 时双高峰， 12 时翻台压缩客单
SOURCE: 账单明细 6

24-HOUR DUAL AXIS 
图 30 / 47 · 捌 · 客单组合逻辑与小票分析 

开台小时双轴图： 11 时与 18 时双高峰， 12 时翻台压缩客单

数据来源 / SOURCE 账单明细 6 月堂食 16,867 桌，按开台时间聚合 

[SVG omitted]

关键结论 / KEY INSIGHTS 12 时桌数最多（ 3,604 桌）桌均却降到 ¥405.5 ，中位时长从 62.0 分钟压到 56.8 分钟； 14 – 16 时低谷仅 960 桌、占 4.5% 收入，是明确的产能闲置窗口。 

清水亭 · 产品结构诊断 · TIANSIGHT 150 / 296
```


#### gold HTML 图 slide 165

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 165 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 34 / 47 · 玖 · 复购分析与客户资产
h2: 月度会员活跃趋势： 5 – 6 月激增来自小龙虾季新客
SOURCE: 会员消费文件 2026

MEMBER ACTIVITY TREND 
图 34 / 47 · 玖 · 复购分析与客户资产 

月度会员活跃趋势： 5 – 6 月激增来自小龙虾季新客

数据来源 / SOURCE 会员消费文件 2026 / 01 – 06 ，按月聚合 

[SVG omitted]

关键结论 / KEY INSIGHTS 消费笔数从 4 月 498 笔涨到 6 月 1,306 笔（ +162% ），与小龙虾季高度重合；但 6 月活跃会员 787 人中只有 15.9% 有复购记录——季节性产品带来的是新客而非复购客。 

清水亭 · 产品结构诊断 · TIANSIGHT 165 / 296
```


#### gold HTML 图 slide 189

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 189 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 39 / 47 · 拾壹 · 季节性产品矩阵与产品生命周期
h2: 小龙虾旬度占比： 6 月已进入回落通道
SOURCE: 账单明细 6

CRAYFISH DECLINE CURVE 
图 39 / 47 · 拾壹 · 季节性产品矩阵与产品生命周期 

小龙虾旬度占比： 6 月已进入回落通道

数据来源 / SOURCE 账单明细 6 月堂食，按上/中/下旬聚合 

[SVG omitted]

关键结论 / KEY INSIGHTS 占比从上旬 15.0% 降至下旬 13.0% ，主力单品周度降幅 17 – 25% ；小龙虾毛利率仅 62 – 63% （全店加权 69.03% ），退潮后菜单将失去 13 – 15% 收入且无接棒产品。 

清水亭 · 产品结构诊断 · TIANSIGHT 189 / 296
```


#### gold HTML 图 slide 193

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 193 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 41 / 47 · 拾壹 · 季节性产品矩阵与产品生命周期
h2: 藕汤替换事件：件数 +92.6% ，单品日均收入 −36.3%
SOURCE: 账单明细 6

SOUP SUBSTITUTION EVENT 
图 41 / 47 · 拾壹 · 季节性产品矩阵与产品生命周期 

藕汤替换事件：件数 +92.6% ，单品日均收入 −36.3% 

数据来源 / SOURCE 账单明细 6 月逐日，铫子煨排骨莲藕汤 vs 洪湖脆藕排骨汤 

[SVG omitted]

关键结论 / KEY INSIGHTS 6 月 17 日三规格 ¥89 / 169 / 269 的铫子煨排骨莲藕汤下架，换成单规格 ¥39 按位售卖的洪湖脆藕排骨汤；煨汤桌均贡献从 ¥46.8 掉到 ¥33.4 （ −28.6% ）。注意全店堂食桌均几乎持平（ ¥408.9 → ¥407.3 ），损失被其他品类补上； 6 / 27 – 6 / 30 新品已从谷底 ¥9,750 回升到 ¥15,325 ，可能是爬坡期而非结构性损失。「年化 ¥272 万」是上限推算，非损失确认（附录 F.14）。 

清水亭 · 产品结构诊断 · TIANSIGHT 193 / 296
```


<a id="l3-viz-calendar"></a>

### L3 viz `calendar`

- FT question: `change over time`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 198
- samples: 3

#### MD data behind `calendar` · diagnosis

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L2220–L2234
- genre: `diagnosis`
- note: 11.5 季节性产品矩阵

```
## 11.5 季节性产品矩阵（建议框架）

| 季节 | 月份 | 湖北时令食材 | 建议产品 | 现状 |
|---|---|---|---|---|
| 春 | 3–5 月 | 藕带、春笋、香椿、荠菜、鳜鱼 | 鲜藕带尖（已有）、武当山笋（已有）、香椿炒蛋、荠菜春卷 | 部分覆盖 |
| **夏** | **5–8 月** | **小龙虾、莲蓬、莲子、菱角、丝瓜、苋菜** | 小龙虾系列（已有 14 款）、豆米烧丝瓜（已有）、莲子冰粉（已有）、**莲蓬/菱角待开发** | **主力覆盖** |
| 秋 | 9–11 月 | 螃蟹、藕、板栗、桂花、鳙鱼 | 洪湖藕系列（已有 4 款）、桂花醪糟（已有）、**螃蟹/板栗待开发** | 部分覆盖 |
| 冬 | 12–2 月 | 腊味、萝卜、白菜、鱼头火锅、羊肉 | 武当山笋炒腊肉（已有）、鱼头（已有）、**腊味拼盘/暖锅待开发** | 部分覆盖 |
| 节日 | — | 端午粽、中秋月饼、春节年菜 | 清水粽（已验证，17 天窗口） | 仅端午覆盖 |

🔑 **关键结论**

1. **夏季覆盖最厚（14 款小龙虾 SKU），秋冬覆盖最薄**。小龙虾退潮后（预计 8 月下旬起），菜单将失去 13–15% 的收入来源且无接棒产品。
2. **秋季螃蟹线完全空白**。湖北（洪湖、梁子湖）是重要的河蟹产区，与清水亭现有的「洪湖藕」品牌资产高度契合，是最自然的秋季接棒品类。
3. **建议建立季节性产品日历**：每季固定 3–5 款时令 SKU，上下架时间提前 30 天锁定，并纳入品项汇总的常规分析口径。
```


#### MD data behind `calendar` · briefing

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L1462–L1470
- genre: `briefing`
- note: 开业营销日历

```
## 6.8 开业营销日历

| 阶段 | 时间 | 动作 | 考核指标 |
|---|---|---|---|
| **口碑修复期** | 开业前 60–14 天 | 烤炉店评分修复 | 烤炉店评分 ≥4.2 |
| **预售期** | 开业前 14 天 | 点评套餐上线、内容预热（只讲 3 个卖点）、烤炉店预告物料 | 预售券核销率 ≥60% |
| **首周** | D1–D7 | 巴斯克赠送启动、明档内容集中产出、试吃车运营 | 日均客流、点评评分 |
| **首月** | D8–D30 | 套餐结构调优、外卖上线（D15 后，避免首周出餐压力） | 人均、连带率、评分 ≥4.4 |
| **三个月** | D31–D90 | 会员沉淀、菜单第二版上线、双店互通券 | 会员数、复购率、评分 ≥4.5 |
```


#### gold HTML 图 slide 198

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 198 / 296
- genre: `diagnosis`
- note: inline SVG omitted; copy geometry from gold file when designing the recipe

```
class: slide figslide
chips: 图 42 / 47 · 拾壹 · 季节性产品矩阵与产品生命周期
h2: 季节性产品日历：夏季覆盖最厚，秋冬接棒缺位
SOURCE: 现有 SKU 的时令属性 + 湖北时令食材谱系

SEASONAL PRODUCT GANTT 
图 42 / 47 · 拾壹 · 季节性产品矩阵与产品生命周期 

季节性产品日历：夏季覆盖最厚，秋冬接棒缺位

数据来源 / SOURCE 现有 SKU 的时令属性 + 湖北时令食材谱系 

[SVG omitted]

关键结论 / KEY INSIGHTS 小龙虾 14 个 SKU 撑起夏季， 8 月下旬退潮后无接棒品类；秋季螃蟹线完全空白，而洪湖、梁子湖是重要河蟹产区，与现有「洪湖藕」品牌资产天然契合。 

清水亭 · 产品结构诊断 · TIANSIGHT 198 / 296
```


---

## 9 Appendix E chart menu

### Original chart menu (清水亭 附录 E)

This table is the MECE viz shopping list from the diagnosis MD. Map each 图表类型 to one L3 viz id by FT question (aliases in taxonomy.md). Do not promote 附录 E names (小提琴、哑铃、三维气泡) to types.

#### 附录 E 可视化图表推荐总表

- source: `ref/清水亭_主辅佐引产品结构诊断报告 (4).md` · L2967–L3017
- genre: `diagnosis`

```
## 附录 E｜可视化图表推荐总表

| 章节 | 图表类型 | 用途 | 关键字段 |
|---|---|---|---|
| 0 | Sankey 数据资产地图 | 文件 → 字段 → 分析模块 | 文件名、字段、模块 |
| 0 | 漏斗图 | 370 → 243 → 118 | 处理步骤、行数 |
| 0 | 瀑布图 | 去重前后金额变化 | 去重项、金额 |
| 0 | 雷达图 | 数据完备度 12 维 | 维度、完备度% |
| 1 | 韦恩图 | 两套框架重合与差异 | 模块清单 |
| 1 | 架构图 | 13 模块四层级 | 模块、层级 |
| 2 | 气泡图 | 六店定位（桌数 × 桌均 × 收入） | 门店、日均桌、桌均、总额 |
| 2 | 直方图 + 累计曲线 | 人均消费分布 | 人均、桌数 |
| 3 | 四象限散点图 | 角色校验（渗透率 × 额量比） | 品项、渗透率、额量比、销售额 |
| 3 | 桑基图 | 角色错配（现角色 → 建议角色） | 品项、现角色、建议角色、销售额 |
| 4 | 帕累托双轴图 | ABC 贡献 + 累计曲线 | 品项、销售额、累计% |
| 4 | 韦恩图 | S1 / S2 / 交集 | 集合规模 |
| 4 | 斜率图 | 双口径排名变动 | 品项、标准排名、实收排名 |
| 4 | 双向条形图 | 系列折让率 | 系列、折让率 |
| 5 | 小提琴图 | 四指标分布 | 四个指标值 |
| 5 | 四象限散点图 | 高潜品识别（千单点击 × 毛利率） | 品项、千单点击、毛利率、销售额 |
| 5 | 哑铃图 | 大份 vs 例份对照 | 品项、规格、毛利率、千单点击 |
| 5 | 热力图 | 待下架条件命中 | 品项 × 4 条标准 |
| 6 | 树状图 Treemap | 菜单结构（面积 = 销售额） | 角色、系列、品项、销售额 |
| 6 | 雷达图 | 3-4-2-1 达标 | 四分类实际 vs 理想 |
| 6 | 横向条形图 | 系列效率指数 | 系列、效率指数 |
| 7 | 矩阵气泡图 | 品类倾向（渗透率 × 桌均贡献） | 系列、渗透率、桌均贡献、额占比 |
| 7 | 哑铃图 | 国贸 vs 五店品类渗透率 | 系列、两组渗透率 |
| 7 | 阶梯柱状图 | 价格带分布（空档标红） | 价格带、SKU 数、销售额 |
| 7 | 箱线图 | 各系列价格分布 | 系列、价格 |
| 8 | 阶梯图 | 主菜件数 × 桌均 | 主菜件数、桌均 |
| 8 | 堆叠柱 | 桌型 × 角色组合 | 桌型、四角色件数 |
| 8 | 网络图 | 连带关系（节点 = 品项） | 品项对、共现桌、提升度 |
| 8 | 哑铃图 | 火烧馍分店对照 | 门店、渗透率、带馍率 |
| 8 | 双轴图 | 24 小时桌数 + 桌均 | 小时、桌数、桌均 |
| 8 | 热力图 | 时段 × 品类 | 时段、系列、桌均贡献 |
| 8 | 矩阵散点 | 区域效率 | 门店、区域、日均桌、元/桌/小时 |
| 9 | 漏斗图 | 复购次数分布 | 次数、会员数 |
| 9 | 趋势线 | 月度会员活跃 | 月份、笔数、会员数 |
| 9 | 条形图 + 目标线 | 分店会员识别率 | 门店、识别率、30% 线 |
| 10 | 3×3 热力图 | 味型 × 工艺九宫格 | 味型组、工艺组、SKU、销售额 |
| 10 | 3×14 热力图 | 味型 × 食材 | 味型组、食材、SKU |
| 10 | 三维气泡 | 工艺-毛利率-销售额 | 工艺、毛利率、销售额、SKU |
| 11 | 折线图 | 小龙虾旬度占比 | 旬、占比 |
| 11 | 瀑布图 | 产品动能 TOP10 升降 | 品项、趋势% |
| 11 | 双轴时序图 | 藕汤替换事件 | 日期、日均件、日均实收 |
| 11 | 甘特图 | 季节性产品日历 | 产品、上架日、下架日 |
| 11 | 气泡图 | 生命周期五阶段 | 品项、渗透率、动能、销售额 |
| 12 | 散点图 | 商圈定位 | 商圈人均、本店人均、月流水 |
| 12 | 堆叠对比图 | 竞品价格带 | 品牌、价格带、SKU 占比 |
| 13 | 优先级矩阵 | 行动清单 | 行动、难度、效益 |
| 13 | 瀑布图 | 效益汇总 | 行动、增量、累计 |
```


---

## 10 Folded types and empties

### Coverage gaps

These surfaces exist in the corpus. They are **not** L2 jobs. Original cuts live here so templates do not invent a 13th type.

### In corpus, folded (do not add L2)

| Surface | Where original lives | Fold into |
|---|---|---|
| quote | 苏帮袁 / 07 blockquotes | `statement` |
| question | 08 Q1–Q3; 06 未解问题 | `verdict` or `statement` |
| timeline | 07 S0–S7; 06 开业日历 | `compare` |
| diagram | 侍天依赖层级; 07 Playing to Win | `compare` + `treemap`/`network` |
| playbook stage card | 07 §8.1–8.8 | `compare` |
| brand profile | 08 C1–C5 | `compare` |
| retired table fills (`sum-roster` `kpi-cards` `state-matrix` `dual-calibre` `profile-card` `falsify-quad`) | were L3 ids | matching L2 job; see `fill-table/README.md` |

#### quote · 苏帮袁 东亚风味分子

- source: `ref/苏帮袁_菜单分析维度体系_第一性原理.md` · L29–L29
- genre: `system`
- note: fold into statement

```
> **对苏帮袁尤其关键的一条**：该研究发现，西方菜系倾向于搭配「共享风味分子」的食材，而**东亚菜系恰恰相反——刻意回避共享分子、靠对比取胜**。苏帮菜属东亚体系，意味着你的「食材×味型」搭配逻辑应按**对比/互补**而非「同类相配」来评估，这直接影响研发矩阵怎么读。
```


#### quote · 07 Stage Gate 必要性

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1614–L1618
- genre: `roadmap`
- note: fold into statement

```
**为什么这个机制值得单列一章：**

> <cite index="4-1">近六成新门店经营不满两年即退出</cite>。
> **一个不设闸门的扩张计划，在统计上等于一个 60% 概率的失败计划。**
> **Stage Gate 是把这个概率降下来的唯一结构性手段。**
```


#### question · 08 三个开放问题

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L1023–L1029
- genre: `dossier`
- note: fold into verdict

```
## 7.3 三个需要用数据回答的开放问题

| 问题 | 现有证据 | 判据 | 何时有答案 |
|---|---|---|---|
| **Q1：58–62 元 还是 72–78 元？** | 55–65 带只有必胜客一家有规模（283）；65–80 带有 4 个品牌评分 4.5+（Wagas 53 / Tubestation 29 / BAKER&SPICE 28 / 比格 84） | 首店 D90 人均实际落点 + 差评中"贵"的占比 | 首店 +90 天 |
| **Q2：披萨能否作为规模载体？** | Tubestation 29 家 × 78 元 × 4.63 分（正面证据）；必胜客 283 家（正面证据） | D60 披萨订单渗透率 ≥25% | 首店 +60 天 |
| **Q3：烘焙能否成为第二曲线？** | BAKER&SPICE 28 家 × 75 元 × 4.56 分（唯一规模样本）；北京无"烘焙×汉堡"成功先例 | 堡胚零售订单渗透率 ≥8% + 烤炉店评分修复至 ≥4.2 | 首店 +90 天 |
```


#### question · 06 未解问题

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L2093–L2109
- genre: `briefing`
- note: fold into verdict

```
# 第十二部分 · 未解问题与二期路线

## 12.1 本次仍未能回答的问题

| 问题 | 需要什么 | 何时有答案 | 优先级 |
|---|---|---|---|
| 真实连带率与订单渗透率 | 订单级小票数据 | 开业 +15 天 | 🔴 |
| 实际人均落点 | 小票数据 | 开业 +15 天 | 🔴 |
| 高峰出餐能力上限 | 开业前压测 | **开业前** | 🔴 |
| 窑炉物业可行性 | 物业硬件确认函 | **本周** | 🔴 |
| 毛利率是否含包材损耗 | 客户确认 | **8.15** | 🔴 |
| 北京消费者对国风融合汉堡的接受度 | 上市后销量 | 开业 +15 天 | 🟡 |
| 披萨能否承担规模载体 | 披萨订单渗透率 | 开业 +60 天 | 🔴 |
| 烤炉店客群与汉堡店的重叠度 | 双店互通券核销 | 开业 +30 天 | 🟡 |
| 外卖真实占比与品质衰减 | 平台数据 + 差评归因 | 开业 +30 天 | 🟡 |
| 跨省供应链稳定性 | 供货方案 + 到货记录 | 开业 +30 天 | 🟡 |
| 二店选址最终确认 | 首店模型验证 + 物业 | 开业 +90 天 | 🟡 |
```


#### timeline · 06 开业营销日历

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L1462–L1470
- genre: `briefing`
- note: fold into compare

```
## 6.8 开业营销日历

| 阶段 | 时间 | 动作 | 考核指标 |
|---|---|---|---|
| **口碑修复期** | 开业前 60–14 天 | 烤炉店评分修复 | 烤炉店评分 ≥4.2 |
| **预售期** | 开业前 14 天 | 点评套餐上线、内容预热（只讲 3 个卖点）、烤炉店预告物料 | 预售券核销率 ≥60% |
| **首周** | D1–D7 | 巴斯克赠送启动、明档内容集中产出、试吃车运营 | 日均客流、点评评分 |
| **首月** | D8–D30 | 套餐结构调优、外卖上线（D15 后，避免首周出餐压力） | 人均、连带率、评分 ≥4.4 |
| **三个月** | D31–D90 | 会员沉淀、菜单第二版上线、双店互通券 | 会员数、复购率、评分 ≥4.5 |
```


#### timeline · 07 二期服务路线

- source: `ref/06_首版汇报报告_V1.0_数据校准版.md` · L2111–L2120
- genre: `briefing`
- note: fold into compare

```
## 12.2 二期服务路线

| 阶段 | 时间 | 核心动作 | 交付 |
|---|---|---|---|
| **开业前** | −14 至 0 天 | 出餐压测、口味盲测、价格敏感度测试 | 开业前测试报告 |
| 开业期 | D1–D15 | 数据回传跑通、首轮观察、A/B R1 | 15 天复盘报告 |
| 优化期 | D16–D60 | 红绿灯执行、A/B R2–R6、菜单删减 | 第二版菜单 + AB 测试报告 |
| **判定期** | D60 | **披萨渗透率判定（H3）** | 战略路径确认书 |
| 沉淀期 | D60–D90 | 单店模型固化、看板 V2 | 单店模型手册 |
| 复制期 | D90+ | 二店筹备、三大体系跑通 | 二店方案 + 系统 V2 |
```


#### diagram · 侍天依赖层级

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L1107–L1131
- genre: `system`
- note: fold into compare + treemap/network

```
## 6.1 依赖层级

```
L0 地基 ── A01 资产盘点 → A02 三路对账 → A03 质量检测
                 ├─→ 口径 A（索引表）
                 └─→ 口径 B（账单明细）
                          │
L1 基础指标 ── A10 ABC ─ A13 额量比 ─ A14 千单点击 ─ A15 毛利率 ─ A16 渗透率
                 │           └────────┬──────────────┘             │
L2 合成分析 ── A11 四分类              ▼                            │
                 │            A17 四象限 → A18 待下架 → A19 高潜品   │
                 ├─→ A20 结构树 ← A07 角色校验 ←────────────────────┤
                 ├─→ A21 3-4-2-1 ─ A22 效率指数 ─→ A23 目标结构     │
                 └─→ A49 生命周期 ← A48 动能榜 ← A45 季节走势 ←─────┤
                                                                    │
L3 行为分析 ── A28 角色组合 → A29 主菜杠杆 → A30 点单公式            │
               A31 连带 ─ A32 时段 ─ A33 星期 ─ A34 区域 ─ A35 外卖 ─┤
               A39 识别率 → A36 复购 → A37 间隔 → A38 会员价值 → A40 │
                                                                    │
L4 属性分析 ── A41 味型×工艺 ─ A42 味型×食材 ─ A43 工艺毛利 → A44 补漏
                                                                    │
L5 外部对照 ── A51 商圈 ─ A52/A53 竞品 ─ A54 榜单 ─ A55 客单反证 ───┤
                                                                    ▼
L6 收敛 ─────────────── A56 优先级矩阵 → A57 效益测算 → A58 结论审查
```
```


#### diagram · 维度扩展收益递减

- source: `ref/侍天TIANSIGHT_分析体系Part1.md` · L49–L59
- genre: `system`
- note: fold into compare

```
### 维度扩展的收益递减顺序

```
当前 6 族 ─── 可回答「卖什么、卖得怎样」
  + D7 成本  ─── 可回答「赚不赚钱」          ← 收益最大，且已证明必要
  + D9 座位  ─── 可回答「资产用得好不好」
  + D8 产能  ─── 可回答「后厨撑不撑得住」
  + D10 人员 ─── 可回答「谁在创造差异」
  + D13 口碑 ─── 可回答「客人为什么不回来」
  + D14 竞争 ─── 可回答「在市场上处于什么位置」
```
```


#### playbook · S0 阶段卡

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1048–L1108
- genre: `roadmap`
- note: fold into compare; also in job/compare.md

```
## 8.1 S0 · 开业前 90 天：把不可逆的事做对

### 阶段命题
> **开业前能改的东西，开业后大多改不了。这 90 天的价值高于之后的 12 个月。**

### 不可逆事项清单（按不可逆程度排序）

| 事项 | 不可逆程度 | 现状 | 截止 |
|---|---|---|---|
| **后厨布局与明档落位** | 🔴🔴🔴 极高（拆改成本巨大） | 施工图未落实烘焙展示区与窑炉 | 施工前 |
| **品牌名与主视觉** | 🔴🔴🔴 | 已定 | — |
| **英文口号与包材文案** | 🔴🔴 印刷后不可逆 | 手册内部有两套英文口号 | 出图前 |
| **物业硬件（电容/排烟/明火）** | 🔴🔴🔴 | 未确认 | 签约前 |
| 菜单结构 | 🔴 可改但成本高 | 已给建议 | 8.15 |
| 定价 | 🟡 可改（涨价难，降价易） | 已给建议 | 8.15 |
| POS 与数据字典 | 🔴 后补极痛苦 | 待建 | 开业前 |

### 关键动作（按问题域）

**D2 产品与菜单**
- 菜单收敛至 28 款（食品 20 + 饮品 8）
- 补三款：小份经典堡 26、基础披萨 38–42、堡胚零售
- 冻结沙拉研发管线 7 款
- 完成 39 款产品的标准配方卡（克重、SOP、出品标准图）

**D3 单店经济模型**
- 🔴 **澄清毛利率口径**（是否含包材与损耗）
- 建立完整 UE 模型：投资额、月度 P&L、坪效人效、回本进度、现金流五张表
- 设定盈亏平衡点：日均客次 ×、日均营业额 ×

**D4 运营效率**
- 🔴 **出餐压测**：60 分钟 80 单，8 分钟出餐率 ≥85%，无单超 15 分钟
- SOP 验收：新员工照 SOP 独立操作合格率 ≥90%
- TOC 首轮瓶颈识别与配置调整

**D1 品牌心智**
- 统一英文口号为 BURGER, DONE RIGHT.
- 修正 RTB 表述（"米其林三星厨房出身 · 前 GUCCI 1921 上海行政总厨"）
- 🔴 **第一信任状从"现烤堡胚"迁移至"现绞原切牛肉"**（§6.1）
- 门头副标定为「现绞 · 现烤 · 现煎」

**D5 增长**
- 烤炉店口碑修复启动（目标 3.9 → 4.2）
- 三平台建档：点评、抖音、外卖（外卖 D15 后上线）
- 5 个套餐上线，含 39 元入门套餐

**数据基础**
- 🔴 **数据字典定稿**
- POS 配置：确保能导出订单级明细
- 看板 V1 模板就位

### 我方赋能交付物
菜单结构定稿 · 定价方案 · 五套餐设计 · 数据字典 · 看板 V1 · 出餐压测方案与执行 · 口味盲测报告 · 明档落位建议 · 品牌话语体系修订 · 开业营销日历

### 典型死法
- 后厨按"什么都能做"设计，开业后发现出餐慢，且改不了
- 包材已印，发现口号有错别字
- 开业后才发现 POS 导不出订单级明细，第一个月数据全废

### 进入 S1 的准入条件
✅ 压测达标　✅ 数据字典定稿　✅ 菜单定稿　✅ SOP 验收通过　✅ 明档三件事落位
```


#### playbook · S1 Gate

- source: `ref/07_战略方法论体系与分阶段赋能路线图_M1.0.md` · L1112–L1162
- genre: `roadmap`
- note: fold into compare

```
## 8.2 S1 · 第 1 家店（0–6 月）：模型成不成立

### 阶段命题
> **首店不是第一家店，是整个决策系统的第一个数据源。**
> **这 6 个月要产出的不是利润，是四个可信的数字：人均、连带率、复购率、回本期。**

### 组织形态
创始人 + 店长 + 厨师长 + 我方数据支持。**管理半径 = 1，创始人可以且应该亲力亲为。**

### 必须回答的四个问题（首店报告 §4.1 的四个未知）
1. 甜品订单渗透率？　2. 小吃订单渗透率？　3. 汉堡与披萨互斥还是共现？　4. 单客平均点几个 SKU？

### 关键动作时间轴

| 时点 | 动作 | 产出 |
|---|---|---|
| **D1** | 数据回传机制启动 | 日报开始 |
| D1–D7 | 巴斯克赠送、明档内容集中产出、试吃车 | 首周口碑 |
| **D7** | 出餐效率首轮复盘 | 瓶颈识别 |
| **D15** | 🔴 **首轮数据回测** | 四个问题的答案 + 红绿灯首批名单 |
| D15–D21 | A/B R1（加购文案） | 连带率优化 |
| D15 | 外卖上线 | 渠道验证 |
| D22–D56 | A/B R2–R6 | 套餐顺序、出餐告知、入口款定价、披萨版位、明档引导 |
| **D30** | 🔴 **H1/H2/H4 假设判定** | 人均、汉堡渗透率、明档有效性 |
| **D60** | 🔴 **H3 判定：披萨渗透率 ≥25%？** | **双载体路径确认 = 二店要不要装窑炉** |
| D60 | 第二版菜单上线（删减 1/3） | 菜单 V2 |
| **D90** | 🔴 **单店模型初版固化** | UE 实测值 |
| D90–D180 | 稳定运营、复购队列观察 | 队列曲线 |
| **D180** | **S1→S2 Gate 评审** | 开不开二店 |

### 六个问题域的工作重心

| 域 | 权重 | 核心工作 |
|---|---|---|
| D1 心智 | ★★★★★ | 显著性建设：让人知道、记得住。**不做价值观营销** |
| D2 产品 | ★★★★★ | 菜单工程矩阵首轮跑通，D60 砍 1/3 |
| D3 模型 | ★★★★★ | UE 五张表实测填充 |
| D4 运营 | ★★★★ | TOC 瓶颈迭代，8 分钟出餐率爬坡 |
| D5 增长 | ★★★ | 评分 ≥4.5、会员沉淀、烤炉导流 |
| D6 组织 | ★ | 只做一件事：**记录，为将来的手册攒素材** |

### 我方赋能交付物
15 天复盘报告 · 菜单 V2 · 六轮 A/B 测试报告 · 单店模型手册 V1 · 队列分析首版 · 差评归因月报 · S1→S2 Gate 评审报告

### 典型死法
- **出餐慢 → 差评 → 评分卡在 4.2 → 流量阀门打不开**（§2.5 已证明 4.4 分是流量台阶）
- 数据没回传，6 个月后仍不知道连带率
- 创始人偏好款舍不得砍，菜单一直是 58 款
- 靠团购冲客流，人均掉到 45 元，模型失真

### S1→S2 Gate（不达标不开二店）
```


#### brand profile · Wagas C1

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L373–L405
- genre: `dossier`
- note: fold into compare

```
### 🥇 C1 · Wagas 沃歌斯 —— "品质西式简餐能开多大"的天花板样本

| 指标 | 数值 |
|---|---|
| **北京门店** | **53 家**（归一化后；未归一化会误计为 47） |
| 人均中位 | **78 元**（区间 67–88） |
| 平均评分 | **4.50** |
| ≥4.5 分门店占比 | **62%** |
| 客单变异 CV | **5.6%**（极稳定） |
| 评分标准差 | 0.20 |
| 单店评论中位 | **1,619** |
| 评论总量 | 95,244 |
| 覆盖 | 9 个行政区 / 43 个商圈 |
| 空间形态 | **商场 15 家 vs 非商场 38 家** |

**门店分布：** 朝阳 18、海淀 10、东城 6、西城 6、大兴 5、昌平 3、丰台 3、石景山 1

**TOP 门店：** 来福士（78/4.6/5,338）、国瑞城（84/4.7/4,742）、富力广场双井（82/4.6/4,211）、五道口购物中心（78/4.2/3,878）、君太百货（79/4.7/3,413）

#### ✅ 该学什么

| 学什么 | 具体 |
|---|---|
| **写字楼底商模型** | 38/53 家不在商场。工作日午餐刚需 > 周末逛街偶发 |
| **客单一致性** | CV 5.6%——53 家店人均全部落在 67–88 元，说明产品结构与套餐设计高度标准化 |
| **全时段结构** | 早餐/午餐/下午茶/晚餐都有产品，摊薄租金 |
| **"健康"作为品类词而非形容词** | Wagas 把"健康"做成了品类（沙拉碗、三明治、意面），不是贴在汉堡上的标签 |
| **单店评论 1,619 的量级** | 这是"品质连锁"单店客流的合理基准，建议作为石头先生 12 个月目标 |

#### ❌ 不该学什么

- **不要学它的品类结构。** Wagas 的核心是沙拉/意面/三明治，与"汉堡"心智相冲突（且北京"轻食沙拉"品类评分仅 3.60）
- **不要学它 78 元的定价。** 它靠的是全时段与轻食心智，不是单一重餐
```


#### brand profile · 魏斯理 5.1

- source: `ref/08_北京西式快餐可参考品牌分析专项_B1.0.md` · L834–L889
- genre: `dossier`
- note: fold into compare

```
## 5.1 🥇 魏斯理汉堡（Wesley Burger）—— **全国范围内与石头先生相似度最高的品牌**

### 为什么它是第一参照对象

**在北京点评库 6,052 家西式门店中，检索"魏斯理 / 魏斯 / Wesley"：0 家。**
**它还没进北京。但它已经在做石头先生想做的事，而且做到了 80+ 家店。**

### 基本档案

| 维度 | 数据 |
|---|---|
| 归属 | 陕西魏家餐饮集团（魏家凉皮母公司）旗下西式快餐品牌 |
| 创立 | <cite index="55-1">品牌诞生于 2018 年，首店 2019 年在西安开业</cite> |
| 定位 | <cite index="49-1">以美式汉堡为主打，搭配七款披萨、三款沙拉、三款意面、小食、饮品；关注食材，坚持高端餐饮标准</cite> |
| **人均** | **约 40 元** |
| **门店数** | <cite index="52-1">品牌目前已进入全国十五个省市，开出超八十家直营门店，全年拓店计划剑指百家规模</cite> |
| **模式** | <cite index="52-1">全直营运营、重资产投建供应链、单店配置 70 余名员工、始终保持稳健拓店节奏</cite> |
| **店型** | <cite index="55-1">采用"重人工、大店面"的直营模式，单店面积通常在 240–500 平方米</cite> |
| 扩张节奏 | <cite index="51-1">2023 年 12 月开始加快开店，以平均每月新开一家的速度在西安及咸阳等城市加密；2024 年 9 月在合肥开出省外首店，同年相继进入太原、郑州</cite> |
| 稀缺性策略 | <cite index="47-1">不少省外城市的门店数保持在 1–2 家，通过强体验、新鲜感、高势能吸引客流，同时也能支撑起相对更重的运营模式</cite> |

### 🔴 最关键的一条：它的堡胚方案

<cite index="52-1">多数连锁品牌选择外采标准化面包胚，魏斯理选择自建加工基地。2026 年 1 月，品牌位于陕西杨凌的全国首座汉堡加工基地正式投产，引进美国 AMF 全自动烘焙生产线，日产能十万个汉堡胚，满产可达二十万个。面团在中央厨房统一完成发酵与成型，以冷冻形态配送到全国门店，门店仅需完成最后烘烤环节。每一只汉堡胚的含水量、气孔密度、表皮酥脆度，在出厂环节便完成标准化锁定</cite>。

> **这正是我方在《战略方法论报告》§8.6 中提出的建议方案：中央工厂做面团与预处理，门店做最后烘烤。**
>
> **魏斯理已经把它做出来了，而且是全国第一座专用汉堡胚加工基地。**
>
> **这条信息的价值有两面：**
> - ✅ **验证了路线的正确性**——石头先生不必再论证"该不该这样做"
> - 🔴 **也说明窗口在收窄**——对方已经把"现烤堡胚"从门店手艺变成了工业化能力

### 与石头先生的逐项对照

| 维度 | 魏斯理汉堡 | 石头先生的汉堡 | 判断 |
|---|---|---|---|
| 母体资产 | 魏家凉皮（<cite index="53-1">魏家旗下品牌门店数一共 500+ 家</cite>）+ 中央厨房 + 冷链 | 十余年精品烘焙 + 合生汇烤炉旗舰店 | 🟡 对方母体更大 |
| **核心工艺卖点** | **现制现做 + 自建堡胚基地** | **现绞现烤现煎** | 🔴 **高度重叠** |
| **产品结构** | 汉堡 + 7 披萨 + 3 沙拉 + 3 意面 + 小食饮品 | 汉堡 + 披萨 + 意面 + 沙拉 + 小食 + 甜品 + 饮品 | 🔴 **几乎完全一致** |
| **人均** | **约 40 元** | 目标 58–62 元 | 🔴 **我们高 45–55%** |
| 单店面积 | 240–500㎡ | 首店约 206㎡ | 🟡 对方更大 |
| 单店人员 | 70 余人 | 首店测算高峰 14–19 人 | ⚠️ 口径可能不同（对方或含全部班次） |
| 扩张模式 | 全直营 | 待定 | — |
| 城市策略 | 省外每城 1–2 家，稀缺性拉排队 | 待定 | 🟢 可借鉴 |
| 已知问题 | <cite index="55-1">2026 年 1 月山东首店因出餐慢、仅支持人工点餐引发讨论，品牌回应称因后厨压力过大；2026 年 6 月杭州门店发生食安投诉，正配合市监部门调查</cite> | — | 🔴 **前车之鉴** |

### ✅ 该学的五件事

1. **中央工厂做面团、门店做最后烘烤**——这是"现烤"与"可复制"之间唯一的可行解
2. **稀缺性开店节奏**——省外每城 1–2 家，用排队制造势能，同时支撑重运营
3. **全直营**——在模型未完全稳定前不开放加盟
4. **重资产投供应链**——把钱花在看不见的地方，而不是装修
5. **完整正餐结构**（汉堡+披萨+意面+沙拉）验证了石头先生的多品类假设可行

### 🔴 该警惕的三件事
```



### Not in this MD corpus (keep for Guizang only)

No `![](image)` in any of the 7 ref files. Do not design diagnosis templates around these until a deck with photos exists:

- `text-image`
- `image-grid`
- `image-hero`

### Gold HTML vs six-element spec

Original gold pages usually have SOURCE + KEY INSIGHTS, not HOW TO READ / TAKEAWAY bars. Template design must add those slots even though the 296-page file mostly omits them.

#### gold chrome without HOW TO READ · 图01

- source: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` · slide 10
- genre: `diagnosis`
- note: template still reserves HOW TO READ + TAKEAWAY

```
class: slide figslide
chips: 图 01 / 47 · 零 · 数据地图、口径定义与数据质量
h2: 数据资产地图： 12 个文件如何支撑 13 个分析模块
SOURCE: /mnt/user-data/uploads 全部 12

DATA ASSET SANKEY 
图 01 / 47 · 零 · 数据地图、口径定义与数据质量 

数据资产地图： 12 个文件如何支撑 13 个分析模块

数据来源 / SOURCE /mnt/user-data/uploads 全部 12 个文件 · 字段清单 vs 模块输入需求 

[SVG omitted]

关键结论 / KEY INSIGHTS 品项汇总新版一份文件独立支撑 6 个模块；账单明细 6 店合计 159,086 行支撑 5 个模块；会员消费仅够支撑复购一个模块，且识别率只有 3.99% 。 

清水亭 · 产品结构诊断 · TIANSIGHT 10 / 296
```


---

## 11 Do not

- Hand the cheap model the raw 17 workshop ids as a menu
- Add a 13th L2 job (`playbook` `profile` `timeline` `quote` `question` fold into existing jobs)
- Add a parallel L3 table taxonomy (`sum-roster` `kpi-cards` `state-matrix` `dual-calibre` `profile-card` `falsify-quad` are L2 jobs)
- Reuse 07 data-source L0–L5 or 08 brand-filter L1–L3 as slide layers
- Invent viz ids; use the 16 + aliases grouped by FT question
- Emit empty competitor figures
- Mix Inter / purple / Guizang `h-hero` into TIANSIGHT
- Keep workshop chrome (`#baslide-chrome`) in the slide
- Drop SOURCE / denom on `续` pages
- Hide n-below-threshold cells; hatch them

---

*Generated by `skills/mdpages2htmlslides/scripts/extract-samples.py`. Do not rewrite the fenced originals.*
