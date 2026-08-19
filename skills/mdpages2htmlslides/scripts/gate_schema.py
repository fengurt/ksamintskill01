#!/usr/bin/env python3
"""Validate GF deck-plan v2: shape, provenance, graph, rhetoric, and fallbacks."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

TEMPLATES = {"cover", "toc", "chapter", "statement", "kpi", "compare", "matrix", "chart", "chart-table", "roster", "verdict", "readme"}
TRANSLATIONS = {"quote": "statement", "playbook": "verdict", "gallery": "roster", "interactive": "chart"}
VIZ = {"bubble", "calendar", "diverging-bar", "funnel", "heatmap", "hist-cdf", "line-dual", "network", "pareto", "quadrant", "radar", "sankey", "slope", "treemap", "venn", "waterfall"}
VIZ_ALIASES = {"bar", "line", "area", "stacked-bar", "scatter", "donut", "timeline", "process", "org", "map", "gauge", "table"}
BLOCKS = {"text", "list", "metric", "table", "fig", "image", "embed", "note", "claim", "lede", "bullets", "kpi-card", "callout", "step", "profile", "quote", "media", "toc-item"}
LAYOUTS = {"full", "hero-band", "split-2", "split-2-62", "split-3", "grid-2x2", "grid-3x2", "table-full", "fig-rail", "fig-strip"}
PACKS = {"air", "mid", "tight"}
ROLES = {"frame", "situation", "complication", "question", "claim", "evidence", "back-matter"}
INTENTS = {"ranking", "magnitude", "part-to-whole", "change-over-time", "deviation", "distribution", "correlation", "flow", "geo"}
EVIDENCE = {"number", "table", "chart", "diagram", "map", "image", "text", "embed"}
DATA_EVIDENCE = {"number", "table", "chart", "map"}
INTENT_VIZ = {
    "ranking": {"pareto", "slope", "diverging-bar"},
    "magnitude": {"bubble", "diverging-bar", "waterfall", "treemap"},
    "part-to-whole": {"treemap", "funnel", "venn", "waterfall"},
    "change-over-time": {"line-dual", "calendar", "slope"},
    "deviation": {"waterfall", "diverging-bar", "slope", "line-dual"},
    "distribution": {"hist-cdf", "heatmap"},
    "correlation": {"bubble", "quadrant", "radar"},
    "flow": {"sankey", "network", "funnel"},
    "geo": {"map"},
}
PAGE_ID = re.compile(r"^p-[0-9]{3,4}$")
MARKDOWN = re.compile(r"\*\*|`[^`]+`|^\s*#{1,6}\s|\[[^\]]*\]\(", re.M)
NUMBER = re.compile(r"[-+−]?\d[\d,.]*(?:\.\d+)?")


def strings(value, path="$"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from strings(item, f"{path}[{index}]")


def layout_name(page: dict) -> str | None:
    layout = page.get("layout")
    return layout.get("solved") if isinstance(layout, dict) else layout


def parse_number(value) -> float | None:
    match = NUMBER.search(str(value or ""))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", "").replace("−", "-"))
    except ValueError:
        return None


def page_data(page: dict) -> tuple[list[str], list[list]]:
    """Return the visible data seam used by P.02/R.01/R.02."""
    content = page.get("content") or {}
    columns = list(content.get("columns") or [])
    rows = list(content.get("rows") or [])
    if columns and rows:
        return columns, rows
    blocks = [block for block in content.get("blocks") or [] if isinstance(block, dict)]
    for block in blocks:
        data = (block.get("data") or block) if block.get("kind") in {"fig", "table"} else {}
        columns, rows = list(data.get("columns") or []), list(data.get("rows") or [])
        if columns and rows:
            return columns, rows
    cards = [block for block in blocks if block.get("kind") == "kpi-card"]
    if cards:
        return ["metric", "value"], [[card.get("label"), card.get("value")] for card in cards]
    return [], []


def validate(plan: dict, policy: dict | None = None):
    policy = policy or {}
    findings: list[tuple[str, str, str, str]] = []

    def add(page: str, code: str, message: str, severity: str = "hard"):
        findings.append((page, code, message, severity))

    version = plan.get("contract_version")
    if version not in {"1.0.0", "2.0.0"}:
        add("$", "CONTRACT_VERSION", "contract_version must be 2.0.0 (1.0.0 is read-only legacy)")
    if not str(plan.get("title") or "").strip():
        add("$", "NO_DECK_TITLE", "title is required")
    if plan.get("mode") not in (None, "slide", "slides", "responsive", "print"):
        add("$", "MODE_UNKNOWN", repr(plan.get("mode")))
    if version == "2.0.0" and plan.get("aspect") != "16:9":
        add("$", "ASPECT", "v2 export aspect must be 16:9")
    pages = plan.get("pages")
    if not isinstance(pages, list) or not pages:
        return findings + [("$", "NO_PAGES", "pages must be a non-empty array", "hard")]

    seen = set()
    pages_by_id = {}
    consistency = {}
    layout_run = 0
    previous_layout = None
    previous_section = None
    as_of_dates = []
    for index, page in enumerate(pages, 1):
        pid = str(page.get("id") or f"p-{index:03d}")
        pages_by_id[pid] = page
        if pid in seen:
            add(pid, "DUP_ID", "duplicate page id")
        seen.add(pid)
        if not PAGE_ID.fullmatch(pid):
            add(pid, "ID_INVALID", "id must match p-NNN or p-NNNN")
        raw_template = page.get("template") or page.get("type")
        template = TRANSLATIONS.get(raw_template, raw_template)
        if template not in TEMPLATES:
            add(pid, "TEMPLATE_UNKNOWN", repr(template))
        if not str(page.get("title") or "").strip():
            add(pid, "NO_TITLE", "title is required")
        for field in ("source", "takeaway", "visualization", "content"):
            if field not in page:
                add(pid, "FIELD_REQUIRED", f"{field} is required")
        layout = layout_name(page)
        if layout not in (None, *LAYOUTS):
            add(pid, "LAYOUT_UNKNOWN", repr(layout))
        if version == "2.0.0":
            solved = page.get("layout")
            if not isinstance(solved, dict) or solved.get("grid") != "12x8" or not isinstance(solved.get("trace"), list):
                add(pid, "L.02", "v2 layout needs solved, 12x8 grid, and trace")
            node = page.get("node") or {}
            if node.get("role") not in ROLES:
                add(pid, "NODE_ROLE", repr(node.get("role")))
            claim = page.get("claim")
            if not isinstance(claim, dict) or any(key not in claim for key in ("subject", "measure", "direction", "period", "scope", "render")):
                add(pid, "CLAIM_SHAPE", "structured claim is incomplete")
            intent = page.get("intent")
            if intent is not None and intent not in INTENTS:
                add(pid, "INTENT_UNKNOWN", repr(intent))
            evidence = page.get("evidence")
            if not isinstance(evidence, list):
                add(pid, "EVIDENCE_SHAPE", "evidence must be an array")
                evidence = []
            if node.get("role") == "evidence" and not any(isinstance(item, dict) and item.get("kind") != "text" for item in evidence):
                add(pid, "R.03", "evidence node needs non-text evidence")
            for item in evidence:
                if not isinstance(item, dict) or item.get("kind") not in EVIDENCE:
                    add(pid, "EVIDENCE_KIND", repr(item.get("kind") if isinstance(item, dict) else item))
                    continue
                if item["kind"] in DATA_EVIDENCE:
                    source = item.get("source") or {}
                    missing = [key for key in ("dataset", "query_hash", "as_of", "transform_chain", "owner") if not source.get(key)]
                    if missing:
                        add(pid, "P.01", "missing provenance: " + ", ".join(missing))
                    try:
                        as_of_dates.append(date.fromisoformat(str(source.get("as_of"))[:10]))
                    except ValueError:
                        add(pid, "P.01", f"invalid as_of {source.get('as_of')!r}")
                if item.get("kind") == "chart":
                    encoding = item.get("encoding") or {}
                    preset = encoding.get("preset")
                    if preset not in VIZ | VIZ_ALIASES:
                        add(pid, "VIZ_UNKNOWN", repr(preset))
                    if page.get("intent") and preset not in INTENT_VIZ.get(page["intent"], set()):
                        add(pid, "R.04", f"{preset} does not answer {page['intent']}")
                    emphasis = encoding.get("emphasis") or {}
                    if not emphasis.get("target") or not emphasis.get("annotation"):
                        add(pid, "R.05", "chart evidence needs one explicit emphasis target")
                    elif "label" not in str(emphasis.get("mode") or ""):
                        add(pid, "V.02", "chart emphasis must use a direct label, not hue alone")
                    if page.get("intent") == "part-to-whole" and not (item.get("profile") or {}).get("sums_to_whole"):
                        add(pid, "R.07", "part-to-whole data does not sum to a whole")
                    zero = ((encoding.get("scale") or {}).get("y") or {}).get("zero")
                    if zero is False and (page.get("intent") not in {"change-over-time", "deviation"} or not encoding.get("axis_break")):
                        add(pid, "R.06", "truncated baseline needs change/deviation intent and an axis break")

            columns, rows = page_data(page)
            if evidence and columns and rows:
                claim = page.get("claim") or {}
                subject = claim.get("subject") or {}
                field, selector, measure = subject.get("field"), subject.get("selector"), claim.get("measure")
                if field not in columns:
                    add(pid, "R.01", f"claim subject field {field!r} is not in evidence columns")
                elif not any(str(row[columns.index(field)]).strip() == str(selector).strip() for row in rows if len(row) > columns.index(field)):
                    add(pid, "R.01", f"claim subject {selector!r} is not in evidence field {field!r}")
                if measure not in columns:
                    add(pid, "R.01", f"claim measure {measure!r} is not in evidence columns")
                elif field in columns:
                    bound = next((row for row in rows if len(row) > columns.index(field) and str(row[columns.index(field)]).strip() == str(selector).strip()), None)
                    computed = parse_number(bound[columns.index(measure)]) if bound and len(bound) > columns.index(measure) else None
                    magnitude = (claim.get("magnitude") or {}).get("value") if isinstance(claim.get("magnitude"), dict) else None
                    if magnitude is not None and (computed is None or abs(float(magnitude) - computed) > 1e-6):
                        add(pid, "R.02", f"claim magnitude {magnitude!r} does not match bound value {computed!r}")
                    direction = claim.get("direction")
                    if computed is not None and ((direction == "increase" and computed < 0) or (direction == "decrease" and computed > 0)):
                        add(pid, "R.02", f"claim direction {direction!r} disagrees with signed value {computed}")
                    if magnitude is not None:
                        key = tuple(str(claim.get(name) or "").strip() for name in ("measure", "scope", "period"))
                        previous = consistency.get(key)
                        if previous and abs(previous[1] - float(magnitude)) > 1e-6:
                            add(pid, "P.02", f"{key} disagrees with {previous[0]}: {magnitude} != {previous[1]}")
                        else:
                            consistency[key] = (pid, float(magnitude))
        if page.get("pack") not in PACKS:
            add(pid, "PACK_UNKNOWN", repr(page.get("pack")))
        if template not in {"cover", "toc", "chapter"} and not str(page.get("source") or (page.get("provenance") or {}).get("source") or "").strip():
            add(pid, "NO_SOURCE", "source or provenance.source is required")

        content = page.get("content") or {}
        if not isinstance(content, dict):
            add(pid, "CONTENT_INVALID", "content must be an object")
            content = {}
        blocks = content.get("blocks") if isinstance(content, dict) else None
        if blocks is None:
            blocks = page.get("blocks") or []
        if not isinstance(blocks, list):
            add(pid, "BLOCKS_INVALID", "content.blocks must be an array")
            blocks = []
        for block in blocks:
            kind = block.get("kind") if isinstance(block, dict) else None
            if kind not in BLOCKS:
                add(pid, "BLOCK_UNKNOWN", repr(kind))
                continue
            if kind == "table":
                columns, rows = block.get("columns") or [], block.get("rows") or []
                if len(columns) > 7:
                    add(pid, "WIDE_TABLE", f"{len(columns)} columns; use appendix bypass")
                if len(rows) > 12:
                    add(pid, "LONG_TABLE", f"{len(rows)} rows; paginate")
                if any(len(row) != len(columns) for row in rows):
                    add(pid, "RAGGED_ROWS", "table row width differs from columns")
            if kind == "fig":
                if block.get("viz") not in VIZ | VIZ_ALIASES:
                    add(pid, "VIZ_UNKNOWN", repr(block.get("viz")))
                if not block.get("fallback"):
                    add(pid, "V.04", "figure needs a static table/text fallback")
            if kind == "embed" and not (block.get("fallback") or block.get("fallback_img") or block.get("fallback_text")):
                add(pid, "V.04", "embed needs a static fallback")
        viz = page.get("visualization")
        if isinstance(viz, str) and viz not in VIZ | VIZ_ALIASES:
            add(pid, "VIZ_UNKNOWN", repr(viz))
        for path, value in strings({"title": page.get("title"), "takeaway": page.get("takeaway"), "content": content}, pid):
            if MARKDOWN.search(value):
                add(pid, "MD_IN_SLOT", f"{path}: {value[:40]!r}")
        if page.get("overflow_of") and page["overflow_of"] not in seen:
            add(pid, "FORWARD_CONT", f"overflow_of={page['overflow_of']} not seen yet")

        section = tuple((page.get("outline_path") or [])[:-1])
        layout_run = layout_run + 1 if layout == previous_layout and section == previous_section and template != "roster" else 1
        previous_layout = layout
        previous_section = section
        if layout_run > int(policy.get("max_layout_run", 4)):
            add(pid, "L.03", f"layout {layout} repeats {layout_run} times", "warn")

    if version == "2.0.0":
        argument = plan.get("argument") or {}
        root = argument.get("root")
        nodes = argument.get("nodes")
        if root not in pages_by_id:
            add("$", "A.03", "argument root is missing")
        if not isinstance(nodes, list) or {node.get("id") for node in nodes if isinstance(node, dict)} != set(pages_by_id):
            add("$", "A.02", "argument nodes must match page ids")
        claims = {pid for pid, page in pages_by_id.items() if (page.get("node") or {}).get("role") == "claim"}
        if root not in claims:
            add("$", "A.03", "argument root must be a claim node")
        children = defaultdict(list)
        for pid, page in pages_by_id.items():
            node = page.get("node") or {}
            parent = node.get("supports")
            if node.get("role") == "evidence":
                if parent not in claims:
                    add(pid, "A.02", "evidence must support exactly one claim")
                else:
                    children[parent].append(pid)
            elif node.get("role") == "claim" and parent:
                if parent not in claims:
                    add(pid, "A.02", "supporting claim must support another claim")
                else:
                    children[parent].append(pid)
        roots = {claim for claim in claims if (pages_by_id[claim].get("node") or {}).get("supports") not in claims}
        if roots != {root}:
            add("$", "A.03", f"expected exactly one root claim ({root}), found {sorted(roots)}")

        def descendants(pid, trail=()):
            if pid in trail:
                add(pid, "A.03", "argument graph contains a cycle")
                return set(), 99
            found, depth = set(), 1
            for child in children.get(pid, []):
                found.add(child)
                below, child_depth = descendants(child, (*trail, pid)) if child in claims else (set(), 1)
                found.update(below)
                depth = max(depth, child_depth + 1)
            return found, depth

        for claim in claims:
            below, depth = descendants(claim)
            if not any((pages_by_id[item].get("node") or {}).get("role") == "evidence" for item in below):
                add(claim, "A.01", "claim has no evidence descendant")
            if claim == root and depth > int(policy.get("max_argument_depth", 3)):
                add("$", "A.03", f"argument depth {depth} exceeds policy")
        for pid, page in pages_by_id.items():
            if (page.get("node") or {}).get("role") == "question":
                if not any((candidate.get("node") or {}).get("answers") == pid for candidate in pages_by_id.values()):
                    add(pid, "A.04", "question has no answering claim edge")
        order = {pid: i for i, pid in enumerate(pages_by_id)}
        situations = [order[pid] for pid, page in pages_by_id.items() if (page.get("node") or {}).get("role") == "situation"]
        complications = [order[pid] for pid, page in pages_by_id.items() if (page.get("node") or {}).get("role") == "complication"]
        if situations and complications and min(complications) < min(situations):
            add("$", "A.05", "complication precedes its situation", "warn")
        for parent, child_ids in children.items():
            scopes = defaultdict(list)
            for child in child_ids:
                if child in claims:
                    scopes[str((pages_by_id[child].get("claim") or {}).get("scope") or "")].append(child)
            for scope, siblings in scopes.items():
                if scope and len(siblings) > 1:
                    add(parent, "A.06", f"sibling claims overlap scope {scope!r}: {siblings}", "warn")
        back = sum(1 for page in pages_by_id.values() if (page.get("node") or {}).get("role") == "back-matter")
        argument_pages = len(pages_by_id) - back
        if argument_pages and back / argument_pages > float(policy.get("backmatter_ratio", .45)):
            add("$", "A.07", f"back-matter ratio {back / argument_pages:.2f} exceeds policy", "warn")
        if as_of_dates and (max(as_of_dates) - min(as_of_dates)).days > int(policy.get("as_of_window_days", 120)):
            add("$", "P.03", "source as_of dates exceed the policy window", "warn")
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--design")
    parser.add_argument("--policy")
    parser.add_argument("--out")
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    policy_path = Path(args.policy) if args.policy else Path(__file__).resolve().parent.parent / "design" / "policy-v2.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8")) if policy_path.is_file() else {}
    findings = validate(plan, policy)
    hard = sum(1 for *_, severity in findings if severity == "hard")
    warn = sum(1 for *_, severity in findings if severity == "warn")
    report = {"version": "2.0.0", "pages": len(plan.get("pages") or []), "hard": hard, "warn": warn, "findings": [
        {"page": page, "code": code, "sev": severity, "msg": message} for page, code, message, severity in findings
    ]}
    if args.out:
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for page, code, message, severity in findings:
        print(f"  {severity.upper():<5} {code:<18} {page:>8}  {message}")
    print(f"gate_schema: {report['pages']} pages · hard {hard} · warn {warn}")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
