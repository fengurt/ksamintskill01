---
name: contrast-audit
description: Audit text and visual contrast across a project. Use for WCAG contrast checks, unreadable HTML, slide/deck legibility, or final accessibility QA on HTML, PDF, PPTX, and images.
---

# Contrast Audit

Find contrast failures without pretending every format offers the same evidence.

## Choose the evidence path

- **HTML**: run `scripts/audit_contrast.py` against files, URLs, directories, or globs. Computed DOM styles are the authoritative automated path.
- **PDF**: render every page, inspect at full size, and use extracted text/graphics metadata only as supporting evidence. Record page numbers for every finding.
- **PPTX**: render every slide, run the presentation format's overflow checks, then inspect text against the actual composed background. Record slide numbers and object ids when available.
- **Images**: inspect the pixels at full size. Use OCR only to locate candidate text; verify contrast against the local background visually or by sampling. Record bounding boxes when available.

Flattened formats cannot reliably reconstruct compositing, gradients, image backgrounds, transparency, or theme inheritance. Label their results **visual review**, not WCAG proof.

## HTML audit

Run from the project root:

```bash
python3 <skill-dir>/scripts/audit_contrast.py . --json-out contrast-audit.json
```

The command discovers HTML recursively, skips dependency/build caches, checks WCAG 2.2 AA by default, prints a compact summary, writes machine-readable JSON, and exits non-zero on failures or unresolved manual review. Use `--help` for URLs, selectors, AAA, waits, and explicit output paths.

Treat these report entries differently:

- `failures`: computed foreground/background pairs below the selected threshold.
- `manual_review`: image/gradient backgrounds, SVG text without an explicit `data-contrast-bg`, canvas, pseudo-content, and other cases where computed CSS is insufficient.
- `errors`: artifacts that were not audited. An error is not a pass.

Fix the shared token or component before patching individual pages. Re-run the same command until failures are zero and every manual-review item has an adjudication.

## Deliverable

Return one concise ledger grouped by artifact and location: observed ratio, required ratio, foreground, background, text sample, confidence, and remediation. Preserve the JSON report when the user asks for a project-wide or repeatable gate.

The audit is complete when every discovered artifact is accounted for, automated HTML failures are zero or explicitly accepted, every flattened-format page/slide/image was visually reviewed, and the final outputs were re-rendered after fixes.
