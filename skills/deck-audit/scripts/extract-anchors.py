#!/usr/bin/env python3
"""Extract fidelity anchors from source units and page material into anchors.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from anchors_lib import extract_from_text


def material_text(page: dict, pages_dir: Path) -> str:
    parts: list[str] = []
    pid = page.get("id") or ""
    for key in ("title", "source", "how_to_read", "takeaway", "notes"):
        val = page.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val)
    material = page.get("material") or {}
    if isinstance(material, dict):
        bullets = material.get("bullets") or []
        if isinstance(bullets, list):
            parts.extend(str(b) for b in bullets)
        table = material.get("table")
        if isinstance(table, dict):
            parts.extend(str(c) for c in (table.get("columns") or []))
            for row in table.get("rows") or []:
                if isinstance(row, list):
                    parts.extend(str(c) for c in row)
                else:
                    parts.append(str(row))
            if table.get("sum"):
                parts.append(str(table["sum"]))
        numbers = material.get("numbers") or []
        if isinstance(numbers, list):
            parts.extend(str(n) for n in numbers)
        if material.get("quote"):
            parts.append(str(material["quote"]))
    md_path = pages_dir / f"{pid}.md"
    if md_path.is_file():
        parts.append(_strip_page_chrome(md_path.read_text(encoding="utf-8")))
    return "\n".join(parts)


def _strip_page_chrome(md: str) -> str:
    """Drop scaffolding lines that invent unit-id digits (## u-0001, units:, role:)."""
    import re

    out: list[str] = []
    for line in md.splitlines():
        if re.match(r"^#+\s*u-\d{4}\s*$", line, re.I):
            continue
        if re.match(r"^units:\s*", line, re.I):
            continue
        if re.match(r"^role:\s*", line, re.I):
            continue
        # neutralize inline unit ids so -0001 is not parsed as a number
        line = re.sub(r"\bu-\d{4}\b", " ", line, flags=re.I)
        out.append(line)
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract deck-audit anchors")
    parser.add_argument("--work", required=True, help="Work dir with units.json + deck.json")
    args = parser.parse_args()
    work = Path(args.work)
    assert work.is_dir(), f"missing work dir: {work}"

    units_path = work / "units.json"
    deck_path = work / "deck.json"
    assert units_path.is_file(), f"missing {units_path}"
    assert deck_path.is_file(), f"missing {deck_path}"

    units = json.loads(units_path.read_text(encoding="utf-8"))
    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    pages_dir = work / "pages"

    source: dict[str, list[dict]] = {}
    for uid, text in units.items():
        source[uid] = extract_from_text(text if isinstance(text, str) else str(text), uid)

    material: dict[str, list[dict]] = {}
    for page in deck.get("pages") or []:
        pid = page.get("id")
        assert pid, "page missing id"
        material[pid] = extract_from_text(material_text(page, pages_dir), pid)

    out = {
        "version": "1.0.0",
        "source": source,
        "material": material,
        "counts": {
            "units": len(source),
            "pages": len(material),
            "source_anchors": sum(len(v) for v in source.values()),
            "material_anchors": sum(len(v) for v in material.values()),
        },
    }
    out_path = work / "anchors.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"anchors: units={out['counts']['units']} pages={out['counts']['pages']} "
        f"src={out['counts']['source_anchors']} mat={out['counts']['material_anchors']} → {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
