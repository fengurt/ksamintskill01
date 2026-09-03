---
name: html-quatracheck
description: Audit rendered HTML pages or slide decks across four quality passes, merge duplicate symptoms by root cause, and return the Top N defects to fix first. Use for HTML quality review, slide QA, overlap or clipping checks, orphan-character or orphan-line checks, accessibility review, or requests for a prioritized rather than exhaustive audit.
---

# HTML QuatraCheck

Audit the rendered result, then report only the highest-value fixes. Default to **Top 10** when the user does not supply N. Return fewer findings when fewer are supported; never pad the list.

## Reuse before checking

- In Baslide01, run the existing `page-audit` preflight (`bash scripts/dev-up.sh`, then `/audit/?run=1`) for HTTP, navigation, roots, scripts, and broken assets.
- For TIANSIGHT decks, apply `skills/TIANSIGHT-html-slides/references/quality-checklist.md` and `audit-checklist.md` as project-specific gates.
- Use an existing repository audit, axe-core integration, or screenshot test before adding new tooling.

## Establish the target

Record the URL or file, intended viewport or fixed canvas, page/slide count, export mode, and requested N. Audit every page when practical. For a very large deck, run mechanical checks across all pages and visually sample every page family plus all mechanically flagged pages; disclose the sampling boundary.

Wait for `document.fonts.ready`, images, SVG, charts, and transitions before measuring. Freeze animation and dynamic timestamps for screenshots. Test in the same browser, OS, viewport, scale, fonts, and headless mode as the baseline.

## Four passes

### 1. Render geometry

Fail visible content that overlaps unintentionally, leaves the canvas, is clipped, is hidden by fixed chrome, or requires unintended scrolling. Compare `scrollWidth/scrollHeight` with the content box and compare visible text/image rectangles with the page or slide root.

Bounding-box intersections are candidates, not proof. Ignore ancestor/descendant containment, backgrounds, decorative layers, and intentional overlays. Confirm a collision or clipping finding in the rendered screenshot.

### 2. Typography and line integrity

Fail:

- a final visual line containing only one meaningful CJK character;
- a punctuation-only line, closing punctuation at line start, or opening punctuation at line end;
- a single paragraph line stranded across a print/page/column break;
- ellipsis or emergency font shrinking that removes required content;
- unreadable type, missing fonts, distorted glyphs, or inconsistent peer sizing;
- text-spacing stress that causes clipping, overlap, or loss of content.

Use `Range.getClientRects()` or equivalent line rectangles for candidates, then inspect visually. Treat single-character brand marks, list indices, chart labels, and deliberate display type as exclusions. CSS `widows` and `orphans` govern fragmentation; they do not prove that a fixed-canvas slide has good line endings.

For the WCAG text-spacing stress pass, override line height to 1.5× font size, paragraph spacing to 2×, letter spacing to 0.12×, and word spacing to 0.16×. Any lost or obscured content is a failure.

### 3. Accessibility and semantics

Run the repository's existing axe-core integration when present. Check at least document language, title, heading order, landmarks, link/button names, keyboard focus, image alternatives, table semantics, text contrast, and meaningful graphical contrast.

Use WCAG AA contrast thresholds: 4.5:1 for normal text, 3:1 for large text, and 3:1 for meaningful non-text graphics or controls. Preserve axe-core's `critical`, `serious`, `moderate`, and `minor` impact, and label `incomplete` results as **needs review**, not as confirmed failures.

For ordinary responsive pages, test reflow at 320 CSS px without loss of information or two-dimensional scrolling. Fixed-dimension presentation canvases are an exception only when their meaning requires that layout; their authoring or viewing interface still needs an accessible alternative.

### 4. Content and export integrity

Fail broken assets, blank regions caused by failed rendering, missing or duplicated content, visible debug/internal fields, chart labels without units or denominators, and print/PDF output that changes page count, clips modules, omits fonts, or leaks controls.

For decks, verify every page family, not only the cover. For data pages, confirm that labels, values, units, denominators, legends, tables, and source notes remain readable in both screen and export modes.

## Collapse to root causes

Merge repeated symptoms when one selector, token, template, renderer, or data rule explains them. Report the shared cause once with the affected page count and representative examples. Keep separate findings only when they require different fixes.

## Rank the Top N

Sort lexicographically; do not invent a blended score:

1. **Severity:** P0 missing/misleading/inaccessible content; P1 overlap, clipping, unreadable text, broken interaction or export; P2 orphan lines/characters, hierarchy, semantics, and consistency; P3 polish.
2. **Reach:** shared root cause affecting more pages before a one-off.
3. **Confidence:** reproduced failure before heuristic or needs-review candidate.
4. **Order:** earlier page or DOM order as the stable tie-breaker.

Do not let many low-severity repeats outrank one P0 failure. A confirmed root cause outranks a vague symptom at the same severity.

## Report format

Start with scope: target, viewport/canvas, pages scanned, pages visually inspected, export mode, and N. Then return one row per finding:

| Rank | Priority | Root cause | Evidence | Reach | Minimum fix | Verify |
|---:|---|---|---|---:|---|---|

Evidence must name the page/slide and selector or component, plus an observable fact such as intersecting rectangles, overflow dimensions, contrast ratio, screenshot, or axe rule. End with counts for confirmed failures, needs-review candidates, and passed zero-tolerance gates.

Zero-tolerance gates for finished slides: unintended overlap 0; clipped/overflowing required content 0; orphan characters/lines 0; visible internal fields 0; broken assets 0; missing fonts 0.

Do not fix anything unless the user asked for fixes. If fixes were requested, patch the shared root cause first, rerun all affected pages, and regenerate screenshots or exports only after HTML passes.

## Benchmark basis

- [WCAG 2.2 Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html): 320 CSS px and no loss of information or functionality; notes presentation-layout exceptions.
- [WCAG 2.2 Text Spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing): stress values and no-content-loss requirement.
- [WCAG 2.2 Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and [Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html): 4.5:1 / 3:1 thresholds.
- [CSS Fragmentation Level 3](https://www.w3.org/TR/css-break-3/#widows-orphans): normative `widows` and `orphans` behavior at fragment breaks.
- [axe-core API](https://github.com/dequelabs/axe-core/blob/develop/doc/API.md): impact, tags, selectors, and incomplete/manual-review results.
- [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots): reproducible screenshot baselines and environment constraints.
