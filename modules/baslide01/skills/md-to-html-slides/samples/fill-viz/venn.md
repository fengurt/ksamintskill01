# L3 viz `venn`

- FT question: `part-to-whole`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 26, 63
- samples: 3

### MD data behind `venn` · diagnosis

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


### gold HTML 图 slide 26

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


### gold HTML 图 slide 63

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
