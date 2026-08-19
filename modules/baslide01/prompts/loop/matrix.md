# Loop · 矩阵 (`matrix`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `matrix`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
格子里看出结构：解锁、九宫、ABC 迁移

Use when: 二维交叉、零值≠缺口、命中组合
Avoid when: 行列没有判读纪律
Slots: rows · cols · cell state · footnote
Skins: TIANSIGHT, swiss, tableai

## Constraint
格子即结构。行列有判读纪律，零值≠缺口要脚注。TIANSIGHT 用 ready/degraded/blocked 三态，禁止彩虹热力。data-page-type=matrix。

## Must
- Set `data-page-type="matrix"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] row+col labels
- [ ] cell states readable
- [ ] zero≠gap footnote if needed
- [ ] no rainbow heatmap
- [ ] data-page-type=matrix
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
