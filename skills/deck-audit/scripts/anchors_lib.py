#!/usr/bin/env python3
"""Shared anchor extraction for deck-audit scripts."""

from __future__ import annotations

import re

NUMBER_RE = re.compile(
    r"(?<![\w.])("
    r"¥\s?[\d,]+(?:\.\d+)?|"
    r"\$\s?[\d,]+(?:\.\d+)?|"
    r"[\d,]+(?:\.\d+)?\s*%|"
    r"[\d,]+(?:\.\d+)?\s*％|"
    r"\d+\s*[:/]\s*\d+|"
    r"[\d,]+(?:\.\d+)?\s*(?:天|店|行|列|页|个|款|SKU|sku|万|亿)?"
    r")(?![\w.])"
)
DATE_RE = re.compile(r"\b\d{4}[-/.年]\d{1,2}([-/.月]\d{1,2})?日?\b")
CJK_NOUN_RE = re.compile(r"[\u4e00-\u9fff]{2,}(?:[ \t]*[A-Za-z0-9一二三四五六七八九十]+)?")
TITLE_CASE_RE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b")
TABLE_CELL_RE = re.compile(r"^\s*\|(.+)\|\s*$", re.M)

STOP_CJK = {
    "封面",
    "续",
    "合计",
    "占比",
    "备注",
    "目录",
    "章节",
    "数据",
    "分析",
    "报告",
    "结论",
    "来源",
    "口径",
    "全文",
    "本次",
    "实际",
    "使用",
    "如下",
    "以上",
    "以下",
    "其中",
    "以及",
    "或者",
    "因为",
    "所以",
    "如果",
    "可以",
    "需要",
    "进行",
    "通过",
    "根据",
    "对应",
    "相关",
    "主要",
    "其他",
    "全部",
    "部分",
    "第一",
    "第二",
    "第三",
    "单元",
    "页码",
}
STOP_EN = {
    "the",
    "and",
    "of",
    "to",
    "in",
    "for",
    "on",
    "with",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "this",
    "that",
    "from",
    "by",
    "as",
    "at",
    "or",
    "be",
    "it",
    "its",
    "not",
    "but",
    "cover",
    "page",
    "slide",
    "deck",
    "table",
    "chart",
    "note",
    "notes",
    "source",
    "takeaway",
    "role",
    "units",
    "roster",
    "statement",
    "chapter",
    "kpi",
    "none",
}

NUMERIC_KINDS = {"number", "percent", "currency", "ratio", "date", "quantity", "table-cell"}


def normalize_value(raw: str) -> str:
    s = raw.strip()
    s = re.sub(r"\s+", "", s.replace("，", ",").replace("％", "%"))
    s = s.replace(",", "")
    s = re.sub(r"(?<!\d)(-?\d+)\.0(?=\D|$)", r"\1", s)
    s = re.sub(r"(?<!\d)0+(\d+)(?=\D|$)", r"\1", s)
    return s.lower()


def classify_token(raw: str) -> str:
    t = raw.strip()
    if "%" in t or "％" in t:
        return "percent"
    if t.startswith("¥") or t.startswith("$"):
        return "currency"
    if re.search(r"[:/]", t) and re.search(r"\d", t):
        return "ratio"
    if DATE_RE.search(t):
        return "date"
    if re.search(r"(天|店|行|列|页|个|款|sku|万|亿)$", t, re.I):
        return "quantity"
    if re.fullmatch(r"[\d,]+(?:\.\d+)?", t.replace(" ", "")):
        return "number"
    return "proper-noun"


def extract_from_text(text: str, origin: str) -> list[dict]:
    found: list[dict] = []
    seen: set[tuple[str, str]] = set()
    # Neutralize unit ids so u-0001 does not yield number 0001
    text = re.sub(r"\bu-\d{4}\b", " ", text, flags=re.I)
    # Neutralize page ids p-0001 similarly
    text = re.sub(r"\bp-\d{4}\b", " ", text, flags=re.I)

    def add(raw: str, kind: str) -> None:
        raw = raw.strip()
        if not raw or len(raw) > 80:
            return
        if re.fullmatch(r"u-\d{4}", raw, re.I):
            return
        if kind == "proper-noun":
            core = re.sub(r"\s+", "", raw)
            if core in STOP_CJK or raw.lower() in STOP_EN:
                return
            if len(core) < 2:
                return
        key = (kind, normalize_value(raw))
        if key in seen:
            return
        seen.add(key)
        found.append(
            {
                "raw": raw,
                "norm": normalize_value(raw),
                "kind": kind,
                "origin": origin,
            }
        )

    for m in DATE_RE.finditer(text):
        add(m.group(0), "date")

    for m in NUMBER_RE.finditer(text):
        add(m.group(1), classify_token(m.group(1)))

    for m in TABLE_CELL_RE.finditer(text):
        cells = [c.strip() for c in m.group(1).split("|")]
        for cell in cells:
            if not cell or set(cell) <= set("-: *"):
                continue
            if re.search(r"\d", cell) or (2 <= len(cell) <= 40):
                add(cell, "table-cell")

    for m in CJK_NOUN_RE.finditer(text):
        add(m.group(0), "proper-noun")

    for m in TITLE_CASE_RE.finditer(text):
        if m.group(0).lower() not in STOP_EN:
            add(m.group(0), "proper-noun")

    return found
