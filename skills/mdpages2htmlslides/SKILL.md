---
name: mdpages2htmlslides
description: Converts F&B diagnosis, TIANSIGHT, strategy, roadmap, and brand-dossier markdown into locked 2880×1620 HTML slides using 4 L1 shells × 12 L2 jobs × 16 L3 viz recipes. Use when turning MD into HTML slides, classifying slide types, writing slot instructions for a cheaper model, or auditing Baslide01 ref decks.
metadata:
  showcase: showcase/showcase.json
---

# MD → HTML slides

Two models. Top model **plans**. Cheap model **fills**. Neither invents CSS.

Locked renderer presets: **5 genres · 4 shells · 12 page templates · 16 visualization recipes**. Deck Grammar v2 supplies the argument, intent, evidence, provenance, encoding, and solved-layout contract above those presets.

- [taxonomy.md](taxonomy.md) · [taxonomy.json](taxonomy.json) · [pipeline.md](pipeline.md)
- Shared contract: [schema/deck-plan.schema.json](schema/deck-plan.schema.json) and [design/page-types.json](design/page-types.json)
- Deck Grammar v2: [reference/deck-grammar-v2.md](reference/deck-grammar-v2.md) and versioned [design/policy-v2.json](design/policy-v2.json)
- Sidera / tiansight brand source: [design/brands/tiansight.json](design/brands/tiansight.json), resolved from the latest published Apuch guide and canonical logo
- One deterministic renderer: [scripts/render-deck.py](scripts/render-deck.py) (`deck-plan.json` → self-contained HTML; `deck.json` is a read-only fallback)
- Render gates: [scripts/gate_schema.py](scripts/gate_schema.py) then [scripts/gate_layout.py](scripts/gate_layout.py) with Python Playwright and installed Chrome; [scripts/export_pdf.py](scripts/export_pdf.py) emits and validates 16:9 PDF pages only after both gates pass
- Original samples per type: [samples/INDEX.md](samples/INDEX.md)
- Complete one-file report: [`ref/REPORT-md-to-html-slide-types.md`](../../ref/REPORT-md-to-html-slide-types.md)
- Full ref audit: [`ref/AUDIT-md-to-html-taxonomy.md`](../../ref/AUDIT-md-to-html-taxonomy.md)
- Baslide01 module: [`modules/baslide01`](../../modules/baslide01)

## When to use

- User drops a report MD and wants HTML slides
- User asks how many slide types / L1 L2 L3 to keep
- User wants a cheaper model to implement a top-model outline
- Files named like 清水亭 / 侍天 / 石头先生 / 苏帮袁 / 首版汇报 / 赋能路线图 / 品牌专项

For already-typed TIANSIGHT pages with D3, also apply `skills/TIANSIGHT-html-slides` and `skills/page-loop`. Do not mix Guizang classes into TIANSIGHT shells.

## Workflow

1. Pick **genre** from the MD (`diagnosis` `system` `briefing` `roadmap` `dossier`).
2. **Top model only:** write GF-compatible `deck-plan.json`: argument `node`, structured `claim`, `intent`, `evidence` with provenance, renderer `template`, structured `content`, and a solved `layout` trace. No HTML.
3. Each slide: L2 job → L3 viz `fill` (or `null`) → bind L1 shell. Table row budget comes from the L2 job.
4. **Cheap model only:** clone `templates/TIANSIGHT/jobs/<job>.html`; fill slots; no new CSS selectors. Tokens from `templates/TIANSIGHT/TIANSIGHT-v2.css`. Size against `samples/job/<id>.md` at 2880×1620. Put SOURCE + GLOSSARY + CONCLUSION + CONFIDENCE in `.sd-rail` (cloned to `#sd-explain`, not painted on the canvas).
5. Set `data-page-type` to the L2 id (`toc` and `readme` are allowed).
6. Apply `prompts/loop/brand.md`. If `prompts/loop/<id>.md` is missing, use the mapped file (`readme`→`statement.md`, `toc`→`chapter.md`).
7. Paginate with `overflow_of` + title suffix `续` (gold: 126/296).
8. Diagnosis pages need SOURCE, HOW TO READ, TAKEAWAY. Then page-audit.
9. Export only through `export_pdf.py`; every PDF page must be 16:9 and the page count must equal the HTML slide count.

## Do not

- Hand the cheap model the raw 17 workshop ids as a menu
- Add a 13th L2 job (`playbook` `profile` `timeline` fold into `compare` / `roster` / `statement`)
- Reuse 07 data-source L0–L5 or 08 brand-filter L1–L3 as slide layers
- Invent viz ids; use the 16 + aliases (FT Visual Vocabulary families in taxonomy.md)
- Create a second page taxonomy: translate `quote→statement`, `playbook→verdict`, `gallery→roster`, and `interactive→chart`
- Treat `sum-roster` / `kpi-cards` / `state-matrix` / `dual-calibre` / `profile-card` / `falsify-quad` as types — those are L2 jobs
- Emit empty competitor figures
- Mix Inter / purple / Guizang `h-hero` into TIANSIGHT
- Keep workshop chrome (`#baslide-chrome`) in the slide
