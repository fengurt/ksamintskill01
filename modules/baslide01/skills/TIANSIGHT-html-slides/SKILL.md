---
name: TIANSIGHT-html-slides
description: Generate 2880×1620 HTML report slides with 侍天 TIANSIGHT v2.0 tokens, 4 L1 shells × 12 L2 jobs, hideable explain panel, font packs, and nine rendering rules. Use when the user asks for TIANSIGHT slides, 侍天报告页, F&B diagnosis / briefing / roadmap / dossier decks, or HTML slides that must carry SOURCE / GLOSSARY / CONCLUSION / CONFIDENCE.
---

# TIANSIGHT HTML slides

Generate **fixed-canvas HTML slides** (2880×1620) for 侍天 TIANSIGHT reports. One decision per page. Do not turn this into a dashboard. SOURCE / GLOSSARY / CONCLUSION / CONFIDENCE live in `#sd-explain`, a bottom drawer hidden by default.

## When to use

- User wants TIANSIGHT / 侍天 / 清水亭-style report pages
- User names an L2 job (`cover` `divider` `toc` `readme` `statement` `kpi` `roster` `chart` `chart-table` `matrix` `compare` `verdict`)
- User wants HTML slides with bronze/paper tokens, IBM Plex Mono numbers, Noto Serif SC body, font replacement, PDF export

Pick the L2 job first, then the TIANSIGHT skin. For magazine / Swiss / Table AI swipe decks, use `skills/guizang-ppt` with a workshop type id.

## Tokens (locked)

Source of truth: `templates/TIANSIGHT/TIANSIGHT-v2.css`. Do not hand-edit hex in a slide.

```css
--sd-surface:#F4F0E7; --sd-paper:#FBF8F2; --sd-primary:#EFE6D2;
--sd-ink:#17130D; --sd-accent:#76551F; --sd-secondary:#8C3228;
--sd-font-serif: "Noto Serif SC", "Songti SC", serif;
--sd-font-mono: "IBM Plex Mono", monospace;
canvas: 2880 × 1620;
type: --sd-em = 2.45% mid (air 2.8% / tight 2.1%); quote 3.6% / 4.4% / 3.0%; KPI 6.6% / 7.2%. Set data-pack from how much copy the page carries. Complete text first; never ellipsis on the canvas.
header: one row — transparent 侍天 logo + `.sd-chip` (`图 18 · 叁 · 本报告核心`) + `.sd-index`. Logo file: `templates/TIANSIGHT/logo/侍天.png`.
```

Text contrast: only `--sd-ink-100` / `--sd-ink-72` / `--sd-ink-60` may render as text. `--sd-ink-45` and below are decoration.

Clone `templates/TIANSIGHT/jobs/<job>.html`. Replace slot text. Do not invent class names. Set `data-job` and `data-page-type` (`divider` → `chapter`).

## 12 L2 jobs × 4 L1 shells

| Job | Shell | Use |
|---|---|---|
| `cover` | `shell-cover` | Deck identity |
| `divider` | `shell-divider` | Chapter cut |
| `toc` | `shell-body` no-rail | Contents |
| `readme` | `shell-body has-rail` | Calibre table (confidence in `#sd-explain`) |
| `statement` | `shell-body has-rail` | One claim |
| `kpi` | `shell-body has-rail` | 3–6 cards |
| `roster` | `shell-body has-rail` | Full list + sum row |
| `chart` | `shell-fig has-rail` | One figure |
| `chart-table` | `shell-fig has-rail` | Figure + executable names |
| `matrix` | `shell-body has-rail` | 九宫 / score, 3-state ink |
| `compare` | `shell-body has-rail` | Left / 因此 / right |
| `verdict` | `shell-body has-rail` | Dispute / fact / handling / falsify |

v1 museum (1440×810, eight layouts): `templates/TIANSIGHT/layouts.html`.

## Explain panel (data jobs)

SOURCE · GLOSSARY (how to read) · CONCLUSION (takeaway) · CONFIDENCE (A/B/C) are **not** on the 2880×1620 canvas. Keep `.sd-rail` in the job HTML as data; `TIANSIGHT-deck.js` clones it into `#sd-explain`, a **bottom drawer hidden by default**. A bottom bar reads 「解释 · 数据出处 / 术语 / 结论 / 置信度」; **E** or the bar opens it. cover / divider / toc never carry `.sd-rail`. `?export=1` / print omit the panel.

## Nine rendering rules

1. Denominator travels with the chart
2. Median split uses `≥` (high side)
3. Zero is not a gap unless the column base meets the threshold
4. `n` below threshold gets hatch fill, never hidden
5. Proxy metrics get a “禁止外部对标” watermark
6. Category sums must close; refuse to render if they do not
7. Bubble / quadrant: area ∝ √size, large-first, dashed median ≥, paper-stroke labels; unlabeled points belong on the following roster. Clone `templates/TIANSIGHT/jobs/chart.html`.
8. Figure 清单 is named grain. Band charts with 品牌数 expand to brand rows. Store-count hists stay as bins, but the 清单 adds 占比 / 累计 and same-unit named samples. Clone `templates/TIANSIGHT/jobs/roster.html`.
9. Header is one line (logo + chip). Bar values stay inside the mark or sit outside in ink with a paper halo — never paper-colored type on `--sd-paper`. Lists stay compact. Statement claim fills a paper well; 2–4 依据 are peer cards. Leftover one-row / one-line pages are absorbed. `data-pack` follows content so a short claim is air and a 10-row roster is tight.

## Fonts and PDF

`--sd-font-serif` / `--sd-font-mono` only. Packs: `TIANSIGHT` `songti` `kaiti` `fangsong` `lxgw` `xiaowei` `roboto-mono`. `?font=` or **F**. Print: `@page 16in 9in`, **P** / `?print=1` for PDF. `?export=1` hides workshop chrome and `#sd-explain`. **E** toggles the bottom explain drawer (closed by default). Never emit `<cite` / `cite index=`.

## Workflow

1. Pick L2 job from the 12. Clone `templates/TIANSIGHT/jobs/<job>.html`.
2. Fill chrome (`.sd-tk` contains logo + `.sd-chip`; then `.sd-h2`) and `.sd-rail` cards (data for `#sd-explain`). Keep one decision per page.
3. Charts: inline SVG `viewBox="0 0 1170 500"` using `--sd-accent` / `--sd-secondary` / `--sd-seq-*`, hatch for small-n, units and value labels on the figure. `--sd-cat-*` only when series must be distinguished and each has a direct label. Bubble/quadrant follow rule 7; every figure is followed by a roster 清单 (rule 8).
4. Serve via `bash scripts/dev-up.sh`. Preview `/preview/?type=<id>&skin=TIANSIGHT` or `/templates/TIANSIGHT/gallery.html`. Apply `prompts/loop/brand.md` and `prompts/loop/<type>.md`.
5. Markdown reports: `python3 scripts/build-TIANSIGHT-deck.py`.

## Do not

- Mix Guizang Swiss classes (`h-hero`, `stat-nb`) into TIANSIGHT pages
- Use Inter / purple gradients / card-dashboard chrome
- Invent a 13th L2 job or a third font family
- Emit a page that cannot answer “tomorrow, do what?”
- Emit `<cite`, `cite index=`, or Cursor cite leftovers on a slide
- Put `…` on the canvas (title, statement, table cell) or leave 孤儿字 / 孤儿行
- Dump fenced ASCII / `█` bars / box wireframes onto a statement page
