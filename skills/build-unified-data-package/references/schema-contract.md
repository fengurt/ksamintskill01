# Schema and build contract

Use this reference when mapping source fields or authoring `build.yml`.

## Table schema

Each `schema.yml` table contains:

```yaml
name: sales_orders_order
title_zh: 销售订单
description: 成交订单明细，不含取消订单
grain: 一行=一个订单明细行
primary_key: [row_uid]
business_keys: [order_id, line_id]
foreign_keys:
  - columns: [customer_id]
    references: crm_customer_customer
    referenced_columns: [customer_id]
columns: []
```

The primary key is a table constraint, not merely documentation. `row_uid` is always unique. Declare business keys even when `row_uid` is the physical primary key.

## Column schema

Required keys:

```yaml
- name: net_amount_cny
  title_zh: 订单净额
  description: 含税订单金额减去订单级优惠后的金额
  physical_type: decimal(18,2)
  logical_type: monetary_amount
  semantic_role: measure
  unit: CNY
  nullable: false
  null_means: null
  sensitivity: none
  derived: true
  formula: gross_amount_cny - discount_amount_cny
  transform_ref: src/transform.py#derive_net_amount
  constraints:
    minimum: "0.00"
```

Allowed `semantic_role` values are `identifier`, `foreign_key`, `dimension`, `measure`, `timestamp`, `label`, `text`, and `asset_reference`. Use `logical_type` for business meaning and `physical_type` for exact storage.

Recommended physical types:

- `string`, `boolean`;
- `int32`, `int64`;
- `decimal(p,s)` for exact numeric values;
- `float32`, `float64` only for genuinely approximate measurements;
- `date32`;
- `timestamp[ms,tz=Asia/Shanghai]` or another explicit IANA timezone;
- `list<string>` for intentionally nested values when consumers support it.

Do not infer identifiers from digits. Postal codes, account numbers, phone numbers, device codes, and classification codes remain strings.

## Null contract

`nullable` answers whether null is permitted. `null_means` answers what a permitted null means. `source_null_tokens` records exact source representations that were converted to null. Never silently combine “not applicable”, “not collected”, “suppressed”, and “failed measurement” when their distinction matters; model a reason/status field.

## Derivation contract

A derived column must provide a formula sufficient for independent review. For domain algorithms, also provide:

- input columns and units;
- algorithm/version;
- parameter values;
- rounding policy, if any;
- transform entrypoint;
- tests or reconciliation totals.

LLM-generated classifications, summaries, extractions, or embeddings additionally record model/provider, exact model revision when available, prompt/template hash, decoding parameters, and confidence or review status. Do not present model output as source truth.

## Build configuration

The bundled CLI consumes `assets/build-config.template.yml`. Paths are resolved relative to the config file. Map columns explicitly; `include_unmapped` defaults to false. A source column omitted from the mapping is intentionally excluded and should be mentioned in assumptions when material.

For complex transformations, generate a stable staging table through a script and list both the raw source and staging artifact in provenance. Do not manually edit final Parquet or CSV files.
