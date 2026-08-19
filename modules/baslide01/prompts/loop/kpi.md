# Loop · 指标卡 (`kpi`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `kpi`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
3–6 个大数，先定基本盘

Use when: 开场数据、经营基本盘、KPI tower
Avoid when: 超过 8 个数还想一眼读完
Slots: value · label · delta
Skins: TIANSIGHT, magazine, swiss, tableai

## Constraint
3–6 张卡，一卡一指标。大数等宽字体，label 小，delta 有方向。禁止 8+ 卡、禁止仪表盘环形图。TIANSIGHT 要 SOURCE/TAKEAWAY。data-page-type=kpi。

## Must
- Set `data-page-type="kpi"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] 3–6 cards
- [ ] tabular numerals
- [ ] delta direction
- [ ] no gauges
- [ ] data-page-type=kpi
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
