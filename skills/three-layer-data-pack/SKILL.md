---
name: three-layer-data-pack
description: Convert raw files of any format (xls, xlsx, csv, json, md, pdf, png, jpg, Google Docs/Sheets, ODF) into a lossless three-layer agent data pack — provenance, query layer (DuckDB/SQLite), orientation catalog. Use when the user asks to build an agent pack, merge/normalize business data exports, make data "agent-ready", or convert spreadsheets/PDFs/scans into a queryable database without data loss.
---

# Three-Layer Agent Data Pack

Turn a folder of raw files into a pack a fresh agent can query correctly **without ever opening the source files**. Success test: given only the pack folder, can an agent answer a business question and avoid the known traps?

## The three layers

| Layer | Answers | Artifacts |
|---|---|---|
| 1. Provenance | "What was the source, exactly?" | untouched source files + `sources.jsonl` (sha256, bytes, row counts) + `original` JSON on every row |
| 2. Query | "What were sales by store/day?" | `pack.duckdb` (primary) + `pack.sqlite` (compatibility) + one JSONL per table |
| 3. Orientation | "What am I looking at? Which queries are valid?" | `catalog.json` + short `README.md` |

Format is never the fix for data loss — parsing is where loss happens. Keep every original cell; type-cast into separate columns.

## Output layout

```
<dataset>/agent/
├── catalog.json          # orientation: grain, joins, traps, counts, sources
├── README.md             # 5-line human entry with example SQL
├── pack.duckdb           # query this (columnar, small)
├── pack.sqlite           # same tables; universal compatibility
├── <table>.jsonl         # one per grain, lossless, portable
├── sources.jsonl         # file-level provenance
├── stores.json           # (or equivalent dimension table)
└── build_agent_db.py     # the build script, checked in for reproducibility
```

Keep raw files where they are; never modify them. If a previous wide-union dump exists (`merged/`), leave it but point its README at `agent/`.

## Workflow

```
- [ ] 1. Inventory: list files, sha256 every file, detect byte-identical duplicates
- [ ] 2. Convert non-native formats to parseable form (see per-format table)
- [ ] 3. Identify grains: what is one row? one ticket / one line item / one txn / one menu item
- [ ] 4. Parse losslessly: every cell into `original`, typed copies into snake_case columns
- [ ] 5. Split PII into its own table; hash identifiers in the public table
- [ ] 6. Write JSONL + SQLite + DuckDB + catalog.json + README
- [ ] 7. Verify (checklist below) — do not skip
```

## Per-format ingestion

| Format | Method | Trap |
|---|---|---|
| xlsx | `openpyxl` `read_only=True` | Some POS/SaaS exports yield **0 rows** in read_only mode — fall back to raw XML iteration over `xl/worksheets/*.xml` + sharedStrings via `zipfile` + `ElementTree`. Header is often row 2–3 (row 1 = title, row 2 = export-filter string; save both into `sources`) |
| xls (binary) | `soffice --headless --convert-to xlsx`, then as xlsx | Don't parse xls directly |
| csv | sniff encoding (`utf-8-sig`, `gb18030`) and delimiter before reading | Excel-exported CSV from Chinese systems is usually GB18030 |
| json / jsonl | already structured; keep verbatim as `original`, add typed projection | Don't flatten nested objects destructively |
| md / txt | keep whole file in provenance; chunk by heading into a `narratives` table if queryable text is needed | — |
| pdf (digital text) | `pdfplumber` for text/tables | Check extraction is non-empty; scanned PDFs return blanks |
| pdf (scanned) / png / jpg | OCR with a VLM pipeline (MinerU API if available — see `mineru-api` skill), then cross-check numbers with a second vision pass | Never trust single-pass OCR for prices/quantities |
| Google Docs/Sheets | export first (Sheets → xlsx, Docs → md/docx), then treat as that format | — |
| ODF (ods/odt) | `soffice --headless --convert-to xlsx/docx` | — |

## Losslessness rules

1. Every row carries `original`: the full source-row object with **original-language keys** and raw values (including sentinels like `"--"` and malformed dates).
2. Cells under blank/duplicate headers go to `original._extra_cells` with column index — never dropped.
3. Typed columns are a projection, not a replacement: ISO dates (`YYYY-MM-DD HH:MM:SS`), numeric parse strips `,` `元` `¥`; unparseable typed value → SQL `NULL`, raw stays in `original`.
4. Sentinels `"" "--" "-" "—"` → `NULL` in typed columns only.
5. Non-standard raw values (e.g. `20256.5.1`) are kept verbatim in `original`; record the interpretation in `catalog.json`.
6. Byte-identical duplicate files: ingest once, record the copy in `sources` with `duplicate_of`.

## Identity and joins

- Stable row id: `{source_id}:{row_index}` (add `:{sheet}` when one source has multiple sheets).
- Every row gets `store_key` (or the equivalent entity key), `source_id`, `row_index`.
- Document every join in `catalog.json` as an explicit equality, e.g. `item_sales.store_key + order_no = orders.store_key + order_no`.
- Pre-build views for the obvious joins (`v_order_items`, `v_store_daily`) so agents don't reinvent them.

## PII

Split into `<table>` (public) and `<table>_pii`: names/phones/emails only in the `_pii` table; public table gets `phone_hash` (sha256) + `has_name`. Strip PII keys from the public `original` too. Never print PII values in chat or commit them to git. Note the split in `catalog.json`.

## catalog.json template

```json
{
  "id": "<dataset>-agent-<period>",
  "query_files": {"duckdb": "pack.duckdb", "sqlite": "pack.sqlite"},
  "grain": {"orders": "one POS ticket", "item_sales": "one sold line; join orders on store_key + order_no"},
  "joins": ["item_sales.store_key + order_no = orders.store_key + order_no"],
  "lossless": "Every source cell is in original JSON. Typed columns use ISO dates and SQL NULL instead of '--'.",
  "period_note": "<date-range mismatches and orphan keys go here — this is the most valuable field>",
  "counts": {"orders": 11965},
  "views": ["v_order_items"],
  "sources": [{"source_id": "...", "filename": "...", "sheet": "...", "sha256": "...", "rows": 0, "duplicate_of": null, "export_filter": "<the POS export-filter string from row 2>"}]
}
```

`period_note` / traps must state anything that makes a naive query wrong: coverage gaps between tables ("orders run through July, line items stop June 30"), orphan foreign keys, fields populated only on the first row of a group.

## Build both databases

SQLite first (stdlib, universal), then DuckDB from it:

```python
con = duckdb.connect("pack.duckdb")
con.execute("ATTACH 'pack.sqlite' AS src (TYPE SQLITE)")
con.execute("CREATE TABLE orders AS SELECT * FROM src.orders")
```

Trap: DuckDB enforces column types on ATTACH-copy — a text value like `时价` in a REAL column aborts the copy. Ensure numeric parse returns `NULL` (raw preserved in `original`) for unparseable values. Recreate views natively in DuckDB (views don't transfer). Store `original` as a JSON string column; index the join keys in SQLite.

## Verification checklist (mandatory)

```
- [ ] Row counts per table match source parse counts, and per-entity splits match
- [ ] min/max dates per table; record coverage mismatches in catalog period_note
- [ ] Orphan-join count (lines without parent); record count + example pattern in catalog
- [ ] Zero NULL `original` columns
- [ ] PII scan: public JSONL/tables contain no raw phone/name keys (grep the JSONL)
- [ ] DuckDB and SQLite return identical counts
- [ ] Re-run build script from scratch → identical counts (reproducibility)
```

## Reference implementation

A complete build script (POS xlsx via raw XML, PII split, dual DB, catalog):
`/Users/af/Public/APUCH/IPTrust/TableAI/education01/边江/侍天/韵主菜牌/agent/build_agent_db.py`
