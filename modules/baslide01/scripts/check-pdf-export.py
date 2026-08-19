#!/usr/bin/env python3
"""Export catalog decks to PDF and assert page count, 16:9, no cite.

D01 增城 is skipped by default (WebGL + ASCII rAF never settle headless
virtual-time). Pass --all or zengcheng-taizikeng to include it.
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = (ROOT / ".dev-url").read_text(encoding="utf-8").strip() if (ROOT / ".dev-url").exists() else "http://127.0.0.1:8765/"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
OUT_DIR = ROOT / "export" / "pdf"

DECKS = (
    ("premium-ppt", "decks/premium-ppt/presentation.html", r'<section class="slide'),
    ("stone-briefing", "decks/stone-briefing/presentation.html", r'class="slide sd-slide'),
    ("stone-html-v1", "decks/stone-briefing/html-v1.html", r'<section class="slide'),
    ("stone-roadmap", "decks/stone-roadmap/presentation.html", r'class="slide sd-slide'),
    ("stone-dossier", "decks/stone-dossier/presentation.html", r'class="slide sd-slide'),
    ("zengcheng-taizikeng", "decks/zengcheng-taizikeng/deck.html", r'class="slide'),
)
OPTIONAL = {"zengcheng-taizikeng"}


def count_slides(html: str, pattern: str) -> int:
    return len(re.findall(pattern, html))


def pdf_info(path: Path) -> tuple[int, float, float]:
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        box = reader.pages[0].mediabox
        return len(reader.pages), float(box.width), float(box.height)
    except Exception:
        pass
    data = path.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page\b", data))
    match = re.search(rb"/MediaBox\s*\[\s*[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)\s*\]", data)
    width = float(match.group(1)) if match else 0.0
    height = float(match.group(2)) if match else 0.0
    return pages, width, height


def print_pdf(url: str, dest: Path, budget_ms: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    cmd = [
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--no-pdf-header-footer",
        f"--virtual-time-budget={budget_ms}",
        f"--print-to-pdf={dest}",
        url,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=max(600, budget_ms // 1000 + 240))
    assert dest.exists() and dest.stat().st_size > 1000, f"empty PDF {dest}"


def selected_decks(argv: list[str]) -> tuple[str, tuple[tuple[str, str, str], ...]]:
    flags = {a for a in argv if a.startswith("--")}
    urls = [a for a in argv if a.startswith("http")]
    names = {a for a in argv if not a.startswith("--") and not a.startswith("http")}
    base = (urls[0] if urls else DEFAULT).rstrip("/") + "/"
    if names:
        unknown = names - {d[0] for d in DECKS}
        if unknown:
            raise SystemExit(f"unknown deck {sorted(unknown)}")
        return base, tuple(d for d in DECKS if d[0] in names)
    if "--all" in flags:
        return base, DECKS
    return base, tuple(d for d in DECKS if d[0] not in OPTIONAL)


def main() -> int:
    base, decks = selected_decks(sys.argv[1:])
    if not CHROME.exists():
        print("FAIL Chrome not found")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fails: list[str] = []

    def ok(cond: bool, msg: str) -> None:
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            fails.append(msg)

    chosen_ids = {d[0] for d in decks}
    for deck_id in OPTIONAL:
        if deck_id not in chosen_ids:
            print(f"SKIP {deck_id} (pass --all or {deck_id} to export)")

    for deck_id, rel, pattern in decks:
        html_path = ROOT / rel
        html = html_path.read_text(encoding="utf-8")
        slides = count_slides(html, pattern)
        ok(slides >= 1, f"{deck_id} slide count {slides}")
        leak = bool(re.search(r"cite\s+index|</?cite\b|&lt;cite", html, re.I))
        ok(not leak, f"{deck_id} HTML has no cite markup")
        sep = "&" if "?" in rel else "?"
        url = urljoin(base, rel) + sep + "export=1&print=1"
        dest = OUT_DIR / f"{deck_id}.pdf"
        budget = max(30000, 8000 + slides * 150)
        t0 = time.time()
        try:
            print_pdf(url, dest, budget)
        except Exception as exc:
            ok(False, f"{deck_id} print-to-pdf {exc}")
            continue
        pages, width, height = pdf_info(dest)
        elapsed = time.time() - t0
        ok(abs(pages - slides) <= 1, f"{deck_id} PDF pages {pages} vs slides {slides} ({elapsed:.1f}s)")
        if width and height:
            aspect = width / height
            ok(1.70 <= aspect <= 1.86, f"{deck_id} PDF aspect {aspect:.3f} ({width:.0f}×{height:.0f})")
        else:
            ok(False, f"{deck_id} PDF missing MediaBox")
        blob = dest.read_bytes()
        ok(b"cite index" not in blob, f"{deck_id} PDF has no cite index")
        print(f"  wrote {dest} {dest.stat().st_size} bytes")

    if fails:
        print(f"\n{len(fails)} failed")
        return 1
    print("\nall PDF exports passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
