# Loop · 关系图 (`diagram`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `diagram`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
系统、三力、分层，几何表达关系

Use when: 架构、作用力、循环
Avoid when: 用装饰图冒充结构
Slots: geometry · html labels · caption
Skins: swiss, tableai

## Constraint
几何表达关系，标签用 HTML 不是贴在图里的字。禁止装饰插画冒充架构。data-page-type=diagram。

## Must
- Set `data-page-type="diagram"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] geometry is the argument
- [ ] HTML labels
- [ ] caption present
- [ ] no stock illustration
- [ ] data-page-type=diagram
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
