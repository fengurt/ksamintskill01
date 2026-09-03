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

from baslide_viz import assign_page_fill, default_baslide, figure_for_page

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

INSIGHT_LABEL_RE = re.compile(
    r"(?m)^\s*(现象|证据|商业含义|含义|行动|建议|结论|当前状态|可从数据推断的一条[^：:\n]{0,30})[：:]\s*(.*?)"
    r"(?=^\s*(?:现象|证据|商业含义|含义|行动|建议|结论|当前状态|可从数据推断的一条[^：:\n]{0,30})[：:]|\Z)",
    re.S,
)

OPPORTUNITY_RE = re.compile(r"^机会\s*\d+\s*[｜|]")
INTERNAL_COPY_RE = re.compile(r"[（(]\s*溢出链末页\s*[）)]")
KEY_RANKING_RE = re.compile(r"排名|TOP|贡献|收入|营收|增量|节约|机会|占比|份额", re.I)

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


def scrub_internal_copy(value):
    """Remove planner-only labels before audience-facing rendering."""
    if isinstance(value, dict):
        return {key: scrub_internal_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [scrub_internal_copy(item) for item in value]
    if isinstance(value, str):
        return INTERNAL_COPY_RE.sub("", value).strip()
    return value


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


def table_column_kind(header: str) -> tuple[str, float]:
    label = str(header).strip().lower()
    if label in {"#", "序号", "编号", "排名", "优先级"}:
        return "index", .38
    if any(token in label for token in ("时点", "日期", "期间", "时间", "月份", "年度")):
        return "date", 1.15
    if label in {"门店", "店", "组别", "类型", "类别"}:
        return "category", .65
    if any(token in label for token in ("可信", "置信", "状态", "等级", "风险")):
        return "status", .9
    if any(token in label for token in ("体量", "数量", "记录数", "价格", "金额", "收入", "占比", "渗透", "评分", "客单", "人均")):
        return "measure", 1.05
    if any(token in label for token in ("资产", "文件", "菜品", "品牌", "项目", "品类", "名称", "对象", "维度")):
        return "key", 1.35
    if any(token in label for token in ("用途", "说明", "定义", "依据", "字段", "内容", "结论", "建议", "范围", "职责", "问题", "动作", "口径", "方式", "引用")):
        return "detail", 1.65
    return "text", 1.0


def table_profile(columns: list, row_count: int = 0) -> tuple[str, list[str], str]:
    profiles = [table_column_kind(column) for column in columns]
    total = sum(weight for _, weight in profiles) or 1
    kinds = [kind for kind, _ in profiles]
    colgroup = "<colgroup>" + "".join(
        f'<col class="col-{kind}" style="width:{weight / total * 100:.2f}%">'
        for kind, weight in profiles
    ) + "</colgroup>"
    density = " sd-table--wide" if len(columns) >= 5 else ""
    if row_count >= 9:
        density += " sd-table--dense"
    return f"sd-table sd-table--{len(columns)}{density}", kinds, colgroup


def table_cell_class(kind: str, value: object) -> str:
    text = str(value).strip()
    classes = [f"col-{kind}"]
    if re.fullmatch(r"[+−-]?\d[\d,]*(?:\.\d+)?(?:\s*(?:%|％|元|家|个|次|份|张|行|列|天|月|年|人|店|分|秒|MB|KB|SKU))*", text, re.I):
        classes.append("num")
    return " ".join(classes)


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
            body_rows = block.get("rows") or []
            table_class, kinds, colgroup = table_profile(cols, len(body_rows))
            head = "".join(f'<th class="col-{kinds[index]}">{esc(col)}</th>' for index, col in enumerate(cols))
            rows = "".join("<tr>" + "".join(
                f'<td class="{table_cell_class(kinds[index] if index < len(kinds) else "text", cell)}">{esc(cell)}</td>'
                for index, cell in enumerate(row)
            ) + "</tr>" for row in body_rows)
            out.append(f'<div class="sd-block" data-block="table"><table class="{table_class}">{colgroup}<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
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


def metric_value(value: str) -> float | None:
    match = re.search(r"[+−-]?\s*\d[\d,]*(?:\.\d+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", "").replace("−", "-").replace(" ", ""))
    except ValueError:
        return None


def metric_unit(value: str) -> str:
    text = str(value)
    if "%" in text or "％" in text:
        return "%"
    for unit in ("万元", "亿元", "元", "万", "家", "店", "人", "次", "份", "桌", "天"):
        if unit in text:
            return unit
    return ""


def argument_kpi_html(page: dict) -> str:
    """Render long KPI labels as evidence, not disconnected dashboard tiles."""
    if page.get("_dish_example"):
        return (
            '<div class="sd-argument-kpi sd-dish-evidence">'
            '<article><div class="sd-evidence-kicker">餐具数据 · DATA GAP</div><strong>1 次</strong>'
            '<h3>当前记录不足以支持餐具选型</h3><p>新店仅有一条餐具破损记录，金额 12 元；应先统一破损品类与原因字段。</p></article>'
            '<article><div class="sd-evidence-kicker">摆盘范例 · WORKING EXAMPLE</div><strong>32 元 / 位</strong>'
            '<h3>新派宋嫂鱼羹已证明“位上菜”可成立</h3>'
            '<div class="sd-penetration"><span>新店 8.2%</span><i style="--w:100%"></i><span>老店 1.8%</span><i style="--w:22%"></i></div>'
            '<p>新店渗透约为老店 4.6 倍；老店同款累计售出 287.5 份。</p></article></div>'
        )
    if page.get("_argument_thesis"):
        return (
            '<div class="sd-argument-kpi is-curated">'
            '<div class="sd-argument-lead">'
            f'<div class="sd-argument-thesis">{esc(page["_argument_thesis"])}</div>'
            f'<div class="sd-argument-question">{esc(page["_argument_question"])}</div></div>'
            '<div class="sd-argument-curated">'
            '<figure class="sd-symbol-proof"><svg viewBox="0 0 360 260" role="img" aria-label="八家高价高分高流量餐厅全部拥有名词化产品符号">'
            '<circle cx="180" cy="128" r="62" class="ring"/><text x="180" y="120" class="center">100%</text><text x="180" y="148" class="center-sub">8 / 8</text>'
            '<g class="nodes"><circle cx="180" cy="28" r="14"/><circle cx="251" cy="57" r="14"/><circle cx="280" cy="128" r="14"/><circle cx="251" cy="199" r="14"/>'
            '<circle cx="180" cy="228" r="14"/><circle cx="109" cy="199" r="14"/><circle cx="80" cy="128" r="14"/><circle cx="109" cy="57" r="14"/></g></svg>'
            '<figcaption><b>高价·高分·高流量餐厅</b><br>全部拥有名词化产品符号</figcaption>'
            '<div class="sd-market-gap"><strong>1 家</strong><span>佛山淮扬门店供给</span></div></figure>'
            '<figure class="sd-price-ladder"><div class="sd-ladder-title">128 元目标价，需要品牌认知跨越两道门槛</div>'
            '<svg viewBox="0 0 820 330" role="img" aria-label="佛山淮扬菜人均31元，江浙品类价格天花板83元，本案目标人均128元">'
            '<rect x="66" y="104" width="450" height="72" class="market-band"/><text x="291" y="145" class="band-label">现有品类认知区间</text>'
            '<line x1="66" y1="205" x2="754" y2="205" class="axis"/><text x="66" y="232" class="tick">0</text><text x="754" y="232" text-anchor="end" class="tick">140 元</text>'
            '<g class="marker base"><line x1="218" y1="86" x2="218" y2="220"/><circle cx="218" cy="205" r="9"/><text x="218" y="65" text-anchor="middle" class="value">31 元</text><text x="218" y="258" text-anchor="middle" class="label">佛山淮扬菜人均</text></g>'
            '<g class="marker ceiling"><line x1="474" y1="86" x2="474" y2="220"/><circle cx="474" cy="205" r="9"/><text x="474" y="65" text-anchor="middle" class="value">83 元</text><text x="474" y="258" text-anchor="middle" class="label">江浙品类价格天花板</text></g>'
            '<g class="marker target"><line x1="695" y1="70" x2="695" y2="220"/><circle cx="695" cy="205" r="11"/><text x="695" y="48" text-anchor="middle" class="value">128 元</text><text x="695" y="258" text-anchor="middle" class="label">本案目标人均</text></g>'
            '<path d="M218 292 V278 H695 V292" class="bracket"/><text x="456" y="318" text-anchor="middle" class="ratio">目标为淮扬均价 4.1× · 比品类天花板高 54%</text>'
            '</svg></figure></div>'
            f'<p class="sd-argument-support">{esc(page["_argument_support"])}</p></div>'
        )
    cards = page.get("_argument_cards") or [
        {
            "value": f'{block.get("value") or ""}{block.get("unit") or ""}',
            "label": block.get("label") or "",
            "note": block.get("note") or block.get("delta") or "",
        }
        for block in (page.get("content") or {}).get("blocks") or []
        if block.get("kind") == "kpi-card"
    ]
    metrics = [(metric_value(card.get("value") or ""), metric_unit(card.get("value") or "")) for card in cards]
    groups: dict[str, list[float]] = {}
    for value, unit in metrics:
        if value is not None and value >= 0 and unit:
            groups.setdefault(unit, []).append(value)
    items = []
    for card, (value, unit) in zip(cards, metrics):
        note = f'<span class="sd-argument-note">{esc(card.get("note") or "")}</span>' if card.get("note") else ""
        meter = ""
        peers = groups.get(unit) or []
        if value is not None and value >= 0 and (unit == "%" or len(peers) >= 2):
            scale = max(100.0, max(peers)) if unit == "%" else max(peers)
            width = 0 if value == 0 else max(2.0, min(100.0, value / scale * 100)) if scale else 0
            scale_label = "占比基准 100%" if unit == "%" else f"同单位最大值 {max(peers):g}{unit}"
            meter = f'<div class="sd-argument-meter"><i style="--w:{width:.1f}%"></i></div><small class="sd-argument-scale">{esc(scale_label)}</small>'
        items.append(
            '<article class="sd-argument-card">'
            f'<strong class="sd-argument-value">{esc(card.get("value") or "")}</strong>'
            f'<span class="sd-argument-label">{esc(card.get("label") or "")}</span>{meter}{note}</article>'
        )
    thesis = page.get("_argument_thesis") or ""
    question = page.get("_argument_question") or ""
    support = page.get("_argument_support") or ""
    lead = (
        '<div class="sd-argument-lead">'
        f'<div class="sd-argument-thesis">{esc(thesis)}</div>'
        f'<div class="sd-argument-question">{esc(question)}</div></div>'
        if thesis or question else ""
    )
    foot = f'<p class="sd-argument-support">{esc(support)}</p>' if support else ""
    return f'<div class="sd-argument-kpi is-generic n-{len(cards)}">{lead}<div class="sd-argument-grid">{"".join(items)}</div>{foot}</div>'


def editorial_points(page: dict, material: str) -> list[str]:
    """Extract a small, faithful set of visible ideas for statement-page composition."""
    points: list[str] = []
    for block in (page.get("content") or {}).get("blocks") or []:
        kind = block.get("kind")
        if kind == "bullets":
            for item in (block.get("items") or []):
                text = str(item)
                points.extend(re.split(r"(?<=[。！？!?])\s*", text) if len(text) > 100 else [text])
        elif kind in {"claim", "lede", "quote", "callout", "step", "profile"}:
            text = str(block.get("text") or block.get("title") or "")
            points.extend(re.split(r"(?<=[。！？!?；;])\s*", text) if len(text) > 100 else [text])
    if not points:
        prose = re.sub(r"(?m)^\s*(?:#+\s*|role:.*|units:.*|u-\d+.*|\|.*)$", "", material or "")
        points.extend(re.split(r"(?<=[。！？!?；;])\s*|\n{2,}", prose))
    cleaned: list[str] = []
    seen: set[str] = set()
    for point in points:
        clean = re.sub(r"<cite\b[^>]*>(.*?)</cite>", r"\1", point, flags=re.I | re.S)
        clean = re.sub(r"<[^>]+>", "", clean)
        clean = re.sub(r"\s+", " ", re.sub(r"^[-*+\d.)、\s]+", "", clean)).replace("⭐", "").strip(" ｜|")
        if not clean or clean in seen or len(clean) < 4:
            continue
        seen.add(clean)
        cleaned.append(clean)
    priority = [p for p in cleaned if re.search(r"^(?:它先|然后|最后)|⭐|→|不是.+而是|必须|结论", p)]
    selected = priority[:4]
    selected.extend(p for p in cleaned if p not in selected)
    def clip(point: str, limit: int = 52) -> str:
        if len(point) <= limit:
            return point
        cut = max(point.rfind(mark, 18, limit) for mark in "，、；：。")
        return point[: cut + 1 if cut >= 18 else limit].rstrip("，、；： ") + ("。" if cut >= 18 else "")
    return [clip(p) for p in selected[:5]]


def editorial_figure(page: dict, material: str) -> str:
    points = editorial_points(page, material)
    if not points:
        return ""
    takeaway = str(page.get("takeaway") or "").strip()
    if re.sub(r"\W+", "", takeaway) == re.sub(r"\W+", "", str(page.get("title") or "")):
        takeaway = ""
    hero = takeaway or next((point for point in reversed(points) if re.search(r"→|不是.+而是|必须|结论|身份|隐喻", point)), points[0])
    points = [point for point in points if point != hero]

    def marked(text: str) -> str:
        safe = esc(text)
        return re.sub(
            r"(?<![\w>])(\d[\d,.，]*(?:\.\d+)?(?:%|％|元|家|店|桌|人|天|月|年|分)?)",
            r'<span style="font-family:var(--sd-font-mono);color:var(--sd-secondary);font-weight:600;">\1</span>',
            safe,
        )

    cards = "".join(
        '<div style="flex:1;min-width:0;border:2px solid var(--sd-ink-14);background:var(--sd-paper);'
        'border-radius:var(--sd-radius-card);padding:.7em .85em;display:flex;flex-direction:column;justify-content:center;gap:.4em;">'
        f'<div style="font-family:var(--sd-font-mono);font-size:var(--sd-type-small);color:var(--sd-ink-60);letter-spacing:.08em;">{index:02d} · 依据</div>'
        f'<div class="sd-lede">{marked(point)}</div></div>'
        for index, point in enumerate(points[:4], 1)
    )
    return (
        '<div style="width:100%;height:100%;display:flex;flex-direction:column;gap:24px;">'
        '<div style="flex:1.4 1 0;min-height:0;border:2px solid var(--sd-ink-14);background:var(--sd-paper);'
        'border-radius:var(--sd-radius-card);padding:.7em .9em;display:flex;gap:.8em;align-items:center;">'
        '<div class="sd-rule" style="width:6px;height:40%;flex:none;margin:0;"></div>'
        f'<div class="sd-quote">{marked(hero[:120])}</div></div>'
        + (f'<div style="flex:1 1 0;min-height:0;display:flex;gap:24px;align-items:stretch;">{cards}</div>' if cards else "")
        + '</div>'
    )


def insight_sections(material: str) -> list[tuple[str, str]]:
    """Return the authored evidence ladder used by TIANSIGHT insight pages."""
    clean = re.sub(r"(?m)^\s*(?:u-\d+|---)\s*$", "", material or "")
    sections: list[tuple[str, str]] = []
    for match in INSIGHT_LABEL_RE.finditer(clean):
        raw = re.sub(r"(?m)^\s*[-*+]\s*", "；", match.group(2)).strip("； \n")
        label, text = match.group(1), re.sub(r"\s+", " ", raw).strip()
        if label.startswith("可从数据推断"):
            label = "推断"
        if text:
            sections.append((label, text))
    return sections


def data_quality_insight_html() -> str:
    """Source-backed paired view for Chaofa insight 12."""
    rows = [
        ("万象滨海购物村", 35.4, 178.7),
        ("番禺永旺", 35.2, 151.3),
        ("陈家祠", 35.2, 157.7),
        ("富力海珠城", 35.1, 156.5),
        ("乐峰广场", 33.0, 161.0),
        ("花都融创茂", 32.6, 169.0),
        ("圣地大厦", 31.4, 175.9),
        ("东方新世界", 29.5, 170.0),
        ("千灯湖环宇城", 26.7, 178.6),
        ("万象食家", 26.3, 179.5),
    ]
    highlight = {"万象滨海购物村": "var(--sd-secondary)", "番禺永旺": "var(--sd-accent)", "万象食家": "var(--sd-ink-100)"}
    x = lambda value: 54 + (value - 25) / 12 * 410
    y = lambda value: 205 - (value - 145) / 40 * 155
    grid = "".join(
        f'<line x1="54" y1="{y(value):.1f}" x2="470" y2="{y(value):.1f}" stroke="var(--sd-ink-14)"/>'
        f'<text x="46" y="{y(value) + 5:.1f}" text-anchor="end" fill="var(--sd-ink-60)" font-size="18">{value}</text>'
        for value in (150, 160, 170, 180)
    ) + "".join(
        f'<line x1="{x(value):.1f}" y1="45" x2="{x(value):.1f}" y2="205" stroke="var(--sd-ink-14)"/>'
        f'<text x="{x(value):.1f}" y="228" text-anchor="middle" fill="var(--sd-ink-60)" font-size="18">{value}%</text>'
        for value in (26, 30, 34)
    )
    dots = []
    for store, missing, sauce in rows:
        color = highlight.get(store, "var(--sd-ink-38)")
        radius = 7 if store in highlight else 5
        dots.append(f'<circle cx="{x(missing):.1f}" cy="{y(sauce):.1f}" r="{radius}" fill="{color}" stroke="var(--sd-paper)" stroke-width="2"/>')
        if store in highlight:
            label = {"万象滨海购物村": "万象滨海", "番禺永旺": "番禺永旺", "万象食家": "万象食家"}[store]
            dy = -11 if store != "万象食家" else 17
            dots.append(f'<text x="{x(missing):.1f}" y="{y(sauce) + dy:.1f}" text-anchor="middle" fill="{color}" font-size="18" font-weight="600">{label}</text>')

    def raw_table(items: list[tuple[str, float, float]]) -> str:
        table_rows = "".join(
            '<tr style="background:' + ('var(--sd-ink-06)' if store in highlight else 'transparent') + ';">'
            f'<td style="padding:.2rem .4rem;color:var(--sd-ink-100);">{esc(store)}</td>'
            f'<td style="padding:.2rem .4rem;text-align:right;font-family:var(--sd-font-mono);color:var(--sd-ink-100);">{missing:.1f}%</td>'
            f'<td style="padding:.2rem .4rem;text-align:right;font-family:var(--sd-font-mono);color:var(--sd-ink-100);">{sauce:.1f}</td></tr>'
            for store, missing, sauce in items
        )
        return (
            '<table style="width:100%;border-collapse:collapse;font-size:1.875rem;line-height:1.16;">'
            '<thead><tr style="border-bottom:2px solid var(--sd-ink-14);color:var(--sd-ink-60);">'
            '<th style="padding:.2rem .4rem;text-align:left;font-weight:500;">门店</th>'
            '<th style="padding:.2rem .4rem;text-align:right;font-weight:500;">人数缺失</th>'
            '<th style="padding:.2rem .4rem;text-align:right;font-weight:500;">酱料/百单</th></tr></thead>'
            f'<tbody>{table_rows}</tbody></table>'
        )
    scenarios = "".join(
        '<div style="display:grid;grid-template-columns:6.2rem 1fr 9.5rem;align-items:center;gap:.5rem;">'
        f'<span style="color:var(--sd-ink-60);">{label}</span><span style="height:.48rem;background:var(--sd-ink-08);border-radius:99px;overflow:hidden;">'
        f'<i style="display:block;width:{value / 168.73 * 100:.1f}%;height:100%;background:{color};"></i></span>'
        f'<span style="text-align:right;font-family:var(--sd-font-mono);color:var(--sd-ink-100);">{value:.2f} 万/年</span></div>'
        for label, value, color in (("保守 20%", 67.49, "var(--sd-ink-100)"), ("中性 35%", 118.11, "var(--sd-secondary)"), ("激进 50%", 168.73, "var(--sd-accent)"))
    )
    return (
        '<div class="sd-dq" style="width:100%;height:100%;display:grid;grid-template-rows:auto minmax(0,1fr) auto auto;gap:14px;color:var(--sd-ink-100);">'
        '<div style="grid-column:1/-1;display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">'
        '<div style="border:2px solid var(--sd-ink-14);background:var(--sd-paper);padding:.55rem .7rem;border-radius:var(--sd-radius-card);"><div style="font-size:1.875rem;color:var(--sd-ink-60);">人数字段缺失率</div><div style="font:600 2.75rem/1 var(--sd-font-mono);margin-top:.22rem;">32.1%</div><div style="font-size:1.875rem;color:var(--sd-ink-60);margin-top:.22rem;">56,710 / 176,886 张堂食单</div></div>'
        '<div style="border:2px solid var(--sd-ink-14);background:var(--sd-paper);padding:.55rem .7rem;border-radius:var(--sd-radius-card);"><div style="font-size:1.875rem;color:var(--sd-ink-60);">保守情景年化漏收</div><div style="font:600 2.75rem/1 var(--sd-font-mono);margin-top:.22rem;color:var(--sd-secondary);">67.49 万元</div><div style="font-size:1.875rem;color:var(--sd-ink-60);margin-top:.22rem;">20% 缺失单 × 2.5 人 × 6 元</div></div>'
        '<div style="border:2px solid var(--sd-ink-14);background:var(--sd-paper);padding:.55rem .7rem;border-radius:var(--sd-radius-card);"><div style="font-size:1.875rem;color:var(--sd-ink-60);">决策影响</div><div style="font-size:1.875rem;line-height:1.25;margin-top:.22rem;">人均消费、桌型匹配及人效指标暂不具备决策可靠性</div><div style="font-size:1.875rem;color:var(--sd-ink-60);margin-top:.22rem;">完成现场核验前，不应作为经营决策依据</div></div></div>'
        '<div style="display:grid;grid-template-columns:1.45fr 1fr;gap:14px;min-height:0;">'
        '<div style="border:2px solid var(--sd-ink-14);background:var(--sd-paper);padding:.55rem .7rem;border-radius:var(--sd-radius-card);display:flex;flex-direction:column;min-height:0;">'
        '<div style="font-size:1.875rem;color:var(--sd-ink-60);">门店级配对检验 · 横轴：人数字段缺失率；纵轴：酱料费件数/100 张堂食单</div>'
        f'<svg viewBox="0 0 500 240" style="width:100%;flex:1;min-height:0;margin-top:.15rem;" role="img" aria-label="十店人数缺失率与酱料费附加率散点图">{grid}{"".join(dots)}</svg></div>'
        '<div style="border:2px solid var(--sd-ink-14);background:var(--sd-paper);padding:.55rem .7rem;border-radius:var(--sd-radius-card);display:flex;flex-direction:column;gap:.5rem;min-height:0;">'
        '<div style="font-size:2rem;font-weight:600;">证据解释</div>'
        '<div style="display:grid;grid-template-rows:repeat(3,1fr);gap:.45rem;font-size:1.875rem;line-height:1.25;flex:1;min-height:0;">'
        '<div style="padding:.45rem .55rem;background:var(--sd-ink-04);border-left:5px solid var(--sd-secondary);"><span style="color:var(--sd-secondary);">●</span> 万象滨海与万象食家：缺失率相差 9.1 个百分点，酱料费附加率仅相差 0.8 件/百单，表明两指标不存在稳定的单变量关系。</div>'
        '<div style="padding:.45rem .55rem;background:var(--sd-ink-04);border-left:5px solid var(--sd-accent);"><span style="color:var(--sd-accent);">●</span> 番禺永旺与万象滨海：缺失率接近，附加率相差 27.4 件/百单，提示收费执行差异可能是主要解释变量。</div>'
        '<div style="padding:.45rem .55rem;background:var(--sd-ink-04);border-left:5px solid var(--sd-ink-60);">管理结论：现有证据只能确认联合风险，尚不能识别各因素的因果贡献。</div></div>'
        '<div style="border-top:1px solid var(--sd-ink-14);padding-top:.45rem;display:grid;gap:.34rem;font-size:1.875rem;">'
        f'{scenarios}</div></div></div>'
        '<div style="border:2px solid var(--sd-ink-14);background:var(--sd-paper);padding:.48rem .65rem .55rem;border-radius:var(--sd-radius-card);">'
        '<div style="font-size:2rem;font-weight:600;margin-bottom:.28rem;">门店原始值（10 店）</div>'
        f'<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;">{raw_table(rows[:5])}{raw_table(rows[5:])}</div></div>'
        '<div style="border-top:2px solid var(--sd-ink-14);padding-top:.38rem;display:grid;grid-template-columns:1.2fr 1.8fr;gap:1rem;font-size:1.875rem;line-height:1.22;color:var(--sd-ink-60);">'
        '<span>口径：堂食桌台；6 元/位；按 2.5 人/桌。来源：§4.3 / §11.5 / §15.4。</span>'
        '<span style="color:var(--sd-ink-100);">验证设计：选择万象食家、番禺永旺、万象滨海购物村，各抽 20 桌，逐单比对人工人数、POS 人数及酱料费实收，用于分解漏录、特殊场景与收费执行三类成因。</span></div></div>'
    )


def insight_figure(page: dict, material: str) -> str:
    """TIANSIGHT statement: one conclusion well plus 2–4 peer evidence cards."""
    sections = insight_sections(material)
    if len(sections) < 2:
        return ""

    def clip(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        cut = max(text.rfind(mark, 28, limit) for mark in "，、；：。")
        return text[: cut + 1 if cut >= 28 else limit].rstrip("，、；： ") + ("。" if cut >= 28 else "")

    hero_index = next((i for i, (label, _) in enumerate(sections) if label in {"商业含义", "含义", "行动", "建议", "结论", "推断"}), 0)
    hero_label, hero = sections[hero_index]
    supports = [item for i, item in enumerate(sections) if i != hero_index][:4]
    if hero_label == "推断":
        sentences = [part.strip() for part in re.split(r"(?<=[。！？])\s*", hero) if part.strip()]
        chosen = next((part for part in sentences if re.search(r"做得比|成功范例|必须|应该|建议|核心", part)), sentences[0])
        hero = chosen
        supports.extend(("案例" if "范例" in part else "依据", part) for part in sentences if part != chosen)
        supports = supports[:4]
    number_re = re.compile(
        r"[-+−]?\d[\d,.]*(?:\.\d+)?\s*(?:%|％|pp|[万亿]?元|家|店|天|周|月|年|小时|分钟|笔|单|份|人|桌|公里|米|倍)",
        re.I,
    )
    def marked(text: str, limit: int) -> str:
        safe = esc(clip(text, limit))
        return number_re.sub(
            lambda match: f'<span style="font-family:var(--sd-font-mono);color:var(--sd-secondary);font-weight:600;">{match.group(0)}</span>',
            safe,
        )
    cards = []
    for index, (label, text) in enumerate(supports, 1):
        number = next(iter(number_re.findall(text)), "")
        percent = re.search(r"([-+−]?\d+(?:\.\d+)?)\s*[%％]", number)
        meter = ""
        if percent:
            width = max(2.0, min(100.0, abs(float(percent.group(1).replace("−", "-")))))
            meter = (
                '<div style="height:.42rem;border-radius:99px;background:var(--sd-ink-08);overflow:hidden;margin:.12rem 0 .08rem;">'
                f'<span style="display:block;width:{width:g}%;height:100%;background:var(--sd-secondary);"></span></div>'
            )
        cards.append(
            '<div style="min-width:0;border:2px solid var(--sd-ink-14);background:var(--sd-paper);color:var(--sd-ink-100);'
            'border-radius:var(--sd-radius-card);padding:.62em .72em;display:flex;flex-direction:column;gap:.28em;">'
            f'<div style="font-family:var(--sd-font-mono);font-size:.9rem;color:var(--sd-accent);letter-spacing:.08em;">{index:02d} · {esc(label)}</div>'
            + (f'<div style="font-family:var(--sd-font-mono);font-size:calc(var(--sd-canvas-h)*.058);line-height:1;color:var(--sd-ink-100);font-weight:600;">{esc(number)}</div>' if number else "")
            + meter
            + f'<div class="sd-lede" style="margin-top:auto;color:var(--sd-ink-100);font-weight:400;">{esc(clip(text, 118 if len(supports) <= 3 else 86))}</div></div>'
        )
    columns = 2 if len(cards) == 4 else max(1, len(cards))
    return (
        '<div style="width:100%;height:100%;display:flex;flex-direction:column;gap:24px;">'
        '<div style="flex:.9 1 0;min-height:0;border:2px solid var(--sd-ink-14);background:var(--sd-paper);color:var(--sd-ink-100);'
        'border-radius:var(--sd-radius-card);padding:.72em .9em;display:flex;gap:.8em;align-items:center;">'
        '<div class="sd-rule" style="width:6px;height:44%;flex:none;margin:0;"></div>'
        f'<div class="sd-quote" style="color:var(--sd-ink-100);font-weight:500;">{marked(hero, 112)}</div></div>'
        f'<div style="flex:1.2 1 0;min-height:0;display:grid;grid-template-columns:repeat({columns},minmax(0,1fr));gap:18px;align-items:stretch;">{"".join(cards)}</div></div>'
    )


def opportunity_visual_page(page: dict, material: str) -> bool:
    """Normalize opportunity pages into comparable change or contribution figures."""
    if not OPPORTUNITY_RE.match(str(page.get("title") or "")):
        return False
    content = dict(page.get("content") or {})
    columns, rows = content.get("columns") or [], content.get("rows") or []
    role = page.get("role") or "statement"

    def use_figure(headers: list[str], data: list[list[str]], fill: str, preview: list[str], note: str) -> bool:
        if not data:
            return False
        page["content"] = {**content, "columns": headers, "rows": data}
        page["_figure_material"] = "| " + " | ".join(headers) + " |\n| " + " | ".join("---" for _ in headers) + " |\n" + "\n".join("| " + " | ".join(map(str, row)) + " |" for row in data)
        page["_preview_columns"] = preview
        page["fill"] = page["recipe"] = fill
        page["how_to_read"] = note
        page["_render_job"] = "chart-table"
        return True

    if role == "statement":
        page["_render_job"] = "statement"
        return True

    # KPI extraction had split baseline→target phrases into unrelated cards.
    if role == "kpi":
        if "君类倾向指数" in material:
            bullets = [re.sub(r"^[-*+]\s*", "", line).strip() for line in material.splitlines() if re.match(r"^\s*[-*+]\s+", line)]
            conclusion = re.search(r"用 4\.5 节的模拟餐单公式验证[：:]\s*(.+)", material)
            page["_figure_material"] = (("结论：" + conclusion.group(1).strip()) if conclusion else "") + "\n\n" + "\n\n".join("证据：" + item for item in bullets[:4])
            page["_render_job"] = "statement"
            page["_insight"] = True
            return True
        if "会员订单占" in material:
            facts = []
            for source_label, target_label in (("现状", "现象"), ("假设", "证据"), ("理论增量", "证据")):
                match = re.search(rf"{source_label}[：:]\s*(.+?。)", material)
                if match:
                    facts.append(f"{target_label}：{match.group(1)}")
            overlap = re.search(r"但这部分(.+?。)", material)
            if overlap:
                facts.append(f"商业含义：这部分{overlap.group(1)}")
            page["_figure_material"] = "\n\n".join(facts)
            page["_render_job"] = "statement"
            page["_insight"] = True
            return True
        transitions = []
        for chunk in re.split(r"[；;\n]", material):
            pair = re.search(r"(\d+(?:\.\d+)?)%\s*→\s*(\d+(?:\.\d+)?)%", chunk)
            if not pair:
                continue
            label = next((name for name in ("老店", "新店") if name in chunk), "会员订单占比" if "会员" in chunk else "目标指标")
            transitions.append([label, pair.group(1) + "%", pair.group(2) + "%"])
        if not transitions:
            current = re.search(r"会员订单占\s*(\d+(?:\.\d+)?)%", material)
            target = re.search(r"会员订单占比提至\s*(\d+(?:\.\d+)?)%", material)
            if current and target:
                transitions = [["会员订单占比", current.group(1) + "%", target.group(1) + "%"]]
        if len(transitions) == 2 and {row[0] for row in transitions} == {"老店", "新店"}:
            tickets = {name: value for name, value in re.findall(r"(老店|新店)[^。；]{0,100}?客单\s*([\d,.]+)\s*元", material)}
            if len(tickets) == 2:
                transitions = [row + [tickets[row[0]] + " 元"] for row in transitions]
                if use_figure(["门店", "当前使用率", "目标使用率", "午市包间客单"], transitions, "slope", ["门店", "当前使用率", "目标使用率", "午市包间客单"], "左侧是当前，右侧是目标；客单仅作测算输入，不编码在线段上"):
                    return True
        if use_figure(["指标", "当前", "目标"], transitions[:4], "slope", ["指标", "当前", "目标"], "左侧是当前，右侧是目标；只比较同一百分比口径"):
            return True
        page["_render_job"] = "statement"
        return True

    if not (columns and rows):
        return True

    # Scenario pages compare the same store under two explicit target levels.
    if columns[:4] == ["目标", "老店年化增量", "新店年化增量", "合计"] and len(rows) >= 2:
        data = [["老店", rows[0][1] + " 元", rows[1][1] + " 元"], ["新店", rows[0][2] + " 元", rows[1][2] + " 元"], ["两店合计", rows[0][3], rows[1][3]]]
        return use_figure(["门店", rows[0][0], rows[1][0]], data, "slope", ["门店", rows[0][0], rows[1][0]], "左侧是保守目标，右侧是进阶目标；金额均为年化增量")

    # Coverage pages are primarily a baseline→target question, not an amount ranking.
    current_col = next((i for i, col in enumerate(columns) if "当前" in str(col)), None)
    target_col = next((i for i, col in enumerate(columns) if str(col) == "目标"), None)
    if current_col is not None and target_col is not None:
        data = [[" · ".join(str(cell) for cell in row[:current_col]), row[current_col], row[target_col]] for row in rows if not any("合计" in str(cell) for cell in row)]
        result = use_figure(["对象", columns[current_col], columns[target_col]], data, "slope", ["对象", columns[current_col], columns[target_col]], "左侧是当前覆盖率，右侧是目标覆盖率")
        if result:
            preview_rows = [row + [source[-1]] for row, source in zip(data, [row for row in rows if not any("合计" in str(cell) for cell in row)])]
            preview_columns = ["对象", columns[current_col], columns[target_col], columns[-1]]
            page["content"] = {**content, "columns": preview_columns, "rows": preview_rows}
            page["_preview_columns"] = preview_columns
        return result

    # Contribution pages rank by the annualized result; all-positive diverging bars obscured this question.
    annual_col = next((i for i, col in enumerate(columns) if "年化" in str(col)), None)
    if annual_col is not None:
        data = [[row[0], row[annual_col]] for row in rows if len(row) > annual_col and not any("合计" in str(cell) for cell in row)]
        input_col = next((i for i, col in enumerate(columns) if re.search(r"客单|转化单数|收入|假设|晚退菜额", str(col))), None)
        preview = [columns[0]] + ([columns[input_col]] if input_col not in {None, 0, annual_col} else []) + [columns[annual_col]]
        result = use_figure([columns[0], columns[annual_col]], data, "pareto", preview, "柱长是各项年化贡献；右侧保留测算输入与精确值")
        if result:
            page["content"] = content
            page["_preview_columns"] = preview
            if any("增量间数/天" in str(col) for col in columns):
                page["_display_title"] = "每店每天多做 1 间包间午市，年化增收 946,708 元"
        return result

    # The conversion opportunity is a genuine like-for-like ticket comparison.
    if "团购客单" in columns and "非团购客单" in columns:
        page["fill"] = page["recipe"] = "slope"
        page["_preview_columns"] = ["门店", "团购客单", "非团购客单"]
        page["how_to_read"] = "左侧是团购客单，右侧是非团购客单；线段显示转化空间"
        page["_render_job"] = "chart-table"
    return True


def chaofa_insight_visual_page(page: dict, work: Path) -> bool:
    """Use comparable evidence charts for Chaofa's insight chapter."""
    if work.name != "chaofa":
        return False
    specs = {
        "p-0027": ("需求增长 +18%，晚市产能已成为约束", ["口径", "5 月", "7 月"], [["日均营收下界", "47.5 万", "56.6 万"], ["日均营收上界", "50.0 万", "59.0 万"]], "slope", "两条线分别保留基线区间上下界；只比较同一营收口径"),
        "p-0028": ("周末溢价 46%–101%：工作日空档差异巨大", ["门店/范围", "周末溢价"], [["万象滨海购物村", "+101%"], ["全网", "+65%"], ["陈家祠", "+46%"]], "diverging-bar", "条长是周末相对工作日的日均营收溢价"),
        "p-0029": ("31 个 SKU 贡献 80%；190 个长尾仅 1.34%", ["SKU 组", "SKU 数", "营收贡献"], [["头部 SKU", "31", "80.0%"], ["长尾 SKU", "190", "1.34%"], ["瘦狗 SKU", "71", "0.71%"]], "diverging-bar", "柱是营收贡献；分组有包含关系，不做累计相加"),
        "p-0031": ("套餐裸单 21,411 张：客单被锁在 177.5 / 321 元", ["套餐", "裸单数", "堂食占比", "套餐价"], [["鲜牛丸 2 人餐", "12,455", "7.04%", "177.5 元"], ["潮发 4 人餐", "8,507", "4.81%", "321 元"], ["两款合计", "21,411", "12.1%", "—"]], "pareto", "柱是未加点裸单数；右表保留价格与堂食占比"),
        "p-0032": ("酒水占比 2.24%，仍低于行业健康区间", ["基准", "营收占比"], [["潮发酒水饮品", "2.24%"], ["行业健康下限", "8.0%"], ["行业健康上限", "15.0%"]], "diverging-bar", "同一营收占比口径；健康区间为 8%–15%"),
        "p-0033": ("外卖占 16.2% 单量，却只贡献 3.9% 营收", ["指标", "占比/相对值"], [["平台外卖单量", "16.2%"], ["平台外卖营收", "3.9%"], ["每单价值 / 堂食", "20.3%"]], "diverging-bar", "三项均为百分比；每单价值以堂食客单=100%"),
        "p-0034": ("圣地大厦台效 822 元，仅为标杆店的 54%", ["门店/基准", "台效（元/台/天）"], [["万象食家标杆", "1,531"], ["全网中位", "1,088"], ["圣地大厦", "822"]], "diverging-bar", "同一台效口径；圣地大厦达到中位数对应约 757 万元年化空间"),
        "p-0035": ("万象食家台效第一，但晚市已无剩余产能", ["经营信号", "占比"], [["晚市坐满天数", "97.8%"], ["≤180 元低价单", "18.8%"], ["外卖单量", "4.7%"]], "diverging-bar", "同为占比但含义不同：高满台是约束，低价单与外卖低是结构优势"),
        "p-0036": ("新会员 829 → 243，会员盘与大盘背向", ["指标", "5 月", "7 月", "5–7 月变化"], [["新会员", "829", "243", "-70.7%"], ["会员流水（万元）", "77.1", "63.4", "-17.8%"], ["全网营收", "—", "—", "+6.2%"]], "diverging-bar", "左侧为下降、右侧为增长；会员指标与全网营收背向"),
        "p-0037": ("90 分钟+桌次占 22.4% 台时，仅贡献 15.3% 营收", ["90 分钟+桌次", "占比"], [["台时占比", "22.4%"], ["营收占比", "15.3%"], ["单量占比", "12.4%"]], "diverging-bar", "同一桌次群体的三种占比；台时明显高于营收贡献"),
        "p-0039": ("午晚比 0.44，低于健康下限 0.55", ["口径", "午晚比"], [["潮发现状", "0.44"], ["行业健康下限", "0.55"], ["行业健康上限", "0.70"]], "diverging-bar", "午市营收÷晚市营收；健康区间为 0.55–0.70"),
    }
    spec = specs.get(str(page.get("id") or ""))
    if not spec:
        return False
    title, columns, rows, fill, note = spec
    page["content"] = {**(page.get("content") or {}), "columns": columns, "rows": rows}
    figure_columns, figure_rows = columns, rows
    if page.get("id") == "p-0029":
        figure_columns = [columns[0], columns[2]]
        figure_rows = [[row[0], row[2]] for row in rows]
    elif page.get("id") == "p-0031":
        figure_columns = columns[:2]
        figure_rows = [row[:2] for row in rows[:2]]
    elif page.get("id") == "p-0036":
        figure_columns = [columns[0], columns[3]]
        figure_rows = [[row[0], row[3]] for row in rows]
    page["_figure_material"] = "| " + " | ".join(figure_columns) + " |\n| " + " | ".join("---" for _ in figure_columns) + " |\n" + "\n".join("| " + " | ".join(row) + " |" for row in figure_rows)
    page["_preview_columns"] = columns
    page["_display_title"] = title
    page["fill"] = page["recipe"] = fill
    page["how_to_read"] = note
    page["_render_job"] = "chart-table"
    return True


def prepare_visual_page(page: dict, work: Path, units: dict[str, str], baslide: Path) -> dict:
    """Promote real numeric evidence to a figure without changing the source page plan."""
    page = dict(page)
    role = page.get("role") or "statement"
    material = page_material_text(page, work, units)
    content = page.get("content") or {}
    columns, rows = content.get("columns") or [], content.get("rows") or []
    if work.name == "chaofa" and page.get("id") == "p-0030" and "数据录入质量" in str(page.get("title") or ""):
        page["_render_job"] = "statement"
        page["_data_quality"] = True
        return page
    if chaofa_insight_visual_page(page, work):
        return page
    if page.get("fill") == "heatmap" and rows:
        numeric_columns = [
            index for index in range(1, len(columns))
            if sum(" num" in f" {table_cell_class('measure', row[index] if index < len(row) else '')}" for row in rows) >= max(2, len(rows) // 2)
        ]
        long_text = max((len(str(cell)) for row in rows for cell in row), default=0) >= 60
        if not numeric_columns and long_text:
            page["content"] = {**content, "blocks": [block for block in content.get("blocks") or [] if block.get("kind") != "fig"]}
            page["fill"] = page["recipe"] = page["visualization"] = None
            page["role"] = page["_render_job"] = "roster"
            return page
    if opportunity_visual_page(page, material):
        return page
    if "话术" in str(page.get("title") or "") and rows and any("年化收入" in str(col) for col in columns):
        value_col = next(i for i, col in enumerate(columns) if "年化收入" in str(col))
        dish_col = next((i for i, col in enumerate(columns) if "菜品" in str(col)), 0)
        store_col = next((i for i, col in enumerate(columns) if "门店" in str(col)), None)
        figure_rows = []
        for row in rows:
            label = (f"{row[store_col]} · " if store_col is not None else "") + str(row[dish_col])
            figure_rows.append([label, row[value_col]])
        page["_figure_material"] = "| 菜品 | 每 +1% 渗透率的年化收入 |\n| --- | ---: |\n" + "\n".join(f"| {label} | {value} |" for label, value in figure_rows)
        page["_preview_columns"] = [columns[dish_col], columns[value_col]]
        conclusion = re.search(r"结论[：:]\s*(.+?。)", material)
        if conclusion:
            page["_display_title"] = conclusion.group(1).strip()
        page["fill"] = page["recipe"] = "pareto"
        page["how_to_read"] = "柱是每提升 1% 渗透率的年化收入；先练高价值菜"
        page["_render_job"] = "chart-table"
        return page
    if role in {"kpi", "statement"} and "洞察" in str(page.get("title") or "") and len(insight_sections(material)) >= 2:
        page["_render_job"] = "statement"
        page["_insight"] = True
        return page
    cards = [block for block in content.get("blocks") or [] if block.get("kind") == "kpi-card"]
    labels = [str(card.get("label") or "") for card in cards]
    if role == "kpi" and 2 <= len(cards) <= 5 and labels and (max(map(len, labels)) >= 18 or sum(map(len, labels)) / len(labels) >= 14):
        page["_render_job"] = "kpi"
        page["_argument_kpi"] = True
        if str(page.get("title") or "").startswith("5.1.5 餐具选择与摆盘建议"):
            page["_dish_example"] = True
        if page.get("id") == "p-0004" and str(page.get("title") or "").startswith("23.1 提案缘起"):
            page["_argument_thesis"] = "不说菜系，说地方：红桥"
            page["_argument_question"] = "如果不说“淮扬菜”，这家店在顾客心里究竟叫什么？"
            page["_argument_support"] = "菜系是知识，需要教育；桥是画面，不需要教育。"
            page["_argument_cards"] = [
                {"value": "8 / 8", "label": "高价·高分·高流量餐厅拥有名词化产品符号"},
                {"value": "1 家", "label": "佛山淮扬门店"},
                {"value": "31 元", "label": "佛山淮扬菜人均"},
                {"value": "83 元", "label": "江浙品类价格天花板"},
                {"value": "128 元", "label": "本案目标人均"},
            ]
        return page
    if role in {"kpi", "statement"} and len(insight_sections(material)) >= 2:
        page["_render_job"] = "statement"
        page["_insight"] = True
        return page
    if role == "kpi" and sum(len(str(card.get("label") or "")) > 24 for card in cards) >= 2:
        page["_render_job"] = "statement"
        return page
    if page.get("fill") == "diverging-bar" and rows and KEY_RANKING_RE.search(str(page.get("title") or "")):
        values = [str(cell) for row in rows for cell in row[1:] if re.search(r"\d", str(cell))]
        if values and not any(re.search(r"(?:^|\s)[−-]\s*\d", value) for value in values):
            page["fill"] = page["recipe"] = "pareto"
            page["how_to_read"] = "柱长是贡献或规模，折线是累计占比；先看头部项"
            page["_render_job"] = "chart-table" if role == "chart-table" else "chart"
            return page
    if role == "roster" and 2 <= len(rows) <= 8 and KEY_RANKING_RE.search(str(page.get("title") or "")):
        numeric = [
            index for index in range(1, len(columns))
            if sum(bool(re.search(r"\d", str(row[index] if index < len(row) else ""))) for row in rows) >= max(2, len(rows) // 2)
        ]
        if len(numeric) == 1:
            page["fill"] = page["recipe"] = "pareto"
            page["how_to_read"] = "柱长是关键值，折线是累计占比；右侧保留精确值"
            page["_render_job"] = "chart-table"
            page["_preview_columns"] = [columns[0], columns[numeric[0]]]
            return page
        current = next((i for i, col in enumerate(columns) if re.search(r"当前|现状|基线", str(col))), None)
        target = next((i for i, col in enumerate(columns) if re.search(r"目标|建议", str(col))), None)
        if current is not None and target is not None:
            page["fill"] = page["recipe"] = "slope"
            page["how_to_read"] = "左侧是当前或基线，右侧是目标；只比较同一口径"
            page["_render_job"] = "chart-table"
            page["_preview_columns"] = [columns[0], columns[current], columns[target]]
            return page
    if role not in {"roster", "matrix", "compare", "readme"} or page.get("fill"):
        return page
    assigned = assign_page_fill(page.get("title") or "", material, role, baslide=baslide)
    header = next((line for line in material.splitlines() if line.strip().startswith("|") and line.count("|") >= 2), "")
    column_count = max(0, len([cell for cell in header.strip().strip("|").split("|") if cell.strip()]))
    if role == "roster" and column_count > 7:
        assigned = {"fill": "heatmap", "recipe": "heatmap", "how_to_read": "浅色为低值，深色为高值；右侧保留关键字段"}
    if assigned.get("fill"):
        page["fill"] = assigned["fill"]
        page["recipe"] = assigned.get("recipe")
        page["how_to_read"] = page.get("how_to_read") or assigned.get("how_to_read") or ""
        page["_render_job"] = "chart-table" if role == "roster" else "chart"
    return page


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
    page = scrub_internal_copy(page)
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


def fill_figure(section: str, page: dict, material: str, job: str, body_html: str, title: str, baslide: Path) -> str:
    fig = None
    try:
        fig = figure_for_page(title, material, preset_fill=page.get("fill") or page.get("recipe"), baslide=baslide)
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
            lambda match: f'font-size="{max(float(match.group(1)), 24 if job == "chart-table" else 22):g}"',
            fig.svg,
        )
        figure = f'<figure class="sd-v2-figure" role="img" aria-label="{esc(caption)}">{svg}<figcaption>{esc(caption)}</figcaption><template class="sd-v2-fallback">{fallback}</template></figure>'
        if job == "chart-table":
            figure_width = "62%" if page.get("_preview_columns") else "68%"
            section = section.replace('display:flex; gap:32px;', 'display:flex; gap:24px;').replace('flex:0 0 58%;', f'flex:0 0 {figure_width};')
            columns = (page.get("content") or {}).get("columns") or []
            rows = (page.get("content") or {}).get("rows") or []
            y_name = ((((page.get("evidence") or [{}])[0].get("encoding") or {}).get("mapping") or {}).get("y"))
            requested = page.get("_preview_columns") or []
            picks = [columns.index(name) for name in requested if name in columns]
            if not picks:
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
                    raw = re.sub(r"<br\s*/?>", "；", str(row[i] if i < len(row) else ""), flags=re.I)
                    raw = re.sub(r"<[^>]+>", "", raw)
                    visible = raw
                    cells.append(f'<td{klass}>{esc(visible)}</td>')
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


def fill_section(section: str, page: dict, work: Path, units: dict[str, str], index: int, total: int, deck_name: str, baslide: Path) -> str:
    role = page.get("role") or "statement"
    job = page.get("_render_job") or ROLE_TO_JOB.get(role, "statement")
    title = page.get("_display_title") or page.get("title") or ""
    path = page.get("outline_path") or []
    kicker = " · ".join([p for p in path[-2:]] or [role])
    material = (page.get("_figure_material") or viz_material(page)) if page.get("_structured") else page_material_text(page, work, units)
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
            section = fill_figure(section, page, material, job, body_html, title, baslide)
        elif job == "statement":
            visual = data_quality_insight_html() if page.get("_data_quality") else (insight_figure(page, material) if page.get("_insight") else editorial_figure(page, material))
            section = replace_div_inner(section, "sd-content", visual or body_html)
        elif job == "kpi" and page.get("_argument_kpi"):
            section = replace_div_inner(section, "sd-content", argument_kpi_html(page))
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
    transparent = config.get("transparent_logo") or {}
    if fallback.is_file() and hashlib.sha256(fallback.read_bytes()).hexdigest() == transparent.get("sha256"):
        return fallback, config
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
        page = prepare_visual_page(page, work, units, baslide)
        role = page.get("role") or "statement"
        job = page.get("_render_job") or ROLE_TO_JOB.get(role, "statement")
        tpl = templates.get(job) or templates.get("statement")
        if not tpl:
            raise SystemExit(f"no template for job {job}")
        sections.append(fill_section(tpl, page, work, units, i, total, deck_name, baslide))

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
:root{{--slide-aspect:16/9;--gf-surface:{surface};--gf-paper:{paper};--gf-primary:{primary};--gf-ink:{ink};--gf-muted:{muted};--gf-grid:color-mix(in srgb,{ink} 18%,transparent);--gf-accent:{accent};--gf-highlight:{highlight};--gf-positive:{accent};--gf-negative:{negative};--gf-warning:#9A671B;--gf-font-body:var(--sd-font-serif);--gf-font-number:var(--sd-font-mono);--gf-safe-x:calc(var(--sd-canvas-w)*.054);--gf-baseline:calc(var(--sd-canvas-w)*.0027778);--sd-primary:var(--gf-primary);--sd-surface:var(--gf-surface);--sd-paper:var(--gf-paper);--sd-ink-100:var(--gf-ink);--sd-ink-60:color-mix(in srgb,var(--gf-ink) 72%,var(--gf-paper));--sd-accent:var(--gf-accent);--sd-secondary:var(--gf-negative);--sd-status-ready:var(--gf-accent);--sd-status-ready-text:var(--gf-accent);--sd-div-pos-1:#AD832B;--sd-div-pos-2:var(--gf-accent);--sd-seq-100:#B68B36;--sd-seq-200:#A67B27;--sd-margin:var(--gf-safe-x);--sd-radius-card:2px;--sd-font-serif:"Songti SC","STSong",serif;--sd-font-mono:"IBM Plex Mono","Songti SC",monospace;--sd-font-symbol:"Songti SC","STSong",serif}}
html[data-font-pack]{{--sd-font-serif:"Songti SC","STSong",serif;--sd-font-mono:"IBM Plex Mono","Songti SC",monospace;--sd-font-symbol:"Songti SC","STSong",serif}}
.sd-slide{{container-type:size;aspect-ratio:var(--slide-aspect)}}
.sd-slide [style*="font-weight:900"]{{font-weight:700!important}}
.sd-table,.sd-num,.num{{font-variant-numeric:tabular-nums}}
.sd-list{{font-size:var(--sd-type-body);line-height:1.45}}
.sd-v2-figure{{width:100%;height:100%;margin:0;display:grid;grid-template-rows:minmax(0,1fr) auto;gap:.4em}}
.sd-v2-figure>svg{{min-height:0;width:100%;height:100%}}
.sd-v2-figure svg text:not([stroke]){{font-weight:400;paint-order:normal;stroke:none}}
.sd-v2-figure svg text[font-weight="600"],.sd-v2-figure svg text[font-weight="700"]{{font-weight:500}}
.sd-v2-figure>figcaption{{font-size:calc(var(--sd-canvas-h)*.0175);font-weight:400;color:var(--gf-muted);line-height:1.35}}
.sd-slide[data-job="chart"] .sd-content,.sd-slide[data-job="chart-table"] .sd-content>div:first-child{{border-width:1px!important;box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--gf-accent) 8%,transparent);overflow:hidden}}
.sd-slide[data-job="chart-table"] .sd-content{{overflow:hidden}}
.sd-slide[data-job="chart"],.sd-slide[data-job="chart-table"]{{--sd-type-h2:calc(var(--sd-canvas-h)*.038)}}
.sd-slide .sd-h2{{font-weight:600}}
.sd-slide[data-job="chart-table"] .sd-table{{font-size:calc(var(--sd-canvas-h)*.0195);line-height:1.28}}
.sd-slide[data-job="chart-table"] .sd-table th,.sd-slide[data-job="chart-table"] .sd-table td{{font-size:inherit!important;font-weight:400}}
.sd-slide[data-job="chart-table"] .sd-table th{{font-weight:600}}
.sd-slide[data-job="kpi"]{{--sd-type-kpi:calc(var(--sd-canvas-h)*.098);--sd-type-h3:calc(var(--sd-canvas-h)*.034)}}
.sd-slide[data-job="kpi"] .sd-content:has(.sd-kpi:nth-child(2):last-child){{--sd-type-kpi:calc(var(--sd-canvas-h)*.100);--sd-type-h3:calc(var(--sd-canvas-h)*.035)}}
.sd-argument-kpi{{width:100%;height:100%;display:grid;grid-template-rows:auto minmax(0,1fr) auto;gap:4%;overflow:hidden}}
.sd-argument-kpi.is-generic{{grid-template-rows:minmax(0,1fr)}}
.sd-argument-lead{{display:grid;grid-template-columns:1.05fr .95fr;gap:4%;align-items:end;border-bottom:1px solid var(--gf-grid);padding-bottom:2.2%}}
.sd-argument-thesis{{font-family:var(--sd-font-serif);font-size:calc(var(--sd-canvas-h)*.052);line-height:1.2;font-weight:600;color:var(--gf-ink)}}
.sd-argument-question{{font-family:var(--sd-font-serif);font-size:calc(var(--sd-canvas-h)*.025);line-height:1.5;color:var(--gf-muted)}}
.sd-argument-grid{{min-height:0;display:grid;grid-template-columns:repeat(12,minmax(0,1fr));grid-auto-rows:minmax(0,1fr);gap:2.4%}}
.sd-argument-card{{grid-column:span 6;min-width:0;background:var(--gf-paper);border-top:3px solid var(--gf-accent);padding:5% 6%;display:flex;flex-direction:column;justify-content:center;gap:8%}}
.sd-argument-kpi.n-3 .sd-argument-card{{grid-column:span 4}}
.sd-argument-kpi.n-5 .sd-argument-card{{grid-column:span 2}}
.sd-argument-kpi.n-5 .sd-argument-card:first-child{{grid-column:span 4}}
.sd-argument-value{{font-family:var(--sd-font-mono);font-size:calc(var(--sd-canvas-h)*.055);line-height:1;font-weight:600;color:var(--gf-negative);white-space:nowrap}}
.sd-argument-label{{font-family:var(--sd-font-serif);font-size:calc(var(--sd-canvas-h)*.022);line-height:1.42;font-weight:400;color:var(--gf-ink)}}
.sd-argument-meter{{width:100%;height:.7em;background:color-mix(in srgb,var(--gf-ink) 9%,var(--gf-paper));overflow:hidden}}
.sd-argument-meter i{{display:block;width:var(--w);height:100%;background:var(--gf-accent)}}
.sd-argument-scale{{font-family:var(--sd-font-mono);font-size:calc(var(--sd-canvas-h)*.014);font-weight:400;color:var(--gf-muted);letter-spacing:.03em}}
.sd-argument-note,.sd-argument-support{{font-family:var(--sd-font-serif);font-size:calc(var(--sd-canvas-h)*.018);line-height:1.4;font-weight:400;color:var(--gf-muted)}}
.sd-argument-support{{margin:0;border-left:3px solid var(--gf-accent);padding-left:1em}}
.sd-argument-curated{{min-height:0;display:grid;grid-template-columns:.78fr 1.22fr;gap:2.5%}}
.sd-symbol-proof,.sd-price-ladder{{min-width:0;background:var(--gf-paper);border-top:3px solid var(--gf-accent);padding:4.5%;margin:0}}
.sd-symbol-proof{{display:grid;grid-template-rows:minmax(0,1fr) auto auto;gap:3%;align-items:center}}
.sd-symbol-proof svg{{width:100%;height:100%;min-height:0}}
.sd-symbol-proof .ring{{fill:color-mix(in srgb,var(--gf-accent) 8%,var(--gf-paper));stroke:var(--gf-accent);stroke-width:3}}
.sd-symbol-proof .nodes circle{{fill:var(--gf-accent);stroke:var(--gf-paper);stroke-width:4}}
.sd-symbol-proof .center{{font-family:var(--sd-font-mono);font-size:36px;font-weight:600;fill:var(--gf-negative);text-anchor:middle}}
.sd-symbol-proof .center-sub{{font-family:var(--sd-font-mono);font-size:20px;fill:var(--gf-muted);text-anchor:middle}}
.sd-symbol-proof figcaption{{font-size:calc(var(--sd-canvas-h)*.021);line-height:1.42;text-align:center}}
.sd-market-gap{{grid-column:1/-1;align-self:end;border-top:1px solid var(--gf-grid);padding-top:4%;display:flex;align-items:baseline;gap:5%}}
.sd-market-gap strong{{font-family:var(--sd-font-mono);font-size:calc(var(--sd-canvas-h)*.036);font-weight:600;color:var(--gf-negative)}}
.sd-market-gap span{{font-size:calc(var(--sd-canvas-h)*.020)}}
.sd-price-ladder{{display:grid;grid-template-rows:auto minmax(0,1fr);gap:3%}}
.sd-ladder-title{{font-size:calc(var(--sd-canvas-h)*.024);font-weight:600}}
.sd-price-ladder svg{{width:100%;height:100%;min-height:0}}
.sd-price-ladder .market-band{{fill:color-mix(in srgb,var(--gf-accent) 10%,var(--gf-paper))}}
.sd-price-ladder .band-label,.sd-price-ladder .tick,.sd-price-ladder .label{{font-family:var(--sd-font-serif);font-size:17px;fill:var(--gf-muted)}}
.sd-price-ladder .axis{{stroke:var(--gf-ink);stroke-width:2}}
.sd-price-ladder .marker line{{stroke:var(--gf-accent);stroke-width:2;stroke-dasharray:5 5}}
.sd-price-ladder .marker circle{{fill:var(--gf-accent)}}
.sd-price-ladder .marker .value{{font-family:var(--sd-font-mono);font-size:25px;font-weight:600;fill:var(--gf-ink)}}
.sd-price-ladder .marker.target line{{stroke:var(--gf-negative);stroke-width:4;stroke-dasharray:none}}
.sd-price-ladder .marker.target circle{{fill:var(--gf-negative)}}
.sd-price-ladder .marker.target .value{{fill:var(--gf-negative)}}
.sd-price-ladder .bracket{{fill:none;stroke:var(--gf-negative);stroke-width:2}}
.sd-price-ladder .ratio{{font-family:var(--sd-font-serif);font-size:18px;font-weight:600;fill:var(--gf-negative)}}
.sd-dish-evidence{{grid-template-columns:.72fr 1.28fr;grid-template-rows:1fr;gap:2.5%}}
.sd-dish-evidence article{{min-width:0;background:var(--gf-paper);border-top:3px solid var(--gf-accent);padding:6%;display:flex;flex-direction:column;align-items:flex-start}}
.sd-evidence-kicker{{font-family:var(--sd-font-mono);font-size:calc(var(--sd-canvas-h)*.016);letter-spacing:.08em;color:var(--gf-accent)}}
.sd-dish-evidence strong{{margin-top:8%;font-family:var(--sd-font-mono);font-size:calc(var(--sd-canvas-h)*.058);line-height:1;font-weight:600;color:var(--gf-negative)}}
.sd-dish-evidence h3{{margin:6% 0 0;font-size:calc(var(--sd-canvas-h)*.028);line-height:1.35;font-weight:600}}
.sd-dish-evidence p{{margin:auto 0 0;font-size:calc(var(--sd-canvas-h)*.020);line-height:1.5;color:var(--gf-muted)}}
.sd-penetration{{width:100%;margin-top:7%;display:grid;grid-template-columns:7em minmax(0,1fr);gap:1em;align-items:center;font-size:calc(var(--sd-canvas-h)*.020)}}
.sd-penetration i{{display:block;width:var(--w);height:.55em;background:var(--gf-accent)}}
.sd-slide[data-job="statement"] .sd-content{{display:flex;align-items:center}}
.sd-slide[data-job="statement"] .sd-content>.sd-block{{width:100%}}
.sd-slide[data-job="roster"] .sd-block[data-block="table"]{{height:96%}}
.sd-slide[data-job="roster"] .sd-table{{height:100%}}
.sd-editorial-figure{{position:relative;width:100%;height:100%;margin:0;padding:4.5% 5%;overflow:hidden;background:var(--gf-paper);border-top:2px solid var(--gf-accent);border-bottom:1px solid var(--gf-grid);display:grid;grid-template-rows:auto minmax(0,1fr) auto;gap:4%;isolation:isolate}}
.sd-editorial-figure blockquote{{position:relative;z-index:2;margin:0;max-width:88%;font-family:var(--sd-font-serif);font-size:calc(var(--sd-canvas-h)*.050);line-height:1.25;font-weight:600;color:var(--gf-ink)}}
.sd-editorial-figure ol{{position:relative;z-index:2;list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));align-content:center;gap:0 5%}}
.sd-editorial-figure li{{min-width:0;padding:3.2% 0;border-top:1px solid var(--gf-grid);display:grid;grid-template-columns:3.4em minmax(0,1fr);gap:1.2em;align-items:start;font-size:calc(var(--sd-canvas-h)*.025);line-height:1.48;color:var(--gf-ink)}}
.sd-editorial-index{{font-family:var(--sd-font-mono);font-size:.72em;letter-spacing:.14em;color:var(--gf-accent);padding-top:.3em}}
.sd-em-num{{font-family:var(--sd-font-mono);font-size:1.08em;color:var(--gf-negative);font-weight:700}}
.sd-editorial-figure figcaption{{position:relative;z-index:2;font-family:var(--sd-font-mono);font-size:var(--sd-type-micro);letter-spacing:.06em;color:var(--gf-muted)}}
.sd-compass-mark{{position:absolute;z-index:0;right:2%;bottom:2%;width:40%;aspect-ratio:1;border:2px solid color-mix(in srgb,var(--gf-accent) 18%,transparent);border-radius:50%}}
.sd-compass-mark:before,.sd-compass-mark:after{{content:"";position:absolute;inset:18%;border:1px solid color-mix(in srgb,var(--gf-accent) 16%,transparent);border-radius:50%}}
.sd-compass-mark:after{{inset:50% -14%;border:0;border-top:1px solid color-mix(in srgb,var(--gf-accent) 13%,transparent);border-radius:0;transform:rotate(-28deg)}}
.sd-editorial-figure.is-manifesto{{grid-template-rows:minmax(0,1fr) auto;align-items:center}}
.sd-editorial-figure.is-manifesto blockquote{{max-width:76%;font-size:calc(var(--sd-canvas-h)*.070);line-height:1.2}}
.sd-editorial-figure.is-manifesto ol{{display:none}}
.sd-editorial-figure.is-duality ol{{grid-template-columns:repeat(2,minmax(0,1fr));gap:7%;align-items:stretch}}
.sd-editorial-figure.is-duality li{{border-top:3px solid var(--gf-accent);grid-template-columns:1fr;grid-template-rows:auto 1fr;font-size:calc(var(--sd-canvas-h)*.030)}}
.sd-editorial-figure.is-route ol{{display:flex;align-items:stretch;gap:0}}
.sd-editorial-figure.is-route li{{flex:1;display:block;padding:4% 2.2%;border-top:3px solid var(--gf-accent);border-right:1px solid var(--gf-grid);font-size:calc(var(--sd-canvas-h)*.023)}}
.sd-editorial-figure.is-route li:last-child{{border-right:0}}
.sd-editorial-figure.is-route .sd-editorial-index{{display:block;margin-bottom:1.2em}}
.sd-editorial-figure.is-constellation blockquote{{max-width:62%}}
.sd-editorial-figure.is-constellation ol{{margin-left:14%;grid-template-columns:repeat(2,minmax(0,1fr))}}
.sd-slide[data-job="roster"] .sd-content{{background:var(--gf-paper);border:1px solid var(--gf-grid);overflow:hidden}}
.sd-slide[data-job="roster"] .sd-table{{border-collapse:collapse;background:transparent}}
.sd-slide[data-job="roster"] .sd-table{{table-layout:fixed;font-family:var(--sd-font-serif)}}
.sd-slide[data-job="roster"] .sd-table th{{background:var(--gf-primary);color:var(--gf-ink);border-color:var(--gf-paper);font-family:var(--sd-font-serif);font-size:calc(var(--sd-canvas-h)*.020);line-height:1.2;letter-spacing:.04em;vertical-align:middle}}
.sd-slide[data-job="roster"] .sd-table td{{border-color:var(--gf-grid);font-family:var(--sd-font-serif);font-size:calc(var(--sd-canvas-h)*.019);line-height:1.42;text-align:left;vertical-align:middle;overflow-wrap:break-word;word-break:normal}}
.sd-slide[data-job="roster"] .sd-table--wide th{{font-size:calc(var(--sd-canvas-h)*.0175)}}
.sd-slide[data-job="roster"] .sd-table--wide td{{font-size:calc(var(--sd-canvas-h)*.017);padding-left:.7em;padding-right:.7em}}
.sd-slide[data-job="roster"] .sd-table--dense th{{font-size:calc(var(--sd-canvas-h)*.017)}}
.sd-slide[data-job="roster"] .sd-table--dense td{{font-size:calc(var(--sd-canvas-h)*.0165);line-height:1.36}}
.sd-slide[data-job="roster"] .sd-table td.num{{font-family:var(--sd-font-mono);text-align:right;white-space:nowrap}}
.sd-slide[data-job="roster"] .sd-table .col-index{{font-family:var(--sd-font-mono);text-align:center;white-space:nowrap}}
.sd-slide[data-job="roster"] .sd-table .col-date{{font-family:var(--sd-font-mono);text-align:center;white-space:normal}}
.sd-slide[data-job="roster"] .sd-table td.col-key{{font-weight:600}}
.sd-slide[data-job="roster"] .sd-table td.col-status{{font-weight:600;color:var(--gf-accent)}}
.sd-slide[data-job="roster"] .sd-table tbody tr:nth-child(even) td{{background:color-mix(in srgb,var(--gf-primary) 28%,var(--gf-paper))}}
.sd-slide[data-job="roster"] .sd-table td:first-child{{color:var(--gf-accent)}}
.sd-slide[data-job="kpi"] .sd-kpi{{border-radius:2px;border-width:1px;border-top:4px solid var(--gf-accent);box-shadow:none}}
.sd-slide[data-job="kpi"] .sd-kpi .v,.sd-em-num{{font-weight:600!important}}
.sd-slide[data-job="divider"]:after{{content:"";position:absolute;width:34%;aspect-ratio:1;right:4%;bottom:-24%;border:2px solid color-mix(in srgb,var(--gf-accent) 18%,transparent);border-radius:50%;box-shadow:inset 0 0 0 calc(var(--sd-canvas-h)*.045) color-mix(in srgb,var(--gf-accent) 5%,transparent)}}
.sd-data{{display:none!important}}
.sd-font-ui,#sd-explain,#sd-explain-restore,.sd-nav-hint{{display:none!important}}
"""
    js = js_path.read_text(encoding="utf-8")
    font = "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap"
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
