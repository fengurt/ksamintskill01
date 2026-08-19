#!/usr/bin/env python3
"""Deterministic GF4p2slides deck-plan → self-contained Baslide HTML."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from baslide_viz import default_baslide, figure_for_page

ROLE_TO_JOB = {
    "cover": "cover",
    "toc": "toc",
    "chapter": "divider",
    "readme": "readme",
    "statement": "statement",
    "kpi": "kpi",
    "roster": "roster",
    "chart": "chart",
    "chart-table": "chart-table",
    "matrix": "matrix",
    "compare": "compare",
    "verdict": "verdict",
}

CN_NUM = "零壹贰叁肆伍陆柒捌玖拾"

DEFAULT_BASLIDE = default_baslide()

MUSTACHE_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")

THEME_TOKENS = {
    "TIANSIGHT": ("#F4F0E7", "#17130D", "#76551F", "#8C3228"),
    "magazine": ("#F1EFEA", "#0A0A0B", "#8E382E", "#B77A29"),
    "swiss": ("#FAFAF8", "#0A0A0A", "#002FA7", "#D51F2B"),
    "tableai": ("#FFFFFF", "#0A1626", "#A88B52", "#8A3042"),
    "atelier": ("#FFFFFF", "#0A1626", "#A88B52", "#8A3042"),
}


def esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def layout_name(page: dict) -> str:
    layout = page.get("layout")
    return str(layout.get("solved") or "") if isinstance(layout, dict) else str(layout or "")


def cn_chapter(n: int) -> str:
    if 1 <= n <= 10:
        return CN_NUM[n]
    return str(n)


def extract_section(template_html: str) -> str:
    m = re.search(r"<section\b[^>]*>[\s\S]*?</section>", template_html, re.I)
    if not m:
        raise ValueError("no <section> in job template")
    return m.group(0)


def replace_div_inner(html: str, class_name: str, new_inner: str) -> str:
    pattern = re.compile(
        rf"<div\b[^>]*class=\"[^\"]*\b{re.escape(class_name)}\b[^\"]*\"[^>]*>",
        re.I,
    )
    m = pattern.search(html)
    if not m:
        return html
    start_inner = m.end()
    pos = m.start()
    depth = 0
    length = len(html)
    while pos < length:
        if html.startswith("<div", pos) and (pos + 4 == length or html[pos + 4] in " \t\n/>"):
            gt = html.find(">", pos)
            if gt < 0:
                break
            depth += 1
            pos = gt + 1
            continue
        if html.startswith("</div>", pos):
            depth -= 1
            if depth == 0:
                return html[:start_inner] + new_inner + html[pos:]
            pos += 6
            continue
        pos += 1
    return html


def replace_tag_inner(html: str, class_name: str, new_inner: str) -> str:
    pattern = re.compile(
        rf"(<(?:div|span)\b[^>]*class=\"[^\"]*\b{re.escape(class_name)}\b[^\"]*\"[^>]*>)([\s\S]*?)(</(?:div|span)>)",
        re.I,
    )
    return pattern.sub(lambda m: m.group(1) + new_inner + m.group(3), html, count=1)


def md_to_html(text: str) -> str:
    """Minimal markdown → TIANSIGHT-flavored HTML. Tables, lists, paragraphs."""
    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    def is_table_sep(line: str) -> bool:
        s = line.strip()
        return bool(re.match(r"^\|?[\s:|-]+\|[\s:|-]+", s)) and "-" in s

    def split_row(line: str) -> list[str]:
        s = line.strip()
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        return [c.strip() for c in s.split("|")]

    def inline(s: str) -> str:
        s = esc(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        return s

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            headers = split_row(line)
            i += 2
            rows: list[list[str]] = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            cells = []
            cells.append("<tr>" + "".join(f"<th>{inline(h)}</th>" for h in headers) + "</tr>")
            for row in rows:
                klass = ' class="sd-sum"' if any("合计" in c or "总计" in c for c in row) else ""
                tds = []
                for j, c in enumerate(row):
                    num = j > 0 and bool(re.search(r"[\d%％]", c))
                    tds.append(f'<td class="num">{inline(c)}</td>' if num else f"<td>{inline(c)}</td>")
                cells.append(f"<tr{klass}>" + "".join(tds) + "</tr>")
            out.append('<table class="sd-table">' + "".join(cells) + "</table>")
            continue
        if re.match(r"^[-*+]\s+", line) or re.match(r"^\d+[.)]\s+", line):
            items: list[str] = []
            ol = bool(re.match(r"^\d+[.)]\s+", line))
            while i < n and (re.match(r"^[-*+]\s+", lines[i]) or re.match(r"^\d+[.)]\s+", lines[i])):
                item = re.sub(r"^([-*+]|\d+[.)])\s+", "", lines[i])
                items.append(f"<li>{inline(item)}</li>")
                i += 1
            tag = "ol" if ol else "ul"
            out.append(f"<{tag} class=\"sd-list\">{''.join(items)}</{tag}>")
            continue
        if line.startswith("#"):
            title = re.sub(r"^#+\s*", "", line).strip()
            out.append(f"<p class=\"sd-lede\"><b>{inline(title)}</b></p>")
            i += 1
            continue
        if line.strip() in {"---", "***", "___"}:
            i += 1
            continue
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not lines[i].startswith("|") and not re.match(
            r"^[-*+#]", lines[i]
        ):
            para.append(lines[i])
            i += 1
        out.append(f"<p>{inline(' '.join(p.strip() for p in para))}</p>")
    return "\n".join(out) if out else "<p></p>"


def structured_html(page: dict) -> str:
    """Bind typed blocks; the human Markdown body is never parsed here."""
    out: list[str] = []
    for block in (page.get("content") or {}).get("blocks") or []:
        kind = block.get("kind")
        if kind == "fig":
            continue
        if kind == "claim":
            out.append(f'<div class="sd-block" data-block="claim"><div class="sd-claim">{esc(block.get("text") or "")}</div></div>')
        elif kind == "lede":
            out.append(f'<div class="sd-block" data-block="lede"><p class="sd-lede">{esc(block.get("text") or "")}</p></div>')
        elif kind == "bullets":
            items = "".join(f"<li>{esc(item)}</li>" for item in (block.get("items") or []))
            out.append(f'<div class="sd-block" data-block="bullets"><ul class="sd-list">{items}</ul></div>')
        elif kind == "table":
            cols = block.get("columns") or []
            head = "".join(f"<th>{esc(col)}</th>" for col in cols)
            rows = "".join("<tr>" + "".join((f'<td class="num">{esc(cell)}</td>' if index and re.search(r"\d", str(cell)) else f"<td>{esc(cell)}</td>") for index, cell in enumerate(row)) + "</tr>" for row in (block.get("rows") or []))
            out.append(f'<div class="sd-block" data-block="table"><table class="sd-table"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        elif kind == "kpi-card":
            out.append(f'<div class="sd-block sd-kpi" data-block="kpi-card"><span class="l">{esc(block.get("label") or "")}</span><strong class="v">{esc(block.get("value") or "")}<small>{esc(block.get("unit") or "")}</small></strong><span class="d">{esc(block.get("note") or block.get("delta") or "")}</span></div>')
        elif kind in {"callout", "step", "profile"}:
            out.append(f'<div class="sd-block sd-callout" data-block="{esc(kind)}"><strong class="t">{esc(block.get("title") or block.get("name") or "")}</strong><p class="b">{esc(block.get("text") or "")}</p></div>')
        elif kind == "quote":
            out.append(f'<div class="sd-block" data-block="quote"><blockquote class="sd-quote">{esc(block.get("text") or "")}<span class="attrib">{esc(block.get("attrib") or "")}</span></blockquote></div>')
        elif kind in {"media", "embed"}:
            src = block.get("src") or block.get("fallback_img") or "media slot"
            out.append(f'<div class="sd-block" data-block="{esc(kind)}"><figure class="sd-media" data-slot="{esc(block.get("slot") or "hero")}" data-ratio="{esc(block.get("ratio") or "16:9")}"><div class="frame"><span class="ph">{esc(src)}</span></div><figcaption>{esc(block.get("caption") or "")}</figcaption></figure></div>')
    return "".join(out)


def viz_material(page: dict) -> str:
    for block in (page.get("content") or {}).get("blocks") or []:
        if block.get("kind") != "fig":
            continue
        data = block.get("data") or {}
        columns, rows = data.get("columns") or [], data.get("rows") or []
        if columns and rows:
            return "| " + " | ".join(map(str, columns)) + " |\n| " + " | ".join("---" for _ in columns) + " |\n" + "\n".join("| " + " | ".join(map(str, row)) + " |" for row in rows)
        labels, values = data.get("labels") or data.get("x") or [], data.get("values") or data.get("y") or []
        if labels and values:
            return "| label | value |\n| --- | --- |\n" + "\n".join(f"| {label} | {value} |" for label, value in zip(labels, values))
    return ""


def normalize_plan_page(page: dict) -> dict:
    template = page.get("template") or page.get("type") or "statement"
    template = {"quote": "statement", "playbook": "verdict", "gallery": "roster", "interactive": "chart"}.get(template, template)
    provenance = page.get("provenance") or {}
    claim = page.get("claim") or {}
    takeaway = page.get("takeaway") or (claim.get("render") if isinstance(claim, dict) else claim) or ""
    return {
        **page,
        "role": template,
        "fill": page.get("visualization") or page.get("fill"),
        "source": page.get("source") or provenance.get("source") or "",
        "how_to_read": provenance.get("how_to_read") or page.get("how_to_read") or "",
        "takeaway": takeaway,
        "_structured": True,
    }


def normalize_legacy_slide(slide: dict) -> dict:
    slots = slide.get("slots") or {}
    blocks = []
    if slots.get("bullets"):
        blocks.append({"kind": "bullets", "items": slots["bullets"]})
    if slots.get("columns") and slots.get("rows"):
        blocks.append({"kind": "table", "columns": slots["columns"], "rows": slots["rows"], "sum": slots.get("sum") or []})
    return normalize_plan_page({
        **slide,
        "template": slide.get("job") or "statement",
        "visualization": slide.get("fill"),
        "content": {"blocks": blocks},
    })


def strip_page_chrome(md: str) -> str:
    out: list[str] = []
    for line in md.splitlines():
        if re.match(r"^#+\s*u-\d{4}\s*$", line, re.I):
            continue
        if re.match(r"^units:\s*", line, re.I):
            continue
        if re.match(r"^role:\s*", line, re.I):
            continue
        line = re.sub(r"\bu-\d{4}\b", " ", line, flags=re.I)
        out.append(line)
    # drop a leading # title line that duplicates the page title
    while out and (not out[0].strip() or out[0].startswith("# ")):
        if out[0].startswith("# "):
            out.pop(0)
            continue
        out.pop(0)
    return "\n".join(out).strip()


def load_units(work: Path) -> dict[str, str]:
    raw = json.loads((work / "units.json").read_text(encoding="utf-8"))
    if isinstance(raw, dict) and all(isinstance(v, str) for v in raw.values()):
        return raw
    if isinstance(raw, dict) and "units" in raw:
        out = {}
        for u in raw["units"]:
            out[u["id"]] = u.get("text") or u.get("digest") or ""
        return out
    return {}


def page_material_text(page: dict, work: Path, units: dict[str, str]) -> str:
    if page.get("_structured"):
        return str((page.get("content") or {}).get("audit_text") or "")
    md_path = work / "pages" / f"{page['id']}.md"
    if md_path.is_file():
        body = strip_page_chrome(md_path.read_text(encoding="utf-8"))
        if body.strip():
            return body
    parts: list[str] = []
    for uid in page.get("units") or []:
        t = units.get(uid)
        if t:
            parts.append(t)
    return "\n\n".join(parts)


def fill_mustaches(html: str, values: dict[str, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(0)[2:-2]
        return values.get(key, "")

    return MUSTACHE_RE.sub(repl, html)


def set_section_attrs(section: str, page: dict, job: str, index: int, total: int) -> str:
    units = " ".join(page.get("units") or [])
    pid = page["id"]
    role = page.get("role") or job
    fill = page.get("fill") or ""

    def add_attrs(m: re.Match[str]) -> str:
        tag = m.group(0)
        tag = re.sub(r'\sclass="([^"]*)"', lambda cm: ' class="' + re.sub(r"\bon\b", "", cm.group(1)).strip() + '"', tag)
        if index == 0 and ' class="' in tag:
            tag = tag.replace(' class="', ' class="on ', 1)
        pairs = [
            ("data-page-id", pid),
            ("data-units", units),
            ("data-page-type", role),
            ("data-job", job),
            ("data-layout", layout_name(page)),
            ("data-pack", page.get("pack") or "mid"),
            ("data-overflow-of", page.get("overflow_of") or ""),
            ("data-node-role", (page.get("node") or {}).get("role") or ""),
            ("data-intent", page.get("intent") or ""),
            ("data-as-of", next((str((item.get("source") or {}).get("as_of") or "") for item in (page.get("evidence") or []) if isinstance(item, dict)), "")),
        ]
        if fill:
            pairs.append(("data-fill", str(fill)))
        for attr, val in pairs:
            if f"{attr}=" in tag:
                tag = re.sub(rf'{attr}="[^"]*"', f'{attr}="{esc(val)}"', tag)
            else:
                tag = tag[:-1] + f' {attr}="{esc(val)}">'
        return tag

    return re.sub(r"<section\b[^>]*>", add_attrs, section, count=1)


def fill_figure(section: str, page: dict, material: str, job: str, body_html: str, title: str) -> str:
    fig = None
    try:
        fig = figure_for_page(title, material, preset_fill=page.get("fill") or page.get("recipe"))
    except Exception as exc:
        if page.get("fill"):
            raise ValueError(f"{page.get('id')} {page.get('fill')} renderer failed: {exc}") from exc
        print(f"render-deck: viz skip {page.get('id')}: {exc}", file=sys.stderr)
    if fig and fig.svg:
        page["fill"] = fig.fill or page.get("fill")
        caption = fig.caption or page.get("takeaway") or title
        fallback = fig.table_html or ""
        svg = re.sub(
            r'font-size="([\d.]+)"',
            lambda match: f'font-size="{max(float(match.group(1)), 21 if job == "chart-table" else 18):g}"',
            fig.svg,
        )
        figure = f'<figure class="sd-v2-figure" role="img" aria-label="{esc(caption)}">{svg}<figcaption>{esc(caption)}</figcaption><div class="sd-v2-fallback" hidden>{fallback}</div></figure>'
        if job == "chart-table":
            columns = (page.get("content") or {}).get("columns") or []
            rows = (page.get("content") or {}).get("rows") or []
            y_name = ((((page.get("evidence") or [{}])[0].get("encoding") or {}).get("mapping") or {}).get("y"))
            picks = [0]
            if y_name in columns and columns.index(y_name) not in picks:
                picks.append(columns.index(y_name))
            if len(picks) == 1 and len(columns) > 1:
                picks.append(1)
            preview_rows = []
            for row in rows[:6]:
                cells = []
                for j, i in enumerate(picks):
                    klass = ' class="num"' if j else ""
                    cells.append(f'<td{klass}>{esc(row[i] if i < len(row) else "")}</td>')
                preview_rows.append("<tr>" + "".join(cells) + "</tr>")
            preview = '<table class="sd-table"><tr>' + "".join(f"<th>{esc(columns[i])}</th>" for i in picks) + "</tr>" + "".join(preview_rows) + "</table>"
            if columns and rows:
                section = re.sub(
                    r'<table class="sd-table">[\s\S]*?</table>',
                    lambda _: preview,
                    section,
                    count=1,
                )
            section = re.sub(
                r"\[[^\]]*SVG viewBox 0 0 1170 500[^\]]*\]",
                lambda _: figure,
                section,
                count=1,
            )
            return section
        return replace_div_inner(section, "sd-content", figure)
    if page.get("fill"):
        raise ValueError(f"{page.get('id')} {page.get('fill')} produced no SVG")
    if any(ch in material for ch in "┌│└─█"):
        body_html = f'<pre class="sd-lede">{esc(material)}</pre>'
    return replace_div_inner(section, "sd-content", body_html or f"<p>{esc(title)}</p>")


def fill_section(section: str, page: dict, work: Path, units: dict[str, str], index: int, total: int, deck_name: str) -> str:
    role = page.get("role") or "statement"
    job = ROLE_TO_JOB.get(role, "statement")
    title = page.get("title") or ""
    path = page.get("outline_path") or []
    kicker = " · ".join([p for p in path[-2:]] or [role])
    material = viz_material(page) if page.get("_structured") else page_material_text(page, work, units)
    if page.get("_structured") and not material:
        material = page_material_text(page, work, units)
    body_html = structured_html(page) if page.get("_structured") else (md_to_html(material) if material else "")
    blocks = (page.get("content") or {}).get("blocks") or []
    prose = " ".join(str(block.get("text") or "") for block in blocks if block.get("kind") in {"lede", "claim", "quote"}).strip()
    sentences = [part.strip() for part in re.split(r"(?<=[。！？!?])\s*", prose) if part.strip()]
    statement_main = (sentences[0] if sentences else page.get("takeaway") or title)[:180]
    statement_support = ("".join(sentences[1:]) or page.get("takeaway") or prose)[:260]
    cards = [block for block in blocks if block.get("kind") == "kpi-card"][:4]

    values = {
        "PAGE_INDEX": str(index + 1),
        "PAGE_TOTAL": str(total),
        "DECK_NAME": deck_name,
        "DECK_KICKER_EN": "DIAGNOSIS",
        "TITLE_LINE1": title,
        "TITLE_LINE2": "",
        "ONE_LINE_DECISION": (page.get("takeaway") or title)[:180],
        "PERIOD": "",
        "SCOPE": "",
        "BASIS": "",
        "ISSUED_DATE": "",
        "STATEMENT_CHIP": kicker,
        "STATEMENT_TITLE": title,
        "STATEMENT_MAIN": statement_main,
        "STATEMENT_SUPPORT": statement_support,
        "KPI_CHIP": kicker,
        "KPI_TITLE": title,
        "README_CHIP": kicker,
        "README_TITLE": title,
        "VERDICT_CHIP": kicker,
        "VERDICT_TITLE": title,
        "MATRIX_CHIP": kicker,
        "MATRIX_TITLE": title,
        "COMPARE_CHIP": kicker,
        "COMPARE_TITLE": title,
        "TOC_CHIP": "目录 · CONTENTS",
        "CHAPTER_NUM_CN": cn_chapter(max(1, index // 12 + 1)),
        "CHAPTER_TITLE_CN": title,
        "CHAPTER_KICKER_EN": "CHAPTER",
        "CHAPTER_ARABIC_LABEL": f"CH. {index + 1}",
        "CHART_TABLE_TITLE": title,
        "FIG_INDEX": str(index + 1),
        "FIG_TOTAL": str(total),
        "FIG_CHIP": kicker,
        "SOURCE_DETAIL": page.get("source") or "source units (verbatim)",
        "SOURCE_SYNC_STATUS": "ready",
        "SOURCE_SYNC_LABEL": "READY",
        "SOURCE_SYNC_AT": "—",
        "SOURCE_DB_ID": "",
        "GLOSSARY_DB_ID": "",
        "GLOSSARY_SYNC_STATUS": "ready",
        "GLOSSARY_SYNC_LABEL": "READY",
        "TERM_1_NAME": "口径",
        "TERM_1_DEF": page.get("how_to_read") or "见正文",
        "HOW_TO_READ_NOTE": page.get("how_to_read") or "",
        "CONCLUSION_DB_ID": "",
        "CONCLUSION_SYNC_STATUS": "ready",
        "CONCLUSION_SYNC_LABEL": "READY",
        "CONCLUSION_TEXT": page.get("takeaway") or title,
        "CONCLUSION_SYNC_AT": "—",
        "CONFIDENCE_DB_ID": "",
        "CONFIDENCE_A_NOTE": "数字来自源文档，机械排版",
        "CONFIDENCE_B_NOTE": "—",
        "CONFIDENCE_C_NOTE": "大纲/分页为 bootstrap 草稿",
        "KPI_1_LABEL": "",
        "KPI_1_VALUE": "",
        "KPI_1_DELTA": "",
        "KPI_2_LABEL": "",
        "KPI_2_VALUE": "",
        "KPI_2_DELTA": "",
        "KPI_3_LABEL": "",
        "KPI_3_VALUE": "",
        "KPI_3_DELTA": "",
        "KPI_4_LABEL": "",
        "KPI_4_VALUE": "",
        "KPI_4_DELTA": "",
        "ACT_1_CN": "",
        "ACT_1_TITLE": "",
        "ACT_1_KICKER_EN": "",
        "ACT_2_CN": "",
        "ACT_2_TITLE": "",
        "ACT_2_KICKER_EN": "",
        "ACT_3_CN": "",
        "ACT_3_TITLE": "",
        "ACT_3_KICKER_EN": "",
        "ACT_4_CN": "",
        "ACT_4_TITLE": "",
        "ACT_4_KICKER_EN": "",
        "ACT_5_CN": "",
        "ACT_5_TITLE": "",
        "ACT_5_KICKER_EN": "",
        "ACT_6_CN": "",
        "ACT_6_TITLE": "",
        "ACT_6_KICKER_EN": "",
        "ACT_7_CN": "",
        "ACT_7_TITLE": "",
        "ACT_7_KICKER_EN": "",
        "ACT_8_CN": "",
        "ACT_8_TITLE": "",
        "ACT_8_KICKER_EN": "",
        "ACT_9_CN": "",
        "ACT_9_TITLE": "",
        "ACT_9_KICKER_EN": "",
    }
    for card_index in range(4):
        card = cards[card_index] if card_index < len(cards) else {}
        slot = card_index + 1
        values[f"KPI_{slot}_LABEL"] = str(card.get("label") or "")
        values[f"KPI_{slot}_VALUE"] = str(card.get("value") or "") + str(card.get("unit") or "")
        values[f"KPI_{slot}_DELTA"] = str(card.get("note") or card.get("delta") or "")

    # Pull period/scope from first units on cover
    blob = material[:800]
    pm = re.search(r"分析期间[：:]\s*(.+)", blob)
    if pm:
        values["PERIOD"] = pm.group(1).strip()[:40]
    sm = re.search(r"分析范围[：:]\s*(.+)", blob)
    if sm:
        values["SCOPE"] = sm.group(1).strip()[:40]

    section = fill_mustaches(section, values)
    if job == "kpi":
        section = re.sub(r'\s*<div class="sd-kpi"[^>]*>\s*<div class="l"></div>\s*<div class="v"></div>\s*<div class="d up"></div>\s*</div>', "", section)
    section = set_section_attrs(section, page, job, index, total)
    section = replace_tag_inner(section, "sd-chip", esc(kicker or role))
    section = replace_tag_inner(section, "sd-h2", esc(title or role))
    section = replace_tag_inner(section, "sd-index", f"{index + 1} / {total}")
    if role in {"cover", "chapter"}:
        section = replace_tag_inner(section, "sd-hero", esc(title))
        if role == "chapter":
            section = section.replace('<div style="position:absolute; bottom:4%;', '<div class="sd-footer" style="position:absolute; bottom:4%;', 1)
        # Keep anchors on cover/chapter: append a compact material block
        if material and body_html:
            extra = f'<div class="sd-content" style="position:absolute;left:var(--sd-margin);right:var(--sd-margin);bottom:8%;max-height:28%;overflow:auto;font-size:var(--sd-type-small);">{body_html}</div>'
            section = section.replace("</section>", extra + "</section>")
    else:
        if job in {"chart", "chart-table"}:
            section = fill_figure(section, page, material, job, body_html, title)
        elif page.get("_structured") and job == "statement":
            section = replace_div_inner(section, "sd-content", structured_html(page))
        elif page.get("_structured") and job == "kpi":
            pass
        else:
            inner = body_html or f"<p>{esc(title)}</p>"
            replaced = replace_div_inner(section, "sd-content", inner)
            if replaced == section:
                section = section.replace("</section>", f'<div class="sd-content">{inner}</div></section>')
            else:
                section = replaced

    section = MUSTACHE_RE.sub("", section)
    if page.get("_structured"):
        payload = json.dumps(page, ensure_ascii=False).replace("</", "<\\/")
        section = section.replace(
            "</section>",
            f'<script type="application/json" class="sd-data">{payload}</script></section>',
        )
    section = re.sub(r"(-?\d+(?:\.\d+)?)px\b", lambda match: f"{float(match.group(1)) / 16:g}rem", section)
    return section


def logo_data_uri(logo_path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(logo_path.read_bytes()).decode("ascii")


def inline_logo_css(css: str, logo_path: Path) -> str:
    if not logo_path.is_file():
        return css.replace('url("logo/侍天.png")', "none")
    return css.replace('url("logo/侍天.png")', f'url("{logo_data_uri(logo_path)}")')


def verified_brand_logo(work: Path, theme: str, fallback: Path) -> tuple[Path, dict]:
    if theme != "TIANSIGHT":
        return fallback, {}
    config_path = Path(__file__).resolve().parent.parent / "design" / "brands" / "tiansight.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    logo = config["logo"]
    target = work / "assets" / "brand" / "tiansight-logo.png"
    if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == logo["sha256"]:
        return target, config
    url = logo["url"]
    if urlparse(url).scheme != "https" or urlparse(url).hostname != "media.apuch.art":
        raise ValueError("untrusted tiansight logo URL")
    request = Request(url, headers={"User-Agent": "mdpages2htmlslides/2"})
    try:
        with urlopen(request, timeout=20) as response:
            if urlparse(response.geturl()).hostname != "media.apuch.art":
                raise ValueError("tiansight logo redirected to an untrusted host")
            raw = response.read(2 * 1024 * 1024 + 1)
    except OSError as exc:
        print(f"render-deck: official logo unavailable, using bundled fallback: {exc}", file=sys.stderr)
        return fallback, config
    if len(raw) > 2 * 1024 * 1024 or hashlib.sha256(raw).hexdigest() != logo["sha256"]:
        raise ValueError("tiansight logo failed size or SHA-256 verification")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    return target, config


def render(work: Path, theme: str, baslide: Path, out: Path) -> int:
    if theme not in THEME_TOKENS:
        raise ValueError(f"unknown theme: {theme}")
    jobs_dir = baslide / "templates" / "TIANSIGHT" / "jobs"
    css_path = baslide / "templates" / "TIANSIGHT" / "TIANSIGHT-v2.css"
    js_path = baslide / "templates" / "TIANSIGHT" / "TIANSIGHT-deck.js"
    assert jobs_dir.is_dir(), f"missing TIANSIGHT jobs at {jobs_dir}"
    assert css_path.is_file(), f"missing {css_path}"
    assert js_path.is_file(), f"missing {js_path}"

    plan_path = work / "deck-plan.json"
    legacy_plan_path = work / "slide-plan.json"
    legacy_path = work / "deck.json"
    source_path = plan_path if plan_path.is_file() else legacy_plan_path if legacy_plan_path.is_file() else legacy_path
    deck = json.loads(source_path.read_text(encoding="utf-8"))
    pages = deck.get("pages") or deck.get("slides") or []
    if plan_path.is_file():
        pages = [normalize_plan_page(page) for page in pages]
    elif legacy_plan_path.is_file():
        pages = [normalize_legacy_slide(page) for page in pages]
    assert pages, "deck plan has no pages"
    units = load_units(work) if (work / "units.json").is_file() else {}
    source = deck.get("source") or ""
    deck_name = deck.get("title") or deck.get("deck_name") or (Path(source).stem if source else work.name)

    templates: dict[str, str] = {}
    for job in sorted(set(ROLE_TO_JOB.values())):
        p = jobs_dir / f"{job}.html"
        if p.is_file():
            templates[job] = extract_section(p.read_text(encoding="utf-8"))

    sections: list[str] = []
    total = len(pages)
    for i, page in enumerate(pages):
        role = page.get("role") or "statement"
        job = ROLE_TO_JOB.get(role, "statement")
        tpl = templates.get(job) or templates.get("statement")
        if not tpl:
            raise SystemExit(f"no template for job {job}")
        sections.append(fill_section(tpl, page, work, units, i, total, deck_name))

    logo_path, brand = verified_brand_logo(work, theme, baslide / "templates" / "TIANSIGHT" / "logo" / "侍天.png")
    if logo_path.is_file():
        uri = logo_data_uri(logo_path)
        sections = [re.sub(r'src="[^\"]*logo/[^\"]*"', f'src="{uri}"', section) for section in sections]
    else:
        sections = [re.sub(r"<img\b[^>]*src=\"[^\"]*logo/[^\"]*\"[^>]*>", "", section) for section in sections]
    css = inline_logo_css(css_path.read_text(encoding="utf-8"), logo_path)
    surface, ink, accent, negative = THEME_TOKENS[theme]
    tokens = brand.get("tokens") or {}
    primary = tokens.get("primary") or surface
    paper = tokens.get("paper") or surface
    highlight = tokens.get("highlight") or accent
    muted = tokens.get("muted") or ink
    css += f"""
:root{{--slide-aspect:16/9;--gf-surface:{surface};--gf-paper:{paper};--gf-primary:{primary};--gf-ink:{ink};--gf-muted:{muted};--gf-grid:color-mix(in srgb,{ink} 18%,transparent);--gf-accent:{accent};--gf-highlight:{highlight};--gf-positive:{accent};--gf-negative:{negative};--gf-warning:#9A671B;--gf-font-body:var(--sd-font-serif);--gf-font-number:var(--sd-font-mono);--gf-safe-x:calc(var(--sd-canvas-w)*.054);--gf-baseline:calc(var(--sd-canvas-w)*.0027778);--sd-primary:var(--gf-primary);--sd-surface:var(--gf-surface);--sd-paper:var(--gf-paper);--sd-ink-100:var(--gf-ink);--sd-ink-60:color-mix(in srgb,var(--gf-ink) 72%,var(--gf-paper));--sd-accent:var(--gf-accent);--sd-secondary:var(--gf-negative);--sd-seq-100:#B68B36;--sd-seq-200:#A67B27;--sd-margin:var(--gf-safe-x);--sd-radius-card:2px}}
.sd-slide{{container-type:size;aspect-ratio:var(--slide-aspect)}}
.sd-table,.sd-num,.num{{font-variant-numeric:tabular-nums}}
.sd-list{{font-size:var(--sd-type-body);line-height:1.45}}
.sd-v2-figure{{width:100%;height:100%;margin:0;display:grid;grid-template-rows:minmax(0,1fr) auto;gap:.4em}}
.sd-v2-figure>svg{{min-height:0;width:100%;height:100%}}
.sd-v2-figure svg text{{paint-order:stroke;stroke:var(--gf-paper);stroke-width:3px;stroke-linejoin:round}}
.sd-v2-figure>figcaption{{font-size:var(--sd-type-micro);color:var(--gf-muted);line-height:1.35}}
.sd-slide[data-job="kpi"]{{--sd-type-kpi:calc(var(--sd-canvas-h)*.098);--sd-type-h3:calc(var(--sd-canvas-h)*.034)}}
.sd-slide[data-job="kpi"] .sd-content:has(.sd-kpi:nth-child(2):last-child){{--sd-type-kpi:calc(var(--sd-canvas-h)*.100);--sd-type-h3:calc(var(--sd-canvas-h)*.035)}}
.sd-slide[data-job="statement"] .sd-content{{display:flex;align-items:center}}
.sd-slide[data-job="statement"] .sd-content>.sd-block{{width:100%}}
.sd-slide[data-job="roster"] .sd-block[data-block="table"]{{height:96%}}
.sd-slide[data-job="roster"] .sd-table{{height:100%}}
.sd-data{{display:none!important}}
"""
    js = js_path.read_text(encoding="utf-8")
    font = "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-font-pack="TIANSIGHT" data-skin="{esc(theme)}" data-contract="{esc(deck.get('contract_version') or 'legacy')}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(deck_name)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link id="sd-font-link" href="{font}" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div id="sd-stage"><div id="deck">
{chr(10).join(sections)}
</div></div>
<script>
{js}
</script>
</body>
</html>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"render-deck: theme={theme} pages={total} → {out}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render longdoc2mdpages pages as TIANSIGHT HTML")
    parser.add_argument("--work", required=True)
    parser.add_argument("--theme", default="TIANSIGHT")
    parser.add_argument("--baslide", default=None, help="baslide01 root (default BASLIDE_ROOT or sibling path)")
    parser.add_argument("-o", "--out", default=None, help="Output HTML (default: work/slides/deck.html)")
    args = parser.parse_args(argv)
    work = Path(args.work).resolve()
    baslide = Path(args.baslide).resolve() if args.baslide else default_baslide()
    out = Path(args.out).resolve() if args.out else work / "slides" / "deck.html"
    return render(work, args.theme, baslide, out)


if __name__ == "__main__":
    raise SystemExit(main())
