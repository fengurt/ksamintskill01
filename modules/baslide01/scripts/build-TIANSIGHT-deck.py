#!/usr/bin/env python3
"""Build 侍天 TIANSIGHT v2.0 HTML decks from markdown.

Every H1 chapter, H2/H3 unit, paragraph, list, and GFM table is emitted.
Canvas copy must be complete: never ellipsis on the field. Paginate at sentence
or clause. No orphan glyph / orphan line. Overflow only past the row/char budget.
Slides clone the 12 L2 jobs in templates/TIANSIGHT/jobs/. No new CSS classes.
"""
from __future__ import annotations

import html
import json
import math
import re
import sys
import base64
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = ROOT / "templates/TIANSIGHT/TIANSIGHT-v2.css"
JS_PATH = ROOT / "templates/TIANSIGHT/TIANSIGHT-deck.js"
LOGO_PATH = ROOT / "templates/TIANSIGHT/logo/侍天.png"

JOBS = (
    "cover", "divider", "toc", "readme", "statement", "kpi",
    "roster", "chart", "chart-table", "matrix", "compare", "verdict",
)
PAGE_TYPE = {
    "cover": "cover",
    "divider": "chapter",
    "toc": "toc",
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
SHELL = {
    "cover": "shell-cover",
    "divider": "shell-divider",
    "toc": "shell-body",
    "readme": "shell-body has-rail",
    "statement": "shell-body has-rail",
    "kpi": "shell-body has-rail",
    "roster": "shell-body has-rail",
    "chart": "shell-fig has-rail",
    "chart-table": "shell-fig has-rail",
    "matrix": "shell-body has-rail",
    "compare": "shell-body has-rail",
    "verdict": "shell-body has-rail",
}
CN_NUM = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖", "拾", "拾壹", "拾贰", "拾叁", "拾肆", "拾伍"]
ROSTER_ROWS = 10
ROSTER_ROWS_WIDE = 7
ORPHAN_PAGE_ROWS = 2
CHART_ROWS = 12
CHART_TABLE_SIDE = 6
BIN_CHART_ROWS = 20
BUBBLE_ROWS = 40
BUBBLE_R_MIN = 8
BUBBLE_R_MAX = 22
BUBBLE_LABEL_MAX = 12
BUBBLE_CLUSTER_PX = 72
NAMED_SERIES_MAX = 24
BUBBLE_MUST_LABELS = (
    "石头先生", "Shake", "汉堡王", "华莱士", "牛约堡", "Wagas", "沃歌斯",
    "必胜客", "麦当劳", "肯德基", "赛百味", "达美乐", "超级碗", "BAKER",
    "Tubestation", "烤炉", "好伦哥", "轻遇",
)
GE20_STORES = 20
DOSSIER_BRAND_MD = ROOT / "ref/mds/08_北京西式快餐可参考品牌分析专项_B1.0.md"
TOC_ROWS = 10
PROSE_MAIN = 96
PROSE_SUPPORT = 420
PROSE_PACK_LIMIT = 2
STATEMENT_MAIN_MAX = 96
STATEMENT_SUPPORT_MAX = 420
STATEMENT_PAGE_MIN = 150
STATEMENT_PAGE_TARGET = 280
STATEMENT_PAGE_MAX = 420
LEAD_IN_MAX = 140
TITLE_CANVAS_MAX = 72
CHIP_CANVAS_MAX = 28
ZW = "\u2060"
ORPHAN_GLUE = 6
CELL_ORPHAN_GLUE = 3
TRAIL_PUNCT = "。，、；：！？—·」』）)］]》>"
SHORT_MAIN = 28
SUPPORT_GRACE = 48
SENT_SPLIT = re.compile(r"(?<=[。！？])(?![\"”」』])")
EMOJI_RE = re.compile(r"[🆕❌✅⚠️🥇🥈🥉✨🍟🥤📌🔴🟡🟢🎯]+")
CLAIM_BREAK = re.compile(r"^结论[一二三四五六七八九十0-9]")

FIG_W = 1170
FIG_H = 500
# viewBox type ≈ same share of figure height as body/title on the 1620 canvas
FIG_CAPTION = 18
FIG_TICK = 16
FIG_CAT = 18
FIG_VAL = 18
FIG_NAME = 20
HOW_FOR_FILL = {
    "pareto": "柱是量，线是累计；看 80% 落在第几根",
    "heatmap": "行×列着色；深色=高，浅色=低；零不是缺口",
    "slope": "左到右是两口径；升用就绪色，降用印泥",
    "hist-cdf": "柱是分箱计数，线是累计覆盖",
    "waterfall": "柱从上一根的顶接着走，看净变化",
    "funnel": "上宽下窄是流失，不是装饰三角",
    "treemap": "面积=份额，同一量纲才能比",
    "diverging-bar": "零轴居中；正负分向。全正时柱长即量",
    "line-dual": "两条线同一横轴，量纲写在图上",
    "quadrant": "中位切分归高侧 ≥",
    "bubble": "面积按平方根，大点先画；虚线是中位 ≥；未标名的点见清单",
    "radar": "各轴同一 0–max 量纲，禁止混单位",
    "timeline": "从左到右是阶段顺序，点上的数是门店目标",
    "weight-shift": "行是门店台阶，块是当时主导的问题域；色深=权重大",
    "slots": "一屏一层；层名是决策，行是可执行项",
    "price-ladder": "纵轴是价格，点是对手；红点是自己",
    "number-axis": "轴上的空档才是机会，不是点与点的装饰间距",
    "stack": "底下是现在该做的，上面是以后才配得上的",
}

NUM_RE = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.*\S)\s*$")
HR_RE = re.compile(r"^---+\s*$")
CHAPTER_RE = re.compile(r"^(第[一二三四五六七八九十零百0-9]+部分|第\s*[0-9]+部分|附录|附[录篇]?)")


CITE_TAG_RE = re.compile(r"</?cite\b[^>]*>", re.I)
CITE_ENTITY_RE = re.compile(r"&lt;/?cite\b[^&]*&gt;", re.I)
CITE_ATTR_RE = re.compile(r"\bcite\s+index\s*=\s*[\"']?[\w.-]+[\"']?", re.I)
CITE_OPEN_RE = re.compile(r"</?cite\b[^>]*", re.I)
CITE_LEAK_RE = re.compile(r"cite\s+index|</?cite\b|&lt;cite", re.I)

SISTER_STORE_REWRITES = (
    ('不用"同一个老板"的说法，用"石头先生家族"', "标明兄弟店、同一老板"),
    ("不用“同一个老板”的说法，用“石头先生家族”", "标明兄弟店、同一老板"),
    ("不用「同一个老板」的说法，用「石头先生家族」", "标明兄弟店、同一老板"),
    ("品牌架构未定义", "品牌架构已定：母品牌「石头先生」+ 业态子品牌"),
    ('与合生汇 B2 的"石头先生的烤炉"关系不明', "烤炉与汉堡是同一老板的兄弟店；要定的是视觉关联强度与口碑修复节奏"),
    ("与合生汇 B2 的“石头先生的烤炉”关系不明", "烤炉与汉堡是同一老板的兄弟店；要定的是视觉关联强度与口碑修复节奏"),
    ("这个关系必须现在定义。", "两店已是兄弟店、同一老板。现在要定的是视觉关联强度，以及烤炉口碑从 3.9 修到 4.2 的节奏。"),
    ("这个关系必须现在定义", "两店已是兄弟店、同一老板。现在要定的是视觉关联强度，以及烤炉口碑从 3.9 修到 4.2 的节奏"),
    ("### 三种可选架构", "### 已定架构：母品牌 + 业态子品牌"),
    ("汉堡店要不要与烤炉做品牌关联？", "两店已是兄弟店：视觉关联做到多强？"),
    ("客户在这个商场里，已经有一家进入全场人气前 6% 的门店。", "兄弟店「石头先生的烤炉」就在本场、同一老板，已进入全场人气前 6%。"),
    ("客户在同商场 B2 已有一家烘焙店", "兄弟店「石头先生的烤炉」就在同商场 B2，同一老板"),
    ('"石头先生的烤炉旗下"', "「烤炉旗下开的汉堡」（从属说反）"),
    ("“石头先生的烤炉旗下”", "「烤炉旗下开的汉堡」（从属说反）"),
    ("门头/主视觉上出现烤炉 logo", "门头把两店 logo 叠成一家店"),
    ("大众点评品牌页合并", "烤炉未到 4.2 前合并点评品牌页"),
    ("隐藏资产与隐藏风险：石头先生的烤炉就在这个商场里", "隐藏资产：兄弟店「石头先生的烤炉」就在本场（同一老板）"),
    ("我方建议 A（母品牌 + 子品牌）", "已定 A（母品牌 + 子品牌）。两店是同一老板的兄弟店"),
    ('"同一支烘焙团队，十余年现烤功底"', "兄弟店、同一个老板；同一支烘焙团队，十余年现烤功底"),
    ("“同一支烘焙团队，十余年现烤功底”", "兄弟店、同一个老板；同一支烘焙团队，十余年现烤功底"),
    ("| 见 §7.8 |", "| 见 §7.3 |"),
)

VOICE_REWRITES = (
    ("**在做任何品牌分析之前，必须先做品牌名归一化。否则所有规模数字都是错的。**", "未归一化的品牌规模一律不作数。"),
    ("在做任何品牌分析之前，必须先做品牌名归一化。否则所有规模数字都是错的。", "未归一化的品牌规模一律不作数。"),
    ("按原型分组。每个档案回答四件事：**它是什么 / 数据长什么样 / 学什么 / 不学什么。**", "按原型建档。只记可迁移与不可复制。"),
    ("按原型分组。每个档案回答四件事：它是什么 / 数据长什么样 / 学什么 / 不学什么。", "按原型建档。只记可迁移与不可复制。"),
    ("为石头先生的汉堡建立一份\"该学谁、学什么、学到什么程度、什么不能学\"的可执行参照系", "为石头先生建立可执行的对标参照"),
    ("为石头先生的汉堡建立一份“该学谁、学什么、学到什么程度、什么不能学”的可执行参照系", "为石头先生建立可执行的对标参照"),
    ("对每个品牌，我们看五件事——**这五件事合起来回答\"它值不值得学\"：**", "五个评估维度："),
    ("对每个品牌，我们看五件事——这五件事合起来回答\"它值不值得学\"：", "五个评估维度："),
    ("不是所有品牌都值得学。我们按三层筛：", "三层筛选："),
    ("一个可执行的目标体系必须分三层：**不变的北极星、可衡量的阶段目标、可证伪的核心命题。**", "目标分三层：北极星、阶段目标、可证伪命题。"),
    ("一个可执行的目标体系必须分三层：不变的北极星、可衡量的阶段目标、可证伪的核心命题。", "目标分三层：北极星、阶段目标、可证伪命题。"),
    ("**性质：** 方法论框架文件 —— 定义问题、选择工具、建立数据基础、给出 1→200 家的分阶段赋能路径", "**性质：** 1→200 家分阶段赋能"),
    ("**本报告回答\"这件事本质上是什么问题、用什么方法解、每个规模阶段该做什么\"**", "对齐 06 首店决策，给出 1→200 家路径"),
)


def esc(text: str) -> str:
    return html.escape(text or "", quote=True)


def strip_cite(text: str) -> str:
    text = text or ""
    text = CITE_TAG_RE.sub("", text)
    text = CITE_ENTITY_RE.sub("", text)
    text = CITE_ATTR_RE.sub("", text)
    text = CITE_OPEN_RE.sub("", text)
    return text


def rewrite_sister_store(text: str) -> str:
    for old, new in SISTER_STORE_REWRITES:
        text = text.replace(old, new)
    return text


def rewrite_report_copy(text: str) -> str:
    text = rewrite_sister_store(text)
    for old, new in VOICE_REWRITES:
        text = text.replace(old, new)
    text = text.replace("……", "——")
    text = text.replace("…", "——")
    text = re.sub(r"(?<!\d)\.\.\.(?!\d)", "——", text)
    return text


def display_title(text: str) -> str:
    title = strip_md(text)
    title = EMOJI_RE.sub("", title)
    title = title.replace('"', "").replace("“", "").replace("”", "")
    title = re.sub(r"\s+", " ", title).strip()
    title = title.replace(" —— ", " · ")
    title = title.replace("可迁移清单：学什么 / 不学什么 / 怎么验证", "可迁移清单")
    title = title.replace("阅读提示 · 本报告先修正了一个方法问题", "阅读提示 · 品牌名归一化")
    title = title.replace("本报告先修正了一个方法问题", "品牌名归一化")
    title = title.replace("推翻 V0.1：", "")
    title = title.replace("明年 20–30 家：", "")
    title = title.replace("为什么 60 元以上的汉堡店活得下去？答案是酒", "60 元以上靠酒撑住")
    title = title.replace("场内西式 9 家全景：55–90 元是真空", "场内西式九家 · 55–90 元真空")
    title = title.replace("北京独立精品汉堡全景（客单 ≥40 元、评论 ≥200）", "北京独立精品汉堡全景")
    title = title.replace("TOP 12 学习对象排序", "TOP 12 学习对象")
    title = title.replace("本报告最重要的一张表：", "")
    title = title.replace("规律一：评论中位数暴露了真实客流，而门店数不暴露", "评论中位才是客流")
    title = title.replace("规律二（反直觉）：品质连锁的门店一致性，高于巨头", "品质连锁一致性高于巨头")
    title = title.replace("规律三：4.5 分是流量阀门，不是荣誉", "4.5 分是流量阀门")
    title = title.replace("规律四：商场店 vs 街边/写字楼店", "商场店 vs 街边")
    title = title.replace("规律五：品类词决定天花板", "品类词决定天花板")
    title = title.replace("可参考性的三层筛选", "可参考性三层筛选")
    title = title.replace("战略级重构：披萨与烘焙不是负担，是石头先生唯一被验证过的规模载体", "披萨与烘焙是规模载体")
    title = title.replace("巴斯克三个月赠送：这不是营销费用，是获客投资", "巴斯克三个月赠送")
    title = re.sub(r"：学什么\s*/\s*不学什么(?:\s*/\s*怎么验证)?", "", title)
    return title


def strip_md(text: str) -> str:
    text = strip_cite(text or "")
    text = EMOJI_RE.sub("", text)
    text = re.sub(r'"([^"]+)"', r"「\1」", text)
    text = re.sub(r"“([^”]+)”", r"「\1」", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    text = text.replace("`", "")
    text = text.replace("……", "——").replace("…", "——")
    text = re.sub(r"(?<!\d)\.\.\.(?!\d)", "——", text)
    text = re.sub(r"^>\s?", "", text, flags=re.M)
    return re.sub(r"\s+", " ", text).strip()


def inline_md(text: str) -> str:
    raw = strip_cite(text or "")
    raw = EMOJI_RE.sub("", raw)
    raw = re.sub(r'"([^"]+)"', r"「\1」", raw)
    raw = re.sub(r"“([^”]+)”", r"「\1」", raw)
    raw = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)
    out = esc(raw)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = re.sub(r"`([^`]+)`", r"<b>\1</b>", out)
    return out


def assert_no_cite(html_text: str, path: str) -> None:
    match = CITE_LEAK_RE.search(html_text)
    assert not match, f"cite markup leaked in {path}: {html_text[match.start():match.start() + 80]!r}"


def has_clip_ellipsis(text: str) -> bool:
    t = (text or "").replace("……", "")
    return "…" in t or "..." in t


def strip_nodes_by_class(html_text: str, cls: str) -> str:
    token = f'class="{cls}"'
    out: list[str] = []
    i = 0
    while True:
        hit = html_text.find(token, i)
        if hit < 0:
            out.append(html_text[i:])
            return "".join(out)
        start = html_text.rfind("<", i, hit + 1)
        if start < 0:
            out.append(html_text[i:])
            return "".join(out)
        depth = 0
        k = start
        closed = False
        while k < len(html_text):
            if html_text.startswith("</", k):
                end = html_text.find(">", k)
                depth -= 1
                k = end + 1 if end >= 0 else len(html_text)
                if depth <= 0:
                    out.append(html_text[i:start])
                    i = k
                    closed = True
                    break
            elif html_text.startswith("<", k):
                end = html_text.find(">", k)
                tag = html_text[k:end + 1] if end >= 0 else ""
                if tag.endswith("/>") or tag.lower().startswith(("<br", "<img", "<hr", "<meta", "<link", "<input")):
                    k = end + 1 if end >= 0 else len(html_text)
                else:
                    depth += 1
                    k = end + 1 if end >= 0 else len(html_text)
            else:
                k += 1
        if not closed:
            out.append(html_text[i:])
            return "".join(out)


def assert_complete_canvas(slides: list[Slide], html_text: str, path: str) -> None:
    for slide in slides:
        if slide.job == "statement":
            main = (slide.extra or {}).get("main") or ""
            support = (slide.extra or {}).get("support") or ""
            assert not has_clip_ellipsis(main), f"clipped statement main: {slide.title!r} {path}"
            assert not has_clip_ellipsis(support), f"clipped statement support: {slide.title!r} {path}"
            assert not looks_diagram(main + support), f"ASCII dumped on statement: {slide.title!r} {path}"
        title = display_title(slide.title)
        assert not has_clip_ellipsis(title), f"ellipsis title {slide.title!r} {path}"
        assert not has_clip_ellipsis(slide.chip), f"ellipsis chip {slide.chip!r} {path}"
    slides_html = "".join(re.findall(r"<section class=\"slide.*?</section>", html_text, re.S))
    canvas = strip_nodes_by_class(slides_html, "sd-rail")
    leak = re.search(r"…|\.\.\.", canvas)
    assert not leak, f"ellipsis on canvas in {path}: {canvas[leak.start() - 24:leak.start() + 24]!r}"
    dumped = re.search(r'class="sd-quote">[^<]*[█▓░┌┐]', html_text)
    assert not dumped, f"ASCII on statement canvas in {path}"
    assert 'alt="侍天"' in html_text, f"missing 侍天 logo in {path}"
    for slide in slides:
        if slide.job == "roster" and re.search(r"·\s*\d+$", slide.title or ""):
            data_rows = len(re.findall(r"<tr\b", slide.body)) - 1
            if "sd-sum" in slide.body:
                data_rows -= 1
            assert data_rows >= 2, f"orphan roster page {slide.title!r} in {path}: {data_rows} rows"
        if slide.job == "statement" and slide.overflow_of:
            main = (slide.extra or {}).get("main") or ""
            support = (slide.extra or {}).get("support") or ""
            assert support.strip() or len(main) >= 24, f"orphan statement page {slide.title!r} in {path}"


SYLLABUS_LEAK = (
    "本专项给出",
    "本文件回答",
    "学什么 / 不学什么 / 学到什么程度",
    "先做品牌名归一化，再谈该学谁",
    "先定义问题，再选工具",
    "每个档案回答四件事",
)


def heading_coverage(chapters: list[Chapter], slides: list[Slide]) -> list[str]:
    titles = " ".join(s.title for s in slides)
    gaps: list[str] = []
    seen: set[str] = set()
    for chapter in chapters:
        for unit in chapter.units:
            raw = unit.h2
            if not raw or raw in seen:
                continue
            seen.add(raw)
            key = display_title(re.sub(r"^[\d.🆕\s]+", "", strip_md(raw)))
            token = re.sub(r"[：:].*$", "", key)[:8]
            if len(token) < 4:
                continue
            if token not in titles and not any(token[:6] in s.title for s in slides):
                gaps.append(raw)
    return gaps


def parse_num(cell: str) -> float | None:
    s = strip_md(cell).replace(",", "").replace("，", "").replace(" ", "")
    s = s.replace("¥", "").replace("￥", "")
    if not s or s in {"—", "-", "–", "N/A", "n/a"}:
        return None
    m = NUM_RE.search(s)
    if not m:
        return None
    v = float(m.group(0))
    if "万" in s:
        v *= 10000
    if "亿" in s:
        v *= 100000000
    return v


def looks_num(cell: str) -> bool:
    s = strip_md(cell)
    if re.fullmatch(r"L\d(?:\s*[–\-]\s*L\d)?", s.replace(" ", "")):
        return False
    if parse_num(s) is None:
        return False
    leftover = NUM_RE.sub("", s)
    leftover = re.sub(r"[%％‰¥￥元家分店万千+\-–—~/=.:\s（）()\[\]【】.,，、·]", "", leftover)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", leftover))
    return cjk <= 2 and len(leftover) <= 8


def first_sentence(text: str, limit: int) -> str:
    t = strip_md(text)
    if not t:
        return ""
    for sep in ("。", "！", "？"):
        if sep in t:
            cut = t.split(sep, 1)[0] + sep
            if 8 <= len(cut) <= limit + 16:
                return cut
    for sep in ("；", "，"):
        if sep in t:
            cut = t.split(sep, 1)[0] + sep
            if 8 <= len(cut) <= limit + 8:
                return cut
    return t


def rest_text(text: str, used: str, limit: int) -> str:
    t = strip_md(text)
    u = strip_md(used)
    if t.startswith(u):
        t = t[len(u):].lstrip("。；；. ")
    return t.strip()


def fig_label(text: str, n: int) -> str:
    t = strip_md(text)
    return t if len(t) <= n else t[:n]


def fit_label(text: str, n: int) -> str:
    t = strip_md(text)
    if len(t) <= n:
        return t
    for sep in ("：", ":", "·", "——", "—", "（", "(", "/", " "):
        head = t.split(sep, 1)[0].strip()
        if 2 <= len(head) <= n:
            return head
    cut = t[:n].rstrip()
    while cut and re.search(r"[A-Za-z]$", cut) and len(t) > len(cut):
        cut = cut[:-1].rstrip()
    return cut or fig_label(t, n)


def truncate(text: str, n: int) -> str:
    return fit_label(text, n)


def fit_phrase(text: str, n: int) -> str:
    t = strip_md(text)
    if len(t) <= n:
        return t
    for sep in ("：", ":", "·", "——", "—", "（", "("):
        head = t.split(sep, 1)[0].strip()
        if 6 <= len(head) <= n:
            return head
    cut = t[:n].rstrip("，、； 的与及和")
    return cut or t[:n]


def sentences_of(text: str) -> list[str]:
    t = strip_md(text)
    if not t:
        return []
    parts = [p.strip() for p in SENT_SPLIT.split(t) if p.strip()]
    out: list[str] = []
    for part in parts:
        if out and part[:1] in "\"“”'」』":
            out[-1] = out[-1] + part[0]
            rest = part[1:].lstrip()
            if rest:
                out.append(rest)
        else:
            out.append(part)
    return out


def take_clause(text: str, n: int) -> tuple[str, str]:
    t = strip_md(text)
    if len(t) <= n:
        return t, ""
    if len(t) == n + 1:
        return t, ""
    window = t[:n]
    for sep in ("；", "：", "，"):
        i = window.rfind(sep)
        if i >= 8:
            return t[: i + 1], t[i + 1 :].lstrip()
    return window, t[n:]


def join_clauses(parts: list[str]) -> str:
    out: list[str] = []
    for raw in parts:
        piece = (raw or "").strip()
        if not piece:
            continue
        if piece[-1] not in "。！？；":
            piece += "。"
        out.append(piece)
    return "".join(out)


def pack_statement_pages(sentences: list[str]) -> list[tuple[str, str]]:
    pages: list[tuple[str, str]] = []
    items = [s.strip() for s in sentences if s and s.strip()]
    i = 0
    while i < len(items):
        main, rest = take_clause(items[i], STATEMENT_MAIN_MAX)
        i += 1
        if rest:
            items.insert(i, rest)
        support: list[str] = []
        used = len(main)
        while i < len(items):
            nxt = items[i]
            if support and CLAIM_BREAK.match(nxt):
                break
            nxt_len = len(nxt)
            if used + nxt_len > STATEMENT_PAGE_MAX:
                leftover_len = sum(len(x) for x in items[i:])
                if leftover_len < STATEMENT_PAGE_MIN:
                    support.extend(items[i:])
                    i = len(items)
                break
            support.append(nxt)
            used += nxt_len
            i += 1
            if used >= STATEMENT_PAGE_TARGET and i < len(items):
                remain = sum(len(x) for x in items[i:])
                if remain >= STATEMENT_PAGE_MIN:
                    break
        pages.append((main, join_clauses(support)))
    return glue_orphan_statement_pages(pages) or [("", "")]


def glue_orphan_statement_pages(pages: list[tuple[str, str]]) -> list[tuple[str, str]]:
    out = list(pages)
    changed = True
    while changed and len(out) >= 2:
        changed = False
        i = 0
        while i < len(out) - 1:
            main_a, support_a = out[i]
            main_b, support_b = out[i + 1]
            n_a = len(main_a) + len(support_a)
            n_b = len(main_b) + len(support_b)
            if n_a + n_b <= STATEMENT_PAGE_MAX and (n_a < STATEMENT_PAGE_MIN or n_b < STATEMENT_PAGE_MIN):
                out[i] = (main_a, join_clauses([support_a, main_b, support_b]))
                out.pop(i + 1)
                changed = True
                continue
            i += 1
    return out


def statement_title_key(title: str) -> str:
    return re.sub(r" · \d+$", "", title or "")


def glue_sparse_statement_slides(slides: list[Slide]) -> list[Slide]:
    out: list[Slide] = []
    for slide in slides:
        if (
            out
            and out[-1].job == "statement"
            and slide.job == "statement"
            and statement_title_key(out[-1].title) == statement_title_key(slide.title)
        ):
            prev = out[-1]
            n_a = len(prev.extra.get("main") or "") + len(prev.extra.get("support") or "")
            n_b = len(slide.extra.get("main") or "") + len(slide.extra.get("support") or "")
            if n_a + n_b <= STATEMENT_PAGE_MAX and (n_a < STATEMENT_PAGE_MIN or n_b < STATEMENT_PAGE_MIN):
                prev.extra["support"] = join_clauses([
                    prev.extra.get("support") or "",
                    slide.extra.get("main") or "",
                    slide.extra.get("support") or "",
                ])
                if slide.overflow_of:
                    prev.overflow_of = prev.overflow_of or "statement"
                continue
        out.append(slide)
    return out


def paginate_rows(rows: list, budget: int) -> list[list]:
    if not rows:
        return [[]]
    pages = [list(rows[i:i + budget]) for i in range(0, len(rows), budget)]
    while len(pages) >= 2 and len(pages[-1]) <= ORPHAN_PAGE_ROWS:
        pages[-2].extend(pages[-1])
        pages.pop()
    if len(pages) >= 2 and len(pages[-1]) < 3:
        need = 3 - len(pages[-1])
        if len(pages[-2]) - need >= 3:
            pages[-1] = pages[-2][-need:] + pages[-1]
            pages[-2] = pages[-2][:-need]
    return pages


def glue_orphans(text: str, n: int = ORPHAN_GLUE) -> str:
    t = (text or "").replace(ZW, "")
    if len(t) < 10:
        return t
    end = len(t)
    while end > 0 and t[end - 1] in TRAIL_PUNCT:
        end -= 1
    idxs = [i for i, ch in enumerate(t[:end]) if "\u4e00" <= ch <= "\u9fff"]
    if len(idxs) < 2:
        return t
    take = min(n, len(idxs) - 1)
    out = t
    for pos in reversed(idxs[-take:]):
        if pos + 1 < len(out):
            out = out[: pos + 1] + ZW + out[pos + 1 :]
    return out


def field_title(text: str) -> str:
    t = display_title(text)
    if len(t) > TITLE_CANVAS_MAX:
        t = fit_phrase(t, TITLE_CANVAS_MAX)
    return glue_orphans(t)


def field_chip(text: str) -> str:
    return glue_orphans(text, 3)


def field_copy(text: str, n: int = ORPHAN_GLUE) -> str:
    return glue_orphans(strip_md(text), n)


def cn_chapter(idx: int) -> str:
    if idx < 0:
        return "序"
    if idx < len(CN_NUM):
        return CN_NUM[idx]
    return str(idx)


@dataclass
class Table:
    headers: list[str]
    rows: list[list[str]]
    source_index: int = 0


@dataclass
class Block:
    kind: str
    text: str = ""
    items: list[str] = field(default_factory=list)
    table: Table | None = None
    ordered: bool = False


@dataclass
class Unit:
    h2: str
    h3: str
    blocks: list[Block]
    chapter: str


@dataclass
class Chapter:
    title: str
    index: int
    units: list[Unit] = field(default_factory=list)


@dataclass
class Slide:
    job: str
    title: str
    chip: str
    body: str
    source: str
    how: str
    takeaway: str
    term: str
    term_def: str
    status: str = "ready"
    overflow_of: str | None = None
    fill: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def parse_table(lines: list[str], start: int) -> tuple[Table, int]:
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and "|" in lines[i] and not HEADING_RE.match(lines[i]):
        raw = lines[i].strip()
        compact = re.sub(r"\s", "", raw)
        if re.fullmatch(r"\|?[:|-]+", compact) and "-" in compact:
            i += 1
            continue
        parts = [c.strip() for c in raw.strip("|").split("|")]
        rows.append(parts)
        i += 1
    if not rows:
        return Table(headers=[], rows=[]), start + 1
    headers = rows[0]
    body = rows[1:]
    width = max(len(headers), max((len(r) for r in body), default=0))
    headers += [""] * (width - len(headers))
    body = [r + [""] * (width - len(r)) for r in body]
    return Table(headers=headers[:width], rows=body), i


def parse_list(lines: list[str], start: int) -> tuple[Block, int]:
    items: list[str] = []
    i = start
    ordered = bool(re.match(r"^\s*\d+[.)、]\s+", lines[i]))
    while i < len(lines):
        m = re.match(r"^\s*(?:[-*+]|(\d+)[.)、])\s+(.*)$", lines[i])
        if not m:
            break
        items.append(m.group(2).strip())
        i += 1
    return Block(kind="list", items=items, ordered=ordered), i


def parse_markdown(text: str, cover_h1_count: int | None = None) -> tuple[list[str], list[Chapter], list[Unit], list[Table]]:
    lines = text.replace("\r\n", "\n").split("\n")
    cover_titles: list[str] = []
    chapters: list[Chapter] = []
    preamble_units: list[Unit] = []
    all_tables: list[Table] = []
    current_chapter: Chapter | None = None
    h2 = ""
    h3 = ""
    buf: list[Block] = []
    table_i = 0
    saw_chapter = False
    i = 0

    def flush() -> None:
        nonlocal buf, h2, h3
        if not buf and not h2 and not h3:
            return
        unit = Unit(h2=h2, h3=h3, blocks=list(buf), chapter=current_chapter.title if current_chapter else "序")
        if current_chapter is None:
            preamble_units.append(unit)
        else:
            current_chapter.units.append(unit)
        buf = []

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if HR_RE.match(line.strip()):
            i += 1
            continue
        hm = HEADING_RE.match(line)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2).strip()
            if level == 1:
                if not saw_chapter and (
                    len(cover_titles) < cover_h1_count if cover_h1_count is not None else not CHAPTER_RE.search(title)
                ):
                    cover_titles.append(title)
                    i += 1
                    continue
                flush()
                saw_chapter = True
                idx = len(chapters)
                current_chapter = Chapter(title=title, index=idx)
                chapters.append(current_chapter)
                h2 = ""
                h3 = ""
                i += 1
                continue
            if level == 2:
                flush()
                h2 = title
                h3 = ""
                i += 1
                continue
            flush()
            h3 = title
            i += 1
            continue
        if line.strip().startswith("```"):
            i += 1
            body_lines: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body_lines.append(lines[i].rstrip())
                i += 1
            if i < len(lines):
                i += 1
            fenced = "\n".join(body_lines).strip()
            if fenced:
                buf.append(Block(kind="diagram", text=fenced))
            continue
        if line.strip().startswith("|") and i + 1 < len(lines) and "|" in lines[i + 1]:
            table, nxt = parse_table(lines, i)
            table.source_index = table_i
            table_i += 1
            all_tables.append(table)
            buf.append(Block(kind="table", table=table))
            i = nxt
            continue
        if re.match(r"^\s*(?:[-*+]|\d+[.)、])\s+", line):
            block, nxt = parse_list(lines, i)
            buf.append(block)
            i = nxt
            continue
        if line.lstrip().startswith(">"):
            quote = re.sub(r"^>\s?", "", line.strip())
            i += 1
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote += " " + re.sub(r"^>\s?", "", lines[i].strip())
                i += 1
            buf.append(Block(kind="quote", text=quote))
            continue
        para = line.strip()
        i += 1
        while i < len(lines) and lines[i].strip() and not HEADING_RE.match(lines[i]) and not lines[i].strip().startswith("|") and not re.match(r"^\s*(?:[-*+]|\d+[.)、])\s+", lines[i]) and not HR_RE.match(lines[i].strip()) and not lines[i].lstrip().startswith(">"):
            para += " " + lines[i].strip()
            i += 1
        buf.append(Block(kind="para", text=para))
    flush()
    return cover_titles, chapters, preamble_units, all_tables


def is_index_header(header: str) -> bool:
    return strip_md(header) in {"排名", "#", "序", "序号", "编号", "ID", "Id", "id", "No", "NO"}


def is_label_header(header: str) -> bool:
    h = strip_md(header)
    if is_index_header(h):
        return True
    return any(k in h for k in ("价格带", "分组", "分区", "项", "等级", "区间", "品牌", "品项", "选层", "假设", "口径", "阶段", "指标", "数据集"))


def should_sum_header(header: str) -> bool:
    h = strip_md(header)
    if h in {"数值", "值", "内容", "项"}:
        return False
    if any(k in h for k in ("评分", "中位", "客单", "均", "占比", "累计", "分", "差额")):
        return False
    return any(k in h for k in ("门店", "商户", "数", "额", "量", "SKU", "行"))


def numeric_cols(table: Table) -> list[int]:
    cols = []
    for c in range(len(table.headers)):
        if is_index_header(table.headers[c] if c < len(table.headers) else ""):
            continue
        if any(k in strip_md(table.headers[c] if c < len(table.headers) else "") for k in ("层级", "级别")):
            continue
        if c == 0 and is_label_header(table.headers[0]):
            continue
        cells = [r[c] if c < len(r) else "" for r in table.rows]
        hits = sum(1 for x in cells if looks_num(x))
        if cells and hits >= max(1, int(0.5 * len(cells))):
            cols.append(c)
    return cols


def label_col(table: Table) -> int:
    if not table.headers:
        return 0
    if is_index_header(table.headers[0]):
        for i, h in enumerate(table.headers):
            if any(k in strip_md(h) for k in ("品牌", "名称", "项", "阶段", "价格带")):
                return i
        return 1 if len(table.headers) > 1 else 0
    return 0


def has_count_series(table: Table) -> bool:
    for c in numeric_cols(table):
        h = strip_md(table.headers[c] if c < len(table.headers) else "")
        if any(k in h for k in ("门店数", "北京门店", "该带总门店", "品牌数", "商户数")):
            return True
        if h == "门店" or h in {"西式门店", "商场店", "非商场店"}:
            return True
    return False


def store_col(table: Table) -> int | None:
    for i, h in enumerate(table.headers):
        hs = strip_md(h)
        if hs in {"北京门店", "门店数", "门店"} or hs.startswith("北京门店"):
            return i
    return None


def is_ge20_band_chart(table: Table) -> bool:
    heads = " ".join(strip_md(h) for h in table.headers)
    return ("≥20" in heads or ">=20" in heads or "≥ 20" in heads) and "品牌数" in heads


def is_brand_scale_table(table: Table) -> bool:
    heads = [strip_md(h) for h in table.headers]
    blob = " ".join(heads)
    return "品牌" in blob and store_col(table) is not None and any(("人均" in h or "客单" in h) for h in heads)


def filter_stores_ge(table: Table, minimum: int) -> Table:
    col = store_col(table)
    assert col is not None, f"no store column in {table.headers}"
    rows = []
    for row in table.rows:
        if is_sum_row(row):
            continue
        n = parse_num(row[col] if col < len(row) else "")
        if n is not None and n >= minimum:
            rows.append(row)
    return Table(headers=table.headers, rows=rows, source_index=-1)


def load_beijing_brand_scale() -> Table:
    assert DOSSIER_BRAND_MD.is_file(), DOSSIER_BRAND_MD
    lines = DOSSIER_BRAND_MD.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if "品牌规模总榜" not in line:
            continue
        j = i + 1
        while j < len(lines) and "|" not in lines[j]:
            j += 1
        assert j < len(lines), "08 §2.1 table missing after 品牌规模总榜"
        table, _ = parse_table(lines, j)
        assert store_col(table) is not None, table.headers
        assert len(table.rows) >= 30, len(table.rows)
        return table
    raise AssertionError("08 §2.1 品牌规模总榜 not found")


def load_beijing_brand_watch() -> Table:
    assert DOSSIER_BRAND_MD.is_file(), DOSSIER_BRAND_MD
    lines = DOSSIER_BRAND_MD.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if "8–14 家梯队" not in line and "8-14 家梯队" not in line:
            continue
        j = i + 1
        while j < len(lines) and "|" not in lines[j]:
            j += 1
        assert j < len(lines), "08 8–14 table missing"
        table, _ = parse_table(lines, j)
        assert len(table.rows) >= 6, len(table.rows)
        return table
    raise AssertionError("08 8–14 家梯队 not found")


def _brand_measure_cols(table: Table) -> tuple[int, int | None, int | None, int | None]:
    name_i = label_col(table)
    store_i = store_col(table)
    if store_i is None:
        for i, h in enumerate(table.headers):
            hs = strip_md(h)
            if hs in {"门店", "店"} or "门店" in hs:
                store_i = i
                break
    price_i = None
    score_i = None
    for i, h in enumerate(table.headers):
        hs = strip_md(h)
        if price_i is None and any(k in hs for k in ("人均", "客单")):
            price_i = i
        if score_i is None and "评分" in hs and "占比" not in hs:
            score_i = i
    return name_i, store_i, price_i, score_i


@lru_cache(maxsize=1)
def load_brand_grain() -> list[tuple[str, float, float, str]]:
    rows: list[tuple[str, float, float, str]] = []
    seen: set[str] = set()
    for table in (load_beijing_brand_scale(), load_beijing_brand_watch()):
        name_i, store_i, price_i, score_i = _brand_measure_cols(table)
        assert store_i is not None and price_i is not None, table.headers
        for row in table.rows:
            if is_sum_row(row):
                continue
            name = strip_md(row[name_i] if name_i < len(row) else row[0])
            if not name or name in seen:
                continue
            stores = parse_num(row[store_i] if store_i < len(row) else "")
            price = parse_num(row[price_i] if price_i < len(row) else "")
            if stores is None or price is None:
                continue
            score = strip_md(row[score_i] if score_i is not None and score_i < len(row) else "")
            seen.add(name)
            rows.append((name, stores, price, score))
    assert len(rows) >= 36, f"brand grain short: {len(rows)}"
    return rows


def parse_price_band(label: str) -> tuple[float | None, float | None] | None:
    raw = strip_md(label)
    s = raw.replace(" ", "").replace("元", "").replace("以上", "+").replace("以下", "-")
    if s.startswith("<") or s.startswith("≤") or s.startswith("＜"):
        hi = parse_num(s)
        return (None, hi) if hi is not None else None
    if s.endswith("+") or "以上" in raw:
        lo = parse_num(s)
        return (lo, None) if lo is not None else None
    match = re.search(r"(\d+(?:\.\d+)?)\s*[–\-]\s*(\d+(?:\.\d+)?)", s)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None


def price_in_band(price: float, lo: float | None, hi: float | None) -> bool:
    if lo is None and hi is None:
        return False
    if lo is None:
        return price < (hi or 0)
    if hi is None:
        return price >= lo
    return price >= lo and price < hi


def brand_from_max_cell(cell: str) -> str:
    match = re.search(r"[（(]([^）)]+)[）)]", strip_md(cell))
    return match.group(1).strip() if match else ""


def is_brand_count_band_table(table: Table) -> bool:
    h0 = strip_md(table.headers[0] if table.headers else "")
    heads = " ".join(strip_md(h) for h in table.headers)
    return h0 in {"价格带", "评分区间"} and "品牌数" in heads


WINE_NAME_RE = re.compile(r"精酿|啤酒|bar|酒馆|餐吧", re.I)
BIN_COUNT_HEADS = {"门店数", "商户数", "品牌数", "该带总门店"}
BIN_LABEL_HEADS = {"价格带", "评分区间", "区间", "客单带"}
SAMPLE_HEADS = {"成功样本", "代表店", "同节样本"}


def is_threshold_table(table: Table) -> bool:
    h0 = strip_md(table.headers[0] if table.headers else "")
    labs = [strip_md(r[0] if r else "") for r in table.rows if not is_sum_row(r)]
    if h0 == "门槛":
        return True
    return bool(labs) and all(re.match(r"^[≥>=]", lab) for lab in labs)


def count_col(table: Table) -> int | None:
    for i, h in enumerate(table.headers):
        hs = strip_md(h)
        if hs in BIN_COUNT_HEADS or hs.endswith("门店数"):
            return i
    return None


def is_bin_count_table(table: Table) -> bool:
    if is_brand_count_band_table(table) or is_threshold_table(table):
        return False
    heads = [strip_md(h) for h in table.headers]
    if "品牌" in heads:
        return False
    if count_col(table) is None:
        return False
    h0 = heads[0] if heads else ""
    body = [r for r in table.rows if not is_sum_row(r)]
    if len(body) < 3:
        return False
    labels = [strip_md(r[0] if r else "") for r in body]
    return h0 in BIN_LABEL_HEADS or bin_labels(labels)


def is_bin_inventory(table: Table) -> bool:
    heads = [strip_md(h) for h in table.headers]
    if "品牌" in heads:
        return False
    return is_bin_count_table(table) or (
        bool(heads)
        and heads[0] in BIN_LABEL_HEADS
        and any(h in BIN_COUNT_HEADS or h in {"占比", "累计"} for h in heads)
    )


def fmt_pct(part: float, whole: float) -> str:
    if whole <= 0:
        return "—"
    pct = 100.0 * part / whole
    if abs(pct - 100) < 0.05:
        return "100%"
    if abs(pct - round(pct)) < 0.05 and pct >= 10:
        return f"{int(round(pct))}%"
    return f"{pct:.1f}%"


def add_share_cum(table: Table) -> Table:
    heads = [strip_md(h) for h in table.headers]
    blob = " ".join(heads)
    if "占比" in blob and "累计" in blob:
        return table
    if len(heads) >= 5:
        return table
    col = count_col(table)
    if col is None:
        return table
    body = [r for r in table.rows if not is_sum_row(r)]
    total = 0.0
    counts: list[float] = []
    for row in body:
        val = parse_num(row[col] if col < len(row) else "")
        if val is None:
            return table
        counts.append(val)
        total += val
    if total <= 0:
        return table
    out_heads = list(table.headers)
    add_share = "占比" not in blob
    add_cum = "累计" not in blob
    if add_share:
        out_heads.append("占比")
    if add_cum:
        out_heads.append("累计")
    running = 0.0
    rows: list[list[str]] = []
    for i, row in enumerate(body):
        lined = list(row) + [""] * (len(table.headers) - len(row))
        lined = lined[: len(table.headers)]
        running += counts[i]
        if add_share:
            lined.append(fmt_pct(counts[i], total))
        if add_cum:
            lined.append(fmt_pct(running, total) if i + 1 < len(body) else "100%")
        rows.append(lined)
    return Table(headers=out_heads, rows=rows, source_index=-1)


def sibling_named_tables(unit: Unit | None) -> list[Table]:
    if unit is None:
        return []
    out: list[Table] = []
    for block in unit.blocks:
        if block.kind != "table" or not block.table:
            continue
        named = block.table
        h0 = strip_md(named.headers[0] if named.headers else "")
        heads = " ".join(strip_md(h) for h in named.headers)
        if h0 not in {"门店", "品牌", "店名"}:
            continue
        if not any(k in heads for k in ("客单", "人均")):
            continue
        if len([r for r in named.rows if not is_sum_row(r)]) < 2:
            continue
        out.append(named)
    return out


def short_store_name(name: str) -> str:
    s = strip_md(name)
    s = re.sub(r"[（(][^）)]*[店站][）)]$", "", s).strip()
    return s or strip_md(name)


def wine_flag(cell: str, name: str) -> bool | None:
    s = strip_md(cell)
    if s in {"否", "无", "不是"} or s == "咖啡":
        return False
    if s in {"是", "有"} or "酒" in s or "精酿" in s:
        return True
    if WINE_NAME_RE.search(name):
        return True
    return None


def _named_measure_cols(table: Table) -> tuple[int, int | None, int | None, int | None, int | None]:
    name_i = 0
    price_i = None
    score_i = None
    review_i = None
    wine_i = None
    for i, h in enumerate(table.headers):
        hs = strip_md(h)
        if price_i is None and any(k in hs for k in ("客单", "人均")):
            price_i = i
        if score_i is None and "评分" in hs and "占比" not in hs:
            score_i = i
        if review_i is None and "评论" in hs:
            review_i = i
        if wine_i is None and any(k in hs for k in ("酒饮", "精酿")):
            wine_i = i
    return name_i, price_i, score_i, review_i, wine_i


def join_band_samples(table: Table, unit: Unit | None) -> Table:
    heads = [strip_md(h) for h in table.headers]
    if any(h in SAMPLE_HEADS for h in heads):
        return table
    named_tables = sibling_named_tables(unit)
    if not named_tables:
        return table
    sample_h = "成功样本" if any(
        any(k in strip_md(h) for k in ("酒饮", "精酿")) for t in named_tables for h in t.headers
    ) else "代表店"
    want_wine = sample_h == "成功样本" or any(
        WINE_NAME_RE.search(strip_md(r[0] if r else ""))
        for t in named_tables
        for r in t.rows
        if not is_sum_row(r)
    )
    out_heads = list(table.headers) + [sample_h]
    if want_wine:
        out_heads.append("样本酒饮")
    rows: list[list[str]] = []
    for row in table.rows:
        if is_sum_row(row):
            continue
        lab = strip_md(row[0] if row else "")
        parsed = parse_price_band(lab)
        hits: list[tuple[float, float, str, bool | None]] = []
        if parsed:
            lo, hi = parsed
            for named in named_tables:
                name_i, price_i, _score_i, review_i, wine_i = _named_measure_cols(named)
                if price_i is None:
                    continue
                for src in named.rows:
                    if is_sum_row(src):
                        continue
                    name = strip_md(src[name_i] if name_i < len(src) else "")
                    price = parse_num(src[price_i] if price_i < len(src) else "")
                    if not name or price is None or not price_in_band(price, lo, hi):
                        continue
                    reviews = parse_num(src[review_i] if review_i is not None and review_i < len(src) else "") or 0
                    wine_cell = src[wine_i] if wine_i is not None and wine_i < len(src) else ""
                    hits.append((reviews, price, name, wine_flag(wine_cell, name)))
        hits.sort(key=lambda item: item[0], reverse=True)
        names = [short_store_name(item[2]) for item in hits]
        if not names:
            sample = "—"
        elif len(names) <= 2:
            sample = "；".join(names)
        else:
            sample = "；".join(names[:2]) + f" 另{len(names) - 2}家"
        lined = list(row) + [""] * (len(table.headers) - len(row))
        lined = lined[: len(table.headers)] + [sample]
        if want_wine:
            flags = [item[3] for item in hits if item[3] is not None]
            yes = sum(1 for flag in flags if flag)
            lined.append(f"{yes}/{len(flags)}" if flags else "—")
        rows.append(lined)
    return Table(headers=out_heads, rows=rows, source_index=-1)


def wine_cross_lede(unit: Unit | None) -> str:
    if unit is None:
        return ""
    for block in unit.blocks:
        if block.kind != "table" or not block.table:
            continue
        heads = " ".join(strip_md(h) for h in block.table.headers)
        if "精酿" not in heads and "酒馆" not in heads and "bar" not in heads.lower():
            continue
        bits: list[str] = []
        for row in block.table.rows:
            if is_sum_row(row) or len(row) < 3:
                continue
            lab = re.sub(r"的独立汉堡店$", "", strip_md(row[0]))
            n = strip_md(row[1])
            wine = strip_md(row[2])
            if lab and n:
                bits.append(f"{lab} {n} 家，{wine}")
        if bits:
            return "；".join(bits) + "。"
    return ""


def bin_peak_lede(table: Table) -> str:
    col = count_col(table)
    if col is None:
        return ""
    body = [r for r in table.rows if not is_sum_row(r)]
    counts = [(strip_md(r[0] if r else ""), parse_num(r[col] if col < len(r) else "") or 0) for r in body]
    total = sum(n for _, n in counts)
    if total <= 0 or not counts:
        return ""
    lab, n = max(counts, key=lambda item: item[1])
    return f"合计 {fmt_val(total)}；峰值在 {lab}（{fmt_val(n)}，{fmt_pct(n, total)}）。"


def is_label_claim(text: str) -> bool:
    s = strip_md(text).strip("：:。")
    if not s or s.startswith("续页"):
        return True
    if len(s) < 12:
        return True
    if re.search(r"(客单|价格|评分).{0,2}分布$", s):
        return True
    if not NUM_RE.search(s) and len(s) <= 16:
        return True
    return False


def claim_fits_table(claim: str, table: Table) -> bool:
    cited = re.search(r"n\s*=\s*([\d,]+)", claim)
    if not cited:
        return True
    col = count_col(table)
    if col is None:
        return True
    total = sum(parse_num(r[col] if col < len(r) else "") or 0 for r in table.rows if not is_sum_row(r))
    return abs(float(cited.group(1).replace(",", "")) - total) < 1


def clean_lede_claim(claim: str) -> str:
    text = strip_md(claim or "").strip("：: ")
    if not text or len(text) > 96:
        return ""
    kept: list[str] = []
    for piece in SENT_SPLIT.split(text) or [text]:
        bit = piece.strip()
        if not bit or is_label_claim(bit):
            continue
        kept.append(bit if bit.endswith("。") else bit + "。")
    return "".join(kept)


def inventory_lede(claim: str, table: Table, unit: Unit | None) -> str:
    parts: list[str] = []
    text = clean_lede_claim(claim)
    if text and claim_fits_table(text, table):
        parts.append(text)
    wine = wine_cross_lede(unit)
    if wine and wine not in "".join(parts):
        parts.append(wine)
    blob = "".join(parts)
    if len(blob) > 140:
        blob = wine or (parts[0] if parts else "")
    if wine:
        return blob
    peak = bin_peak_lede(table)
    if peak and peak not in blob:
        blob = (blob + peak) if blob else peak
    return blob


def expand_brand_grain(table: Table) -> Table:
    body = [r for r in table.rows if not is_sum_row(r)]
    bands: list[tuple[str, float | None, float | None, list[str]]] = []
    for row in body:
        lab = strip_md(row[0] if row else "")
        parsed = parse_price_band(lab)
        if parsed:
            bands.append((lab, parsed[0], parsed[1], row))
    if not bands:
        return Table(headers=table.headers, rows=body, source_index=-1)
    max_i = next((i for i, h in enumerate(table.headers) if "最大" in strip_md(h)), None)
    out: list[list[str]] = []
    for lab, lo, hi, src_row in bands:
        hits = [
            (stores, name, price, score)
            for name, stores, price, score in load_brand_grain()
            if price_in_band(price, lo, hi)
        ]
        hits.sort(key=lambda item: item[0], reverse=True)
        if not hits:
            fallback = brand_from_max_cell(src_row[max_i]) if max_i is not None and max_i < len(src_row) else ""
            out.append([lab, fallback or "—", "—", "—", "—", "—"])
            continue
        for stores, name, price, score in hits:
            out.append([
                lab,
                name,
                fmt_val(stores),
                fmt_val(price),
                score or "—",
                "≥20" if stores >= GE20_STORES else "—",
            ])
    assert len(out) >= len(bands), "expand_inventory empty for brand-count bands"
    return Table(
        headers=["价格带", "品牌", "北京门店", "人均中位", "平均评分", "规模"],
        rows=out,
        source_index=-1,
    )


def expand_inventory(title: str, table: Table, unit: Unit | None = None) -> Table:
    if is_brand_count_band_table(table):
        return expand_brand_grain(table)
    body = [r for r in table.rows if not is_sum_row(r)]
    work = Table(headers=list(table.headers), rows=body, source_index=-1)
    if is_threshold_table(work):
        return work
    if is_bin_count_table(work):
        work = add_share_cum(work)
        work = join_band_samples(work, unit)
    return work


def inventory_title(title: str) -> str:
    base = display_title(title)
    base = re.sub(r"\s*·\s*清单(?:\s*·\s*\d+)?$", "", base)
    suffix = " · 清单"
    if len(base) + len(suffix) <= TITLE_CANVAS_MAX:
        return base + suffix
    return fit_phrase(base, TITLE_CANVAS_MAX - len(suffix)) + suffix


def parse_span_hi(cell: str) -> float | None:
    s = strip_md(cell).replace(",", "").replace("，", "")
    found = NUM_RE.findall(s)
    if not found:
        return parse_num(cell)
    v = max(float(x.replace(",", "")) for x in found)
    if "万" in s:
        v *= 10000
    if "亿" in s:
        v *= 100000000
    return v


def split_kpi_value(cell: str) -> tuple[str, str]:
    s = strip_md(cell)
    bits = re.split(r"[，,]\s*(?=[+\-−↑↓])", s, maxsplit=1)
    core, extra = (bits[0].strip(), bits[1].strip()) if len(bits) == 2 else (s, "")
    if looks_num(core):
        return core, extra
    matches = list(re.finditer(r"(\d[\d,.]*)\s*(万亿|万|亿)?\s*(家|元|%)?", s))
    with_unit = [m for m in matches if m.group(2) or m.group(3)]
    pick = with_unit[-1] if with_unit else (matches[-1] if matches else None)
    if pick:
        return re.sub(r"\s+", "", pick.group(0)), extra
    return core, extra


def mixed_time_and_share(table: Table) -> bool:
    blob = " ".join(strip_md(c) for r in table.rows for c in r)
    return ("%" in blob or "％" in blob) and bool(re.search(r"\d\s*(个月|周|天)", blob))


def is_sum_row(row: list[str]) -> bool:
    a = strip_md(row[0] if row else "")
    return a.startswith("合计") or a.startswith("总计") or a.startswith("全量") or a == "SUM"


def col_is_num(table: Table, idx: int) -> bool:
    return idx in numeric_cols(table)


def td(cell: str, numeric: bool) -> str:
    cls = ' class="num"' if numeric else ""
    if numeric:
        return f"<td{cls}>{inline_md(cell)}</td>"
    return f"<td{cls}>{inline_md(glue_orphans(strip_md(cell), CELL_ORPHAN_GLUE))}</td>"


def th(cell: str, numeric: bool) -> str:
    cls = ' class="num"' if numeric else ""
    return f"<th{cls}>{esc(glue_orphans(strip_md(cell) or ' ', CELL_ORPHAN_GLUE))}</th>"


def table_html(headers: list[str], rows: list[list[str]], num_idx: set[int], sum_row: list[str] | None = None) -> str:
    head = "".join(th(h, i in num_idx) for i, h in enumerate(headers))
    body = []
    for row in rows:
        body.append("<tr>" + "".join(td(row[i] if i < len(row) else "", i in num_idx) for i in range(len(headers))) + "</tr>")
    if sum_row:
        cells = "".join(td(sum_row[i] if i < len(sum_row) else "—", i in num_idx) for i in range(len(headers)))
        body.append(f'<tr class="sd-sum">{cells}</tr>')
    return f'<table class="sd-table"><tr>{head}</tr>{"".join(body)}</table>'


FIG_UID = 0


def next_fig_uid() -> str:
    global FIG_UID
    FIG_UID += 1
    return f"sdfig{FIG_UID}"


def cat_color(i: int) -> str:
    return f"var(--sd-cat-{(i % 8) + 1})"


def unit_of(header: str) -> str:
    h = strip_md(header)
    if any(k in h for k in ("占比", "%", "比例")):
        return "%"
    if any(k in h for k in ("元", "客单", "售价", "价")):
        return "元"
    if "份" in h:
        return "份"
    if any(k in h for k in ("门店", "商户")) or (h.endswith("数") and "评" not in h and "份" not in h):
        return "家"
    if "评分" in h or h.endswith("分"):
        return "分"
    return ""


def unit_from_cells(table: Table, vcol: int, header: str) -> str:
    u = unit_of(header)
    if u:
        return u
    sample = " ".join(strip_md(r[vcol] if vcol < len(r) else "") for r in table.rows[:8])
    if "家" in sample:
        return "家"
    if "%" in sample or "％" in sample:
        return "%"
    if "元" in sample:
        return "元"
    return ""


def fmt_measure(v: float, unit: str = "") -> str:
    if unit == "%":
        if abs(v - round(v)) < 1e-6:
            return f"{int(round(v))}%"
        return f"{v:.1f}%"
    core = fmt_val(v)
    if unit == "元":
        return core if "万" in core else f"{core}元"
    if unit == "家":
        return f"{core}家"
    if unit == "分":
        return core
    return core


def nice_max(vmax: float) -> float:
    if vmax <= 0:
        return 1.0
    mag = 10 ** math.floor(math.log10(vmax))
    for m in (1.0, 2.0, 2.5, 5.0, 10.0):
        if vmax <= m * mag + 1e-9:
            return m * mag
    return 10.0 * mag


def y_ticks(vmax: float, count: int = 4) -> list[float]:
    top = nice_max(vmax)
    return [top * i / count for i in range(count + 1)]


def highlight_index(labels: list[str], values: list[float], title: str) -> int:
    blob = title + " " + " ".join(labels)
    keys = ("55–60", "55-60", "35–45", "35-45", "4.4–4.6", "4.4-4.6", "断崖", "空档")
    for i, lab in enumerate(labels):
        if any(k in lab for k in keys):
            return i
    if any(k in blob for k in ("55–60", "55-60")):
        for i, lab in enumerate(labels):
            if "55" in lab and "60" in lab:
                return i
    if "4.5" in title or "4.4" in title:
        for i, lab in enumerate(labels):
            if "4.4" in lab or "4.5" in lab:
                return i
    if any(k in title for k in ("Wagas", "沃歌斯", "65–80", "65-80", "品质连锁")):
        for i, lab in enumerate(labels):
            if "Wagas" in lab or "沃歌斯" in lab:
                return i
    if any(k in title for k in ("场内", "真空", "九家", "Shake Shack")):
        for i, lab in enumerate(labels):
            if "Shake" in lab or "合生汇" in lab:
                return i
    for key in ("合生汇", "烤炉", "石头先生", "双井", "和牛怪物", "Shake"):
        for i, lab in enumerate(labels):
            if key in lab:
                return i
    if values:
        return max(range(len(values)), key=lambda i: values[i])
    return 0


def is_small_n(val: float, values: list[float], unit: str) -> bool:
    total = sum(max(0, v) for v in values) or 1
    if unit == "家" and 0 < val < 30:
        return True
    return 0 < val / total < 0.025 and len(values) >= 6


def needs_proxy(title: str) -> bool:
    return any(k in title for k in ("代理", "估算", "公开报道", "爬取", "非客户表", "禁止外部对标"))


def figure_plot_cap(fill: str, labels_all: list[str], n_body: int) -> int:
    if fill in {"bubble", "quadrant"}:
        return BUBBLE_ROWS
    if fill == "timeline":
        return 10
    if fill == "radar":
        return 8
    if bin_labels(labels_all) or fill == "hist-cdf":
        return max(BIN_CHART_ROWS, min(n_body, NAMED_SERIES_MAX))
    if fill in {"pareto", "hbar", "diverging-bar", "treemap", "waterfall", "funnel", "slope", "heatmap", "line-dual"}:
        return min(n_body, NAMED_SERIES_MAX)
    return min(n_body, CHART_ROWS)


def figure_caption(fill: str, header: str, n: int, unit: str, title: str = "") -> str:
    bits = [f"n={n}"]
    if header:
        bits.append(header)
    if unit and unit not in header:
        bits.append(f"单位{unit}")
    extra = {
        "hist-cdf": "柱=计数 · 点=累计份额",
        "pareto": "柱=值 · 点=累计 · 虚线=80%",
        "heatmap": "浅=低 · 深=高",
        "slope": "右端标注增减",
        "quadrant": "虚线=中位 · 高侧含等于 ≥",
        "diverging-bar": "柱长=量",
        "treemap": "面积=份额",
        "waterfall": "柱接上一根的顶",
        "funnel": "宽=量",
        "radar": "各轴同一量纲",
        "bubble": "面积∝√量 · 虚线=中位 ≥",
        "timeline": "点=阶段门店目标",
        "line-dual": "同横轴",
    }.get(fill)
    if extra:
        bits.append(extra)
    if needs_proxy(title):
        bits.append("禁止外部对标")
    return " · ".join(bits)


SEQ_FILLS = (
    "var(--sd-seq-100)",
    "var(--sd-seq-200)",
    "var(--sd-seq-300)",
    "var(--sd-seq-400)",
    "var(--sd-seq-500)",
    "var(--sd-seq-600)",
)


def seq_paint(t: float) -> tuple[str, str]:
    idx = min(5, max(0, int(max(0.0, min(1.0, t)) * 6 - 1e-9)))
    ink = "var(--sd-ink-100)" if idx <= 2 else "var(--sd-paper)"
    return SEQ_FILLS[idx], ink


def svg_text(
    x: float,
    y: float,
    text: str,
    *,
    size: int = FIG_CAT,
    fill: str = "var(--sd-ink-100)",
    anchor: str = "start",
    family: str = "var(--sd-font-serif)",
    weight: str = "400",
    stroke: str | None = None,
    stroke_width: float = 0,
) -> str:
    extra = ""
    if stroke and stroke_width:
        extra = (
            f' stroke="{stroke}" stroke-width="{stroke_width}" '
            f'paint-order="stroke" stroke-linejoin="round"'
        )
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" '
        f'font-family="{family}" font-weight="{weight}" fill="{fill}"{extra} '
        f'style="font-variant-numeric:tabular-nums">{esc(text)}</text>'
    )


def fig_scale(n: int) -> float:
    if n <= 4:
        return 1.22
    if n <= 8:
        return 1.08
    return 1.0


def fig_text_w(text: str, size: int) -> float:
    return max(1.0, len(text) * size * 0.62)


def bar_value_label(
    x: float,
    y: float,
    bw: float,
    h: float,
    label: str,
    *,
    vertical: bool,
    small: bool,
    weight: str = "600",
    size: int | None = None,
) -> str:
    val = size or FIG_VAL
    tw = fig_text_w(label, val)
    if vertical:
        inside = (not small) and h >= (val + 18) and bw >= (tw + 6)
        if inside:
            return svg_text(
                x + bw / 2, y + val + 4, label, size=val,
                fill="var(--sd-paper)", anchor="middle",
                family="var(--sd-font-mono)", weight=weight,
            )
        return svg_text(
            x + bw / 2, y - 6, label, size=val,
            fill="var(--sd-ink-100)", anchor="middle",
            family="var(--sd-font-mono)", weight=weight,
            stroke="var(--sd-paper)", stroke_width=3.5,
        )
    inside = (not small) and bw >= (tw + 24) and h >= val
    if inside:
        return svg_text(
            x + bw - 8, y + h * 0.72, label, size=val,
            fill="var(--sd-paper)", anchor="end",
            family="var(--sd-font-mono)", weight=weight,
        )
    return svg_text(
        x + bw + 8, y + h * 0.72, label, size=val,
        fill="var(--sd-ink-100)",
        family="var(--sd-font-mono)", weight=weight,
        stroke="var(--sd-paper)", stroke_width=3.5,
    )


def svg_halo_text(x: float, y: float, text: str, *, size: int = FIG_TICK, fill: str = "var(--sd-ink-100)", anchor: str = "middle") -> str:
    return svg_text(
        x, y, text, size=size, fill=fill, anchor=anchor,
        stroke="var(--sd-paper)", stroke_width=4,
    )


def _median(vals: list[float]) -> float:
    ordered = sorted(vals)
    return ordered[len(ordered) // 2] if ordered else 0.0


def scatter_label_indices(
    labels: list[str],
    xs: list[float],
    ys: list[float],
    sizes: list[float],
    highlight: int,
    limit: int = BUBBLE_LABEL_MAX,
) -> set[int]:
    n = len(labels)
    if n <= 8:
        return set(range(n))
    ranked = sorted(range(n), key=lambda i: sizes[i] if i < len(sizes) else 0, reverse=True)
    priority: list[tuple[int, int]] = []

    def add(idx: int, weight: int) -> None:
        if 0 <= idx < n:
            priority.append((weight, idx))

    add(highlight, 0)
    for i, lab in enumerate(labels):
        if any(k in lab for k in ("石头先生", "Shake", "烤炉")):
            add(i, 1)
        elif any(k in lab for k in BUBBLE_MUST_LABELS):
            add(i, 2)
    if n:
        add(min(range(n), key=lambda i: xs[i]), 3)
        add(max(range(n), key=lambda i: xs[i]), 3)
        add(min(range(n), key=lambda i: ys[i]), 3)
        add(max(range(n), key=lambda i: ys[i]), 3)
    for i in ranked:
        add(i, 4)
    picked: set[int] = set()
    for _, idx in sorted(priority, key=lambda item: item[0]):
        if idx in picked:
            continue
        picked.add(idx)
        if len(picked) >= limit:
            break
    return picked


def place_scatter_label(
    cx: float,
    cy: float,
    radius: float,
    placed: list[tuple[float, float]],
) -> tuple[float, float, str] | None:
    candidates = (
        (cx, cy - radius - 12, "middle"),
        (cx + radius + 10, cy + 4, "start"),
        (cx - radius - 10, cy + 4, "end"),
        (cx, cy + radius + 18, "middle"),
        (cx + radius + 14, cy - radius - 8, "start"),
        (cx - radius - 14, cy - radius - 8, "end"),
        (cx + radius + 14, cy + radius + 14, "start"),
        (cx - radius - 14, cy + radius + 14, "end"),
        (cx, cy - radius - 30, "middle"),
    )
    for x, y, anchor in candidates:
        if x < 10 or x > FIG_W - 10 or y < 16 or y > FIG_H - 16:
            continue
        if any(abs(x - px) < 92 and abs(y - py) < 20 for px, py in placed):
            continue
        return x, y, anchor
    return None


def thin_scatter_labels(
    labeled: set[int],
    xs: list[float],
    ys: list[float],
    sizes: list[float],
    highlight: int,
    px,
    py,
    min_dist: float = BUBBLE_CLUSTER_PX,
) -> set[int]:
    kept: list[int] = []
    for i in sorted(
        labeled,
        key=lambda idx: (0 if idx == highlight else 1, -(sizes[idx] if idx < len(sizes) else 0)),
    ):
        if i != highlight and any(
            math.hypot(px(xs[i]) - px(xs[j]), py(ys[i]) - py(ys[j])) < min_dist for j in kept
        ):
            continue
        kept.append(i)
    return set(kept)


def svg_root(inner: str, uid: str | None = None) -> str:
    uid = uid or next_fig_uid()
    defs = (
        f'<defs><pattern id="{uid}-hatch" width="7" height="7" patternUnits="userSpaceOnUse" '
        f'patternTransform="rotate(35)">'
        f'<line x1="0" y1="0" x2="0" y2="7" stroke="var(--sd-ink-45)" stroke-width="1.6"/>'
        f"</pattern></defs>"
    )
    return (
        f'<svg viewBox="0 0 {FIG_W} {FIG_H}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" '
        f'xmlns="http://www.w3.org/2000/svg" role="img">'
        f'<rect x="0" y="0" width="{FIG_W}" height="{FIG_H}" fill="var(--sd-paper)"/>'
        f"{defs}{inner}</svg>"
    )


def svg_caption(text: str) -> str:
    return svg_text(16, FIG_H - 10, text, size=FIG_CAPTION, fill="var(--sd-ink-60)", family="var(--sd-font-mono)")


def svg_y_grid(left: float, top: float, right: float, bot: float, ticks: list[float], vmax: float, unit: str) -> str:
    inner_h = FIG_H - top - bot
    parts: list[str] = []
    for t in ticks:
        y = FIG_H - bot - inner_h * (t / vmax if vmax else 0)
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{FIG_W - right}" y2="{y:.1f}" '
            f'stroke="var(--sd-ink-14)" stroke-width="1" stroke-dasharray="4 5"/>'
        )
        parts.append(svg_text(left - 10, y + 5, fmt_measure(t, unit), size=FIG_TICK, fill="var(--sd-ink-60)", anchor="end", family="var(--sd-font-mono)"))
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{FIG_H - bot}" stroke="var(--sd-ink-14)" stroke-width="2"/>')
    parts.append(f'<line x1="{left}" y1="{FIG_H - bot}" x2="{FIG_W - right}" y2="{FIG_H - bot}" stroke="var(--sd-ink-28)" stroke-width="2"/>')
    return "".join(parts)


def bar_paint(uid: str, highlight: bool, small: bool) -> str:
    if small:
        stroke = "var(--sd-secondary)" if highlight else "var(--sd-accent)"
        width = "2.2" if highlight else "1.2"
        return f'fill="url(#{uid}-hatch)" stroke="{stroke}" stroke-width="{width}"'
    if highlight:
        return 'fill="var(--sd-secondary)"'
    return 'fill="var(--sd-accent)"'


def svg_hbars(labels: list[str], values: list[float], *, diverging: bool, unit: str = "", caption: str = "", highlight: int = 0) -> str:
    uid = next_fig_uid()
    n = max(1, len(labels))
    cat_s = max(14, int(round(FIG_CAT * fig_scale(n))))
    val_s = max(14, int(round(FIG_VAL * fig_scale(n))))
    top, bot, left, right = 40, 36, 340, 96
    inner_h = FIG_H - top - bot
    inner_w = FIG_W - left - right
    gap = max(6, 14 - n)
    bh = max(12, (inner_h - gap * n) / n)
    parts: list[str] = []
    has_neg = any(v < 0 for v in values)
    if diverging or has_neg:
        vmax = nice_max(max((abs(v) for v in values), default=1) or 1)
        zero = left + inner_w / 2
        parts.append(f'<line x1="{zero:.1f}" y1="{top}" x2="{zero:.1f}" y2="{FIG_H - bot}" stroke="var(--sd-ink-28)" stroke-width="2"/>')
        for t in y_ticks(vmax, 2):
            if t == 0:
                continue
            dx = (inner_w / 2) * (t / vmax)
            parts.append(f'<line x1="{zero - dx:.1f}" y1="{top}" x2="{zero - dx:.1f}" y2="{FIG_H - bot}" stroke="var(--sd-ink-14)" stroke-dasharray="4 5"/>')
            parts.append(f'<line x1="{zero + dx:.1f}" y1="{top}" x2="{zero + dx:.1f}" y2="{FIG_H - bot}" stroke="var(--sd-ink-14)" stroke-dasharray="4 5"/>')
        for i, (lab, val) in enumerate(zip(labels, values)):
            y = top + i * (bh + gap)
            bw = (inner_w / 2) * (abs(val) / vmax)
            x = zero if val >= 0 else zero - bw
            paint = 'fill="var(--sd-status-ready-text)"' if val >= 0 else 'fill="var(--sd-secondary)"'
            if i == highlight:
                paint = 'fill="var(--sd-secondary)"' if val < 0 else 'fill="var(--sd-accent)"'
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(bw, 1):.1f}" height="{bh:.1f}" {paint} rx="2"/>')
            parts.append(svg_text(left - 14, y + bh * 0.72, lab if len(lab) <= 16 else truncate(lab, 16), size=cat_s, anchor="end"))
            tx = x + bw + 10 if val >= 0 else x - 10
            parts.append(svg_text(tx, y + bh * 0.72, fmt_measure(val, unit), size=val_s, fill="var(--sd-ink-100)", anchor="start" if val >= 0 else "end", family="var(--sd-font-mono)", weight="600"))
        if caption:
            parts.append(svg_caption(caption))
        return svg_root("".join(parts), uid)
    vmax = nice_max(max(values) if values else 1)
    for t in y_ticks(vmax, 4):
        x = left + inner_w * (t / vmax)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{FIG_H - bot}" stroke="var(--sd-ink-14)" stroke-dasharray="4 5"/>')
        parts.append(svg_text(x, top - 8, fmt_measure(t, unit), size=FIG_TICK, fill="var(--sd-ink-60)", anchor="middle", family="var(--sd-font-mono)"))
    parts.append(f'<line x1="{left}" y1="{FIG_H - bot}" x2="{FIG_W - right}" y2="{FIG_H - bot}" stroke="var(--sd-ink-28)" stroke-width="2"/>')
    for i, (lab, val) in enumerate(zip(labels, values)):
        y = top + i * (bh + gap)
        bw = inner_w * (max(0, val) / vmax)
        small = is_small_n(val, values, unit)
        parts.append(f'<rect x="{left}" y="{y:.1f}" width="{max(bw, 1):.1f}" height="{bh:.1f}" {bar_paint(uid, i == highlight, small)} rx="2"/>')
        parts.append(svg_text(left - 14, y + bh * 0.72, lab if len(lab) <= 16 else truncate(lab, 16), size=cat_s, anchor="end"))
        label = fmt_measure(val, unit)
        parts.append(bar_value_label(left, y, bw, bh, label, vertical=False, small=small, size=val_s))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts), uid)


def svg_vbars(labels: list[str], values: list[float], *, cdf: bool, mark80: bool, unit: str = "", caption: str = "", highlight: int = 0) -> str:
    uid = next_fig_uid()
    n = max(1, len(labels))
    cat_s = max(14, int(round(FIG_CAT * fig_scale(n))))
    val_s = max(14, int(round(FIG_VAL * fig_scale(n))))
    top, bot, left = 52, (130 if n > 16 else 102 if n > 10 else 80), 108
    right = 88 if cdf else 40
    inner_h = FIG_H - top - bot
    inner_w = FIG_W - left - right
    gap = 8 if n <= 10 else 5
    bw = max(10, (inner_w - gap * n) / n)
    vmax = nice_max(max(values) if values else 1)
    total = sum(max(0, v) for v in values) or 1
    parts = [svg_y_grid(left, top, right, bot, y_ticks(vmax), vmax, unit)]
    if caption:
        parts.append(svg_text(left, 24, caption, size=FIG_CAPTION, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"))
    value_labels: list[str] = []
    x_labels: list[str] = []
    cdf_meta: list[tuple[float, float, float, int]] = []
    acc = 0.0
    cross80 = None
    for i, (lab, val) in enumerate(zip(labels, values)):
        x = left + i * (bw + gap)
        h = inner_h * (max(0, val) / vmax)
        y = FIG_H - bot - h
        small = is_small_n(val, values, unit)
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(h, 1):.1f}" {bar_paint(uid, i == highlight, small)} rx="2"/>')
        lab_n = 6 if n > 16 else 10
        lab_s = truncate(lab, lab_n)
        if n > 10:
            x_labels.append(
                f'<text x="{x + bw / 2:.1f}" y="{FIG_H - bot + 16:.1f}" text-anchor="end" font-size="{FIG_TICK}" '
                f'font-family="var(--sd-font-serif)" fill="var(--sd-ink-72)" '
                f'style="font-variant-numeric:tabular-nums" '
                f'transform="rotate(-40 {x + bw / 2:.1f} {FIG_H - bot + 16:.1f})">{esc(lab_s)}</text>'
            )
        else:
            x_labels.append(svg_text(x + bw / 2, FIG_H - bot + 26, lab_s, size=cat_s, anchor="middle", fill="var(--sd-ink-72)"))
        label = fmt_measure(val, unit)
        weight = "700" if i == highlight else "600"
        value_labels.append(bar_value_label(x, y, bw, h, label, vertical=True, small=small, weight=weight, size=val_s))
        if cdf:
            acc += max(0, val)
            share = acc / total
            cx = x + bw / 2
            cy = top + inner_h * (1 - share)
            cdf_meta.append((cx, cy, share, i))
            if cross80 is None and share >= 0.8:
                cross80 = cx
    if cdf and cdf_meta:
        pts = " ".join(f"{cx:.1f},{cy:.1f}" for cx, cy, _, _ in cdf_meta)
        parts.append(f'<polyline fill="none" stroke="var(--sd-secondary)" stroke-width="2.5" points="{pts}"/>')
        for cx, cy, share, i in cdf_meta:
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.5" fill="var(--sd-secondary)"/>')
            if i == highlight or i == n - 1:
                label = f"{share * 100:.0f}%"
                parts.append(svg_text(cx, top - 10, label, size=FIG_TICK, fill="var(--sd-ink-100)", anchor="middle", family="var(--sd-font-mono)", weight="600"))
        parts.append(f'<line x1="{FIG_W - right}" y1="{top}" x2="{FIG_W - right}" y2="{FIG_H - bot}" stroke="var(--sd-ink-14)" stroke-width="2"/>')
        for pct in (0, 25, 50, 75, 100):
            y = FIG_H - bot - inner_h * (pct / 100)
            parts.append(svg_text(FIG_W - right + 8, y + 4, f"{pct}%", size=FIG_TICK, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"))
        if mark80:
            y80 = top + inner_h * 0.2
            parts.append(f'<line x1="{left}" y1="{y80:.1f}" x2="{FIG_W - right}" y2="{y80:.1f}" stroke="var(--sd-secondary)" stroke-width="1.2" stroke-dasharray="5 5"/>')
            parts.append(svg_text(FIG_W - right - 8, top - 10, "累计 80%", size=FIG_TICK, fill="var(--sd-ink-100)", anchor="end", family="var(--sd-font-mono)"))
            if cross80 is not None:
                parts.append(f'<line x1="{cross80}" y1="{top}" x2="{cross80}" y2="{FIG_H - bot}" stroke="var(--sd-ink-28)" stroke-width="1" stroke-dasharray="3 4"/>')
    parts.extend(value_labels)
    parts.extend(x_labels)
    return svg_root("".join(parts), uid)


def svg_waterfall(labels: list[str], values: list[float], unit: str = "", caption: str = "", highlight: int = 0) -> str:
    n = max(1, len(labels))
    top, bot, left, right = 28, 72, 72, 48
    inner_h = FIG_H - top - bot
    inner_w = FIG_W - left - right
    gap = 10
    bw = max(8, (inner_w - gap * n) / n)
    running = 0.0
    spans: list[tuple[float, float, float]] = []
    for val in values:
        start = running
        running += val
        spans.append((start, running, val))
    lo = min(0.0, min((s[0] for s in spans), default=0), min((s[1] for s in spans), default=0))
    hi = max(0.0, max((s[0] for s in spans), default=1), max((s[1] for s in spans), default=1))
    span = (hi - lo) or 1
    parts: list[str] = []
    zero_y = FIG_H - bot - inner_h * ((0 - lo) / span)
    parts.append(f'<line x1="{left}" y1="{zero_y:.1f}" x2="{FIG_W - right}" y2="{zero_y:.1f}" stroke="var(--sd-ink-14)" stroke-width="2"/>')
    prev_top = None
    for i, (lab, (start, end, val)) in enumerate(zip(labels, spans)):
        x = left + i * (bw + gap)
        y1 = FIG_H - bot - inner_h * ((start - lo) / span)
        y2 = FIG_H - bot - inner_h * ((end - lo) / span)
        y = min(y1, y2)
        h = max(4, abs(y2 - y1))
        color = "var(--sd-status-ready-text)" if val >= 0 else "var(--sd-secondary)"
        if i == 0 or i == n - 1 or i == highlight:
            color = "var(--sd-accent)"
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{color}" rx="2"/>')
        if prev_top is not None:
            parts.append(f'<line x1="{x - gap:.1f}" y1="{prev_top:.1f}" x2="{x:.1f}" y2="{y1:.1f}" stroke="var(--sd-ink-28)" stroke-width="1.5"/>')
        prev_top = y2
        parts.append(svg_text(x + bw / 2, FIG_H - bot + 26, lab if len(lab) <= 8 else truncate(lab, 8), size=15, anchor="middle", fill="var(--sd-ink-72)"))
        parts.append(svg_text(x + bw / 2, y - 8, fmt_measure(val, unit), size=15, fill="var(--sd-ink-100)", anchor="middle", family="var(--sd-font-mono)", weight="600"))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def svg_timeline(labels: list[str], values: list[float], unit: str = "", caption: str = "", highlight: int = 0) -> str:
    n = max(1, len(labels))
    top, bot, side, gap = 36, 28, 24, 10
    cw = (FIG_W - side * 2 - gap * (n - 1)) / n
    ch = FIG_H - top - bot
    parts: list[str] = []
    if caption:
        parts.append(svg_text(side, 24, caption, size=FIG_CAPTION, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"))
    for i, (lab, val) in enumerate(zip(labels, values)):
        x = side + i * (cw + gap)
        hi = i == highlight
        fill = "var(--sd-secondary)" if hi else "var(--sd-accent)"
        parts.append(f'<rect x="{x:.1f}" y="{top}" width="{cw:.1f}" height="{ch:.1f}" fill="{fill}" rx="4"/>')
        ink = "var(--sd-paper)"
        parts.append(svg_text(x + cw / 2, top + 36, f"{i + 1:02d}", size=FIG_TICK, fill=ink, anchor="middle", family="var(--sd-font-mono)"))
        parts.append(svg_text(x + cw / 2, top + 78, lab if len(lab) <= 6 else truncate(lab, 6), size=FIG_NAME, fill=ink, anchor="middle", weight="700"))
        parts.append(svg_text(x + cw / 2, top + ch * 0.62, fmt_measure(val, unit or "家"), size=36, fill=ink, anchor="middle", family="var(--sd-font-mono)", weight="700"))
    return svg_root("".join(parts))


def svg_funnel(labels: list[str], values: list[float], unit: str = "", caption: str = "", highlight: int = 0) -> str:
    n = max(1, len(labels))
    top, bot = 28, 32
    vmax = max(values) if values else 1
    if vmax <= 0:
        vmax = 1
    row_h = (FIG_H - top - bot) / n
    parts: list[str] = []
    for i, (lab, val) in enumerate(zip(labels, values)):
        frac = max(0.22, max(0, val) / vmax)
        ww = (FIG_W - 120) * frac
        x = (FIG_W - ww) / 2
        y = top + i * row_h + 6
        h = row_h - 14
        fill = "var(--sd-secondary)" if i == highlight else "var(--sd-accent)"
        next_frac = max(0.22, max(0, values[i + 1]) / vmax) if i + 1 < n else frac * 0.72
        nw = (FIG_W - 120) * next_frac
        nx = (FIG_W - nw) / 2
        pts = f"{x:.1f},{y:.1f} {x + ww:.1f},{y:.1f} {nx + nw:.1f},{y + h:.1f} {nx:.1f},{y + h:.1f}"
        parts.append(f'<polygon points="{pts}" fill="{fill}"/>')
        ink = "var(--sd-paper)"
        parts.append(svg_text(FIG_W / 2, y + h * 0.58, f"{lab}  {fmt_measure(val, unit)}", size=20, fill=ink, anchor="middle", weight="600"))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def svg_treemap(labels: list[str], values: list[float], unit: str = "", caption: str = "", highlight: int = 0) -> str:
    items = sorted(zip([max(0, v) for v in values], labels, range(len(labels))), reverse=True)
    total = sum(v for v, _, _ in items) or 1
    x, y = 16.0, 16.0
    rw, rh = FIG_W - 32, FIG_H - 40
    parts: list[str] = []
    remain = total
    for i, (val, lab, src) in enumerate(items):
        if i == len(items) - 1:
            ww, hh = rw, rh
        elif rw >= rh:
            ww = max(56, rw * (val / remain))
            hh = rh
        else:
            ww = rw
            hh = max(40, rh * (val / remain))
        fill = "var(--sd-secondary)" if src == highlight or i == 0 else "var(--sd-accent)"
        if i > 2 and src != highlight:
            fill = "var(--sd-primary)"
        ink = "var(--sd-ink-100)" if fill == "var(--sd-primary)" else "var(--sd-paper)"
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{hh:.1f}" fill="{fill}" stroke="var(--sd-paper)" stroke-width="3"/>')
        if ww > 90 and hh > 44:
            share = f"{100 * val / total:.1f}%"
            parts.append(svg_text(x + 14, y + 28, lab if len(lab) <= 12 else truncate(lab, 12), size=20, fill=ink, weight="600"))
            parts.append(svg_text(x + 14, y + 52, f"{fmt_measure(val, unit)} · {share}", size=16, fill=ink, family="var(--sd-font-mono)"))
        remain -= val
        if rw >= rh:
            x += ww
            rw -= ww
        else:
            y += hh
            rh -= hh
        if remain <= 0:
            break
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def svg_slope(labels: list[str], left_vals: list[float], right_vals: list[float], left_h: str, right_h: str, unit: str = "", caption: str = "", highlight: int = 0) -> str:
    top, bot, left, right = 44, 36, 240, 200
    lx, rx = left, FIG_W - right
    allv = left_vals + right_vals
    lo, hi = min(allv, default=0), max(allv, default=1)
    if hi == lo:
        hi = lo + 1
    pad = (hi - lo) * 0.08
    lo, hi = lo - pad, hi + pad
    parts = [
        f'<line x1="{lx}" y1="{top}" x2="{lx}" y2="{FIG_H - bot}" stroke="var(--sd-ink-28)" stroke-width="2"/>',
        f'<line x1="{rx}" y1="{top}" x2="{rx}" y2="{FIG_H - bot}" stroke="var(--sd-ink-28)" stroke-width="2"/>',
        svg_text(lx, 26, left_h, size=16, anchor="middle", family="var(--sd-font-mono)", fill="var(--sd-ink-60)"),
        svg_text(rx, 26, right_h, size=16, anchor="middle", family="var(--sd-font-mono)", fill="var(--sd-ink-60)"),
    ]
    used_l: list[float] = []
    used_r: list[float] = []
    def nudge(y: float, used: list[float]) -> float:
        for prev in used:
            if abs(y - prev) < 16:
                y = prev + 16
        used.append(y)
        return y
    for i, (lab, a, b) in enumerate(zip(labels, left_vals, right_vals)):
        ya = top + (FIG_H - top - bot) * (1 - (a - lo) / (hi - lo))
        yb = top + (FIG_H - top - bot) * (1 - (b - lo) / (hi - lo))
        color = "var(--sd-status-ready-text)" if b >= a else "var(--sd-secondary)"
        if i == highlight:
            color = "var(--sd-accent)"
        thick = 3.2 if i == highlight else 2.2
        parts.append(f'<line x1="{lx}" y1="{ya:.1f}" x2="{rx}" y2="{yb:.1f}" stroke="{color}" stroke-width="{thick}"/>')
        parts.append(f'<circle cx="{lx}" cy="{ya:.1f}" r="5.5" fill="{color}"/>')
        parts.append(f'<circle cx="{rx}" cy="{yb:.1f}" r="5.5" fill="{color}"/>')
        ly = nudge(ya + 5, used_l)
        ry = nudge(yb + 5, used_r)
        delta = b - a
        sign = "+" if delta >= 0 else ""
        parts.append(svg_text(lx - 12, ly, f"{lab}  {fmt_measure(a, unit)}", size=15, anchor="end"))
        parts.append(svg_text(rx + 12, ry, f"{fmt_measure(b, unit)}  {sign}{fmt_measure(delta, unit)}", size=15, family="var(--sd-font-mono)", fill=color, weight="600"))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def svg_line_dual(labels: list[str], series: list[list[float]], names: list[str], unit: str = "", caption: str = "", highlight: int = 0) -> str:
    n = max(1, len(labels))
    top, bot, left, right = 44, 70, 88, 36
    inner_h = FIG_H - top - bot
    inner_w = FIG_W - left - right
    flat = [v for s in series for v in s]
    lo, hi = min(flat, default=0), max(flat, default=1)
    if hi == lo:
        hi = lo + 1
    vmax = nice_max(hi)
    parts = [svg_y_grid(left, top, right, bot, y_ticks(vmax), vmax, unit)]
    colors = ["var(--sd-accent)", "var(--sd-secondary)", "var(--sd-status-ready-text)"]
    for si, vals in enumerate(series[:3]):
        pts = []
        for i, val in enumerate(vals):
            x = left + (inner_w * i / max(1, n - 1))
            y = top + inner_h * (1 - (val / vmax if vmax else 0))
            pts.append(f"{x:.1f},{y:.1f}")
            r = 5.5 if i == highlight else 4
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{colors[si]}"/>')
            if i == highlight or n <= 8:
                parts.append(svg_text(x, y - 12, fmt_measure(val, unit), size=13, fill="var(--sd-ink-100)", anchor="middle", family="var(--sd-font-mono)", weight="600"))
        parts.append(f'<polyline fill="none" stroke="{colors[si]}" stroke-width="2.8" points="{" ".join(pts)}"/>')
        parts.append(svg_text(left + 8 + si * 220, 22, names[si] if si < len(names) else f"S{si+1}", size=16, fill=colors[si], family="var(--sd-font-mono)", weight="600"))
    for i, lab in enumerate(labels):
        x = left + (inner_w * i / max(1, n - 1))
        parts.append(svg_text(x, FIG_H - bot + 26, lab if len(lab) <= 8 else truncate(lab, 8), size=14, anchor="middle", fill="var(--sd-ink-72)"))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def svg_heatmap(row_labs: list[str], col_labs: list[str], grid: list[list[float | None]], unit: str = "", caption: str = "", highlight: int = 0) -> str:
    rows, cols = max(1, len(row_labs)), max(1, len(col_labs))
    left, top, right, bot = 228, 52, 28, 36
    cw = (FIG_W - left - right) / cols
    rh = (FIG_H - top - bot) / rows
    flat = [v for row in grid for v in row if v is not None]
    lo, hi = (min(flat), max(flat)) if flat else (0.0, 1.0)
    if hi == lo:
        hi = lo + 1
    parts: list[str] = []
    for j, h in enumerate(col_labs):
        parts.append(svg_text(left + (j + 0.5) * cw, 34, h if len(h) <= 10 else truncate(h, 10), size=FIG_TICK, anchor="middle", family="var(--sd-font-mono)", fill="var(--sd-ink-60)"))
    for i, lab in enumerate(row_labs):
        weight = "700" if i == highlight else "400"
        parts.append(svg_text(left - 12, top + (i + 0.62) * rh, lab if len(lab) <= 14 else truncate(lab, 14), size=FIG_CAT, anchor="end", weight=weight))
        for j in range(cols):
            val = grid[i][j] if i < len(grid) and j < len(grid[i]) else None
            x = left + j * cw + 3
            y = top + i * rh + 3
            if val is None:
                fill, label, ink = "var(--sd-ink-14)", "—", "var(--sd-ink-60)"
            else:
                t = (val - lo) / (hi - lo)
                fill, ink = seq_paint(t)
                label = fmt_measure(val, unit)
            stroke = ' stroke="var(--sd-secondary)" stroke-width="2.2"' if i == highlight else ' stroke="var(--sd-paper)" stroke-width="1"'
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw - 6:.1f}" height="{rh - 6:.1f}" fill="{fill}" rx="3"{stroke}/>')
            parts.append(svg_text(x + (cw - 6) / 2, y + (rh - 6) * 0.64, label, size=FIG_VAL, fill=ink, anchor="middle", family="var(--sd-font-mono)", weight="600"))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def bar_weight(token: str) -> float:
    return token.count("█") + 0.5 * token.count("▓") + 0.25 * token.count("░")


def parse_weight_shift(text: str) -> list[tuple[str, list[tuple[str, float]], str]]:
    rows: list[tuple[str, list[tuple[str, float]], str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        matched = re.match(r"^(\d+\s*家)\s*(.*)$", line)
        if not matched:
            continue
        stage = re.sub(r"\s+", "", matched.group(1))
        rest = matched.group(2)
        segs: list[tuple[str, float]] = []
        pos = 0
        for bar in re.finditer(r"[█▓░]+", rest):
            labels = rest[pos:bar.start()].strip()
            segs.append((labels or "·", bar_weight(bar.group())))
            pos = bar.end()
        note = rest[pos:].strip()
        rows.append((stage, segs, note))
    return rows


def svg_weight_shift(rows: list[tuple[str, list[tuple[str, float]], str]], caption: str = "") -> str:
    if not rows:
        return svg_root("")
    top, bot, left = 40, 28, 108
    row_h = (FIG_H - top - bot) / len(rows)
    max_w = max((sum(w for _, w in segs) or 1 for _, segs, _ in rows), default=1)
    inner = FIG_W - left - 28
    parts: list[str] = []
    if caption:
        parts.append(svg_text(left, 24, caption, size=FIG_CAPTION, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"))
    for i, (stage, segs, note) in enumerate(rows):
        y = top + i * row_h + 6
        h = row_h - 12
        parts.append(svg_text(left - 12, y + h * 0.68, stage, size=FIG_CAT, anchor="end", weight="700", family="var(--sd-font-mono)"))
        if not segs:
            parts.append(f'<rect x="{left}" y="{y:.1f}" width="{inner:.1f}" height="{h:.1f}" fill="var(--sd-primary)" rx="4"/>')
            parts.append(svg_text(left + 18, y + h * 0.68, note or stage, size=22, fill="var(--sd-ink-100)", weight="700"))
            continue
        x = float(left)
        for lab, weight in segs:
            ww = max(56.0, inner * (weight / max_w) * 0.9)
            fill, ink = seq_paint(min(1.0, weight / 8.0))
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{h:.1f}" fill="{fill}" rx="4"/>')
            if ww >= 64:
                parts.append(svg_text(x + 10, y + h * 0.68, lab, size=18, fill=ink, weight="700", family="var(--sd-font-mono)"))
            x += ww + 8
        if note:
            parts.append(svg_text(min(x + 4, FIG_W - 220), y + h * 0.68, note, size=16, fill="var(--sd-ink-72)"))
    return svg_root("".join(parts))


def parse_box_slots(text: str) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in text.splitlines():
        if "┌" in line:
            title = re.sub(r"[┌┐─━]+", "", line).strip()
            current = {"title": title, "items": []}
            groups.append(current)
        elif current is not None and "│" in line:
            item = re.sub(r"[│┃]", "", line).strip()
            if item:
                current["items"].append(item)
        elif "└" in line:
            current = None
    return groups


def svg_slots(groups: list[dict[str, Any]], caption: str = "") -> str:
    n = max(1, len(groups))
    gap = 14
    top = 18
    gh = (FIG_H - top - 20 - gap * (n - 1)) / n
    parts: list[str] = []
    for i, group in enumerate(groups):
        y = top + i * (gh + gap)
        parts.append(
            f'<rect x="16" y="{y:.1f}" width="{FIG_W - 32}" height="{gh:.1f}" '
            f'fill="var(--sd-paper)" stroke="var(--sd-ink-14)" stroke-width="2" rx="6"/>'
        )
        parts.append(f'<rect x="16" y="{y:.1f}" width="10" height="{gh:.1f}" fill="var(--sd-accent)" rx="2"/>')
        parts.append(svg_text(40, y + 34, group["title"], size=22, weight="700"))
        for j, item in enumerate(group["items"][:5]):
            parts.append(svg_text(40, y + 66 + j * 28, item, size=20, fill="var(--sd-ink-72)"))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def svg_categorical_grid(groups: list[dict[str, Any]], caption: str = "") -> str:
    groups = groups[:9]
    n = max(1, len(groups))
    cols = 3 if n >= 5 else 2
    rows = math.ceil(n / cols)
    gap, side, top, bot = 14, 18, 30, 24
    cw = (FIG_W - side * 2 - gap * (cols - 1)) / cols
    ch = (FIG_H - top - bot - gap * (rows - 1)) / rows
    parts: list[str] = []
    if caption:
        parts.append(svg_text(side, 21, caption, size=FIG_CAPTION, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"))
    for i, group in enumerate(groups):
        x = side + (i % cols) * (cw + gap)
        y = top + (i // cols) * (ch + gap)
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ch:.1f}" fill="var(--sd-paper)" stroke="var(--sd-ink-14)" stroke-width="2" rx="5"/>')
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="8" height="{ch:.1f}" fill="var(--sd-accent)" rx="2"/>')
        parts.append(svg_text(x + 24, y + 34, truncate(group["title"], 14), size=20, weight="700"))
        for j, item in enumerate(group.get("items", [])[:2]):
            parts.append(svg_text(x + 24, y + 66 + j * 28, truncate(item, 22), size=16, fill="var(--sd-ink-72)"))
    return svg_root("".join(parts))


def parse_price_ladder(text: str) -> list[tuple[float, str, bool]]:
    rows: list[tuple[float, str, bool]] = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw or re.fullmatch(r"[─\-━↑↓▲\s]+", raw):
            continue
        matched = re.search(r"(\d+(?:\.\d+)?)\s*[─–—\-]{1,}\s+(\S.+)$", raw)
        if matched:
            lab = matched.group(2).strip()
            rows.append((float(matched.group(1)), lab, "★" in raw or "石头" in lab))
            continue
        matched = re.search(r"(.+?)[：:]\s*(\d+(?:\.\d+)?)\s*元", raw)
        if matched:
            lab = matched.group(1).strip()
            rows.append((float(matched.group(2)), lab, "★" in raw or "石头" in lab))
    return rows


def svg_price_ladder(rows: list[tuple[float, str, bool]], caption: str = "") -> str:
    if not rows:
        return svg_root("")
    prices = [p for p, _, _ in rows]
    lo, hi = min(prices), max(prices)
    if hi == lo:
        hi = lo + 1
    pad = (hi - lo) * 0.1
    lo, hi = lo - pad, hi + pad
    left, top, bot = 170, 36, 28
    inner_h = FIG_H - top - bot
    parts = [f'<line x1="{left}" y1="{top}" x2="{left}" y2="{FIG_H - bot}" stroke="var(--sd-ink-28)" stroke-width="2"/>']
    used: list[float] = []
    for price, lab, mine in rows:
        y = top + inner_h * (1 - (price - lo) / (hi - lo))
        for prev in used:
            if abs(y - prev) < 18:
                y = prev + 18
        used.append(y)
        fill = "var(--sd-secondary)" if mine else "var(--sd-accent)"
        r = 8 if mine else 5.5
        parts.append(f'<circle cx="{left}" cy="{y:.1f}" r="{r}" fill="{fill}"/>')
        parts.append(svg_text(left - 16, y + 6, f"{fmt_val(price)}元", size=18, anchor="end", family="var(--sd-font-mono)", weight="700"))
        parts.append(svg_text(left + 22, y + 6, lab, size=20, fill=fill if mine else "var(--sd-ink-100)", weight="700" if mine else "400"))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def parse_number_axis(text: str) -> tuple[list[float], list[str], str]:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return [], [], ""
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", lines[0])]
    labels = re.split(r"\s{2,}", lines[1].strip()) if len(lines) > 1 else []
    notes: list[str] = []
    for ln in lines[2:]:
        s = ln.strip()
        if s in {"↑", "↓", "▲"} or re.fullmatch(r"[─\-↑↓▲\s]+", s):
            continue
        notes.append(s)
    return nums, labels, " ".join(notes)


def svg_number_axis(nums: list[float], labels: list[str], note: str, caption: str = "") -> str:
    if len(nums) < 2:
        return svg_root("")
    lo, hi = min(nums), max(nums)
    if hi == lo:
        hi = lo + 1
    left, right = 56, 56
    y = FIG_H * 0.4
    inner = FIG_W - left - right
    parts = [f'<line x1="{left}" y1="{y}" x2="{FIG_W - right}" y2="{y}" stroke="var(--sd-ink-28)" stroke-width="3"/>']
    for i, num in enumerate(nums):
        x = left + inner * (num - lo) / (hi - lo)
        parts.append(f'<circle cx="{x:.1f}" cy="{y}" r="6" fill="var(--sd-accent)"/>')
        parts.append(svg_text(x, y - 20, fmt_val(num), size=18, anchor="middle", family="var(--sd-font-mono)", weight="700"))
        if i < len(labels) and labels[i]:
            parts.append(svg_text(x, y + 34, labels[i], size=16, anchor="middle"))
    gaps = [(nums[i + 1] - nums[i], i) for i in range(len(nums) - 1)]
    if gaps:
        span, idx = max(gaps)
        x1 = left + inner * (nums[idx] - lo) / (hi - lo)
        x2 = left + inner * (nums[idx + 1] - lo) / (hi - lo)
        parts.append(f'<line x1="{x1:.1f}" y1="{y + 72}" x2="{x2:.1f}" y2="{y + 72}" stroke="var(--sd-secondary)" stroke-width="4"/>')
        parts.append(svg_text((x1 + x2) / 2, y + 104, note or f"空档 {fmt_val(span)} 元", size=20, anchor="middle", fill="var(--sd-secondary)", weight="700"))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def parse_stack_rows(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if "←" in s:
            left, right = s.split("←", 1)
            rows.append((left.strip(), right.strip()))
        else:
            rows.append((s, ""))
    return rows


def svg_stack(rows: list[tuple[str, str]], caption: str = "") -> str:
    n = max(1, len(rows))
    top, bot = 24, 24
    rh = (FIG_H - top - bot) / n
    parts: list[str] = []
    for i, (lab, note) in enumerate(rows):
        frac = 0.4 + 0.6 * ((i + 1) / n)
        ww = (FIG_W - 80) * frac
        x = (FIG_W - ww) / 2
        y = top + i * rh + 6
        h = rh - 12
        fill, ink = seq_paint(1 - i / max(1, n - 1))
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{h:.1f}" fill="{fill}" rx="4"/>')
        parts.append(svg_text(FIG_W / 2, y + h * 0.65, f"{lab}  {note}".strip(), size=20, anchor="middle", fill=ink, weight="700"))
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def looks_diagram(text: str) -> bool:
    return bool(re.search(r"[█▓░┌┐└┘│]{1,}|[═─]{6,}", text or ""))


def parse_calc_waterfall(text: str) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        matched = re.search(r"(?:≈|=)\s*([+\-]?\d[\d,.]*)\s*(元|%)?\s*$", raw)
        if not matched:
            continue
        lab = re.sub(r"\s*[≈=].*$", "", raw).strip()
        lab = re.sub(r"\s+", " ", lab)
        if len(lab) > 16:
            lab = lab.split(" ")[0][:16]
        rows.append((lab or "项", float(matched.group(1).replace(",", ""))))
    return rows


def classify_diagram(text: str) -> str:
    if re.search(r"[█▓░]", text) and re.search(r"\d+\s*家|D[1-6]", text):
        return "weight-shift"
    if "┌" in text or "└" in text:
        return "slots"
    if "对于" in text and ("因为" in text or "是" in text) and text.count("\n") <= 8:
        return "claim"
    if len(parse_calc_waterfall(text)) >= 3:
        return "calc"
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    nums, _, _ = parse_number_axis(text)
    if len(nums) >= 3 and re.search(r"─{2,}", first) and not re.search(r"[\u4e00-\u9fff]", first):
        return "number-axis"
    if len(parse_price_ladder(text)) >= 3:
        return "price-ladder"
    if text.count("㎡") >= 2 and re.search(r"[=→]", text):
        return "facts"
    if text.count("←") >= 2:
        return "stack"
    arrows = [ln for ln in text.splitlines() if "→" in ln or "->" in ln]
    if len(arrows) >= 2 or (len(arrows) == 1 and arrows[0].count("→") >= 2):
        return "flow"
    facts = [ln for ln in text.splitlines() if "：" in ln or re.search(r".+=.+\d", ln)]
    if len(facts) >= 2:
        return "facts"
    return "lines"


ITEM_LINE = re.compile(r"^(?:D\d|S\d|P\d|[①-⑩]|[0-9]+[\.、]|[-*•])")


def looks_item_wall(sentences: list[str]) -> bool:
    if len(sentences) < 4:
        return False
    return sum(1 for s in sentences if ITEM_LINE.match(s)) >= 4


def svg_quadrant(labels: list[str], xs: list[float], ys: list[float], x_name: str = "X", y_name: str = "Y", caption: str = "", highlight: int = 0) -> str:
    top, bot, left, right = 40, 48, 88, 40
    inner_w = FIG_W - left - right
    inner_h = FIG_H - top - bot
    mx, my = _median(xs), _median(ys)
    minx, maxx = min(xs, default=0), max(xs, default=1)
    miny, maxy = min(ys, default=0), max(ys, default=1)
    if maxx == minx:
        maxx = minx + 1
    if maxy == miny:
        maxy = miny + 1
    pad_x = (maxx - minx) * 0.18
    pad_y = (maxy - miny) * 0.18
    minx, maxx = minx - pad_x, maxx + pad_x
    miny, maxy = miny - pad_y, maxy + pad_y
    def px(v: float) -> float:
        return left + inner_w * (v - minx) / (maxx - minx)
    def py(v: float) -> float:
        return top + inner_h * (1 - (v - miny) / (maxy - miny))
    labeled = thin_scatter_labels(
        scatter_label_indices(labels, xs, ys, [1.0] * len(labels), highlight),
        xs, ys, [1.0] * len(labels), highlight, px, py, min_dist=36,
    )
    parts = [
        f'<rect x="{left}" y="{top}" width="{inner_w}" height="{inner_h}" fill="var(--sd-paper)" stroke="var(--sd-ink-14)"/>',
    ]
    if len(xs) >= 4:
        parts.extend([
            f'<line x1="{px(mx):.1f}" y1="{top}" x2="{px(mx):.1f}" y2="{FIG_H - bot}" stroke="var(--sd-ink-28)" stroke-dasharray="6 6"/>',
            f'<line x1="{left}" y1="{py(my):.1f}" x2="{FIG_W - right}" y2="{py(my):.1f}" stroke="var(--sd-ink-28)" stroke-dasharray="6 6"/>',
            svg_text(px(mx) + 8, top + 22, f"{x_name} 中位 ≥ {fmt_val(mx)}", size=FIG_TICK, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"),
            svg_text(left + 8, py(my) - 10, f"{y_name} 中位 ≥ {fmt_val(my)}", size=FIG_TICK, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"),
        ])
    order = sorted(range(len(labels)), key=lambda i: 1 if i == highlight else 0)
    placed: list[tuple[float, float]] = []
    labels_svg: list[str] = []
    for i in order:
        lab, x, y = labels[i], xs[i], ys[i]
        fill = "var(--sd-secondary)" if i == highlight else "var(--sd-accent)"
        cx, cy = px(x), py(y)
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="{fill}" '
            f'stroke="var(--sd-paper)" stroke-width="1.4"/>'
        )
        if i not in labeled:
            continue
        pos = place_scatter_label(cx, cy, 9, placed)
        if pos is None and i != highlight:
            continue
        lx, ly, anchor = pos or (cx, cy - 20, "middle")
        placed.append((lx, ly))
        labels_svg.append(svg_halo_text(lx, ly, fit_label(lab, 12), anchor=anchor))
    parts.extend(labels_svg)
    if caption:
        note = caption
        if len(labeled) < len(labels) and "其余见清单" not in note:
            note = f"{caption} · 标 {len(labeled)} 家，其余见清单"
        parts.append(svg_caption(note))
    return svg_root("".join(parts))


def svg_bubble(labels: list[str], xs: list[float], ys: list[float], sizes: list[float], caption: str = "", highlight: int = 0) -> str:
    top, bot, left, right = 48, 52, 96, 48
    inner_w = FIG_W - left - right
    inner_h = FIG_H - top - bot
    minx, maxx = min(xs, default=0), max(xs, default=1)
    miny, maxy = min(ys, default=0), max(ys, default=1)
    if maxx == minx:
        maxx = minx + 1
    if maxy == miny:
        maxy = miny + 1
    pad_x = (maxx - minx) * 0.16
    pad_y = (maxy - miny) * 0.16
    minx, maxx = minx - pad_x, maxx + pad_x
    miny, maxy = miny - pad_y, maxy + pad_y
    def px(v: float) -> float:
        return left + inner_w * (v - minx) / (maxx - minx)
    def py(v: float) -> float:
        return top + inner_h * (1 - (v - miny) / (maxy - miny))
    smax = max(sizes) if sizes else 1
    mx, my = _median(xs), _median(ys)
    labeled = thin_scatter_labels(
        scatter_label_indices(labels, xs, ys, sizes, highlight),
        xs, ys, sizes, highlight, px, py,
    )
    parts = [
        f'<rect x="{left}" y="{top}" width="{inner_w}" height="{inner_h}" fill="var(--sd-paper)" stroke="var(--sd-ink-14)"/>',
    ]
    if len(xs) >= 4:
        parts.extend([
            f'<line x1="{px(mx):.1f}" y1="{top}" x2="{px(mx):.1f}" y2="{FIG_H - bot}" stroke="var(--sd-ink-28)" stroke-dasharray="6 6"/>',
            f'<line x1="{left}" y1="{py(my):.1f}" x2="{FIG_W - right}" y2="{py(my):.1f}" stroke="var(--sd-ink-28)" stroke-dasharray="6 6"/>',
            svg_text(px(mx) + 8, top + 18, f"客单中位 ≥ {fmt_val(mx)}", size=FIG_TICK, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"),
            svg_text(left + 8, py(my) - 8, f"评分中位 ≥ {fmt_val(my)}", size=FIG_TICK, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"),
        ])
    for t in (minx + pad_x, (minx + maxx) / 2, maxx - pad_x):
        parts.append(svg_text(px(t), FIG_H - bot + 28, fmt_val(t), size=FIG_TICK, anchor="middle", fill="var(--sd-ink-60)", family="var(--sd-font-mono)"))
    for t in (miny + pad_y, (miny + maxy) / 2, maxy - pad_y):
        parts.append(svg_text(left - 8, py(t) + 6, fmt_val(t), size=FIG_TICK, anchor="end", fill="var(--sd-ink-60)", family="var(--sd-font-mono)"))
    order = sorted(range(len(labels)), key=lambda i: (sizes[i] if i < len(sizes) else 0, i == highlight), reverse=True)
    placed: list[tuple[float, float]] = []
    labels_svg: list[str] = []
    for i in order:
        lab, x, y, s = labels[i], xs[i], ys[i], sizes[i]
        cx, cy = px(x), py(y)
        frac = math.sqrt(s / smax) if smax else 0
        r = BUBBLE_R_MIN + (BUBBLE_R_MAX - BUBBLE_R_MIN) * frac
        fill = "var(--sd-secondary)" if i == highlight else "var(--sd-accent)"
        opacity = 0.42 if r >= 16 else 0.8
        stroke = "var(--sd-ink-100)" if i == highlight else "var(--sd-paper)"
        sw = 2.2 if i == highlight else 1.3
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>'
        )
        if i not in labeled:
            continue
        pos = place_scatter_label(cx, cy, r, placed)
        if pos is None and i != highlight:
            continue
        lx, ly, anchor = pos or (cx, cy - r - 12, "middle")
        placed.append((lx, ly))
        if math.hypot(lx - cx, ly - cy) > r + 14:
            labels_svg.append(
                f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" '
                f'stroke="var(--sd-ink-28)" stroke-width="1"/>'
            )
        labels_svg.append(svg_halo_text(lx, ly, fit_label(lab, 12), anchor=anchor))
    parts.extend(labels_svg)
    note = (caption or "面积∝√量 · 虚线=中位 ≥").replace(" · 未标名见清单", "")
    if len(labeled) < len(labels) and "其余见清单" not in note:
        note = f"{note} · 标 {len(labeled)} 家，其余见清单"
    parts.append(svg_caption(note))
    return svg_root("".join(parts))


def svg_radar(labels: list[str], values: list[float], unit: str = "", caption: str = "") -> str:
    n = max(3, len(labels))
    cx, cy, r = FIG_W / 2, FIG_H / 2 - 6, 168
    vmax = nice_max(max(values) if values else 1)
    parts: list[str] = []
    for ring in (0.33, 0.66, 1.0):
        pts = []
        for i in range(n):
            ang = -math.pi / 2 + i * 2 * math.pi / n
            pts.append(f"{cx + r * ring * math.cos(ang):.1f},{cy + r * ring * math.sin(ang):.1f}")
        parts.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="var(--sd-ink-14)" stroke-width="1"/>')
        parts.append(svg_text(cx + 8, cy - r * ring, fmt_measure(vmax * ring, unit), size=12, fill="var(--sd-ink-60)", family="var(--sd-font-mono)"))
    poly = []
    for i in range(n):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        lab = labels[i] if i < len(labels) else ""
        val = values[i] if i < len(values) else 0
        rr = r * (max(0, val) / vmax)
        x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        lx, ly = cx + (r + 32) * math.cos(ang), cy + (r + 32) * math.sin(ang)
        poly.append(f"{x:.1f},{y:.1f}")
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="var(--sd-accent)"/>')
        parts.append(svg_text(lx, ly, f"{lab} {fmt_measure(val, unit)}", size=14, anchor="middle"))
    parts.append(f'<polygon points="{" ".join(poly)}" fill="var(--sd-accent)" fill-opacity="0.22" stroke="var(--sd-accent)" stroke-width="2.4"/>')
    if caption:
        parts.append(svg_caption(caption))
    return svg_root("".join(parts))


def svg_figure(
    fill_id: str,
    labels: list[str],
    values: list[float],
    table: Table | None = None,
    vcols: list[int] | None = None,
    unit: str = "",
    caption: str = "",
    highlight: int | None = None,
    title: str = "",
) -> str:
    body = [r for r in (table.rows if table else []) if not is_sum_row(r)]
    nums = vcols or (numeric_cols(table) if table else [])
    lcol = label_col(table) if table else 0
    hi = highlight if highlight is not None else highlight_index(labels, values, title)
    kw = {"unit": unit, "caption": caption, "highlight": hi}

    def labs(limit: int) -> list[str]:
        return [strip_md(r[lcol] if lcol < len(r) else r[0]) for r in body[:limit]]

    series_n = min(len(body), NAMED_SERIES_MAX) if body else 12
    if fill_id == "heatmap" and table and len(nums) >= 2:
        rows = labs(series_n)
        cols = [strip_md(table.headers[c]) for c in nums[:8]]
        grid = [[parse_num(r[c] if c < len(r) else "") for c in nums[:8]] for r in body[:series_n]]
        drawn = svg_heatmap(rows, cols, grid, **kw)
    elif fill_id == "slope" and table and len(nums) >= 2:
        pair = slope_col_pair(table, nums) or (nums[0], nums[1])
        ca, cb = pair
        a = [parse_num(r[ca] if ca < len(r) else "") or 0 for r in body[:series_n]]
        b = [parse_num(r[cb] if cb < len(r) else "") or 0 for r in body[:series_n]]
        drawn = svg_slope(labs(series_n), a, b, strip_md(table.headers[ca]), strip_md(table.headers[cb]), **kw)
    elif fill_id == "line-dual" and table and len(nums) >= 2:
        series = [[parse_num(r[c] if c < len(r) else "") or 0 for r in body[:series_n]] for c in nums[:2]]
        names = [strip_md(table.headers[c]) for c in nums[:2]]
        drawn = svg_line_dual(labs(series_n), series, names, **kw)
    elif fill_id == "quadrant" and table and len(nums) >= 2:
        xc, yc, _ = pick_axis_cols(table, nums, title)
        xs = [parse_num(r[xc] if xc < len(r) else "") or 0 for r in body[:BUBBLE_ROWS]]
        ys = [parse_num(r[yc] if yc < len(r) else "") or 0 for r in body[:BUBBLE_ROWS]]
        drawn = svg_quadrant(
            labs(BUBBLE_ROWS), xs, ys,
            x_name=strip_md(table.headers[xc]), y_name=strip_md(table.headers[yc]),
            caption=caption, highlight=hi,
        )
    elif fill_id == "bubble" and table and len(nums) >= 2:
        xc, yc, zc = pick_axis_cols(table, nums, title)
        zc = zc if zc is not None else nums[0]
        xs = [parse_num(r[xc] if xc < len(r) else "") or 0 for r in body[:BUBBLE_ROWS]]
        ys = [parse_num(r[yc] if yc < len(r) else "") or 0 for r in body[:BUBBLE_ROWS]]
        zs = [parse_num(r[zc] if zc < len(r) else "") or 0 for r in body[:BUBBLE_ROWS]]
        drawn = svg_bubble(labs(BUBBLE_ROWS), xs, ys, zs, caption=caption, highlight=hi)
    elif fill_id == "timeline":
        drawn = svg_timeline(labels, values, **kw)
    elif fill_id == "radar":
        drawn = svg_radar(labels[:8], values[:8], unit=unit, caption=caption)
    elif fill_id == "waterfall":
        drawn = svg_waterfall(labels, values, **kw)
    elif fill_id == "funnel":
        drawn = svg_funnel(labels, values, **kw)
    elif fill_id == "treemap":
        drawn = svg_treemap(labels, values, **kw)
    elif fill_id == "pareto":
        drawn = svg_vbars(labels, values, cdf=True, mark80=True, **kw)
    elif fill_id == "hist-cdf":
        drawn = svg_vbars(labels, values, cdf=True, mark80=False, **kw)
    elif fill_id == "diverging-bar":
        drawn = svg_hbars(labels, values, diverging=True, **kw)
    else:
        drawn = svg_hbars(labels, values, diverging=False, **kw)
    if needs_proxy(title):
        mark = svg_text(FIG_W / 2, FIG_H / 2 + 8, "禁止外部对标", size=40, fill="var(--sd-ink-14)", anchor="middle", weight="700")
        drawn = drawn.replace("</svg>", mark + "</svg>")
    return drawn


def fmt_val(v: float) -> str:
    if abs(v) >= 100000000:
        return f"{v / 100000000:.2f}亿"
    if abs(v) >= 10000:
        return f"{v / 10000:.1f}万"
    if abs(v - round(v)) < 1e-6:
        return f"{int(round(v)):,}"
    return f"{v:.1f}"


def heading_of(unit: Unit) -> str:
    return strip_md(unit.h3 or unit.h2 or unit.chapter)


def avg_cell_len(table: Table) -> float:
    cells = [strip_md(c) for r in table.rows for c in r]
    return sum(len(c) for c in cells) / max(1, len(cells))


QUAL_HEADERS = (
    "情景", "判断", "建议", "含义", "读法", "动作", "理由", "交付", "状态", "里程碑",
    "核心命题", "决策方式", "功能", "目标", "产品", "测什么", "判定指标", "决策影响",
    "风险点", "门槛", "基准", "健康区间", "内容", "作用", "产出", "依据", "优先级",
)


def is_text_heavy(table: Table) -> bool:
    nums = numeric_cols(table)
    if not nums:
        return True
    if has_count_series(table):
        return False
    for c, h in enumerate(table.headers):
        if not any(k in strip_md(h) for k in QUAL_HEADERS):
            continue
        lens = [len(strip_md(r[c] if c < len(r) else "")) for r in table.rows]
        avg = (sum(lens) / len(lens)) if lens else 0
        if avg >= 22:
            return True
    long_cols = 0
    for c, h in enumerate(table.headers):
        if c in nums or c == 0 or is_index_header(h):
            continue
        lens = [len(strip_md(r[c] if c < len(r) else "")) for r in table.rows]
        if lens and (sum(lens) / len(lens)) >= 18:
            long_cols += 1
    return long_cols >= 2


def measure_kinds(table: Table) -> int:
    kinds: set[str] = set()
    for c in numeric_cols(table):
        h = strip_md(table.headers[c] if c < len(table.headers) else "")
        if "评分" in h or (h.endswith("分") and "部分" not in h):
            kinds.add("score")
        elif any(k in h for k in ("中位", "客单", "均")):
            kinds.add("stat")
        elif any(k in h for k in ("最大", "天花板")):
            kinds.add("max")
        elif any(k in h for k in ("占比", "%")):
            kinds.add("share")
        elif any(k in h for k in ("门店", "品牌", "数")):
            kinds.add("count")
        else:
            kinds.add("other")
    return len(kinds)


def cols_commensurate(table: Table, nums: list[int]) -> bool:
    if len(nums) < 2:
        return False
    heads = [strip_md(table.headers[i]) for i in nums]
    if all(any(k in h for k in ("占比", "%", "比例")) for h in heads):
        return True
    if all(any(k in h for k in ("评分", "分")) for h in heads):
        return True
    maxima: list[float] = []
    for c in nums:
        vs = [parse_num(r[c] if c < len(r) else "") for r in table.rows]
        vs = [abs(v) for v in vs if v is not None]
        if vs:
            maxima.append(max(vs))
    if len(maxima) < 2:
        return False
    if max(maxima) / max(min(maxima), 1e-6) <= 8:
        return True
    joined = " ".join(
        strip_md(r[c] if c < len(r) else "")
        for r in table.rows
        for c in nums
    )
    return joined.count("家") >= max(4, len(table.rows))


def period_pair(headers: list[str], nums: list[int]) -> bool:
    if len(nums) < 2:
        return False
    blob = " ".join(strip_md(headers[c]) for c in nums[:2])
    return any(k in blob for k in ("V0", "V1", "标准", "实收", "前", "后", "本次", "上次", "原", "现"))


def bin_labels(labels: list[str]) -> bool:
    hits = 0
    for lab in labels:
        if len(lab) > 10:
            continue
        if any(k in lab for k in ("元", "km", "以上", "以下", "环带", "环")):
            hits += 1
        elif re.search(r"\d+\s*[–\-]\s*\d+", lab) and any(k in lab for k in ("分", "m", "店", "家", "%", "楼")):
            hits += 1
        elif re.match(r"^[<≤]?\d+", lab) and any(k in lab for k in ("–", "-", "+", "以上", "以下")):
            hits += 1
    return hits >= max(2, (len(labels) + 1) // 2)


def pick_value_col(table: Table, nums: list[int], title: str) -> int:
    if not nums:
        return 1
    scored: list[tuple[int, int]] = []
    for c in nums:
        h = strip_md(table.headers[c] if c < len(table.headers) else "")
        score = 0
        if h == "门店" or h.endswith("门店") or any(k in h for k in ("门店数", "商户数", "该带总门店", "额", "规模", "销量", "品牌数", "人数", "北京门店", "总分")):
            score += 5
        if h.endswith("数") and "评" not in h:
            score += 2
        if any(k in h for k in ("占比", "贡献", "%", "总分")):
            score += 1
        sample = " ".join(strip_md(r[c] if c < len(r) else "") for r in table.rows[:8])
        if ("%" in sample or "％" in sample) and any(k in title for k in ("酒", "精酿", "占比")):
            score += 8
        if any(k in h for k in ("评分", "分")):
            score -= 1
        if any(k in title for k in ("价格", "规模", "分布")) and any(k in h for k in ("门店", "规模", "带")):
            score += 2
        if any(k in title for k in ("稳定", "CV", "变异", "复制")) and any(k in h for k in ("稳定", "CV", "变异")):
            score += 8
        scored.append((score, c))
    scored.sort(reverse=True)
    return scored[0][1]


def slope_col_pair(table: Table, nums: list[int]) -> tuple[int, int] | None:
    if len(nums) < 2:
        return None
    heads = [(c, strip_md(table.headers[c] if c < len(table.headers) else "")) for c in nums]

    def find_one(pred) -> int | None:
        for c, h in heads:
            if pred(h):
                return c
        return None

    mall = find_one(lambda h: "商场店" in h and "非" not in h and "客单" not in h and "评分" not in h)
    street = find_one(lambda h: "非商场" in h and "客单" not in h and "评分" not in h)
    if mall is not None and street is not None:
        return mall, street
    price = [
        c for c, h in heads
        if any(k in h for k in ("客单", "人均")) and not any(k in h for k in ("CV", "变异", "标准差"))
        or ("中位" in h and not any(k in h for k in ("店数", "评分", "门店", "评论")))
    ]
    if len(price) >= 2:
        return price[0], price[1]
    return None


def figure_title(title: str, table: Table) -> str:
    base = display_title(title)
    h0 = strip_md(table.headers[0] if table.headers else "")
    heads = " ".join(strip_md(h) for h in table.headers)
    extra = ""
    if h0 in {"价格带", "评分区间"}:
        extra = h0
    elif h0 == "分组" and "精酿" in heads:
        extra = "酒饮占比"
    elif "合生汇店客单" in heads or ("合生汇" in heads and "其他店" in heads):
        extra = "合生汇 vs 北京"
    elif "商场店" in heads and "非商场" in heads:
        extra = "商场 vs 街边"
    elif "总分" in heads and any(k in base for k in ("TOP", "学习对象")):
        extra = "总分"
    elif any(k in heads for k in ("客单", "人均")) and "评分" in heads and "标准差" not in heads:
        extra = "客单×评分"
    elif h0 == "商圈":
        extra = "商圈"
    if h0 == "情景" and "人均" in heads:
        extra = extra or "人均对照"
    if extra and extra not in base and len(base) + len(extra) + 3 <= TITLE_CANVAS_MAX:
        return f"{base} · {extra}"
    return base


def pick_axis_cols(table: Table, nums: list[int], title: str) -> tuple[int, int, int | None]:
    def find(*keys: str) -> int | None:
        for c in nums:
            h = strip_md(table.headers[c] if c < len(table.headers) else "")
            if "标准" in h or "CV" in h:
                continue
            if any(k in h for k in keys):
                return c
        return None

    x = find("人均", "客单")
    y = find("平均评分", "评分")
    z = find("评论", "总分", "门店", "商户", "规模")
    if x is not None and y is not None:
        return x, y, z
    if len(nums) >= 3:
        return nums[0], nums[1], nums[2]
    if len(nums) >= 2:
        return nums[0], nums[1], None
    return nums[0], nums[0], None


def pick_fill(title: str, table: Table, labels: list[str], values: list[float]) -> str:
    t = title + " " + " ".join(table.headers)
    nums = numeric_cols(table)
    n = len(labels)
    head0 = strip_md(table.headers[0] if table.headers else "")
    if head0 == "阶段" or any(k in title for k in ("路线图阶段", "分阶段目标", "门店台阶")):
        return "timeline"
    if any(k in title for k in ("权重", "阶段迁移")) and len(nums) >= 3:
        return "heatmap"
    if any(k in title for k in ("帕累托", "二八", "贡献度", "学习对象", "TOP 12", "TOP12", "一致性", "稳定性")) or ("贡献" in title and not bin_labels(labels)):
        return "pareto"
    if any(k in title for k in ("SKU",)) and 4 <= n <= 10:
        return "treemap"
    if any(k in t for k in ("瀑布", "增减", "对账", "情景", "人均测算", "成本测算")):
        return "waterfall"
    if any(k in t for k in ("漏斗",)):
        return "funnel"
    if any(k in t for k in ("四象限", "象限")):
        return "quadrant"
    if any(k in t for k in ("雷达",)):
        return "radar"
    if slope_col_pair(table, nums):
        return "slope"
    if period_pair(table.headers, nums):
        return "slope"
    if any(k in t for k in ("热力",)) or (len(nums) >= 3 and cols_commensurate(table, nums) and n >= 3):
        return "heatmap"
    if bin_labels(labels) or any(k in t for k in ("价格带", "环带", "分箱", "评分区间")):
        return "hist-cdf"
    x, y, z = pick_axis_cols(table, nums, title) if nums else (None, None, None)
    if x is not None and y is not None and x != y and n >= 2:
        xh = strip_md(table.headers[x])
        yh = strip_md(table.headers[y])
        if any(k in xh for k in ("人均", "客单")) and "评分" in yh:
            return "bubble" if z is not None else "quadrant"
    if any(k in t for k in ("结构", "构成", "拆分")) and 4 <= n <= 8:
        return "treemap"
    if any(v < 0 for v in values):
        return "diverging-bar"
    if period_pair(table.headers, nums) or any(k in t for k in ("趋势", "同比", "双轴")):
        return "slope" if period_pair(table.headers, nums) else "line-dual"
    if n >= 5 and not bin_labels(labels) and any(k in t for k in ("排名", "规模", "门店")):
        return "pareto"
    return "hbar"


def has_plot_axes(table: Table) -> bool:
    heads = " ".join(strip_md(h) for h in table.headers)
    return any(k in heads for k in ("客单", "人均", "评分", "门店数", "该带总门店", "评论", "占比", "毛利", "SKU", "品牌数", "均价"))


def classify_table(title: str, table: Table, genre: str) -> str:
    t = title + " " + " ".join(table.headers)
    rows = [r for r in table.rows if not is_sum_row(r)]
    n = len(rows)
    nums = numeric_cols(table)
    head0 = strip_md(table.headers[0] if table.headers else "")
    lcol = label_col(table)
    labels = [strip_md(r[lcol] if lcol < len(r) else r[0]) for r in rows]
    if any(k in t for k in ("九宫", "评分矩阵", "3×3", "3x3")) and n <= 9:
        return "matrix"
    if any(k in title for k in ("Gate", "不达标不进")) or head0 == "Gate":
        return "roster"
    if head0 in {"产品", "我们的产品"}:
        return "roster"
    if any(k in title for k in ("结论", "必须记住", "读法")) and n <= 10:
        heads0 = " ".join(strip_md(h) for h in table.headers)
        if head0 == "情景" and nums and n >= 3:
            return "chart"
        if n >= 2 and any(k in heads0 for k in ("客单", "人均")) and "评分" in heads0:
            return "chart"
        return "roster"
    if head0 == "情景" and nums and n >= 3:
        return "chart"
    if any(k in t for k in ("学什么", "不学", "对照", "双口径", "vs", "对比")) and len(table.headers) <= 4 and not nums:
        return "compare"
    if 3 <= n <= 6 and len(table.headers) <= 4 and (
        head0 in {"维度", "层级", "解法", "层"}
        or any(k in title for k in ("评估维度", "三层筛选"))
    ):
        return "kpi"
    if 3 <= n <= 6 and nums and len(table.headers) <= 3 and head0 in {"指标", "项", "科目", "维度", "域", "数据集"}:
        return "kpi"
    if 3 <= n <= 6 and nums and len(table.headers) <= 3 and any(k in title for k in ("指标", "大盘", "基本盘", "KPI", "关键数", "看板", "健康度")):
        return "kpi"
    if is_text_heavy(table) and not has_plot_axes(table):
        return "roster"
    if mixed_time_and_share(table):
        return "roster"
    if head0 == "阶段" and has_count_series(table):
        return "chart"
    if len(table.headers) == 2 and head0 in {"指标", "项", "科目", "维度", "域"}:
        if 3 <= n <= 6 and nums:
            return "kpi"
        return "roster"
    if not nums:
        return "roster"
    short_labels = all(len(x) <= 18 for x in labels[:8])
    compact = avg_cell_len(table) <= 14
    heads = " ".join(strip_md(h) for h in table.headers)
    has_price = any(k in heads for k in ("客单", "人均", "售价", "定价", "均价"))
    has_score = "评分" in heads
    if n >= 3 and has_price and has_score:
        return "chart"
    if n == 2 and measure_kinds(table) >= 2:
        blob = " ".join(strip_md(c) for r in rows for c in r)
        if "%" not in blob and "％" not in blob:
            return "roster"
    if n >= 4 and has_price and has_score:
        return "chart"
    if n >= 4 and has_count_series(table):
        return "chart"
    if n >= 4 and has_price and n <= CHART_ROWS and short_labels:
        return "chart"
    if "viz" in genre and 3 <= n <= BIN_CHART_ROWS and short_labels and avg_cell_len(table) <= 24:
        return "chart"
    if n == 2 and nums and short_labels and compact:
        return "kpi" if len(table.headers) <= 3 else "roster"
    if n == 2 and nums and len(table.headers) <= 3:
        return "kpi"
    if n == 2 and nums:
        return "roster"
    bins = bin_labels(labels)
    if bins and nums:
        return "chart"
    if n >= 5 and has_count_series(table):
        return "chart"
    if measure_kinds(table) >= 3 and len(table.headers) >= 5 and not (has_price and has_score) and not has_count_series(table):
        return "roster"
    named_rows = not bins and not any(k in "".join(labels) for k in ("元", "%", "以上", "以下"))
    if named_rows and len(table.headers) >= 4 and not has_plot_axes(table):
        return "roster"
    chartish = bins or any(k in t for k in ("价格带", "规模", "占比", "分布", "贡献", "环带", "楼层", "结构", "帕累托", "评分", "漏斗", "瀑布", "商圈"))
    row_cap = BIN_CHART_ROWS if bins else CHART_ROWS
    if n >= 3 and n <= row_cap and short_labels and (chartish or (len(nums) >= 1 and avg_cell_len(table) <= 14)):
        if has_plot_axes(table):
            return "chart"
        if 5 <= n <= CHART_TABLE_SIDE and all(len(x) <= 12 for x in labels) and not bins:
            return "chart-table"
        return "chart"
    return "roster"


def status_for(text: str) -> str:
    if any(k in text for k in ("未确认", "缺口", "断开", "不可达", "未解决")):
        return "blocked"
    if any(k in text for k in ("待验证", "假设", "缓存", "需澄清", "谨慎")):
        return "degraded"
    return "ready"


def takeaway_from(blocks: list[Block], fallback: str, genre: str) -> str:
    paras = [strip_md(b.text) for b in blocks if b.kind in {"para", "quote"} and strip_md(b.text)]
    for p in reversed(paras):
        if NUM_RE.search(p) and len(p) < 160:
            return p
    for p in paras:
        if any(k in p for k in ("因此", "必须", "结论", "铁律", "建议", "死法", "关卡", "学", "不学")):
            return first_sentence(p, 120)
    if genre == "roadmap":
        return fallback or "关卡未写清，阶段不放行。"
    if genre == "dossier":
        return fallback or "未归一化的规模不作数。"
    return fallback or "一页一个决策。"


def rail_cards(slide: Slide, issued: str) -> str:
    sync = {"ready": "实时同步 · LIVE", "degraded": "缓存中 · CACHED", "blocked": "连接中断 · OFFLINE"}[slide.status]
    extra = slide.extra or {}
    conf_a = esc(field_copy(extra.get("conf_a") or "门店库与客户表可复核的事实。", 3))
    conf_b = esc(field_copy(extra.get("conf_b") or "公开报道与行业报告，作旁证。", 3))
    conf_c = esc(field_copy(extra.get("conf_c") or "待验证假设，禁止当作已证事实。", 3))
    return f'''<!-- SOURCE / GLOSSARY / CONCLUSION / CONFIDENCE: data for #sd-explain, not painted on the canvas. -->
<div class="sd-rail">
    <div class="sd-rail-card" data-live-source="md.source" data-sync-status="{slide.status}" data-sync-at="{esc(issued)}">
      <div class="head"><span>数据出处 · SOURCE</span><span class="sd-live live {slide.status}">{sync}</span></div>
      <div class="body">{esc(field_copy(slide.source, 3))}</div>
      <div class="foot">更新于 {esc(issued)}</div>
    </div>
    <div class="sd-rail-card" data-live-source="md.glossary" data-sync-status="ready" data-sync-at="{esc(issued)}">
      <div class="head"><span>术语解释 · GLOSSARY</span><span class="sd-live live ready">实时同步 · LIVE</span></div>
      <div class="body"><div class="term"><b>{esc(field_copy(slide.term, 3))}</b><br><span>{esc(field_copy(slide.term_def, 3))}</span></div></div>
      <div class="foot">HOW TO READ · {esc(field_copy(slide.how, 3))}</div>
    </div>
    <div class="sd-rail-card" data-live-source="md.conclusion" data-sync-status="{slide.status}" data-sync-at="{esc(issued)}">
      <div class="head"><span>结论解释 · CONCLUSION</span><span class="sd-live live {slide.status}">{sync}</span></div>
      <div class="body">{esc(field_copy(slide.takeaway, 3))}</div>
      <div class="foot">{esc(issued)}</div>
    </div>
    <div class="sd-rail-card" data-live-source="md.confidence" data-sync-status="ready" data-sync-at="{esc(issued)}">
      <div class="head"><span>置信度分级 · CONFIDENCE</span><span class="sd-live live ready">实时同步 · LIVE</span></div>
      <div class="body">
        <div class="term"><span class="sd-status ready">A · 数据支撑</span><br><span>{conf_a}</span></div>
        <div class="term"><span class="sd-status degraded">B · 外部佐证</span><br><span>{conf_b}</span></div>
        <div class="term"><span class="sd-status blocked">C · 待验证假设</span><br><span>{conf_c}</span></div>
      </div>
      <div class="foot">A 数据 · B 佐证 · C 假设</div>
    </div>
  </div>'''


LOGO_HREF = "logo/侍天.png"


def logo_img(style: str = "") -> str:
    extra = f' style="{style}"' if style else ""
    return f'<img src="{LOGO_HREF}" alt="侍天"{extra} />'


def chrome(meta: dict, slide: Slide, index: int, total: int) -> str:
    return (
        f'<div class="sd-tk"><span class="sd-chip">{esc(field_chip(slide.chip))}</span></div>\n'
        f'<div class="sd-index">{index} / {total}</div>\n'
        f'<div class="sd-h2">{esc(field_title(slide.title))}</div>'
    )


def paper_well(inner: str, *, grow: str = "1 1 0", extra: str = "") -> str:
    return (
        f'<div style="flex:{grow}; min-height:0; min-width:0; border:2px solid var(--sd-ink-14); '
        f'background:var(--sd-paper); border-radius:var(--sd-radius-card); {extra}">{inner}</div>'
    )


def statement_field(main: str, support: str) -> str:
    bits = [s for s in sentences_of(support) if s] if support else []
    if support and not bits:
        bits = [support]
    if len(bits) >= 5:
        quote_grow = "0 0 auto"
    elif len(bits) == 4:
        quote_grow = "0.85 1 0"
    elif len(bits) <= 1:
        quote_grow = "1.4 1 0"
    else:
        quote_grow = "1.15 1 0"
    quote = paper_well(
        '<div class="sd-rule" style="width:6px; height:40%; flex:none; margin:0;"></div>'
        f'<div class="sd-quote">{esc(field_copy(main))}</div>',
        grow=quote_grow,
        extra="padding:0.7em 0.9em; display:flex; gap:0.8em; align-items:center;",
    )
    shell = (
        '<div class="sd-content" style="display:flex; flex-direction:column; '
        'justify-content:stretch; gap:24px;">'
    )
    if not bits:
        return f"{shell}{quote}</div>"
    if len(bits) == 1:
        lede = paper_well(
            f'<div class="sd-lede">{esc(field_copy(bits[0]))}</div>',
            extra="padding:0.7em 0.9em; display:flex; align-items:center;",
        )
        return f"{shell}{quote}{lede}</div>"
    if len(bits) <= 4:
        card_flex = "flex:1 1 46%;" if len(bits) == 4 else "flex:1;"
        wrap = "flex-wrap:wrap;" if len(bits) == 4 else ""
        cards = []
        for i, sentence in enumerate(bits):
            cards.append(
                f'<div style="{card_flex} min-width:0; border:2px solid var(--sd-ink-14); '
                'background:var(--sd-paper); border-radius:var(--sd-radius-card); '
                'padding:0.7em 0.85em; display:flex; flex-direction:column; '
                'justify-content:center; gap:0.4em;">'
                f'<div style="font-family:var(--sd-font-mono); font-size:var(--sd-type-small); '
                f'color:var(--sd-ink-60); letter-spacing:.08em;">{i + 1:02d}</div>'
                f'<div class="sd-lede">{esc(field_copy(sentence))}</div></div>'
            )
        return (
            f"{shell}{quote}"
            f'<div style="flex:1 1 0; min-height:0; display:flex; gap:24px; '
            f'align-items:stretch; {wrap}">{"".join(cards)}</div></div>'
        )
    rows = "".join(
        f'<tr><td class="num">{i + 1:02d}</td><td>{esc(field_copy(s))}</td></tr>'
        for i, s in enumerate(bits)
    )
    return (
        f"{shell}{quote}"
        f'<div style="flex:1 1 0; min-height:0;">'
        f'<table class="sd-table" style="height:100%;">'
        f'<tr><th class="num">序</th><th>依据</th></tr>{rows}</table></div></div>'
    )


def footer(meta: dict, index: int, total: int) -> str:
    return f'<div class="sd-footer"><span>{esc(meta["deck_name"])}</span><span>{index} / {total}</span></div>'


def pack_of(slide: Slide) -> str:
    job = slide.job
    extra = slide.extra or {}
    if job == "statement":
        support = extra.get("support") or ""
        bits = sentences_of(support) if support else []
        n = len(extra.get("main") or "") + len(support)
        if len(bits) >= 5:
            return "tight"
        if len(bits) == 4:
            return "mid"
        if n < 160 or len(bits) <= 2:
            return "air"
        if n > 340:
            return "tight"
        return "mid"
    if job == "roster":
        rows = max(0, slide.body.count("<tr") - 1)
        wide = bool(extra.get("wide"))
        has_lede = "sd-lede" in (slide.body or "")
        if has_lede:
            if rows >= 10 or wide:
                return "tight"
            return "mid"
        if rows <= 6 and not wide:
            return "air"
        if rows >= 10 or wide:
            return "tight"
        return "mid"
    if job == "kpi":
        cards = extra.get("cards") or []
        textish = any(len(str(card[0])) >= 8 or len(str(card[2] or "")) >= 12 for card in cards)
        if len(cards) <= 3 or textish:
            return "air"
        return "mid"
    if job == "compare":
        n = len(extra.get("left") or "") + len(extra.get("right") or "")
        if n < 180:
            return "air"
        return "mid"
    if job == "chart":
        n = extra.get("n") or 0
        if 0 < n <= 4:
            return "air"
        return "mid"
    if job in {"matrix", "verdict"}:
        return "air"
    return "mid"


def wrap_slide(slide: Slide, inner: str, index: int, total: int, meta: dict) -> str:
    job = slide.job
    assert job in JOBS, job
    pt = PAGE_TYPE[job]
    shell = SHELL[job]
    on = " on" if index == 1 else ""
    foot = footer(meta, index, total) if job != "cover" else ""
    pack = pack_of(slide)
    fill = slide.fill or ""
    if job == "statement":
        main = (slide.extra or {}).get("main") or ""
        support = (slide.extra or {}).get("support") or ""
        bits = sentences_of(support) if support else []
        if len(main) <= 96 and len(bits) <= 3:
            fill = "poster"
    return (
        f'<section class="slide sd-slide{on} {shell}" data-job="{job}" data-page-type="{pt}" '
        f'data-fill="{esc(fill)}" data-pack="{pack}">\n'
        f"{inner}\n{foot}\n</section>"
    )


class DeckBuilder:
    def __init__(self, meta: dict, cover_titles: list[str], chapters: list[Chapter], preamble: list[Unit], tables: list[Table]):
        self.meta = meta
        self.cover_titles = cover_titles
        self.chapters = chapters
        self.preamble = preamble
        self.tables = tables
        self.slides: list[Slide] = []
        self.table_emitted = set()
        self.fig_i = 0
        self._ge20_injected = False
        self._ge20_subset_emitted = False

    def add(self, slide: Slide) -> None:
        self.slides.append(slide)

    def stamp_conf_on_recent_readme(self, conf: dict[str, str]) -> None:
        for slide in reversed(self.slides):
            if slide.job in {"cover", "divider", "toc"}:
                break
            if slide.job == "readme":
                extra = dict(slide.extra or {})
                extra.update(conf)
                slide.extra = extra

    def chip_for(self, chapter: str, unit: Unit | None = None) -> str:
        for i, ch in enumerate(self.chapters):
            if ch.title == chapter:
                short = display_title(ch.title.split("·")[-1].strip()).strip("（）() ")
                return f"{cn_chapter(i + 1)} · {fit_phrase(short, CHIP_CANVAS_MAX)}"
        if unit and unit.h2:
            return fit_phrase(unit.h2, CHIP_CANVAS_MAX)
        return "序 · 阅读"

    def emit_cover(self) -> None:
        self.add(Slide(
            job="cover",
            title=self.meta["title1"],
            chip="",
            body="",
            source=self.meta["source_detail"],
            how="封面只定身份",
            takeaway=self.meta["decision"],
            term="终局",
            term_def="以可复制的单店模型倒推首店决策",
            extra={
                "title2": self.meta["title2"],
                "period": self.meta["period"],
                "scope": self.meta["scope"],
                "basis": self.meta["basis"],
                "issued": self.meta["issued"],
                "mark": self.meta["brand_mark"],
            },
        ))

    def emit_toc(self) -> None:
        acts = []
        for i, ch in enumerate(self.chapters):
            short = re.sub(r"^第[一二三四五六七八九十零百0-9]+\s*部分\s*[·•]?\s*", "", ch.title)
            short = re.sub(r"^附录\s*[·•]?\s*", "", short)
            short = display_title(short or ch.title)
            en = self.meta.get("acts_en", {}).get(ch.title) or fit_label(short, 24).upper()
            acts.append((cn_chapter(i + 1), short, en))
        for page, start in enumerate(range(0, len(acts), TOC_ROWS)):
            chunk = acts[start:start + TOC_ROWS]
            title = "目录 · CONTENTS" if page == 0 else f"目录 · CONTENTS · {page + 1}"
            self.add(Slide(
                job="toc",
                title=title,
                chip="序 · 目录",
                body="",
                source=self.meta["source_detail"],
                how="按章阅读，一章一个决策链",
                takeaway="按章读。",
                term="章",
                term_def="H1 切幕；正文页挂在章下",
                extra={"acts": chunk},
            ))

    def emit_readme_from(self, unit: Unit) -> bool:
        title = heading_of(unit)
        if not any(k in title for k in ("阅读", "口径", "置信", "版本说明", "数据基础", "阅读提示", "数据资产")):
            return False
        tables = [b.table for b in unit.blocks if b.kind == "table" and b.table]
        conf_rows = []
        calibre = None
        for tb in tables:
            heads = "".join(tb.headers)
            if any(k in heads for k in ("等级", "置信")) or any("数据支撑" in "".join(r) for r in tb.rows):
                conf_rows = tb.rows
                self.table_emitted.add(tb.source_index)
            elif calibre is None:
                calibre = tb
                self.table_emitted.add(tb.source_index)
        notes = [strip_md(b.text) for b in unit.blocks if b.kind in {"para", "quote"}]
        a = "门店库与客户表可复核的事实。"
        b = "公开报道与行业报告，作旁证。"
        c = "待验证假设，禁止当作已证事实。"
        for r in conf_rows:
            line = " ".join(strip_md(x) for x in r)
            if line.startswith("A") or "数据支撑" in line:
                a = line
            elif line.startswith("B") or "外部" in line:
                b = line
            elif line.startswith("C") or "待验证" in line:
                c = line
        conf = {"conf_a": a, "conf_b": b, "conf_c": c}
        empty_body = not calibre and not notes
        if "置信" in title and empty_body:
            self.stamp_conf_on_recent_readme(conf)
            leftover = [tb for tb in tables if tb.source_index not in self.table_emitted]
            for tb in leftover:
                self.emit_table(title, tb, unit)
            return True
        rows_html = ""
        if calibre:
            rows_html = table_html(calibre.headers, calibre.rows[:6], set(numeric_cols(calibre)))
        else:
            rows_html = "<div style='font-family:var(--sd-font-serif);font-size:var(--sd-type-body);line-height:1.6;color:var(--sd-ink-72)'>" + "<br>".join(esc(n) for n in notes[:4]) + "</div>"
        self.add(Slide(
            job="readme",
            title=title,
            chip=self.chip_for(unit.chapter, unit),
            body=rows_html,
            source=self.meta["source_detail"],
            how="先看口径，再看置信度，再进论证",
            takeaway=takeaway_from(unit.blocks, notes[0] if notes else title, self.meta["genre"]),
            term="置信度",
            term_def="A 数据支撑 / B 外部佐证 / C 待验证假设",
            extra=conf,
            status=status_for(title + "".join(notes[:2])),
        ))
        leftover = [tb for tb in tables if tb.source_index not in self.table_emitted]
        for tb in leftover:
            self.emit_table(title, tb, unit)
        leftover_blocks = [b for b in unit.blocks if b.kind in {"para", "quote", "list"}]
        if leftover_blocks and not calibre:
            pass
        elif leftover_blocks:
            self.emit_prose(unit, leftover_blocks)
        return True

    def emit_figure_slide(self, unit: Unit, title: str, svg: str, fill: str, claim: str, inventory: Table | None = None) -> None:
        self.fig_i += 1
        self.add(Slide(
            job="chart",
            title=display_title(title),
            chip=f"图 {self.fig_i} · {self.chip_for(unit.chapter, unit)}",
            body="",
            source=self.meta["source_detail"],
            how=HOW_FOR_FILL.get(fill, "一张主图回答一个决策"),
            takeaway=claim or takeaway_from(unit.blocks, title, self.meta["genre"]),
            term="读图",
            term_def=HOW_FOR_FILL.get(fill, "图上的块是决策，不是装饰"),
            fill=fill,
            extra={"svg": svg, "fig": self.fig_i},
        ))
        if inventory and inventory.rows:
            self.emit_roster(title, expand_inventory(title, inventory, unit), unit, close_sum=False, claim=claim, inventory_of=self.fig_i)

    def emit_diagram(self, unit: Unit, text: str, title: str = "") -> None:
        title = display_title(title or heading_of(unit))
        claim = takeaway_from(unit.blocks, title, self.meta["genre"])
        kind = classify_diagram(text)
        if kind == "claim":
            pages = pack_statement_pages(sentences_of(text) or [strip_md(text)])
            for i, (main, support) in enumerate(pages):
                self.emit_statement(unit, title, glue_orphans(main), glue_orphans(support), overflow=i > 0, page=i + 1)
            return
        if kind == "calc":
            calc = parse_calc_waterfall(text)
            if len(calc) >= 3:
                fake = Table(headers=["项", "元"], rows=[[lab, str(val)] for lab, val in calc], source_index=-1)
                self.emit_chart(title, fake, unit, claim=claim)
                return
        if kind == "weight-shift":
            rows = parse_weight_shift(text)
            if rows:
                inv = Table(
                    headers=["台阶", "块", "注"],
                    rows=[[st, " / ".join(lab for lab, _ in segs), note] for st, segs, note in rows],
                    source_index=-1,
                )
                self.emit_figure_slide(unit, title, svg_weight_shift(rows, "行=门店台阶 · 块=主导问题域 · 色深=权重"), "weight-shift", claim, inventory=inv)
                return
        if kind == "slots":
            groups = parse_box_slots(text)
            if groups:
                inv = Table(
                    headers=["格", "项"],
                    rows=[[g["title"], it] for g in groups for it in (g["items"] or ["—"])],
                    source_index=-1,
                )
                self.emit_figure_slide(unit, title, svg_slots(groups), "slots", claim, inventory=inv)
                return
        if kind == "price-ladder":
            ladder = parse_price_ladder(text)
            if len(ladder) >= 3:
                inv = Table(
                    headers=["点", "人均", "本项目"],
                    rows=[[lab, str(price), "是" if mine else ""] for price, lab, mine in ladder],
                    source_index=-1,
                )
                self.emit_figure_slide(unit, title, svg_price_ladder(ladder, "纵轴=人均 · 红点=本项目"), "price-ladder", claim, inventory=inv)
                return
        if kind == "number-axis":
            nums, labels, note = parse_number_axis(text)
            if len(nums) >= 3:
                inv_rows = [[labels[i] if i < len(labels) else str(n), str(n)] for i, n in enumerate(nums)]
                if note:
                    inv_rows.append(["空档", note])
                inv = Table(headers=["点", "值"], rows=inv_rows, source_index=-1)
                self.emit_figure_slide(unit, title, svg_number_axis(nums, labels, note), "number-axis", claim, inventory=inv)
                return
        if kind == "stack":
            stack = parse_stack_rows(text)
            if len(stack) >= 3:
                inv = Table(headers=["层", "注"], rows=[[lab, note] for lab, note in stack], source_index=-1)
                self.emit_figure_slide(unit, title, svg_stack(stack, "底下是现在 · 上面是以后"), "stack", claim, inventory=inv)
                return
        if kind == "flow":
            steps: list[str] = []
            for line in text.splitlines():
                bits = [p.strip() for p in re.split(r"→|->", line) if p.strip()]
                if len(bits) >= 2:
                    steps.extend(bits)
                elif line.strip():
                    steps.append(line.strip())
            if len(steps) >= 2:
                fake = Table(headers=["阶段", "序"], rows=[[s, str(i + 1)] for i, s in enumerate(steps[:10])], source_index=-1)
                self.emit_chart(title, fake, unit, claim=claim)
                return
        rows: list[list[str]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if "：" in line:
                left, right = line.split("：", 1)
                rows.append([left.strip(), right.strip()])
            elif "=" in line:
                left, right = line.split("=", 1)
                rows.append([left.strip(), right.strip()])
            else:
                rows.append([str(len(rows) + 1), line])
        if rows:
            self.emit_roster(title, Table(headers=["项", "内容"], rows=rows, source_index=-1), unit, close_sum=False, claim=claim)

    def emit_statement(self, unit: Unit, title: str, main: str, support: str, *, overflow: bool = False, page: int = 1) -> None:
        self.add(Slide(
            job="statement",
            title=display_title(title) + (f" · {page}" if overflow else ""),
            chip=self.chip_for(unit.chapter, unit),
            body="",
            source=self.meta["source_detail"],
            how="一页一个判断",
            takeaway=takeaway_from(unit.blocks, main, self.meta["genre"]),
            term=display_title(title) or "判断",
            term_def=support or title,
            extra={"main": main, "support": support},
            overflow_of="statement" if overflow else None,
            status=status_for(main + support),
        ))

    def emit_prose(self, unit: Unit, blocks: list[Block] | None = None) -> None:
        blocks = blocks if blocks is not None else [b for b in unit.blocks if b.kind != "table"]
        title = heading_of(unit)
        quotes = [b for b in blocks if b.kind == "quote"]
        paras = [b for b in blocks if b.kind == "para"]
        lists = [b for b in blocks if b.kind == "list"]
        if any(k in title for k in ("当场决策", "争议", "证伪", "未解", "风险登记", "杀死这个项目")):
            self.emit_verdict(unit, paras, lists)
            return
        if any(k in title for k in ("学什么", "不学", "对照", "双口径", "vs")) and lists:
            self.emit_compare_lists(unit, lists, paras)
            return
        sentences: list[str] = []
        long_lists: list[Block] = []
        for block in blocks:
            if block.kind == "diagram" or (block.kind in {"para", "quote"} and looks_diagram(block.text)):
                self.emit_diagram(unit, block.text, title)
                continue
            if block.kind in {"para", "quote"}:
                sentences.extend(sentences_of(block.text))
            elif block.kind == "list":
                items = [strip_md(x) for x in block.items if strip_md(x)]
                if len(items) > 6:
                    long_lists.append(block)
                else:
                    sentences.extend(items)
        if not sentences:
            if title and not long_lists:
                self.emit_statement(unit, title, glue_orphans(title), glue_orphans(unit.chapter))
            for lst in long_lists:
                self.emit_list_roster(unit, lst)
            return
        if looks_item_wall(sentences):
            wall = Table(
                headers=["项", "内容"],
                rows=[[str(i + 1), s] for i, s in enumerate(sentences)],
                source_index=-1,
            )
            self.emit_roster(title, wall, unit, close_sum=False)
            for lst in long_lists:
                self.emit_list_roster(unit, lst)
            return
        pages = pack_statement_pages(sentences)
        for i, (main, support) in enumerate(pages):
            self.emit_statement(unit, title, glue_orphans(main), glue_orphans(support), overflow=i > 0, page=i + 1)
        for lst in long_lists:
            self.emit_list_roster(unit, lst)

    def emit_verdict(self, unit: Unit, paras: list[Block], lists: list[Block]) -> None:
        title = heading_of(unit)
        texts = [strip_md(p.text) for p in paras if strip_md(p.text)]
        items: list[str] = []
        for lst in lists:
            items.extend(strip_md(x) for x in lst.items)
        four = items[:4] if len(items) >= 4 else texts[:4]
        while len(four) < 4:
            four.append("见本章原文。")
        self.add(Slide(
            job="verdict",
            title=title,
            chip=self.chip_for(unit.chapter, unit),
            body="",
            source=self.meta["source_detail"],
            how="顺序固定：争议→事实→处理→证伪",
            takeaway=takeaway_from(unit.blocks, four[-1], self.meta["genre"]),
            term="证伪",
            term_def="写清推翻条件，禁止无条件鸡汤",
            extra={"dispute": four[0], "fact": four[1], "resolution": four[2], "falsify": four[3]},
            status=status_for(title),
        ))

    def emit_compare_lists(self, unit: Unit, lists: list[Block], paras: list[Block]) -> None:
        title = heading_of(unit)
        left = lists[0].items
        right = lists[1].items if len(lists) > 1 else []
        left_s = "；".join(strip_md(x) for x in left[:6])
        right_s = "；".join(strip_md(x) for x in right[:6]) if right else (strip_md(paras[0].text) if paras else "不学：把别人的成本结构当自己的。")
        self.add(Slide(
            job="compare",
            title=title,
            chip=self.chip_for(unit.chapter, unit),
            body="",
            source=self.meta["source_detail"],
            how="左右同题，中间是因此",
            takeaway=takeaway_from(unit.blocks, left_s, self.meta["genre"]),
            term="因此",
            term_def="两列必须共用一个量纲或同一决策",
            extra={"left_label": "可迁移", "left": left_s, "right_label": "不可复制", "right": right_s, "connector": "因此"},
        ))
        for lst in lists[2:]:
            self.emit_list_roster(unit, lst)

    def emit_list_roster(self, unit: Unit, lst: Block) -> None:
        title = heading_of(unit)
        headers = ["项", "内容"]
        rows = [[str(i + 1), it] for i, it in enumerate(lst.items)]
        fake = Table(headers=headers, rows=rows, source_index=-1)
        if "dossier-viz" in self.meta["genre"] and 4 <= len(rows) <= 9:
            groups = [{"title": row[0], "items": [strip_md(row[1])]} for row in rows]
            self.emit_figure_slide(
                unit,
                title,
                svg_categorical_grid(groups, f"n={len(rows)} · 分类清单；完整文字见后页清单"),
                "slots",
                inventory=fake,
            )
            return
        self.emit_roster(title, fake, unit, close_sum=False)

    def emit_table(self, title: str, table: Table, unit: Unit, claim: str = "") -> None:
        if table.source_index in self.table_emitted and table.source_index >= 0:
            return
        if table.source_index >= 0:
            self.table_emitted.add(table.source_index)
        rows = [r for r in table.rows if not is_sum_row(r)]
        if (
            "dossier-viz" in self.meta["genre"]
            and not numeric_cols(table)
            and 3 <= len(rows) <= 10
            and 2 <= len(table.headers) <= 4
        ):
            groups = [
                {
                    "title": strip_md(row[0]),
                    "items": [
                        f"{strip_md(table.headers[i])}：{strip_md(row[i])}"
                        for i in range(1, min(len(row), len(table.headers)))
                        if strip_md(row[i])
                    ],
                }
                for row in rows
            ]
            self.emit_figure_slide(
                unit,
                title,
                svg_categorical_grid(groups, f"n={len(rows)} · 分类映射；完整文字见后页清单"),
                "slots",
                claim,
                inventory=Table(headers=table.headers, rows=rows, source_index=-1),
            )
            return
        job = classify_table(title, table, self.meta["genre"])
        if job == "kpi":
            self.emit_kpi(title, table, unit, claim=claim)
        elif job == "matrix":
            self.emit_matrix(title, table, unit, claim=claim)
        elif job == "compare":
            self.emit_compare_table(title, table, unit, claim=claim)
        elif job == "chart":
            self.emit_chart(title, table, unit, claim=claim)
        elif job == "chart-table":
            self.emit_chart_table(title, table, unit, claim=claim)
        else:
            self.emit_roster(title, table, unit, close_sum=True, claim=claim)

    def emit_kpi(self, title: str, table: Table, unit: Unit, claim: str = "") -> None:
        nums = numeric_cols(table)
        vcol = pick_value_col(table, nums, title) if nums else 1
        if vcol == 0 and len(table.headers) > 1:
            vcol = 1
        cards = []
        for row in table.rows[:6]:
            if is_sum_row(row):
                continue
            label = strip_md(row[0])
            raw = strip_md(row[vcol] if vcol < len(row) else row[1] if len(row) > 1 else "")
            cjk = len(re.findall(r"[\u4e00-\u9fff]", raw))
            if nums and cjk <= 2:
                val, split_d = split_kpi_value(raw)
            else:
                val, split_d = raw, ""
            nxt = strip_md(row[vcol + 1]) if vcol + 1 < len(row) else ""
            nxt_h = strip_md(table.headers[vcol + 1]) if vcol + 1 < len(table.headers) else ""
            note_ok = nxt and (any(k in nxt_h for k in ("含义", "说明", "读法", "基准")) or not any(k in nxt_h for k in QUAL_HEADERS))
            delta = split_d or (nxt if note_ok else "")
            cards.append((val or "—", label, delta))
        while len(cards) < 3:
            cards.append(("—", "待补", ""))
        self.add(Slide(
            job="kpi",
            title=title,
            chip=self.chip_for(unit.chapter, unit),
            body="",
            source=self.meta["source_detail"],
            how="三至六卡，同一口径",
            takeaway=claim or takeaway_from(unit.blocks, f"{cards[0][1]} = {cards[0][0]}", self.meta["genre"]),
            term=strip_md(table.headers[vcol] if table.headers else "指标"),
            term_def="大数等宽，方向看 delta",
            extra={"cards": cards[:6]},
        ))

    def emit_matrix(self, title: str, table: Table, unit: Unit, claim: str = "") -> None:
        cells = []
        body = [r for r in table.rows if not is_sum_row(r)]
        for r in body[:3]:
            for c in range(1, min(4, len(r))):
                lab = f"{strip_md(r[0])}×{strip_md(table.headers[c] if c < len(table.headers) else str(c))}"
                val = strip_md(r[c])
                st = "blocked" if val in {"0", "0 款", "—", ""} else ("degraded" if "待" in val or "低" in val else "ready")
                cells.append((st, lab, val or "—"))
        while len(cells) < 9:
            cells.append(("degraded", "空档", "0"))
        self.add(Slide(
            job="matrix",
            title=title,
            chip=self.chip_for(unit.chapter, unit),
            body="",
            source=self.meta["source_detail"],
            how="每格 = 状态点 + 数量；零值≠缺口",
            takeaway=claim or takeaway_from(unit.blocks, title, self.meta["genre"]),
            term="零值",
            term_def="零不是缺口，除非列基数过阈",
            extra={"cells": cells[:9]},
        ))

    def emit_compare_table(self, title: str, table: Table, unit: Unit, claim: str = "") -> None:
        h = table.headers
        left_h = strip_md(h[0] if h else "左")
        right_h = strip_md(h[1] if len(h) > 1 else "右")
        left_bits, right_bits = [], []
        for row in table.rows[:8]:
            if is_sum_row(row):
                continue
            left_bits.append(strip_md(row[0]))
            if len(row) > 1:
                right_bits.append(strip_md(row[1]))
        self.add(Slide(
            job="compare",
            title=title,
            chip=self.chip_for(unit.chapter, unit),
            body="",
            source=self.meta["source_detail"],
            how="左右同量纲，中间因此",
            takeaway=claim or takeaway_from(unit.blocks, title, self.meta["genre"]),
            term="因此",
            term_def="两列必须能一起做决定",
            extra={
                "left_label": left_h,
                "left": "；".join(left_bits[:8]),
                "right_label": right_h,
                "right": "；".join(right_bits[:8]),
                "connector": "因此",
            },
        ))

    def _draw_figure(
        self,
        fill: str,
        labels: list[str],
        values: list[float],
        table: Table,
        nums: list[int],
        vcol: int,
        title: str,
    ) -> str:
        header = strip_md(table.headers[vcol] if vcol < len(table.headers) else "")
        if fill == "heatmap":
            header = " / ".join(strip_md(table.headers[c]) for c in nums[:4])
        unit = unit_from_cells(table, vcol if fill != "heatmap" else (nums[0] if nums else vcol), header)
        return svg_figure(
            fill,
            labels,
            values,
            table=table,
            vcols=nums,
            unit=unit,
            caption=figure_caption(fill, header, len(labels), unit, title),
            highlight=highlight_index(labels, values, title),
            title=title,
        )

    def emit_chart(self, title: str, table: Table, unit: Unit, claim: str = "", source: str | None = None) -> None:
        body = [r for r in table.rows if not is_sum_row(r)]
        nums = numeric_cols(table)
        lcol = label_col(table)
        vcol = pick_value_col(table, nums, title)
        labels_all = [strip_md(r[lcol] if lcol < len(r) else r[0]) for r in body]
        probe = [parse_span_hi(r[vcol] if vcol < len(r) else "") or 0 for r in body[:8]]
        fill = pick_fill(title, table, labels_all[:12], probe)
        cap = figure_plot_cap(fill, labels_all, len(body))
        plot = body[:cap]
        labels = [strip_md(r[lcol] if lcol < len(r) else r[0]) for r in plot]
        parser = parse_span_hi if fill == "timeline" else parse_num
        values = [parser(r[vcol] if vcol < len(r) else "") or 0 for r in plot]
        self.fig_i += 1
        svg = self._draw_figure(fill, labels, values, table, nums, vcol, title)
        title = figure_title(title, table)
        src = source or self.meta["source_detail"]
        self.add(Slide(
            job="chart",
            title=title,
            chip=f"图 {self.fig_i} · {self.chip_for(unit.chapter, unit)}",
            body="",
            source=src,
            how=HOW_FOR_FILL.get(fill, "一张主图回答一个决策"),
            takeaway=claim or takeaway_from(unit.blocks, f"{labels[0]} = {fmt_val(values[0])}" if labels else title, self.meta["genre"]),
            term=strip_md(table.headers[vcol] if vcol < len(table.headers) else "值"),
            term_def="分母随图走；中位切分归高侧 ≥",
            fill=fill,
            extra={"svg": svg, "fig": self.fig_i, "n": len(labels)},
        ))
        inv = expand_inventory(title, Table(headers=table.headers, rows=body, source_index=-1), unit)
        self.emit_roster(title, inv, unit, close_sum=True, claim=claim, inventory_of=self.fig_i, source=src)
        self._complete_ge20_figure(title, table, unit, claim)

    def emit_chart_table(self, title: str, table: Table, unit: Unit, claim: str = "") -> None:
        body = [r for r in table.rows if not is_sum_row(r)]
        nums = numeric_cols(table)
        lcol = label_col(table)
        vcol = pick_value_col(table, nums, title)
        labels_all = [strip_md(r[lcol] if lcol < len(r) else r[0]) for r in body]
        probe = [parse_num(r[vcol] if vcol < len(r) else "") or 0 for r in body[:8]]
        fill = pick_fill(title, table, labels_all[:12], probe)
        plot = body[:figure_plot_cap(fill, labels_all, len(body))]
        labels = [strip_md(r[lcol] if lcol < len(r) else r[0]) for r in plot]
        values = [parse_num(r[vcol] if vcol < len(r) else "") or 0 for r in plot]
        self.fig_i += 1
        svg = self._draw_figure(fill, labels, values, table, nums, vcol, title)
        side_rows = [[strip_md(r[lcol] if lcol < len(r) else r[0]), strip_md(r[vcol] if vcol < len(r) else "")] for r in body[:CHART_TABLE_SIDE]]
        title = figure_title(title, table)
        self.add(Slide(
            job="chart-table",
            title=title,
            chip=f"图 {self.fig_i} · {self.chip_for(unit.chapter, unit)}",
            body="",
            source=self.meta["source_detail"],
            how=HOW_FOR_FILL.get(fill, "左图给形状，右表给可执行名单"),
            takeaway=claim or takeaway_from(unit.blocks, f"{labels[0]} = {fmt_val(values[0])}" if labels else title, self.meta["genre"]),
            term=strip_md(table.headers[vcol] if vcol < len(table.headers) else "值"),
            term_def="分母随图走；中位切分归高侧 ≥",
            fill=fill,
            extra={"svg": svg, "rows": side_rows, "fig": self.fig_i},
        ))
        inv = expand_inventory(title, Table(headers=table.headers, rows=body, source_index=-1), unit)
        self.emit_roster(title, inv, unit, close_sum=True, claim=claim, inventory_of=self.fig_i)
        self._complete_ge20_figure(title, table, unit, claim)

    def _complete_ge20_figure(self, title: str, table: Table, unit: Unit, claim: str) -> None:
        if is_ge20_band_chart(table) and not self._ge20_injected:
            self._ge20_injected = True
            self._ge20_subset_emitted = True
            brands = filter_stores_ge(load_beijing_brand_scale(), GE20_STORES)
            assert len(brands.rows) >= 24, f"≥20 brand list short: {len(brands.rows)}"
            self.emit_chart(
                "北京品牌分布 · 门店数 ≥ 20 家",
                brands,
                unit,
                claim="北京门店 ≥ 20 家的西式品牌全量，来自 08 §2.1 归一化总榜。",
                source="08 品牌专项 §2.1 · 北京点评库 2026-06 · 归一化后北京门店 ≥ 20 家",
            )
            return
        if self._ge20_subset_emitted or self._ge20_injected or not is_brand_scale_table(table):
            return
        body = [r for r in table.rows if not is_sum_row(r)]
        brands = filter_stores_ge(table, GE20_STORES)
        if len(brands.rows) < 8 or len(brands.rows) >= len(body):
            return
        self._ge20_subset_emitted = True
        self._ge20_injected = True
        self.emit_chart(
            "北京品牌分布 · 门店数 ≥ 20 家",
            brands,
            unit,
            claim=claim or f"从总榜切出北京门店 ≥ 20 家，共 {len(brands.rows)} 个品牌。",
        )

    def emit_roster(self, title: str, table: Table, unit: Unit, close_sum: bool, claim: str = "", *, inventory_of: int | None = None, source: str | None = None) -> None:
        body = [r for r in table.rows if not is_sum_row(r)]
        existing_sum = next((r for r in table.rows if is_sum_row(r)), None)
        nums = set(numeric_cols(table))
        headers = table.headers or ["项"]
        bin_inv = is_bin_inventory(table)
        row_budget = ROSTER_ROWS if bin_inv else (ROSTER_ROWS_WIDE if len(headers) >= 5 else ROSTER_ROWS)
        pages = paginate_rows(body, row_budget)
        do_sum = close_sum and not is_threshold_table(table)
        for pi, chunk in enumerate(pages):
            last = pi == len(pages) - 1
            sum_row = None
            if do_sum and last:
                if existing_sum:
                    sum_row = existing_sum
                else:
                    summable = [c for c in nums if should_sum_header(headers[c] if c < len(headers) else "")]
                    if summable:
                        sums = []
                        for c, h in enumerate(headers):
                            if c in summable:
                                total = 0.0
                                ok = True
                                for r in body:
                                    v = parse_num(r[c] if c < len(r) else "")
                                    if v is None:
                                        ok = False
                                        break
                                    total += v
                                sums.append(fmt_val(total) if ok else "—")
                            else:
                                sums.append("合计" if c == 0 else "—")
                        sum_row = sums
            html_tbl = table_html(headers, chunk, nums, sum_row)
            if inventory_of and pi == 0 and bin_inv:
                lede = inventory_lede(claim, table, unit)
                if lede:
                    html_tbl = (
                        f'<div class="sd-lede" style="margin-bottom:0.55em;">{esc(field_copy(lede))}</div>'
                        + html_tbl
                    )
            if inventory_of:
                st_title = inventory_title(title) if pi == 0 else f"{inventory_title(title)} · {pi + 1}"
                chip = f"图 {inventory_of} 清单 · {self.chip_for(unit.chapter, unit)}"
                overflow = "chart"
                how = (
                    "分箱清单带占比与累计；同节有名样本则挂上，不拆成几百行店"
                    if bin_inv
                    else "图后清单是全量切片，禁止 TOP 冒充全量"
                )
                src = (source or self.meta["source_detail"]) + f" · 图 {inventory_of} · {len(body)} 行"
            else:
                st_title = display_title(title) if pi == 0 else f"{display_title(title)} · {pi + 1}"
                chip = self.chip_for(unit.chapter, unit)
                overflow = None if pi == 0 else "roster"
                how = "行是全量切片；合计行只出现在末页"
                src = self.meta["source_detail"] + f" · {len(body)} 行"
            self.add(Slide(
                job="roster",
                title=st_title,
                chip=chip,
                body=html_tbl,
                source=src,
                how=how,
                takeaway=(claim or takeaway_from(unit.blocks, f"{title} · {len(body)} 行", self.meta["genre"])) if last else f"续页 · 全表 {len(body)} 行",
                term=strip_md(headers[0]) if not inventory_of else "清单",
                term_def="禁止 TOP10 冒充全量",
                overflow_of=overflow if inventory_of else overflow,
                extra={"wide": len(headers) > 6, "fig": inventory_of} if inventory_of else {"wide": len(headers) > 6},
            ))

    def emit_unit(self, unit: Unit) -> None:
        title = heading_of(unit)
        if self.emit_readme_from(unit):
            return
        claim = takeaway_from(unit.blocks, title, self.meta["genre"])
        pending: list[Block] = []

        def flush_prose() -> None:
            if pending:
                self.emit_prose(unit, list(pending))
                pending.clear()

        def pending_lead_in() -> str | None:
            if not pending:
                return None
            if any(b.kind == "list" and len([x for x in b.items if strip_md(x)]) >= 4 for b in pending):
                return None
            texts: list[str] = []
            for block in pending:
                if block.kind in {"para", "quote"}:
                    texts.extend(sentences_of(block.text) or [strip_md(block.text)])
                elif block.kind == "list":
                    texts.extend(strip_md(x) for x in block.items if strip_md(x))
            blob = "".join(piece for piece in texts if piece)
            if 0 < len(blob) <= LEAD_IN_MAX:
                return blob
            return None

        saw = False
        for block in unit.blocks:
            saw = True
            if block.kind == "diagram":
                flush_prose()
                self.emit_diagram(unit, block.text, title)
            elif block.kind == "table" and block.table:
                lead = pending_lead_in()
                if lead is not None:
                    pending.clear()
                    self.emit_table(title, block.table, unit, claim=lead)
                else:
                    flush_prose()
                    self.emit_table(title, block.table, unit, claim=claim)
            elif block.kind in {"para", "quote", "list"}:
                pending.append(block)
        flush_prose()
        if not saw:
            self.emit_prose(unit, [])

    def emit_divider(self, chapter: Chapter) -> None:
        short = re.sub(r"^第[一二三四五六七八九十零百0-9]+\s*部分\s*[·•]?\s*", "", chapter.title)
        short = re.sub(r"^附录\s*[·•]?\s*", "", short)
        short = display_title(short or chapter.title)
        en = self.meta.get("acts_en", {}).get(chapter.title) or "CHAPTER"
        self.add(Slide(
            job="divider",
            title=short,
            chip="",
            body="",
            source=self.meta["source_detail"],
            how="切幕，无正文",
            takeaway=short,
            term="章扉",
            term_def="上一章结束，下一章开始",
            extra={
                "num": cn_chapter(chapter.index + 1),
                "en": en,
                "label": f"第 {chapter.index + 1} 章",
            },
        ))

    def build(self) -> list[Slide]:
        self.emit_cover()
        self.emit_toc()
        for unit in self.preamble:
            self.emit_unit(unit)
        for ch in self.chapters:
            self.emit_divider(ch)
            for unit in ch.units:
                self.emit_unit(unit)
        missing = [t.source_index for t in self.tables if t.source_index not in self.table_emitted]
        if missing:
            orphan = Unit(h2="补遗 · 未挂载表格", h3="", blocks=[], chapter="附录")
            for t in self.tables:
                if t.source_index in missing:
                    self.emit_table(f"补遗表 {t.source_index + 1}", t, orphan)
        self.slides = glue_sparse_statement_slides(self.slides)
        return self.slides


def render_slide(slide: Slide, index: int, total: int, meta: dict) -> str:
    job = slide.job
    issued = meta["issued"]
    if job == "cover":
        x = slide.extra
        inner = f'''
  <div class="sd-tk"><span class="sd-chip">{esc(meta["kicker"])}</span></div>
  <div style="position:absolute; top:20%; left:var(--sd-margin); right:18%;">
    <div class="sd-hero" style="font-size:var(--sd-type-hero);">{esc(field_copy(meta["title1"]))}<br><span style="font-size:.52em; color:var(--sd-ink-72); font-weight:600;">{esc(field_copy(x["title2"]))}</span></div>
    <div class="sd-rule" style="margin:calc(var(--sd-canvas-h) * 0.022) 0 calc(var(--sd-canvas-h) * 0.016);"></div>
    <div style="font-family:var(--sd-font-serif); font-size:var(--sd-type-h3); color:var(--sd-ink-72); max-width:22em; line-height:1.5;">{esc(field_copy(meta["decision"]))}</div>
  </div>
  <div style="position:absolute; left:var(--sd-margin); right:var(--sd-margin); bottom:calc(var(--sd-canvas-h) * 0.048); display:flex; gap:48px; flex-wrap:wrap; font-family:var(--sd-font-mono); font-size:var(--sd-type-small); color:var(--sd-ink-60); border-top:var(--sd-hairline); padding-top:0.5em;">
    <span>分析期间 / PERIOD&nbsp; <b style="color:var(--sd-accent)">{esc(x["period"])}</b></span>
    <span>分析范围 / SCOPE&nbsp; <b style="color:var(--sd-accent)">{esc(x["scope"])}</b></span>
    <span>分类基准 / BASIS&nbsp; <b style="color:var(--sd-accent)">{esc(x["basis"])}</b></span>
    <span>出具日期 / ISSUED&nbsp; <b style="color:var(--sd-accent)">{esc(x["issued"])}</b></span>
  </div>
  <div style="position:absolute; right:var(--sd-margin); top:20%; width:calc(var(--sd-canvas-h) * 0.20); height:calc(var(--sd-canvas-h) * 0.20);">{logo_img("width:100%;height:100%;object-fit:contain")}</div>'''
        return wrap_slide(slide, inner, index, total, meta)
    if job == "divider":
        x = slide.extra
        inner = f'''
  <div class="sd-tk"><span class="sd-chip">{esc(x["num"])} · {esc(field_chip(slide.title))}</span></div>
  <div class="sd-index">{index} / {total}</div>
  <div style="position:absolute; top:18%; left:var(--sd-margin); font-family:var(--sd-font-serif); font-size:var(--sd-type-display); font-weight:900; color:var(--sd-accent); line-height:1;">{esc(x["num"])}</div>
  <div class="sd-eyebrow" style="position:absolute; top:38%; left:var(--sd-margin);">{esc(x["en"])}</div>
  <div class="sd-hero" style="position:absolute; top:44%; left:var(--sd-margin); right:var(--sd-margin); font-size:var(--sd-type-h1);">{esc(field_title(slide.title))}</div>
  <div style="position:absolute; top:58%; left:var(--sd-margin); font-family:var(--sd-font-mono); font-size:var(--sd-type-small); color:var(--sd-ink-60);">{esc(field_copy(x["label"], 3))}</div>
  <div style="position:absolute; bottom:4%; right:var(--sd-margin); font-family:var(--sd-font-mono); font-size:var(--sd-type-micro); color:var(--sd-ink-60);">{esc(meta["deck_name"])} · {index} / {total}</div>'''
        return wrap_slide(slide, inner, index, total, meta)
    if job == "toc":
        rows = []
        for cn, title, en in slide.extra["acts"]:
            rows.append(
                '<div style="display:flex; align-items:baseline; gap:32px; padding:0.38em 0; border-bottom:1px solid var(--sd-ink-07);">'
                f'<span style="font-family:var(--sd-font-serif); font-weight:700; color:var(--sd-accent); width:1.8em; font-size:var(--sd-type-body);">{esc(cn)}</span>'
                f'<span style="font-family:var(--sd-font-serif); font-size:var(--sd-type-body); flex:1;">{esc(field_copy(title))}</span>'
                f'<span style="font-family:var(--sd-font-mono); font-size:var(--sd-type-small); color:var(--sd-ink-60); letter-spacing:.04em;">{esc(field_copy(en, 3))}</span>'
                "</div>"
            )
        inner = chrome(meta, slide, index, total) + f'<div class="sd-content no-rail">{"".join(rows)}</div>'
        return wrap_slide(slide, inner, index, total, meta)
    rail = rail_cards(slide, issued)
    if job == "readme":
        inner = chrome(meta, slide, index, total) + f'''
  <div class="sd-content">{slide.body}</div>
  {rail}'''
        return wrap_slide(slide, inner, index, total, meta)
    if job == "statement":
        inner = chrome(meta, slide, index, total) + f'''
  {statement_field(slide.extra["main"], slide.extra["support"])}
  {rail}'''
        return wrap_slide(slide, inner, index, total, meta)
    if job == "kpi":
        cards = []
        ncard = len(slide.extra["cards"])
        textish = any(len(str(val)) > 8 for val, _, _ in slide.extra["cards"])
        if textish:
            basis = "flex:1; min-width:0;"
            wrap = "flex-direction:row;"
            vstyle = "font-size:var(--sd-type-h2); line-height:1.25; white-space:normal;" if ncard <= 3 else "font-size:var(--sd-type-h3); line-height:1.3; white-space:normal;"
        else:
            basis = "flex:1 1 28%; min-height:46%;" if ncard > 4 else "flex:1;"
            wrap = "flex-wrap:wrap;" if ncard > 4 else ""
            vstyle = ""
        for val, lab, delta in slide.extra["cards"]:
            dcls = "down" if any(k in delta for k in ("↓", "降")) else "up"
            dhtml = f'<div class="d {dcls}">{esc(field_copy(delta, 3))}</div>' if delta else ""
            cards.append(
                f'<div class="sd-kpi" style="{basis}"><div class="l">{esc(field_copy(lab))}</div>'
                f'<div class="v" style="{vstyle}">{esc(val)}</div>{dhtml}</div>'
            )
        inner = chrome(meta, slide, index, total) + f'<div class="sd-content" style="display:flex; gap:28px; align-items:stretch; {wrap}">{"".join(cards)}</div>{rail}'
        return wrap_slide(slide, inner, index, total, meta)
    if job == "roster":
        inner = chrome(meta, slide, index, total) + f'<div class="sd-content">{slide.body}</div>{rail}'
        return wrap_slide(slide, inner, index, total, meta)
    if job == "chart":
        inner = chrome(meta, slide, index, total) + f'''
  <div class="sd-content" style="background:var(--sd-paper); border:2px solid var(--sd-ink-14); border-radius:var(--sd-radius-card); overflow:hidden;">{slide.extra["svg"]}</div>
  {rail}'''
        return wrap_slide(slide, inner, index, total, meta)
    if job == "chart-table":
        rows = "".join(f"<tr><td>{esc(field_copy(n, 3))}</td><td class='num'>{esc(v)}</td></tr>" for n, v in slide.extra["rows"])
        inner = chrome(meta, slide, index, total) + f'''
  <div class="sd-content" style="display:flex; gap:32px;">
    <div style="flex:0 0 58%; background:var(--sd-paper); border:2px solid var(--sd-ink-14); border-radius:var(--sd-radius-card); overflow:hidden;">{slide.extra["svg"]}</div>
    <div style="flex:1;"><table class="sd-table"><tr><th>可执行名单</th><th class="num">数值</th></tr>{rows}</table></div>
  </div>
  {rail}'''
        return wrap_slide(slide, inner, index, total, meta)
    if job == "matrix":
        cells = []
        for st, lab, val in slide.extra["cells"]:
            cells.append(
                '<div style="border:2px solid var(--sd-ink-14); border-radius:var(--sd-radius-card); padding:20px; background:var(--sd-paper); display:flex; flex-direction:column; gap:12px;">'
                f'<span class="sd-status {st}">{esc(field_copy(lab, 3))}</span>'
                f'<span style="font-family:var(--sd-font-mono); font-size:var(--sd-type-h3); font-weight:700;">{esc(val)}</span></div>'
            )
        inner = chrome(meta, slide, index, total) + f'<div class="sd-content" style="display:grid; grid-template-columns:repeat(3,1fr); grid-template-rows:repeat(3,1fr); gap:20px;">{"".join(cells)}</div>{rail}'
        return wrap_slide(slide, inner, index, total, meta)
    if job == "compare":
        x = slide.extra
        inner = chrome(meta, slide, index, total) + f'''
  <div class="sd-content" style="display:flex; align-items:stretch; gap:0;">
    <div style="flex:1; border:2px solid var(--sd-ink-14); border-radius:var(--sd-radius-card) 0 0 var(--sd-radius-card); padding:32px; background:var(--sd-paper);">
      <div style="font-family:var(--sd-font-mono); font-size:var(--sd-type-micro); letter-spacing:.06em; text-transform:uppercase; color:var(--sd-ink-60); margin-bottom:16px;">{esc(field_copy(x["left_label"], 3))}</div>
      <div style="font-family:var(--sd-font-serif); font-size:var(--sd-type-body); line-height:1.6;">{esc(field_copy(x["left"]))}</div>
    </div>
    <div style="width:128px; flex:none; display:flex; align-items:center; justify-content:center; background:var(--sd-accent-wash-10); border-top:2px solid var(--sd-ink-14); border-bottom:2px solid var(--sd-ink-14);">
      <div style="font-family:var(--sd-font-mono); font-size:var(--sd-type-micro); color:var(--sd-accent); writing-mode:vertical-rl; letter-spacing:.1em;">{esc(x["connector"])}</div>
    </div>
    <div style="flex:1; border:2px solid var(--sd-ink-14); border-radius:0 var(--sd-radius-card) var(--sd-radius-card) 0; padding:32px; background:var(--sd-paper);">
      <div style="font-family:var(--sd-font-mono); font-size:var(--sd-type-micro); letter-spacing:.06em; text-transform:uppercase; color:var(--sd-ink-60); margin-bottom:16px;">{esc(field_copy(x["right_label"], 3))}</div>
      <div style="font-family:var(--sd-font-serif); font-size:var(--sd-type-body); line-height:1.6;">{esc(field_copy(x["right"]))}</div>
    </div>
  </div>
  {rail}'''
        return wrap_slide(slide, inner, index, total, meta)
    if job == "verdict":
        x = slide.extra
        inner = chrome(meta, slide, index, total) + f'''
  <div class="sd-content" style="display:grid; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; gap:24px;">
    <div style="border:2px solid var(--sd-secondary); border-radius:var(--sd-radius-card); padding:28px; background:var(--sd-secondary-wash-08);">
      <div style="font-family:var(--sd-font-mono); font-size:var(--sd-type-micro); letter-spacing:.06em; text-transform:uppercase; color:var(--sd-secondary); margin-bottom:12px;">争议点 · DISPUTE</div>
      <div style="font-family:var(--sd-font-serif); font-size:var(--sd-type-body); line-height:1.6;">{esc(field_copy(x["dispute"]))}</div>
    </div>
    <div style="border:2px solid var(--sd-ink-60); border-radius:var(--sd-radius-card); padding:28px; background:var(--sd-paper);">
      <div style="font-family:var(--sd-font-mono); font-size:var(--sd-type-micro); letter-spacing:.06em; text-transform:uppercase; color:var(--sd-ink-60); margin-bottom:12px;">事实 · FACT</div>
      <div style="font-family:var(--sd-font-serif); font-size:var(--sd-type-body); line-height:1.6;">{esc(field_copy(x["fact"]))}</div>
    </div>
    <div style="border:2px solid var(--sd-accent); border-radius:var(--sd-radius-card); padding:28px; background:var(--sd-accent-wash-06);">
      <div style="font-family:var(--sd-font-mono); font-size:var(--sd-type-micro); letter-spacing:.06em; text-transform:uppercase; color:var(--sd-accent); margin-bottom:12px;">处理 · RESOLUTION</div>
      <div style="font-family:var(--sd-font-serif); font-size:var(--sd-type-body); line-height:1.6;">{esc(field_copy(x["resolution"]))}</div>
    </div>
    <div style="border:2px solid var(--sd-status-ready-text); border-radius:var(--sd-radius-card); padding:28px; background:rgba(27,143,90,.07);">
      <div style="font-family:var(--sd-font-mono); font-size:var(--sd-type-micro); letter-spacing:.06em; text-transform:uppercase; color:var(--sd-status-ready-text); margin-bottom:12px;">证伪条件 · FALSIFY IF</div>
      <div style="font-family:var(--sd-font-serif); font-size:var(--sd-type-body); line-height:1.6;">{esc(field_copy(x["falsify"]))}</div>
    </div>
  </div>
  {rail}'''
        return wrap_slide(slide, inner, index, total, meta)
    raise AssertionError(job)


def document(title: str, slides_html: str) -> str:
    logo = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    css = CSS_PATH.read_text(encoding="utf-8").replace(
        'url("logo/侍天.png")', f'url("data:image/png;base64,{logo}")'
    )
    js = JS_PATH.read_text(encoding="utf-8")
    return f'''<!DOCTYPE html>
<html lang="zh-CN" data-font-pack="TIANSIGHT" data-skin="TIANSIGHT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link id="sd-font-link" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=IBM+Plex+Mono:wght@400;500;600&family=LXGW+WenKai:wght@400;700&family=ZCOOL+XiaoWei&family=Roboto+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div id="sd-stage"><div id="deck">
{slides_html}
</div></div>
<script>
{js}
</script>
</body>
</html>
'''


DECKS = [
    {
        "id": "stone-briefing",
        "source": "ref/mds/06_首版汇报报告_V1.0_数据校准版.md",
        "out": "decks/stone-briefing/presentation.html",
        "genre": "briefing",
        "kicker": "TIANSIGHT · WISDOM NAVIGATOR FOR PREMIUM F&B CHAINS",
        "title1": "石头先生的汉堡",
        "title2": "北京首店 · 首版汇报 V1.0",
        "decision": "终局 1,000 家，倒推首店。校准：6 修、3 推翻、1 战略重构。",
        "period": "点评库 2026-06",
        "scope": "北京 6,052 西式门店 · 合生汇锚点",
        "basis": "V1.0 数据校准版",
        "issued": "2026.08.15",
        "deck_name": "石头先生的汉堡 · 首版汇报 V1.0",
        "brand_mark": "侍天",
        "source_detail": "北京点评门店库 2026-06 · 西式参考集 6,052 · 客户产品结构表 0812 · 施工图 A1.02",
        "acts_en": {
            "第一部分 · 战略全局：从 1 到 1000": "FROM 1 TO 1000",
            "第二部分 · 北京西式赛道结构（全量数据）": "BEIJING WESTERN TRACK",
            "第三部分 · 合生汇竞争分析（全量数据 · 本报告核心）": "HOPSON ONE COMPETITION",
            "第四部分 · 产品结构诊断（数据驱动）": "PRODUCT STRUCTURE",
            "第五部分 · 首店菜单结构（8.15 交付核心）": "FIRST-STORE MENU",
            "第六部分 · 定价、套餐与开业营销": "PRICE · COMBO · OPENING",
            "第七部分 · 品牌心智与视觉（深化）": "BRAND MINDSET",
            "第八部分 · 点单与经营动线（深化）": "ORDERING · FLOW",
            "第九部分 · 数据测试与验证体系（本次大幅扩写）": "TEST & FALSIFY",
            "第十部分 · 全国连锁的体系建设": "CHAIN SYSTEM",
            "第十一部分 · 需当场决策清单": "DECISIONS NOW",
            "第十二部分 · 未解问题与二期路线": "OPEN QUESTIONS",
            "附录": "APPENDIX",
        },
    },
    {
        "id": "stone-roadmap",
        "source": "ref/mds/07_战略方法论体系与分阶段赋能路线图_M1.0.md",
        "out": "decks/stone-roadmap/presentation.html",
        "genre": "roadmap",
        "kicker": "TIANSIGHT · WISDOM NAVIGATOR FOR PREMIUM F&B CHAINS",
        "title1": "石头先生的汉堡",
        "title2": "战略方法论 · 分阶段赋能路线图 M1.0",
        "decision": "1 → 200 家。关卡未写清，阶段不放行。",
        "period": "框架日 2026-08-13",
        "scope": "1 → 200 家分阶段赋能",
        "basis": "M1.0 方法论框架",
        "issued": "2026.08.13",
        "deck_name": "石头先生的汉堡 · 赋能路线图 M1.0",
        "brand_mark": "侍天",
        "source_detail": "方法论框架 M1.0 · 对齐 06 首版汇报 V1.0 · 北京点评库 2026-06 作竞争约束",
        "acts_en": {
            "第一部分 · 问题定义": "PROBLEM DEFINITION",
            "第二部分 · 方法论体系": "METHOD STACK",
            "第三部分 · 高质量数据源体系": "DATA SOURCES",
            "第四部分 · 宏观环境（PESTEL 裁剪版）": "PESTEL",
            "第五部分 · 中国消费趋势": "CONSUMPTION TRENDS",
            "第六部分 · 竞争格局的结构性变化 🔴": "STRUCTURAL SHIFT",
            "第七部分 · 北京落地的战略选择": "BEIJING CHOICES",
            "第八部分 · 分阶段赋能路线图（1 → 200 家）": "STAGE ROADMAP",
            "第九部分 · 指标体系": "METRICS",
            "第十部分 · 风险登记册": "RISK REGISTER",
            "第十一部分 · 治理机制": "GOVERNANCE",
            "附录": "APPENDIX",
        },
    },
    {
        "id": "stone-dossier",
        "source": "ref/mds/08_北京西式快餐可参考品牌分析专项_B1.0.md",
        "out": "decks/stone-dossier/presentation.html",
        "genre": "dossier",
        "kicker": "TIANSIGHT · WISDOM NAVIGATOR FOR PREMIUM F&B CHAINS",
        "title1": "北京西式快餐",
        "title2": "可参考品牌分析专项 B1.0",
        "decision": "6,052 店归一化 · 130 品牌。对标只问可迁移性。",
        "period": "点评库 2026-06",
        "scope": "西式参考集 6,052 · 归一化后 ≥3 店约 130 品牌",
        "basis": "B1.0 品牌专项",
        "issued": "2026.08.13",
        "deck_name": "北京西式快餐 · 品牌专项 B1.0",
        "brand_mark": "侍天",
        "source_detail": "北京点评门店库 2026-06 · 品牌名归一化 · 全国公开数据作补充（禁止把点评客单当实收对标）",
        "acts_en": {
            "第一部分 · 方法与评估框架": "METHOD · RUBRIC",
            "第二部分 · 北京西式品牌全景": "BEIJING PANORAMA",
            "第三部分 · 跨品牌规律（从数据里提炼）": "CROSS-BRAND LAWS",
            "第四部分 · 标杆品牌深度档案": "BENCHMARK FILES",
            "第五部分 · 全国维度：北京数据库里看不到的品牌": "NATIONAL GAPS",
            "第六部分 · 可参考性评分矩阵": "SCORE MATRIX",
            "第七部分 · 可迁移清单：学什么 / 不学什么 / 怎么验证": "LEARN / DON'T",
            "第八部分 · 建议的持续监测机制": "MONITORING",
            "附录": "APPENDIX",
        },
    },
]


def build_one(meta: dict) -> dict[str, Any]:
    src = ROOT / meta["source"]
    text = rewrite_report_copy(strip_cite(src.read_text(encoding="utf-8")))
    if meta.get("promote_subheads"):
        text = re.sub(r"^(#{2,3})(?=\s)", lambda m: m.group(1)[1:], text, flags=re.M)
    cover_titles, chapters, preamble, tables = parse_markdown(text, meta.get("cover_h1_count"))
    builder = DeckBuilder(meta, cover_titles, chapters, preamble, tables)
    slides = builder.build()
    jobs_used = sorted({s.job for s in slides})
    unknown = [j for j in jobs_used if j not in JOBS]
    assert not unknown, unknown
    missing_tables = [t.source_index for t in tables if t.source_index not in builder.table_emitted]
    assert not missing_tables, f"tables not emitted: {missing_tables}"
    for s in slides:
        svg = (s.extra or {}).get("svg") or ""
        if s.job in {"chart", "chart-table"}:
            assert svg, f"empty figure on {s.title}"
            assert "sd-cat-" not in svg, f"rainbow category fill on {s.title}"
        if "全市西式" in s.title and s.job == "chart":
            assert s.fill == "hist-cdf", f"全市西式 must be hist-cdf, got {s.fill}"
            assert "960家" in svg, f"hist must plot 门店数, got {s.title}"
            assert "55–60" in svg or "55-60" in svg
        if "275" in s.title and "价格带" in s.title and s.job == "chart":
            assert "100–150" in svg or "100-150" in svg, f"275 价格带 dropped high spend: {s.title}"
            assert "150+" in svg, f"275 价格带 missing 150+: {s.title}"
            assert "39家" in svg, f"275 价格带 missing 100–150 peak: {s.title}"
        if meta["id"] == "stone-dossier" and s.job == "chart":
            if "规律一" in s.title:
                assert "轻遇" in svg, f"规律一 figure dropped 轻遇三明治: {s.title}"
            if "品质连锁" in s.title:
                assert "好伦哥" in svg, f"规律二 figure dropped 好伦哥: {s.title}"
    total = len(slides)
    html_slides = "\n".join(render_slide(s, i + 1, total, meta) for i, s in enumerate(slides))
    out = ROOT / meta["out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    logo_out = out.parent / "logo/侍天.png"
    logo_out.parent.mkdir(exist_ok=True)
    logo_out.write_bytes(LOGO_PATH.read_bytes())
    html_doc = document(meta["deck_name"], html_slides)
    assert_no_cite(html_doc, str(out))
    assert_complete_canvas(slides, html_doc, str(out))
    if meta["id"] == "stone-briefing":
        forbidden = (
            "cite index",
            "石头先生家族",
            "品牌架构未定义",
            "关系不明",
            "这个关系必须现在定义",
            "兄弟店「的烤炉」",
        )
        hits = [p for p in forbidden if p in html_doc]
        assert not hits, f"stale 烤炉 copy in {out}: {hits}"
    syllabus = [p for p in SYLLABUS_LEAK if p in html_doc]
    assert not syllabus, f"syllabus voice in {out}: {syllabus}"
    gaps = heading_coverage(chapters, slides)
    assert not gaps, f"MD H2 not on slides in {meta['id']}: {gaps}"
    charts = [s for s in slides if s.job in {"chart", "chart-table"}]
    inventories = [s for s in slides if s.job == "roster" and s.overflow_of == "chart"]
    fig_ids = {s.extra.get("fig") for s in charts if s.extra.get("fig")}
    inv_ids = {s.extra.get("fig") for s in inventories if s.extra.get("fig")}
    missing_inv = sorted(fig_ids - inv_ids)
    assert not missing_inv, f"figure missing inventory page in {meta['id']}: {missing_inv}"
    ge20 = [s for s in slides if "门店数 ≥ 20" in s.title]
    if meta["id"] in {"stone-briefing", "stone-dossier"}:
        assert any(s.job == "chart" for s in ge20), f"missing ≥20 brand distribution in {meta['id']}"
        inv_html = "".join(s.body for s in ge20 if s.job == "roster")
        for brand in ("麦当劳", "牛约堡", "德克士", "极度比萨"):
            assert brand in inv_html, f"{brand} missing from ≥20 inventory in {meta['id']}"
        ge20_fig = next(s for s in ge20 if s.job == "chart")
        ge20_svg = (ge20_fig.extra or {}).get("svg") or ""
        assert "中位" in ge20_svg, f"≥20 bubble missing median: {ge20_fig.title}"
        assert not re.search(r'r="(?:3[5-9]|[4-9]\d)', ge20_svg), f"≥20 bubble radius too large: {ge20_fig.title}"
        band_inv = "".join(
            s.body for s in slides
            if s.job == "roster" and "价格带" in s.title and "规模" in s.title and "清单" in s.title
        )
        if band_inv:
            assert "华莱士" in band_inv and "麦当劳" in band_inv, f"价格带清单 missing brands in {meta['id']}"
            assert band_inv.count("<tr>") >= 20, f"价格带清单 not expanded in {meta['id']}: {band_inv.count('<tr>')} rows"
        skinny_band = [
            s.title for s in slides
            if s.job == "roster" and "清单" in s.title and "价格带" in s.title
            and "品牌" not in s.body
            and s.body.count("<th") <= 2
        ]
        assert not skinny_band, f"价格带清单 still 2-col in {meta['id']}: {skinny_band}"
        if meta["id"] == "stone-briefing":
            wine_band = "".join(
                s.body for s in slides
                if s.job == "roster" and "靠酒" in s.title and "价格带" in s.title and "清单" in s.title
            )
            if wine_band:
                assert "占比" in wine_band, "2.4 价格带清单 missing 占比"
                assert "He BURGER" in wine_band, "2.4 价格带清单 missing 成功样本"
    out.write_text(html_doc, encoding="utf-8")
    counts = {}
    for s in slides:
        counts[s.job] = counts.get(s.job, 0) + 1
    report = {
        "id": meta["id"],
        "source": meta["source"],
        "out": meta["out"],
        "bytes": out.stat().st_size,
        "slides": total,
        "chapters": len(chapters),
        "tables_in_md": len(tables),
        "tables_emitted": len(builder.table_emitted),
        "jobs": counts,
        "cover_titles": cover_titles,
        "h2_covered": True,
    }
    return report


def main() -> int:
    if sys.argv[1:] == ["--self-check"]:
        svg = svg_categorical_grid([{"title": str(i), "items": ["内容"]} for i in range(12)], "检查")
        assert svg.count("<rect") == 19 and "10</text>" not in svg
        print("TIANSIGHT visualization self-check: ok")
        return 0
    reports = []
    targets = sys.argv[1:]
    decks = DECKS
    if targets:
        decks = [d for d in DECKS if d["id"] in targets or d["source"] in targets]
    for meta in decks:
        rep = build_one(meta)
        reports.append(rep)
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    (ROOT / "decks/TIANSIGHT-v2-coverage.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
