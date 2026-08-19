#!/usr/bin/env python3
"""Assert the longdoc-to-deck coverage ledger closes.

Stages:
  index   — index.json exists and unit ids are unique/contiguous-ish
  outline — every unit id appears exactly once in outline.md
  deck    — every unit maps to exactly one page; overflow_of parents exist
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

UNIT_ID_RE = re.compile(r"\bu-\d{4}\b")
PAGE_ID_RE = re.compile(r"^p-\d{4}$")


def load_index(work: Path) -> dict:
    path = work / "index.json"
    assert path.is_file(), f"missing {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "units" in data and isinstance(data["units"], list), "index.units must be a list"
    return data


def unit_ids(index: dict) -> list[str]:
    ids = [u["id"] for u in index["units"]]
    assert len(ids) == len(set(ids)), "duplicate unit ids in index.json"
    for uid in ids:
        assert UNIT_ID_RE.fullmatch(uid), f"bad unit id: {uid}"
    return ids


def check_index(work: Path) -> None:
    index = load_index(work)
    ids = unit_ids(index)
    assert index.get("total_units") == len(ids), "total_units mismatch"
    digest = work / "index.md"
    assert digest.is_file(), f"missing {digest}"
    print(f"index OK: {len(ids)} units")


def extract_unit_ids_from_text(text: str) -> list[str]:
    return UNIT_ID_RE.findall(text)


def check_outline(work: Path) -> None:
    index = load_index(work)
    expected = set(unit_ids(index))
    outline_path = work / "outline.md"
    assert outline_path.is_file(), f"missing {outline_path}"
    text = outline_path.read_text(encoding="utf-8")
    found = extract_unit_ids_from_text(text)
    found_set = set(found)
    duplicates = [uid for uid in found_set if found.count(uid) > 1]
    orphans = sorted(expected - found_set)
    extras = sorted(found_set - expected)
    assert not duplicates, f"duplicate unit ids in outline: {duplicates[:20]}"
    assert not orphans, f"orphan units (in index, missing from outline): {orphans[:20]} (n={len(orphans)})"
    assert not extras, f"unknown unit ids in outline: {extras[:20]}"
    assert len(found_set) == len(expected), "mapped != total"
    print(f"outline OK: mapped={len(found_set)} total={len(expected)} closes")


def check_deck(work: Path) -> None:
    index = load_index(work)
    expected = set(unit_ids(index))
    deck_path = work / "deck.json"
    assert deck_path.is_file(), f"missing {deck_path}"
    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    assert "pages" in deck and isinstance(deck["pages"], list), "deck.pages must be a list"
    pages = deck["pages"]
    page_ids = [p.get("id") for p in pages]
    assert all(isinstance(pid, str) and PAGE_ID_RE.match(pid) for pid in page_ids), "bad page ids"
    assert len(page_ids) == len(set(page_ids)), "duplicate page ids"

    mapped: list[str] = []
    for page in pages:
        units = page.get("units") or []
        assert isinstance(units, list), f"{page.get('id')}: units must be list"
        mapped.extend(units)
        role = page.get("role")
        assert role, f"{page.get('id')}: missing role"
        assert page.get("title"), f"{page.get('id')}: missing title"

    mapped_set = set(mapped)
    duplicates = sorted({uid for uid in mapped_set if mapped.count(uid) > 1})
    orphans = sorted(expected - mapped_set)
    extras = sorted(mapped_set - expected)
    assert not duplicates, f"unit mapped to multiple pages: {duplicates[:20]}"
    assert not orphans, f"orphan units (not on any page): {orphans[:20]} (n={len(orphans)})"
    assert not extras, f"unknown unit ids on pages: {extras[:20]}"

    id_set = set(page_ids)
    for page in pages:
        overflow = page.get("overflow_of")
        if overflow is not None:
            assert overflow in id_set, f"{page['id']}: overflow_of {overflow} missing"
            assert overflow != page["id"], f"{page['id']}: overflow_of self"

    pages_dir = work / "pages"
    if pages_dir.is_dir():
        for page in pages:
            md = pages_dir / f"{page['id']}.md"
            assert md.is_file(), f"missing page material {md}"

    print(
        f"deck OK: pages={len(pages)} mapped={len(mapped_set)} total={len(expected)} closes"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Coverage ledger gates for longdoc-to-deck")
    parser.add_argument(
        "--stage",
        required=True,
        choices=("index", "outline", "deck"),
        help="Which gate to run",
    )
    parser.add_argument("--work", required=True, help="Work directory with index/outline/deck")
    args = parser.parse_args()
    work = Path(args.work)
    assert work.is_dir(), f"work dir missing: {work}"

    try:
        if args.stage == "index":
            check_index(work)
        elif args.stage == "outline":
            check_outline(work)
        else:
            check_deck(work)
    except AssertionError as exc:
        print(f"FAIL [{args.stage}]: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
