#!/usr/bin/env python3
"""Score each deck page against budgets.json — flag overfull and starved pages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BULLET_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s+", re.M)
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$", re.M)


def count_table_rows(text: str) -> int:
    rows = [ln for ln in text.splitlines() if TABLE_ROW_RE.match(ln)]
    # Exclude separator rows
    data = [
        r
        for r in rows
        if not re.match(r"^\|?\s*:?-{3,}", r.strip())
    ]
    # Exclude header if present (first data-ish row often header) — count body ≈ max(0, n-1)
    if len(data) <= 1:
        return max(0, len(data) - 0)
    return max(0, len(data) - 1)


def score_page(page: dict, budgets: dict, units_text: dict[str, str]) -> dict:
    role = page.get("role") or "statement"
    b = budgets["roles"].get(role) or budgets["roles"]["statement"]
    unit_ids = page.get("units") or []
    texts = [units_text.get(uid, "") for uid in unit_ids]
    blob = "\n".join(texts)
    material = page.get("material") or {}
    if material.get("bullets"):
        bullets = len(material["bullets"])
    else:
        bullets = len(BULLET_RE.findall(blob))
    if isinstance(material.get("table"), dict) and material["table"].get("rows"):
        rows = len(material["table"]["rows"])
    elif unit_ids and units_text:
        # Sum per-unit so multiple tables on one page do not double-count headers
        rows = sum(count_table_rows(units_text.get(uid, "")) for uid in unit_ids)
    else:
        rows = count_table_rows(blob)
    chars = len(blob)
    if not chars and page.get("title"):
        chars = len(page["title"]) + len(page.get("takeaway") or "")

    over = (
        chars > b.get("chars_max", 10**9)
        or rows > b.get("rows_max", 10**9)
        or bullets > b.get("bullets_max", 10**9)
    )
    chars_min = b.get("chars_min", 0)
    rows_min = b.get("rows_min", 0)
    thin_chars = chars < chars_min
    thin_rows = bool(rows_min) and rows < rows_min

    # Atomic page: single unit that cannot be split further without mid-structure cuts
    atomic_oversize = over and len(unit_ids) <= 1

    if over and not atomic_oversize:
        verdict = "overfull"
    elif role in ("cover", "chapter", "toc") and chars >= 0:
        verdict = "ok"
    elif thin_chars or thin_rows:
        # Empty cover scaffold
        if not unit_ids and role == "cover":
            verdict = "ok"
        elif chars == 0 and not unit_ids:
            verdict = "ok"
        # Single short unit is a valid thin module (not a bad split)
        elif len(unit_ids) <= 1:
            verdict = "ok"
        else:
            verdict = "starved"
    else:
        verdict = "ok"

    fit = {
        "chars": chars,
        "rows": rows,
        "bullets": bullets,
        "budget": f"{role}:chars≤{b.get('chars_max')}/rows≤{b.get('rows_max')}",
        "verdict": verdict,
        "atomic_oversize": atomic_oversize,
    }
    return fit


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate fit for longdoc2mdpages pages")
    parser.add_argument("--work", required=True, help="Work directory with deck.json")
    parser.add_argument(
        "--budgets",
        default=None,
        help="Path to budgets.json (default: sibling of this script)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write fit objects back into deck.json",
    )
    parser.add_argument(
        "--fail-on",
        default="overfull",
        choices=("none", "overfull", "starved", "any"),
        help="Exit non-zero when these verdicts appear (default: overfull)",
    )
    args = parser.parse_args()
    work = Path(args.work)
    budgets_path = (
        Path(args.budgets)
        if args.budgets
        else Path(__file__).resolve().parent.parent / "budgets.json"
    )
    budgets = json.loads(budgets_path.read_text(encoding="utf-8"))
    deck_path = work / "deck.json"
    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    units_path = work / "units.json"
    units_text = {}
    if units_path.is_file():
        units_text = json.loads(units_path.read_text(encoding="utf-8"))

    counts = {"ok": 0, "overfull": 0, "starved": 0}
    for page in deck.get("pages") or []:
        fit = score_page(page, budgets, units_text)
        page["fit"] = fit
        counts[fit["verdict"]] = counts.get(fit["verdict"], 0) + 1
        print(f"{page.get('id')}\t{page.get('role')}\t{fit['verdict']}\t{fit['budget']}\tchars={fit['chars']}\trows={fit['rows']}")

    if args.write:
        deck_path.write_text(json.dumps(deck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"summary: ok={counts['ok']} overfull={counts['overfull']} starved={counts['starved']}",
        file=sys.stderr,
    )
    fail = args.fail_on
    if fail == "none":
        return 0
    if fail == "overfull" and counts["overfull"]:
        return 1
    if fail == "starved" and counts["starved"]:
        return 1
    if fail == "any" and (counts["overfull"] or counts["starved"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
