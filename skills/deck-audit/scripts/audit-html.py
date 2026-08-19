#!/usr/bin/env python3
"""Hop2: compare page material anchors to HTML slide text. Emits audit-html.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anchors_lib import NUMERIC_KINDS, extract_from_text  # noqa: E402


class SlideParser(HTMLParser):
    """Collect text per section.slide, skipping script/style/chrome."""

    SKIP_TAGS = {"script", "style", "noscript"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slides: list[dict] = []
        self._in_slide = False
        self._skip_depth = 0
        self._chrome_depth = 0
        self._buf: list[str] = []
        self._title_buf: list[str] = []
        self._in_title = False
        self._attrs: dict[str, str] = {}
        self._tag_stack: list[str] = []
        self._sd_rail: list[str] = []
        self._sd_explain: list[str] = []
        self._in_sd_rail = False
        self._in_sd_explain = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        classes = set((ad.get("class") or "").split())
        self._tag_stack.append(tag)

        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return

        eid = ad.get("id") or ""
        if eid == "baslide-chrome" or "baslide-chrome" in classes:
            self._chrome_depth += 1
            return
        if self._chrome_depth:
            return

        if tag == "section" and "slide" in classes:
            self._in_slide = True
            self._buf = []
            self._title_buf = []
            self._sd_rail = []
            self._sd_explain = []
            self._attrs = {
                "data-page-id": ad.get("data-page-id") or "",
                "id": eid,
                "data-units": ad.get("data-units") or "",
                "class": ad.get("class") or "",
            }
            return

        if not self._in_slide:
            return

        if "sd-rail" in classes:
            self._in_sd_rail = True
        if eid == "sd-explain" or "sd-explain" in classes:
            self._in_sd_explain = True
        if tag in {"h1", "h2", "h3"} and not self._title_buf:
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        if tag in self.SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if self._chrome_depth and (tag == "div" or tag == "nav" or tag == "aside"):
            # best-effort: decrement when leaving chrome container
            self._chrome_depth = max(0, self._chrome_depth - 1)

        if not self._in_slide:
            return

        if tag in {"h1", "h2", "h3"}:
            self._in_title = False
        if tag in {"div", "aside", "section"}:
            self._in_sd_rail = False
            self._in_sd_explain = False

        if tag == "section" and self._in_slide:
            text = "".join(self._buf)
            rail = "".join(self._sd_rail).strip()
            explain = "".join(self._sd_explain).strip()
            # Deduplicate sd-rail cloned into sd-explain
            if rail and explain and rail == explain:
                text = text.replace(explain, rail, 1)
            title = re.sub(r"\s+", " ", "".join(self._title_buf)).strip()
            self.slides.append(
                {
                    "index": len(self.slides),
                    "attrs": dict(self._attrs),
                    "title": title,
                    "text": text,
                }
            )
            self._in_slide = False
            self._buf = []
            self._attrs = {}

    def handle_data(self, data: str) -> None:
        if self._skip_depth or self._chrome_depth or not self._in_slide:
            return
        if self._in_sd_rail:
            self._sd_rail.append(data)
        if self._in_sd_explain:
            self._sd_explain.append(data)
        self._buf.append(data)
        if self._in_title:
            self._title_buf.append(data)


def load_accepted(path: Path | None) -> set[tuple[str, str, str]]:
    if not path or not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        (row.get("page", ""), row.get("code", ""), row.get("anchor", ""))
        for row in (data if isinstance(data, list) else [])
    }


def map_slides_to_pages(
    slides: list[dict], pages: list[dict]
) -> tuple[dict[int, str], list[dict]]:
    """Return slide_index → page_id and ambiguity/unmapped notes."""
    by_id = {p["id"]: p for p in pages}
    title_index: dict[str, list[str]] = {}
    for p in pages:
        t = re.sub(r"\s+", " ", (p.get("title") or "").strip())
        if t:
            title_index.setdefault(t, []).append(p["id"])

    mapping: dict[int, str] = {}
    notes: list[dict] = []
    used_pages: set[str] = set()
    order_cursor = 0
    page_ids_in_order = [p["id"] for p in pages]

    for slide in slides:
        idx = slide["index"]
        attrs = slide["attrs"]
        pid = attrs.get("data-page-id") or ""
        method = "data-page-id"
        if not pid and attrs.get("id") and re.fullmatch(r"p-\d{4}", attrs["id"]):
            pid = attrs["id"]
            method = "id"
        if not pid:
            title = slide.get("title") or ""
            # strip 续 suffix variants for match
            title_key = re.sub(r"\s+", " ", title).strip()
            cands = title_index.get(title_key) or []
            if len(cands) == 1:
                pid = cands[0]
                method = "title"
            elif len(cands) > 1:
                notes.append(
                    {
                        "slide": idx,
                        "code": "AMBIGUOUS",
                        "detail": f"title {title_key!r} matches {cands}",
                    }
                )
                method = "ambiguous"
        if not pid:
            # document order among unused pages
            while order_cursor < len(page_ids_in_order) and page_ids_in_order[order_cursor] in used_pages:
                order_cursor += 1
            if order_cursor < len(page_ids_in_order):
                pid = page_ids_in_order[order_cursor]
                order_cursor += 1
                method = "order"
            else:
                notes.append(
                    {
                        "slide": idx,
                        "code": "UNMAPPED",
                        "detail": f"no page left for slide title={slide.get('title')!r}",
                    }
                )
                continue
        if pid not in by_id:
            notes.append(
                {
                    "slide": idx,
                    "code": "UNMAPPED",
                    "detail": f"page id {pid} not in deck.json",
                }
            )
            continue
        mapping[idx] = pid
        used_pages.add(pid)
        if method in {"order", "ambiguous"}:
            notes.append(
                {
                    "slide": idx,
                    "code": "MAP",
                    "detail": f"mapped to {pid} via {method}",
                }
            )
    return mapping, notes


def main() -> int:
    parser = argparse.ArgumentParser(description="deck-audit hop2 pages→HTML")
    parser.add_argument("--work", required=True)
    parser.add_argument("--html", required=True, help="Path to deck HTML")
    parser.add_argument("--accepted", default=None)
    parser.add_argument(
        "--source",
        default=None,
        help="Degraded mode: source.md (unused for anchors; mapping by title/order only)",
    )
    args = parser.parse_args()
    work = Path(args.work)
    html_path = Path(args.html)
    assert html_path.is_file(), f"missing html: {html_path}"

    anchors_path = work / "anchors.json"
    if not anchors_path.is_file():
        import subprocess

        subprocess.check_call(
            [sys.executable, str(Path(__file__).with_name("extract-anchors.py")), "--work", str(work)]
        )
    anchors = json.loads(anchors_path.read_text(encoding="utf-8"))
    deck = json.loads((work / "deck.json").read_text(encoding="utf-8"))
    pages = deck.get("pages") or []

    skill_accepted = Path(__file__).resolve().parent.parent / "accepted.json"
    work_accepted = work / "accepted.json"
    accepted_path = Path(args.accepted) if args.accepted else (
        work_accepted if work_accepted.is_file() else skill_accepted
    )
    accepted = load_accepted(accepted_path)

    raw = html_path.read_text(encoding="utf-8", errors="replace")
    parser_html = SlideParser()
    parser_html.feed(raw)
    slides = parser_html.slides
    mapping, map_notes = map_slides_to_pages(slides, pages)

    findings: list[dict] = []
    for note in map_notes:
        if note["code"] == "UNMAPPED":
            findings.append(
                {
                    "page": None,
                    "slide": note["slide"],
                    "code": "UNMAPPED",
                    "severity": "hard",
                    "anchor": "",
                    "kind": "map",
                    "detail": note["detail"],
                }
            )
        elif note["code"] == "AMBIGUOUS":
            findings.append(
                {
                    "page": None,
                    "slide": note["slide"],
                    "code": "AMBIGUOUS",
                    "severity": "warn",
                    "anchor": "",
                    "kind": "map",
                    "detail": note["detail"],
                }
            )

    for slide in slides:
        idx = slide["index"]
        pid = mapping.get(idx)
        if not pid:
            continue
        mat = anchors["material"].get(pid) or []
        slide_anchors = extract_from_text(slide["text"], f"slide-{idx}")
        slide_norms = {a["norm"] for a in slide_anchors}

        for a in mat:
            if a["kind"] not in NUMERIC_KINDS and not (
                a["kind"] == "proper-noun" and len(a["raw"]) >= 3
            ):
                continue
            if a["norm"] in slide_norms:
                continue
            if (pid, "HMISS", a["raw"]) in accepted:
                continue
            findings.append(
                {
                    "page": pid,
                    "slide": idx,
                    "code": "HMISS",
                    "severity": "hard",
                    "anchor": a["raw"],
                    "kind": a["kind"],
                    "detail": f"in material {pid} missing from slide {idx}",
                }
            )

        # HEXTRA: numeric on slide not in material (warn)
        mat_norms = {a["norm"] for a in mat}
        for a in slide_anchors:
            if a["kind"] not in NUMERIC_KINDS:
                continue
            if a["norm"] in mat_norms:
                continue
            if (pid, "HEXTRA", a["raw"]) in accepted:
                continue
            findings.append(
                {
                    "page": pid,
                    "slide": idx,
                    "code": "HEXTRA",
                    "severity": "warn",
                    "anchor": a["raw"],
                    "kind": a["kind"],
                    "detail": f"on slide {idx} not in material {pid}",
                }
            )

    hard = [f for f in findings if f["severity"] == "hard"]
    warn = [f for f in findings if f["severity"] == "warn"]
    report = {
        "version": "1.0.0",
        "hop": "html",
        "work": str(work),
        "html": str(html_path),
        "accepted_path": str(accepted_path),
        "counts": {
            "slides": len(slides),
            "mapped": len(mapping),
            "pages": len(pages),
            "hard": len(hard),
            "warn": len(warn),
            "by_code": {
                code: sum(1 for f in findings if f["code"] == code)
                for code in sorted({f["code"] for f in findings})
            },
        },
        "mapping": {str(k): v for k, v in mapping.items()},
        "map_notes": map_notes,
        "findings": findings,
    }
    out_path = work / "audit-html.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"hop2: slides={len(slides)} mapped={len(mapping)} hard={len(hard)} warn={len(warn)} → {out_path}",
        file=sys.stderr,
    )
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
