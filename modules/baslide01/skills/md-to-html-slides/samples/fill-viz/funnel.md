# L3 viz `funnel`

- FT question: `part-to-whole`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 13, 164
- samples: 4

### MD data behind `funnel` · diagnosis

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


### MD data behind `funnel` · system

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


### gold HTML 图 slide 13

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


### gold HTML 图 slide 164

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
