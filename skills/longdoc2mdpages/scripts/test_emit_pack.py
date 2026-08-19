#!/usr/bin/env python3
"""Smoke: emit-pack writes a GF deck-plan and every locked viz draws SVG."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

def _load_emit():
    script = Path(__file__).resolve().parent / "emit-pack.py"
    spec = importlib.util.spec_from_file_location("emit_pack", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_budget():
    script = Path(__file__).resolve().parent / "budget.py"
    spec = importlib.util.spec_from_file_location("page_budget", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

VIZ_DIR = Path(__file__).resolve().parents[2] / "mdpages2htmlslides" / "scripts"


def _mini_work(root: Path) -> Path:
    work = root / "mini"
    work.mkdir()
    (work / "pages").mkdir()
    units = {
        "u-0001": "口径 A 二八",
    }
    index = {
        "source": "mini.md",
        "total_units": 1,
        "units": [{"id": "u-0001", "kind": "table", "digest": "二八", "heading_path": ["肆"]}],
    }
    page_md = """# 口径 A 二八

role: `chart`
units: u-0001

| 分类 | 额占比 |
|---|---:|
| 首选品 | 63.2% |
| 必售品 | 23.5% |
| 观察品 | 10.3% |
| 长尾品 | 3.1% |
"""
    (work / "pages" / "p-0001.md").write_text(page_md, encoding="utf-8")
    (work / "outline.md").write_text("- 肆（u-0001）\n", encoding="utf-8")
    (work / "index.md").write_text("- u-0001 table 二八\n", encoding="utf-8")
    (work / "units.json").write_text(json.dumps(units), encoding="utf-8")
    (work / "index.json").write_text(json.dumps(index), encoding="utf-8")
    deck = {
        "version": "1",
        "source": "mini.md",
        "pages": [
            {
                "id": "p-0001",
                "role": "chart",
                "title": "口径 A 二八 · 帕累托",
                "units": ["u-0001"],
                "outline_path": ["肆"],
                "material": {
                    "table": {
                        "columns": ["分类", "额占比"],
                        "rows": [["首选品", "63.2%"], ["必售品", "23.5%"]],
                    }
                },
                "source": "",
                "how_to_read": "",
                "takeaway": "",
                "fit": {"verdict": "ok"},
            }
        ],
    }
    (work / "deck.json").write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")
    (work / "audit-source.json").write_text(json.dumps({"counts": {"hard": 0}, "findings": []}), encoding="utf-8")
    return work


def main() -> int:
    import sys

    sys.path.insert(0, str(VIZ_DIR))
    from baslide_viz import figure_for_page, lock_fill

    with tempfile.TemporaryDirectory() as tmp:
        work = _mini_work(Path(tmp))
        emit_mod = _load_emit()
        pack = emit_mod.emit(work, genre="diagnosis", skin="TIANSIGHT")
        assert pack["ready"] is True
        assert (work / "deck-plan.json").is_file()
        assert (work / "MANIFEST.md").is_file()
        plan = json.loads((work / "deck-plan.json").read_text(encoding="utf-8"))
        assert plan["contract_version"] == "2.0.0"
        assert plan["title"] == "mini"
        assert plan["argument"]["root"] == "p-0001"
        slide = plan["pages"][0]
        assert slide["template"] == "chart"
        assert slide["visualization"] in {None, "pareto", "diverging-bar", "treemap", "hist-cdf"}
        if slide["visualization"]:
            assert lock_fill(slide["visualization"]) == slide["visualization"]
            assert slide["content"]["blocks"][0]["fallback"]["rows"]
        assert slide["layout"]["grid"] == "12x8"
        assert slide["claim"]["measure"] == "额占比"
        assert slide["evidence"][0]["source"]["query_hash"]
        budget = _load_budget()
        assert budget.predict(slide, slide.get("layout") or "full", slide.get("pack") or "mid") > 0
        dense = {**slide, "id": "p-dense", "template": "roster", "title": "dense", "units": ["u-1"], "content": {"columns": ["a", "b"], "rows": [[str(i), "x" * 250] for i in range(7)], "blocks": [{"kind": "table", "rows": [[str(i), "x" * 250] for i in range(7)]}]}}
        split = emit_mod.split_dense_rosters([dense])
        assert len(split) == 3 and split[1]["overflow_of"] == "p-dense" and split[1]["units"] == []
        renumbered, root = emit_mod.renumber_pages(split, "p-dense")
        assert root == "p-0001" and renumbered[1]["overflow_of"] == "p-0001"
        md = (work / "pages" / "p-0001.md").read_text(encoding="utf-8")
        fig = figure_for_page(slide["title"], md, preset_fill=slide["visualization"])
        assert fig is not None, "expected SVG figure"
        assert "<svg" in fig.svg
        print(f"OK emit-pack fill={slide['visualization']} svg={len(fig.svg)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
