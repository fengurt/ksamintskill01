#!/usr/bin/env python3
"""Close a longdoc2mdpages pack around the GF4p2slides page-plan seam."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROLE_TO_JOB = {
    "cover": "cover",
    "toc": "toc",
    "chapter": "chapter",
    "readme": "readme",
    "overflow": "statement",
    "statement": "statement",
    "kpi": "kpi",
    "roster": "roster",
    "chart": "chart",
    "chart-table": "chart-table",
    "matrix": "matrix",
    "compare": "compare",
    "verdict": "verdict",
}

JOB_TO_SHELL = {
    "cover": "cover",
    "chapter": "divider",
    "chart": "fig",
    "chart-table": "fig",
    "toc": "body",
    "readme": "body",
    "statement": "body",
    "kpi": "body",
    "roster": "body",
    "matrix": "body",
    "compare": "body",
    "verdict": "body",
}

PACK_FILES = (
    "index.json",
    "index.md",
    "units.json",
    "outline.md",
    "deck.json",
    "deck-plan.json",
    "pack.json",
    "MANIFEST.md",
    "anchors.json",
    "audit-source.json",
    "audit.md",
    "fit-report.json",
    "source-manifest.json",
)


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "mdpages2htmlslides" / "scripts"


def load_viz():
    sys.path.insert(0, str(_scripts_dir()))
    import baslide_viz  # type: ignore

    return baslide_viz


def load_coverage():
    script = Path(__file__).resolve().parent / "check-coverage.py"
    spec = importlib.util.spec_from_file_location("longdoc_coverage", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def page_material(work: Path, page: dict) -> str:
    md_path = work / "pages" / f"{page['id']}.md"
    if md_path.is_file():
        return md_path.read_text(encoding="utf-8")
    material = page.get("material") or {}
    parts: list[str] = []
    for b in material.get("bullets") or []:
        parts.append(str(b))
    table = material.get("table") or {}
    if isinstance(table, dict):
        cols = table.get("columns") or []
        if cols:
            parts.append("| " + " | ".join(str(c) for c in cols) + " |")
            parts.append("| " + " | ".join("---" for _ in cols) + " |")
        for row in table.get("rows") or []:
            if isinstance(row, list):
                parts.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(parts)


NUMBER_RE = re.compile(r"[-+−]?\d[\d,.]*(?:\.\d+)?(?:/\d[\d,.]*)?\s*(?:%|％|万|亿|元|家|店|人|次|桌|bps|pp)?", re.I)


def clean_inline(value: object) -> str:
    text = str(value or "")
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[┌┐└┘├┤│↑]+", " ", text)
    text = re.sub(r"─{2,}", " ", text)
    return re.sub(r"[*_`]", "", text).strip()


def clean_markdown(markdown: str) -> str:
    return "\n".join(clean_inline(re.sub(r"^#{1,6}\s+", "", line)) for line in markdown.splitlines())


def split_row(line: str) -> list[str]:
    text = line.strip().strip("|")
    return [clean_inline(cell) for cell in text.split("|")]


def first_table(markdown: str) -> tuple[list[str], list[list[str]]]:
    lines = markdown.replace("\r\n", "\n").splitlines()
    for index, line in enumerate(lines[:-1]):
        if "|" not in line or not re.match(r"^\s*\|?.*-{3,}.*\|", lines[index + 1]):
            continue
        columns = split_row(line)
        rows = []
        for row in lines[index + 2:]:
            if "|" not in row or not row.strip():
                break
            cells = split_row(row)
            if len(cells) == len(columns):
                rows.append(cells)
        if columns and rows:
            return columns, rows
    return [], []


def bullets_from(markdown: str) -> list[str]:
    return [clean_inline(re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)) for line in markdown.splitlines() if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line)][:6]


def content_lines(markdown: str) -> list[str]:
    """Source prose only; page scaffolding must never become evidence."""
    out = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if (not stripped or stripped.startswith(("<!--", "|", "#"))
                or re.match(r"^(?:role|units):", stripped, re.I)
                or re.fullmatch(r"u-\d+", stripped, re.I)):
            continue
        out.append(stripped)
    return out


def prose_from(markdown: str, limit: int = 420) -> str:
    lines = []
    for stripped in content_lines(markdown):
        if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", stripped):
            continue
        lines.append(clean_inline(stripped))
    return " ".join(lines)[:limit]


def parse_num(value: object) -> float | None:
    text = re.sub(r"\s+", "", str(value).replace("，", ","))
    match = re.fullmatch(r"[¥￥$]?\s*([-+−]?\d[\d,]*(?:\.\d+)?)(?:/\d[\d,]*(?:\.\d+)?)?\s*(?:[%％]|万|亿|元|家|店|人|次|桌|项|个|分|倍|天|小时|分钟|㎡|m²|bps|pp)?\+?", text, re.I)
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", "").replace("−", "-"))
    except ValueError:
        return None


def first_num(value: object) -> float | None:
    match = re.search(r"[-+−]?\d[\d,]*(?:\.\d+)?", str(value or ""))
    return float(match.group(0).replace(",", "").replace("−", "-")) if match else None


def content_from_page(page: dict, markdown: str, job: str) -> dict:
    material = page.get("material") or {}
    table = material.get("table") if isinstance(material, dict) else {}
    if not isinstance(table, dict):
        table = {}
    columns, rows = first_table(markdown)
    if not columns:
        columns, rows = table.get("columns") or [], table.get("rows") or []
    bullets = ((material.get("bullets") or []) if isinstance(material, dict) else []) or bullets_from(markdown)
    blocks = []
    if job == "kpi":
        cards = []
        for row in rows:
            numeric = next((cell for cell in row[1:] if parse_num(cell) is not None), None)
            if numeric is not None:
                cards.append({"kind": "kpi-card", "label": row[0], "value": numeric, "unit": "", "note": ""})
        if not cards:
            for line in content_lines(markdown):
                for clause in re.split(r"[；;。，，]", line):
                    number = NUMBER_RE.search(clause)
                    if not number:
                        continue
                    if re.search(r"20\d{2}[-/.年]\d{1,2}(?:[-/.月]\d{1,2})?", clause):
                        continue
                    if not re.search(r"(?:%|％|万|亿|元|家|店|人|次|桌|项|个|分|倍|天|小时|分钟|㎡|m²|bps|pp)$", number.group(0).strip(), re.I):
                        continue
                    label = re.sub(re.escape(number.group(0)), "", re.sub(r"[*_`#|]", "", clause)).strip(" ：:-")
                    cards.append({"kind": "kpi-card", "label": label[:32] or "指标", "value": number.group(0).strip(), "unit": "", "note": ""})
                    if len(cards) == 4:
                        break
                if len(cards) == 4:
                    break
        blocks.extend(cards[:4])
    if columns and rows and job in {"chart-table", "roster", "compare", "matrix"}:
        blocks.append({
            "kind": "table",
            "columns": columns,
            "rows": rows,
            "sum": table.get("sum") or [],
        })
    elif bullets:
        blocks.append({"kind": "bullets", "items": bullets[:6]})
    elif job not in {"cover", "chapter", "chart", "kpi"} or not blocks:
        prose = prose_from(markdown)
        if prose:
            blocks.append({"kind": "lede", "text": prose})
    return {
        "blocks": blocks,
        "columns": columns,
        "rows": rows,
        "sum": table.get("sum") or [],
        "bullets": bullets,
        "audit_text": clean_markdown(markdown),
    }


def data_profile(columns: list[str], rows: list[list[str]]) -> dict:
    numeric = []
    values = []
    for index, column in enumerate(columns):
        if re.search(r"^(?:#|id|编号|序号|代码)$", str(column).strip(), re.I):
            continue
        col_values = [parse_num(row[index]) for row in rows if index < len(row)]
        if col_values and sum(value is not None for value in col_values) >= max(1, len(col_values) // 2):
            numeric.append(column)
            values.extend(value for value in col_values if value is not None)
    nonzero = [abs(value) for value in values if value]
    total = sum(values) if values else 0
    return {
        "rows": len(rows),
        "series": len(numeric),
        "measures": numeric,
        "dims": ["nominal"] if columns else [],
        "negatives": any(value < 0 for value in values),
        "sums_to_whole": bool(values) and (abs(total - 100) <= 2 or abs(total - 1) <= .02),
        "magnitude_ratio": round(max(nonzero) / min(nonzero), 3) if len(nonzero) > 1 else 1,
        "missingness": round(sum(1 for row in rows for cell in row if str(cell).strip() in {"", "—", "-"}) / max(1, len(rows) * max(1, len(columns))), 3),
    }


def intent_for(fill: str | None, job: str, title: str) -> str | None:
    if fill in {"pareto", "slope"}:
        return "ranking"
    if fill in {"line-dual", "calendar"} or re.search(r"趋势|同比|环比|变化", title):
        return "change-over-time"
    if fill in {"waterfall", "diverging-bar"} or re.search(r"偏差|下降|流失|差距", title):
        return "deviation"
    if fill in {"treemap", "funnel", "venn"}:
        return "part-to-whole"
    if fill in {"hist-cdf", "heatmap"}:
        return "distribution"
    if fill in {"bubble", "quadrant", "radar"}:
        return "correlation"
    if fill in {"sankey", "network"}:
        return "flow"
    if job == "roster":
        return "ranking"
    if job in {"kpi", "compare", "chart", "chart-table"}:
        return "magnitude"
    return None


def claim_for(page: dict, content: dict, markdown: str) -> dict:
    columns, rows = content["columns"], content["rows"]
    cards = [block for block in content.get("blocks") or [] if block.get("kind") == "kpi-card"]
    if cards:
        columns = ["metric", "value"]
        rows = [[card.get("label"), card.get("value")] for card in cards]
    measure = next((column for index, column in enumerate(columns) if index and any(parse_num(row[index]) is not None for row in rows if index < len(row))), columns[1] if len(columns) > 1 else "content")
    measure_index = columns.index(measure) if measure in columns else None
    magnitude = first_num(rows[0][measure_index]) if rows and measure_index is not None and len(rows[0]) > measure_index else None
    title = clean_inline(page.get("takeaway") or page.get("title") or page["id"])
    direction = "decrease" if magnitude is not None and magnitude < 0 and re.search(r"下降|下滑|减少|流失|亏|低于", title) else "increase" if magnitude is not None and magnitude > 0 and re.search(r"增长|上升|提高|增加|高于", title) else "describe"
    period_match = re.search(r"20\d{2}(?:[-/.年]\d{1,2})?", markdown)
    return {
        "subject": {"field": columns[0] if columns else "topic", "selector": clean_inline(rows[0][0] if rows and rows[0] else page.get("title") or page["id"])[:80]},
        "measure": measure,
        "direction": direction,
        "magnitude": {"value": magnitude, "unit": "source"} if magnitude is not None else None,
        "period": period_match.group(0) if period_match else "source period",
        "scope": ((" / ".join(page.get("outline_path") or []) or "deck") + (f" / {clean_inline(rows[0][0])}" if rows and rows[0] else "") + f" [{page.get('id')}]").strip(),
        "render": title[:180],
    }


def node_role(page: dict, job: str, index: int, has_evidence: bool) -> str:
    if index == 0:
        return "claim"
    if has_evidence and job in {"chart", "chart-table", "roster", "kpi"}:
        return "evidence"
    if job in {"cover", "toc", "readme"}:
        return "frame"
    if job == "chapter":
        return "situation"
    if job == "verdict":
        return "complication"
    return "situation"


def solve_layout(job: str, profile: dict, has_figure: bool) -> dict:
    if job == "chart-table":
        solved = "fig-rail"
    elif job == "chart":
        solved = "fig-strip"
    elif job == "roster":
        solved = "table-full"
    elif job == "kpi":
        solved = "hero-band"
    elif job == "compare":
        solved = "split-2"
    elif job == "matrix":
        solved = "grid-2x2"
    else:
        solved = "full"
    return {"solved": solved, "grid": "12x8", "trace": [f"evidence_rows={profile['rows']}", f"series={profile['series']}", f"figure={str(has_figure).lower()}"]}


def solve_pack(job: str, content: dict) -> str:
    rows = len(content.get("rows") or [])
    if job in {"statement", "kpi"} or (job in {"roster", "chart-table"} and rows <= 7):
        return "air"
    if rows > 10:
        return "tight"
    return "mid"


def split_dense_rosters(pages: list[dict]) -> list[dict]:
    """Keep long comparison rows legible without shrinking type."""
    out = []
    for page in pages:
        content = page.get("content") or {}
        rows = content.get("rows") or []
        if page.get("template") != "roster" or not rows or sum(len(str(cell)) for row in rows for cell in row) <= 900:
            out.append(page)
            continue
        chunks, current, chars = [], [], 0
        for row in rows:
            row_chars = sum(len(str(cell)) for cell in row)
            if current and (len(current) == 3 or chars + row_chars > 850):
                chunks.append(current)
                current, chars = [], 0
            current.append(row)
            chars += row_chars
        if current:
            chunks.append(current)
        if len(chunks) > 1 and len(chunks[-1]) == 1 and len(chunks[-2]) > 1:
            chunks[-1].insert(0, chunks[-2].pop())
        base_id, base_title = page["id"], page["title"]
        for index, chunk in enumerate(chunks):
            part = copy.deepcopy(page)
            part["id"] = base_id if index == 0 else f"{base_id}-cont-{index + 1}"
            part["title"] = f"{base_title} · {index + 1}/{len(chunks)}"
            part["overflow_of"] = None if index == 0 else base_id
            part["units"] = page.get("units") or [] if index == 0 else []
            part["content"]["rows"] = chunk
            part["pack"] = "air"
            for block in part["content"].get("blocks") or []:
                if block.get("kind") == "table":
                    block["rows"] = chunk
            columns = part["content"].get("columns") or []
            part["content"]["audit_text"] = "\n".join([
                "| " + " | ".join(map(str, columns)) + " |",
                "| " + " | ".join("---" for _ in columns) + " |",
                *("| " + " | ".join(map(str, row)) + " |" for row in chunk),
            ])
            profile = data_profile(part["content"].get("columns") or [], chunk)
            part["claim"] = claim_for(part, part["content"], part["content"]["audit_text"])
            if part.get("evidence"):
                part["evidence"][0]["profile"] = profile
                encoding = part["evidence"][0].get("encoding") or {}
                if encoding:
                    encoding["emphasis"]["target"] = chunk[0][0]
            part["layout"] = solve_layout("roster", profile, False)
            out.append(part)
    return out


def renumber_pages(pages: list[dict], root_id: str | None) -> tuple[list[dict], str | None]:
    mapping = {page["id"]: f"p-{index:04d}" for index, page in enumerate(pages, 1)}
    for page in pages:
        old_id = page["id"]
        page["id"] = mapping[old_id]
        if page.get("overflow_of"):
            page["overflow_of"] = mapping[page["overflow_of"]]
        supports = (page.get("node") or {}).get("supports")
        if supports:
            page["node"]["supports"] = mapping.get(supports, supports)
    return pages, mapping.get(root_id, root_id)


def drop_structural_pages(pages: list[dict], root_id: str | None) -> tuple[list[dict], str | None]:
    """Discard importer-only root markers while preserving their unit coverage."""
    pending = []
    kept = []
    for page in pages:
        if clean_inline(page.get("title") or "").lower() == "(root)" and not (page.get("content") or {}).get("blocks"):
            pending.extend(page.get("units") or [])
            if page.get("id") == root_id:
                root_id = None
            continue
        if pending:
            page["units"] = [*pending, *(page.get("units") or [])]
            pending = []
        kept.append(page)
    if pending and kept:
        kept[-1]["units"] = [*(kept[-1].get("units") or []), *pending]
    return kept, root_id or (kept[0]["id"] if kept else None)


def source_provenance(work: Path, deck: dict, material: str, units: list[str]) -> dict:
    manifest = {}
    path = work / "source-manifest.json"
    if path.is_file():
        manifest = json.loads(path.read_text(encoding="utf-8"))
    source = manifest.get("source") or deck.get("source") or work.name
    as_of = manifest.get("as_of")
    if not as_of:
        source_path = Path(str(source))
        as_of = datetime.fromtimestamp(source_path.stat().st_mtime, timezone.utc).date().isoformat() if source_path.exists() else datetime.now(timezone.utc).date().isoformat()
    return {
        "dataset": str(source),
        "query_hash": hashlib.sha256((material + "\n" + " ".join(units)).encode("utf-8")).hexdigest()[:16],
        "as_of": as_of,
        "transform_chain": ["normalize-source", "segment", "paginate"],
        "owner": "source document",
    }


def deck_name_for(work: Path, deck: dict) -> str:
    current = clean_inline(deck.get("title") or "")
    if current and current.lower() not in {"deck", "slides", "presentation"}:
        return current
    manifest_path = work / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    source = Path(str(manifest.get("source") or deck.get("source") or work.name))
    if source.suffix.lower() == ".zip" or source.is_dir():
        return source.stem
    source_md = work / "source.md"
    if source_md.is_file():
        match = re.search(r"^#\s+(.+)$", source_md.read_text(encoding="utf-8"), re.M)
        if match:
            return clean_inline(match.group(1))
    return source.stem or work.name


def build_deck_plan(work: Path, deck: dict, *, genre: str, skin: str, viz) -> dict:
    pages = []
    fill_counts: dict[str, int] = {}
    root_id = (deck.get("pages") or [{}])[0].get("id")
    deck_name = deck_name_for(work, deck)
    argument_nodes = []
    promoted_titles = set()
    for page_index, page in enumerate(deck.get("pages") or []):
        page = dict(page)
        if page_index == 0 and clean_inline(page.get("title") or "").lower() in {"", "deck", "slides", "presentation"}:
            page["title"] = deck_name
        role = page.get("role") or "statement"
        job = ROLE_TO_JOB.get(role, "statement")
        material = page_material(work, page)
        assigned = viz.assign_page_fill(page.get("title") or "", material, role)
        fill = assigned.get("fill")
        recipe = assigned.get("recipe")
        promoted = role not in {"chart", "chart-table"} and bool(fill)
        promoted_title = re.sub(r"\s*(?:续|·\s*\d+/\d+)\s*$", "", clean_inline(page.get("title") or ""))
        if promoted and (page.get("overflow_of") or "续" in str(page.get("title") or "") or promoted_title in promoted_titles):
            fill = recipe = None
        elif promoted:
            promoted_titles.add(promoted_title)
        content = content_from_page(page, material, job)
        if job == "kpi" and sum(block.get("kind") == "kpi-card" for block in content["blocks"]) < 2:
            job = "statement"
            content = content_from_page(page, material, job)
        if job == "roster" and not content["rows"]:
            job = "statement"
        if len(content["columns"]) > 7 or len(content["rows"]) > 12:
            appendix = work / "assets" / "tables" / f"{page['id']}.csv"
            appendix.parent.mkdir(parents=True, exist_ok=True)
            with appendix.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(content["columns"])
                writer.writerows(content["rows"])
            content["appendix"] = str(appendix.relative_to(work))
            content["columns"] = content["columns"][:7]
            content["rows"] = [row[:7] for row in content["rows"][:8]]
            for block in content["blocks"]:
                if block.get("kind") == "table":
                    block["columns"], block["rows"] = content["columns"], content["rows"]
        profile = data_profile(content["columns"], content["rows"])
        if fill and not profile["measures"] and fill not in viz.SEMANTIC_L3:
            fill = recipe = None
        if job == "chart" and not fill:
            job = "statement"
        if job == "chart-table" and not fill:
            job = "roster"
        if job == "roster" and fill:
            job = "chart-table"
        elif fill and job in {"statement", "compare", "matrix"}:
            job = "chart-table" if content["columns"] and content["rows"] else "chart"
        if fill:
            fill_counts[fill] = fill_counts.get(fill, 0) + 1
        path = page.get("outline_path") or []
        how = (page.get("how_to_read") or "").strip() or assigned.get("how_to_read") or ""
        if fill:
            figure_columns, figure_rows = content["columns"], content["rows"]
            if not figure_rows:
                labels = content.get("bullets") or []
                figure_columns, figure_rows = ["label"], [[label] for label in labels[:8]]
            content["blocks"].insert(0, {
                "kind": "fig",
                "viz": fill,
                "data": {"columns": figure_columns, "rows": figure_rows},
                "caption": how,
                "fallback": {"columns": figure_columns, "rows": figure_rows},
            })
        source = page.get("source") or deck.get("source") or " ".join(page.get("units") or [])
        provenance = source_provenance(work, deck, material, page.get("units") or [])
        claim = claim_for(page, content, material)
        intent = intent_for(fill, job, page.get("title") or "")
        evidence = []
        visible_data = any(block.get("kind") in {"fig", "table", "kpi-card"} for block in content["blocks"])
        if profile["measures"] and visible_data:
            kind = "chart" if fill else "table"
            item = {"kind": kind, "profile": profile, "source": provenance}
            if fill:
                item["encoding"] = {
                    "preset": fill,
                    "mapping": {"x": content["columns"][0] if content["columns"] else "label", "y": profile["measures"][0]},
                    "geom": [fill], "stat": ["identity"], "position": "identity",
                    "scale": {"y": {"zero": True}},
                    "coord": "cartesian", "facet": None,
                    "emphasis": {"target": (content["rows"][0][0] if content["rows"] else claim["subject"]["selector"]), "mode": "accent+label", "annotation": claim["render"][:80]},
                    "scenario": "actual",
                }
            evidence.append(item)
        elif fill and visible_data:
            evidence.append({"kind": "diagram", "source": provenance})
        elif any(block.get("kind") == "kpi-card" for block in content["blocks"]):
            evidence.append({"kind": "number", "profile": profile, "source": provenance})
        graph_role = node_role(page, job, page_index, bool(evidence))
        node = {"role": graph_role, "supports": root_id if graph_role == "evidence" else None}
        plan_page = {
            "id": page["id"],
            "template": job,
            "shell": JOB_TO_SHELL.get(job, "body"),
            "node": node,
            "claim": claim,
            "intent": intent,
            "evidence": evidence,
            "layout": solve_layout(job, profile, bool(fill)),
            "pack": page.get("pack") or solve_pack(job, content),
            "overflow_of": page.get("overflow_of"),
            "title": clean_inline(page.get("title") or page["id"]),
            "source": source,
            "takeaway": clean_inline(page.get("takeaway") or ""),
            "visualization": fill,
            "units": page.get("units") or [],
            "outline_path": path,
            "provenance": {
                "source": source,
                "how_to_read": how,
                "unit": page.get("unit") or "",
                **provenance,
            },
            "content": content,
        }
        pages.append(plan_page)
        argument_nodes.append({"id": page["id"], **node})
        page["fill"] = fill
        if recipe and recipe != fill:
            page["recipe"] = recipe
        elif "recipe" in page:
            del page["recipe"]
        if how and not (page.get("how_to_read") or "").strip():
            page["how_to_read"] = how
    pages, root_id = drop_structural_pages(pages, root_id)
    pages, root_id = renumber_pages(split_dense_rosters(pages), root_id)
    argument_nodes = [{"id": page["id"], **page["node"]} for page in pages]
    return {
        "contract_version": "2.0.0",
        "title": deck_name,
        "deck_name": deck_name,
        "brand_skill": skin,
        "mode": "slides",
        "aspect": "16:9",
        "source": deck.get("source") or "",
        "genre": genre,
        "theme": skin,
        "baslide": "modules/baslide01",
        "policy_version": "2.0.0",
        "argument": {"root": root_id, "nodes": argument_nodes},
        "pages": pages,
        "fill_counts": fill_counts,
    }


def write_manifest(work: Path, pack: dict) -> str:
    pages_n = pack["counts"]["pages"]
    units_n = pack["counts"]["units"]
    fills = pack["counts"]["fills"]
    roles = pack["counts"]["roles"]
    role_lines = "\n".join(f"- `{k}` × {v}" for k, v in sorted(roles.items()))
    fill_lines = "\n".join(f"- `{k}` × {v}" for k, v in sorted(pack.get("fill_counts", {}).items())) or "- （无图页或未推断）"
    present = "\n".join(f"- `{p}`" + (" ✓" if (work / p).exists() or (p == "pages/" and (work / "pages").is_dir()) else "") for p in pack["outputs"])
    return f"""# 可开发文件包 · {work.name}

这个目录是 **longdoc2mdpages 的完成物**：长文档已经切成可交给 Baslide01 开发幻灯片的材料。
**不要求** 在这里交付 HTML 幻灯片。

- 源文档：`{pack.get("source") or "—"}`
- 单元：{units_n} · 页：{pages_n} · 已分配 L3 fill：{fills}
- 皮肤：`{pack.get("skin")}` · 体裁：`{pack.get("genre")}`
- 生成：{pack.get("emitted_at")}

## 调用的 skill 与阶段

1. `longdoc2mdpages`
   - a · segment → `index.json` `index.md` `units.json`
   - b · outline → `outline.md`
   - c · pagination → `deck.json` `pages/`
   - d · emit → 本清单 + `deck-plan.json`
2. `deck-audit` hop1 · source → pages（`anchors.json` `audit-source.json` `audit.md`）

后续（本包完成之后，另开 Baslide01 开发）：

3. `mdpages2htmlslides` — 按 `deck-plan.json` 的 GF page template / visualization 渲染
4. `page-loop` — `modules/baslide01/prompts/loop/`
5. `deck-audit` hop2 · pages → HTML
6. `page-audit`

## 角色分布

{role_lines}

## L3 fill

{fill_lines}

## 产出文件

{present}

开发幻灯片时从 `deck-plan.json` 读取页面计划，不要重新切页。
"""


def emit(
    work: Path,
    *,
    genre: str,
    skin: str,
    write_deck: bool = True,
    allow_overfull: bool = False,
) -> dict:
    viz = load_viz()
    coverage = load_coverage()
    coverage.check_index(work)
    coverage.check_outline(work)
    coverage.check_deck(work)
    deck_path = work / "deck.json"
    assert deck_path.is_file(), f"missing {deck_path}"
    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    pages = deck.get("pages") or []
    assert pages, "deck.json has no pages"
    assert (work / "units.json").is_file(), "missing units.json"
    missing_fit = [p["id"] for p in pages if not isinstance(p.get("fit"), dict)]
    assert not missing_fit, f"fit gate not run for pages: {missing_fit[:20]}"
    overfull = [p["id"] for p in pages if p["fit"].get("verdict") == "overfull"]
    assert allow_overfull or not overfull, f"overfull pages: {overfull[:20]}"
    audit_path = work / "audit-source.json"
    assert audit_path.is_file(), "hop1 gate not run: missing audit-source.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert (audit.get("counts") or {}).get("hard", 0) == 0, "hop1 gate has hard findings"

    index = {}
    if (work / "index.json").is_file():
        index = json.loads((work / "index.json").read_text(encoding="utf-8"))

    plan = build_deck_plan(work, deck, genre=genre, skin=skin, viz=viz)
    (work / "deck-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if write_deck:
        deck_path.write_text(json.dumps(deck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    roles: dict[str, int] = {}
    for p in plan["pages"]:
        r = p.get("template") or p.get("role") or "?"
        roles[r] = roles.get(r, 0) + 1
    pages_dir = work / "pages"
    page_md = 0
    if pages_dir.is_dir():
        page_md = len([f for f in pages_dir.iterdir() if f.suffix == ".md"])

    outputs = list(PACK_FILES) + ["pages/"]
    pack = {
        "version": "2.0",
        "ready": True,
        "purpose": "longdoc2mdpages file pack for Baslide01 slide development",
        "source": deck.get("source") or index.get("source") or "",
        "work": work.name,
        "genre": genre,
        "skin": skin,
        "baslide": "modules/baslide01",
        "emitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "units": index.get("total_units") or len(index.get("units") or []),
            "pages": len(plan["pages"]),
            "source_pages": len(pages),
            "page_md": page_md,
            "fills": sum((plan.get("fill_counts") or {}).values()),
            "roles": roles,
        },
        "fill_counts": plan.get("fill_counts") or {},
        "outputs": outputs,
        "skills": [
            {
                "id": "longdoc2mdpages",
                "stages": ["a-segment", "b-outline", "c-pagination", "d-emit"],
            },
            {"id": "deck-audit", "stages": ["hop1"]},
        ],
        "later": [
            {"id": "mdpages2htmlslides", "input": "deck-plan.json"},
            {"id": "page-loop", "prompts": "modules/baslide01/prompts/loop"},
            {"id": "deck-audit", "stages": ["hop2"]},
            {"id": "page-audit"},
        ],
    }
    (work / "pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (work / "MANIFEST.md").write_text(write_manifest(work, pack), encoding="utf-8")
    print(
        f"emit-pack: pages={len(plan['pages'])} fills={pack['counts']['fills']} → {work / 'deck-plan.json'}",
        file=sys.stderr,
    )
    return pack


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the developable longdoc file pack")
    parser.add_argument("--work", required=True)
    parser.add_argument("--genre", default="diagnosis")
    parser.add_argument("--skin", default="TIANSIGHT")
    parser.add_argument("--theme", default=None, help="alias of --skin")
    parser.add_argument("--allow-overfull", action="store_true")
    args = parser.parse_args(argv)
    work = Path(args.work).resolve()
    skin = args.theme or args.skin or "TIANSIGHT"
    emit(work, genre=args.genre, skin=skin, allow_overfull=args.allow_overfull)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
