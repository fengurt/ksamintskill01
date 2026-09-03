#!/usr/bin/env python3
"""Export a gated self-contained deck to a verified 16:9 PDF."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--schema-report")
    parser.add_argument("--layout-report")
    parser.add_argument("--report")
    parser.add_argument("--benchmark-direct", action="store_true", help="Skip generic source gates for benchmark-built HTML")
    args = parser.parse_args()
    html = Path(args.html).resolve()
    out = Path(args.out).resolve()
    schema_path = Path(args.schema_report).resolve() if args.schema_report else html.parent.parent / "schema-report.json"
    layout_path = Path(args.layout_report).resolve() if args.layout_report else html.parent.parent / "audit-layout.json"
    if not args.benchmark_direct:
        if not schema_path.is_file():
            raise SystemExit(f"schema report missing: {schema_path}")
        if not layout_path.is_file():
            raise SystemExit(f"layout report missing: {layout_path}")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        if schema.get("hard") or (schema.get("summary") or {}).get("hard"):
            raise SystemExit("PDF export blocked: schema gate has hard findings")
        if (layout.get("summary") or {}).get("hard"):
            raise SystemExit("PDF export blocked: layout gate has hard findings")

    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter

    out.parent.mkdir(parents=True, exist_ok=True)
    failure = RuntimeError("large deck: use bounded chunks") if html.stat().st_size > 6_000_000 else None
    slide_count = 0
    for attempt in range(0 if failure else 2):
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome")
            except Exception:
                browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1600, "height": 900})
                page.goto(html.as_uri(), wait_until="load", timeout=180_000)
                page.evaluate("document.fonts && document.fonts.ready")
                page.evaluate("document.documentElement.classList.add('sd-printing','sd-export')")
                page.emulate_media(media="print")
                slide_count = page.locator("section.sd-slide").count()
                page.pdf(path=str(out), width="16in", height="9in", print_background=True, prefer_css_page_size=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
                failure = None
                break
            except Exception as exc:
                failure = exc
            finally:
                browser.close()
    if failure:
        chunks = out.parent / f".{out.stem}-chunks"
        chunks.mkdir(exist_ok=True)
        writer = PdfWriter()
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome")
            except Exception:
                browser = p.chromium.launch()
            probe = browser.new_page(viewport={"width": 1600, "height": 900})
            probe.goto(html.as_uri(), wait_until="load", timeout=180_000)
            slide_count = probe.locator("section.sd-slide").count()
            probe.close()
            browser.close()
            for start in range(1, slide_count + 1, 8):
                end = min(start + 7, slide_count)
                chunk = chunks / f"{start:05d}.pdf"
                if chunk.is_file() and len(PdfReader(str(chunk)).pages) == end - start + 1:
                    writer.append(str(chunk))
                    continue
                try:
                    browser = p.chromium.launch(channel="chrome")
                except Exception:
                    browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1600, "height": 900})
                page.goto(html.as_uri(), wait_until="load", timeout=180_000)
                page.evaluate("document.fonts && document.fonts.ready")
                page.locator("section.sd-slide").evaluate_all(
                    "(slides, keep) => slides.forEach((slide, i) => { if (i < keep[0] || i >= keep[1]) slide.remove(); })",
                    [start - 1, end],
                )
                page.evaluate("document.documentElement.classList.add('sd-printing','sd-export')")
                page.emulate_media(media="print")
                print(f"export_pdf: chunk {start}-{end}", flush=True)
                page.pdf(path=str(chunk), width="16in", height="9in", print_background=True, prefer_css_page_size=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
                page.close()
                browser.close()
                writer.append(str(chunk))
        with out.open("wb") as handle:
            writer.write(handle)
        shutil.rmtree(chunks)

    reader = PdfReader(str(out))
    findings = []
    if len(reader.pages) != slide_count:
        findings.append({"code": "PAGE_COUNT", "expected": slide_count, "actual": len(reader.pages)})
    for index, pdf_page in enumerate(reader.pages, 1):
        width, height = float(pdf_page.mediabox.width), float(pdf_page.mediabox.height)
        if height <= 0 or abs(width / height - 16 / 9) > 0.001:
            findings.append({"code": "ASPECT", "page": index, "width": width, "height": height})
    report = {"version": 1, "mode": "benchmark-direct" if args.benchmark_direct else "gated", "html": str(html), "pdf": str(out), "pages": len(reader.pages), "hard": len(findings), "findings": findings}
    report_path = Path(args.report).resolve() if args.report else html.parent.parent / "audit-pdf.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"export_pdf: {len(reader.pages)} pages · hard {len(findings)} → {out}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
