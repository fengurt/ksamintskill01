#!/usr/bin/env python3
"""fileye — identify, fingerprint and inventory any file into a manifest.

Standard library only. openpyxl is used opportunistically for a canonical
content hash of .xlsx files; everything else works without it.

Usage:
    python fileye.py look   <file> [--out manifest.json] [--full]
    python fileye.py verify <file> <manifest.json>
    python fileye.py batch  <dir>  [--out manifests/] [--full]

Every fact in the manifest is placed under one of three trust classes:
    detected  - computed by fileye from the bytes (reproducible by anyone)
    claimed   - read from the filesystem or from metadata embedded in the
                file (trivially editable; treat as a statement, never a fact)
    trusted   - stamped by the ingesting host at ingest time (only as
                trustworthy as that host and its clock)
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import io
import json
import os
import platform
import re
import sqlite3
import struct
import sys
import zipfile

FILEYE_VERSION = "1.0.0"
HASH_CHUNK = 1 << 20  # 1 MiB
SAMPLE_BYTES = 1 << 16  # 64 KiB read for sniffing


# --------------------------------------------------------------------------
# 1. Identity: hashes
# --------------------------------------------------------------------------

def hash_file(path: str) -> dict:
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()
    size = 0
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(HASH_CHUNK)
            if not chunk:
                break
            size += len(chunk)
            sha256.update(chunk)
            sha1.update(chunk)
            md5.update(chunk)
    out = {
        "sha256": sha256.hexdigest(),
        "size_bytes": size,
        # sha1 / md5 are reported only so that legacy inventories can be
        # matched; never use them as identity — both have known collisions.
        "legacy_sha1": sha1.hexdigest(),
        "legacy_md5": md5.hexdigest(),
    }
    try:  # optional, faster hash if the package exists
        import blake3  # type: ignore

        h = blake3.blake3()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(HASH_CHUNK), b""):
                h.update(chunk)
        out["blake3"] = h.hexdigest()
    except Exception:
        out["blake3"] = None
    return out


# --------------------------------------------------------------------------
# 2. Type: magic bytes first, extension second
# --------------------------------------------------------------------------

MAGIC = [
    (b"PK\x03\x04", "zip"),
    (b"PK\x05\x06", "zip"),  # empty archive
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "ole2"),
    (b"%PDF", "pdf"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"SQLite format 3\x00", "sqlite"),
    (b"PAR1", "parquet"),
    (b"ARROW1", "arrow"),
    (b"\x93NUMPY", "npy"),
    (b"\x1f\x8b", "gzip"),
    (b"BZh", "bzip2"),
    (b"\xfd7zXZ\x00", "xz"),
    (b"\x28\xb5\x2f\xfd", "zstd"),
    (b"7z\xbc\xaf\x27\x1c", "7z"),
    (b"Rar!\x1a\x07", "rar"),
    (b"ustar", "tar"),  # checked at offset 257 below
    (b"{\\rtf", "rtf"),
    (b"OggS", "ogg"),
    (b"fLaC", "flac"),
    (b"ID3", "mp3"),
    (b"\x1a\x45\xdf\xa3", "matroska"),
    (b"\x7fELF", "elf"),
    (b"MZ", "pe"),
    (b"\xca\xfe\xba\xbe", "mach-o-fat"),
    (b"\xcf\xfa\xed\xfe", "mach-o"),
    (b"%!PS", "postscript"),
    (b"8BPS", "psd"),
    (b"II*\x00", "tiff"),
    (b"MM\x00*", "tiff"),
    (b"\x00\x00\x01\x00", "ico"),
    (b"BM", "bmp"),
    (b"wOFF", "woff"),
    (b"wOF2", "woff2"),
    (b"\x00\x01\x00\x00\x00", "ttf"),
    (b"OTTO", "otf"),
    (b"HDF\r\n\x1a\n", "hdf5"),
    (b"\x89HDF\r\n\x1a\n", "hdf5"),
    (b"CDF\x01", "netcdf"),
    (b"CDF\x02", "netcdf"),
    (b"\x80\x04\x95", "pickle"),
    (b"\x80\x05\x95", "pickle"),
]

OOXML_MAP = {
    "xl/": "xlsx",
    "word/": "docx",
    "ppt/": "pptx",
    "visio/": "vsdx",
}


def detect_type(path: str, head: bytes) -> dict:
    ext = os.path.splitext(path)[1].lower()
    detected = None
    container = None
    notes = []

    if len(head) >= 262 and head[257:262] == b"ustar":
        detected = "tar"
    else:
        for sig, name in MAGIC:
            if name == "tar":
                continue
            if head.startswith(sig):
                detected = name
                break

    if detected == "zip":
        container = "zip"
        detected, sub_notes = refine_zip(path)
        notes.extend(sub_notes)
    elif detected == "ole2":
        container = "ole2"
        detected = refine_ole2(ext, head)
    elif detected == "riff" or head[:4] == b"RIFF":
        container = "riff"
        tag = head[8:12]
        detected = {b"WAVE": "wav", b"AVI ": "avi", b"WEBP": "webp"}.get(tag, "riff")
    elif head[4:8] == b"ftyp":
        brand = head[8:12]
        detected = "heic" if brand[:3] in (b"hei", b"mif") else "mp4"
    elif detected is None:
        detected = sniff_text(head, ext)

    mime = MIME.get(detected, "application/octet-stream")
    ext_expect = EXT_FOR.get(detected)
    agreement = (ext in ext_expect) if ext_expect else None
    if agreement is False:
        notes.append(f"extension {ext or '(none)'} disagrees with detected type {detected}")
    return {
        "detected": detected,
        "container": container,
        "mime": mime,
        "claimed_extension": ext or None,
        "extension_agrees": agreement,
        "notes": notes,
    }


def refine_zip(path: str) -> tuple[str, list]:
    notes = []
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
    except zipfile.BadZipFile:
        return "zip-corrupt", ["zip central directory unreadable"]
    nameset = set(names)
    if "[Content_Types].xml" in nameset:
        for prefix, t in OOXML_MAP.items():
            if any(n.startswith(prefix) for n in names):
                if t == "xlsx" and "xl/vbaProject.bin" in nameset:
                    return "xlsm", notes
                if t == "docx" and "word/vbaProject.bin" in nameset:
                    return "docm", notes
                if t == "pptx" and "ppt/vbaProject.bin" in nameset:
                    return "pptm", notes
                return t, notes
        return "ooxml-unknown", notes
    if "mimetype" in nameset:
        try:
            with zipfile.ZipFile(path) as z:
                mt = z.read("mimetype").decode("ascii", "replace").strip()
        except Exception:
            mt = ""
        if "opendocument.spreadsheet" in mt:
            return "ods", notes
        if "opendocument.text" in mt:
            return "odt", notes
        if "opendocument.presentation" in mt:
            return "odp", notes
        if "epub" in mt:
            return "epub", notes
    if "META-INF/MANIFEST.MF" in nameset:
        return "jar", notes
    if "AndroidManifest.xml" in nameset:
        return "apk", notes
    if any(n.endswith(".numbers") or n == "Index/Document.iwa" for n in names):
        return "numbers", notes
    return "zip", notes


def refine_ole2(ext: str, head: bytes) -> str:
    # Reliable OLE2 sub-typing needs directory-stream parsing; extension is a
    # hint only, so we report the container and flag the hint.
    hint = {".xls": "xls", ".doc": "doc", ".ppt": "ppt", ".msg": "msg"}.get(ext)
    return f"ole2:{hint}" if hint else "ole2"


def sniff_text(head: bytes, ext: str) -> str:
    if not head:
        return "empty"
    if b"\x00" in head[:8192]:
        return "binary-unknown"
    enc, text = decode_sample(head)
    if text is None:
        return "binary-unknown"
    s = text.lstrip()
    low = s[:512].lower()
    if low.startswith("<?xml") or low.startswith("<xml"):
        return "xml"
    if low.startswith("<!doctype html") or low.startswith("<html"):
        return "html"
    if low.startswith("<svg"):
        return "svg"
    if s[:1] in "{[":
        try:
            json.loads(text)
            return "json"
        except Exception:
            # could be ndjson: every line parses on its own
            lines = [ln for ln in text.splitlines() if ln.strip()][:50]
            threshold = 0.5 if ext in (".ndjson", ".jsonl") else 0.8
            if len(lines) >= 2 and sum(_is_json_line(ln) for ln in lines) >= threshold * len(lines):
                return "ndjson"
    if s.startswith("---\n") or re.match(r"^[\w-]+:\s", s):
        if ext in (".yml", ".yaml"):
            return "yaml"
    if ext == ".md" or re.search(r"^#{1,6}\s", s, re.M):
        if ext in (".md", ".markdown", ""):
            return "markdown"
    if ext in (".py", ".js", ".ts", ".sh", ".sql", ".r", ".go", ".rs", ".java", ".c", ".cpp", ".h"):
        return "source:" + ext[1:]
    if looks_like_csv(text):
        return "csv"
    if ext in (".txt", ".log"):
        return "text"
    return "text"


def _is_json_line(line: str) -> bool:
    try:
        json.loads(line)
        return True
    except Exception:
        return False


def looks_like_csv(text: str) -> bool:
    lines = [ln for ln in text.splitlines() if ln.strip()][:20]
    if len(lines) < 2:
        return False
    delim = None
    try:
        delim = csv.Sniffer().sniff("\n".join(lines), delimiters=",;\t|").delimiter
    except csv.Error:
        # Sniffer needs a decent sample; fall back to the most consistent delimiter
        best = None
        for d in (",", ";", "\t", "|"):
            counts = [ln.count(d) for ln in lines]
            if counts[0] >= 1 and len(set(counts)) <= 2:
                score = (min(counts), -len(set(counts)))
                if best is None or score > best[0]:
                    best = (score, d)
        delim = best[1] if best else None
    if delim is None:
        return False
    counts = [ln.count(delim) for ln in lines]
    return counts[0] >= 1 and len(set(counts)) <= 2


def decode_sample(raw: bytes) -> tuple[str | None, str | None]:
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig", raw[3:].decode("utf-8", "replace")
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return "utf-16", raw.decode("utf-16", "replace")
    for enc in ("utf-8", "gb18030", "shift_jis", "latin-1"):
        try:
            return enc, raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return None, None


MIME = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xlsm": "application/vnd.ms-excel.sheet.macroEnabled.12",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "pdf": "application/pdf",
    "csv": "text/csv",
    "json": "application/json",
    "ndjson": "application/x-ndjson",
    "xml": "application/xml",
    "html": "text/html",
    "markdown": "text/markdown",
    "text": "text/plain",
    "png": "image/png",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "tiff": "image/tiff",
    "svg": "image/svg+xml",
    "sqlite": "application/vnd.sqlite3",
    "parquet": "application/vnd.apache.parquet",
    "zip": "application/zip",
    "gzip": "application/gzip",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
    "odt": "application/vnd.oasis.opendocument.text",
    "mp4": "video/mp4",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
}

EXT_FOR = {
    "xlsx": {".xlsx"}, "xlsm": {".xlsm"}, "docx": {".docx"}, "docm": {".docm"},
    "pptx": {".pptx"}, "pptm": {".pptm"}, "pdf": {".pdf"}, "csv": {".csv", ".tsv", ".txt"},
    "json": {".json"}, "ndjson": {".ndjson", ".jsonl", ".json"}, "xml": {".xml"},
    "html": {".html", ".htm"}, "markdown": {".md", ".markdown"}, "png": {".png"},
    "jpeg": {".jpg", ".jpeg"}, "gif": {".gif"}, "webp": {".webp"}, "sqlite": {".sqlite", ".db", ".sqlite3"},
    "parquet": {".parquet"}, "zip": {".zip"}, "gzip": {".gz", ".gzip", ".tgz"}, "ods": {".ods"},
    "odt": {".odt"}, "mp4": {".mp4", ".m4a", ".m4v", ".mov"}, "mp3": {".mp3"}, "wav": {".wav"},
    "tar": {".tar"}, "svg": {".svg"}, "yaml": {".yml", ".yaml"},
}


# --------------------------------------------------------------------------
# 3. Provenance: what is claimed vs what is trusted
# --------------------------------------------------------------------------

def iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    return _dt.datetime.fromtimestamp(ts, tz=_dt.timezone.utc).isoformat()


def fs_claims(path: str) -> dict:
    st = os.stat(path)
    birth = getattr(st, "st_birthtime", None)
    return {
        "path": os.path.abspath(path),
        "filename": os.path.basename(path),
        "fs_mtime": iso(st.st_mtime),
        "fs_ctime": iso(st.st_ctime),
        "fs_birthtime": iso(birth),
        "note": "filesystem timestamps are user-editable; treat as claims",
    }


def ooxml_claims(path: str) -> dict:
    out = {}
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            if "docProps/core.xml" in names:
                core = z.read("docProps/core.xml").decode("utf-8", "replace")
                for tag, key in (
                    ("dcterms:created", "created"),
                    ("dcterms:modified", "modified"),
                    ("dc:creator", "creator"),
                    ("cp:lastModifiedBy", "last_modified_by"),
                    ("dc:title", "title"),
                    ("cp:revision", "revision"),
                ):
                    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", core, re.S)
                    if m:
                        out[key] = m.group(1).strip()
            if "docProps/app.xml" in names:
                app = z.read("docProps/app.xml").decode("utf-8", "replace")
                for tag, key in (("Application", "application"), ("AppVersion", "app_version"), ("Company", "company")):
                    m = re.search(rf"<{tag}>(.*?)</{tag}>", app, re.S)
                    if m:
                        out[key] = m.group(1).strip()
            # zip entry timestamps: another claim, but hard to keep consistent when faking
            infos = z.infolist()
            if infos:
                stamps = sorted(_dt.datetime(*i.date_time).isoformat() for i in infos if i.date_time[0] >= 1980)
                if stamps:
                    out["zip_entry_time_min"] = stamps[0]
                    out["zip_entry_time_max"] = stamps[-1]
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    if out:
        out["note"] = "embedded metadata is plain XML inside the zip; editable"
    return out


def pdf_claims(head_full: bytes) -> dict:
    out = {}
    for key in ("CreationDate", "ModDate", "Producer", "Creator", "Author", "Title"):
        m = re.search(rb"/" + key.encode() + rb"\s*\(([^)]{0,200})\)", head_full)
        if m:
            out[key.lower()] = m.group(1).decode("latin-1", "replace")
    if out:
        out["note"] = "PDF info dictionary is editable; treat as claims"
    return out


def trusted_stamp() -> dict:
    return {
        "ingested_at": _dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
        "ingest_host": platform.node(),
        "ingest_os": platform.platform(),
        "python": platform.python_version(),
        "fileye_version": FILEYE_VERSION,
        "note": "only as trustworthy as this host and its clock; chain manifests in an append-only log for non-repudiation",
    }


# --------------------------------------------------------------------------
# 4. Structure: type-specific inventory
# --------------------------------------------------------------------------

def _count(pattern: bytes, blob: bytes) -> int:
    return len(re.findall(pattern, blob))


def structure_xlsx(path: str) -> dict:
    out = {"kind": "spreadsheet"}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        sheets_xml = sorted(n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        sheet_names = []
        if "xl/workbook.xml" in names:
            wb = z.read("xl/workbook.xml").decode("utf-8", "replace")
            sheet_names = re.findall(r"<sheet [^>]*name=\"([^\"]*)\"", wb)
            out["defined_names"] = _count(rb"<definedName ", wb.encode())
            hidden = re.findall(r"<sheet [^>]*state=\"(hidden|veryHidden)\"", wb)
            out["hidden_sheets"] = len(hidden)
        per_sheet = []
        totals = {"rows": 0, "cells": 0, "formulas": 0, "merged_ranges": 0, "hidden_rows": 0, "hidden_cols": 0,
                  "data_validations": 0, "conditional_formats": 0, "hyperlinks": 0}
        for i, n in enumerate(sheets_xml):
            blob = z.read(n)
            dim = re.search(rb"<dimension ref=\"([^\"]+)\"", blob)
            s = {
                "name": sheet_names[i] if i < len(sheet_names) else n,
                "dimension": dim.group(1).decode() if dim else None,
                "rows": _count(rb"<row[ >]", blob),
                "cells": _count(rb"<c[ >]", blob),
                "formulas": _count(rb"<f[ >/]", blob),
                "merged_ranges": _count(rb"<mergeCell ", blob),
                "hidden_rows": _count(rb"<row [^>]*hidden=\"1\"", blob),
                "hidden_cols": _count(rb"<col [^>]*hidden=\"1\"", blob),
                "data_validations": _count(rb"<dataValidation[ >]", blob),
                "conditional_formats": _count(rb"<conditionalFormatting[ >]", blob),
                "hyperlinks": _count(rb"<hyperlink ", blob),
                "has_drawing": b"<drawing " in blob,
                "has_autofilter": b"<autoFilter " in blob,
                "has_sheet_protection": b"<sheetProtection " in blob,
            }
            per_sheet.append(s)
            for k in totals:
                totals[k] += s[k]
        out["sheets"] = len(sheets_xml)
        out["per_sheet"] = per_sheet
        out["totals"] = totals
        out["shared_strings"] = _count(rb"<si>", z.read("xl/sharedStrings.xml")) if "xl/sharedStrings.xml" in names else 0
        out["charts"] = sum(1 for n in names if re.match(r"xl/charts/chart\d+\.xml$", n))
        out["images"] = sum(1 for n in names if n.startswith("xl/media/"))
        out["comments_parts"] = sum(1 for n in names if re.match(r"xl/comments\d*\.xml$", n))
        out["pivot_caches"] = sum(1 for n in names if n.startswith("xl/pivotCache/pivotCacheDefinition"))
        out["external_links"] = sum(1 for n in names if n.startswith("xl/externalLinks/externalLink") and n.endswith(".xml"))
        out["has_vba"] = "xl/vbaProject.bin" in names
        out["has_power_query"] = any("customXml" in n or "queryTable" in n for n in names)
        out["tables"] = sum(1 for n in names if re.match(r"xl/tables/table\d+\.xml$", n))
        if "xl/styles.xml" in names:
            styles = z.read("xl/styles.xml")
            out["number_formats_custom"] = _count(rb"<numFmt ", styles)
    return out


def content_hash_xlsx(path: str) -> dict:
    """Canonical hash over (sheet, cell, value, formula): identifies the DATA
    regardless of zip timestamps, styles or column widths."""
    try:
        import openpyxl  # type: ignore
    except Exception:
        return {"algorithm": None, "value": None, "reason": "openpyxl not installed"}
    try:
        wb = openpyxl.load_workbook(path, data_only=False, read_only=True)
        h = hashlib.sha256()
        cells = 0
        for ws in wb.worksheets:
            h.update(("\x1fSHEET\x1f" + ws.title).encode("utf-8"))
            for row in ws.iter_rows():
                for c in row:
                    if c.value is None:
                        continue
                    v = c.value
                    kind = "f" if isinstance(v, str) and v.startswith("=") else type(v).__name__
                    h.update(f"\x1e{c.coordinate}\x1f{kind}\x1f{v!r}".encode("utf-8"))
                    cells += 1
        wb.close()
        return {"algorithm": "sha256(sheet|coord|type|repr(value-or-formula))", "value": h.hexdigest(), "cells_hashed": cells}
    except Exception as exc:  # noqa: BLE001
        return {"algorithm": None, "value": None, "reason": f"openpyxl failed: {exc}"}


def structure_docx(path: str) -> dict:
    out = {"kind": "document"}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        doc = z.read("word/document.xml") if "word/document.xml" in names else b""
        out.update({
            "paragraphs": _count(rb"<w:p[ >]", doc),
            "tables": _count(rb"<w:tbl>", doc),
            "table_rows": _count(rb"<w:tr[ >]", doc),
            "tracked_insertions": _count(rb"<w:ins ", doc),
            "tracked_deletions": _count(rb"<w:del ", doc),
            "footnote_refs": _count(rb"<w:footnoteReference ", doc),
            "hyperlinks": _count(rb"<w:hyperlink ", doc),
            "fields": _count(rb"<w:fldChar ", doc) + _count(rb"<w:fldSimple ", doc),
            "drawings": _count(rb"<w:drawing>", doc),
            "images": sum(1 for n in names if n.startswith("word/media/")),
            "embedded_objects": sum(1 for n in names if n.startswith("word/embeddings/")),
            "comments": _count(rb"<w:comment ", z.read("word/comments.xml")) if "word/comments.xml" in names else 0,
            "headers": sum(1 for n in names if re.match(r"word/header\d*\.xml$", n)),
            "footers": sum(1 for n in names if re.match(r"word/footer\d*\.xml$", n)),
            "has_vba": "word/vbaProject.bin" in names,
            "styles_defined": _count(rb"<w:style ", z.read("word/styles.xml")) if "word/styles.xml" in names else 0,
        })
        text = re.sub(rb"<[^>]+>", b"", doc)
        out["approx_chars"] = len(text.decode("utf-8", "replace"))
    return out


def structure_pptx(path: str) -> dict:
    out = {"kind": "presentation"}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        slides = [n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        out["slides"] = len(slides)
        out["notes_slides"] = sum(1 for n in names if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n))
        out["images"] = sum(1 for n in names if n.startswith("ppt/media/"))
        out["charts"] = sum(1 for n in names if re.match(r"ppt/charts/chart\d+\.xml$", n))
        out["embedded_objects"] = sum(1 for n in names if n.startswith("ppt/embeddings/"))
        out["layouts"] = sum(1 for n in names if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml$", n))
        out["has_vba"] = "ppt/vbaProject.bin" in names
        shapes = 0
        for n in slides:
            shapes += _count(rb"<p:sp>", z.read(n))
        out["shapes"] = shapes
    return out


def structure_pdf(path: str, size: int) -> dict:
    out = {"kind": "pdf"}
    with open(path, "rb") as fh:
        blob = fh.read()
    out["pages"] = _count(rb"/Type\s*/Page[^s]", blob)
    out["objects"] = _count(rb"\d+\s+\d+\s+obj\b", blob)
    out["is_encrypted"] = b"/Encrypt" in blob
    out["has_acroform"] = b"/AcroForm" in blob
    out["has_javascript"] = b"/JavaScript" in blob or b"/JS" in blob
    out["fonts"] = _count(rb"/Type\s*/Font\b", blob)
    out["images"] = _count(rb"/Subtype\s*/Image\b", blob)
    out["has_text_layer_hint"] = out["fonts"] > 0
    out["xref_streams"] = b"/XRef" in blob
    out["incremental_updates"] = max(0, blob.count(b"%%EOF") - 1)
    m = re.match(rb"%PDF-(\d\.\d)", blob)
    out["pdf_version"] = m.group(1).decode() if m else None
    out["note"] = "counts are regex-based on raw bytes; objects inside compressed object streams are not visible"
    return out


def structure_csv(path: str, head: bytes) -> dict:
    out = {"kind": "table"}
    enc, _ = decode_sample(head)
    out["encoding"] = enc
    out["has_bom"] = head.startswith(b"\xef\xbb\xbf")
    crlf = head.count(b"\r\n")
    lf = head.count(b"\n") - crlf
    out["line_ending"] = "CRLF" if crlf > lf else "LF" if lf else None
    with open(path, "r", encoding=enc or "utf-8", errors="replace", newline="") as fh:
        sample = fh.read(SAMPLE_BYTES)
        try:
            delim = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            first = sample.splitlines()[0] if sample else ""
            delim = max((",", ";", "\t", "|"), key=first.count)
        fh.seek(0)
        reader = csv.reader(fh, delimiter=delim)
        header = next(reader, [])
        widths = {}
        rows = 0
        empty = 0
        for row in reader:
            rows += 1
            if not any(cell.strip() for cell in row):
                empty += 1
            widths[len(row)] = widths.get(len(row), 0) + 1
    out.update({
        "delimiter": delim,
        "columns": len(header),
        "header": header[:200],
        "data_rows": rows,
        "empty_rows": empty,
        "ragged_rows": sum(v for k, v in widths.items() if k != len(header)),
        "width_histogram": widths,
    })
    return out


def structure_json(path: str) -> dict:
    out = {"kind": "json"}
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return {"kind": "json", "parse_error": str(exc)}

    def depth(o, d=0):
        if isinstance(o, dict):
            return max([depth(v, d + 1) for v in o.values()] or [d + 1])
        if isinstance(o, list):
            return max([depth(v, d + 1) for v in o] or [d + 1])
        return d

    out["top_level_type"] = type(data).__name__
    if isinstance(data, dict):
        out["top_level_keys"] = list(data.keys())[:100]
        out["key_count"] = len(data)
    elif isinstance(data, list):
        out["length"] = len(data)
        if data and isinstance(data[0], dict):
            keys = set()
            for item in data[:1000]:
                if isinstance(item, dict):
                    keys.update(item.keys())
            out["record_keys_union"] = sorted(keys)[:200]
    out["max_depth"] = depth(data)
    return out


def structure_ndjson(path: str) -> dict:
    n = bad = 0
    keys = set()
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip():
                continue
            n += 1
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and n <= 1000:
                    keys.update(obj.keys())
            except Exception:
                bad += 1
    return {"kind": "ndjson", "records": n, "unparseable_lines": bad, "record_keys_union": sorted(keys)[:200]}


def structure_text(path: str, head: bytes) -> dict:
    enc, _ = decode_sample(head)
    lines = 0
    chars = 0
    with open(path, "r", encoding=enc or "utf-8", errors="replace") as fh:
        for line in fh:
            lines += 1
            chars += len(line)
    crlf = head.count(b"\r\n")
    lf = head.count(b"\n") - crlf
    return {"kind": "text", "encoding": enc, "lines": lines, "chars": chars,
            "line_ending": "CRLF" if crlf > lf else "LF" if lf else None,
            "has_bom": head.startswith(b"\xef\xbb\xbf")}


def structure_sqlite(path: str) -> dict:
    out = {"kind": "database"}
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        cur = con.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        out["tables"] = []
        for t in tables:
            cols = [r[1] for r in cur.execute(f'PRAGMA table_info("{t}")')]
            n = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            out["tables"].append({"name": t, "columns": cols, "rows": n})
        out["views"] = cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view'").fetchone()[0]
        out["indexes"] = cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'").fetchone()[0]
        con.close()
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    return out


def structure_image(detected: str, head: bytes) -> dict:
    out = {"kind": "image"}
    try:
        if detected == "png" and len(head) >= 24:
            w, h = struct.unpack(">II", head[16:24])
            out.update(width=w, height=h, bit_depth=head[24], color_type=head[25])
        elif detected == "gif" and len(head) >= 10:
            w, h = struct.unpack("<HH", head[6:10])
            out.update(width=w, height=h)
        elif detected == "bmp" and len(head) >= 26:
            w, h = struct.unpack("<ii", head[18:26])
            out.update(width=w, height=abs(h))
        elif detected == "jpeg":
            i = 2
            while i + 9 < len(head):
                if head[i] != 0xFF:
                    break
                marker = head[i + 1]
                if marker in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", head[i + 5:i + 9])
                    out.update(width=w, height=h)
                    break
                seg = struct.unpack(">H", head[i + 2:i + 4])[0]
                i += 2 + seg
            out["has_exif"] = b"Exif\x00\x00" in head
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    return out


def structure_zip(path: str) -> dict:
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        return {
            "kind": "archive",
            "entries": len(infos),
            "uncompressed_bytes": sum(i.file_size for i in infos),
            "compressed_bytes": sum(i.compress_size for i in infos),
            "encrypted_entries": sum(1 for i in infos if i.flag_bits & 0x1),
            "top_level": sorted({i.filename.split("/")[0] for i in infos})[:50],
        }


def structure_for(detected: str, path: str, head: bytes, size: int) -> dict:
    try:
        if detected in ("xlsx", "xlsm"):
            return structure_xlsx(path)
        if detected in ("docx", "docm"):
            return structure_docx(path)
        if detected in ("pptx", "pptm"):
            return structure_pptx(path)
        if detected == "pdf":
            return structure_pdf(path, size)
        if detected == "csv":
            return structure_csv(path, head)
        if detected == "json":
            return structure_json(path)
        if detected == "ndjson":
            return structure_ndjson(path)
        if detected in ("text", "markdown", "xml", "html", "yaml", "svg") or detected.startswith("source:"):
            return structure_text(path, head)
        if detected == "sqlite":
            return structure_sqlite(path)
        if detected in ("png", "jpeg", "gif", "bmp"):
            return structure_image(detected, head)
        if detected in ("zip", "jar", "apk", "epub", "ods", "odt", "odp"):
            return structure_zip(path)
    except Exception as exc:  # noqa: BLE001
        return {"kind": "unknown", "error": str(exc)}
    return {"kind": "opaque", "note": "no structural parser for this type; bytes only"}


# --------------------------------------------------------------------------
# 5. Lossless levels: what a downstream conversion must preserve
# --------------------------------------------------------------------------

def lossless_plan(detected: str, structure: dict) -> dict:
    """Which layers exist in this file. A conversion is only 'lossless' at a
    level if every layer present at that level survives the round trip."""
    layers = {"L0_bytes": True}
    if structure.get("kind") == "spreadsheet":
        t = structure.get("totals", {})
        layers.update({
            "L1_values": True,
            "L2_formulas": t.get("formulas", 0) > 0 or structure.get("defined_names", 0) > 0,
            "L3_layout": any(t.get(k, 0) for k in ("merged_ranges", "hidden_rows", "hidden_cols"))
                         or structure.get("number_formats_custom", 0) > 0 or structure.get("hidden_sheets", 0) > 0,
            "L4_objects": any(structure.get(k) for k in ("charts", "images", "comments_parts", "pivot_caches", "tables"))
                          or any(t.get(k, 0) for k in ("data_validations", "conditional_formats", "hyperlinks")),
            "L5_code_and_links": bool(structure.get("has_vba") or structure.get("external_links") or structure.get("has_power_query")),
        })
    elif structure.get("kind") == "document":
        layers.update({
            "L1_text": True,
            "L2_structure": structure.get("tables", 0) > 0 or structure.get("headers", 0) > 0 or structure.get("footers", 0) > 0,
            "L3_revisions": structure.get("tracked_insertions", 0) + structure.get("tracked_deletions", 0) + structure.get("comments", 0) > 0,
            "L4_objects": structure.get("images", 0) + structure.get("embedded_objects", 0) + structure.get("drawings", 0) > 0,
            "L5_code_and_links": bool(structure.get("has_vba")) or structure.get("fields", 0) > 0,
        })
    elif structure.get("kind") == "presentation":
        layers.update({
            "L1_text": structure.get("shapes", 0) > 0,
            "L2_structure": structure.get("slides", 0) > 0,
            "L3_revisions": structure.get("notes_slides", 0) > 0,
            "L4_objects": structure.get("images", 0) + structure.get("charts", 0) + structure.get("embedded_objects", 0) > 0,
            "L5_code_and_links": bool(structure.get("has_vba")),
        })
    elif structure.get("kind") == "table":
        layers.update({"L1_values": True, "L2_formulas": False, "L3_layout": False, "L4_objects": False, "L5_code_and_links": False})
    elif structure.get("kind") == "pdf":
        layers.update({
            "L1_text": structure.get("has_text_layer_hint", False),
            "L2_structure": True,
            "L3_revisions": structure.get("incremental_updates", 0) > 0,
            "L4_objects": structure.get("images", 0) > 0 or structure.get("has_acroform", False),
            "L5_code_and_links": structure.get("has_javascript", False),
        })
    present = [k for k, v in layers.items() if v]
    return {
        "layers_present": present,
        "minimum_lossless_store": "keep the original bytes content-addressed by sha256 (L0); every other layer is derivable from it",
        "conversion_warning": (
            "CSV/JSON exports keep L1 only; any layer above L1 that is present here is lost on that path"
            if len(present) > 2 else None
        ),
    }


# --------------------------------------------------------------------------
# 6. Assemble
# --------------------------------------------------------------------------

def look(path: str, full: bool = False) -> dict:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with open(path, "rb") as fh:
        head = fh.read(SAMPLE_BYTES)
    identity = hash_file(path)
    typ = detect_type(path, head)
    detected = typ["detected"]
    warnings = list(typ.pop("notes", []))

    claimed = {"filesystem": fs_claims(path)}
    if typ["container"] == "zip":
        emb = ooxml_claims(path)
        if emb:
            claimed["embedded"] = emb
    elif detected == "pdf":
        with open(path, "rb") as fh:
            emb = pdf_claims(fh.read())
        if emb:
            claimed["embedded"] = emb

    structure = structure_for(detected, path, head, identity["size_bytes"])
    if not full:
        structure.pop("width_histogram", None)
        if "per_sheet" in structure and len(structure["per_sheet"]) > 20:
            structure["per_sheet"] = structure["per_sheet"][:20] + [{"truncated": True}]

    content_hash = None
    if detected in ("xlsx", "xlsm"):
        content_hash = content_hash_xlsx(path)
    elif structure.get("kind") in ("table", "text", "json", "ndjson"):
        with open(path, "rb") as fh:
            raw = fh.read()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        canon = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n").rstrip(b"\n")
        content_hash = {"algorithm": "sha256(strip BOM, normalise line endings, strip trailing newline)", "value": hashlib.sha256(canon).hexdigest()}

    if identity["size_bytes"] == 0:
        warnings.append("file is empty")
    if typ["container"] == "zip" and detected.endswith("corrupt"):
        warnings.append("container unreadable; structure not inventoried")
    if structure.get("kind") == "table" and structure.get("ragged_rows"):
        warnings.append(f"{structure['ragged_rows']} rows have a column count different from the header")
    if structure.get("kind") == "pdf" and structure.get("is_encrypted"):
        warnings.append("PDF is encrypted; text layer may be inaccessible")
    if structure.get("kind") == "pdf" and not structure.get("has_text_layer_hint"):
        warnings.append("no font objects found; likely scanned — OCR required before text extraction")
    if structure.get("has_vba"):
        warnings.append("file contains VBA; do not open with macros enabled on an untrusted host")
    if structure.get("external_links"):
        warnings.append("workbook references external workbooks; values may be stale")
    emb = claimed.get("embedded", {})
    fs_m = claimed["filesystem"].get("fs_mtime")
    if emb.get("modified") and fs_m:
        try:
            em = _dt.datetime.fromisoformat(emb["modified"].replace("Z", "+00:00"))
            fm = _dt.datetime.fromisoformat(fs_m)
            if abs((em - fm).total_seconds()) > 7 * 86400:
                warnings.append("embedded 'modified' and filesystem mtime differ by more than 7 days; at least one claim is stale or edited")
        except Exception:
            pass

    return {
        "fileye": FILEYE_VERSION,
        "identity": {**identity, "content_hash": content_hash,
                     "note": "sha256 identifies these exact bytes; content_hash identifies the data across re-saves"},
        "type": typ,
        "provenance": {"trusted": trusted_stamp(), "claimed": claimed},
        "structure": structure,
        "lossless": lossless_plan(detected, structure),
        "warnings": warnings,
    }


def verify(path: str, manifest_path: str) -> dict:
    with open(manifest_path, "r", encoding="utf-8") as fh:
        m = json.load(fh)
    now = hash_file(path)
    same = now["sha256"] == m["identity"]["sha256"]
    out = {"path": path, "bytes_identical": same, "sha256_now": now["sha256"], "sha256_manifest": m["identity"]["sha256"]}
    if not same and m["identity"].get("content_hash", {}) and m["identity"]["content_hash"].get("value"):
        fresh = look(path)
        ch_now = (fresh["identity"].get("content_hash") or {}).get("value")
        out["content_identical"] = ch_now == m["identity"]["content_hash"]["value"]
        out["note"] = ("bytes changed but data did not (re-save, metadata edit, or zip timestamps)"
                       if out["content_identical"] else "data changed")
    return out


def batch(directory: str, out_dir: str | None, full: bool) -> list:
    results = []
    for root, _dirs, files in os.walk(directory):
        for f in sorted(files):
            p = os.path.join(root, f)
            try:
                m = look(p, full)
            except Exception as exc:  # noqa: BLE001
                m = {"error": str(exc), "path": p}
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
                sha = m.get("identity", {}).get("sha256", "error")
                with open(os.path.join(out_dir, f"{sha[:16]}_{f}.fileye.json"), "w", encoding="utf-8") as fh:
                    json.dump(m, fh, ensure_ascii=False, indent=2)
            results.append({
                "path": p,
                "sha256": m.get("identity", {}).get("sha256"),
                "type": m.get("type", {}).get("detected"),
                "size": m.get("identity", {}).get("size_bytes"),
                "warnings": len(m.get("warnings", [])),
            })
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description="fileye: identify, fingerprint and inventory any file")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("look", help="produce a manifest for one file")
    a.add_argument("file")
    a.add_argument("--out", help="write manifest JSON here (default: stdout)")
    a.add_argument("--full", action="store_true", help="do not truncate large per-sheet or histogram sections")
    b = sub.add_parser("verify", help="check a file against an earlier manifest")
    b.add_argument("file")
    b.add_argument("manifest")
    c = sub.add_parser("batch", help="manifest every file under a directory")
    c.add_argument("dir")
    c.add_argument("--out", help="directory to write one manifest per file")
    c.add_argument("--full", action="store_true")
    args = ap.parse_args(argv)

    if args.cmd == "look":
        m = look(args.file, args.full)
        text = json.dumps(m, ensure_ascii=False, indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"wrote {args.out}")
        else:
            print(text)
    elif args.cmd == "verify":
        print(json.dumps(verify(args.file, args.manifest), ensure_ascii=False, indent=2))
    elif args.cmd == "batch":
        rows = batch(args.dir, args.out, args.full)
        print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
