---
name: page-loop
description: Constraint loops for Baslide01 HTML slide generation. Use when generating or revising any slide so the chosen page type and brand skin stay beautiful and on-token. Trigger on 生成幻灯片, loop 提示词, page type, 侍天, Guizang, or after writing HTML decks.
---

# Page loop

Every generated HTML slide must pass **brand loop** then **type loop**. Generate → check → patch. Stop only when checks pass or after 3 iterations (then report remaining fails).

## Files

- Brand: `prompts/loop/brand.md`
- Type: `prompts/loop/<id>.md` (ids from `page-types.json`)
- Registry: `page-types.json` → `types[].loop`

## When generating

1. Pick type id first, then skin. Do not invent an 18th type.
2. Read `prompts/loop/brand.md`.
3. Read `prompts/loop/<type>.md` (or `types[].loop.prompt` + `checks`).
4. Copy the layout at `skins.<skin>.href`. Do not invent CSS classes. TIANSIGHT `chart` / `roster` already encode the bubble and 清单 recipes — start from those filled jobs. Header is one row: transparent 侍天 logo + chip. Set `data-pack` from how much copy the page carries.
5. Set `data-page-type="<id>"`. Omit workshop chrome (`?export=1`).
6. Score every check. Any miss → patch and loop.
7. Complete canvas copy: no `…` on the field, no 孤儿字 / 孤儿行. Paginate. Type scale is secondary.

## Preview

Open `/preview/?type=<id>&skin=<skin>` to see the live template beside the loop prompt.

## Do not

- Mix TIANSIGHT tokens with Guizang classes on one page
- Skip the type loop because “it’s just a draft”
- Treat `/loop 5m` as a substitute for these files — timed loops are optional; these checks are mandatory on every HTML write
