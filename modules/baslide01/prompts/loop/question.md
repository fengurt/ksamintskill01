# Loop · 提问 / 悬念 (`question`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `question`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
把读者停在一个问题上

Use when: 转折、收束前、互动
Avoid when: 问题里已经藏了答案还装不知道
Slots: question · optional stake
Skins: magazine, swiss, tableai

## Constraint
只停在一个问题上。问句巨大，可选一行赌注。不要在同页给答案。data-page-type=question。

## Must
- Set `data-page-type="question"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] one question
- [ ] no answer on page
- [ ] optional stake ≤1 line
- [ ] hero scale type
- [ ] data-page-type=question
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
