#!/usr/bin/env python3
"""Check D03.1 / D04 / D05 figures: inventory after each figure, no silent row cut."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECKS = (
    ("D03.1", ROOT / "decks/stone-briefing/presentation.html"),
    ("D04", ROOT / "decks/stone-roadmap/presentation.html"),
    ("D05", ROOT / "decks/stone-dossier/presentation.html"),
)
ZW = re.compile(r"[\u2060\u200b\u200c\u200d\ufeff]")


def clean(text: str) -> str:
    return ZW.sub("", re.sub(r"<[^>]+>", "", text or "")).strip()


def parse_slides(path: Path) -> list[dict]:
    html = path.read_text(encoding="utf-8")
    slides = []
    for i, block in enumerate(re.finditer(r"<section class=\"slide[^>]*>.*?</section>", html, re.S), start=1):
        chunk = block.group(0)
        job = re.search(r'data-job="([^"]+)"', chunk)
        fill = re.search(r'data-fill="([^"]+)"', chunk)
        title = re.search(r'class="sd-h2">(.*?)</div>', chunk, re.S)
        chip = re.search(r'class="sd-chip">(.*?)</div>', chunk)
        n_cap = re.search(r">n=(\d+)", chunk)
        fig = re.search(r"图\s+(\d+)", clean(chip.group(1) if chip else ""))
        rows = re.findall(r"<tr>(.*?)</tr>", chunk, re.S)
        data_rows = 0
        for row in rows[1:]:
            if 'class="sd-sum"' in row:
                continue
            data_rows += 1
        slides.append({
            "page": i,
            "job": job.group(1) if job else "",
            "fill": fill.group(1) if fill else "",
            "title": clean(title.group(1) if title else ""),
            "chip": clean(chip.group(1) if chip else ""),
            "fig": int(fig.group(1)) if fig else None,
            "n_plot": int(n_cap.group(1)) if n_cap else None,
            "table_rows": data_rows,
            "has_svg": "<svg" in chunk,
        })
    return slides


def audit_deck(deck_id: str, path: Path) -> dict:
    slides = parse_slides(path)
    figures = [s for s in slides if s["job"] in {"chart", "chart-table"}]
    inv_by_fig: dict[int, list[dict]] = {}
    for s in slides:
        if s["job"] != "roster":
            continue
        if "清单" not in s["chip"] and "清单" not in s["title"]:
            continue
        if s["fig"] is None:
            continue
        inv_by_fig.setdefault(s["fig"], []).append(s)
    missing = []
    truncated = []
    for fig in figures:
        fid = fig["fig"]
        invs = inv_by_fig.get(fid or -1, [])
        inv_rows = sum(s["table_rows"] for s in invs)
        if not invs:
            missing.append(fig)
        plot_n = fig["n_plot"]
        if plot_n is not None and inv_rows and plot_n < inv_rows:
            if fig["fill"] == "hist-cdf":
                continue
            truncated.append({**fig, "inv_rows": inv_rows, "inv_pages": len(invs)})
        elif plot_n is None and inv_rows > 12 and fig["fill"] not in {"bubble", "quadrant", "timeline"}:
            truncated.append({**fig, "inv_rows": inv_rows, "inv_pages": len(invs), "n_plot": "—"})
    return {
        "deck": deck_id,
        "slides": len(slides),
        "figures": len(figures),
        "inventories": sum(len(v) for v in inv_by_fig.values()),
        "missing": missing,
        "truncated": truncated,
        "figure_pages": figures,
        "inv_by_fig": {str(k): v for k, v in inv_by_fig.items()},
    }


def audit_d033() -> dict:
    links = json.loads((ROOT / "decks/stone-briefing/data/page-links.json").read_text(encoding="utf-8"))
    formulas = json.loads((ROOT / "decks/stone-briefing/data/formulas-index.json").read_text(encoding="utf-8"))
    by_deck: dict[str, list] = {}
    for row in links:
        by_deck.setdefault(row["deck_id"], []).append(row)
    out = {"formulas": len(formulas), "decks": {}}
    for deck_id, rows in by_deck.items():
        charts = [r for r in rows if r.get("job") in {"chart", "chart-table"}]
        linked = [r for r in charts if r.get("formula_id")]
        out["decks"][deck_id] = {
            "pages": len(rows),
            "charts": len(charts),
            "charts_linked": len(linked),
            "unlinked_charts": [
                {"page": r["page"], "title": r.get("title"), "job": r.get("job")}
                for r in charts if not r.get("formula_id")
            ],
        }
    return out


def main() -> int:
    reports = [audit_deck(deck_id, path) for deck_id, path in DECKS]
    d033 = audit_d033()
    fails = 0
    for rep in reports:
        print(f"\n{rep['deck']}  slides={rep['slides']}  figures={rep['figures']}  清单页={rep['inventories']}")
        if rep["missing"]:
            fails += len(rep["missing"])
            print(f"  FAIL 无清单 {len(rep['missing'])}")
            for fig in rep["missing"]:
                print(f"    p={fig['page']} 图{fig['fig']} {fig['title']}")
        else:
            print("  PASS 每张 figure 后有清单")
        if rep["truncated"]:
            fails += len(rep["truncated"])
            print(f"  FAIL 图上截行 {len(rep['truncated'])}")
            for fig in rep["truncated"]:
                print(
                    f"    p={fig['page']} 图{fig['fig']} plot={fig['n_plot']} 清单={fig['inv_rows']}行 "
                    f"{fig['fill']} {fig['title']}"
                )
        else:
            print("  PASS 图行数未小于清单")
    print("\n库公式", d033["formulas"])
    for deck_id, row in d033["decks"].items():
        print(f"  {deck_id} pages={row['pages']} charts={row['charts']} linked={row['charts_linked']}")
        if row["unlinked_charts"]:
            fails += len(row["unlinked_charts"])
            print(f"    FAIL 未挂公式 {len(row['unlinked_charts'])}")
            for item in row["unlinked_charts"][:12]:
                print(f"      p={item['page']} {item['title']}")
    print(f"\n{'FAIL' if fails else 'PASS'} {fails} issues")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
