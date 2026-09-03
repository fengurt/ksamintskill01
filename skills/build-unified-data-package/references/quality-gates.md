# Quality gates

Run automated validation first, then perform this semantic review.

## Release-blocking checks

- Package and table names follow the contract.
- Every table has exactly one declared grain and no mixed total/detail rows.
- `row_uid` is non-null, unique, reproducible, and traceable to a source locator.
- Business keys and foreign keys have the intended meaning; join cardinalities were measured.
- Every output field has source or derivation lineage.
- IDs remain strings and preserve leading zeros and long digits.
- Units, currency, percent convention, timezone, precision, and CRS are explicit where applicable.
- Nulls are not placeholder values; null reasons are not collapsed when materially different.
- Decimal truth has no display rounding.
- Source, code, lock, data, and asset hashes reconcile.
- Every Parquet round-trip difference count is zero.
- `README.md` conclusions are supported by packaged truth and clearly separate fact, inference, and limitation.
- License, classification, per-field sensitivity, and distribution scope permit the intended handoff.

## Reconciliation

For financial or operational datasets, compare source and output totals for stable control measures such as record count, amount, quantity, and distinct business keys. Record expected differences caused by exclusions, deduplication, or normalization. A zero cell round-trip proves encoding fidelity after transformation; it does not prove that the transformation was correct.

## Sampling

Inspect representative rows from the beginning, middle, and end; null-heavy rows; maximum/minimum values; non-ASCII text; leading-zero IDs; dates near boundaries; duplicate keys; and every transformation branch. Use a fixed seed for random samples and record it.

## Warning policy

A warning may ship only if it does not change the meaning of the stated use, appears in README, and has an owner or resolution path. Unknown grain, unknown unit, unmatched foreign keys above an accepted threshold, unverifiable formulas, checksum failures, or unauthorized sensitive data are errors, not warnings.
