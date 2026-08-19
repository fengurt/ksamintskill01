# TIANSIGHT templates

Canonical skin: **v2.0** at 2880×1620 (16:9). Tokens, chrome, font packs, and print/PDF live in `TIANSIGHT-v2.css`. Do not hand-edit hex inside a slide.

| File | Role |
|---|---|
| `TIANSIGHT-v2.css` | Design tokens + 4 L1 shells + hideable `#sd-explain` + font packs + `@media print` |
| `TIANSIGHT-deck.js` | Fit-to-viewport, ← →, **E** explain, **F** font cycle, **P** print/PDF, `?font=` `?export=1` |
| `jobs/<job>.html` | 12 L2 jobs. `chart` and `roster` are filled recipes (√-area bubble + brand-grain 清单). Clone these; do not invent classes |
| `logo/侍天.png` | Transparent 侍天 mark. Header leftmost. Source knock-out also at the brand logo folder. |
| `gallery.html` | 12-up iframe preview |
| `layouts.html` | v1 museum (1440×810, eight workshop layouts) |

## L1 shells (4)

`shell-cover` · `shell-divider` · `shell-body` · `shell-fig`

Rail (`.sd-rail`) is required **as data** on data jobs: readme, statement, kpi, roster, chart, chart-table, matrix, compare, verdict. Four cards — SOURCE / GLOSSARY / CONCLUSION / CONFIDENCE — are not painted on the canvas; the deck script clones them into `#sd-explain` (bottom drawer, **hidden by default**). **E** or the bottom bar opens it. cover / divider / toc never carry it.

## L2 jobs (12)

cover · divider · toc · readme · statement · kpi · roster · chart · chart-table · matrix · compare · verdict

`data-job` is the L2 id. `data-page-type` maps divider → `chapter`; toc/readme keep their L2 ids.

## Fonts

`--sd-font-serif` / `--sd-font-mono` only (two-family system). Packs: `TIANSIGHT` `songti` `kaiti` `fangsong` `lxgw` `xiaowei` `roboto-mono`.

```
/templates/TIANSIGHT/jobs/cover.html?font=lxgw
/decks/stone-briefing/presentation.html?font=songti&export=1
```

Print uses `@page { size: 16in 9in }` so Chrome keeps 16:9. **P** or FONT UI “PDF / 打印” calls `window.print()`. `?export=1` hides workshop chrome and `#sd-explain`. `?print=1` shows every slide for headless PDF. Present mode contain-fits the local window (this Mac is 3024×1964 / 1512×982 CSS).

## Build decks from markdown

```
python3 scripts/build-TIANSIGHT-deck.py
```

Outputs `decks/stone-briefing/` `decks/stone-roadmap/` `decks/stone-dossier/`. Spec source: `ref/TIANSIGHTtemplatespreview (1)/`.
