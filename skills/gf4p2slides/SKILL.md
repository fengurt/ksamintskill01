---
name: gf4p2slides
description: Turn structured page material into brand-consistent slide decks, responsive HTML, and print-friendly documents. Use when classifying page types, planning data visualizations, or creating a brand-specific sub-skill that reuses one generic presentation grammar.
metadata:
  author: ksamint
  origin: ksamint
  repository: fengurt/ksamintskill01
  showcase: showcase/showcase.json
---

# GF4p2slides

Generic framework for page material to slides, HTML, and documents.

Keep three concerns separate:

1. **Narrative page type**: what this page must communicate.
2. **Visualization recipe**: how structured evidence should be shown.
3. **Brand pack**: how the result should look and sound.

Do not copy a full renderer into every brand skill. A brand sub-skill should call this skill, provide official assets and tokens, and override a page or visualization only when the published brand guide requires it.

## Load only what the task needs

- Read [references/page-templates.md](references/page-templates.md) when classifying or designing pages.
- Read [references/data-visualizations.md](references/data-visualizations.md) when a page contains structured data or a visualization renderer is being developed.
- Read [references/brand-subskills.md](references/brand-subskills.md) when creating or updating a brand-specific sub-skill.

## Brand source

For a named brand, resolve the latest published guide, theme tokens, and official assets from `https://apuch.art/` before creating or restyling an artifact. If the brand is not published there, use an official guide supplied by the user. Never invent a logo, brand color, font, or brand claim.

Record the source URL and publication/version date in the brand sub-skill. Brand assets are inputs, not decoration to approximate.

## Workflow

1. Choose the output mode: `slides`, `html`, or `document`.
2. Read the source material and make a page list. Every page gets exactly one primary page template from the 12-template registry.
3. Add a visualization recipe only when the page has a concrete data question. Tables, quotations, and prose do not need a chart id.
4. Load the selected brand sub-skill. Apply its tokens and assets without changing the page taxonomy.
5. Render the primary mode first. Derive the other modes from the same page plan instead of rewriting the narrative.
6. Check fit, source fidelity, accessibility, and visual consistency before delivery.

## Page-plan interface

Use this minimum shape between planning and rendering:

```json
{
  "title": "Deck title",
  "brand_skill": "example-gf4p2slides",
  "mode": "slides",
  "pages": [
    {
      "id": "p-001",
      "template": "cover",
      "title": "A decision-shaped title",
      "source": "Source label or URL",
      "takeaway": "The one conclusion this page earns",
      "visualization": null,
      "content": {}
    }
  ]
}
```

Required for every page: `id`, `template`, `title`, and `content`. Use `source` whenever the page makes a factual claim. Use `takeaway` on evidence and decision pages. `visualization` is one registered visualization id or `null`.

The `content` object is template-specific. Renderers must reject an unknown template or visualization id rather than silently inventing one.

## Output modes

- **Slides**: fixed 16:9 pages. Paginate instead of shrinking below the brand pack's minimum type size.
- **HTML**: responsive sections using the same order, titles, sources, and takeaways. Do not preserve slide geometry when it harms reading.
- **Document**: print-friendly linear flow. Keep evidence tables and citations available even when the slide used a chart.

## Quality bar

- One communication job per page.
- One primary page template per page.
- One data question before one chart recipe.
- The chart has a text alternative and underlying table or data payload.
- Titles state the decision or finding, not the chart form.
- Official logos keep their aspect ratio and clear space.
- Color is never the only carrier of meaning.
- No 3D charts, rainbow palettes, decorative axes, or unlabeled proxy data.
- Overflow creates another page; it does not create another template id.

## Test the contract

Use [showcase/samples/decision-brief.md](showcase/samples/decision-brief.md) for a representative layout smoke test. Compare its five-page structured output with [showcase/samples/page-plan.json](showcase/samples/page-plan.json), and inspect [showcase/demo.html](showcase/demo.html) for the reference rendering.

The browser lab tests deterministic fit and required content. It does not classify pages, invoke a model, or replace source-fidelity review.

## Current boundary

This first version defines the stable taxonomy, page-plan interface, brand-pack seam, and visualization renderer contract. It does not bundle a universal HTML/SVG renderer yet. Add renderers recipe by recipe only after each has a real example, an accessible fallback, and a runnable check.
