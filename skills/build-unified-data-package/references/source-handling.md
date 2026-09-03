# Source handling

Read only the section matching the source.

## CSV and TSV

- Detect encoding and delimiter; record non-default choices.
- Preserve original text before casting. Do not let readers coerce IDs or long integers.
- Treat headers, footers, totals, notes, and repeated headings as layout, not records.
- Record the header row and source row numbering convention used by `row_uid`.

## Excel

- Inventory every sheet, hidden sheet, named range, merged area, formula column, and filtered row.
- Decide whether truth is the formula expression or cached value. Record the choice as `excel_formula_mode: formula|cached`; the bundled builder defaults to `formula` so an absent cached value cannot silently erase a formula.
- Do not treat formatting, comments, or merged titles as data unless required.
- Separate tables with different grains even when they share one sheet.

## JSON, JSONL, XML, APIs, and databases

- Preserve the exact query, endpoint, pagination, snapshot time, parameters, and authentication scope without copying secrets.
- Flatten only stable objects. Keep repeated child objects in child tables rather than duplicating parent facts.
- Use source primary keys for locators when stable; otherwise use record index plus immutable source hash.

## PDFs, documents, images, audio, and video

- Store the binary as `data/assets/<sha256>.<ext>` and create an asset index table.
- Derived OCR, transcription, layout, object, or metadata tables must link back through `asset_uid`, page/time/region locators, and extraction method.
- Distinguish source text, extracted text, normalized text, and model-generated summaries.
- Preserve page number, bounding box, time offsets, language, and confidence when available.

## Graph data

Use at least node and edge tables. Node rows identify entities; edge rows identify directed or undirected relations and declare source/target foreign keys, relation type, validity interval, and provenance. Hyperedges require an edge table plus an edge-member table.

## Embeddings and vectors

Store `source_row_uid`, vector dimension, element type, model/provider, exact model revision when known, generated time, normalization, and distance metric. Treat embeddings as derived artifacts. Never mix vectors from different model revisions in one logical vector column without a model identifier.

## Geospatial

Declare CRS, axis order, geometry type, and coordinate precision. Prefer a recognized geospatial Parquet profile when all target engines support it; otherwise store WKB plus explicit CRS metadata.

## Unsupported or proprietary formats

Do not improvise a lossy parser. Preserve and hash the original, identify an authorized extractor, capture its version and parameters, validate extraction against representative samples, and package both the asset index and derived tables. If extraction cannot be verified, state that limitation and do not claim full conversion.
