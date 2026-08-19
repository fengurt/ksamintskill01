#!/usr/bin/env python3
"""Assert generated TIANSIGHT decks have complete canvas copy."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = (ROOT / ".dev-url").read_text(encoding="utf-8").strip() if (ROOT / ".dev-url").exists() else "http://127.0.0.1:8765/"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DECKS = (
    ROOT / "decks/stone-briefing/presentation.html",
    ROOT / "decks/stone-roadmap/presentation.html",
    ROOT / "decks/stone-dossier/presentation.html",
)


def strip_nodes_by_class(html_text: str, cls: str) -> str:
    token = f'class="{cls}"'
    out: list[str] = []
    i = 0
    while True:
        hit = html_text.find(token, i)
        if hit < 0:
            out.append(html_text[i:])
            return "".join(out)
        start = html_text.rfind("<", i, hit + 1)
        if start < 0:
            out.append(html_text[i:])
            return "".join(out)
        depth = 0
        k = start
        closed = False
        while k < len(html_text):
            if html_text.startswith("</", k):
                end = html_text.find(">", k)
                depth -= 1
                k = end + 1 if end >= 0 else len(html_text)
                if depth <= 0:
                    out.append(html_text[i:start])
                    i = k
                    closed = True
                    break
            elif html_text.startswith("<", k):
                end = html_text.find(">", k)
                tag = html_text[k:end + 1] if end >= 0 else ""
                if tag.endswith("/>") or tag.lower().startswith(("<br", "<img", "<hr", "<meta", "<link", "<input")):
                    k = end + 1 if end >= 0 else len(html_text)
                else:
                    depth += 1
                    k = end + 1 if end >= 0 else len(html_text)
            else:
                k += 1
        if not closed:
            out.append(html_text[i:])
            return "".join(out)


def static_check() -> list[str]:
    fails: list[str] = []
    for path in DECKS:
        html = path.read_text(encoding="utf-8")
        slides_html = "".join(re.findall(r"<section class=\"slide.*?</section>", html, re.S))
        canvas = strip_nodes_by_class(slides_html, "sd-rail")
        leak = re.search(r"…|\.\.\.", canvas)
        if leak:
            fails.append(f"{path.name} canvas ellipsis {canvas[leak.start() - 20:leak.start() + 20]!r}")
    return fails


def chrome_check(base: str) -> list[str]:
    if not CHROME.exists():
        return []
    url = base.rstrip("/") + "/audit/canvas-copy.html?run=1"
    dest = ROOT / "export" / "canvas-copy-audit.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--virtual-time-budget=90000",
        f"--dump-dom",
        url,
    ]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=180)
    html = proc.stdout
    dest.write_text(html, encoding="utf-8")
    match = re.search(r'<pre id="out">([\s\S]*?)</pre>', html)
    if not match:
        return ["chrome audit missing #out"]
    raw = match.group(1)
    raw = raw.replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        return [f"chrome audit JSON {raw[:200]!r}"]
    items = report.get("items") or []
    return [f"{row.get('kind')} {row.get('deck')}#p={row.get('page')} {row.get('text')}" for row in items]


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    fails = static_check()
    fails.extend(chrome_check(base))
    for row in fails:
        print("FAIL " + row)
    if fails:
        print(f"\n{len(fails)} failed")
        return 1
    print("PASS canvas copy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
