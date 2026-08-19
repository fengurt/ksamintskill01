# Loop · 封面 (`cover`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `cover`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
这一份 deck 是谁、讲什么、给谁看

Use when: 第一页、章扉、品牌开场
Avoid when: 已经进入论证，还在铺身份
Slots: kicker · title · one-line decision · meta chips
Skins: TIANSIGHT, magazine, swiss, tableai, atelier

## Constraint
封面只定身份。超大标题 ≤3 行，一行决策，kicker + meta chips。决策是判断，不是目录、方法说明或「本报告将回答 A / B / C」。留白要像杂志封面，不要仪表盘。套所选皮肤令牌与类名，data-page-type=cover。

## Must
- Set `data-page-type="cover"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] title ≤3 lines
- [ ] one-line decision present
- [ ] kicker + chips
- [ ] no chart/KPI dump
- [ ] data-page-type=cover
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
