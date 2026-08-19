# Loop · Brand (all types)

Apply this file on **every** HTML slide, then apply `prompts/loop/<type>.md`. Generate, check, fix, repeat. Stop only when every check passes. Do not invent a new page type.

## Tokens (pick one skin, never mix)

| Skin | Surface | Ink | Accent | Type |
|---|---|---|---|---|
| TIANSIGHT | `#F4F0E7` paper `#FBF8F2` | `#17130D` | gold `#76551F` / seal `#8C3228` | `--sd-font-serif` + `--sd-font-mono` · canvas 2880×1620 · packs via `?font=` |
| magazine | theme from `references/themes.md` only | — | no custom hex | Noto Serif SC + Playfair · classes from `template.html` |
| swiss | paper/ink from Swiss theme | IKB / lemon / lime / safety orange **one** | Inter + Noto Sans SC | classes from `template-swiss.html` |
| tableai | `#0A1626` `#FFFFFF` | `#A88B52` only | Manrope 600/700 · radius 2–4px · **no box-shadow** |
| atelier | copy atelier template tokens | — | do not invent classes |

## Must

1. `data-page-type="<id>"` on every `<section class="slide">`.
2. Copy layout from the linked template. **Do not invent CSS class names.**
3. One decision per page. If it cannot answer “tomorrow, do what?” on data pages, delete it.
4. Workshop chrome (`#baslide-chrome`) is not part of the slide. Generate as if `?export=1`.
5. Numbers: tabular / IBM Plex Mono (TIANSIGHT) or the skin’s numeral face. Right-align in tables.
6. Whitespace: magazine or report, never a SaaS dashboard. No purple gradients, no Inter on TIANSIGHT, no 3D charts, no rainbow heatmaps.
7. Images: standard ratios (16:9, 16:10, 4:3, 1:1). Grids share one height class.
8. After writing HTML, re-read this file and the type loop. Fail any missed check and patch. Max 3 loops, then report remaining fails.
9. Canvas copy is complete. Type scale is allowed only after every glyph is visible. Never put `…` / `...` on the field (title, statement, table cell, chip). Paginate at `。！？` / `；`. No 孤儿字, no 孤儿行, no leftover one-line page. TIANSIGHT header is one row: transparent 侍天 logo + `.sd-chip`. Use `.sd-quote` in a paper well on statement. `.sd-h2` wraps; do not clip. Set `data-pack=air|mid|tight` from how much copy the page carries so a short claim fills the well and a 10-row roster stays readable.
10. Fenced code, ASCII bars (`█`), box wireframes (`┌─┐`), and price ladders are **figures** (`chart` / `roster`). Never dump them onto `statement`. Large structured copy becomes an infographic; a statement page stays one claim.

## Must not

- Mix TIANSIGHT classes with Guizang (`h-hero`, `stat-nb`) on the same page
- Screenshot or keep the top bar in the exported page
- Invent a 18th page type
- Decorative stock art pretending to be structure
- More than one job on one slide
- `<cite`, `cite index=`, or `&lt;cite` on the canvas or in `#sd-explain`
- Syllabus voice on the canvas: 「本专项给出」「本文件回答」「学什么 / 不学什么 / 怎么验证」

## Beauty bar

The page should look like a printed 侍天 report or a locked Guizang skin: hairline rules, gold/navy accents, serif or the skin’s locked sans, generous margins, one focal point. If it looks like a Bootstrap admin, it fails.

## Type proportion (TIANSIGHT · 2880×1620)

The slide is a **poster**. Size is a share of canvas height, never a desktop px habit. Default `--sd-em` = **2.45% of 1620** (mid). A short page sets `data-pack=air` (2.8% / statement quote 4.8%); a dense roster sets `data-pack=tight` (2.1%). Do not jump the whole deck to 2.7% or down to the v2.5 floor. Complete text first; do not raise this stair if a line would clip, ellipsis, or orphan.

| Role | Token | mid | air | tight |
|---|---|---|---|---|
| Cover | `--sd-type-hero` | 9.0% | 9.0% | 9.0% |
| Chapter numeral | `--sd-type-display` | 11.8% | 11.8% | 11.8% |
| Chapter title | `--sd-type-h1` | 5.2% | 5.2% | 5.2% |
| Statement | `--sd-type-quote` | 3.6% | 4.8% | 3.0% |
| KPI value | `--sd-type-kpi` | 6.6% | 7.2% | 6.6% |
| Slide title | `--sd-type-h2` | 3.4% | 3.6% | 2.8% |
| Card / cell | `--sd-type-h3` | 2.4% | 2.6% | 2.0% |
| Prose / table | `--sd-type-body` | 2.45% | 2.6% | 2.0% |
| Caption | `--sd-type-small` | 1.75% | 2.0% | 1.5% |
| Chrome | `--sd-type-micro` | 1.3% | 1.3% | 1.3% |

Bands: margin 3.2% of width · title band 14.8% of height (one-line header) · footer 5.6% of height · content 14.8%–94.4%. Cover decision uses `--sd-type-h3`. KPI label sits above the value; the number fills the card. SVG labels use the same shares of the figure box. If copy does not fit, paginate — never shrink by cutting words.
