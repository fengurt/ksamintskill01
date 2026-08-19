# Loop · 对照 (`compare`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `compare`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
因此：左已验证，右未复制 / 旧 vs 新

Use when: 门店对照、方案对照、前后
Avoid when: 两列没有共同量纲
Slots: left · therefore · right
Skins: TIANSIGHT, magazine, swiss, tableai

## Constraint
左右同量纲，中间「因此」。禁止两列各说各话。TIANSIGHT 用 viz-duo 箭头。data-page-type=compare。

## Must
- Set `data-page-type="compare"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] shared unit
- [ ] therefore connector
- [ ] two columns only
- [ ] one decision
- [ ] data-page-type=compare
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
