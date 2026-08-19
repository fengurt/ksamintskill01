# Page file format

`pages/p-0031.md` — frontmatter is the contract, the body is for humans.

```markdown
---
id: p-0031
template: chart-table
layout: fig-rail            # optional; defaults to the type's layout
pack: mid                   # air | mid | tight
outline_path: ["卷三｜盈利模型诊断", "3.2 竞争分析", "3.2.2 竞对方法论范式"]
units: [u-0087, u-0088, u-0089, u-0091]
overflow_of: null
source: "competitor_menu.jsonl · 商场粤菜类工作表 · 9 品类"
takeaway: "竞对倾向指数靠拍脑袋，韵有 90,038 条记录可以算准"
visualization: diverging-bar
provenance:
  source: "competitor_menu.jsonl · 商场粤菜类工作表 · 9 品类"
  how_to_read: "倾向指数 = 一桌客人点该品类的份数期望；主单乐观，次单保守"
  unit: "元 / 桌"
content:
  blocks:
    - kind: fig
      viz: diverging-bar
      data:
        x: [粥档, 招牌必点, 经典粤菜, 大厨小炒, 烧腊凉菜]
        主单: [44.50, 103.20, 19.60, 13.20, 34.40]
        次单: [39.50, 31.20, 15.60, 23.60, 39.20]
      caption: "主单 vs 次单贡献"
    - kind: table
      columns: [品类, 定位, 倾向指数, 平均定价]
      rows:
        - [粥档, 君, 0.5, 83.55]
        - [招牌必点, 臣, 0.8, 70.27]
      sum: [合计, "—", 3.9, "—"]
---

竞对底稿把「模拟餐单点餐测试」变成可计算模型……
（正文仅供人工审阅，下游从不解析）
```

## Three rules that prevent most downstream damage

**Slot values are plain text.** No `**bold**`, no backticks, no `#`, no
`[link](url)`. Emphasis is the renderer's job through block semantics. Both
gates fail on markdown found in a slot — `MD_IN_SLOT` before render,
`MD_LEAK` after.

**`claim` is not the title.** The title says what the page is about; the claim
says what to do about it. If they are the same string, the gate fires
`TITLE_ECHO` and the page reads as a document heading with filler under it.

**`units` is exhaustive and exclusive.** Every source unit appears on exactly
one page. This is what makes `gate_fidelity.py` meaningful and what lets a
reviewer trace any number on any slide back to its origin.
