#!/usr/bin/env python3
"""Cut original ref MD/HTML into MECE slide-type sample files. Do not rewrite prose."""
from __future__ import annotations

import html as htmlmod
import json
import re
from pathlib import Path

ROOT = Path("/Users/af/cpro01/0thebrain01/baslide01")
REF = ROOT / "ref"
OUT = ROOT / "skills/md-to-html-slides/samples"
HTML_SEL = Path("/tmp/baslide-samples/html-selected.json")
HTML_FIGS = Path("/tmp/baslide-samples/html-figs.json")

FILES = {
    "qing": REF / "清水亭_主辅佐引产品结构诊断报告 (4).md",
    "html": REF / "清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html",
    "r06": REF / "06_首版汇报报告_V1.0_数据校准版.md",
    "r07": REF / "07_战略方法论体系与分阶段赋能路线图_M1.0.md",
    "r08": REF / "08_北京西式快餐可参考品牌分析专项_B1.0.md",
    "sid": REF / "侍天TIANSIGHT_分析体系Part1.md",
    "sby": REF / "苏帮袁_菜单分析维度体系_第一性原理.md",
}

REL = {k: str(v.relative_to(ROOT)) for k, v in FILES.items()}

CACHE: dict[str, list[str]] = {}


def lines_of(key: str) -> list[str]:
    if key not in CACHE:
        CACHE[key] = FILES[key].read_text(encoding="utf-8").splitlines()
    return CACHE[key]


def cut(key: str, start: int, end: int) -> str:
    rows = lines_of(key)
    chunk = rows[start - 1 : end]
    return "\n".join(chunk).rstrip() + "\n"


def h1s(key: str) -> str:
    """Verbatim H1 lines — implicit TOC / chapter inventory."""
    rows = [r for r in lines_of(key) if r.startswith("# ") and not r.startswith("##")]
    return "\n".join(rows).rstrip() + "\n"


def fence(text: str) -> str:
    return "```\n" + text.rstrip() + "\n```\n"


def sample_md(title: str, src: str, loc: str, genre: str, body: str, note: str = "") -> str:
    bits = [f"### {title}", "", f"- source: `{src}` · {loc}", f"- genre: `{genre}`"]
    if note:
        bits.append(f"- note: {note}")
    bits += ["", fence(body), ""]
    return "\n".join(bits)


def html_slide(sel: list[dict], i: int) -> dict:
    for s in sel:
        if s["i"] == i:
            return s
    raise KeyError(i)


def html_block(s: dict) -> str:
    parts = []
    parts.append(f"class: {s['cls']}")
    if s.get("chips"):
        parts.append("chips: " + " | ".join(s["chips"]))
    if s.get("h1"):
        parts.append("h1: " + " / ".join(s["h1"]))
    if s.get("h2"):
        parts.append("h2: " + " / ".join(s["h2"]))
    if s.get("src"):
        parts.append("SOURCE: " + " | ".join(s["src"]))
    if s.get("take"):
        parts.append("TAKEAWAY: " + " | ".join(s["take"]))
    parts.append("")
    parts.append(s.get("text") or "")
    if s.get("tables"):
        parts.append("\n--- tables (first rows) ---\n")
        parts.append("\n\n".join(s["tables"]))
    return "\n".join(parts).rstrip() + "\n"


REPORT = ROOT / "ref" / "REPORT-md-to-html-slide-types.md"

JOB_IDS = [
    "cover", "toc", "chapter", "readme", "statement", "kpi",
    "roster", "chart", "chart-table", "matrix", "compare", "verdict",
]
VIZ_IDS = [
    "sankey", "funnel", "waterfall", "radar", "venn", "bubble", "hist-cdf",
    "pareto", "slope", "diverging-bar", "quadrant", "heatmap", "treemap",
    "network", "line-dual", "calendar",
]
VIZ_FAMILY = {
    "sankey": "flow",
    "funnel": "part-to-whole",
    "waterfall": "deviation",
    "radar": "correlation",
    "venn": "part-to-whole",
    "bubble": "magnitude",
    "hist-cdf": "distribution",
    "pareto": "ranking",
    "slope": "ranking",
    "diverging-bar": "deviation",
    "quadrant": "correlation",
    "heatmap": "distribution",
    "treemap": "part-to-whole",
    "network": "flow",
    "line-dual": "change over time",
    "calendar": "change over time",
}
RETIRED_TABLE = {
    "sum-roster": "roster",
    "kpi-cards": "kpi",
    "state-matrix": "matrix",
    "dual-calibre": "compare",
    "profile-card": "compare",
    "falsify-quad": "verdict",
}


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def strip_h1(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        if lines and lines[0].strip() == "":
            lines = lines[1:]
    return "\n".join(lines)


def demote_headings(text: str, by: int = 1) -> str:
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence and line.startswith("#"):
            n = 0
            while n < len(line) and line[n] == "#":
                n += 1
            if n and (n == len(line) or line[n] == " "):
                line = "#" * min(n + by, 6) + line[n:]
        out.append(line)
    return "\n".join(out)


def include_sample(path: Path, heading: str) -> str:
    raw = path.read_text(encoding="utf-8")
    body = demote_headings(strip_h1(raw), 1)
    return f"{heading}\n\n{body.rstrip()}\n"


def assemble_report(cov_rows: list[str]) -> None:
    """One reading copy: taxonomy + every original sample."""
    parts: list[str] = []

    toc_jobs = "\n".join(f"   - [`{jid}`](#l2-{jid})" for jid in JOB_IDS)
    toc_viz = "\n".join(f"   - [`{vid}`](#l3-viz-{vid})" for vid in VIZ_IDS)

    parts += [
        "# MD → HTML slide types · complete sample report",
        "",
        "One file. Taxonomy lock + original content per type. Prose is verbatim from `ref/`. SVG omitted. HTML tables truncated to 8 rows.",
        "",
        "- Date: 2026-08-14",
        "- Canvas: **1440×810** · skin **TIANSIGHT**",
        "- Lock: **5 genres · 4 L1 shells · 12 L2 jobs · 16 L3 viz**",
        "- Tables: one mark family on `body` (row budget lives on the L2 job, not a parallel type layer)",
        "- Viz pick: FT Visual Vocabulary question → one of 16 recipes (or `null`)",
        "- Per-type files (regenerable): `skills/md-to-html-slides/samples/`",
        "- Regenerator: `python3 skills/md-to-html-slides/scripts/extract-samples.py`",
        "- Audit companion: [`AUDIT-md-to-html-taxonomy.md`](AUDIT-md-to-html-taxonomy.md)",
        "",
        "Size each template so the **densest** sample in that type still fits SOURCE + HOW TO READ + TAKEAWAY. Do not add a 13th L2 job.",
        "",
        "## Contents",
        "",
        "1. [How to use](#1-how-to-use)",
        "2. [Corpus](#2-corpus)",
        "3. [Locked taxonomy](#3-locked-taxonomy)",
        "4. [Two-model pipeline](#4-two-model-pipeline)",
        "5. [Coverage matrix](#5-coverage-matrix)",
        "6. [L2 jobs](#6-l2-jobs)",
        toc_jobs,
        "7. [Overflow (`续`)](#7-overflow-续)",
        "8. [L3 viz recipes](#8-l3-viz-recipes)",
        toc_viz,
        "9. [Appendix E chart menu](#9-appendix-e-chart-menu)",
        "10. [Folded types and empties](#10-folded-types-and-empties)",
        "11. [Do not](#11-do-not)",
        "",
        "---",
        "",
        "## 1 How to use",
        "",
        "1. Pick **genre** from the source MD (`diagnosis` `system` `briefing` `roadmap` `dossier`).",
        "2. Classify each chunk as one **L2 job**. Bind the **L1 shell**. Name the **L3 viz** `fill` (or `null`). Table row budget comes from the L2 job.",
        "3. Design / fill the HTML so the densest original sample below still fits 1440×810.",
        "4. If a table exceeds the row budget, emit the **same job** with `overflow_of` and title suffix `续`.",
        "5. Quote, question, timeline, diagram, playbook, and brand profile fold into existing L2 jobs — see §10.",
        "6. `text-image` `image-grid` `image-hero` never appear in this MD corpus. Keep them for Guizang only.",
        "",
        "---",
        "",
        "## 2 Corpus",
        "",
        "| File | Role | Grade | Est. pages |",
        "|---|---|---|---|",
        "| `清水亭_主辅佐引产品结构诊断报告 (4).md` | diagnosis SoT | A+ | 280–320 |",
        "| `清水亭_产品结构诊断_TIANSIGHT幻灯片 (5).html` | visual gold (shells + 47 figs) | B visual / C spec | **296 real** |",
        "| `侍天TIANSIGHT_分析体系Part1.md` | system bible A01–A58 | A | 90–110 |",
        "| `苏帮袁_菜单分析维度体系_第一性原理.md` | system seed | A | 14–18 |",
        "| `06_首版汇报报告_V1.0_数据校准版.md` | briefing | A | 140–180 |",
        "| `07_战略方法论体系与分阶段赋能路线图_M1.0.md` | roadmap | A | 100–140 |",
        "| `08_北京西式快餐可参考品牌分析专项_B1.0.md` | dossier | A | 80–110 |",
        "",
        "Gold HTML: 4 CSS classes (`slide cover` 1, `slide divider` 17, `slide` 231, `slide figslide` 47). Tokens pass (`#76551F`, Noto Serif SC, IBM Plex Mono). Failures vs workshop spec: no `data-page-type`; HOW TO READ 6/296; TAKEAWAY 16/296; 126/296 titles contain `续`.",
        "",
        "No mermaid. No `![](image)` in any of the seven files.",
        "",
        "---",
        "",
        "## 3 Locked taxonomy",
        "",
        "### 3.1 Genre (5) — not a slide type",
        "",
        "| Id | MD shape | Bars |",
        "|---|---|---|",
        "| `diagnosis` | 清水亭 13-module dump | SOURCE + HOW TO READ + TAKEAWAY |",
        "| `system` | 侍天 A01–A58 / 苏帮袁 dimensions | SOURCE + takeaway |",
        "| `briefing` | 06 首版汇报 | TAKEAWAY on data pages |",
        "| `roadmap` | 07 stages + gates | takeaway = gate or 死法 |",
        "| `dossier` | 08 brand files | SOURCE + learn/don’t |",
        "",
        "### 3.2 L1 shells (4) — cheap model copies these only",
        "",
        "| Id | Class | n / 296 | Workshop layout |",
        "|---|---|---:|---|",
        "| `cover` | `slide cover` | 1 | `cover` (deck) |",
        "| `divider` | `slide divider` | 17 | `cover` as 章扉 |",
        "| `body` | `slide` | 231 | `kpi-grid` `roster` `matrix-full` `verdict` `viz-duo` |",
        "| `fig` | `slide figslide` | 47 | `viz-full` `viz-table` |",
        "",
        "Shared chrome: `.tk.tl/.tr/.bl/.br` `.cap` `.hd` `.chip` `.srcbar` `.takebar` footer index. Fig default viewBox: `0 0 1320 500`.",
        "",
        "### 3.3 L2 jobs (12)",
        "",
        "| Id | Shell | Classify when | Table budget | Workshop |",
        "|---|---|---|---|---|",
        "| `cover` | cover | First page | — | cover |",
        "| `toc` | body | Contents (≤2 pages) | act list | — |",
        "| `chapter` | divider | H1 / 第 N 章 | — | chapter |",
        "| `readme` | body | 阅读指南, calibre, confidence | calibre table OK | statement |",
        "| `statement` | body | One claim, quote, or question | — | statement quote question |",
        "| `kpi` | body | 3–6 numbers | 3–6 cards | kpi |",
        "| `roster` | body | Named list that must sum | 8–12 rows + `.sum` | roster |",
        "| `chart` | fig | One figure, one decision | — | chart |",
        "| `chart-table` | fig | Figure + executable names | side table ≤8 rows | chart-table |",
        "| `matrix` | body | 九宫, unlock, score, ABC migrate | ≤9 cells, 3-state | matrix |",
        "| `compare` | body | Dual calibre, A vs B, stages, learn/don’t, timeline, diagram | 2 cols or 1–3 profiles | compare timeline diagram |",
        "| `verdict` | body | 争议四段, 当场决策, 证伪 | 4 cells or decision list | verdict |",
        "",
        "Modifier, not a job: `overflow: true` + `overflow_of` + title `续`. Gold: 126/296.",
        "",
        "A `<table>` is a mark on `body`, not a fifth shell and not a sixth type layer. Stephen Few: table = lookup exact values; graph = see a relationship.",
        "",
        "Retired as `fill` ids: `sum-roster` → `roster`; `kpi-cards` → `kpi`; `state-matrix` → `matrix`; `dual-calibre` / `profile-card` → `compare`; `falsify-quad` → `verdict`.",
        "",
        "### 3.4 L3 viz (16) — FT Visual Vocabulary",
        "",
        "Pick the **question**, then one recipe. Source: Financial Times Visual Vocabulary (Cotgreave / Smith, 2016). 附录 E lists ~40 图表类型; they collapse here via aliases.",
        "",
        "| FT question | Recipes | Do not add |",
        "|---|---|---|",
        "| Magnitude | `bubble` `diverging-bar` | extra bar skins |",
        "| Ranking | `pareto` `slope` | bump → `slope` |",
        "| Distribution | `hist-cdf` `heatmap` | violin/boxplot/ridgeline → `hist-cdf` |",
        "| Change over time | `line-dual` `calendar` | gantt → `calendar` |",
        "| Part-to-whole | `treemap` `funnel` `waterfall` `venn` | pie / 3D |",
        "| Flow | `sankey` `network` | chord → `venn` |",
        "| Correlation | `quadrant` `radar` | extra scatter skins |",
        "| Deviation | `diverging-bar` `waterfall` | dumbbell → `diverging-bar` |",
        "| Spatial | — | maps; none in this MD corpus |",
        "",
        "`sankey` `funnel` `waterfall` `radar` `venn` `bubble` `hist-cdf` `pareto` `slope` `diverging-bar` `quadrant` `heatmap` `treemap` `network` `line-dual` `calendar`",
        "",
        "Aliases: violin/boxplot/ridgeline/stacked-bar → `hist-cdf`; dumbbell → `diverging-bar`; bump → `slope`; gantt → `calendar`; chord → `venn`; architecture → `treemap`.",
        "",
        "No 3D. No rainbow. Matrix ink = ready / degraded / blocked. A 3-state HTML grid is L2 `matrix`, not a 17th viz.",
        "",
        "---",
        "",
        "## 4 Two-model pipeline",
        "",
        "```",
        "MD",
        " → TOP MODEL: genre + slide-plan JSON (shell, job, fill, slots, overflow_of)",
        " → CHEAP MODEL: clone L1 HTML, fill slots, no new CSS",
        " → page-loop (brand.md + type checks) → page-audit",
        "```",
        "",
        "Top model must not emit HTML. Cheap model must not pick a new job or viz id.",
        "",
        "Required on every slide object: `id` `shell` `job` `title`.",
        "Required on diagnosis data slides: `source` `how_to_read` `takeaway`.",
        "`fill` is an L3 viz id or `null`. Do not put retired table ids in `fill`.",
        "",
        "---",
        "",
        "## 5 Coverage matrix",
        "",
        "Every job × genre cell has at least one original cut. Gold HTML is tagged `diagnosis` because the 296-page file is the 清水亭 deck.",
        "",
        *cov_rows,
        "",
        "---",
        "",
        "## 6 L2 jobs",
        "",
        "Original excerpts. Use these to size type, row budget, and chrome. Do not invent extra slots.",
        "",
    ]

    for jid in JOB_IDS:
        parts.append(include_sample(OUT / "job" / f"{jid}.md", f'<a id="l2-{jid}"></a>\n\n### L2 `{jid}`'))
        parts.append("")

    parts += [
        "---",
        "",
        "## 7 Overflow (`续`)",
        "",
        include_sample(OUT / "job" / "overflow.md", "### Modifier `overflow`"),
        "",
        "---",
        "",
        "## 8 L3 viz recipes",
        "",
        "One viz id per fig shell. Pick FT question first, then the recipe. Copy SVG geometry from the gold HTML.",
        "",
    ]
    for vid in VIZ_IDS:
        parts.append(include_sample(OUT / "fill-viz" / f"{vid}.md", f'<a id="l3-viz-{vid}"></a>\n\n### L3 viz `{vid}`'))
        parts.append("")

    parts += [
        "---",
        "",
        "## 9 Appendix E chart menu",
        "",
        include_sample(OUT / "fill-viz" / "_appendix-E-chart-menu.md", "### Original chart menu (清水亭 附录 E)"),
        "",
        "---",
        "",
        "## 10 Folded types and empties",
        "",
        include_sample(OUT / "gaps.md", "### Coverage gaps"),
        "",
        "---",
        "",
        "## 11 Do not",
        "",
        "- Hand the cheap model the raw 17 workshop ids as a menu",
        "- Add a 13th L2 job (`playbook` `profile` `timeline` `quote` `question` fold into existing jobs)",
        "- Add a parallel L3 table taxonomy (`sum-roster` `kpi-cards` `state-matrix` `dual-calibre` `profile-card` `falsify-quad` are L2 jobs)",
        "- Reuse 07 data-source L0–L5 or 08 brand-filter L1–L3 as slide layers",
        "- Invent viz ids; use the 16 + aliases grouped by FT question",
        "- Emit empty competitor figures",
        "- Mix Inter / purple / Guizang `h-hero` into TIANSIGHT",
        "- Keep workshop chrome (`#baslide-chrome`) in the slide",
        "- Drop SOURCE / denom on `续` pages",
        "- Hide n-below-threshold cells; hatch them",
        "",
        "---",
        "",
        "*Generated by `skills/md-to-html-slides/scripts/extract-samples.py`. Do not rewrite the fenced originals.*",
        "",
    ]
    write(REPORT, "\n".join(parts))
    print("report", REPORT, "lines", len(REPORT.read_text(encoding="utf-8").splitlines()))


def dump_html_chrome() -> tuple[list[dict], list[dict]]:
    """Parse gold HTML once so this script does not depend on a prior /tmp dump."""
    raw = FILES["html"].read_text(encoding="utf-8")

    def strip_tags(s: str) -> str:
        s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
        s = re.sub(r"</(p|div|tr|h[1-6]|li|blockquote)>", "\n", s, flags=re.I)
        s = re.sub(r"<svg[\s\S]*?</svg>", "[SVG omitted]", s, flags=re.I)
        s = re.sub(r"<[^>]+>", " ", s)
        s = htmlmod.unescape(s)
        s = re.sub(r"[ \t]+", " ", s)
        s = re.sub(r"\n[ \t]+", "\n", s)
        s = re.sub(r"\n{3,}", "\n\n", s)
        return s.strip()

    def table_md(body: str, max_rows: int = 8) -> list[str]:
        mds = []
        for t in re.findall(r"<table[\s\S]*?</table>", body, re.I):
            rows = []
            for tr in re.findall(r"<tr[\s\S]*?</tr>", t, re.I):
                cells = [re.sub(r"\s+", " ", strip_tags(c)).strip() for c in re.findall(r"<t[hd][^>]*>([\s\S]*?)</t[hd]>", tr, re.I)]
                if cells:
                    rows.append(cells)
            if not rows:
                continue
            ncol = max(len(r) for r in rows)
            def pad(r: list[str]) -> list[str]:
                return r + [""] * (ncol - len(r))
            head = pad(rows[0])
            lines = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * ncol) + "|"]
            body_rows = rows[1 : max_rows + 1]
            for r in body_rows:
                lines.append("| " + " | ".join(pad(r)) + " |")
            more = max(0, len(rows) - 1 - max_rows)
            if more:
                lines.append(f"| … | ({more} more rows omitted) |")
            mds.append("\n".join(lines))
        return mds

    slides = []
    i = 0
    for p in re.split(r"(?=<section\b)", raw):
        if not p.lower().startswith("<section"):
            continue
        i += 1
        m = re.match(r"<section([^>]*)>([\s\S]*)$", p, re.I)
        attrs, body = m.group(1), m.group(2)
        body = re.sub(r"</section>[\s\S]*$", "", body, flags=re.I)
        cls_m = re.search(r'class="([^"]*)"', attrs, re.I)
        h2 = [strip_tags(x) for x in re.findall(r"<h2[^>]*>([\s\S]*?)</h2>", body, re.I)]
        h1 = [strip_tags(x) for x in re.findall(r"<h1[^>]*>([\s\S]*?)</h1>", body, re.I)]
        chips = [strip_tags(x) for x in re.findall(r'class="chip[^"]*"[^>]*>([\s\S]*?)</span>', body, re.I)]
        src = [strip_tags(x) for x in re.findall(r'class="srct"[^>]*>([\s\S]*?)</', body, re.I)]
        take = [strip_tags(x) for x in re.findall(r'class="taket"[^>]*>([\s\S]*?)</', body, re.I)]
        slides.append({
            "i": i,
            "cls": cls_m.group(1) if cls_m else "",
            "h1": h1,
            "h2": h2,
            "chips": chips[:4],
            "src": src[:2],
            "take": take[:2],
            "tables": table_md(body, 8),
            "text": strip_tags(body)[:1800],
        })
    want = {
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 20, 21, 22, 24, 26, 27,
        30, 31, 33, 38, 42, 47, 50, 62, 63, 67, 71, 72, 78, 83, 93, 100, 101,
        102, 105, 120, 124, 142, 150, 164, 172, 174, 198, 225, 226, 230, 232,
        233, 251, 255, 256, 259, 261, 265,
    }
    sel = [s for s in slides if s["i"] in want]
    figs = []
    for s in slides:
        if "figslide" in s["cls"]:
            figs.append({k: s[k] for k in ("i", "h2", "chips", "src", "take", "text")})
            figs[-1]["text"] = s["text"][:500]
    HTML_SEL.parent.mkdir(parents=True, exist_ok=True)
    HTML_SEL.write_text(json.dumps(sel, ensure_ascii=False, indent=2), encoding="utf-8")
    HTML_FIGS.write_text(json.dumps(figs, ensure_ascii=False, indent=2), encoding="utf-8")
    return sel, figs


def main() -> None:
    sel, figs = dump_html_chrome()
    fig_by_i = {f["i"]: f for f in figs}

    job_meta = {
        "verdict": ("body", "verdict", "争议 / 事实 / 处理 / 证伪  or decision list", "4 cells or decision list"),
        "compare": ("body", "compare / timeline / diagram", "left · therefore · right (or stage playbook / learn-don't)", "2 cols or 1–3 profile cards"),
        "matrix": ("body", "matrix", "row × col · cell state · zero≠gap footnote", "≤9 cells, 3-state ink"),
        "chart-table": ("fig", "chart-table", "chart 58% + table 42% · shared takeaway", "side table ≤8 rows"),
        "chart": ("fig", "chart", "one figure · SOURCE · HOW TO READ · TAKEAWAY", None),
        "roster": ("body", "roster", "full names · sum row · not TOP10-as-all", "8–12 rows + .sum closes"),
        "kpi": ("body", "kpi", "3–6 cards: value · label · delta", "3–6 cards"),
        "statement": ("body", "statement / quote / question", "one claim · optional supporting line", None),
        "readme": ("body", "statement", "calibre table · confidence · how to read", "calibre table OK"),
        "chapter": ("divider", "chapter", "act number · chapter title · one-line promise", None),
        "toc": ("body", "—", "act list · bilingual labels · no charts", "act list, no charts"),
        "cover": ("cover", "cover", "kicker · title ≤3 lines · one-line decision · meta chips", None),
    }

    jobs: dict[str, list[str]] = {k: [] for k in job_meta}

    jobs["cover"] = [
        sample_md("S1 diagnosis · 清水亭 title block", REL["qing"], "L1–L8", "diagnosis", cut("qing", 1, 8)),
        sample_md("S2 system · 侍天 title + one-liner", REL["sid"], "L1–L16", "system", cut("sid", 1, 16)),
        sample_md("S3 briefing · 06 title block", REL["r06"], "L1–L8", "briefing", cut("r06", 1, 8)),
        sample_md("S4 roadmap · 07 title + nature", REL["r07"], "L1–L8", "roadmap", cut("r07", 1, 8)),
        sample_md("S5 dossier · 08 title + purpose", REL["r08"], "L1–L8", "dossier", cut("r08", 1, 8)),
        sample_md("S6 system-seed · 苏帮袁 H1 + lede", REL["sby"], "L1–L5", "system", cut("sby", 1, 5)),
        sample_md("S7 gold HTML slide 1", REL["html"], "slide 1 / 296", "diagnosis", html_block(html_slide(sel, 1)), "SVG compass omitted"),
    ]

    jobs["toc"] = [
        sample_md("S1 roadmap · 07 目录表", REL["r07"], "L11–L25", "roadmap", cut("r07", 11, 25)),
        sample_md("S2 diagnosis · 清水亭 H1 章目录 (implicit TOC)", REL["qing"], "all H1", "diagnosis", h1s("qing"), "gold HTML paginates this into slides 2–3"),
        sample_md("S3 system · Part 1/2/3 分工 + 本册 H1", REL["sid"], "L9–L16 + all H1", "system", cut("sid", 9, 16) + "\n" + h1s("sid")),
        sample_md("S4 briefing · 06 部分 H1 (implicit TOC)", REL["r06"], "all H1", "briefing", h1s("r06")),
        sample_md("S5 dossier · 08 部分 H1 (implicit TOC)", REL["r08"], "all H1", "dossier", h1s("r08")),
        sample_md("S6 gold HTML slides 2–3", REL["html"], "slides 2–3", "diagnosis", html_block(html_slide(sel, 2)) + "\n--- slide 3 ---\n" + html_block(html_slide(sel, 3))),
    ]

    jobs["chapter"] = [
        sample_md("S1 diagnosis · chapter H1s", REL["qing"], "all H1", "diagnosis", h1s("qing")),
        sample_md("S2 system · 侍天 八部分扉页", REL["sid"], "L19, L73, L92, L188, L833, L1105, L1169, L1220", "system", "\n".join([
            cut("sid", 19, 19).rstrip(),
            cut("sid", 73, 73).rstrip(),
            cut("sid", 92, 92).rstrip(),
            cut("sid", 188, 188).rstrip(),
            cut("sid", 833, 833).rstrip(),
            cut("sid", 1105, 1105).rstrip(),
            cut("sid", 1169, 1169).rstrip(),
            cut("sid", 1220, 1220).rstrip(),
        ]) + "\n"),
        sample_md("S3 briefing · 06 部分扉页", REL["r06"], "all H1", "briefing", h1s("r06")),
        sample_md("S4 roadmap · 07 部分扉页", REL["r07"], "all H1", "roadmap", h1s("r07")),
        sample_md("S5 dossier · 08 部分扉页", REL["r08"], "all H1", "dossier", h1s("r08")),
        sample_md("S6 gold HTML divider · 序 / 第0章 / 经营基本盘 / 结论", REL["html"], "slides 4, 7, 30, 225", "diagnosis", "\n".join([
            html_block(html_slide(sel, 4)).rstrip(),
            "--- slide 7 ---",
            html_block(html_slide(sel, 7)).rstrip(),
            "--- slide 30 ---",
            html_block(html_slide(sel, 30)).rstrip(),
            "--- slide 225 ---",
            html_block(html_slide(sel, 225)).rstrip(),
        ]) + "\n"),
    ]

    jobs["readme"] = [
        sample_md("S1 diagnosis · 双口径阅读指南", REL["qing"], "L11–L24", "diagnosis", cut("qing", 11, 24)),
        sample_md("S2 briefing · 数据基础与置信度", REL["r06"], "L30–L69", "briefing", cut("r06", 30, 69)),
        sample_md("S3 dossier · 品牌归一化阅读提示", REL["r08"], "L11–L49", "dossier", cut("r08", 11, 49)),
        sample_md("S4 system · 口径 A/B + 三路对账", REL["sid"], "L73–L88", "system", cut("sid", 73, 88)),
        sample_md("S5 roadmap · 数据源分层 + 五条纪律", REL["r07"], "L495–L575", "roadmap", cut("r07", 495, 575)),
        sample_md("S6 gold HTML 阅读指南", REL["html"], "slides 5–6", "diagnosis", html_block(html_slide(sel, 5)) + "\n--- slide 6 ---\n" + html_block(html_slide(sel, 6))),
        sample_md("S7 gold HTML 数据资产表 (calibre companion)", REL["html"], "slide 8", "diagnosis", html_block(html_slide(sel, 8))),
    ]

    jobs["statement"] = [
        sample_md("S1 system-seed · 一道菜是五个系统的交点", REL["sby"], "L7–L18", "system", cut("sby", 7, 18)),
        sample_md("S2 system · 侍天一句话", REL["sid"], "L4–L7", "system", cut("sid", 4, 7)),
        sample_md("S3 briefing · 三条铁律", REL["r06"], "L91–L120", "briefing", cut("r06", 91, 120)),
        sample_md("S4 briefing · 战略级重构主张", REL["r06"], "L122–L126", "briefing", cut("r06", 122, 126)),
        sample_md("S5 briefing · 一页纸五句话", REL["r06"], "L2182–L2194", "briefing", cut("r06", 2182, 2194)),
        sample_md("S6 roadmap · 北极星", REL["r07"], "L38–L48", "roadmap", cut("r07", 38, 48)),
        sample_md("S7 roadmap · 一页纸六句话", REL["r07"], "L1706–L1720", "roadmap", cut("r07", 1706, 1720)),
        sample_md("S8 diagnosis · 三个必须先修的问题 (claim cluster)", REL["qing"], "L95–L119", "diagnosis", cut("qing", 95, 119)),
        sample_md("S9 dossier · 三个必须记住的结论", REL["r08"], "L153–L185", "dossier", cut("r08", 153, 185)),
        sample_md("S10 dossier · 一页纸七句话", REL["r08"], "L1108–L1124", "dossier", cut("r08", 1108, 1124)),
        sample_md("S11 gold HTML · 额量比是价格指数", REL["html"], "slide 265", "diagnosis", html_block(html_slide(sel, 265))),
        sample_md("S12 gold HTML · 三个必须先修", REL["html"], "slide 14", "diagnosis", html_block(html_slide(sel, 14))),
    ]

    jobs["kpi"] = [
        sample_md("S1 diagnosis · 六店经营对比 (sum row = KPI tower source)", REL["qing"], "L303–L337", "diagnosis", cut("qing", 303, 337)),
        sample_md("S2 diagnosis · 主辅佐引四格总览", REL["qing"], "L386–L395", "diagnosis", cut("qing", 386, 395)),
        sample_md("S3 diagnosis · 四指标分布", REL["qing"], "L807–L811", "diagnosis", cut("qing", 807, 811)),
        sample_md("S4 system · A04 样例门店卡", REL["sid"], "L251–L264", "system", cut("sid", 251, 264)),
        sample_md("S5 briefing · 全市大盘 KPI", REL["r06"], "L226–L250", "briefing", cut("r06", 226, 250)),
        sample_md("S6 roadmap · Gate 指标总表", REL["r07"], "L1032–L1044", "roadmap", cut("r07", 1032, 1044)),
        sample_md("S7 roadmap · 宏观三数字", REL["r07"], "L591–L600", "roadmap", cut("r07", 591, 600)),
        sample_md("S8 dossier · Wagas 指标卡原料", REL["r08"], "L373–L386", "dossier", cut("r08", 373, 386)),
        sample_md("S9 gold HTML · 六店经营对比", REL["html"], "slide 31", "diagnosis", html_block(html_slide(sel, 31))),
        sample_md("S10 gold HTML · 角色总览四格", REL["html"], "slide 38", "diagnosis", html_block(html_slide(sel, 38))),
    ]

    jobs["roster"] = [
        sample_md("S1 diagnosis · 附录 A 全量名录 (first 12 + header)", REL["qing"], "L2644–L2658", "diagnosis", cut("qing", 2644, 2658), "118 rows in source; paginate 8–12 / page"),
        sample_md("S2 diagnosis · 13 个「主」SKU 逐项", REL["qing"], "L414–L427", "diagnosis", cut("qing", 414, 427)),
        sample_md("S3 system · A01–A20 分析点总表 (paginate)", REL["sid"], "L110–L133", "system", cut("sid", 110, 133), "58 rows in source"),
        sample_md("S4 briefing · 45 元以上能开到 20 家的 8 个品牌", REL["r06"], "L103–L120", "briefing", cut("r06", 103, 120)),
        sample_md("S5 briefing · 首版汉堡 5 款名录", REL["r06"], "L1086–L1096", "briefing", cut("r06", 1086, 1096)),
        sample_md("S6 dossier · 北京西式规模总榜 (first 15)", REL["r08"], "L88–L106", "dossier", cut("r08", 88, 106), "32 rows in source"),
        sample_md("S7 roadmap · 方法论速查表 (first 12)", REL["r07"], "L1643–L1656", "roadmap", cut("r07", 1643, 1656), "paginate; rest in overflow"),
        sample_md("S8 gold HTML body table + 续", REL["html"], "slides 8–9", "diagnosis", html_block(html_slide(sel, 8)) + "\n--- slide 9 续 ---\n" + html_block(html_slide(sel, 9))),
        sample_md("S9 gold HTML · 口径 A 结果 (roster density)", REL["html"], "slide 50", "diagnosis", html_block(html_slide(sel, 50))),
    ]

    jobs["chart"] = [
        sample_md("S1 diagnosis · 推荐图表纪律 (章结构)", REL["qing"], "L11–L22", "diagnosis", cut("qing", 11, 22), "every diagnosis chapter ends with 推荐图表 — see fill-viz/"),
        sample_md("S2 system · 洛伦兹 / 基尼 / 帕累托配方", REL["sid"], "L837–L847", "system", cut("sid", 837, 847)),
        sample_md("S3 briefing · 价格带直方图表 (chart data, no image)", REL["r06"], "L252–L283", "briefing", cut("r06", 252, 283)),
        sample_md("S4 briefing · 竞争力雷达表", REL["r06"], "L854–L871", "briefing", cut("r06", 854, 871)),
        sample_md("S5 dossier · 单店评论中位 vs 门店数", REL["r08"], "L204–L233", "dossier", cut("r08", 204, 233)),
        sample_md("S6 roadmap · 死亡带规模柱 (chart data)", REL["r07"], "L610–L627", "roadmap", cut("r07", 610, 627)),
        sample_md("S7 gold HTML fig chrome · sankey 图01", REL["html"], "slide 10", "diagnosis", html_block(html_slide(sel, 10))),
        sample_md("S8 gold HTML fig chrome · pareto", REL["html"], "slide 62", "diagnosis", html_block(html_slide(sel, 62))),
        sample_md("S9 gold HTML fig chrome · hist-cdf", REL["html"], "slide 124", "diagnosis", html_block(html_slide(sel, 124))),
    ]

    jobs["chart-table"] = [
        sample_md("S1 diagnosis · 人均分档表 + 推荐直方图", REL["qing"], "L339–L380", "diagnosis", cut("qing", 339, 380)),
        sample_md("S2 diagnosis · 角色错配规则 + 名单头", REL["qing"], "L439–L456", "diagnosis", cut("qing", 439, 456)),
        sample_md("S3 system · A04 样例表 (pairs with bubble)", REL["sid"], "L251–L264", "system", cut("sid", 251, 264)),
        sample_md("S4 briefing · 竞争定位矩阵 (pairs with radar)", REL["r06"], "L841–L852", "briefing", cut("r06", 841, 852)),
        sample_md("S5 roadmap · Gate 表 (pairs with stage waterfall)", REL["r07"], "L1032–L1044", "roadmap", cut("r07", 1032, 1044)),
        sample_md("S6 dossier · 价格带 × 规模 + 读法", REL["r08"], "L138–L160", "dossier", cut("r08", 138, 160)),
        sample_md("S7 gold HTML 四象限页 chrome", REL["html"], "slide 42", "diagnosis", html_block(html_slide(sel, 42))),
        sample_md("S8 gold HTML 高潜品四象限", REL["html"], "slide 83", "diagnosis", html_block(html_slide(sel, 83))),
    ]

    jobs["matrix"] = [
        sample_md("S1 diagnosis · 味型 × 工艺九宫", REL["qing"], "L1938–L1976", "diagnosis", cut("qing", 1938, 1976)),
        sample_md("S2 diagnosis · 双口径分类迁移矩阵", REL["qing"], "L732–L744", "diagnosis", cut("qing", 732, 744)),
        sample_md("S3 diagnosis · 价格空档扫描", REL["qing"], "L1403–L1432", "diagnosis", cut("qing", 1403, 1432)),
        sample_md("S4 system-seed · 五族根本问题表", REL["sby"], "L7–L18", "system", cut("sby", 7, 18)),
        sample_md("S5 system · 维度组合三条约束", REL["sid"], "L61–L69", "system", cut("sid", 61, 69)),
        sample_md("S6 briefing · 价格带 × 规模天花板", REL["r06"], "L74–L89", "briefing", cut("r06", 74, 89)),
        sample_md("S7 briefing · 九宫格重复度", REL["r06"], "L928–L942", "briefing", cut("r06", 928, 942)),
        sample_md("S8 roadmap · 框架 × 阶段使用矩阵", REL["r07"], "L468–L491", "roadmap", cut("r07", 468, 491)),
        sample_md("S9 dossier · 可参考性评分矩阵 TOP12", REL["r08"], "L951–L980", "dossier", cut("r08", 951, 980)),
        sample_md("S10 gold HTML · 互补关系矩阵", REL["html"], "slide 24", "diagnosis", html_block(html_slide(sel, 24))),
        sample_md("S11 gold HTML · 味型×工艺九宫页", REL["html"], "slide 172", "diagnosis", html_block(html_slide(sel, 172))),
    ]

    jobs["compare"] = [
        sample_md("S1 briefing · V0.1 vs V1.0 对照", REL["r06"], "L11–L26", "briefing", cut("r06", 11, 26)),
        sample_md("S2 diagnosis · 系列级双口径 + 折让率", REL["qing"], "L762–L787", "diagnosis", cut("qing", 762, 787)),
        sample_md("S3 diagnosis · 框架对照 苏帮袁 vs 本次要求", REL["qing"], "L210–L237", "diagnosis", cut("qing", 210, 237)),
        sample_md("S4 system · 君臣佐使 vs Menu Engineering", REL["sid"], "L853–L877", "system", cut("sid", 853, 877)),
        sample_md("S5 dossier · Wagas 该学 / 不该学", REL["r08"], "L373–L405", "dossier", cut("r08", 373, 405)),
        sample_md("S6 dossier · 分阶段该看谁", REL["r08"], "L982–L990", "dossier", cut("r08", 982, 990)),
        sample_md("S7 dossier · 六大品牌原型", REL["r08"], "L187–L199", "dossier", cut("r08", 187, 199)),
        sample_md("S8 roadmap · S0 阶段卡片 (命题/不可逆/死法/Gate)", REL["r07"], "L1048–L1108", "roadmap", cut("r07", 1048, 1108)),
        sample_md("S9 roadmap · Playing to Win 五问", REL["r07"], "L177–L190", "roadmap", cut("r07", 177, 190)),
        sample_md("S10 roadmap · JTBD 四任务", REL["r07"], "L192–L207", "roadmap", cut("r07", 192, 207)),
        sample_md("S11 gold HTML 框架对照页", REL["html"], "slide 22", "diagnosis", html_block(html_slide(sel, 22))),
        sample_md("S12 gold HTML 合并体系", REL["html"], "slide 27", "diagnosis", html_block(html_slide(sel, 27))),
    ]

    jobs["verdict"] = [
        sample_md("S1 diagnosis · F.1 争议四段 (gold A58)", REL["qing"], "L3071–L3122", "diagnosis", cut("qing", 3071, 3122)),
        sample_md("S2 diagnosis · 十条核心结论", REL["qing"], "L2569–L2582", "diagnosis", cut("qing", 2569, 2582)),
        sample_md("S3 diagnosis · P0 行动清单", REL["qing"], "L2584–L2596", "diagnosis", cut("qing", 2584, 2596)),
        sample_md("S4 system · A58 证伪登记 + 三轮战果", REL["sid"], "L804–L829", "system", cut("sid", 804, 829)),
        sample_md("S5 briefing · 需当场决策清单", REL["r06"], "L2069–L2089", "briefing", cut("r06", 2069, 2089)),
        sample_md("S6 briefing · 未解问题", REL["r06"], "L2093–L2109", "briefing", cut("r06", 2093, 2109)),
        sample_md("S7 dossier · 十条可迁移 + 六条不该学", REL["r08"], "L995–L1021", "dossier", cut("r08", 995, 1021)),
        sample_md("S8 dossier · 三个开放问题 (falsify timing)", REL["r08"], "L1023–L1029", "dossier", cut("r08", 1023, 1029)),
        sample_md("S9 roadmap · 宏观六条推论", REL["r07"], "L671–L680", "roadmap", cut("r07", 671, 680)),
        sample_md("S10 roadmap · 风险登记册", REL["r07"], "L1581–L1600", "roadmap", cut("r07", 1581, 1600)),
        sample_md("S11 gold HTML 十条结论", REL["html"], "slide 226", "diagnosis", html_block(html_slide(sel, 226))),
        sample_md("S12 gold HTML F.1 证伪页", REL["html"], "slide 261", "diagnosis", html_block(html_slide(sel, 261))),
        sample_md("S13 gold HTML F.0 审查索引", REL["html"], "slide 256", "diagnosis", html_block(html_slide(sel, 256))),
    ]

    table_into_job = {
        "roster": [
            sample_md("Budget · 六店合计行", REL["qing"], "L307–L315", "diagnosis", cut("qing", 307, 315), "retired fill id sum-roster"),
            sample_md("Budget · 附录 A 累计%", REL["qing"], "L2644–L2658", "diagnosis", cut("qing", 2644, 2658), "retired fill id sum-roster"),
        ],
        "kpi": [
            sample_md("Budget · 主辅佐引四格", REL["qing"], "L390–L395", "diagnosis", cut("qing", 390, 395), "retired fill id kpi-cards"),
            sample_md("Budget · 全市大盘 4 指标", REL["r06"], "L226–L237", "briefing", cut("r06", 226, 237), "retired fill id kpi-cards"),
        ],
        "matrix": [
            sample_md("Budget · 九宫 SKU 数", REL["qing"], "L1944–L1951", "diagnosis", cut("qing", 1944, 1951), "retired fill id state-matrix"),
            sample_md("Budget · 迁移矩阵 4×4", REL["qing"], "L736–L742", "diagnosis", cut("qing", 736, 742), "retired fill id state-matrix"),
        ],
        "compare": [
            sample_md("Budget · 系列双口径", REL["qing"], "L762–L777", "diagnosis", cut("qing", 762, 777), "retired fill id dual-calibre"),
            sample_md("Budget · 侍天口径 A/B", REL["sid"], "L73–L86", "system", cut("sid", 73, 86), "retired fill id dual-calibre"),
            sample_md("Budget · Wagas 档案", REL["r08"], "L373–L405", "dossier", cut("r08", 373, 405), "retired fill id profile-card"),
        ],
        "verdict": [
            sample_md("Budget · F.1 四段", REL["qing"], "L3071–L3122", "diagnosis", cut("qing", 3071, 3122), "retired fill id falsify-quad"),
            sample_md("Budget · 附录 F 体例", REL["qing"], "L3023–L3029", "diagnosis", cut("qing", 3023, 3029), "retired fill id falsify-quad"),
        ],
    }
    for jid, extra in table_into_job.items():
        jobs[jid].extend(extra)

    for jid, blocks in jobs.items():
        shell, workshop, slots, budget = job_meta[jid]
        head = [
            f"# L2 `{jid}`",
            "",
            f"- L1 shell: `{shell}`",
            f"- workshop map: {workshop}",
            f"- slots: {slots}",
            f"- table budget: {budget or '—'}",
            f"- samples: {len(blocks)} original excerpts (verbatim; not rewritten)",
            "",
            "Use these to size type, row budget, and chrome. Do not invent extra slots. Tables are this job’s mark, not a separate type.",
            "",
        ]
        write(OUT / "job" / f"{jid}.md", "\n".join(head + blocks))

    # overflow modifier
    overflow = [
        "# Modifier `overflow` (not an L2 job)",
        "",
        "- rule: same job + fill; `overflow_of` parent id; title suffix `续`; repeat SOURCE; TAKEAWAY only on last page",
        "- gold: 126 / 296 titles contain 续",
        "",
        sample_md("S1 gold HTML 续 · 数据资产表", REL["html"], "slide 9", "diagnosis", html_block(html_slide(sel, 9))),
        sample_md("S2 gold HTML 续 · 分类基数", REL["html"], "slide 11 then 12", "diagnosis", html_block(html_slide(sel, 11)) + "\n--- slide 12 续 ---\n" + html_block(html_slide(sel, 12))),
        sample_md("S3 gold HTML 长续链 · 口径 A 二八名录", REL["html"], "slide 50", "diagnosis", html_block(html_slide(sel, 50)), "slides 51–61 continue the same roster — 11 overflow pages, one job"),
        sample_md("S4 diagnosis · 附录 A 必须分页", REL["qing"], "L2644–L2658", "diagnosis", cut("qing", 2644, 2658), "source has 118 SKU rows"),
        sample_md("S5 system · A01–A58 总表必须分页", REL["sid"], "L110–L133", "system", cut("sid", 110, 133), "58 analysis-point rows"),
        sample_md("S6 dossier · 规模总榜必须分页", REL["r08"], "L88–L106", "dossier", cut("r08", 88, 106), "32 brand rows"),
    ]

    write(OUT / "job" / "overflow.md", "\n".join(overflow))

    ft_dir = OUT / "fill-table"
    if ft_dir.exists():
        for p in ft_dir.glob("*.md"):
            p.unlink()
    write(
        ft_dir / "README.md",
        "\n".join([
            "# Retired: L3 table ids are not types",
            "",
            "Tables are a mark on L2 `body` jobs. Row budgets live on the job.",
            "",
            "| Retired `fill` id | Use L2 |",
            "|---|---|",
            *[f"| `{old}` | `{new}` |" for old, new in RETIRED_TABLE.items()],
            "",
            "Original cuts now sit in `samples/job/<id>.md` under **Budget ·** headings.",
            "",
        ]),
    )

    fig_map = {
        "sankey": [10, 47],
        "funnel": [13, 164],
        "waterfall": [17, 232],
        "radar": [20, 105],
        "venn": [26, 63],
        "bubble": [33],
        "hist-cdf": [36, 124, 129],
        "pareto": [62],
        "slope": [71],
        "diverging-bar": [72, 84, 121],
        "quadrant": [42, 83, 230],
        "heatmap": [93, 151, 174, 184],
        "treemap": [29, 102],
        "network": [142],
        "line-dual": [150, 165, 189, 193],
        "calendar": [198],
    }
    extra_md: dict[str, list[tuple[str, int, int, str, str]]] = {
        "sankey": [("qing", 30, 58, "diagnosis", "0.1 数据资产 + 推荐 Sankey")],
        "funnel": [
            ("qing", 61, 73, "diagnosis", "0.2 370→118 漏斗表"),
            ("sid", 1171, 1181, "system", "周期漏斗：日→周→月→季→年→事件"),
        ],
        "waterfall": [
            ("qing", 3071, 3110, "diagnosis", "F.1 对账瀑布数字"),
            ("r07", 610, 627, "roadmap", "死亡带规模变化 → 柱/瀑布"),
        ],
        "bubble": [
            ("qing", 303, 337, "diagnosis", "2.1 六店 → 气泡图推荐"),
            ("r08", 204, 227, "dossier", "门店数 × 单店评论中位"),
        ],
        "hist-cdf": [
            ("qing", 343, 380, "diagnosis", "2.2 人均分档 + 推荐直方图"),
            ("r06", 252, 272, "briefing", "全市西式价格带直方图"),
        ],
        "pareto": [("qing", 505, 519, "diagnosis", "4.2 口径 A 二八结果")],
        "slope": [("qing", 746, 760, "diagnosis", "双口径排名变动")],
        "diverging-bar": [("qing", 762, 777, "diagnosis", "系列折让率正负双向")],
        "quadrant": [
            ("qing", 399, 407, "diagnosis", "角色理论 vs 实际"),
            ("r06", 841, 852, "briefing", "竞争定位矩阵"),
        ],
        "heatmap": [
            ("qing", 1938, 1960, "diagnosis", "九宫销售额"),
            ("r06", 928, 936, "briefing", "九宫重复三条线"),
        ],
        "network": [
            ("qing", 1531, 1553, "diagnosis", "8.4 连带提升度 TOP15"),
            ("sid", 1107, 1131, "system", "依赖层级 ASCII → network/treemap"),
        ],
        "calendar": [
            ("qing", 2220, 2234, "diagnosis", "11.5 季节性产品矩阵"),
            ("r06", 1462, 1470, "briefing", "开业营销日历"),
        ],
        "line-dual": [("qing", 2096, 2117, "diagnosis", "11.1 小龙虾旬度")],
        "treemap": [
            ("qing", 1133, 1161, "diagnosis", "6.1 现状结构树"),
            ("sid", 1107, 1131, "system", "依赖层级 L0–L6"),
        ],
        "venn": [("qing", 210, 237, "diagnosis", "1.1 框架对照")],
        "radar": [
            ("qing", 1161, 1183, "diagnosis", "6.2 3-4-2-1 达标"),
            ("r06", 854, 866, "briefing", "竞争力雷达表"),
        ],
    }
    appendix_e = cut("qing", 2967, 3017)

    for vid, ids in fig_map.items():
        blocks = []
        for key, a, b, genre, note in extra_md.get(vid, []):
            blocks.append(sample_md(f"MD data behind `{vid}` · {genre}", REL[key], f"L{a}–L{b}", genre, cut(key, a, b), note))
        for i in ids:
            f = fig_by_i[i]
            blocks.append(sample_md(
                f"gold HTML 图 slide {i}",
                REL["html"],
                f"slide {i} / 296",
                "diagnosis",
                html_block({**f, "cls": "slide figslide", "h1": [], "tables": [], "n_tables": 0, "contd": False}),
                "inline SVG omitted; copy geometry from gold file when designing the recipe",
            ))
        head = [
            f"# L3 viz `{vid}`",
            "",
            f"- FT question: `{VIZ_FAMILY[vid]}`",
            f"- L2 job: `chart` (or `chart-table` / `matrix` when the figure is a grid)",
            f"- gold slides: {', '.join(str(x) for x in ids)}",
            f"- samples: {len(blocks)}",
            "",
        ]
        write(OUT / "fill-viz" / f"{vid}.md", "\n".join(head + blocks))

    write(
        OUT / "fill-viz" / "_appendix-E-chart-menu.md",
        "\n".join([
            "# Original chart menu (清水亭 附录 E)",
            "",
            "This table is the MECE viz shopping list from the diagnosis MD. Map each 图表类型 to one L3 viz id by FT question (aliases in taxonomy.md). Do not promote 附录 E names (小提琴、哑铃、三维气泡) to types.",
            "",
            sample_md("附录 E 可视化图表推荐总表", REL["qing"], "L2967–L3017", "diagnosis", appendix_e),
        ]),
    )

    write(
        OUT / "gaps.md",
        "\n".join([
            "# Coverage gaps (explicit empties — MECE)",
            "",
            "These surfaces exist in the corpus. They are **not** L2 jobs. Original cuts live here so templates do not invent a 13th type.",
            "",
            "## In corpus, folded (do not add L2)",
            "",
            "| Surface | Where original lives | Fold into |",
            "|---|---|---|",
            "| quote | 苏帮袁 / 07 blockquotes | `statement` |",
            "| question | 08 Q1–Q3; 06 未解问题 | `verdict` or `statement` |",
            "| timeline | 07 S0–S7; 06 开业日历 | `compare` |",
            "| diagram | 侍天依赖层级; 07 Playing to Win | `compare` + `treemap`/`network` |",
            "| playbook stage card | 07 §8.1–8.8 | `compare` |",
            "| brand profile | 08 C1–C5 | `compare` |",
            "| retired table fills (`sum-roster` `kpi-cards` `state-matrix` `dual-calibre` `profile-card` `falsify-quad`) | were L3 ids | matching L2 job; see `fill-table/README.md` |",
            "",
            sample_md("quote · 苏帮袁 东亚风味分子", REL["sby"], "L29–L29", "system", cut("sby", 29, 29), "fold into statement"),
            sample_md("quote · 07 Stage Gate 必要性", REL["r07"], "L1614–L1618", "roadmap", cut("r07", 1614, 1618), "fold into statement"),
            sample_md("question · 08 三个开放问题", REL["r08"], "L1023–L1029", "dossier", cut("r08", 1023, 1029), "fold into verdict"),
            sample_md("question · 06 未解问题", REL["r06"], "L2093–L2109", "briefing", cut("r06", 2093, 2109), "fold into verdict"),
            sample_md("timeline · 06 开业营销日历", REL["r06"], "L1462–L1470", "briefing", cut("r06", 1462, 1470), "fold into compare"),
            sample_md("timeline · 07 二期服务路线", REL["r06"], "L2111–L2120", "briefing", cut("r06", 2111, 2120), "fold into compare"),
            sample_md("diagram · 侍天依赖层级", REL["sid"], "L1107–L1131", "system", cut("sid", 1107, 1131), "fold into compare + treemap/network"),
            sample_md("diagram · 维度扩展收益递减", REL["sid"], "L49–L59", "system", cut("sid", 49, 59), "fold into compare"),
            sample_md("playbook · S0 阶段卡", REL["r07"], "L1048–L1108", "roadmap", cut("r07", 1048, 1108), "fold into compare; also in job/compare.md"),
            sample_md("playbook · S1 Gate", REL["r07"], "L1112–L1162", "roadmap", cut("r07", 1112, 1162), "fold into compare"),
            sample_md("brand profile · Wagas C1", REL["r08"], "L373–L405", "dossier", cut("r08", 373, 405), "fold into compare"),
            sample_md("brand profile · 魏斯理 5.1", REL["r08"], "L834–L889", "dossier", cut("r08", 834, 889), "fold into compare"),
            "",
            "## Not in this MD corpus (keep for Guizang only)",
            "",
            "No `![](image)` in any of the 7 ref files. Do not design diagnosis templates around these until a deck with photos exists:",
            "",
            "- `text-image`",
            "- `image-grid`",
            "- `image-hero`",
            "",
            "## Gold HTML vs six-element spec",
            "",
            "Original gold pages usually have SOURCE + KEY INSIGHTS, not HOW TO READ / TAKEAWAY bars. Template design must add those slots even though the 296-page file mostly omits them.",
            "",
            sample_md("gold chrome without HOW TO READ · 图01", REL["html"], "slide 10", "diagnosis", html_block(html_slide(sel, 10)), "template still reserves HOW TO READ + TAKEAWAY"),
            "",
        ]),
    )

    genre_order = ["diagnosis", "system", "briefing", "roadmap", "dossier"]

    def cell_label(blocks: list[str], genre: str) -> str:
        hits = [b for b in blocks if f"- genre: `{genre}`" in b]
        gold = [b for b in hits if REL["html"] in b]
        mdn = len(hits) - len(gold)
        if not hits:
            return "—"
        bits = []
        if mdn:
            bits.append(f"{mdn} md")
        if gold:
            bits.append(f"{len(gold)} html")
        return "+".join(bits)

    cov_rows = ["| Job | n | diagnosis | system | briefing | roadmap | dossier |", "|---|---:|---|---|---|---|---|"]
    for jid in JOB_IDS:
        blocks = jobs[jid]
        cells = " | ".join(cell_label(blocks, g) for g in genre_order)
        cov_rows.append(f"| `{jid}` | {len(blocks)} | {cells} |")

    index = [
        "# Sample library · original content per slide type",
        "",
        "Cuts from `ref/` only. Prose is verbatim. SVG paths omitted. HTML tables truncated to 8 rows. Inline SVG omitted.",
        "",
        "Regenerate: `python3 skills/md-to-html-slides/scripts/extract-samples.py`",
        "",
        "## MECE map",
        "",
        "| Layer | Ids | Folder |",
        "|---|---|---|",
        "| L2 jobs (12) + overflow | cover … verdict + overflow | `job/` |",
        "| L3 viz (16) by FT question | sankey … calendar | `fill-viz/` |",
        "| tables | not a type; row budget on L2 | `job/` Budget · headings; `fill-table/README.md` |",
        "| folded / image-* empties | quote question timeline diagram playbook profile | `gaps.md` |",
        "",
        "Lock: **5 genres · 4 L1 shells · 12 L2 jobs · 16 L3 viz**. `fill` is a viz id or `null`.",
        "",
        "## Genre coverage of L2 jobs",
        "",
        *cov_rows,
        "",
        "Every job × genre cell has at least one original cut. Gold HTML is tagged `diagnosis` because the 296-page file is the 清水亭 deck.",
        "",
        "## How to use for template design",
        "",
        "1. Open `job/<id>.md`. Every sample is one real page-worth of content.",
        "2. Size the shell so the **densest** sample still fits 1440×810 with SOURCE + HOW TO READ + TAKEAWAY.",
        "3. Open `fill-viz/<id>.md` for chart recipes. Pick FT question first, then one viz id per fig shell.",
        "4. If a sample overflows, that is an `overflow` page, not a new type. See `job/overflow.md`.",
        "5. Do not add an L2 because a sample looks unique (`playbook`, `profile`). Map it with `gaps.md`.",
        "6. Do not add L3 table ids. Row budgets are on `kpi` `roster` `matrix` `compare` `verdict`.",
        "7. Folded originals (quote / question / timeline / diagram / playbook / profile) are in `gaps.md`.",
        "8. Complete one-file report: [`ref/REPORT-md-to-html-slide-types.md`](../../../ref/REPORT-md-to-html-slide-types.md).",
        "",
    ]
    write(OUT / "INDEX.md", "\n".join(index))
    assemble_report(cov_rows)
    print("wrote", OUT)
    print("files", len(list(OUT.rglob("*.md"))))
    for jid in JOB_IDS:
        print(f"  job/{jid}: {len(jobs[jid])}")


if __name__ == "__main__":
    main()
