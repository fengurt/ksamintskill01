# Loop · 左文右图 (`text-image`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `text-image`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
叙述配一张主图，图对齐正文不齐标题

Use when: 案例、现场、产品说明
Avoid when: 图是无信息的装饰底图
Slots: kicker · title · body · figure
Skins: magazine, atelier

## Constraint
左文右图。图对齐正文首行，不要和超大标题齐顶。标准比例 16:10 或 4:3。图必须有信息。data-page-type=text-image。

## Must
- Set `data-page-type="text-image"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] split layout
- [ ] figure aligns to body
- [ ] standard aspect ratio
- [ ] image carries information
- [ ] data-page-type=text-image
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
