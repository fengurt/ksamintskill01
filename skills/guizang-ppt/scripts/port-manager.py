#!/usr/bin/env python3
"""
Port manager for the deck local server.

Functions:
  1. check_port(port)           - check if a port is free (returns True/False)
  2. find_free_port(start)        - find first free port starting from `start`
  3. kill_existing(name)         - kill any existing process matching `name`
  4. serve(start_port=8765)       - main entry: kill old, find free, daemonize serve-detached
  5. status()                     - show current status of all listening processes

Usage:
  python3 port-manager.py serve
  python3 port-manager.py status
  python3 port-manager.py kill
  python3 port-manager.py free 9000
"""
import os
import re
import sys
import time
import socket
import signal
import subprocess
from pathlib import Path
from typing import Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
SCRIPT_NAME = 'serve-detached.py'
LOG_FILE = '/tmp/ppt-detached.log'
DEFAULT_START_PORT = 8765
PORT_RANGE = 50  # how many ports to scan if all occupied


def is_port_free(port: int) -> bool:
    """Return True if `port` is not bound on 127.0.0.1."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False


def find_free_port(start: int = DEFAULT_START_PORT, exclude: Optional[set] = None) -> int:
    """Find first free port starting from `start` (excluding ports in `exclude`).
    Raises RuntimeError if none found within PORT_RANGE."""
    exclude = exclude or set()
    for p in range(start, start + PORT_RANGE):
        if p in exclude:
            continue
        if is_port_free(p):
            return p
    raise RuntimeError(f'No free port found between {start} and {start + PORT_RANGE}')


def listening_pids() -> list[tuple[int, str]]:
    """Return list of (pid, command) for processes listening on TCP ports (using lsof)."""
    try:
        out = subprocess.check_output(
            ['lsof', '-nP', '-iTCP', '-sTCP:LISTEN'],
            stderr=subprocess.DEVNULL, text=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    results = []
    seen_pids = set()
    for line in out.split('\n')[1:]:  # skip header
        m = re.search(r'^\S+\s+(\d+)\s+\S+', line)
        if m:
            pid = int(m.group(1))
            if pid in seen_pids:
                continue
            seen_pids.add(pid)
            results.append((pid, line.strip()))
    return results


def kill_existing(name: str = SCRIPT_NAME) -> int:
    """Kill any process whose command line contains `name`. Returns count killed."""
    killed = 0
    try:
        out = subprocess.check_output(['pgrep', '-f', name], text=True)
    except subprocess.CalledProcessError:
        return 0
    for line in out.strip().split('\n'):
        if not line:
            continue
        try:
            pid = int(line)
        except ValueError:
            continue
        try:
            os.kill(pid, signal.SIGKILL)
            killed += 1
            print(f'  killed pid={pid}')
        except ProcessLookupError:
            pass
    return killed


def status() -> None:
    """Print a table of current listening processes."""
    print('=' * 70)
    print('Listening TCP processes on 127.0.0.1')
    print('=' * 70)
    pids = listening_pids()
    if not pids:
        print('(none)')
        return
    for pid, line in pids:
        print(f'  pid={pid:6d}  {line[:100]}')


def find_deck_process() -> Optional[int]:
    """Find the PID of the running serve-detached.py process."""
    try:
        out = subprocess.check_output(['pgrep', '-f', SCRIPT_NAME], text=True).strip()
    except subprocess.CalledProcessError:
        return None
    if not out:
        return None
    try:
        return int(out.split('\n')[0])
    except (ValueError, IndexError):
        return None


def free_port(start: int) -> None:
    """Find and print first free port from `start`."""
    p = find_free_port(start)
    print(f'First free port from {start}: {p}')


def serve(start_port: int = DEFAULT_START_PORT) -> None:
    """Kill old instance, find free port, start serve-detached in background."""
    print('=== Port manager: serve ===')
    # 1. Kill existing
    existing = find_deck_process()
    if existing:
        print(f'Found existing serve-detached.py pid={existing}, killing...')
        kill_existing()
        time.sleep(0.5)
    # 2. Check requested port
    port = start_port
    if not is_port_free(port):
        print(f'Port {port} is occupied, scanning for free port...')
        try:
            port = find_free_port(start_port)
        except RuntimeError as e:
            print(f'ERROR: {e}')
            sys.exit(1)
    # 3. Start the server
    print(f'Starting serve-detached.py on port {port}...')
    proc = subprocess.Popen(
        ['python3', str(SCRIPTS_DIR / SCRIPT_NAME), str(port), str(ROOT)],
        stdout=open(LOG_FILE, 'ab'),
        stderr=subprocess.STDOUT,
        start_new_session=True,  # detach from parent
    )
    # 4. Verify
    time.sleep(1.5)
    if is_port_free(port):
        print(f'ERROR: server did not bind to {port} (check {LOG_FILE})')
        sys.exit(1)
    print(f'✓ Server up on http://127.0.0.1:{port}/')
    print(f'  log: {LOG_FILE}')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == 'serve':
        port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_START_PORT
        serve(port)
    elif cmd == 'status':
        status()
    elif cmd == 'kill':
        n = kill_existing()
        print(f'Killed {n} process(es)')
    elif cmd == 'free':
        start = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_START_PORT
        free_port(start)
    else:
        print(f'Unknown command: {cmd}')
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
