#!/usr/bin/env python3
"""Lint authored skills: SKILL.md frontmatter name+description required."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def main() -> int:
    errors: list[str] = []
    skills = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    assert skills, "no skills/"
    for skill_dir in skills:
        md = skill_dir / "SKILL.md"
        if not md.is_file():
            errors.append(f"{skill_dir.name}: missing SKILL.md")
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        m = FRONTMATTER_RE.match(text)
        if not m:
            errors.append(f"{skill_dir.name}: missing YAML frontmatter")
            continue
        meta = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        if not meta.get("name"):
            errors.append(f"{skill_dir.name}: frontmatter missing name")
        if not meta.get("description"):
            errors.append(f"{skill_dir.name}: frontmatter missing description")
    if errors:
        print("FAIL lint-skills:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: {len(skills)} skills pass lint")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
