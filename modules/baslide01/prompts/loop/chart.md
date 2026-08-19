# Loop · 单图全幅 (`chart`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `chart`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
一张主图回答一个决策

Use when: 帕累托、瀑布、四象限、直方图、气泡、阶段权重、价位梯、ASCII/代码块示意图
Avoid when: 图上看不出明天做什么。ASCII 条和线框禁止当正文。
Slots: source · chart 72% · how-to-read · takeaway
Skins: TIANSIGHT, swiss, tableai

## Constraint
一张主图占约 72% 高度，回答一个决策。图上的轴名、刻度、直接标注必须跟页面字号同一套比例；柱内数字必须落在柱里，装不下就改到柱外用墨色+纸色描边，禁止浅底上的纸色字。必须有 SOURCE、HOW TO READ、TAKEAWAY（可执行 + 数字）。禁止双图、禁止装饰 3D。页眉一行：logo + chip。data-page-type=chart。

气泡 / 象限：面积按平方根，大点先画，虚线是中位 ≥，标签带纸色描边；密集团只标分得开的点，其余见后页清单。禁止线性半径把麦当劳画成盖住全图的圆。clone `templates/TIANSIGHT/jobs/chart.html` 里的 SVG 当配方。

## Must
- Set `data-page-type="chart"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] one chart
- [ ] source bar
- [ ] how-to-read
- [ ] takeaway with number
- [ ] bubble/quadrant uses √ area, median ≥, selective labels
- [ ] unlabeled points promised on the following 清单
- [ ] data-page-type=chart
- [ ] skin tokens only

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
