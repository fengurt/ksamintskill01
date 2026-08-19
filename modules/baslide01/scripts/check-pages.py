#!/usr/bin/env python3
"""HTTP checks for the local gallery. Exit 1 on any fail."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = (ROOT / ".dev-url").read_text(encoding="utf-8").strip() if (ROOT / ".dev-url").exists() else "http://127.0.0.1:8765/"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url: str, follow: bool = True):
    parts = urlsplit(url)
    quoted = urlunsplit((
        parts.scheme,
        parts.netloc,
        quote(parts.path, safe="/%"),
        parts.query,
        parts.fragment,
    ))
    req = urllib.request.Request(quoted, method="GET")
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=20) as res:
            return res.status, res.headers, res.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read() if exc.fp else b""


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT).rstrip("/")
    fails: list[str] = []

    def ok(cond: bool, msg: str) -> None:
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            fails.append(msg)

    status, _, body = fetch(base + "/page-types.json")
    ok(status == 200, f"page-types.json HTTP {status}")
    types = json.loads(body.decode("utf-8")) if status == 200 else {"types": []}
    ok(len(types.get("types", [])) == 17, f"17 page types (got {len(types.get('types', []))})")
    missing_loop = [t.get("id") for t in types.get("types", []) if not (t.get("loop") or {}).get("prompt")]
    ok(not missing_loop, f"every type has loop prompt ({missing_loop})")

    status, _, cat = fetch(base + "/catalog.json")
    ok(status == 200, f"catalog.json HTTP {status}")
    catalog = json.loads(cat.decode("utf-8")) if status == 200 else {"surfaces": []}

    for surface in catalog.get("surfaces", []):
        path = surface["path"]
        status, _, html = fetch(base + path)
        text = html.decode("utf-8", "replace")
        ok(status == 200, f"{path} HTTP {status}")
        if path.endswith(".html") or path.endswith("/"):
            ok("baslide-chrome.js" in text, f"{path} injects chrome")
        if "stone-" in path or path.endswith("presentation.html"):
            leak = "cite index" in text or "<cite" in text or "&lt;cite" in text
            ok(not leak, f"{path} has no cite markup")
        if path.endswith("/data.html"):
            ok('class="hero"' in text or "class='hero'" in text, f"{path} has hero")
            ok("D03.3" not in text, f"{path} is unnumbered")

    status, _, idx = fetch(base + "/decks/stone-briefing/data/formulas-index.json")
    ok(status == 200, f"formulas-index HTTP {status}")
    if status == 200:
        formulas = {row["id"]: row for row in json.loads(idx.decode("utf-8"))}
        ok(float(formulas.get("F01", {}).get("value", 0)) == 6052, "F01 city 6052")
        ok(float(formulas.get("F07", {}).get("value", 0)) >= 24, "F07 ge20")
    status, _, _ = fetch(base + "/decks/stone-briefing/data/pack.sqlite")
    ok(status == 200, "pack.sqlite HTTP 200")
    status, _, links_body = fetch(base + "/decks/stone-briefing/data/page-links.json")
    ok(status == 200, f"page-links HTTP {status}")
    if status == 200:
        rows = json.loads(links_body.decode("utf-8"))
        linked = sum(1 for row in rows if row.get("formula_id"))
        ok(linked >= 80, f"page-links linked {linked}")

    status, headers, _ = fetch(base + "/demos/TIANSIGHT", follow=False)
    loc = headers.get("Location") if headers else None
    ok(status in {301, 302} and loc and loc.rstrip("?").endswith("/"), f"/demos/TIANSIGHT redirects ({status} {loc})")

    status, _, css = fetch(base + "/assets/baslide-chrome.css")
    text = css.decode("utf-8", "replace") if status == 200 else ""
    ok(status == 200 and "[hidden]" in text and "baslide-chrome-off" in text, "chrome hide CSS")

    for js in (
        "/demos/TIANSIGHT/src/TIANSIGHT.app.js",
        "/demos/TIANSIGHT/src/TIANSIGHT.viz.js",
        "/assets/baslide-chrome.js",
        "/assets/baslide-chrome.css",
        "/assets/baslide-thumbs.css",
        "/assets/baslide-catalog.js",
        "/audit/agent.js",
        "/prompts/loop/brand.md",
        "/prompts/loop/kpi.md",
        "/preview/",
    ):
        status, _, _ = fetch(base + js)
        ok(status == 200, f"{js} HTTP {status}")

    status, _, layouts = fetch(base + "/templates/TIANSIGHT/layouts.html?slide=6")
    text = layouts.decode("utf-8", "replace")
    ok(status == 200 and 'data-page-type="kpi"' in text, "layouts.html kpi type")
    ok("baslide-chrome.js" in text, "layouts.html chrome")

    status, _, home = fetch(base + "/")
    home_text = home.decode("utf-8", "replace")
    ok(status == 200 and "page-types.json" in home_text, "homepage loads page-types.json")
    ok("baslide-thumbs.css" in home_text and "baslide-catalog.js" in home_text, "homepage thumbs")

    status, _, preview = fetch(base + "/preview/?type=kpi&skin=TIANSIGHT")
    prev_text = preview.decode("utf-8", "replace")
    ok(status == 200 and "baslide-catalog.js" in prev_text, "preview page")

    if fails:
        print(f"\n{len(fails)} failed")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
