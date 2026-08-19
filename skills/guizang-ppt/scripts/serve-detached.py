#!/usr/bin/env python3
"""Truly detached no-cache server (double-fork) so it survives shell exit.
Port + dir are configurable via CLI args: serve-detached.py <port> <dir>
"""
import os
import sys
import time
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# Double-fork to fully detach from parent session
if os.fork() > 0:
    os._exit(0)
os.setsid()
if os.fork() > 0:
    os._exit(0)

# Defaults — read port + dir from CLI args
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
chdir_target = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path.cwd()
os.chdir(str(chdir_target))

# Redirect stdio to log
with open('/tmp/ppt-detached.log', 'a') as f:
    os.dup2(f.fileno(), 1)
    os.dup2(f.fileno(), 2)

class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    def log_message(self, fmt, *args):
        with open('/tmp/ppt-detached.log', 'a') as f:
            f.write('%s - %s\n' % (self.address_string(), fmt % args))

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
with open('/tmp/ppt-detached.log', 'a') as f:
    f.write(f'\n[start] {time.strftime("%H:%M:%S")} pid={os.getpid()} port={port}\n')
ThreadingHTTPServer(('127.0.0.1', port), NoCacheHandler).serve_forever()
