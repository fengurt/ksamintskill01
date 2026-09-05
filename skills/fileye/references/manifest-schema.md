# fileye manifest schema (v1.0)

One JSON object per file. Every leaf belongs to a trust class: **detected** (computed from bytes), **claimed** (read from filesystem or embedded metadata; editable), **trusted** (stamped by the ingesting host).

```
{
  "fileye": "1.0.0",
  "identity":   { ... },   detected
  "type":       { ... },   detected + one claimed field
  "provenance": { "trusted": {...}, "claimed": {...} },
  "structure":  { ... },   detected, type-specific
  "lossless":   { ... },   detected
  "warnings":   [ ... ]    detected
}
```

## identity

| field | class | computation |
|---|---|---|
| sha256 | detected | SHA-256 over all bytes, 1 MiB chunks. The primary key of the file. |
| size_bytes | detected | byte count |
| blake3 | detected | present only if the `blake3` package is installed; faster alternative key |
| legacy_sha1, legacy_md5 | detected | for matching older inventories only; both algorithms have public collisions, never use for identity |
| content_hash.algorithm | detected | text describing the canonicalisation |
| content_hash.value | detected | xlsx: sha256 over `sheet|coord|type|repr(value-or-formula)` for every non-empty cell, sheets in workbook order, cells in row-major order. text/csv/json/ndjson: sha256 after stripping BOM, converting CRLF/CR to LF, stripping trailing newline. null with `reason` when not computable. |

Two files with equal sha256 are byte-identical. Two files with equal content_hash but different sha256 differ only in packaging (zip timestamps, styles, column widths, encoding of line endings).

## type

| field | class | computation |
|---|---|---|
| detected | detected | magic bytes at offset 0 (tar at 257), then container refinement: zip → OOXML part prefixes / ODF mimetype / jar / apk / epub; RIFF → wav/avi/webp; ftyp → mp4/heic; no signature → text sniff (xml, html, svg, json, ndjson, yaml, markdown, csv, source:ext, text) |
| container | detected | `zip`, `ole2`, `riff` or null |
| mime | detected | lookup from detected |
| claimed_extension | claimed | lowercase extension from the path |
| extension_agrees | detected | whether claimed_extension is in the expected set for detected; null when there is no expectation |

OLE2 files are reported as `ole2:xls`, `ole2:doc` etc. — the suffix is the extension hint, not a proven sub-type.

## provenance.trusted

| field | computation |
|---|---|
| ingested_at | UTC ISO-8601 from the running host's clock at manifest time |
| ingest_host, ingest_os, python | `platform` module |
| fileye_version | script version; re-run manifests when the extractor changes |

This is the only time in the manifest that can be defended. To make it non-repudiable, append `(sha256, ingested_at, previous_entry_hash)` to a log whose each entry hashes the previous one.

## provenance.claimed

`filesystem`: path, filename, fs_mtime, fs_ctime, fs_birthtime (null where the OS does not expose it). All editable with one command.

`embedded` (present for OOXML and PDF): created, modified, creator, last_modified_by, title, revision, application, app_version, company (OOXML `docProps/core.xml` and `app.xml`, plain XML); creationdate, moddate, producer, creator, author, title (PDF info dictionary). Also `zip_entry_time_min/max` — the timestamps on the zip entries themselves, a third independent claim that forgers often forget to align.

A warning is raised when embedded `modified` and `fs_mtime` differ by more than seven days.

## structure (by `kind`)

**spreadsheet** (xlsx/xlsm): sheets, hidden_sheets, defined_names, per_sheet[] {name, dimension, rows, cells, formulas, merged_ranges, hidden_rows, hidden_cols, data_validations, conditional_formats, hyperlinks, has_drawing, has_autofilter, has_sheet_protection}, totals{...}, shared_strings, charts, images, comments_parts, pivot_caches, external_links, tables, has_vba, has_power_query, number_formats_custom. All counts are regex tallies over the XML parts. `rows` counts `<row>` elements, so trailing formatted-but-empty rows are included; `cells` counts `<c>` elements including empty styled cells.

**document** (docx/docm): paragraphs, tables, table_rows, tracked_insertions, tracked_deletions, footnote_refs, hyperlinks, fields, drawings, images, embedded_objects, comments, headers, footers, has_vba, styles_defined, approx_chars.

**presentation** (pptx/pptm): slides, notes_slides, images, charts, embedded_objects, layouts, shapes, has_vba.

**pdf**: pages, objects, is_encrypted, has_acroform, has_javascript, fonts, images, has_text_layer_hint, xref_streams, incremental_updates, pdf_version. Regex over raw bytes; content inside compressed object streams is not counted.

**table** (csv/tsv): encoding, has_bom, line_ending, delimiter (csv.Sniffer over the first 64 KiB), columns, header[], data_rows, empty_rows, ragged_rows, width_histogram (with --full).

**json**: top_level_type, top_level_keys / length, record_keys_union (first 1000 records), max_depth. **ndjson**: records, unparseable_lines, record_keys_union.

**text** (txt, md, xml, html, yaml, svg, source:*): encoding, lines, chars, line_ending, has_bom.

**database** (sqlite): tables[] {name, columns[], rows}, views, indexes. Opened read-only.

**image** (png/jpeg/gif/bmp): width, height, plus bit_depth/color_type for png and has_exif for jpeg.

**archive** (zip and zip-based formats without a structural parser): entries, uncompressed_bytes, compressed_bytes, encrypted_entries, top_level[].

**opaque**: no parser; identity and type only.

## lossless

`layers_present`: list of layer keys present in this file (see lossless-levels.md). `minimum_lossless_store`: fixed text reminding that only content-addressed original bytes are lossless. `conversion_warning`: set when layers above L1 exist.

## warnings

Free-text, one item per finding. Current triggers: empty file; extension/type disagreement; unreadable container; ragged CSV rows; encrypted PDF; PDF without fonts (likely scanned); VBA present; external workbook links; embedded vs filesystem modified-date divergence over seven days.
