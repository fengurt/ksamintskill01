#!/usr/bin/env python3
"""Verify D03.1 / D03.2 / D04 / D05 page counts and formula links against live HTML."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINKS = json.loads((ROOT / "decks/stone-briefing/data/page-links.json").read_text(encoding="utf-8"))
DECKS = {
    "D03.1": ROOT / "decks/stone-briefing/presentation.html",
    "D03.2": ROOT / "decks/stone-briefing/html-v1.html",
    "D04": ROOT / "decks/stone-roadmap/presentation.html",
    "D05": ROOT / "decks/stone-dossier/presentation.html",
}


def main() -> int:
    fails = 0
    for deck_id, path in DECKS.items():
        html_n = len(re.findall(r'<section class="slide', path.read_text(encoding="utf-8")))
        rows = [r for r in LINKS if r["deck_id"] == deck_id]
        charts = [r for r in rows if r.get("job") in {"chart", "chart-table"}]
        linked = [r for r in rows if r.get("formula_id")]
        ok = [r for r in linked if r.get("data_ok")]
        print(f"{deck_id} html={html_n} links={len(rows)} formulas={len(linked)} data_ok={len(ok)}")
        if html_n != len(rows):
            print(f"  FAIL page count html={html_n} links={len(rows)}")
            fails += 1
        bad = [r for r in charts if not r.get("formula_id") or not r.get("data_ok")]
        if bad:
            print(f"  FAIL charts without verified formula {len(bad)}")
            fails += len(bad)
            for r in bad[:8]:
                print(f"    p={r['page']} {r['title']}")
    hit = next(
        (r for r in LINKS if r["deck_id"] == "D03.1" and r.get("job") == "chart" and "275" in (r.get("title") or "")),
        None,
    )
    if not hit or hit.get("formula_id") != "F04":
        print(f"  FAIL 275 chart formula {hit}")
        fails += 1
    else:
        print(f"PASS 275 → {hit['formula_id']} p={hit['page']}")
    print("FAIL" if fails else "PASS", fails, "issues")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
