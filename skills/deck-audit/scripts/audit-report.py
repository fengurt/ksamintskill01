#!/usr/bin/env python3
"""Merge hop1/hop2 JSON into audit.md (failures first)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_optional(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Write deck-audit audit.md")
    parser.add_argument("--work", required=True)
    args = parser.parse_args()
    work = Path(args.work)
    src = load_optional(work / "audit-source.json")
    html = load_optional(work / "audit-html.json")

    findings: list[dict] = []
    if src:
        for f in src.get("findings") or []:
            findings.append({**f, "hop": "source"})
    if html:
        for f in html.get("findings") or []:
            findings.append({**f, "hop": "html"})

    hard = [f for f in findings if f.get("severity") == "hard"]
    warn = [f for f in findings if f.get("severity") == "warn"]

    lines = [
        "# Deck audit",
        "",
        f"- work: `{work}`",
        f"- hop1: {'yes' if src else 'no'} · hop2: {'yes' if html else 'no'}",
        f"- hard: **{len(hard)}** · warn: **{len(warn)}**",
        "",
    ]
    if src:
        c = src.get("counts") or {}
        lines.append(
            f"- source pages: {c.get('pages')} · hard {c.get('hard')} · warn {c.get('warn')} · by_code {c.get('by_code')}"
        )
    if html:
        c = html.get("counts") or {}
        lines.append(
            f"- html slides: {c.get('slides')} · mapped {c.get('mapped')} · hard {c.get('hard')} · warn {c.get('warn')} · by_code {c.get('by_code')}"
        )
    lines.append("")

    def emit_block(title: str, items: list[dict]) -> None:
        if not items:
            return
        lines.append(f"## {title}")
        lines.append("")
        # group by page
        by_page: dict[str, list[dict]] = {}
        for f in items:
            key = f.get("page") or f"(slide {f.get('slide')})"
            by_page.setdefault(str(key), []).append(f)
        for page, rows in sorted(by_page.items()):
            lines.append(f"### {page}")
            for f in rows:
                slide = f" slide={f['slide']}" if f.get("slide") is not None else ""
                lines.append(
                    f"- `{f['code']}` ({f['hop']}{slide}) {f.get('anchor','')} — {f.get('detail','')}"
                )
            lines.append("")

    emit_block("FAIL", hard)
    emit_block("WARN", warn)
    if not findings:
        lines.append("## PASS")
        lines.append("")
        lines.append("No findings.")
        lines.append("")

    out = work / "audit.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"report → {out} (hard={len(hard)} warn={len(warn)})", file=sys.stderr)
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
