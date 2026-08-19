# Loop · 全量名录 (`roster`)

Read `prompts/loop/brand.md` first. Then this file. Generate one HTML page of type `roster`. Re-check every item. If any fail, fix and loop. Stop only when all pass.

## Job
逐一列名，合计必须闭合

Use when: 下架清单、错配名录、门店表、图后细项
Avoid when: 只给 TOP10 却声称全量；价格带清单只重复分箱合计
Slots: sortable table · sum row · filter chips
Skins: TIANSIGHT, swiss, tableai

## Constraint
全量列名，合计行必须闭合。禁止 TOP10 冒充全量。数字右齐等宽。data-page-type=roster。

图后清单是全量切片。品牌数分箱图的清单必须落到品牌行（价格带 / 品牌 / 门店 / 人均 / 评分 / 规模），不要再印 8 行带合计。商户数 / 门店数直方图保持分箱，不拆成几百行店；清单必须带占比与累计，同节有门店/品牌样本则挂上代表店，不要只印两列带合计。clone `templates/TIANSIGHT/jobs/roster.html`。

## Must
- Set `data-page-type="roster"` on the slide.
- Copy the chosen skin’s layout from `page-types.json` → `skins.<name>.href`. Do not invent classes.
- Keep the page’s single job. Do not smuggle another type onto this slide.

## Checks
- [ ] sum row closes
- [ ] not TOP10-as-all
- [ ] figure 清单 is named grain when the chart was 品牌数 bins
- [ ] store-count bin 清单 has 占比 / 累计, not just 门店数
- [ ] tabular right-aligned nums
- [ ] filter chips optional
- [ ] data-page-type=roster
- [ ] skin tokens only
- [ ] no leftover 1-row orphan page
- [ ] one-line header: logo + chip

## Loop
1. Write the HTML from the template.
2. Score the checks. Any miss → patch.
3. Repeat until all pass or 3 iterations, then report remaining fails.
