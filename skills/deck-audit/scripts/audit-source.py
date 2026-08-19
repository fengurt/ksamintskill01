#!/usr/bin/env python3
"""Hop1: compare source unit anchors to page material. Emits audit-source.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HARD = {"MISS", "ALTER", "INVENT"}
WARN = {"ORDER", "DENOM", "PROSE"}

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anchors_lib import NUMERIC_KINDS, extract_from_text  # noqa: E402

DENOM_HINT = re.compile(r"(口径|分母|基准|denom|denominator|开台数|营业天)", re.I)


def load_accepted(path: Path | None) -> set[tuple[str, str, str]]:
    if not path or not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    out: set[tuple[str, str, str]] = set()
    for row in data if isinstance(data, list) else []:
        out.add((row.get("page", ""), row.get("code", ""), row.get("anchor", "")))
    return out


def is_accepted(
    accepted: set[tuple[str, str, str]], page: str, code: str, anchor: str
) -> bool:
    return (page, code, anchor) in accepted


def near_miss(a: str, b: str) -> bool:
    """True if same digit length / similar shape but different value."""
    if a == b:
        return False
    da = re.sub(r"[^\d.]", "", a)
    db = re.sub(r"[^\d.]", "", b)
    if not da or not db or da == db:
        return False
    if abs(len(da) - len(db)) > 1:
        return False
    # same length digits, at most 2 positions differ
    if len(da) == len(db):
        diffs = sum(1 for x, y in zip(da, db) if x != y)
        return 1 <= diffs <= 2
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="deck-audit hop1 source→pages")
    parser.add_argument("--work", required=True)
    parser.add_argument(
        "--accepted",
        default=None,
        help="Path to accepted.json (default: skill accepted.json then work/accepted.json)",
    )
    args = parser.parse_args()
    work = Path(args.work)
    anchors_path = work / "anchors.json"
    if not anchors_path.is_file():
        # auto-extract
        import subprocess

        subprocess.check_call(
            [sys.executable, str(Path(__file__).with_name("extract-anchors.py")), "--work", str(work)]
        )
    anchors = json.loads(anchors_path.read_text(encoding="utf-8"))
    deck = json.loads((work / "deck.json").read_text(encoding="utf-8"))
    units = json.loads((work / "units.json").read_text(encoding="utf-8"))

    skill_accepted = Path(__file__).resolve().parent.parent / "accepted.json"
    work_accepted = work / "accepted.json"
    accepted_path = Path(args.accepted) if args.accepted else (
        work_accepted if work_accepted.is_file() else skill_accepted
    )
    accepted = load_accepted(accepted_path)

    findings: list[dict] = []
    pages = deck.get("pages") or []

    for page in pages:
        pid = page["id"]
        unit_ids = page.get("units") or []
        mat_list = anchors["material"].get(pid) or []
        mat_by_norm = {a["norm"]: a for a in mat_list}
        mat_norms = set(mat_by_norm)

        # Collect source anchors for claimed units
        src_anchors: list[dict] = []
        for uid in unit_ids:
            src_anchors.extend(anchors["source"].get(uid) or [])

        src_by_norm: dict[str, dict] = {}
        for a in src_anchors:
            src_by_norm.setdefault(a["norm"], a)

        # MISS: source numeric/table/proper in units but not on page
        for norm, a in src_by_norm.items():
            if a["kind"] not in NUMERIC_KINDS and a["kind"] != "proper-noun":
                continue
            if a["kind"] == "proper-noun":
                # CJK nouns ≥2 chars, or multi-word English titles only
                if re.search(r"[\u4e00-\u9fff]", a["raw"]):
                    if len(re.sub(r"\s+", "", a["raw"])) < 3:
                        continue
                elif " " not in a["raw"].strip():
                    continue
            if norm in mat_norms:
                continue
            # Proper nouns: if the phrase is still on the page, extractor chunking is not a drop
            if a["kind"] == "proper-noun":
                mat_text_path = work / "pages" / f"{pid}.md"
                mat_blob = mat_text_path.read_text(encoding="utf-8") if mat_text_path.is_file() else ""
                if a["raw"] and a["raw"] in mat_blob:
                    continue
            # ALTER: near-miss against material (numeric kinds only)
            altered = None
            if a["kind"] in NUMERIC_KINDS:
                for mn, ma in mat_by_norm.items():
                    if ma["kind"] in NUMERIC_KINDS and near_miss(norm, mn):
                        altered = ma
                        break
            if altered:
                code = "ALTER"
                detail = f"source {a['raw']} ≈ page {altered['raw']}"
                anchor_raw = a["raw"]
            else:
                code = "MISS"
                detail = f"unit {a.get('origin')} → missing on {pid}"
                anchor_raw = a["raw"]
            if is_accepted(accepted, pid, code, anchor_raw):
                continue
            findings.append(
                {
                    "page": pid,
                    "code": code,
                    "severity": "hard",
                    "anchor": anchor_raw,
                    "kind": a["kind"],
                    "detail": detail,
                }
            )

        # INVENT: page numeric anchors not in any claimed unit (skip empty-unit scaffolds)
        if unit_ids:
            title_blob = " ".join(
                [
                    page.get("title") or "",
                    " ".join(page.get("outline_path") or []),
                ]
            )
            title_norms = {a["norm"] for a in extract_from_text(title_blob, "title")}
            for norm, a in mat_by_norm.items():
                if a["kind"] not in NUMERIC_KINDS:
                    continue
                if norm in src_by_norm:
                    continue
                if norm in title_norms:
                    continue
                # section indexes like 0.1 / 1.2.3 are outline crumbs, not inventions
                if re.fullmatch(r"\d+(?:\.\d+)+", a["raw"].strip()):
                    continue
                if is_accepted(accepted, pid, "INVENT", a["raw"]):
                    continue
                findings.append(
                    {
                        "page": pid,
                        "code": "INVENT",
                        "severity": "hard",
                        "anchor": a["raw"],
                        "kind": a["kind"],
                        "detail": f"on {pid} but not in units {unit_ids}",
                    }
                )

        # DENOM warn: page has percent but unit texts had denom hints not on page
        mat_text_path = work / "pages" / f"{pid}.md"
        mat_text = mat_text_path.read_text(encoding="utf-8") if mat_text_path.is_file() else ""
        has_pct = any(a["kind"] == "percent" for a in mat_list)
        if has_pct and unit_ids:
            unit_blob = "\n".join(units.get(uid, "") for uid in unit_ids)
            if DENOM_HINT.search(unit_blob) and not DENOM_HINT.search(mat_text):
                if not is_accepted(accepted, pid, "DENOM", "%"):
                    findings.append(
                        {
                            "page": pid,
                            "code": "DENOM",
                            "severity": "warn",
                            "anchor": "%",
                            "kind": "percent",
                            "detail": "percent on page; denom/口径 line in units but not in material",
                        }
                    )

    hard = [f for f in findings if f["code"] in HARD]
    warn = [f for f in findings if f["code"] in WARN]
    report = {
        "version": "1.0.0",
        "hop": "source",
        "work": str(work),
        "accepted_path": str(accepted_path),
        "counts": {
            "pages": len(pages),
            "hard": len(hard),
            "warn": len(warn),
            "by_code": {
                code: sum(1 for f in findings if f["code"] == code)
                for code in sorted({f["code"] for f in findings})
            },
        },
        "findings": findings,
    }
    out_path = work / "audit-source.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"hop1: pages={len(pages)} hard={len(hard)} warn={len(warn)} → {out_path}",
        file=sys.stderr,
    )
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
