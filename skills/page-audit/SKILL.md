---
name: page-audit
description: Audits Baslide01 HTML pages and slide decks for broken assets, missing home navigation, TIANSIGHT script paths, slide roots, and layout-token violations. Use when the user asks to 审计页面, page audit, review slides, check HTML decks, or verify every page can return home.
---

# Page Audit Agent

Dedicated auditor for Baslide01 HTML surfaces. Do not generate new decks in this skill; only inspect and report.

## Live console

Open `/audit/` (or `http://127.0.0.1:<port>/audit/?run=1`). That page is the visual agent: it reads `catalog.json` and checks every listed HTML surface. Deck numbers live in `decks.json` and `/decks/` (D01–D06).

If the local server is not up: `bash scripts/dev-up.sh`.

## When invoked in chat

1. Confirm the gallery server is listening (documented ports 8765 / 8080 / 5173).
2. Fetch `/catalog.json` and every `surfaces[].path`.
3. For each HTML page, run the checklist below.
4. Return a table: page · grade · findings. Failures first.
5. Do not “fix later” silently — if the user asked for audit only, stop after the report. If they asked to fix, patch fails then re-run `/audit/?run=1`.

## Checklist (every HTML page)

| Code | Fail if |
|---|---|
| HTTP | Status not 200 |
| HOME | Path is not `/` and there is no 首页 chrome (`baslide-chrome.js` or `a[href=/]`) |
| JS | TIANSIGHT demo/original missing `src/TIANSIGHT.{registry,schema,viz,demo,app}.js` |
| ASSET | Same-origin `script[src]` / `img[src]` / `link[href]` 404 |
| ROOT | No `#deck`, `.slide`, `#app`, or `.hero` |
| TITLE | Empty `<title>` (warn) |
| TOKEN | TIANSIGHT pages using Inter / purple gradients / missing `--gold:#76551F` (warn) |
| LAYOUT | Invented CSS classes not in the chosen template (warn) |

Chrome is injected by `scripts/serve.py` on every `.html` response. A page that only works via `file://` without chrome is still a fail for workshop serving.

## Report format

```
# Page audit
- pages: N · pass: A · warn: B · fail: C

## FAIL  /path
- HOME  没有返回首页
- ASSET img 断链 ./images/foo.svg

## WARN  /path
- TITLE 缺少 title
```

Open the live agent when done: paste `http://127.0.0.1:<port>/audit/`.
