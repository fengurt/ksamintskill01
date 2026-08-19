#!/usr/bin/env python3
"""Acceptance harness: from index.json build outline.md + deck.json that closes.

Groups units by heading_path leaf, packs into pages respecting budgets.json,
emits overflow chains when overfull. Used to prove gates on long fixtures
without requiring an LLM for stages b–d.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

BULLET_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s+", re.M)
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$", re.M)


def table_rows(text: str) -> int:
    rows = [ln for ln in text.splitlines() if TABLE_ROW_RE.match(ln)]
    data = [r for r in rows if not re.match(r"^\|?\s*:?-{3,}", r.strip())]
    return max(0, len(data) - 1) if data else 0


def pick_role(units: list[dict], texts: dict[str, str]) -> str:
    kinds = [u["kind"] for u in units]
    if all(k == "heading" for k in kinds):
        return "chapter"
    if "table" in kinds:
        return "roster" if any(table_rows(texts.get(u["id"], "")) >= 4 for u in units) else "chart-table"
    if "list" in kinds and sum(1 for u in units if u["kind"] == "list") >= 1:
        blob = "\n".join(texts.get(u["id"], "") for u in units)
        if len(BULLET_RE.findall(blob)) <= 6 and any(u["kind"] == "number-block" for u in units):
            return "kpi"
        return "statement"
    if "number-block" in kinds:
        return "kpi"
    if "quote" in kinds:
        return "statement"
    if "figure" in kinds or "code" in kinds:
        return "chart"
    return "statement"


def resplit_overfull(pages: list[dict], texts: dict[str, str], budgets: dict) -> list[dict]:
    """Guarantee no multi-unit page exceeds role budget; split greedily."""
    out: list[dict] = []
    for page in pages:
        role = page.get("role") or "statement"
        b = budgets["roles"].get(role) or budgets["roles"]["statement"]
        uids = list(page.get("units") or [])
        if not uids:
            out.append(page)
            continue
        batch: list[str] = []
        for uid in uids:
            trial = batch + [uid]
            blob = "\n".join(texts.get(u, "") for u in trial)
            rows = sum(table_rows(texts.get(u, "")) for u in trial)
            bullets = len(BULLET_RE.findall(blob))
            fits = (
                len(blob) <= b.get("chars_max", 10**9)
                and rows <= b.get("rows_max", 10**9)
                and bullets <= b.get("bullets_max", 10**9)
            )
            if batch and not fits:
                out.append({**page, "units": batch, "overflow_of": None})
                batch = [uid]
                # role may change for remaining — keep page role for overflow chain
            else:
                batch = trial
        if batch:
            out.append({**page, "units": batch, "overflow_of": None})
    for idx, page in enumerate(out, start=1):
        page["id"] = f"p-{idx:04d}"
    return out


def merge_starved(pages: list[dict], texts: dict[str, str], budgets: dict) -> list[dict]:
    """Merge consecutive thin pages that share outline_path when the result fits."""
    if not pages:
        return pages
    out: list[dict] = []
    i = 0
    while i < len(pages):
        cur = dict(pages[i])
        while i + 1 < len(pages):
            nxt = pages[i + 1]
            if cur.get("outline_path") != nxt.get("outline_path"):
                break
            cur_blob = "\n".join(texts.get(uid, "") for uid in (cur.get("units") or []))
            role = cur.get("role") or "statement"
            b = budgets["roles"].get(role) or budgets["roles"]["statement"]
            # Only merge when current page is below chars_min (starved candidate)
            if len(cur_blob) >= b.get("chars_min", 0):
                break
            trial_units = (cur.get("units") or []) + (nxt.get("units") or [])
            trial_role = nxt.get("role") if cur.get("role") == "chapter" else (cur.get("role") or "statement")
            if trial_role == "chapter":
                trial_role = nxt.get("role") or "statement"
            tb = budgets["roles"].get(trial_role) or budgets["roles"]["statement"]
            blob = "\n".join(texts.get(uid, "") for uid in trial_units)
            rows = max((table_rows(texts.get(uid, "")) for uid in trial_units), default=0)
            bullets = len(BULLET_RE.findall(blob))
            if (
                len(blob) <= tb.get("chars_max", 10**9)
                and rows <= tb.get("rows_max", 10**9)
                and bullets <= tb.get("bullets_max", 10**9)
            ):
                cur = {
                    **cur,
                    "units": trial_units,
                    "role": trial_role,
                    "title": cur.get("title") or nxt.get("title"),
                    "overflow_of": None,
                }
                i += 1
                continue
            break
        out.append(cur)
        i += 1
    for idx, page in enumerate(out, start=1):
        page["id"] = f"p-{idx:04d}"
        page["overflow_of"] = None
    return out


def pack_pages(
    group_units: list[dict],
    texts: dict[str, str],
    budgets: dict,
    path: list[str],
    page_seq: list[int],
) -> list[dict]:
    """Greedy pack units into pages; overflow when overfull."""
    pages: list[dict] = []
    i = 0
    while i < len(group_units):
        role = pick_role(group_units[i : i + 1], texts)
        b = budgets["roles"].get(role) or budgets["roles"]["statement"]
        batch = [group_units[i]]
        i += 1
        # Try to merge following units under same path while under budget
        while i < len(group_units):
            trial = batch + [group_units[i]]
            trial_role = pick_role(trial, texts)
            tb = budgets["roles"].get(trial_role) or b
            blob = "\n".join(texts.get(u["id"], "") for u in trial)
            rows = sum(table_rows(texts.get(u["id"], "")) for u in trial)
            bullets = len(BULLET_RE.findall(blob))
            if (
                len(blob) <= tb.get("chars_max", 10**9)
                and rows <= tb.get("rows_max", 10**9)
                and bullets <= tb.get("bullets_max", 10**9)
            ):
                batch = trial
                role = trial_role
                b = tb
                i += 1
            else:
                break

        page_seq[0] += 1
        pid = f"p-{page_seq[0]:04d}"
        title_src = path[-1] if path else batch[0]["digest"][:60]
        title = title_src
        pages.append(
            {
                "id": pid,
                "role": role,
                "outline_path": path,
                "title": title,
                "units": [u["id"] for u in batch],
                "overflow_of": None,
                "material": {"bullets": [], "table": {}, "numbers": [], "quote": None},
                "source": "",
                "how_to_read": "",
                "takeaway": "",
                "notes": "",
            }
        )
    # Mark overflow chains when consecutive pages share outline_path and role and later ones are continuations
    # For overfull single-unit pages already split by pack — link siblings with same path+role
    by_key: dict[tuple, list[dict]] = defaultdict(list)
    for p in pages:
        by_key[(tuple(p["outline_path"]), p["role"])].append(p)
    for group in by_key.values():
        if len(group) <= 1:
            continue
        parent = group[0]["id"]
        for idx, p in enumerate(group[1:], start=2):
            p["overflow_of"] = parent
            if not p["title"].endswith("续"):
                p["title"] = f"{group[0]['title']} 续"
            if idx == len(group):
                p["takeaway"] = p.get("takeaway") or "（溢出链末页）"
    return pages


def write_outline(index: dict, out: Path) -> None:
    lines = [
        f"# Outline — {index.get('source') or ''}",
        "",
        "Every unit id appears exactly once.",
        "",
    ]
    groups: dict[tuple[str, ...], list] = defaultdict(list)
    for u in index["units"]:
        groups[tuple(u["heading_path"] or ("(root)",))].append(u)

    seen_prefixes: set[tuple[str, ...]] = set()
    for path in sorted(groups.keys(), key=lambda p: p):
        for depth in range(1, len(path) + 1):
            prefix = path[:depth]
            if prefix in seen_prefixes:
                continue
            seen_prefixes.add(prefix)
            indent = "  " * (depth - 1)
            here = groups.get(prefix, [])
            if here:
                ids = " ".join(u["id"] for u in here)
                lines.append(f"{indent}- {prefix[-1]}（{ids}）")
            else:
                lines.append(f"{indent}- {prefix[-1]}")

    lines += ["", "```mermaid", "mindmap", "  root((doc))"]
    tops = sorted({p[0] for p in groups if p})
    for title in tops[:40]:
        safe = re.sub(r"[^\w\u4e00-\u9fff\- ]", "", title)[:40] or "node"
        lines.append(f"    {safe}")
    lines += ["```", ""]
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", required=True)
    parser.add_argument(
        "--budgets",
        default=str(Path(__file__).resolve().parent.parent / "budgets.json"),
    )
    args = parser.parse_args()
    work = Path(args.work)
    index = json.loads((work / "index.json").read_text(encoding="utf-8"))
    texts = {}
    units_path = work / "units.json"
    if units_path.is_file():
        texts = json.loads(units_path.read_text(encoding="utf-8"))
    budgets = json.loads(Path(args.budgets).read_text(encoding="utf-8"))

    write_outline(index, work / "outline.md")

    groups: dict[tuple[str, ...], list] = defaultdict(list)
    for u in index["units"]:
        groups[tuple(u["heading_path"] or ("(root)",))].append(u)

    page_seq = [0]
    pages: list[dict] = []
    # Cover page from first heading if any
    if index["units"]:
        page_seq[0] += 1
        first = index["units"][0]
        pages.append(
            {
                "id": f"p-{page_seq[0]:04d}",
                "role": "cover",
                "outline_path": [],
                "title": (first["heading_path"][0] if first["heading_path"] else "Deck"),
                "units": [],
                "overflow_of": None,
                "material": {"bullets": [], "table": {}, "numbers": [], "quote": None},
                "source": "",
                "how_to_read": "",
                "takeaway": "",
                "notes": "cover scaffold",
            }
        )

    for path, units in sorted(groups.items(), key=lambda kv: kv[0]):
        pages.extend(pack_pages(units, texts, budgets, list(path), page_seq))

    # Optional coalesce of thin pages (disabled when it would create overfull)
    pages = merge_starved(pages, texts, budgets)
    # Drop pages that are still overfull by splitting at unit boundaries
    pages = resplit_overfull(pages, texts, budgets)

    deck = {
        "version": "1.0.0",
        "source": index.get("source") or "",
        "outline": str(work / "outline.md"),
        "pages": pages,
    }
    (work / "deck.json").write_text(
        json.dumps(deck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    pages_dir = work / "pages"
    pages_dir.mkdir(exist_ok=True)
    for p in pages:
        md = [
            f"# {p['title']}",
            "",
            f"role: `{p['role']}`",
            f"units: {' '.join(p['units']) or '(none)'}",
            "",
        ]
        for uid in p["units"]:
            md.append(f"## {uid}")
            md.append("")
            md.append(texts.get(uid, ""))
            md.append("")
        (pages_dir / f"{p['id']}.md").write_text("\n".join(md), encoding="utf-8")

    print(f"outline+deck: pages={len(pages)} units={index['total_units']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
