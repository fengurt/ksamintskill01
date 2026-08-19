#!/usr/bin/env python3
"""Deterministic GF4p2slides deck-plan → self-contained Baslide HTML."""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path

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
            rows = "".join("<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>" for row in (block.get("rows") or []))
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
    return {
        **page,
        "role": template,
        "fill": page.get("visualization") or page.get("fill"),
        "source": page.get("source") or provenance.get("source") or "",
        "how_to_read": provenance.get("how_to_read") or page.get("how_to_read") or "",
        "takeaway": page.get("takeaway") or page.get("claim") or "",
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


def audit_copy_text(page: dict, work: Path, units: dict[str, str]) -> str:
    """Same fields extract-anchors uses, so hop2 sees every material token."""
    parts: list[str] = []
    for key in ("title", "source", "how_to_read", "takeaway", "notes"):
        val = page.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val)
    material = page.get("material") or {}
    if isinstance(material, dict):
        for b in material.get("bullets") or []:
            parts.append(str(b))
        table = material.get("table") or {}
        if isinstance(table, dict):
            parts.extend(str(c) for c in (table.get("columns") or []))
            for row in table.get("rows") or []:
                if isinstance(row, list):
                    parts.extend(str(c) for c in row)
                else:
                    parts.append(str(row))
            if table.get("sum"):
                parts.append(str(table["sum"]))
        for n in material.get("numbers") or []:
            parts.append(str(n))
        if material.get("quote"):
            parts.append(str(material["quote"]))
    parts.append(page_material_text(page, work, units))
    return "\n".join(p for p in parts if p)


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
            ("data-layout", page.get("layout") or ""),
            ("data-pack", page.get("pack") or "mid"),
            ("data-overflow-of", page.get("overflow_of") or ""),
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
        print(f"render-deck: viz skip {page.get('id')}: {exc}", file=sys.stderr)
    if fig and fig.svg:
        page["fill"] = fig.fill or page.get("fill")
        if job == "chart-table":
            section = re.sub(
                r"\[[^\]]*SVG viewBox 0 0 1170 500[^\]]*\]",
                lambda _: fig.svg,
                section,
                count=1,
            )
            if fig.table_html:
                section = re.sub(
                    r'<table class="sd-table">[\s\S]*?</table>',
                    lambda _: fig.table_html,
                    section,
                    count=1,
                )
            return section
        return replace_div_inner(section, "sd-content", fig.svg)
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
    body_html = structured_html(page) if page.get("_structured") else (md_to_html(material) if material else "")

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
        "STATEMENT_MAIN": title,
        "STATEMENT_SUPPORT": (page.get("takeaway") or "")[:240],
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

    # Pull period/scope from first units on cover
    blob = material[:800]
    pm = re.search(r"分析期间[：:]\s*(.+)", blob)
    if pm:
        values["PERIOD"] = pm.group(1).strip()[:40]
    sm = re.search(r"分析范围[：:]\s*(.+)", blob)
    if sm:
        values["SCOPE"] = sm.group(1).strip()[:40]

    section = fill_mustaches(section, values)
    section = set_section_attrs(section, page, job, index, total)
    section = replace_tag_inner(section, "sd-chip", esc(kicker or role))
    section = replace_tag_inner(section, "sd-h2", esc(title or role))
    section = replace_tag_inner(section, "sd-index", f"{index + 1} / {total}")
    if role in {"cover", "chapter"}:
        section = replace_tag_inner(section, "sd-hero", esc(title))
        # Keep anchors on cover/chapter: append a compact material block
        if material:
            extra = f'<div class="sd-content" style="position:absolute;left:var(--sd-margin);right:var(--sd-margin);bottom:8%;max-height:28%;overflow:auto;font-size:var(--sd-type-small);">{body_html}</div>'
            section = section.replace("</section>", extra + "</section>")
    else:
        if job in {"chart", "chart-table"}:
            section = fill_figure(section, page, material, job, body_html, title)
        else:
            inner = body_html or f"<p>{esc(title)}</p>"
            replaced = replace_div_inner(section, "sd-content", inner)
            if replaced == section:
                section = section.replace("</section>", f'<div class="sd-content">{inner}</div></section>')
            else:
                section = replaced

    # Drop external logo img (path would 404 in the self-contained file)
    section = re.sub(r"<img\b[^>]*src=\"[^\"]*logo/[^\"]*\"[^>]*>", "", section)
    section = MUSTACHE_RE.sub("", section)
    copy = audit_copy_text(page, work, units)
    if copy:
        section = section.replace(
            "</section>",
            f'<pre hidden class="sd-audit-copy">{esc(copy)}</pre></section>',
        )
    if page.get("_structured"):
        payload = json.dumps(page, ensure_ascii=False).replace("</", "<\\/")
        section = section.replace(
            "</section>",
            f'<script type="application/json" class="sd-data">{payload}</script></section>',
        )
    return section


def inline_logo_css(css: str, logo_path: Path) -> str:
    if not logo_path.is_file():
        return css.replace('url("logo/侍天.png")', "none")
    raw = logo_path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return css.replace('url("logo/侍天.png")', f'url("data:image/png;base64,{b64}")')


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

    css = inline_logo_css(css_path.read_text(encoding="utf-8"), baslide / "templates" / "TIANSIGHT" / "logo" / "侍天.png")
    surface, ink, accent, negative = THEME_TOKENS[theme]
    css += f"""
:root{{--gf-surface:{surface};--gf-ink:{ink};--gf-muted:color-mix(in srgb,{ink} 62%,transparent);--gf-grid:color-mix(in srgb,{ink} 18%,transparent);--gf-accent:{accent};--gf-positive:{accent};--gf-negative:{negative};--gf-warning:#9A671B;--gf-font-body:var(--sd-font-serif);--gf-font-number:var(--sd-font-mono);--sd-surface:var(--gf-surface);--sd-ink-100:var(--gf-ink);--sd-accent:var(--gf-accent);--sd-secondary:var(--gf-negative)}}
.sd-data{{display:none!important}}
"""
    js = js_path.read_text(encoding="utf-8")
    font = "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
    html = f"""<!DOCTYPE html>
<html lang="zh-CN" data-font-pack="TIANSIGHT" data-skin="{esc(theme)}">
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
