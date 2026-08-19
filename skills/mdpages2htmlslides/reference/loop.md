# The repair loop — where it lives and why

## What changed from the old `prompts/loop/*.md`

The previous design had 20 prose loop files (`brand.md` plus one per job) and
asked the agent to self-apply them: *"After writing HTML, re-read this file and
patch. Max 3 loops."*

Measured on the delivered 382-page deck, that loop caught **nothing**:

| `brand.md` rule | Actual result |
|---|---|
| "Copy layout from the linked template" | Templates were bypassed entirely |
| "Do not invent CSS class names" | Renderer emitted inline styles instead |
| "Never put `…` on the field" | Never checked |
| "No 孤儿行, no leftover one-line page" | 40 statement pages at 1–3% ink fill |
| "Set data-pack from how much copy the page carries" | 342/382 had no pack at all |

Self-applied prose is the weakest form of enforcement available. An agent that
is already improvising cannot reliably audit its own improvisation, and a rule
with no observable signal attached is a rule that gets skipped under load.

## The three-way split

Every rule now goes to exactly one of three homes, chosen by whether it is
**measurable**, **structural**, or **taste**:

| Kind | Home | Enforced by | Example |
|---|---|---|---|
| Measurable | `scripts/gate_layout.py` | rendering + measurement, exit 1 | fill band, tiny type, ink overflow, md leak, hex literal |
| Structural | `design/page-types.json` | schema validation before render | ≤7 columns, kpi-card cardinality 3–6, claim ≤42 chars |
| Taste | `design/beauty-bar.md` | one human/agent read per deck | "spend your boldness in one place" |

**20 prose files → 1 short taste file + code + data.** Per-type nuance that used
to be prose (`roster.md` saying "last row `.sum` must close") is now a field in
`page-types.json` that the schema gate reads. Data beats prose because data is
checkable.

## Loop shape

```
plan ──▶ gate_schema ──▶ render ──▶ gate_layout ──▶ hard == 0 ? ship
  ▲                                      │
  └──────── apply actions[] ─────────────┘   (max 3 rounds)
```

Two properties make this converge where the old loop did not:

1. **The agent edits the plan, never the HTML.** HTML shape is a pure function
   of the plan, so a repair cannot introduce a new visual defect — it can only
   move content between well-formed pages. The old loop let the agent patch
   HTML, so each repair round could add as many defects as it removed.

2. **The gate emits `actions[]`, not just complaints.** `UNDERFULL` ships with
   `{"op":"densify","hint":"raise pack to air, merge with the neighbouring
   page, or promote a block to fig"}`. A finding without a proposed move is a
   finding the agent will rationalise away.

## Stopping

Three rounds, then stop. A page still failing after three rounds is marked
`needs_human` with its findings attached, and **stays in the deck**, visibly
flagged. It is never silently clipped — clipping is how the last deck shipped
284 `overflow:hidden` boxes and a 0-hard audit.

## The calibration return path

`gate_layout.py --calibrate deck-plan.json` compares each page's `predicted_h`
(from the planner's budget model) against measured `need_h` and writes
`suggested_scale`. Feed that back into `longdoc2mdpages/scripts/budget.py`.

This is the only self-correcting loop in the system: pagination predictions get
better every run instead of staying wrong forever at `chars≤1600`.
