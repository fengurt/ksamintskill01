# Unified Data Package v1: normative profile

Keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

## Package contract

The directory MUST contain `README.md`, `manifest.json`, `schema.yml`, at least one `data/*.parquet`, a corresponding `data/*.csv` view, and `src/`. `data/assets/` MAY contain non-tabular payloads. The package name MUST match `^[a-z0-9]+(?:_[a-z0-9]+)*_v[0-9]+(?:_[0-9]+){0,2}$` and SHOULD follow `<domain>_<subject>_<action>_v<version>`.

`package_version` is the dataset release. `spec_version` is the standard release. They MUST NOT be conflated.

## Ten rules

1. **One package, one coherent subject; one table, one grain.** Every table declares `grain` as “one row = …”.
2. **Stable machine names.** Table names follow `<domain>_<subject>_<grain>`; table and field names are lowercase snake case. Human names belong in the schema.
3. **Row-level lineage.** Every row has a non-null, unique `row_uid` in `<source-sha256-first-8>:<percent-encoded-source-part>:<percent-encoded-source-locator>` form. The full source SHA-256 remains in the manifest. A stable business/entity key is separate from `row_uid`.
4. **Explicit numeric semantics.** Conventional unit suffixes are `_m`, `_km`, `_cnt`, `_cny`, `_pct`, `_score`, and `_year`. Other numeric measures are allowed only when `schema.yml` declares an unambiguous `unit`; currency additionally declares currency code, and percent declares whether values are 0–100 or ratios are 0–1.
5. **Identifiers are strings.** Fields with semantic role `identifier` or `foreign_key`, and names ending in `_id`, are stored as strings.
6. **Null is not a placeholder.** Zero, empty string, hyphen, “无”, and “未知” MUST NOT stand in for null. Each nullable field declares `null_means`; source tokens converted to null are recorded.
7. **Time is ISO 8601.** Dates are `YYYY-MM-DD`; timestamps include an offset. The package declares an IANA timezone and each temporal field declares precision and semantics.
8. **Derivations are reproducible.** Every derived field declares `derived: true`, a reviewable formula or algorithm, and a transform reference when implementation exceeds a simple expression.
9. **Truth is exact.** Parquet is truth, uses Zstandard level 3, and does not round for display. Decimal measures use Parquet `DECIMAL`, not binary floating point when exactness is required. CSV is not truth.
10. **Release is gated.** The manifest records full source hashes, output artifact hashes, row/column counts, normalized content hashes, and round-trip differences. Distribution requires `validation.status=pass`, `errors_cnt=0`, and all `roundtrip_diff_cells=0`.

## Determinism

“Same result” means that the same source bytes, configuration, code, dependency lock, parameters, ordering, and random seeds produce the same schema and normalized content hash. Byte-identical Parquet output is desirable but not required across different writer versions. `built_at` is intentionally volatile and is excluded from normalized content identity.

## Truth and views

- Parquet MUST preserve logical types and nulls.
- CSV MUST use UTF-8; a BOM MAY be used for spreadsheet compatibility.
- CSV formula-like string cells beginning with `=`, `+`, `-`, or `@` SHOULD be escaped for safe viewing. This does not alter Parquet truth.
- If a full CSV duplicate is impractical, `csv_mode: preview` MUST identify a deterministic selection rule and row count.

## Machine-validation boundary

Syntactic validation does not prove semantic correctness. A conforming release therefore has two gates:

1. automated structure, type, constraint, checksum, and round-trip checks;
2. semantic review of grain, key meaning, formulas, joins, conclusions, license, and sensitivity.

## Agent-native extensions

The following fields are required for professional agent interchange even though consumers that implement only the minimal v1 manifest may ignore them:

- package: `package_version`, `profiles`, `purpose`, `classification`, `license`;
- table: `primary_key`, `foreign_keys`, `content_sha256`, `csv_mode`;
- column: `description`, `logical_type`, `semantic_role`, `nullable`, `null_means`, `sensitivity`;
- build: entrypoint, code hash, dependency lock hash, parameters, and random seed;
- artifacts: relative path, media type, bytes, and SHA-256.

Unknown metadata fields MUST be preserved by tooling.

The formal machine contracts are [manifest.schema.json](manifest.schema.json) and [schema.schema.json](schema.schema.json). Conforming validators SHOULD apply them before deeper data checks.
