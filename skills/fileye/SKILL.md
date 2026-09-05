---
name: fileye
description: Identify, fingerprint and inventory any file before acting on it, so every agent describes the same file the same way. Use this whenever a file is uploaded, discovered, ingested, converted, deduplicated, or handed between agents — Excel/CSV/Word/PDF/JSON/images/archives/databases, anything. Trigger on phrases like "what is this file", "is this the same file", "has this changed", "was the conversion lossless", "index / catalogue / inventory these files", "build a data package", "check file integrity", or any pipeline that stores files for later retrieval. Use it even when the user only says "read this spreadsheet" if the result will be stored, converted, or trusted later.
metadata:
  author: ksamint
  origin: ksamint
  repository: fengurt/ksamintskill01
---

# fileye

fileye gives an agent one standard way to answer four questions about a file before touching its contents:

1. **Which bytes is this?** — identity (sha256), and whether the *data* is the same as another file even when the bytes differ (content hash).
2. **What is it?** — type detected from magic bytes, with the extension recorded as a claim, never as truth.
3. **Where did it come from and when?** — split into *claimed* (filesystem dates, embedded metadata: all editable) and *trusted* (this host's ingest stamp).
4. **What is inside, and what would a conversion lose?** — a structural inventory plus a list of the information layers present (values, formulas, layout, objects, code/links).

The one thing fileye does not do is reconstruct a file from metadata. A hash is a one-way fingerprint; row counts and formula counts are descriptive statistics with endless collisions. Lossless recovery has exactly one source: the original bytes, stored content-addressed. Everything fileye produces is an index around those bytes.

## Protocol

Follow these steps in order whenever a file enters your work.

### Step 1 — Look

```bash
python scripts/fileye.py look <file> --out <file>.fileye.json
```

Produces the manifest (schema in `references/manifest-schema.md`). Read the `warnings` array first, then `type.detected`, then `lossless.layers_present`. For a directory:

```bash
python scripts/fileye.py batch <dir> --out manifests/
```

### Step 2 — Decide trust before using any fact

Every fact sits under one of three keys. Use them accordingly:

| Class | Where it lives | How to treat it |
|---|---|---|
| detected | `identity`, `type.detected`, `structure`, `lossless` | Reproducible from the bytes by anyone; safe to rely on |
| claimed | `type.claimed_extension`, `provenance.claimed.*` | A statement made by the file or the filesystem; record it, never assert it as fact |
| trusted | `provenance.trusted` | As trustworthy as the ingesting host and its clock; becomes evidence only when chained into an append-only log |

When you write about a file to a user or to another agent, say "the file claims it was modified on X" and "it was ingested on Y", not "the file was modified on X". When `type.extension_agrees` is false, use the detected type and say so.

### Step 3 — Store bytes before deriving anything

If the file will be kept, converted, or referenced later, store the original under its sha256 first (`<store>/<sha256[:2]>/<sha256>`) and record the manifest next to it. Derived artefacts (CSV, Parquet, JSON, DB rows) are views; they never replace the original. This is what makes "lossless" true for the whole system regardless of what any converter drops.

### Step 4 — Convert only to a stated level, then prove it

Before converting, read `lossless.layers_present`. Decide which level the target must preserve and say it out loud in your output ("this CSV preserves L1 values only; the 85 formulas and 12 merged ranges in the source are not carried"). For workbooks, run the round trip:

```bash
python scripts/roundtrip_xlsx.py compare <original.xlsx> <converted.xlsx|.ndjson|.csv> [--sheet NAME]
```

Report the verdict per level. `not_checkable` is not a pass. Levels are defined in `references/lossless-levels.md`.

### Step 5 — Verify on every later read

```bash
python scripts/fileye.py verify <file> <file>.fileye.json
```

`bytes_identical: false` with `content_identical: true` means a re-save or metadata edit, not a data change. Both false means the data changed and every derived artefact from the old manifest is stale.

## Writing about a file (output convention)

When summarising a file for a human or another agent, use this order and nothing speculative:

```
<filename> — <detected type>, <size>, sha256 <first 12 chars>
Claims: extension <ext> (agrees / disagrees), created <claimed> by <claimed creator>, modified <claimed>
Ingested: <trusted stamp>
Structure: <the three or four numbers that matter for this type>
Layers present: <from lossless.layers_present>
Warnings: <each warning as its own line, or "none">
```

Numbers come from the manifest; if the manifest could not compute one, say "not inventoried", not a guess.

## Two hashes, two questions

`identity.sha256` answers "are these the same bytes?". `identity.content_hash` answers "is this the same data?" — for workbooks it hashes (sheet, cell, type, value-or-formula) and ignores zip timestamps, styles and column widths; for text-like files it strips BOM and normalises line endings. Deduplicate on content_hash; audit on sha256. Never use md5 or sha1 for either purpose — they are reported only to match legacy inventories.

## Limits to state plainly

- OLE2 files (.xls/.doc/.ppt) are typed by container plus extension hint; sub-type is not proven.
- PDF counts are regex scans of raw bytes; objects inside compressed object streams are invisible. A PDF with no font objects is reported as likely scanned.
- The workbook content hash needs openpyxl; without it the manifest says so and `content_hash.value` is null.
- Structural counts for xlsx/docx/pptx come from the XML parts, so they are exact for what the zip contains but say nothing about rendering.
- Nothing here detects malicious content beyond flagging VBA, external links and PDF JavaScript.

## Reference files

- `references/manifest-schema.md` — every field in the manifest, its trust class and how it is computed.
- `references/lossless-levels.md` — the L0–L5 layer model per file type and what each common export path drops.
- `references/type-detection.md` — magic-byte table and the zip/OLE2 refinement rules, for extending the detector.
