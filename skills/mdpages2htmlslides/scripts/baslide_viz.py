#!/usr/bin/env python3
"""Load Baslide01's TIANSIGHT figure recipes (pick_fill + svg_figure).

Does not invent a 17th L3 id. Builder-only recipe names (hbar, timeline, …)
are mapped onto the locked 16 before they are written into deck-plan.json.
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LOCKED_L3 = (
    "sankey",
    "funnel",
    "waterfall",
    "radar",
    "venn",
    "bubble",
    "hist-cdf",
    "pareto",
    "slope",
    "diverging-bar",
    "quadrant",
    "heatmap",
    "treemap",
    "network",
    "line-dual",
    "calendar",
)

RECIPE_TO_L3 = {
    "hbar": "diverging-bar",
    "timeline": "calendar",
    "weight-shift": "heatmap",
    "slots": "treemap",
    "price-ladder": "slope",
    "number-axis": "line-dual",
    "stack": "network",
}

# Longer needles first.
FILL_HINTS = (
    ("四象限", "quadrant"),
    ("帕累托", "pareto"),
    ("桑基", "sankey"),
    ("漏斗", "funnel"),
    ("瀑布", "waterfall"),
    ("雷达", "radar"),
    ("韦恩", "venn"),
    ("维恩", "venn"),
    ("气泡", "bubble"),
    ("热力", "heatmap"),
    ("树图", "treemap"),
    ("矩形树", "treemap"),
    ("斜率", "slope"),
    ("坡度", "slope"),
    ("直方图", "hist-cdf"),
    ("分箱", "hist-cdf"),
    ("箱线", "hist-cdf"),
    ("网络", "network"),
    ("双轴", "line-dual"),
    ("日历", "calendar"),
    ("象限", "quadrant"),
    ("二八", "pareto"),
    ("sankey", "sankey"),
    ("funnel", "funnel"),
    ("waterfall", "waterfall"),
    ("radar", "radar"),
    ("venn", "venn"),
    ("bubble", "bubble"),
    ("pareto", "pareto"),
    ("heatmap", "heatmap"),
    ("treemap", "treemap"),
    ("quadrant", "quadrant"),
    ("hist-cdf", "hist-cdf"),
    ("diverging", "diverging-bar"),
    ("line-dual", "line-dual"),
)

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
    "calendar": "从左到右是阶段顺序",
    "sankey": "流量宽=量；分叉是去向，不是装饰带",
    "venn": "重叠才是交集；面积不按精确比例时要写出口径",
    "network": "点是实体，线是关系；不要把流程画成装饰网",
}

_BUILDER = None


def default_baslide() -> Path:
    env = os.environ.get("BASLIDE_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve()
    repo = here.parents[3]
    bundled = repo / "modules" / "baslide01"
    if (bundled / "scripts" / "build-TIANSIGHT-deck.py").is_file():
        return bundled
    return Path.home() / "cpro01/0thebrain01/baslide01"


def load_builder(baslide: Path | None = None) -> Any:
    global _BUILDER
    if _BUILDER is not None:
        return _BUILDER
    root = Path(baslide).resolve() if baslide else default_baslide()
    script = root / "scripts" / "build-TIANSIGHT-deck.py"
    if not script.is_file():
        raise FileNotFoundError(f"Baslide01 builder missing: {script}")
    spec = importlib.util.spec_from_file_location("baslide01_build_tiansight", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    _BUILDER = mod
    return mod


def lock_fill(recipe: str | None) -> str | None:
    if not recipe:
        return None
    mapped = RECIPE_TO_L3.get(recipe, recipe)
    if mapped in LOCKED_L3:
        return mapped
    return None


def hint_fill(text: str) -> str | None:
    if not text:
        return None
    blob = text
    lower = text.lower()
    for needle, fid in FILL_HINTS:
        if needle.isascii():
            if needle.lower() in lower:
                return fid
        elif needle in blob:
            return fid
    return None


def first_gfm_table(md: str, builder: Any):
    lines = (md or "").replace("\r\n", "\n").split("\n")
    for i, line in enumerate(lines):
        if "|" not in line:
            continue
        if i + 1 >= len(lines):
            continue
        nxt = lines[i + 1].strip()
        if not (("-" in nxt or "—" in nxt) and "|" in nxt):
            continue
        table, _ = builder.parse_table(lines, i)
        if table.headers and table.rows:
            return table
    return None


def series_from_table(table, title: str, builder: Any) -> tuple[list[str], list[float]]:
    rows = [r for r in table.rows if not builder.is_sum_row(r)]
    if not rows:
        return [], []
    lcol = builder.label_col(table)
    nums = builder.numeric_cols(table)
    if not nums:
        return [], []
    vc = builder.pick_value_col(table, nums, title)
    labels: list[str] = []
    values: list[float] = []
    for r in rows:
        cell = r[vc] if vc < len(r) else ""
        parsed = builder.parse_num(cell)
        if parsed is not None:
            labels.append(builder.strip_md(r[lcol] if lcol < len(r) else r[0]))
            values.append(float(parsed))
    return labels, values


def pick_recipe(title: str, material: str, table, labels: list[str], values: list[float], builder: Any) -> str | None:
    hinted = hint_fill(f"{title}\n{material}")
    if hinted:
        return hinted
    if table is None or not values:
        if any(ch in (material or "") for ch in "┌│└─█"):
            return "network"
        return None
    recipe = builder.pick_fill(title, table, labels, values)
    return recipe


@dataclass
class Figure:
    fill: str | None
    recipe: str | None
    svg: str
    table_html: str
    unit: str
    caption: str


def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def table_preview_html(table, builder: Any, limit: int = 8) -> str:
    if table is None or not table.headers:
        return ""
    rows = [r for r in table.rows if not builder.is_sum_row(r)][:limit]
    head = "".join(f"<th>{_esc(builder.strip_md(h))}</th>" for h in table.headers)
    body = []
    for row in rows:
        tds = []
        for j, cell in enumerate(row[: len(table.headers)]):
            text = builder.strip_md(cell)
            num = j > 0 and bool(re.search(r"[\d%％¥]", text))
            tds.append(f'<td class="num">{_esc(text)}</td>' if num else f"<td>{_esc(text)}</td>")
        body.append("<tr>" + "".join(tds) + "</tr>")
    return f'<table class="sd-table"><tr>{head}</tr>{"".join(body)}</table>'


def _custom_svg(fill: str, labels: list[str], values: list[float]) -> str | None:
    """The four graph/set/time recipes Baslide previously disguised as bars."""
    labs = [str(label)[:14] for label in labels[:8]] or ["A", "B", "C", "D"]
    vals = values[: len(labs)] or [4.0, 3.0, 2.0, 1.0]
    text = lambda x, y, value, anchor="middle": f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="var(--gf-ink,var(--sd-ink-100))" font-size="18">{_esc(value)}</text>'
    if fill == "calendar":
        xs = [100 + i * 930 / max(1, len(labs) - 1) for i in range(len(labs))]
        body = '<path d="M100 250H1030" stroke="var(--gf-grid,var(--sd-ink-28))" stroke-width="4"/>'
        for x, label, value in zip(xs, labs, vals):
            body += f'<circle cx="{x:.1f}" cy="250" r="14" fill="var(--gf-accent,var(--sd-accent))"/>' + text(x, 220, label) + text(x, 292, value)
    elif fill == "venn":
        body = '<circle cx="470" cy="245" r="150" fill="var(--gf-accent,var(--sd-accent))" fill-opacity=".28"/><circle cx="690" cy="245" r="150" fill="var(--gf-negative,var(--sd-secondary))" fill-opacity=".25"/>'
        body += text(410, 250, labs[0]) + text(750, 250, labs[1] if len(labs) > 1 else "B") + text(580, 250, "∩")
    elif fill == "network":
        import math
        pts = [(585 + 205 * math.cos(i * 2 * math.pi / len(labs)), 250 + 175 * math.sin(i * 2 * math.pi / len(labs))) for i in range(len(labs))]
        body = "".join(f'<line x1="{pts[i][0]:.1f}" y1="{pts[i][1]:.1f}" x2="{pts[(i+1)%len(pts)][0]:.1f}" y2="{pts[(i+1)%len(pts)][1]:.1f}" stroke="var(--gf-grid,var(--sd-ink-28))" stroke-width="4"/>' for i in range(len(pts)))
        body += "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="28" fill="var(--gf-accent,var(--sd-accent))"/>{text(x, y+6, label)}' for (x, y), label in zip(pts, labs))
    elif fill == "sankey":
        scale = 170 / max(max(abs(v) for v in vals), 1)
        body = ""
        for i, (label, value) in enumerate(zip(labs[:4], vals[:4])):
            y = 85 + i * 95
            width = max(10, abs(value) * scale)
            body += f'<path d="M210 {y} C430 {y}, 680 {250}, 930 {250}" fill="none" stroke="var(--gf-accent,var(--sd-accent))" stroke-opacity=".45" stroke-width="{width:.1f}"/>' + text(180, y + 6, label, "end")
        body += '<rect x="925" y="150" width="30" height="200" fill="var(--gf-ink,var(--sd-ink-100))"/>'
    else:
        return None
    return f'<svg viewBox="0 0 1170 500" role="img" aria-label="{_esc(fill)} visualization" data-viz="{_esc(fill)}">{body}</svg>'


def _raw_heatmap_svg(table, builder: Any) -> str:
    """Heatmap raw cells so mixed units never inherit one column's suffix."""
    rows = [row for row in table.rows if not builder.is_sum_row(row)][:8]
    nums = builder.numeric_cols(table)[:6]
    left, top, right, bottom = 220, 54, 24, 28
    cell_w = (1170 - left - right) / max(1, len(nums))
    cell_h = (500 - top - bottom) / max(1, len(rows))
    body = ""
    for col, index in enumerate(nums):
        body += f'<text x="{left + (col + .5) * cell_w:.1f}" y="32" text-anchor="middle" fill="var(--gf-ink,var(--sd-ink-100))" font-size="18">{_esc(builder.strip_md(table.headers[index]))}</text>'
    for row_index, row in enumerate(rows):
        body += f'<text x="{left - 12}" y="{top + (row_index + .62) * cell_h:.1f}" text-anchor="end" fill="var(--gf-ink,var(--sd-ink-100))" font-size="18">{_esc(builder.strip_md(row[builder.label_col(table)]))}</text>'
        for col, index in enumerate(nums):
            raw = builder.strip_md(row[index] if index < len(row) else "—")
            value = builder.parse_num(raw)
            shade = "var(--sd-seq-100)" if value is None or abs(value) < 50 else "var(--sd-accent)" if abs(value) < 100 else "var(--sd-seq-600)"
            ink = "var(--sd-ink-100)" if shade == "var(--sd-seq-100)" else "var(--sd-paper)"
            x, y = left + col * cell_w, top + row_index * cell_h
            body += f'<rect x="{x + 3:.1f}" y="{y + 3:.1f}" width="{cell_w - 6:.1f}" height="{cell_h - 6:.1f}" fill="{shade}" rx="3"/>'
            body += f'<text x="{x + cell_w / 2:.1f}" y="{y + cell_h * .64:.1f}" text-anchor="middle" fill="{ink}" font-size="18">{_esc(raw)}</text>'
    return f'<svg viewBox="0 0 1170 500" role="img" aria-label="heatmap visualization" data-viz="heatmap">{body}</svg>'


def figure_for_page(
    title: str,
    material: str,
    *,
    preset_fill: str | None = None,
    baslide: Path | None = None,
) -> Figure | None:
    builder = load_builder(baslide)
    table = first_gfm_table(material, builder)
    labels, values = series_from_table(table, title, builder) if table else ([], [])
    recipe = preset_fill or pick_recipe(title, material, table, labels, values, builder)
    fill = lock_fill(recipe)
    if fill is None and not values:
        return None
    if fill is None:
        recipe = recipe or "hbar"
        fill = lock_fill(recipe) or "diverging-bar"
    unit = ""
    caption = ""
    value_header = ""
    vcols = None
    if table is not None:
        nums = builder.numeric_cols(table)
        if nums:
            vc = builder.pick_value_col(table, nums, title)
            value_header = table.headers[vc] if vc < len(table.headers) else ""
            sample = " ".join(builder.strip_md(row[vc] if vc < len(row) else "") for row in table.rows[:8])
            unit = builder.unit_of(value_header)
            if unit == "%" and "%" not in sample and "％" not in sample:
                unit = ""
            if unit == "家" and "家" not in sample and not any(word in value_header for word in ("门店", "商户")):
                unit = ""
            if fill == "slope" and builder.slope_col_pair(table, nums) is None:
                groups = {}
                for index in nums:
                    cells = " ".join(builder.strip_md(row[index] if index < len(row) else "") for row in table.rows[:8])
                    column_unit = "%" if "%" in cells or "％" in cells else "元" if "元" in cells else ""
                    groups.setdefault(column_unit, []).append(index)
                vcols = next((group[:2] for key, group in groups.items() if key and len(group) >= 2), None)
                if vcols:
                    unit = next(key for key, group in groups.items() if group[:2] == vcols)
        caption = builder.figure_caption(recipe or fill, value_header, len(labels), unit, title)
        caption = re.sub(r"^n=\d+ · ", "", caption)
    svg = (_raw_heatmap_svg(table, builder) if fill == "heatmap" and table is not None else None) or _custom_svg(fill, labels, values) or builder.svg_figure(
        recipe or fill,
        labels,
        values,
        table=table,
        vcols=vcols,
        unit=unit,
        caption=caption,
        title=title,
    )
    svg = re.sub(r" · 标 \d+ 家，其余见清单", " · 其余见清单", svg or "")
    if not svg or "<svg" not in svg:
        return None
    return Figure(
        fill=fill,
        recipe=recipe,
        svg=svg,
        table_html=table_preview_html(table, builder),
        unit=unit,
        caption=caption,
    )


def assign_page_fill(title: str, material: str, role: str, *, baslide: Path | None = None) -> dict[str, str | None]:
    """Return {fill, recipe, how_to_read} for deck-plan. fill is locked L3 or null."""
    if role not in {"chart", "chart-table"}:
        hinted = hint_fill(f"{title}\n{material}")
        return {"fill": hinted, "recipe": hinted, "how_to_read": HOW_FOR_FILL.get(hinted or "", "") if hinted else ""}
    try:
        builder = load_builder(baslide)
    except FileNotFoundError:
        hinted = hint_fill(f"{title}\n{material}")
        return {"fill": hinted, "recipe": hinted, "how_to_read": HOW_FOR_FILL.get(hinted or "", "")}
    table = first_gfm_table(material, builder)
    labels, values = series_from_table(table, title, builder) if table else ([], [])
    recipe = pick_recipe(title, material, table, labels, values, builder)
    fill = lock_fill(recipe)
    return {
        "fill": fill,
        "recipe": recipe,
        "how_to_read": HOW_FOR_FILL.get(fill or "", ""),
    }
