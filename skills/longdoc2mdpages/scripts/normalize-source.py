#!/usr/bin/env python3
"""Normalize one Markdown file, directory, or ZIP into a deterministic work source."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath

ALLOWED = {".md", ".csv"}
MAX_FILES = 5000
MAX_UNCOMPRESSED = 256 * 1024 * 1024


def natural_key(value: str):
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def safe_name(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or any(part.startswith(".") for part in path.parts):
        raise ValueError(f"unsafe archive entry: {name}")
    if not path.parts or path.parts[0] == "__MACOSX":
        raise ValueError(f"ignored archive entry: {name}")
    return path


def collect(source: Path, original: Path) -> list[Path]:
    files: list[Path] = []
    if source.is_file() and source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_FILES or sum(info.file_size for info in entries) > MAX_UNCOMPRESSED:
                raise ValueError("archive is too large")
            seen = set()
            for info in entries:
                if info.is_dir():
                    continue
                rel = safe_name(info.filename)
                if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
                    raise ValueError(f"symlink archive entry denied: {info.filename}")
                if rel.suffix.lower() not in ALLOWED:
                    continue
                if rel in seen:
                    raise ValueError(f"duplicate archive entry: {info.filename}")
                seen.add(rel)
                target = original.joinpath(*rel.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                files.append(target)
    elif source.is_dir():
        items = [
            item for item in source.rglob("*")
            if item.is_file() and not item.is_symlink()
            and not any(part.startswith(".") for part in item.relative_to(source).parts)
            and item.suffix.lower() in ALLOWED
        ]
        if len(items) > MAX_FILES or sum(item.stat().st_size for item in items) > MAX_UNCOMPRESSED:
            raise ValueError("source directory is too large")
        for item in items:
            rel = item.relative_to(source)
            target = original / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            files.append(target)
    elif source.is_file() and source.suffix.lower() == ".md":
        target = original / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        files.append(target)
    else:
        raise ValueError("source must be a Markdown file, directory, or ZIP")
    return sorted(files, key=lambda p: natural_key(p.relative_to(original).as_posix()))


def normalize(source: Path, work: Path) -> dict:
    source = source.expanduser().resolve()
    work = work.expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    work.mkdir(parents=True, exist_ok=True)
    normalized = work / "source.md"
    if source == normalized:
        return json.loads((work / "source-manifest.json").read_text(encoding="utf-8")) if (work / "source-manifest.json").is_file() else {
            "version": 1, "source": str(source), "markdown": ["source.md"], "tables": []
        }
    original = work / "original"
    table_dir = work / "assets" / "tables"
    for generated in (original, table_dir):
        if generated.exists():
            shutil.rmtree(generated)
    original.mkdir(parents=True, exist_ok=True)
    files = collect(source, original)
    markdown = [p for p in files if p.suffix.lower() == ".md"]
    tables = [p for p in files if p.suffix.lower() == ".csv"]
    if not markdown:
        raise ValueError("source contains no Markdown files")
    for item in tables:
        rel = item.relative_to(original)
        target = table_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
    chunks = []
    for item in markdown:
        rel = item.relative_to(original).as_posix()
        text = item.read_text(encoding="utf-8-sig").strip()
        chunks.append(f"<!-- source-file: {rel} -->\n\n{text}")
    normalized.write_text("\n\n---\n\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    manifest = {
        "version": 1,
        "source": str(source),
        "normalized": "source.md",
        "markdown": [p.relative_to(original).as_posix() for p in markdown],
        "tables": [p.relative_to(original).as_posix() for p in tables],
    }
    (work / "source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--work", required=True)
    args = parser.parse_args()
    result = normalize(Path(args.source), Path(args.work))
    print(f"normalize-source: {len(result['markdown'])} md · {len(result['tables'])} csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
