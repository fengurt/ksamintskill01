# Loop · 过程 / 时间 (`timeline`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `timeline`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
步骤或时间轴，一步不能跳

Use when: 流水线、分期建设、动能周序
Avoid when: 步骤其实是并列分类
Slots: steps or ticks · current state
Skins: magazine, swiss, tableai

## Constraint
步骤有先后，标出当前态。禁止把并列分类画成时间轴。4–7 步为宜。data-page-type=timeline。

## Must
- Set `data-page-type="timeline"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] ordered steps
- [ ] current state marked
- [ ] not a disguised taxonomy
- [ ] 4–7 steps
- [ ] data-page-type=timeline
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
