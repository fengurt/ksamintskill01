#!/usr/bin/env python3
"""No-cache static server. Injects 首页 / 审计 chrome into every HTML page."""
from __future__ import annotations

import argparse
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

CHROME_MARK = b"baslide-chrome.js"
CHROME_SNIPPET = (
    b'\n<link rel="stylesheet" href="/assets/baslide-chrome.css">'
    b'\n<script src="/assets/baslide-chrome.js" defer></script>\n'
)


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:
        if self._redirect_dir_slash():
            return
        if self._serve_html_with_chrome():
            return
        super().do_GET()

    def _redirect_dir_slash(self) -> bool:
        parsed = urlparse(self.path)
        rel = unquote(parsed.path)
        if rel.endswith("/") or not rel:
            return False
        target = (Path.cwd() / rel.lstrip("/")).resolve()
        try:
            target.relative_to(Path.cwd())
        except ValueError:
            return False
        if not target.is_dir():
            return False
        location = quote(rel, safe="/") + "/"
        if parsed.query:
            location += "?" + parsed.query
        self.send_response(301)
        self.send_header("Location", location)
        self.end_headers()
        return True

    def _html_file(self) -> Path | None:
        parsed = urlparse(self.path)
        rel = unquote(parsed.path).lstrip("/")
        root = Path.cwd()
        target = (root / rel).resolve() if rel else root
        try:
            target.relative_to(root)
        except ValueError:
            return None
        if target.is_dir():
            for name in ("index.html", "index.htm"):
                candidate = target / name
                if candidate.is_file():
                    return candidate
            return None
        if target.is_file() and target.suffix.lower() in {".html", ".htm"}:
            return target
        return None

    def _serve_html_with_chrome(self) -> bool:
        html_path = self._html_file()
        if html_path is None:
            return False
        started = __import__("time").perf_counter()
        data = html_path.read_bytes()
        injected = CHROME_MARK not in data
        if injected:
            lower = data.lower()
            idx = lower.rfind(b"</body>")
            if idx >= 0:
                data = data[:idx] + CHROME_SNIPPET + data[idx:]
            else:
                data = data + CHROME_SNIPPET
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        # region agent log
        try:
            import json, time
            from pathlib import Path
            rec = {
                "sessionId": "1a3c9c",
                "runId": "pre-fix",
                "hypothesisId": "H6",
                "location": "scripts/serve.py:_serve_html_with_chrome",
                "message": "html served",
                "data": {
                    "path": self.path[:180],
                    "bytes": len(data),
                    "injected": injected,
                    "ms": round((__import__("time").perf_counter() - started) * 1000, 2),
                },
                "timestamp": int(time.time() * 1000),
            }
            with Path("/Users/af/cpro01/0thebrain01/baslide01/.cursor/debug-1a3c9c.log").open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass
        # endregion
        return True


def bind_server(host: str, start_port: int) -> ThreadingHTTPServer:
    last_error = None
    for port in range(start_port, start_port + 50):
        try:
            return ThreadingHTTPServer((host, port), NoCacheHandler)
        except OSError as exc:
            last_error = exc
            continue
    raise RuntimeError(f"No free port found between {start_port} and {start_port + 49}: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve baslide01 with no-cache headers.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--dir", default=".", help="Directory to serve")
    args = parser.parse_args()

    root = Path(args.dir).resolve()
    os.chdir(root)
    httpd = bind_server(args.host, args.port)
    host, port = httpd.server_address[:2]
    print(f"baslide01 http://{host}:{port}/", flush=True)
    print(f"root {root}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
