---
name: build-unified-data-package
description: Convert raw tabular, document, media, graph, vector, geospatial, or mixed datasets into a reproducible Unified Data Package with Parquet truth tables, human CSV views, machine-readable schema and manifest, row-level lineage, source and artifact hashes, deterministic build scripts, and release-gating validation. Use when an agent must clean, normalize, package, audit, hand off, or make data AI/agent-native; do not use for analysis-only requests that do not need a reusable data deliverable.
metadata:
  version: "1.0.0"
  standard: "unified-data-package/v1"
  compatibility: "Agent Skills; Python 3.10+; Codex, Claude Code, Cursor"
---

# Build Unified Data Package

Produce a package that a new human or agent can understand, verify, join, and rebuild without asking the producer what the data means.

## Non-negotiable outcome

Every released package must contain:

```text
<package_name>/
  README.md
  manifest.json
  schema.yml
  data/*.parquet
  data/*.csv
  src/
```

Parquet is truth. CSV is a human view. Never invent missing values, units, grain, formulas, keys, conclusions, or provenance. Record justified inferences as assumptions and unresolved semantic questions as limitations.

Read [references/specification.md](references/specification.md) before designing or validating a package. It is normative.

## Workflow

### 1. Preserve and inspect

- Treat all inputs as read-only. Hash the original bytes before transformation.
- Resolve all relevant files, sheets, tables, database queries, URLs, and asset objects.
- Run `python3 <skill-dir>/scripts/udp.py inspect <inputs...>` for supported local files.
- Identify the package purpose, table grain, source locator, business keys, relations, units, time semantics, null semantics, derivations, sensitivity, and license.
- Ask only when a missing decision would materially change meaning. Otherwise choose the least-assumptive interpretation and disclose it.

Read [references/source-handling.md](references/source-handling.md) when the source is not a simple CSV/TSV/Excel/JSON/JSONL/Parquet table or when formulas, merged cells, OCR, databases, APIs, graphs, vectors, geospatial data, or media are involved.

### 2. Design the contract before transforming

- Copy `assets/build-config.template.yml` and complete it.
- Use one package per coherent subject and one table per grain.
- Give every table an explicit primary key or document why only `row_uid` is available.
- Declare foreign keys; do not rely on similar column names.
- Map every output column explicitly. IDs are strings. Numeric physical types require a unit in `schema.yml`; conventional suffixes remain preferred but the schema is authoritative for non-listed units.
- Keep row lineage separate from stable entity identity. `row_uid` locates the source observation; business IDs identify real entities across source versions.
- Put sensitive-data handling and allowed-use constraints in the contract before any external transfer.

Read [references/schema-contract.md](references/schema-contract.md) while authoring the mapping. Read [references/profiles.md](references/profiles.md) only for non-tabular or mixed data.

### 3. Transform deterministically

- Prefer the bundled builder for supported mappings:

  ```bash
  python3 <skill-dir>/scripts/udp.py build --config <build.yml> --output <new-parent-directory>
  ```

- The output target must be new. Do not overwrite a released package; create a new package version.
- For complex domain logic, add a focused transform under the generated package's `src/`, pin its dependencies, make inputs and parameters explicit, and run it before the final builder. Do not hide transformations in an interactive notebook.
- Preserve source order unless sorting is part of the declared transformation. Pin random seeds for sampling, matching, inference, or model calls.
- Do not round truth values. Store money as decimal with explicit precision and scale.
- Put binary originals or derived media under `data/assets/` by content hash and index them from a Parquet table.

### 4. Validate independently

Always run:

```bash
python3 <skill-dir>/scripts/udp.py validate <package-directory> --json
```

Then apply the semantic review in [references/quality-gates.md](references/quality-gates.md). The script verifies structure and machine-testable invariants; the agent must still verify that grain, definitions, formulas, joins, conclusions, privacy, and license are substantively correct.

Do not distribute a package when:

- validation status is not `pass`;
- `errors_cnt` is nonzero;
- any `roundtrip_diff_cells` is nonzero;
- an input, transformation, unit, key, or formula needed to reproduce truth is missing;
- sensitive data would be released beyond its allowed scope.

Warnings may remain only when they are visible in `README.md` and do not undermine the stated use.

### 5. Deliver the package

- Archive the complete package directory without changing its internal root name.
- Report package name/version, tables and grains, row counts, validation result, major assumptions, and limitations.
- Give the user the package, not loose output files.
- If the package is too large for a complete CSV mirror, produce a deterministic preview CSV, set `csv_mode: preview`, and state the preview rule in README and manifest.

## Source support boundary

The skill can package any data, but no generic script can correctly interpret every proprietary or domain-specific format. For unsupported inputs, preserve the original as a hashed asset, use an appropriate extractor within the user's authorization, package extracted facts as separate derived tables, and record the extractor, version, parameters, and source relationship. Never describe an indexed asset as semantically converted when it was only copied.

## Platform portability

The core skill follows the open Agent Skills structure and avoids platform-only syntax. For installation paths and invocation in Codex, Claude Code, and Cursor, read [references/platforms.md](references/platforms.md).
