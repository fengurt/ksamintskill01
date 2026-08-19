# Loop · 图片网格 (`image-grid`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `image-grid`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
多图同高同比例对比

Use when: 证据墙、场景组、截图组
Avoid when: 比例混用、高度不齐
Slots: uniform frames · captions
Skins: magazine, swiss, tableai

## Constraint
多图同高同比例，每格一句 caption。禁止混用高度类。2×2 或 3×2。data-page-type=image-grid。

## Must
- Set `data-page-type="image-grid"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] uniform height
- [ ] uniform ratio
- [ ] captions
- [ ] 2×2 or 3×2
- [ ] data-page-type=image-grid
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
