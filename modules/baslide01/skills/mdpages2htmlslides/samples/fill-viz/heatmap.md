# L3 viz `heatmap`

- FT question: `distribution`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 93, 151, 174, 184
- samples: 6

### MD data behind `heatmap` · diagnosis

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


### MD data behind `heatmap` · briefing

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


### gold HTML 图 slide 93

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


### gold HTML 图 slide 151

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


### gold HTML 图 slide 174

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


### gold HTML 图 slide 184

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
