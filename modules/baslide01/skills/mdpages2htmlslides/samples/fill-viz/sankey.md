# L3 viz `sankey`

- FT question: `flow`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 10, 47
- samples: 3

### MD data behind `sankey` · diagnosis

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


### gold HTML 图 slide 10

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


### gold HTML 图 slide 47

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
