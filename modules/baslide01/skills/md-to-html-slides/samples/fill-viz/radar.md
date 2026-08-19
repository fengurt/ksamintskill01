# L3 viz `radar`

- FT question: `correlation`
- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)
- gold slides: 20, 105
- samples: 4

### MD data behind `radar` · diagnosis

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


### MD data behind `radar` · briefing

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


### gold HTML 图 slide 20

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


### gold HTML 图 slide 105

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
