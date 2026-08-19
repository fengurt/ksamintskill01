#!/usr/bin/env python3
"""Cache-busting static server for the deck — sends no-cache headers so the
browser always re-fetches the latest version.
"""
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
print(f'no-cache server on http://127.0.0.1:{port}/', file=sys.stderr)
ThreadingHTTPServer(('127.0.0.1', port), NoCacheHandler).serve_forever()
