#!/usr/bin/env python3
"""Hop2: compare page material anchors to HTML slide text. Emits audit-html.json."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anchors_lib import NUMERIC_KINDS, extract_from_text, normalize_value  # noqa: E402


class SlideParser(HTMLParser):
    """Collect text per section.slide, skipping script/style/chrome."""

    SKIP_TAGS = {"script", "style", "noscript"}
    SKIP_CLASSES = {"sd-index", "sd-tk", "sd-rail", "sd-footer", "sd-audit-copy"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slides: list[dict] = []
        self._in_slide = False
        self._skip_depth = 0
        self._chrome_depth = 0
        self._noncontent_depth = 0
        self._noncontent_tag = ""
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
        if self._noncontent_depth:
            if tag == self._noncontent_tag:
                self._noncontent_depth += 1
            return

        eid = ad.get("id") or ""
        if eid == "baslide-chrome" or "baslide-chrome" in classes:
            self._chrome_depth += 1
            return
        if self._chrome_depth:
            return

        if "hidden" in ad or ad.get("aria-hidden", "").lower() == "true" or classes & self.SKIP_CLASSES:
            self._noncontent_depth = 1
            self._noncontent_tag = tag
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
        if self._noncontent_depth:
            if tag == self._noncontent_tag:
                self._noncontent_depth -= 1
                if not self._noncontent_depth:
                    self._noncontent_tag = ""
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
            text = " ".join(self._buf)
            rail = " ".join(self._sd_rail).strip()
            explain = " ".join(self._sd_explain).strip()
            # Deduplicate sd-rail cloned into sd-explain
            if rail and explain and rail == explain:
                text = text.replace(explain, rail, 1)
            title = re.sub(r"\s+", " ", " ".join(self._title_buf)).strip()
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
        if self._skip_depth or self._chrome_depth or self._noncontent_depth or not self._in_slide:
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


def scalar_text(value) -> list[str]:
    if isinstance(value, dict):
        return [text for child in value.values() for text in scalar_text(child)]
    if isinstance(value, list):
        return [text for child in value for text in scalar_text(child)]
    return [str(value)] if value is not None else []


def plan_material(pages: list[dict]) -> dict[str, list[dict]]:
    """Required visible material is the public renderer payload, not audit provenance."""
    material = {}
    for page in pages:
        content = page.get("content") or {}
        blocks = content.get("blocks") or []
        template = page.get("template")
        if template == "kpi":
            visible = [block for block in blocks if block.get("kind") == "kpi-card"]
        elif template == "chart":
            visible = []
        elif template == "chart-table":
            columns, rows = content.get("columns") or [], content.get("rows") or []
            y_name = (((page.get("evidence") or [{}])[0].get("encoding") or {}).get("mapping") or {}).get("y")
            picks = [0]
            if y_name in columns and columns.index(y_name) not in picks:
                picks.append(columns.index(y_name))
            if len(picks) == 1 and len(columns) > 1:
                picks.append(1)
            visible = [[columns[i] for i in picks], [[row[i] if i < len(row) else "" for i in picks] for row in rows[:6]]]
        else:
            visible = [block for block in blocks if block.get("kind") != "fig"]
        text = "\n".join([str(page.get("title") or ""), *scalar_text(visible)])
        material[page["id"]] = extract_from_text(text, page["id"])
    return material


def plan_authorized_material(pages: list[dict]) -> dict[str, set[str]]:
    """All plan evidence may render, but only content blocks are required to render."""
    out = {}
    for page in pages:
        text = "\n".join(scalar_text({
            "title": page.get("title"),
            "takeaway": page.get("takeaway"),
            "claim": page.get("claim"),
            "evidence": page.get("evidence"),
            "content": page.get("content"),
        }))
        out[page["id"]] = {item["norm"] for item in extract_from_text(text, page["id"])}
    return out


def renderer_derived_norms(page: dict, slide_index: int | None = None) -> set[str]:
    """Known labels mechanically derived by the named SVG recipe."""
    viz = page.get("visualization")
    rows = (page.get("content") or {}).get("rows") or []
    width = max((len(row) for row in rows if isinstance(row, list)), default=0)
    columns = []
    for index in range(width):
        values = []
        for row in rows:
            if index >= len(row):
                continue
            match = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(row[index]))
            if match:
                values.append(float(match.group(0).replace(",", "")))
        if values:
            columns.append(values)
    out = set()
    if page.get("template") == "chapter" and slide_index is not None:
        out.update({str(max(1, slide_index // 12 + 1)), str(slide_index + 1)})
    def formatted(value: float) -> str:
        if abs(value) >= 100000000:
            return normalize_value(f"{value / 100000000:.2f}亿")
        if abs(value) >= 10000:
            return normalize_value(f"{value / 10000:.1f}万")
        return normalize_value(f"{value:.1f}")

    def nice_max(value: float) -> float:
        if value <= 0:
            return 1.0
        magnitude = 10 ** math.floor(math.log10(value))
        return next(multiplier * magnitude for multiplier in (1, 2, 2.5, 5, 10) if value <= multiplier * magnitude + 1e-9)

    for values in columns:
        for value in values:
            rounded = formatted(value)
            out.update({rounded, normalize_value(rounded + "%"), normalize_value(rounded + "万")})
            if abs(value) >= 10000:
                out.add(normalize_value(f"{value / 10000:.1f}万"))
    if viz == "bubble":
        out.add("0")
        for values in columns:
            out.add(normalize_value(f"{max(values) / 2:.1f}"))
            if len(values) > 1:
                if min(values) == max(values):
                    for offset in (-1, -.5, .5, 1):
                        out.add(normalize_value(f"{values[0] + offset:.1f}"))
                else:
                    out.add(normalize_value(f"{(min(values) + max(values)) / 2:.1f}"))
    if viz in {"hist-cdf", "pareto"}:
        out.update(normalize_value(f"{tick}%") for tick in (0, 25, 50, 75, 100))
        for values in columns:
            top = nice_max(max(values))
            for index in range(5):
                tick = top * index / 4
                core = formatted(tick)
                out.update({core, normalize_value(core + "%"), normalize_value(core + "元"), normalize_value(core + "家")})
            total = sum(abs(value) for value in values)
            if total:
                running = 0.0
                for value in values:
                    running += abs(value)
                    out.add(normalize_value(f"{round(running / total * 100)}%"))
    if viz == "quadrant":
        ceiling = min(100, int(max((max(values) for values in columns), default=0)))
        out.update(str(value) for value in range(0, ceiling + 1, 5))
        for values in columns:
            ordered = sorted(values)
            if ordered:
                out.add(formatted(ordered[len(ordered) // 2]))
    if viz == "slope":
        for row in rows:
            values = []
            for cell in row:
                match = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(cell))
                if match:
                    values.append(float(match.group(0).replace(",", "")))
            for left in values:
                for right in values:
                    delta = formatted(right - left)
                    out.update({delta, normalize_value(delta + "%"), normalize_value(delta + "万")})
    return out


def numeric_authorized(norm: str, kind: str, authorized: set[str]) -> bool:
    if norm in authorized:
        return True
    if kind == "quantity":
        numeric = re.match(r"-?\d[\d,]*(?:\.\d+)?", norm)
        if numeric and normalize_value(numeric.group(0)) in authorized:
            return True
    return any(
        value.startswith(norm + "/")
        or value.endswith("/" + norm)
        or re.fullmatch(re.escape(norm) + r"(?:%|万|亿|元|家|店|人|次|桌|项|个|分|倍|天|小时|分钟|㎡|m²|bps|pp)", value)
        for value in authorized
    )


def map_slides_to_pages(
    slides: list[dict], pages: list[dict]
) -> tuple[dict[int, str], list[dict], dict[int, str]]:
    """Return slide_index → page_id, notes, and slide_index → map method."""
    by_id = {p["id"]: p for p in pages}
    title_index: dict[str, list[str]] = {}
    for p in pages:
        t = re.sub(r"\s+", " ", (p.get("title") or "").strip())
        if t:
            title_index.setdefault(t, []).append(p["id"])

    mapping: dict[int, str] = {}
    methods: dict[int, str] = {}
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
        methods[idx] = method
        used_pages.add(pid)
        if method in {"order", "ambiguous"}:
            notes.append(
                {
                    "slide": idx,
                    "code": "MAP",
                    "detail": f"mapped to {pid} via {method}",
                }
            )
    return mapping, notes, methods


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
    parser.add_argument(
        "--dump-slides",
        default=None,
        metavar="PATH",
        help="Write slides.json (index, id, title, text, mapped page, map reason) for GUI",
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
    plan_path = work / "deck-plan.json"
    deck = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else json.loads((work / "deck.json").read_text(encoding="utf-8"))
    pages = deck.get("pages") or []
    pages_by_id = {page["id"]: page for page in pages}
    structured = plan_path.is_file() and deck.get("contract_version")
    material = plan_material(pages) if structured else anchors["material"]
    authorized = plan_authorized_material(pages) if structured else {
        pid: {item["norm"] for item in items} for pid, items in material.items()
    }

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
    mapping, map_notes, methods = map_slides_to_pages(slides, pages)

    # Always write slides.json under work for the GUI inspector; --dump-slides can override path.
    dump_target = Path(args.dump_slides) if args.dump_slides else (work / "slides.json")
    dump_rows = []
    for slide in slides:
        idx = slide["index"]
        attrs = slide.get("attrs") or {}
        dump_rows.append(
            {
                "slide": idx,
                "id": attrs.get("id") or attrs.get("data-page-id") or "",
                "title": slide.get("title") or "",
                "text": slide.get("text") or "",
                "mapped_page": mapping.get(idx),
                "map_reason": methods.get(idx) or "unmapped",
                "data_units": attrs.get("data-units") or "",
            }
        )
    dump_target.write_text(
        json.dumps(
            {"version": "1.0.0", "html": str(html_path), "slides": dump_rows},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"slides dump → {dump_target}", file=sys.stderr)

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
        mat = material.get(pid) or []
        slide_text = slide["text"].replace(f"{idx + 1} / {len(slides)}", "")
        slide_text = re.sub(rf"\bCH\.\s*{idx + 1}\b", "", slide_text, flags=re.I)
        slide_anchors = extract_from_text(slide_text, f"slide-{idx}")
        slide_norms = {a["norm"] for a in slide_anchors}
        slide_text_norm = normalize_value(slide["text"])

        for a in mat:
            if a["kind"] not in NUMERIC_KINDS and not (
                a["kind"] == "proper-noun" and len(a["raw"]) >= 3
            ):
                continue
            if a["norm"] in slide_norms or a["norm"] in slide_text_norm:
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
        page = pages_by_id.get(pid) or {}
        mat_norms = set(authorized.get(pid) or {a["norm"] for a in mat})
        mat_norms.update(renderer_derived_norms(page, idx))
        for a in slide_anchors:
            if a["kind"] not in NUMERIC_KINDS:
                continue
            if numeric_authorized(a["norm"], a["kind"], mat_norms):
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
