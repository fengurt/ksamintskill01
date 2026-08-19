# Baslide01

HTML slide workshop: generate, preview, and keep working decks in one static repo.

The original drop in `files (10)/` is the 侍天 TIANSIGHT report prototype. Script tags pointed at `src/` while the JS files sat next to `index.html`, so the demo did not load. The working copy is `demos/TIANSIGHT/` with that layout restored.

## Local run

```bash
bash scripts/dev-up.sh
```

The script frees only a listener that belongs to this repo, then binds the first free port among **8765 → 8080 → 5173**. It opens the gallery in the browser.

The homepage is a **page-type catalog** (`page-types.json`): pick the job of the page, then a skin. Workshop top bar: 首页 / 类型 / 审计. Press **H** to hide. `?export=1` and print omit the bar.

| Surface | Path |
|---|---|
| Gallery | `/` |
| Page types | `/types/` |
| Page audit agent | `/audit/?run=1` |
| TIANSIGHT demo | `/demos/TIANSIGHT/` |
| Deck 编号总表 | `/decks/` |
| D01 增城太子坑 | `/decks/zengcheng-taizikeng/deck.html` |
| D02 Premium PPT | `/decks/premium-ppt/presentation.html` |
| D03 首版汇报 | `/decks/stone-briefing/` |
| D03.1 MD→侍天 | `/decks/stone-briefing/presentation.html` |
| D03.2 HTML 导入 | `/decks/stone-briefing/html-v1.html` |
| D04 赋能路线图 | `/decks/stone-roadmap/presentation.html` |
| D05 品牌专项 | `/decks/stone-dossier/presentation.html` |
| D06 清水亭诊断 | `/decks/qingshuiting/presentation.html` |
| TIANSIGHT v2 gallery | `/templates/TIANSIGHT/gallery.html` |
| TIANSIGHT v1 layouts | `/templates/TIANSIGHT/layouts.html` |
| Magazine template | `/templates/magazine/template.html` |
| Swiss template | `/templates/swiss/template-swiss.html` |
| Table AI template | `/templates/tableai/template-tableai.html` |
| Atelier template | `/templates/atelier/template-atelier.html` |
| Guizang skill index | `/skills/guizang-ppt/INDEX.html` |

## Skills

Installed into this repo and into `~/.cursor/skills/guizang-ppt` / `~/.claude/skills/guizang-ppt-skill`.

- **guizang-ppt** — single-file HTML PPT. Style A magazine, Style B Swiss, Style C Table AI. Source: [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) with Table AI fork.
- **TIANSIGHT-html-slides** — 1440×810 report slides using TIANSIGHT tokens, 8 layouts, six rendering rules.
- **page-audit** — 页面审计 Agent. Open `/audit/`, or ask the agent to 审计页面.

## Templates

| Folder | Style | Use |
|---|---|---|
| `templates/magazine/` | A · 电子杂志 × 电子墨水 | Narrative, essays, talks |
| `templates/swiss/` | B · Swiss International | Product, data, method |
| `templates/tableai/` | C · Table AI Design System | KPI, SaaS, brand decks |
| `templates/atelier/` | Atelier (gold + navy serif) | Editorial brand talks |
| `templates/TIANSIGHT/` | 侍天 v2.0（2880×1620，12 L2 jobs） | F&B / briefing / roadmap / dossier；v1 `layouts.html` 仍保留 |

## Existing decks

Numbers live in `decks.json`. Locate updates by **D01–D06**.

- **D01** `decks/zengcheng-taizikeng/` — Style C deck with local SVG images. Keyboard ← →, ESC overview, B low-power.
- **D02** `decks/premium-ppt/` — 5-page sample.
- **D03** `decks/stone-briefing/` — 首版汇报 hub. D03.1 is the 06 MD→侍天 generate; D03.2 is the imported 32-page HTML. The pack DB lives inside each stone deck as an unnumbered 库 page (`data.html`); sqlite stays in D03 and is not copied.
- **D04** `decks/stone-roadmap/` — 07 赋能路线图.
- **D05** `decks/stone-dossier/` — 08 品牌专项.
- **D06** `decks/qingshuiting/` — 清水亭产品结构诊断（从 `ref/htmls/` 导入，296 页 1440×810）。
- `demos/TIANSIGHT/` — ingest → align → gate → render. Click **载入演示数据** if the first paint is empty; it auto-clicks on load.

## Constraints

- No bundler. Open HTML, or serve the repo root.
- Do not invent CSS classes that are missing from the chosen template.
- TIANSIGHT v2 canvas is 2880×1620 (`templates/TIANSIGHT/TIANSIGHT-v2.css`). Font packs via `?font=` or F. Tokens live in `cursor_project_rules/project-context.mdc`.
