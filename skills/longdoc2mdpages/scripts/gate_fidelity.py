#!/usr/bin/env python3
"""Gate 1 — nothing was lost between the source document and the pages.

Two independent checks, because either alone is easy to pass by accident:
  COVERAGE  every unit id appears exactly once across all pages
  NUMBERS   the multiset of numbers in the source survives into the pack

Data routed to assets/tables/ by the appendix bypass counts as kept, which is
what makes the bypass safe to use aggressively.

  python3 gate_fidelity.py --units units.json --plan deck-plan.json \
      --assets page-pack/assets/tables --out fidelity.json
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def numbers(s: str) -> Counter:
    return Counter(n.replace(",", "").rstrip(".") for n in NUM.findall(s) if len(n) > 1)


def page_text(p: dict) -> str:
    parts = [p.get("title", ""), p.get("takeaway", ""), p.get("source", "")]

    def walk(v):
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, (int, float)):
            parts.append(str(v))
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)

    walk(p.get("content"))
    walk(p.get("blocks"))  # legacy deck-plan
    walk(p.get("provenance"))
    walk(p.get("claim"))
    walk(p.get("evidence"))
    return " ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--assets", default=None)
    ap.add_argument("--out", default="fidelity.json")
    a = ap.parse_args()

    units = json.loads(Path(a.units).read_text(encoding="utf-8"))
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))

    used = Counter(u for p in plan["pages"] for u in (p.get("units") or []))
    missing = sorted(set(units) - set(used))
    dupes = sorted(u for u, n in used.items() if n > 1)
    ghosts = sorted(set(used) - set(units))

    src = Counter()
    for t in units.values():
        src += numbers(t)
    dst = Counter()
    for p in plan["pages"]:
        dst += numbers(page_text(p))
    if a.assets and Path(a.assets).is_dir():
        for f in Path(a.assets).glob("*"):
            if not f.is_file():
                continue
            dst += numbers(f.read_text(encoding="utf-8"))
    lost = sorted(k for k, v in src.items() if dst.get(k, 0) < v)

    findings = []
    if missing: findings.append(("COVERAGE_MISSING", "hard", f"{len(missing)} unit(s) on no page", missing[:20]))
    if dupes:   findings.append(("COVERAGE_DUP", "hard", f"{len(dupes)} unit(s) on more than one page", dupes[:20]))
    if ghosts:  findings.append(("COVERAGE_GHOST", "hard", f"{len(ghosts)} unknown unit id(s)", ghosts[:20]))
    if lost:    findings.append(("NUMBERS_LOST", "warn",
                                 f"{len(lost)} number(s) unreachable from pages or assets", lost[:20]))

    hard = sum(1 for f in findings if f[1] == "hard")
    Path(a.out).write_text(json.dumps(
        {"units": len(units), "pages": len(plan["pages"]), "hard": hard,
         "findings": [{"code": c, "sev": s, "msg": m, "sample": x} for c, s, m, x in findings]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    for c, s, m, _ in findings:
        print(f"  {s.upper():<5} {c:<18} {m}")
    print(f"gate_fidelity: {len(units)} units -> {len(plan['pages'])} pages · hard {hard}")
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
