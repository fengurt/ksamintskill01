# Loop · 主张页 (`statement`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `statement`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
一个判断，带够依据

Use when: 方法论一句、原则、why now
Avoid when: 需要图表才能成立的结论；短导语后面紧跟表格（导语并进表页）
Slots: statement · supporting line
Skins: magazine, swiss, tableai

## Constraint
一个判断，依据装到同一页直到约 280 字。3–6 条列表留在本页；7 条以上改 roster。页眉一行：logo + chip。主句用 `.sd-quote` 占满纸色井。1 条依据用 `.sd-lede` 井；2–4 条用对等纸色卡（编号 + `.sd-lede`），禁止「序 / 01 / 02」瘦表漂在下沿。5 条以上才用 `.sd-table` 并拉满剩余高度。辅句必须整句完整；超出分页（续），禁止截断、禁止画布省略号、禁止只剩一行的孤儿页、禁止大片空白。短页 `data-pack=air`（quote 4.8%），密页 `data-pack=tight`。禁止图。data-page-type=statement。

## Must
- Set `data-page-type="statement"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] one claim only
- [ ] supporting lines are complete sentences (paginate if over budget)
- [ ] no `…` / `...` on the canvas
- [ ] no 孤儿字 / 孤儿行
- [ ] `.sd-quote` fills a paper well; 2–4 依据 are peer cards, not a skinny 序 table
- [ ] no orphan leftover page
- [ ] field is not mostly empty; `data-pack` matches copy
- [ ] no charts
- [ ] data-page-type=statement
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
