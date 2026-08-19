# Loop · 主视觉 (`image-hero`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `image-hero`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
一张图定场，文字让路

Use when: 封面辅页、现场、21:9 情景
Avoid when: 图上叠满字
Slots: hero image · title block · optional kpi row
Skins: swiss, tableai, atelier

## Constraint
一张图定场，文字让路。标题块最多两行，禁止图上叠满字。data-page-type=image-hero。

## Must
- Set `data-page-type="image-hero"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] one hero image
- [ ] title ≤2 lines
- [ ] no text wallpaper
- [ ] optional kpi row only
- [ ] data-page-type=image-hero
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
