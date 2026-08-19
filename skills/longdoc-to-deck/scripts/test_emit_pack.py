#!/usr/bin/env python3
"""Smoke: emit-pack writes slide-plan + locked fill; viz draws an SVG."""

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
    return mod.emit

VIZ_DIR = Path(__file__).resolve().parents[2] / "md-to-html-slides" / "scripts"


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
        emit = _load_emit()
        pack = emit(work, genre="diagnosis", skin="TIANSIGHT")
        assert pack["ready"] is True
        assert (work / "slide-plan.json").is_file()
        assert (work / "MANIFEST.md").is_file()
        plan = json.loads((work / "slide-plan.json").read_text(encoding="utf-8"))
        slide = plan["slides"][0]
        assert slide["job"] == "chart"
        assert slide["fill"] in {None, "pareto", "diverging-bar", "treemap", "hist-cdf"}
        if slide["fill"]:
            assert lock_fill(slide["fill"]) == slide["fill"]
        md = (work / "pages" / "p-0001.md").read_text(encoding="utf-8")
        fig = figure_for_page(slide["title"], md, preset_fill=slide["fill"])
        assert fig is not None, "expected SVG figure"
        assert "<svg" in fig.svg
        print(f"OK emit-pack fill={slide['fill']} recipe={slide.get('recipe')} svg={len(fig.svg)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
