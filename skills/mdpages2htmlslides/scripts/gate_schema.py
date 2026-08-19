#!/usr/bin/env python3
"""Validate the shared GF deck-plan contract before rendering."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TEMPLATES = {
    "cover", "toc", "chapter", "statement", "kpi", "compare", "matrix",
    "chart", "chart-table", "roster", "verdict", "readme",
}
TRANSLATIONS = {"quote": "statement", "playbook": "verdict", "gallery": "roster", "interactive": "chart"}
VIZ = {
    "bubble", "calendar", "diverging-bar", "funnel", "heatmap", "hist-cdf",
    "line-dual", "network", "pareto", "quadrant", "radar", "sankey",
    "slope", "treemap", "venn", "waterfall",
}
VIZ_ALIASES = {
    "bar", "line", "area", "stacked-bar", "scatter", "donut", "timeline",
    "process", "org", "map", "gauge", "table",
}
BLOCKS = {
    "text", "list", "metric", "table", "fig", "image", "embed", "note",
    "claim", "lede", "bullets", "kpi-card", "callout", "step", "profile",
    "quote", "media", "toc-item",
}
LAYOUTS = {"full", "hero-band", "split-2", "split-2-62", "split-3", "grid-2x2", "grid-3x2", "table-full", "fig-rail", "fig-strip"}
PACKS = {"air", "mid", "tight"}
PAGE_ID = re.compile(r"^p-[0-9]{3,4}$")
MARKDOWN = re.compile(r"\*\*|`[^`]+`|^\s*#{1,6}\s|\[[^\]]*\]\(", re.M)


def strings(value, path="$"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from strings(item, f"{path}[{index}]")


def validate(plan):
    errors = []
    if plan.get("contract_version") != "1.0.0":
        errors.append(("$", "CONTRACT_VERSION", "contract_version must be 1.0.0"))
    if not str(plan.get("title") or "").strip():
        errors.append(("$", "NO_DECK_TITLE", "title is required"))
    pages = plan.get("pages")
    if not isinstance(pages, list) or not pages:
        return errors + [("$", "NO_PAGES", "pages must be a non-empty array")]
    if plan.get("mode") not in (None, "slide", "slides", "responsive", "print"):
        errors.append(("$", "MODE_UNKNOWN", repr(plan.get("mode"))))

    seen = set()
    for index, page in enumerate(pages, 1):
        pid = page.get("id") or f"p-{index:03d}"
        if pid in seen:
            errors.append((pid, "DUP_ID", "duplicate page id"))
        seen.add(pid)
        if not PAGE_ID.fullmatch(str(pid)):
            errors.append((pid, "ID_INVALID", "id must match p-NNN or p-NNNN"))

        raw_template = page.get("template") or page.get("type")
        template = TRANSLATIONS.get(raw_template, raw_template)
        if template not in TEMPLATES:
            errors.append((pid, "TEMPLATE_UNKNOWN", repr(template)))
        if not str(page.get("title") or "").strip():
            errors.append((pid, "NO_TITLE", "title is required"))
        for field in ("source", "takeaway", "visualization", "content"):
            if field not in page:
                errors.append((pid, "FIELD_REQUIRED", f"{field} is required"))
        if page.get("layout") not in (None, *LAYOUTS):
            errors.append((pid, "LAYOUT_UNKNOWN", repr(page.get("layout"))))
        if page.get("pack") not in PACKS:
            errors.append((pid, "PACK_UNKNOWN", repr(page.get("pack"))))
        if template not in {"cover", "toc", "chapter"} and not str(page.get("source") or "").strip():
            provenance = page.get("provenance") or {}
            if not str(provenance.get("source") or "").strip():
                errors.append((pid, "NO_SOURCE", "source or provenance.source is required"))

        content = page.get("content") or {}
        if not isinstance(content, dict):
            errors.append((pid, "CONTENT_INVALID", "content must be an object"))
            content = {}
        blocks = content.get("blocks") if isinstance(content, dict) else None
        if blocks is None:
            blocks = page.get("blocks") or []
        if not isinstance(blocks, list):
            errors.append((pid, "BLOCKS_INVALID", "content.blocks must be an array"))
            blocks = []
        for block in blocks:
            kind = block.get("kind") if isinstance(block, dict) else None
            if kind not in BLOCKS:
                errors.append((pid, "BLOCK_UNKNOWN", repr(kind)))
                continue
            if kind == "table":
                columns = block.get("columns") or []
                rows = block.get("rows") or []
                if len(columns) > 7:
                    errors.append((pid, "WIDE_TABLE", f"{len(columns)} columns; use appendix bypass"))
                if len(rows) > 12:
                    errors.append((pid, "LONG_TABLE", f"{len(rows)} rows; use appendix bypass"))
                if any(len(row) != len(columns) for row in rows):
                    errors.append((pid, "RAGGED_ROWS", "table row width differs from columns"))
            if kind == "fig" and block.get("viz") not in VIZ | VIZ_ALIASES:
                errors.append((pid, "VIZ_UNKNOWN", repr(block.get("viz"))))
            if kind == "embed" and not (block.get("fallback") or block.get("fallback_img") or block.get("fallback_text")):
                errors.append((pid, "NO_FALLBACK", "embed needs a table, text, or image fallback"))

        viz = page.get("visualization")
        if isinstance(viz, str) and viz not in VIZ | VIZ_ALIASES:
            errors.append((pid, "VIZ_UNKNOWN", repr(viz)))
        for path, value in strings({"title": page.get("title"), "takeaway": page.get("takeaway"), "content": content}, pid):
            if MARKDOWN.search(value):
                errors.append((pid, "MD_IN_SLOT", f"{path}: {value[:40]!r}"))
        if page.get("overflow_of") and page["overflow_of"] not in seen:
            errors.append((pid, "FORWARD_CONT", f"overflow_of={page['overflow_of']} not seen yet"))
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--design")  # retained for old job definitions
    parser.add_argument("--out")
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    errors = validate(plan)
    report = {"pages": len(plan.get("pages") or []), "hard": len(errors), "findings": [
        {"page": page, "code": code, "sev": "hard", "msg": message} for page, code, message in errors
    ]}
    if args.out:
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for page, code, message in errors:
        print(f"  {code:<18} {page:>8}  {message}")
    print(f"gate_schema: {report['pages']} pages · {report['hard']} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
