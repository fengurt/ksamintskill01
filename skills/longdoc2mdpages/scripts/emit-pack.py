#!/usr/bin/env python3
"""Close a longdoc2mdpages pack around the GF4p2slides page-plan seam."""

from __future__ import annotations

import argparse
import importlib.util
import json
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


def content_from_page(page: dict) -> dict:
    material = page.get("material") or {}
    table = material.get("table") if isinstance(material, dict) else {}
    if not isinstance(table, dict):
        table = {}
    blocks = []
    bullets = (material.get("bullets") or []) if isinstance(material, dict) else []
    if bullets:
        blocks.append({"kind": "bullets", "items": bullets[:6]})
    if table.get("columns") and table.get("rows"):
        blocks.append({
            "kind": "table",
            "columns": table.get("columns") or [],
            "rows": table.get("rows") or [],
            "sum": table.get("sum") or [],
        })
    return {
        "blocks": blocks,
        "columns": table.get("columns") or [],
        "rows": table.get("rows") or [],
        "sum": table.get("sum") or [],
        "bullets": bullets,
    }


def build_deck_plan(work: Path, deck: dict, *, genre: str, skin: str, viz) -> dict:
    pages = []
    fill_counts: dict[str, int] = {}
    for page in deck.get("pages") or []:
        role = page.get("role") or "statement"
        job = ROLE_TO_JOB.get(role, "statement")
        material = page_material(work, page)
        assigned = viz.assign_page_fill(page.get("title") or "", material, role)
        fill = assigned.get("fill")
        recipe = assigned.get("recipe")
        if fill:
            fill_counts[fill] = fill_counts.get(fill, 0) + 1
        path = page.get("outline_path") or []
        how = (page.get("how_to_read") or "").strip() or assigned.get("how_to_read") or ""
        content = content_from_page(page)
        if fill:
            content["blocks"].insert(0, {
                "kind": "fig",
                "viz": fill,
                "data": {"columns": content["columns"], "rows": content["rows"]},
                "caption": how,
            })
        source = page.get("source") or deck.get("source") or " ".join(page.get("units") or [])
        plan_page = {
            "id": page["id"],
            "template": job,
            "shell": JOB_TO_SHELL.get(job, "body"),
            "layout": page.get("layout"),
            "pack": page.get("pack") or "mid",
            "overflow_of": page.get("overflow_of"),
            "title": page.get("title") or page["id"],
            "source": source,
            "takeaway": page.get("takeaway") or "",
            "visualization": fill,
            "units": page.get("units") or [],
            "outline_path": path,
            "provenance": {
                "source": source,
                "how_to_read": how,
                "unit": page.get("unit") or "",
            },
            "content": content,
        }
        pages.append(plan_page)
        page["fill"] = fill
        if recipe and recipe != fill:
            page["recipe"] = recipe
        elif "recipe" in page:
            del page["recipe"]
        if how and not (page.get("how_to_read") or "").strip():
            page["how_to_read"] = how
    return {
        "contract_version": "1.0.0",
        "title": deck.get("title") or Path(deck.get("source") or work.name).stem,
        "deck_name": deck.get("title") or Path(deck.get("source") or work.name).stem,
        "brand_skill": skin,
        "mode": "slide",
        "source": deck.get("source") or "",
        "genre": genre,
        "theme": skin,
        "baslide": "modules/baslide01",
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
    for p in pages:
        r = p.get("role") or "?"
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
            "pages": len(pages),
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
        f"emit-pack: pages={len(pages)} fills={pack['counts']['fills']} → {work / 'deck-plan.json'}",
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
