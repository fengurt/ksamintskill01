# Loop · 章扉 (`chapter`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `chapter`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
切幕：上一章结束，下一章开始

Use when: 章节切换、Act divider
Avoid when: 正文论证页
Slots: act number · chapter title · one-line promise
Skins: TIANSIGHT, magazine, swiss, tableai

## Constraint
章扉是切幕不是目录。巨大章号 + 章名 + 一句承诺。禁止正文段落、禁止图表。呼吸感优先。data-page-type=chapter。

## Must
- Set `data-page-type="chapter"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] act number dominant
- [ ] one promise line
- [ ] no body paragraphs
- [ ] no charts
- [ ] data-page-type=chapter
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
