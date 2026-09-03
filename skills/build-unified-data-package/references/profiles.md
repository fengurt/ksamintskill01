# Data profiles

Declare profiles in the manifest. A package may combine them.

| Profile | Truth representation | Required linkage |
| --- | --- | --- |
| `tabular/v1` | typed Parquet table | `row_uid`, grain, keys |
| `document/v1` | asset plus document/page/chunk tables | `asset_uid`, page or character locator |
| `asset/v1` | content-addressed binary plus asset index | `asset_uid`, SHA-256, media type, bytes |
| `vector/v1` | Parquet fixed/list vector column | `source_row_uid`, model, dimension, metric |
| `graph/v1` | node, edge, optional edge-member tables | declared node/edge keys and direction |
| `geo/v1` | compatible geometry encoding plus CRS | geometry type, CRS, axis order |
| `timeseries/v1` | event/observation table | entity key, event time, timezone, sampling semantics |

Profiles extend the core; they do not relax it. Every derived representation keeps provenance to the source observation or asset. When a consumer cannot support a specialized Parquet logical type, use a conservative physical representation and declare the logical type in `schema.yml`.

## Documents and chunks

Chunking is a derived operation. Record tokenizer or segmentation method, chunk size, overlap, page/character offsets, language, and source hash. Do not overwrite document text with a summary.

## Assets

Minimum asset index fields:

```text
row_uid, asset_uid, asset_path, media_type, sha256, bytes_cnt
```

`asset_path` must be package-relative and must not escape the package root. Content-addressed filenames prevent accidental ambiguity but do not replace human titles or source locators.

## AI-generated data

Label model-generated values as derived and record generation lineage. If human review is required, include a review status and reviewer role without embedding personal information unnecessarily.
