# L3 viz `diverging-bar`

- FT question: `deviation`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 72, 84, 121
- samples: 4

### MD data behind `diverging-bar` · diagnosis

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


### gold HTML 图 slide 72

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


### gold HTML 图 slide 84

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


### gold HTML 图 slide 121

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
