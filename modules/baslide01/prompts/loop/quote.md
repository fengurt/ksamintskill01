# Loop · 金句 (`quote`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `quote`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
别人的话或自己的一句，慢下来

Use when: 创始人、客户、原则原文
Avoid when: 堆三条以上引用
Slots: quote · source
Skins: magazine, swiss, tableai

## Constraint
一句引用，慢下来。引号或衬线大字，来源右下。禁止三条金句墙。data-page-type=quote。

## Must
- Set `data-page-type="quote"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] single quote
- [ ] source present
- [ ] no quote wall
- [ ] generous whitespace
- [ ] data-page-type=quote
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
