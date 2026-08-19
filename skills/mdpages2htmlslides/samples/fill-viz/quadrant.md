# L3 viz `quadrant`

- FT question: `correlation`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 42, 83, 230
- samples: 5

### MD data behind `quadrant` · diagnosis

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


### MD data behind `quadrant` · briefing

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


### gold HTML 图 slide 42

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


### gold HTML 图 slide 83

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


### gold HTML 图 slide 230

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
