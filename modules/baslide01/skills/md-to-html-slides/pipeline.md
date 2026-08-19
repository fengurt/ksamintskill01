# Two-model pipeline

Top model writes JSON. Cheap model writes HTML from that JSON. Loop prompts check the HTML.

## Roles

| Model | Does | Must not |
|---|---|---|
| Top | Genre, chunking, L2/L3 labels, slot text, pagination plan, denom, takeaway | Emit HTML, invent L2/L3 ids |
| Cheap | Clone L1 shell, substitute slots, keep class names | New CSS, new jobs, new viz, drop SOURCE on `续` pages |
| Loop | `prompts/loop/brand.md` + mapped type file, max 3 patches | “It’s a draft” skip |

## Slide-plan schema

```json
{
  "source": "path/to/report.md",
  "genre": "diagnosis",
  "skin": "TIANSIGHT",
  "slides": [
    {
      "id": "p-004",
      "shell": "body",
      "job": "roster",
      "fill": null,
      "overflow_of": null,
      "chips": ["A10", "口径 A", "72 天"],
      "kicker": "肆 · ABC 与二八",
      "title": "口径 A：118 SKU 全量归属",
      "source": "品项汇总·索引表 · 118 SKU · 额 = 标准价 × 72 天销量",
      "how_to_read": "行是 SKU，最后一行必须闭合到 100%",
      "takeaway": "前 40 款扛 80% 额，先动长尾。",
      "falsify_id": "F.6",
      "slots": { "columns": ["SKU", "额", "累计%"], "rows": [], "sum": [] }
    }
  ]
}
```

Required on every slide object: `id` `shell` `job` `title`.
Required on diagnosis data slides: `source` `how_to_read` `takeaway`.
`fill` is an L3 viz id, or `null`. Tables are not a fill id — they inherit the L2 job’s row budget.

## Pagination

If rows > budget in taxonomy.json:

1. Keep the same `job` and `fill`
2. Set `overflow_of` to the parent `id`
3. Append `续` to `title`
4. Repeat SOURCE and denom; TAKEAWAY only on the last overflow page

## Shell clone map

| L2 job | Clone |
|---|---|
| cover | `templates/TIANSIGHT/jobs/cover.html` |
| chapter / divider | `templates/TIANSIGHT/jobs/divider.html` |
| toc | `templates/TIANSIGHT/jobs/toc.html` |
| readme | `templates/TIANSIGHT/jobs/readme.html` |
| statement | `templates/TIANSIGHT/jobs/statement.html` |
| chart / chart-table | `templates/TIANSIGHT/jobs/chart.html` / `chart-table.html` |
| matrix | `templates/TIANSIGHT/jobs/matrix.html` |
| kpi | `templates/TIANSIGHT/jobs/kpi.html` |
| roster | `templates/TIANSIGHT/jobs/roster.html` |
| compare | `templates/TIANSIGHT/jobs/compare.html` |
| verdict | `templates/TIANSIGHT/jobs/verdict.html` |

Tokens: `templates/TIANSIGHT/TIANSIGHT-v2.css`. v1 museum: `templates/TIANSIGHT/layouts.html`. Gold fig SVG recipes: `ref/清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html`.

## Cheap-model HTML rules

1. `data-page-type="<job>"` on `<section class="slide">`
2. No new class names
3. Numbers: `n` or `.num`, IBM Plex Mono, right-aligned in tables
4. Roster last row `.sum` must close
5. `n` below threshold: hatch, never hide
6. Proxy metrics: watermark `禁止外部对标`
7. One decision per page
8. Bubble / quadrant: area ∝ √size, large-first, dashed median ≥; unlabeled → next roster. Clone the SVG in `jobs/chart.html`.
9. Figure 清单 is named grain. 品牌数 bins expand to brand rows. Store-count hists stay bins, with 占比 / 累计 and same-unit named samples.

## Checks after fill

- Brand loop: `prompts/loop/brand.md`
- Type loop: `prompts/loop/<job or mapped>.md`
- Audit: `skills/page-audit` (ROOT, TITLE, TOKEN, HOME chrome when served)
