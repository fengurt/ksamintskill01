#!/usr/bin/env python3
"""Shallow-clone / refresh upstream skill libraries into vendor/ (gitignored)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = Path(os.environ.get("VENDOR_ROOT", ROOT / "vendor")).expanduser().resolve()
SOURCES = ROOT / "registry" / "sources.yaml"


def parse_sources(text: str) -> list[dict]:
    blocks = re.split(r"\n\s*-\s+id:\s*", text)
    entries: list[dict] = []
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        eid = lines[0].strip()
        data: dict = {"id": eid}
        for line in lines[1:]:
            m = re.match(r"\s*([a-z_]+):\s*(.*)$", line)
            if not m:
                continue
            key, value = m.group(1), m.group(2).strip().strip('"').strip("'")
            if key == "exclude_paths":
                continue
            data[key] = value
        excl = re.findall(r"^\s+-\s+(\S+)$", block, re.M)
        data["exclude_paths"] = [item for item in excl if "/" in item]
        entries.append(data)
    return entries


def sync_git(entry: dict, dest: Path) -> None:
    url = entry["url"]
    pin = entry.get("synced_commit") or entry.get("pin", "main")
    depth = str(entry.get("depth", "1"))
    if dest.exists() and (dest / ".git").exists():
        print(f"update {entry['id']}")
        subprocess.check_call(
            ["git", "-C", str(dest), "fetch", "--depth", depth, "origin", pin]
        )
        subprocess.check_call(["git", "-C", str(dest), "checkout", "-q", "FETCH_HEAD"])
    else:
        if dest.exists():
            shutil.rmtree(dest)
        print(f"clone {entry['id']}")
        subprocess.check_call(["git", "clone", "--depth", depth, "--no-checkout", url, str(dest)])
        subprocess.check_call(["git", "-C", str(dest), "fetch", "--depth", depth, "origin", pin])
        subprocess.check_call(["git", "-C", str(dest), "checkout", "-q", "FETCH_HEAD"])
    expected = entry.get("synced_commit")
    if expected:
        head = subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"], text=True).strip()
        if head != expected:
            raise RuntimeError(f"{entry['id']} expected {expected}, got {head}")
    for rel in entry.get("exclude_paths") or []:
        path = dest / rel
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"  excluded {rel}")


def sync_local(entry: dict, dest: Path) -> None:
    path = Path(os.path.expanduser(entry["path"]))
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    if not path.exists():
        print(f"skip missing local {entry['id']}: {path}")
        return
    dest.symlink_to(path)
    print(f"link {entry['id']} -> {path}")


def main() -> int:
    VENDOR.mkdir(parents=True, exist_ok=True)
    entries = parse_sources(SOURCES.read_text(encoding="utf-8"))
    git_only = "--git-only" in sys.argv[1:]
    production = "--production" in sys.argv[1:]
    for entry in entries:
        if production:
            if entry.get("publish") != "true":
                continue
            if entry.get("kind") != "git" or not re.fullmatch(r"[0-9a-f]{40}", entry.get("synced_commit", "")):
                raise ValueError("Published sources require a Git source and full synced_commit")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", entry["id"]):
            raise ValueError("Invalid source id")
        dest = VENDOR / entry["id"]
        kind = entry.get("kind")
        if kind == "git":
            sync_git(entry, dest)
        elif kind == "local":
            if git_only:
                continue
            sync_local(entry, dest)
        else:
            print(f"unknown kind for {entry['id']}: {kind}", file=sys.stderr)
            return 1
    print("sync-vendor done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
