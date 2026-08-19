# Loop · 图 + 名录 (`chart-table`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `chart-table`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
图给形状，表给可执行名单

Use when: 四象限 + SKU 表、空档 + 补位清单
Avoid when: 表不是全量、没有合计行
Slots: chart 58% · table 42% · sum-check · takeaway
Skins: TIANSIGHT

## Constraint
左图 58% 给形状，右表 42% 给可执行预览。表必须有合计行。共享一条 TAKEAWAY。data-page-type=chart-table。右表 ≤6 行是预览；全量细项在后页 roster 清单。气泡规则与 `chart` 相同。

## Must
- Set `data-page-type="chart-table"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] chart+table split
- [ ] sum-check row
- [ ] shared takeaway
- [ ] table is complete not TOP10
- [ ] data-page-type=chart-table
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
