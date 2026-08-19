# Deck grammar v2

Distilled from `deck-grammar-v2-review-and-benchmark.html`, supplied for the
2026-08-19 update. This file records the operative contract; it is not a copy
of the review document.

## Page identity

A deck is an argument graph rendered as a page sequence. A page authors:

- `node`: one of `frame situation complication question claim evidence back-matter`, plus its graph edge;
- `claim`: structured subject, measure, direction, magnitude, period, scope, and rendered assertion;
- `intent`: `ranking magnitude part-to-whole change-over-time deviation distribution correlation flow geo`;
- `evidence`: a set of `number table chart diagram map image text embed` blocks.

The pipeline computes the data profile, chooses an encoding and layout preset,
and retains the solver trace. The legacy 12 template ids remain renderer
presets, not a competing taxonomy.

## Cross-cutting requirements

Every data-bearing evidence block carries `dataset`, `query_hash`, `as_of`,
`transform_chain`, and `owner`. The renderer uses one 16:9 aspect parameter,
a 12×8 grid, a safe area, a named type scale, tabular numbers, exactly one
emphasis target on chart evidence, direct labels, and a static fallback for
embeds.

## Gate order

1. schema and references;
2. provenance and cross-page consistency;
3. argument graph;
4. claim/evidence rhetoric;
5. measured layout fit and rhythm;
6. contrast, type floor, greyscale redundancy, static fallbacks, and PDF geometry.

Invariants block generation or export. Tunable defects and advisories live in
`design/policy-v2.json`; they do not become unowned constants in code.
