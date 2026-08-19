#!/usr/bin/env python3
"""Segment a Markdown document into atomic units for longdoc-to-deck.

Never splits tables, fenced code blocks, or contiguous list runs mid-structure.
Emits index.json + index.md (one-line digest per unit).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+")
BLOCKQUOTE_RE = re.compile(r"^\s*>\s?")
FIGURE_RE = re.compile(r"^\s*!\[")
NUMBER_HEAVY_RE = re.compile(r"[\d.%％]+")

KINDS = (
    "prose",
    "list",
    "table",
    "code",
    "quote",
    "figure",
    "number-block",
    "heading",
)

MAX_PROSE_CHARS = 850  # under statement chars_max (900)
MAX_TABLE_DATA_ROWS = 10  # row-boundary chunks (header repeated); never mid-row
MAX_LIST_CHARS = 800
MAX_CODE_CHARS = 2000  # keep fences whole unless extremely long — still atomic fence


@dataclass
class Unit:
    id: str
    kind: str
    heading_path: list[str]
    char_count: int
    line_start: int
    line_end: int
    digest: str
    text: str = field(repr=False)

    def to_index(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "heading_path": self.heading_path,
            "char_count": self.char_count,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "digest": self.digest,
        }


def _digest(text: str, limit: int = 120) -> str:
    flat = re.sub(r"\s+", " ", text.strip())
    if len(flat) <= limit:
        return flat
    return flat[: limit - 1] + "…"


def _chunk_table(lines_slice: list[str], start_line_1idx: int) -> list[tuple[int, int, str]]:
    """Split a table at row boundaries into header + batches of data rows."""
    rows = list(lines_slice)
    if not rows:
        return []
    header_lines: list[str] = []
    data_lines: list[str] = []
    # First row = header; second may be separator
    idx = 0
    if idx < len(rows):
        header_lines.append(rows[idx])
        idx += 1
    if idx < len(rows) and _is_table_sep(rows[idx]):
        header_lines.append(rows[idx])
        idx += 1
    data_lines = rows[idx:]
    # Drop blank data lines
    data_lines = [r for r in data_lines if r.strip()]
    if len(data_lines) <= MAX_TABLE_DATA_ROWS:
        text = "\n".join(rows)
        return [(start_line_1idx, start_line_1idx + len(rows) - 1, text)]

    chunks: list[tuple[int, int, str]] = []
    # Approximate line mapping: header occupies len(header_lines), then data
    data_start_line = start_line_1idx + len(header_lines)
    for batch_start in range(0, len(data_lines), MAX_TABLE_DATA_ROWS):
        batch = data_lines[batch_start : batch_start + MAX_TABLE_DATA_ROWS]
        text = "\n".join(header_lines + batch)
        line_s = data_start_line + batch_start
        line_e = line_s + len(batch) - 1
        if batch_start == 0:
            line_s = start_line_1idx
        chunks.append((line_s, max(line_e, line_s), text))
    return chunks


def _chunk_list(text: str, start_line: int, end_line: int) -> list[tuple[int, int, str]]:
    if len(text) <= MAX_LIST_CHARS:
        return [(start_line, end_line, text)]
    lines = text.splitlines()
    chunks: list[tuple[int, int, str]] = []
    buf: list[str] = []
    buf_start = start_line
    for offset, line in enumerate(lines):
        abs_line = start_line + offset
        if not buf:
            buf_start = abs_line
        buf.append(line)
        if LIST_RE.match(line) and len("\n".join(buf)) >= MAX_LIST_CHARS and len(buf) > 1:
            # flush previous items only
            keep = buf[:-1]
            if keep:
                chunks.append((buf_start, buf_start + len(keep) - 1, "\n".join(keep)))
            buf = [line]
            buf_start = abs_line
    if buf:
        chunks.append((buf_start, buf_start + len(buf) - 1, "\n".join(buf)))
    return chunks or [(start_line, end_line, text)]


def _is_table_sep(line: str) -> bool:
    s = line.strip()
    if not s.startswith("|"):
        return False
    return bool(re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", s))


def _classify_prose(text: str) -> str:
    digits = len(NUMBER_HEAVY_RE.findall(text))
    words = max(1, len(re.findall(r"\S+", text)))
    if digits >= 4 and digits / words >= 0.25:
        return "number-block"
    if FIGURE_RE.search(text):
        return "figure"
    return "prose"


def _split_prose_paragraphs(block_lines: list[str], start_line: int) -> list[tuple[int, int, str]]:
    """Return (line_start, line_end, text) chunks for prose, soft-splitting long runs."""
    chunks: list[tuple[int, int, str]] = []
    buf: list[str] = []
    buf_start = start_line

    def flush() -> None:
        nonlocal buf, buf_start
        if not buf:
            return
        text = "\n".join(buf)
        # Soft-split only on blank-line boundaries already represented;
        # if a single paragraph is huge, keep it whole (atomic paragraph).
        chunks.append((buf_start, buf_start + len(buf) - 1, text))
        buf = []

    for i, line in enumerate(block_lines):
        abs_line = start_line + i
        if line.strip() == "":
            flush()
            buf_start = abs_line + 1
            continue
        if not buf:
            buf_start = abs_line
        buf.append(line)
        joined = "\n".join(buf)
        if len(joined) >= MAX_PROSE_CHARS and line.strip() == "":
            flush()
            buf_start = abs_line + 1
    flush()
    return chunks


def segment_markdown(source: str, source_path: str | None = None) -> dict:
    lines = source.splitlines()
    units: list[Unit] = []
    heading_stack: list[tuple[int, str]] = []  # (level, title)
    i = 0
    n = len(lines)
    unit_seq = 0

    def heading_path() -> list[str]:
        return [t for _, t in heading_stack]

    def emit(kind: str, text: str, line_start: int, line_end: int) -> None:
        nonlocal unit_seq
        unit_seq += 1
        uid = f"u-{unit_seq:04d}"
        units.append(
            Unit(
                id=uid,
                kind=kind,
                heading_path=heading_path(),
                char_count=len(text),
                line_start=line_start,
                line_end=line_end,
                digest=_digest(text),
                text=text,
            )
        )

    while i < n:
        line = lines[i]
        abs_line = i + 1  # 1-indexed

        # Blank lines
        if line.strip() == "":
            i += 1
            continue

        # Headings — become units and update path
        hm = HEADING_RE.match(line)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2).strip()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))
            emit("heading", line.rstrip(), abs_line, abs_line)
            i += 1
            continue

        # Fenced code
        fm = FENCE_RE.match(line)
        if fm:
            fence = fm.group(1)[0]
            fence_len = len(fm.group(1))
            start = i
            i += 1
            while i < n:
                close = FENCE_RE.match(lines[i])
                if close and close.group(1)[0] == fence and len(close.group(1)) >= fence_len:
                    i += 1
                    break
                i += 1
            text = "\n".join(lines[start:i])
            emit("code", text, start + 1, i)
            continue

        # Table (contiguous pipe rows including separator) — chunk at row boundaries
        if TABLE_ROW_RE.match(line) or _is_table_sep(line):
            start = i
            i += 1
            while i < n and (TABLE_ROW_RE.match(lines[i]) or _is_table_sep(lines[i]) or lines[i].strip() == ""):
                # Stop if blank followed by non-table
                if lines[i].strip() == "":
                    if i + 1 < n and not (
                        TABLE_ROW_RE.match(lines[i + 1]) or _is_table_sep(lines[i + 1])
                    ):
                        break
                i += 1
            # Trim trailing blank from table block
            end = i
            while end > start and lines[end - 1].strip() == "":
                end -= 1
            for ls, le, chunk_text in _chunk_table(lines[start:end], start + 1):
                emit("table", chunk_text, ls, le)
            continue

        # Blockquote run
        if BLOCKQUOTE_RE.match(line):
            start = i
            i += 1
            while i < n and (BLOCKQUOTE_RE.match(lines[i]) or lines[i].strip() == ""):
                if lines[i].strip() == "":
                    if i + 1 < n and not BLOCKQUOTE_RE.match(lines[i + 1]):
                        break
                i += 1
            end = i
            while end > start and lines[end - 1].strip() == "":
                end -= 1
            text = "\n".join(lines[start:end])
            emit("quote", text, start + 1, end)
            continue

        # List run (contiguous list items; nested ok) — chunk on item boundaries when long
        if LIST_RE.match(line):
            start = i
            i += 1
            while i < n:
                cur = lines[i]
                if LIST_RE.match(cur):
                    i += 1
                    continue
                # Continuation indented line of a list item
                if cur.strip() and (cur.startswith("  ") or cur.startswith("\t")):
                    i += 1
                    continue
                if cur.strip() == "":
                    # Peek: next non-blank still list?
                    j = i + 1
                    while j < n and lines[j].strip() == "":
                        j += 1
                    if j < n and LIST_RE.match(lines[j]):
                        i = j
                        continue
                    break
                break
            end = i
            while end > start and lines[end - 1].strip() == "":
                end -= 1
            text = "\n".join(lines[start:end])
            for ls, le, chunk_text in _chunk_list(text, start + 1, end):
                emit("list", chunk_text, ls, le)
            continue

        # Figure / image line(s)
        if FIGURE_RE.match(line):
            start = i
            i += 1
            while i < n and (FIGURE_RE.match(lines[i]) or lines[i].strip() == ""):
                if lines[i].strip() == "" and i + 1 < n and not FIGURE_RE.match(lines[i + 1]):
                    break
                i += 1
            end = i
            while end > start and lines[end - 1].strip() == "":
                end -= 1
            text = "\n".join(lines[start:end])
            emit("figure", text, start + 1, end)
            continue

        # Prose paragraph until blank / structural boundary
        start = i
        i += 1
        while i < n:
            cur = lines[i]
            if cur.strip() == "":
                break
            if (
                HEADING_RE.match(cur)
                or FENCE_RE.match(cur)
                or TABLE_ROW_RE.match(cur)
                or LIST_RE.match(cur)
                or BLOCKQUOTE_RE.match(cur)
                or FIGURE_RE.match(cur)
            ):
                break
            i += 1
        text = "\n".join(lines[start:i])
        kind = _classify_prose(text)
        if kind == "prose" and len(text) > MAX_PROSE_CHARS:
            # Prefer blank-line paragraphs; else soft-split on sentence boundaries
            paras = _split_prose_paragraphs(lines[start:i], start + 1)
            if len(paras) > 1:
                for ps, pe, ptext in paras:
                    emit(_classify_prose(ptext), ptext, ps, pe)
            else:
                # sentence-ish split for a single huge paragraph
                parts = re.split(r"(?<=[。！？.!?])\s*", text)
                buf = ""
                part_start = start + 1
                for part in parts:
                    if not part:
                        continue
                    candidate = (buf + part) if not buf else (buf + part)
                    if buf and len(candidate) > MAX_PROSE_CHARS:
                        emit(_classify_prose(buf), buf, part_start, part_start)
                        buf = part
                        part_start = part_start
                    else:
                        buf = candidate
                if buf:
                    emit(_classify_prose(buf), buf, part_start, i)
        else:
            emit(kind, text, start + 1, i)

    index = {
        "version": "1.0.0",
        "source": source_path,
        "total_units": len(units),
        "total_chars": sum(u.char_count for u in units),
        "kinds": {k: sum(1 for u in units if u.kind == k) for k in KINDS},
        "units": [u.to_index() for u in units],
    }
    # Keep full texts separately for pagination material extraction
    texts = {u.id: u.text for u in units}
    return {"index": index, "texts": texts}


def write_outputs(result: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    index = result["index"]
    (out_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "units.json").write_text(
        json.dumps(result["texts"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        f"# Unit digest — {index.get('source') or '(stdin)'}",
        "",
        f"total_units: **{index['total_units']}** · total_chars: **{index['total_chars']}**",
        "",
        "| id | kind | chars | path | digest |",
        "|----|------|------:|------|--------|",
    ]
    for u in index["units"]:
        path = " / ".join(u["heading_path"]) if u["heading_path"] else "(root)"
        path_esc = path.replace("|", "\\|")
        dig = u["digest"].replace("|", "\\|")
        lines.append(
            f"| {u['id']} | {u['kind']} | {u['char_count']} | {path_esc} | {dig} |"
        )
    lines.append("")
    (out_dir / "index.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Segment Markdown into longdoc-to-deck units")
    parser.add_argument("input", nargs="?", help="Markdown file (default: stdin)")
    parser.add_argument("-o", "--out", required=True, help="Output work directory")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.input:
        path = Path(args.input)
        text = path.read_text(encoding="utf-8")
        source_path = str(path.resolve())
    else:
        text = sys.stdin.read()
        source_path = None

    result = segment_markdown(text, source_path=source_path)
    out_dir = Path(args.out)
    write_outputs(result, out_dir)
    print(
        f"Wrote {result['index']['total_units']} units → {out_dir}/index.json",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
