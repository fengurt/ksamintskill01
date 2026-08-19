# Style C · Screenshot Backgrounds

This directory is **intentionally empty** for v1.

## Why no WebP shipped?

Style C uses Table AI's brand palette:
- background: `#FFFFFF` (pure white)
- ink: `#0A1626` (universe deep blue)
- accent: `#A88B52` (sundial dark gold)

The Skill's `references/screenshot-framing.md` workflow renders product screenshots onto **solid color backgrounds** derived from `--paper` / `--ink` / `--grey-1`. No photographic asset is needed — Table AI's design language is intentionally minimal (white-canvas with hairline borders), not "CleanShot X frame" decorative.

If you want a visible decorative background for hero / closing slides, generate one via the same Tonal-bg or Noise-bg pipeline used by Style A/B. For Style C, prefer:

| File pattern | Use case |
|--------------|----------|
| `style-c-paper-tone.webp` | Optional warm-cream tone over pure white (for hero light page) |
| `style-c-ink-grain.webp` | Optional deep-blue grain over dark slide (for closing) |
| `style-c-gold-thread.webp` | Optional gold thread weave (extremely subtle; for gold-bg alt slide) |

## How to add a background

1. Generate a **2048x1280 px WebP** (or larger).
2. File size ≤ 200 KB.
3. Naming: follow the kebab-case pattern above.
4. Reference it from `references/screenshot-framing.md` (extend the table).
5. Reference it from `references/themes-tableai.md` (in the optional decorative section).

If you don't need these, **leave this directory empty**. Pure white + dark blue is on-brand.
