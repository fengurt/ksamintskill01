#!/usr/bin/env python3
"""Build and validate Unified Data Package v1 artifacts.

This CLI intentionally separates judgment from mechanics: an agent or analyst
defines the semantic mapping in YAML; this program performs deterministic I/O,
typing, lineage, hashing, packaging, and machine-testable validation.
"""

from __future__ import annotations

import argparse
import copy
import csv
import datetime as dt
import hashlib
import json
import mimetypes
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import urllib.parse
import zipfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - exercised through CLI failure
    print(
        "Missing dependency. Install scripts/requirements.txt in an isolated "
        f"environment. Original error: {exc}",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


SPEC_VERSION = "unified-data-package/v1"
PACKAGE_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*_v[0-9]+(?:_[0-9]+){0,2}$")
TABLE_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+){2,}$")
FIELD_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
ROW_UID_RE = re.compile(r"^[0-9a-f]{8}:[^:]+:.+$")
DECIMAL_RE = re.compile(r"^decimal\((\d+),(\d+)\)$")
TIMESTAMP_RE = re.compile(r"^timestamp\[(s|ms|us|ns),tz=([^\]]+)\]$")
LIST_RE = re.compile(r"^list<(string|int32|int64|float32|float64)>$")
NUMERIC_TYPES = {"int32", "int64", "float32", "float64"}
UNIT_SUFFIXES = ("_m", "_km", "_cnt", "_cny", "_pct", "_score", "_year")
ID_ROLES = {"identifier", "foreign_key"}
SENSITIVE_NAME_RE = re.compile(
    r"(^|_)(name|phone|mobile|email|address|id_card|passport|ssn|dob|birth|patient|medical)(_|$)",
    re.IGNORECASE,
)


class UDPError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def media_type(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def json_dump(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def yaml_dump(path: Path, value: Any) -> None:
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise UDPError(f"{label} must be a mapping")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise UDPError(f"{label} must be a list")
    return value


def normalized_scalar(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, Decimal):
        return {"$decimal": format(value, "f")}
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return {"$iso8601": value.isoformat()}
    if isinstance(value, bytes):
        return {"$bytes": value.hex()}
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, (list, tuple)):
        return [normalized_scalar(item) for item in value]
    if hasattr(value, "item"):
        return normalized_scalar(value.item())
    return value


def normalized_content_hash(table: pa.Table) -> str:
    digest = hashlib.sha256()
    digest.update(json.dumps(table.column_names, separators=(",", ":")).encode("utf-8"))
    columns = [table.column(i).to_pylist() for i in range(table.num_columns)]
    for row_idx in range(table.num_rows):
        row = [normalized_scalar(column[row_idx]) for column in columns]
        digest.update(b"\n")
        digest.update(
            json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
    return digest.hexdigest()


def roundtrip_diff_cells(before: pa.Table, after: pa.Table) -> int:
    if before.column_names != after.column_names:
        return max(before.num_rows, after.num_rows) * max(before.num_columns, after.num_columns)
    diff = abs(before.num_rows - after.num_rows) * before.num_columns
    common_rows = min(before.num_rows, after.num_rows)
    for idx in range(before.num_columns):
        left = before.column(idx).to_pylist()
        right = after.column(idx).to_pylist()
        for row_idx in range(common_rows):
            if normalized_scalar(left[row_idx]) != normalized_scalar(right[row_idx]):
                diff += 1
    return diff


def arrow_type(type_text: str) -> pa.DataType:
    simple = {
        "string": pa.string(),
        "boolean": pa.bool_(),
        "int32": pa.int32(),
        "int64": pa.int64(),
        "float32": pa.float32(),
        "float64": pa.float64(),
        "date32": pa.date32(),
    }
    if type_text in simple:
        return simple[type_text]
    match = DECIMAL_RE.match(type_text)
    if match:
        precision, scale = map(int, match.groups())
        if precision < 1 or scale < 0 or scale > precision:
            raise UDPError(f"Invalid decimal type: {type_text}")
        return pa.decimal128(precision, scale)
    match = TIMESTAMP_RE.match(type_text)
    if match:
        unit, timezone = match.groups()
        ZoneInfo(timezone)
        return pa.timestamp(unit, tz=timezone)
    match = LIST_RE.match(type_text)
    if match:
        return pa.list_(arrow_type(match.group(1)))
    raise UDPError(f"Unsupported physical_type: {type_text}")


def is_numeric_type(type_text: str) -> bool:
    return type_text in NUMERIC_TYPES or bool(DECIMAL_RE.match(type_text))


def source_is_null(value: Any, tokens: list[Any]) -> bool:
    if value is None or value is pd.NA:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    return any(value == token or str(value) == str(token) for token in tokens)


def cast_scalar(value: Any, spec: dict[str, Any], package_timezone: str, null_tokens: list[Any]) -> Any:
    if source_is_null(value, null_tokens):
        return None

    type_text = str(spec["physical_type"])
    parse = spec.get("parse") or {}
    if not isinstance(parse, dict):
        raise UDPError(f"parse for {spec.get('name')} must be a mapping")

    if type_text == "string":
        result = str(value)
        if parse.get("strip"):
            result = result.strip()
        if parse.get("unicode_normalization"):
            result = unicodedata.normalize(str(parse["unicode_normalization"]), result)
        return result

    if type_text == "boolean":
        if isinstance(value, bool):
            return value
        truthy = {str(v).casefold() for v in parse.get("true_values", ["true", "1", "yes", "y", "是"])}
        falsy = {str(v).casefold() for v in parse.get("false_values", ["false", "0", "no", "n", "否"])}
        folded = str(value).strip().casefold()
        if folded in truthy:
            return True
        if folded in falsy:
            return False
        raise UDPError(f"Cannot parse boolean value {value!r} for {spec.get('name')}")

    text = str(value).strip()
    thousands = parse.get("thousands_separator")
    if thousands:
        text = text.replace(str(thousands), "")

    if type_text in {"int32", "int64"}:
        try:
            number = Decimal(text)
        except InvalidOperation as exc:
            raise UDPError(f"Cannot parse integer value {value!r} for {spec.get('name')}") from exc
        if number != number.to_integral_value():
            raise UDPError(f"Non-integral value {value!r} for {spec.get('name')}")
        return int(number)

    if type_text in {"float32", "float64"}:
        try:
            return float(text)
        except ValueError as exc:
            raise UDPError(f"Cannot parse float value {value!r} for {spec.get('name')}") from exc

    decimal_match = DECIMAL_RE.match(type_text)
    if decimal_match:
        precision, scale = map(int, decimal_match.groups())
        try:
            number = Decimal(text)
        except InvalidOperation as exc:
            raise UDPError(f"Cannot parse decimal value {value!r} for {spec.get('name')}") from exc
        quantum = Decimal(1).scaleb(-scale)
        quantized = number.quantize(quantum)
        if quantized != number:
            raise UDPError(
                f"Value {value!r} exceeds declared scale {scale} for {spec.get('name')}; refusing to round"
            )
        digits = len(quantized.as_tuple().digits)
        if digits > precision:
            raise UDPError(f"Value {value!r} exceeds precision {precision} for {spec.get('name')}")
        return quantized

    if type_text == "date32":
        if isinstance(value, dt.datetime):
            return value.date()
        if isinstance(value, dt.date):
            return value
        fmt = parse.get("format")
        try:
            return dt.datetime.strptime(text, fmt).date() if fmt else dt.date.fromisoformat(text)
        except ValueError as exc:
            raise UDPError(f"Cannot parse ISO date {value!r} for {spec.get('name')}") from exc

    timestamp_match = TIMESTAMP_RE.match(type_text)
    if timestamp_match:
        _, timezone = timestamp_match.groups()
        fmt = parse.get("format")
        try:
            parsed = dt.datetime.strptime(text, fmt) if fmt else pd.Timestamp(value).to_pydatetime()
        except (ValueError, TypeError) as exc:
            raise UDPError(f"Cannot parse timestamp {value!r} for {spec.get('name')}") from exc
        target_tz = ZoneInfo(timezone or package_timezone)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=target_tz)
        else:
            parsed = parsed.astimezone(target_tz)
        return parsed

    list_match = LIST_RE.match(type_text)
    if list_match:
        item_type = list_match.group(1)
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise UDPError(f"List value for {spec.get('name')} must be a JSON array") from exc
        if not isinstance(value, (list, tuple)):
            raise UDPError(f"List value for {spec.get('name')} is not a list")
        item_spec = {"name": spec.get("name"), "physical_type": item_type, "parse": parse.get("items", {})}
        return [cast_scalar(item, item_spec, package_timezone, []) for item in value]

    raise UDPError(f"Unsupported physical type {type_text}")


def load_source_table(path: Path, table_cfg: dict[str, Any]) -> pd.DataFrame:
    suffix = path.suffix.lower()
    selector = table_cfg.get("selector")
    header_row = int(table_cfg.get("header_row", 1))
    header_index = header_row - 1
    if header_index < 0:
        raise UDPError("header_row is 1-based and must be at least 1")

    if suffix in {".csv", ".tsv"}:
        delimiter = table_cfg.get("delimiter", "\t" if suffix == ".tsv" else ",")
        encoding = table_cfg.get("encoding", "utf-8-sig")
        return pd.read_csv(
            path,
            sep=delimiter,
            encoding=encoding,
            header=header_index,
            dtype=object,
            keep_default_na=False,
            na_filter=False,
        )
    if suffix in {".xlsx", ".xlsm"}:
        if selector is None:
            raise UDPError(f"Excel source {path} requires a sheet selector")
        formula_mode = str(table_cfg.get("excel_formula_mode", "formula"))
        if formula_mode not in {"formula", "cached"}:
            raise UDPError("excel_formula_mode must be 'formula' or 'cached'")
        return pd.read_excel(
            path,
            sheet_name=selector,
            header=header_index,
            dtype=object,
            keep_default_na=False,
            engine_kwargs={"data_only": formula_mode == "cached"},
        )
    if suffix in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True, dtype=False)
    if suffix == ".json":
        raw = json.loads(path.read_text(encoding=table_cfg.get("encoding", "utf-8")))
        if selector is not None:
            if not isinstance(raw, dict) or selector not in raw:
                raise UDPError(f"JSON selector {selector!r} not found in {path}")
            raw = raw[selector]
        if not isinstance(raw, list):
            raise UDPError(f"JSON table in {path} must resolve to an array of objects")
        return pd.DataFrame(raw)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise UDPError(f"Unsupported tabular source: {path}")


def make_row_uids(
    source_hash: str,
    selector: str,
    frame: pd.DataFrame,
    table_cfg: dict[str, Any],
) -> list[str]:
    encoded_selector = urllib.parse.quote(selector, safe="") or "table"
    source_key = table_cfg.get("source_key")
    if source_key:
        if source_key not in frame.columns:
            raise UDPError(f"source_key {source_key!r} does not exist")
        locators = frame[source_key].tolist()
        if any(value is None or str(value) == "" for value in locators):
            raise UDPError(f"source_key {source_key!r} contains null/empty locators")
    else:
        start = int(table_cfg.get("source_row_number_start", 2))
        locators = list(range(start, start + len(frame)))
    return [
        f"{source_hash[:8]}:{encoded_selector}:{urllib.parse.quote(str(locator), safe='')}"
        for locator in locators
    ]


def schema_column(column_cfg: dict[str, Any]) -> dict[str, Any]:
    result = {key: value for key, value in column_cfg.items() if key not in {"source", "parse"}}
    result["source_field"] = column_cfg.get("source")
    result.setdefault("title_zh", result["name"])
    result.setdefault("description", "")
    result.setdefault("logical_type", result["physical_type"])
    result.setdefault("semantic_role", "dimension")
    result.setdefault("unit", None)
    result.setdefault("nullable", True)
    result.setdefault("null_means", None)
    result.setdefault("sensitivity", "none")
    result.setdefault("derived", False)
    return result


ROW_UID_SCHEMA = {
    "name": "row_uid",
    "title_zh": "行追溯标识",
    "description": "Source-observation identifier derived from source hash, part, and locator.",
    "physical_type": "string",
    "logical_type": "lineage_identifier",
    "semantic_role": "identifier",
    "unit": None,
    "nullable": False,
    "null_means": None,
    "sensitivity": "internal",
    "derived": True,
    "formula": "<source_sha256_first8>:<percent_encoded_source_part>:<percent_encoded_source_locator>",
    "source_field": None,
}


def build_arrow_table(
    frame: pd.DataFrame,
    table_cfg: dict[str, Any],
    source_hash: str,
    selector: str,
    package_timezone: str,
) -> tuple[pa.Table, list[dict[str, Any]]]:
    column_cfgs = require_list(table_cfg.get("columns"), f"columns for {table_cfg.get('name')}")
    if not column_cfgs:
        raise UDPError(f"Table {table_cfg.get('name')} has no columns")
    source_null_tokens = table_cfg.get("source_null_tokens", [""])
    if not isinstance(source_null_tokens, list):
        raise UDPError("source_null_tokens must be a list")

    row_uids = make_row_uids(source_hash, selector, frame, table_cfg)
    arrays: list[pa.Array] = [pa.array(row_uids, type=pa.string())]
    fields: list[pa.Field] = [pa.field("row_uid", pa.string(), nullable=False)]
    schema_columns: list[dict[str, Any]] = [dict(ROW_UID_SCHEMA)]
    seen = {"row_uid"}

    for raw_column_cfg in column_cfgs:
        cfg = require_mapping(raw_column_cfg, "column")
        for key in ("source", "name", "physical_type"):
            if key not in cfg:
                raise UDPError(f"Column mapping missing {key}: {cfg}")
        source_name = cfg["source"]
        output_name = str(cfg["name"])
        if source_name not in frame.columns:
            raise UDPError(f"Source column {source_name!r} missing for output {output_name}")
        if output_name in seen:
            raise UDPError(f"Duplicate output column {output_name}")
        seen.add(output_name)
        if not FIELD_RE.fullmatch(output_name):
            raise UDPError(f"Invalid field name {output_name}")

        type_text = str(cfg["physical_type"])
        target_type = arrow_type(type_text)
        values = [
            cast_scalar(value, cfg, package_timezone, source_null_tokens)
            for value in frame[source_name].tolist()
        ]
        nullable = bool(cfg.get("nullable", True))
        if not nullable and any(value is None for value in values):
            raise UDPError(f"Non-nullable column {output_name} contains null")
        arrays.append(pa.array(values, type=target_type))
        fields.append(pa.field(output_name, target_type, nullable=nullable))
        column_schema = schema_column(cfg)
        column_schema["source_null_tokens"] = source_null_tokens
        schema_columns.append(column_schema)

    metadata = {
        b"unified_data_package.spec_version": SPEC_VERSION.encode("utf-8"),
        b"unified_data_package.table": str(table_cfg["name"]).encode("utf-8"),
        b"unified_data_package.grain": str(table_cfg["grain"]).encode("utf-8"),
    }
    schema = pa.schema(fields, metadata=metadata)
    return pa.Table.from_arrays(arrays, schema=schema), schema_columns


def safe_csv_scalar(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def write_csv_view(table: pa.Table, path: Path, mode: str, preview_rows: int) -> tuple[int, str | None]:
    if mode not in {"full", "preview"}:
        raise UDPError(f"csv_mode must be full or preview, got {mode!r}")
    indices = list(range(table.num_rows))
    preview_rule = None
    if mode == "preview" and table.num_rows > preview_rows:
        head_count = (preview_rows + 1) // 2
        tail_count = preview_rows // 2
        indices = list(range(head_count)) + list(range(table.num_rows - tail_count, table.num_rows))
        preview_rule = f"first {head_count} and last {tail_count} rows in truth order"
    columns = [table.column(idx).to_pylist() for idx in range(table.num_columns)]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(table.column_names)
        for row_idx in indices:
            writer.writerow([safe_csv_scalar(column[row_idx]) for column in columns])
    return len(indices), preview_rule


def build_asset_table(
    assets_cfg: list[Any],
    asset_table_cfg: dict[str, Any],
    config_dir: Path,
    package_root: Path,
) -> tuple[pa.Table, list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    assets_dir = package_root / "data" / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    for idx, raw in enumerate(assets_cfg, start=1):
        cfg = require_mapping(raw, f"asset {idx}")
        source_path = (config_dir / str(cfg["path"])).resolve()
        if not source_path.is_file():
            raise UDPError(f"Asset does not exist: {source_path}")
        digest = sha256_file(source_path)
        suffix = source_path.suffix.lower()
        destination = assets_dir / f"{digest}{suffix}"
        if not destination.exists():
            shutil.copyfile(source_path, destination)
        records.append(
            {
                "row_uid": f"{digest[:8]}:asset:1",
                "asset_uid": f"sha256:{digest}",
                "asset_path": destination.relative_to(package_root).as_posix(),
                "asset_title": cfg.get("title") or source_path.name,
                "media_type": cfg.get("media_type") or media_type(source_path),
                "sha256": digest,
                "bytes_cnt": source_path.stat().st_size,
            }
        )
        sources.append(
            {
                "source_id": cfg.get("source_id", f"asset_{idx:03d}"),
                "file": source_path.name,
                "path": str(cfg["path"]),
                "media_type": cfg.get("media_type") or media_type(source_path),
                "sha256": digest,
                "bytes_cnt": source_path.stat().st_size,
                "rows": 0,
                "cols": 0,
            }
        )

    columns = [
        ROW_UID_SCHEMA,
        {"name": "asset_uid", "title_zh": "资产标识", "description": "Content-addressed asset identifier.", "physical_type": "string", "logical_type": "identifier", "semantic_role": "identifier", "unit": None, "nullable": False, "null_means": None, "sensitivity": "internal", "derived": True, "formula": "sha256:<full_asset_sha256>"},
        {"name": "asset_path", "title_zh": "包内路径", "description": "Package-relative asset path.", "physical_type": "string", "logical_type": "path", "semantic_role": "asset_reference", "unit": None, "nullable": False, "null_means": None, "sensitivity": "internal", "derived": True, "formula": "data/assets/<sha256>.<extension>"},
        {"name": "asset_title", "title_zh": "资产标题", "description": "Human-readable title.", "physical_type": "string", "logical_type": "label", "semantic_role": "label", "unit": None, "nullable": False, "null_means": None, "sensitivity": "internal", "derived": False},
        {"name": "media_type", "title_zh": "媒体类型", "description": "IANA media type when known.", "physical_type": "string", "logical_type": "media_type", "semantic_role": "dimension", "unit": None, "nullable": False, "null_means": None, "sensitivity": "none", "derived": True, "formula": "configured value or filename MIME inference"},
        {"name": "sha256", "title_zh": "资产哈希", "description": "Full SHA-256 of asset bytes.", "physical_type": "string", "logical_type": "sha256", "semantic_role": "identifier", "unit": None, "nullable": False, "null_means": None, "sensitivity": "none", "derived": True, "formula": "sha256(asset_bytes)"},
        {"name": "bytes_cnt", "title_zh": "字节数", "description": "Asset size in bytes.", "physical_type": "int64", "logical_type": "file_size", "semantic_role": "measure", "unit": "byte", "nullable": False, "null_means": None, "sensitivity": "none", "derived": True, "formula": "length(asset_bytes)"},
    ]
    arrow_fields = [pa.field(c["name"], arrow_type(c["physical_type"]), nullable=bool(c["nullable"])) for c in columns]
    arrays = [pa.array([record[c["name"]] for record in records], type=field.type) for c, field in zip(columns, arrow_fields)]
    metadata = {
        b"unified_data_package.spec_version": SPEC_VERSION.encode(),
        b"unified_data_package.table": str(asset_table_cfg["name"]).encode(),
        b"unified_data_package.grain": str(asset_table_cfg["grain"]).encode("utf-8"),
    }
    return pa.Table.from_arrays(arrays, schema=pa.schema(arrow_fields, metadata=metadata)), [dict(c) for c in columns], sources


def markdown_items(items: list[Any], empty_text: str = "- None declared.") -> str:
    return "\n".join(f"- {item}" for item in items) if items else empty_text


def build_readme(package_cfg: dict[str, Any], table_schemas: list[dict[str, Any]]) -> str:
    table_lines = [f"- `{table['name']}`: {table['grain']}" for table in table_schemas]
    return f"""# {package_cfg['name']}

## What this is

{package_cfg['purpose']}

## Conclusions

{markdown_items(package_cfg.get('conclusions', []), '- No analytical conclusion declared; this package is a normalized data deliverable.')}

## Scope and grain

{chr(10).join(table_lines)}

## Definitions and conventions

- Truth: `data/*.parquet`
- Human views: `data/*.csv`
- Timezone: `{package_cfg['timezone']}`
- Specification: `{package_cfg.get('spec_version', SPEC_VERSION)}`
- Classification: `{package_cfg.get('classification', 'internal')}`
- CSV formula-like string cells are escaped for safe spreadsheet viewing; Parquet truth is unchanged.

## Assumptions

{markdown_items(package_cfg.get('assumptions', []))}

## Limitations

{markdown_items(package_cfg.get('limitations', []))}

## Rebuild and validate

`src/` contains the copied build configuration, builder, and dependency specification. Rebuilding requires the same source bytes at the configured paths. Validate with `python3 src/udp.py validate . --json`.
"""


def artifact_manifest(package_root: Path) -> list[dict[str, Any]]:
    artifacts = []
    for path in sorted(
        p
        for p in package_root.rglob("*")
        if p.is_file() and p.relative_to(package_root).as_posix() != "manifest.json"
    ):
        artifacts.append(
            {
                "path": path.relative_to(package_root).as_posix(),
                "media_type": media_type(path),
                "sha256": sha256_file(path),
                "bytes_cnt": path.stat().st_size,
            }
        )
    return artifacts


def meta_schema_path(filename: str) -> Path | None:
    candidates = [
        Path(__file__).resolve().parents[1] / "references" / filename,
        Path(__file__).resolve().parent / "schemas" / filename,
    ]
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def apply_meta_schema(instance: Any, filename: str, label: str, errors: list[str]) -> None:
    path = meta_schema_path(filename)
    if path is None:
        errors.append(f"Validator meta-schema missing: {filename}")
        return
    contract = json.loads(path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(contract, format_checker=FormatChecker())
    for issue in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in issue.absolute_path) or "<root>"
        errors.append(f"{label}.{location}: {issue.message}")


def build_package(config_path: Path, output_parent: Path) -> Path:
    config_path = config_path.resolve()
    config_dir = config_path.parent
    config = require_mapping(yaml.safe_load(config_path.read_text(encoding="utf-8")), "build config")
    package_cfg = require_mapping(config.get("package"), "package")
    sources_cfg = require_list(config.get("sources", []), "sources")
    assets_cfg = require_list(config.get("assets", []), "assets")

    for key in ("name", "version", "timezone", "purpose"):
        if not package_cfg.get(key):
            raise UDPError(f"package.{key} is required")
    package_name = str(package_cfg["name"])
    if not PACKAGE_RE.fullmatch(package_name):
        raise UDPError(f"Invalid package name: {package_name}")
    ZoneInfo(str(package_cfg["timezone"]))
    if package_cfg.get("spec_version", SPEC_VERSION) != SPEC_VERSION:
        raise UDPError(f"This builder supports only {SPEC_VERSION}")

    output_parent = output_parent.resolve()
    output_parent.mkdir(parents=True, exist_ok=True)
    final_root = output_parent / package_name
    if final_root.exists():
        raise UDPError(f"Output already exists; create a new version instead of overwriting: {final_root}")
    temp_root = Path(tempfile.mkdtemp(prefix=f".{package_name}.building-", dir=output_parent))

    try:
        (temp_root / "data").mkdir()
        (temp_root / "src").mkdir()
        rebuild_config = copy.deepcopy(config)
        for rebuild_source in rebuild_config.get("sources", []):
            resolved_source = (config_dir / str(rebuild_source["path"])).resolve()
            rebuild_source["path"] = os.path.relpath(resolved_source, final_root / "src")
        for rebuild_asset in rebuild_config.get("assets", []):
            resolved_asset = (config_dir / str(rebuild_asset["path"])).resolve()
            rebuild_asset["path"] = os.path.relpath(resolved_asset, final_root / "src")
        yaml_dump(temp_root / "src" / "build.yml", rebuild_config)
        shutil.copyfile(Path(__file__), temp_root / "src" / "udp.py")
        requirements = Path(__file__).with_name("requirements.txt")
        if requirements.exists():
            shutil.copyfile(requirements, temp_root / "src" / "requirements.txt")
        schemas_dir = temp_root / "src" / "schemas"
        schemas_dir.mkdir()
        for schema_name in ("manifest.schema.json", "schema.schema.json"):
            schema_source = meta_schema_path(schema_name)
            if schema_source is None:
                raise UDPError(f"Builder meta-schema missing: {schema_name}")
            shutil.copyfile(schema_source, schemas_dir / schema_name)

        table_schemas: list[dict[str, Any]] = []
        table_manifests: list[dict[str, Any]] = []
        source_manifests: list[dict[str, Any]] = []
        source_by_id: dict[str, dict[str, Any]] = {}

        for source_index, raw_source_cfg in enumerate(sources_cfg, start=1):
            source_cfg = require_mapping(raw_source_cfg, f"source {source_index}")
            source_path = (config_dir / str(source_cfg["path"])).resolve()
            if not source_path.is_file():
                raise UDPError(f"Source does not exist: {source_path}")
            source_hash = sha256_file(source_path)
            source_id = str(source_cfg.get("source_id", f"source_{source_index:03d}"))
            source_manifest = {
                "source_id": source_id,
                "file": source_path.name,
                "path": str(source_cfg["path"]),
                "media_type": media_type(source_path),
                "sha256": source_hash,
                "bytes_cnt": source_path.stat().st_size,
                "rows": 0,
                "cols": 0,
            }
            source_manifests.append(source_manifest)
            source_by_id[source_id] = source_manifest

            for raw_table_cfg in require_list(source_cfg.get("tables", []), f"tables for {source_id}"):
                table_cfg = require_mapping(raw_table_cfg, "table")
                for key in ("name", "grain", "columns"):
                    if key not in table_cfg:
                        raise UDPError(f"Table mapping missing {key}")
                table_name = str(table_cfg["name"])
                if not TABLE_RE.fullmatch(table_name):
                    raise UDPError(f"Invalid table name {table_name}")
                if any(existing["name"] == table_name for existing in table_schemas):
                    raise UDPError(f"Duplicate table name {table_name}")
                selector = str(table_cfg.get("selector") or source_path.stem)
                frame = load_source_table(source_path, table_cfg)
                source_manifest["rows"] += int(len(frame))
                source_manifest["cols"] = max(source_manifest["cols"], int(len(frame.columns)))
                table, column_schemas = build_arrow_table(
                    frame, table_cfg, source_hash, selector, str(package_cfg["timezone"])
                )
                parquet_path = temp_root / "data" / f"{table_name}.parquet"
                pq.write_table(
                    table,
                    parquet_path,
                    compression="zstd",
                    compression_level=3,
                    use_dictionary=True,
                    write_statistics=True,
                )
                reloaded = pq.read_table(parquet_path)
                diff = roundtrip_diff_cells(table, reloaded)
                csv_mode = str(table_cfg.get("csv_mode", "full"))
                csv_rows, preview_rule = write_csv_view(
                    reloaded,
                    temp_root / "data" / f"{table_name}.csv",
                    csv_mode,
                    int(table_cfg.get("csv_preview_rows", 1000)),
                )
                table_schema = {
                    "name": table_name,
                    "title_zh": table_cfg.get("title_zh", table_name),
                    "description": table_cfg.get("description", ""),
                    "grain": table_cfg["grain"],
                    "source_id": source_id,
                    "source_part": selector,
                    "primary_key": table_cfg.get("primary_key", ["row_uid"]),
                    "business_keys": table_cfg.get("business_keys", []),
                    "foreign_keys": table_cfg.get("foreign_keys", []),
                    "columns": column_schemas,
                }
                table_schemas.append(table_schema)
                table_manifests.append(
                    {
                        "name": table_name,
                        "grain": table_cfg["grain"],
                        "rows": reloaded.num_rows,
                        "cols": reloaded.num_columns,
                        "primary_key": table_schema["primary_key"],
                        "content_sha256": normalized_content_hash(reloaded),
                        "roundtrip_diff_cells": diff,
                        "csv_mode": csv_mode,
                        "csv_rows": csv_rows,
                        "csv_preview_rule": preview_rule,
                    }
                )

        if assets_cfg:
            asset_table_cfg = require_mapping(config.get("asset_table"), "asset_table")
            for key in ("name", "grain"):
                if not asset_table_cfg.get(key):
                    raise UDPError(f"asset_table.{key} is required when assets are present")
            asset_table, asset_columns, asset_sources = build_asset_table(
                assets_cfg, asset_table_cfg, config_dir, temp_root
            )
            source_manifests.extend(asset_sources)
            table_name = str(asset_table_cfg["name"])
            parquet_path = temp_root / "data" / f"{table_name}.parquet"
            pq.write_table(asset_table, parquet_path, compression="zstd", compression_level=3)
            reloaded = pq.read_table(parquet_path)
            diff = roundtrip_diff_cells(asset_table, reloaded)
            csv_rows, _ = write_csv_view(reloaded, temp_root / "data" / f"{table_name}.csv", "full", 0)
            table_schemas.append(
                {
                    "name": table_name,
                    "title_zh": asset_table_cfg.get("title_zh", table_name),
                    "description": asset_table_cfg.get("description", "Content-addressed binary asset index."),
                    "grain": asset_table_cfg["grain"],
                    "source_id": "multiple_assets",
                    "source_part": "asset",
                    "primary_key": ["row_uid"],
                    "business_keys": ["asset_uid"],
                    "foreign_keys": [],
                    "columns": asset_columns,
                }
            )
            table_manifests.append(
                {
                    "name": table_name,
                    "grain": asset_table_cfg["grain"],
                    "rows": reloaded.num_rows,
                    "cols": reloaded.num_columns,
                    "primary_key": ["row_uid"],
                    "content_sha256": normalized_content_hash(reloaded),
                    "roundtrip_diff_cells": diff,
                    "csv_mode": "full",
                    "csv_rows": csv_rows,
                    "csv_preview_rule": None,
                }
            )
            profiles = package_cfg.setdefault("profiles", [])
            if "asset/v1" not in profiles:
                profiles.append("asset/v1")

        if not table_schemas:
            raise UDPError("A package must contain at least one truth table")

        schema_document = {
            "package": package_name,
            "spec_version": SPEC_VERSION,
            "timezone": package_cfg["timezone"],
            "tables": table_schemas,
        }
        yaml_dump(temp_root / "schema.yml", schema_document)
        (temp_root / "README.md").write_text(build_readme(package_cfg, table_schemas), encoding="utf-8")

        skill_script_hash = sha256_file(Path(__file__))
        requirements_hash = sha256_file(requirements) if requirements.exists() else None
        now = dt.datetime.now(ZoneInfo(str(package_cfg["timezone"]))).replace(microsecond=0).isoformat()
        manifest = {
            "package": package_name,
            "package_version": str(package_cfg["version"]),
            "spec_version": SPEC_VERSION,
            "profiles": package_cfg.get("profiles", ["tabular/v1"]),
            "built_at": now,
            "timezone": package_cfg["timezone"],
            "purpose": package_cfg["purpose"],
            "classification": package_cfg.get("classification", "internal"),
            "license": package_cfg.get("license"),
            "source": source_manifests,
            "tables": table_manifests,
            "build": {
                "entrypoint": "src/udp.py build --config src/build.yml --output <new-parent-directory>",
                "code_sha256": skill_script_hash,
                "config_sha256": sha256_file(temp_root / "src" / "build.yml"),
                "input_config_sha256": sha256_file(config_path),
                "lock_sha256": requirements_hash,
                "random_seed": 0,
                "python": sys.version.split()[0],
                "pandas": pd.__version__,
                "pyarrow": pa.__version__,
            },
            "artifacts": artifact_manifest(temp_root),
            "validation": {
                "status": "pass" if all(t["roundtrip_diff_cells"] == 0 for t in table_manifests) else "fail",
                "errors_cnt": sum(1 for t in table_manifests if t["roundtrip_diff_cells"] != 0),
                "warnings_cnt": 0,
            },
        }
        json_dump(temp_root / "manifest.json", manifest)
        result = validate_package(temp_root)
        if result["errors"]:
            manifest["validation"] = {
                "status": "fail",
                "errors_cnt": len(result["errors"]),
                "warnings_cnt": len(result["warnings"]),
            }
            json_dump(temp_root / "manifest.json", manifest)
            raise UDPError("Built package failed validation:\n- " + "\n- ".join(result["errors"]))
        manifest["validation"] = {
            "status": "pass",
            "errors_cnt": 0,
            "warnings_cnt": len(result["warnings"]),
        }
        json_dump(temp_root / "manifest.json", manifest)
        os.replace(temp_root, final_root)
        return final_root
    except Exception:
        if temp_root.exists():
            shutil.rmtree(temp_root)
        raise


def validate_constraints(values: list[Any], column: dict[str, Any], errors: list[str], table_name: str) -> None:
    constraints = column.get("constraints") or {}
    if not isinstance(constraints, dict):
        errors.append(f"{table_name}.{column['name']}: constraints must be a mapping")
        return
    non_null = [value for value in values if value is not None]
    if "enum" in constraints:
        allowed = {str(value) for value in constraints["enum"]}
        bad = [value for value in non_null if str(value) not in allowed]
        if bad:
            errors.append(f"{table_name}.{column['name']}: {len(bad)} values outside enum")
    if "pattern" in constraints:
        pattern = re.compile(str(constraints["pattern"]))
        bad = [value for value in non_null if not pattern.fullmatch(str(value))]
        if bad:
            errors.append(f"{table_name}.{column['name']}: {len(bad)} values fail pattern")
    for key, op in (("minimum", lambda a, b: a < b), ("maximum", lambda a, b: a > b)):
        if key in constraints:
            bound = Decimal(str(constraints[key]))
            bad = []
            for value in non_null:
                try:
                    if op(Decimal(str(value)), bound):
                        bad.append(value)
                except InvalidOperation:
                    errors.append(f"{table_name}.{column['name']}: non-numeric value for {key}")
                    return
            if bad:
                errors.append(f"{table_name}.{column['name']}: {len(bad)} values violate {key}")


def validate_package(package_root: Path) -> dict[str, Any]:
    package_root = package_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    required = ["README.md", "manifest.json", "schema.yml", "data", "src"]
    for name in required:
        if not (package_root / name).exists():
            errors.append(f"Missing required path: {name}")
    if errors:
        return {"status": "fail", "errors": errors, "warnings": warnings}

    try:
        manifest = require_mapping(json.loads((package_root / "manifest.json").read_text(encoding="utf-8")), "manifest")
    except Exception as exc:
        return {"status": "fail", "errors": [f"Invalid manifest.json: {exc}"], "warnings": warnings}
    try:
        schema = require_mapping(yaml.safe_load((package_root / "schema.yml").read_text(encoding="utf-8")), "schema")
    except Exception as exc:
        return {"status": "fail", "errors": [f"Invalid schema.yml: {exc}"], "warnings": warnings}

    apply_meta_schema(manifest, "manifest.schema.json", "manifest", errors)
    apply_meta_schema(schema, "schema.schema.json", "schema", errors)

    package_name = str(manifest.get("package", ""))
    if not PACKAGE_RE.fullmatch(package_name):
        errors.append(f"Invalid manifest package name: {package_name}")
    if schema.get("package") != package_name:
        errors.append("schema package does not match manifest package")
    if manifest.get("spec_version") != SPEC_VERSION or schema.get("spec_version") != SPEC_VERSION:
        errors.append(f"spec_version must be {SPEC_VERSION}")
    try:
        ZoneInfo(str(manifest.get("timezone")))
    except Exception:
        errors.append("manifest timezone must be a valid IANA timezone")
    if schema.get("timezone") != manifest.get("timezone"):
        errors.append("schema timezone does not match manifest timezone")

    recorded_validation = manifest.get("validation") or {}
    if recorded_validation.get("status") != "pass":
        errors.append("manifest validation status is not pass")
    if recorded_validation.get("errors_cnt") != 0:
        errors.append("manifest validation errors_cnt is not zero")

    artifact_paths: set[str] = set()
    for artifact in manifest.get("artifacts", []):
        rel = str(artifact.get("path", ""))
        if rel.startswith("/") or ".." in Path(rel).parts:
            errors.append(f"Unsafe artifact path: {rel}")
            continue
        if rel in artifact_paths:
            errors.append(f"Duplicate artifact path: {rel}")
        artifact_paths.add(rel)
        path = package_root / rel
        if not path.is_file():
            errors.append(f"Artifact missing: {rel}")
            continue
        if sha256_file(path) != artifact.get("sha256"):
            errors.append(f"Artifact checksum mismatch: {rel}")
        if path.stat().st_size != artifact.get("bytes_cnt"):
            errors.append(f"Artifact size mismatch: {rel}")

    actual_artifact_paths = {
        path.relative_to(package_root).as_posix()
        for path in package_root.rglob("*")
        if path.is_file() and path.relative_to(package_root).as_posix() != "manifest.json"
    }
    for rel in sorted(actual_artifact_paths - artifact_paths):
        errors.append(f"Unlisted artifact: {rel}")
    for rel in sorted(artifact_paths - actual_artifact_paths):
        errors.append(f"Listed artifact is not distributable: {rel}")

    manifest_tables = {str(item.get("name")): item for item in manifest.get("tables", [])}
    schema_tables = require_list(schema.get("tables", []), "schema tables")
    if not schema_tables:
        errors.append("No tables declared")
    loaded_tables: dict[str, pa.Table] = {}
    schema_by_name: dict[str, dict[str, Any]] = {}

    for raw_table_schema in schema_tables:
        table_schema = require_mapping(raw_table_schema, "table schema")
        table_name = str(table_schema.get("name", ""))
        if not TABLE_RE.fullmatch(table_name):
            errors.append(f"Invalid table name: {table_name}")
        if table_name in schema_by_name:
            errors.append(f"Duplicate table schema: {table_name}")
            continue
        schema_by_name[table_name] = table_schema
        grain = table_schema.get("grain")
        if not isinstance(grain, str) or not grain.strip():
            errors.append(f"{table_name}: grain is required")
        table_manifest = manifest_tables.get(table_name)
        if table_manifest is None:
            errors.append(f"{table_name}: missing manifest table")
            continue
        if table_manifest.get("grain") != grain:
            errors.append(f"{table_name}: grain differs between schema and manifest")
        parquet_path = package_root / "data" / f"{table_name}.parquet"
        csv_path = package_root / "data" / f"{table_name}.csv"
        if not parquet_path.is_file():
            errors.append(f"{table_name}: missing Parquet truth")
            continue
        if not csv_path.is_file():
            errors.append(f"{table_name}: missing CSV view")
        try:
            table = pq.read_table(parquet_path)
        except Exception as exc:
            errors.append(f"{table_name}: unreadable Parquet: {exc}")
            continue
        loaded_tables[table_name] = table
        if table.num_rows != table_manifest.get("rows"):
            errors.append(f"{table_name}: row count differs from manifest")
        if table.num_columns != table_manifest.get("cols"):
            errors.append(f"{table_name}: column count differs from manifest")
        if normalized_content_hash(table) != table_manifest.get("content_sha256"):
            errors.append(f"{table_name}: normalized content hash mismatch")
        if table_manifest.get("roundtrip_diff_cells") != 0:
            errors.append(f"{table_name}: roundtrip_diff_cells is not zero")

        column_schemas = require_list(table_schema.get("columns", []), f"columns for {table_name}")
        declared_names = [str(column.get("name")) for column in column_schemas if isinstance(column, dict)]
        if declared_names != table.column_names:
            errors.append(f"{table_name}: schema column order/names differ from Parquet")
            continue
        if "row_uid" not in declared_names:
            errors.append(f"{table_name}: row_uid missing")

        for index, raw_column in enumerate(column_schemas):
            column = require_mapping(raw_column, f"column {index} in {table_name}")
            name = str(column.get("name", ""))
            if not FIELD_RE.fullmatch(name):
                errors.append(f"{table_name}: invalid field name {name}")
            type_text = str(column.get("physical_type", ""))
            try:
                expected_type = arrow_type(type_text)
            except UDPError as exc:
                errors.append(f"{table_name}.{name}: {exc}")
                continue
            actual_field = table.schema.field(index)
            if actual_field.type != expected_type:
                errors.append(f"{table_name}.{name}: Parquet type {actual_field.type} != {expected_type}")
            nullable = column.get("nullable")
            if not isinstance(nullable, bool):
                errors.append(f"{table_name}.{name}: nullable must be boolean")
            values = table.column(index).to_pylist()
            null_count = sum(value is None for value in values)
            if nullable is False and null_count:
                errors.append(f"{table_name}.{name}: non-nullable column has {null_count} nulls")
            if nullable is True and not column.get("null_means"):
                warnings.append(f"{table_name}.{name}: nullable field has no substantive null_means")
            role = column.get("semantic_role")
            if (role in ID_ROLES or name.endswith("_id")) and type_text != "string":
                errors.append(f"{table_name}.{name}: identifiers must be strings")
            if is_numeric_type(type_text) and not name.endswith(UNIT_SUFFIXES) and not column.get("unit"):
                errors.append(f"{table_name}.{name}: numeric field lacks suffix and schema unit")
            if name.endswith("_cny") and not DECIMAL_RE.match(type_text):
                errors.append(f"{table_name}.{name}: CNY amount must use DECIMAL")
            if column.get("derived") and not column.get("formula"):
                errors.append(f"{table_name}.{name}: derived field lacks formula")
            if TIMESTAMP_RE.match(type_text) and not actual_field.type.tz:
                errors.append(f"{table_name}.{name}: timestamp lacks timezone")
            validate_constraints(values, column, errors, table_name)

        row_uid_values = table.column("row_uid").to_pylist() if "row_uid" in table.column_names else []
        if any(value is None or not ROW_UID_RE.fullmatch(str(value)) for value in row_uid_values):
            errors.append(f"{table_name}: invalid row_uid format")
        if len(set(row_uid_values)) != len(row_uid_values):
            errors.append(f"{table_name}: duplicate row_uid values")

        primary_key = table_schema.get("primary_key") or []
        if not primary_key:
            errors.append(f"{table_name}: primary_key is required")
        elif any(column not in table.column_names for column in primary_key):
            errors.append(f"{table_name}: primary_key references missing column")
        else:
            key_columns = [table.column(column).to_pylist() for column in primary_key]
            keys = [tuple(column[row] for column in key_columns) for row in range(table.num_rows)]
            if any(any(item is None for item in key) for key in keys):
                errors.append(f"{table_name}: primary_key contains null")
            if len(set(keys)) != len(keys):
                errors.append(f"{table_name}: primary_key is not unique")

    if set(manifest_tables) != set(schema_by_name):
        errors.append("Manifest and schema table sets differ")

    for table_name, table_schema in schema_by_name.items():
        source_table = loaded_tables.get(table_name)
        if source_table is None:
            continue
        for fk in table_schema.get("foreign_keys", []):
            if not isinstance(fk, dict):
                errors.append(f"{table_name}: foreign key must be a mapping")
                continue
            columns = fk.get("columns", [])
            target_name = fk.get("references")
            target_columns = fk.get("referenced_columns", [])
            target_table = loaded_tables.get(target_name)
            if target_table is None:
                errors.append(f"{table_name}: foreign key target {target_name} missing")
                continue
            if len(columns) != len(target_columns) or not columns:
                errors.append(f"{table_name}: foreign key columns are invalid")
                continue
            if any(c not in source_table.column_names for c in columns) or any(c not in target_table.column_names for c in target_columns):
                errors.append(f"{table_name}: foreign key references missing columns")
                continue
            target_values = {
                tuple(target_table.column(c)[row].as_py() for c in target_columns)
                for row in range(target_table.num_rows)
            }
            missing = 0
            for row in range(source_table.num_rows):
                key = tuple(source_table.column(c)[row].as_py() for c in columns)
                if any(item is None for item in key):
                    continue
                if key not in target_values:
                    missing += 1
            if missing:
                errors.append(f"{table_name}: {missing} foreign-key rows do not match {target_name}")

    for source in manifest.get("source", []):
        digest = str(source.get("sha256", ""))
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"Source {source.get('file')}: invalid SHA-256")

    status = "pass" if not errors else "fail"
    return {"status": status, "errors": errors, "warnings": warnings}


def inspect_path(path: Path) -> list[dict[str, Any]]:
    if path.is_dir():
        reports: list[dict[str, Any]] = []
        for item in sorted(path.rglob("*")):
            if item.is_file() and not any(part.startswith(".") for part in item.relative_to(path).parts):
                reports.extend(inspect_path(item))
        return reports
    if not path.is_file():
        raise UDPError(f"Input does not exist: {path}")

    report: dict[str, Any] = {
        "path": str(path.resolve()),
        "file": path.name,
        "media_type": media_type(path),
        "sha256": sha256_file(path),
        "bytes_cnt": path.stat().st_size,
        "kind": "asset",
    }
    suffix = path.suffix.lower()
    tables: list[dict[str, Any]] = []
    try:
        if suffix in {".xlsx", ".xlsm"}:
            workbook = pd.ExcelFile(path)
            for sheet in workbook.sheet_names:
                frame = pd.read_excel(path, sheet_name=sheet, dtype=object, keep_default_na=False)
                columns = [str(column) for column in frame.columns]
                tables.append(
                    {
                        "selector": sheet,
                        "rows": len(frame),
                        "cols": len(columns),
                        "columns": columns,
                        "pii_name_candidates": [column for column in columns if SENSITIVE_NAME_RE.search(column)],
                    }
                )
        elif suffix in {".csv", ".tsv", ".json", ".jsonl", ".ndjson", ".parquet"}:
            frame = load_source_table(path, {"selector": None, "header_row": 1})
            columns = [str(column) for column in frame.columns]
            tables.append(
                {
                    "selector": path.stem,
                    "rows": len(frame),
                    "cols": len(columns),
                    "columns": columns,
                    "pii_name_candidates": [column for column in columns if SENSITIVE_NAME_RE.search(column)],
                }
            )
    except Exception as exc:
        report["inspection_error"] = str(exc)
    if tables:
        report["kind"] = "tabular"
        report["tables"] = tables
    return [report]


def deterministic_archive(package_root: Path, output_path: Path) -> dict[str, Any]:
    validation = validate_package(package_root)
    if validation["errors"]:
        raise UDPError("Refusing to archive invalid package:\n- " + "\n- ".join(validation["errors"]))
    if output_path.exists():
        raise UDPError(f"Archive output already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    root_name = package_root.name
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in package_root.rglob("*") if p.is_file()):
            relative = Path(root_name) / path.relative_to(package_root)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return {"path": str(output_path.resolve()), "sha256": sha256_file(output_path), "bytes_cnt": output_path.stat().st_size}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="udp", description="Build and validate Unified Data Packages")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect source files without modifying them")
    inspect_parser.add_argument("inputs", nargs="+", type=Path)
    inspect_parser.add_argument("--output", type=Path, help="Optional JSON report path")

    build_parser = subparsers.add_parser("build", help="Build a new package from YAML configuration")
    build_parser.add_argument("--config", required=True, type=Path)
    build_parser.add_argument("--output", required=True, type=Path, help="Parent directory for the new package")

    validate_parser = subparsers.add_parser("validate", help="Validate an existing package")
    validate_parser.add_argument("package", type=Path)
    validate_parser.add_argument("--json", action="store_true", dest="as_json")

    archive_parser = subparsers.add_parser("archive", help="Create a deterministic ZIP after validation")
    archive_parser.add_argument("package", type=Path)
    archive_parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.command == "inspect":
            report = {"files": [item for path in args.inputs for item in inspect_path(path)]}
            if args.output:
                if args.output.exists():
                    raise UDPError(f"Inspection output already exists: {args.output}")
                json_dump(args.output, report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
        if args.command == "build":
            result = build_package(args.config, args.output)
            print(json.dumps({"status": "pass", "package": str(result)}, ensure_ascii=False, indent=2))
            return 0
        if args.command == "validate":
            result = validate_package(args.package)
            if args.as_json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"status: {result['status']}")
                for issue in result["errors"]:
                    print(f"ERROR: {issue}")
                for issue in result["warnings"]:
                    print(f"WARNING: {issue}")
            return 0 if result["status"] == "pass" else 1
        if args.command == "archive":
            result = deterministic_archive(args.package.resolve(), args.output.resolve())
            print(json.dumps({"status": "pass", **result}, ensure_ascii=False, indent=2))
            return 0
    except (UDPError, OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
