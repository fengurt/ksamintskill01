# Loop · 结论 / 证伪 (`verdict`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `verdict`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
争议、事实、处理、证伪；或行动收束

Use when: A58、closing manifesto、下一步
Avoid when: 没有证伪条件的鸡汤结尾
Slots: dispute · fact · handling · falsify
Skins: TIANSIGHT, magazine, swiss, tableai

## Constraint
争议 / 事实 / 处理 / 证伪 四格，或一句可执行收束。禁止鸡汤。TIANSIGHT 可盖印。data-page-type=verdict。

## Must
- Set `data-page-type="verdict"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] falsify or next action
- [ ] no empty pep talk
- [ ] four cells or one close line
- [ ] data-page-type=verdict
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
