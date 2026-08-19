#!/usr/bin/env python3
"""Runnable contract check: translations, 16 SVGs, renderer, legacy fallback."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))

from baslide_viz import LOCKED_L3, figure_for_page


def load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TABLE = """| label | value | peer |
| --- | ---: | ---: |
| Alpha | 42 | 18 |
| Beta | 31 | 27 |
| Gamma | 19 | 35 |
| Delta | 8 | 20 |
"""


def main() -> int:
    gate = load("gate_schema", "gate_schema.py")
    pages = []
    for index, viz in enumerate(LOCKED_L3, 1):
        fig = figure_for_page(viz, TABLE, preset_fill=viz)
        assert fig and fig.fill == viz and "<svg" in fig.svg, viz
        assert fig.table_html, f"{viz} needs a table fallback"
        pages.append({
            "id": f"p-{index:03d}",
            "template": "chart",
            "title": f"{viz} golden",
            "source": "golden fixture",
            "takeaway": "The selected recipe remains identifiable.",
            "visualization": viz,
            "layout": "fig-rail",
            "pack": "mid",
            "units": [f"u-{index:04d}"],
            "overflow_of": None,
            "content": {"blocks": [{"kind": "fig", "viz": viz, "data": {
                "columns": ["label", "value", "peer"],
                "rows": [["Alpha", 42, 18], ["Beta", 31, 27], ["Gamma", 19, 35], ["Delta", 8, 20]],
            }}]},
        })
    translated = [
        {"id": f"p-{100 + i:03d}", "template": old, "title": old, "source": "legacy", "takeaway": "", "visualization": None, "layout": "full", "pack": "mid", "content": {"blocks": [{"kind": "text", "text": "ok"}]}}
        for i, old in enumerate(("quote", "playbook", "gallery", "interactive"))
    ]
    plan = {"contract_version": "1.0.0", "title": "golden", "mode": "slide", "pages": pages + translated}
    assert not gate.validate(plan)
    bad_codes = {code for _, code, _ in gate.validate({"title": "bad", "pages": [{
        "id": "bad", "template": "chart", "title": "bad", "source": "x", "takeaway": "",
        "visualization": None, "layout": "bogus", "pack": "bogus", "content": {"blocks": []},
    }]})}
    assert {"CONTRACT_VERSION", "ID_INVALID", "LAYOUT_UNKNOWN", "PACK_UNKNOWN"} <= bad_codes

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "plan"
        work.mkdir()
        (work / "deck-plan.json").write_text(json.dumps(plan), encoding="utf-8")
        out = work / "slides" / "deck.html"
        subprocess.run([sys.executable, str(HERE / "render-deck.py"), "--work", str(work), "--theme", "TIANSIGHT", "--baslide", str(REPO / "modules/baslide01"), "-o", str(out)], check=True)
        html = out.read_text(encoding="utf-8")
        assert html.count('class="sd-data"') == len(plan["pages"])
        assert 'data-skin="TIANSIGHT"' in html

        legacy = Path(tmp) / "legacy"
        legacy.mkdir()
        (legacy / "deck.json").write_text(json.dumps({"title": "legacy", "pages": [{"id": "p-0001", "role": "statement", "title": "Legacy", "material": {"bullets": ["still supported"]}}]}), encoding="utf-8")
        legacy_out = legacy / "slides" / "deck.html"
        subprocess.run([sys.executable, str(HERE / "render-deck.py"), "--work", str(legacy), "--baslide", str(REPO / "modules/baslide01"), "-o", str(legacy_out)], check=True)
        assert "Legacy" in legacy_out.read_text(encoding="utf-8")

        old_plan = Path(tmp) / "old-plan"
        old_plan.mkdir()
        (old_plan / "slide-plan.json").write_text(json.dumps({"deck_name": "old plan", "slides": [{
            "id": "p-0001", "job": "statement", "title": "Legacy slide-plan", "slots": {"bullets": ["still supported"]},
        }]}), encoding="utf-8")
        old_out = old_plan / "slides" / "deck.html"
        subprocess.run([sys.executable, str(HERE / "render-deck.py"), "--work", str(old_plan), "--baslide", str(REPO / "modules/baslide01"), "-o", str(old_out)], check=True)
        assert "Legacy slide-plan" in old_out.read_text(encoding="utf-8")
    print("test_contract.py ok · 16 SVG recipes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
