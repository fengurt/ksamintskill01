# Lossless levels

"Lossless" is meaningless until you say which layer. A workbook carries up to six layers; most export paths keep one. fileye reports which layers a file actually contains so a conversion can be declared lossless *at a level* and proven with `roundtrip_xlsx.py`.

## The layer model

| Level | Spreadsheet (xlsx/xlsm/ods) | Document (docx/odt) | PDF |
|---|---|---|---|
| L0 bytes | the file itself | the file itself | the file itself |
| L1 | cached cell values with their types (number/date/bool/text/error) | body text in reading order | extracted text (only if a text layer exists) |
| L2 | formulas, defined names, array/shared formula groups | headings, tables, headers/footers, lists, footnotes | page structure, bookmarks, links |
| L3 | layout: merged ranges, hidden rows/cols/sheets, number formats, column widths, freeze panes, sheet state | tracked changes, comments, revisions | incremental updates (edit history) |
| L4 | objects: charts, images, comments, pivot caches, tables, data validation, conditional formatting, hyperlinks | images, drawings, embedded objects | images, form fields |
| L5 | code and links: VBA, external workbook references, Power Query / connections | VBA, dynamic fields | JavaScript, embedded files |

L0 is always present and is the only level that guarantees every other one. Storing the original content-addressed makes the *system* lossless even when every converter is lossy.

## What each export path keeps (spreadsheets)

| Target | L1 values | L2 formulas | L3 layout | L4 objects | L5 code/links |
|---|---|---|---|---|---|
| CSV / TSV | yes, but types collapse to text; dates become whatever the formatter printed; leading zeros and precision may be lost | no | no | no | no |
| JSON (array of rows) | yes; types survive if the converter emitted them, dates need an explicit convention | only if the converter stored them separately | no | no | no |
| Parquet | yes with typed columns | no | no | no | no |
| Pandas / DataFrame round-trip | yes | no | no | no | no |
| ndjson from `roundtrip_xlsx.py extract` | yes | yes | number formats only | no | no |
| openpyxl load → save | yes | yes | mostly (widths/panes/styles kept) | partially — charts and images are dropped by openpyxl unless specifically handled | VBA only with `keep_vba=True`; external links kept as references |
| Excel → Excel "Save As" | yes | yes | yes | yes | yes, but sha256 changes every time (new zip timestamps, new revision counter) — content_hash stays stable |

Dates deserve a specific warning: Excel stores them as serial numbers with a number format. A CSV export prints the formatted string; a Parquet export needs the converter to recognise the format and emit a date type. Either way the serial value is gone. Values with formulas store the last cached result; if the workbook was saved with calculation off, the cached value can disagree with the formula. Compare both.

## Declaring a conversion lossless

State the level, then prove it:

1. Read `lossless.layers_present` from the manifest.
2. Choose the level the target must preserve. If the file has L2 and the target is CSV, the honest statement is "L1 preserved; 85 formulas dropped" — say the number.
3. Run `roundtrip_xlsx.py compare original converted`. Report the verdict table verbatim. `not_checkable` means the target format cannot carry that layer; it is not a pass.
4. Record the verdict beside the manifest so a later reader knows what the derived artefact is good for.

## Cheap versus full preservation — the trade-off

- **Values only (L1)**: fastest, smallest, works with every downstream tool. Loses the logic that produced the numbers; historical workbooks become unexplainable.
- **Values + formulas (L1–L2)**: one extra table of (sheet, cell, formula). Preserves how numbers were derived. Roughly doubles extraction cost; storage is still small.
- **Full (L0 + L1–L5 inventory)**: original bytes plus a normalised cell table plus a layout/object inventory. Any question about the source can be answered later. Highest parsing cost; storage is dominated by L0, which is cheap.

For an archive that will be queried by programs and AI agents, keep L0 for everything, extract L1 for everything, extract L2 wherever `layers_present` includes it, and leave L3–L5 as an inventory (counts and presence flags) until a consumer needs them.
