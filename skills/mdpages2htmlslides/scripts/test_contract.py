#!/usr/bin/env python3
"""Runnable contract check: translations, 16 SVGs, renderer, legacy fallback."""
from __future__ import annotations

import importlib.util
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))

from baslide_viz import LOCKED_L3, figure_for_page


def load(name: str, file):
    spec = importlib.util.spec_from_file_location(name, Path(file) if isinstance(file, Path) else HERE / file)
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
    layout_gate = load("gate_layout", "gate_layout.py")
    audit = load("audit_html", REPO / "skills/deck-audit/scripts/audit-html.py")
    parser = audit.SlideParser()
    parser.feed('<section class="slide"><h2>Only visible</h2><pre hidden class="sd-audit-copy">Revenue 999</pre></section>')
    assert parser.slides[0]["text"].strip() == "Only visible"
    assert not audit.numeric_authorized("4", "number", {"42"})
    assert not audit.numeric_authorized("999", "number", {"42"})
    assert audit.numeric_authorized("100 SKU", "quantity", {"100"})
    bubble = {"visualization": "bubble", "content": {"rows": [["A", "74", "4.1"], ["B", "321", "4.8"]]}}
    assert {"0", "197.5", "4.4"} <= audit.renderer_derived_norms(bubble)
    assert "999" not in audit.renderer_derived_norms(bubble)
    assert {"12", "133"} <= audit.renderer_derived_norms({"template": "chapter"}, 132)
    sparse = figure_for_page("sparse", "| label | value |\n| --- | ---: |\n| Kept | 6.3 |\n| Missing | — |\n", preset_fill="diverging-bar")
    assert sparse and "Missing" not in sparse.svg
    layout_contract = json.loads((HERE.parent / "design/page-types.json").read_text(encoding="utf-8"))
    policy = json.loads((HERE.parent / "design/policy-v2.json").read_text(encoding="utf-8"))
    layout_contract["contrast"] = policy["contrast"]
    layout_contract["_body_floor_px"] = policy["type_floor"]["body_u"] * 16
    layout_contract["_data_floor_px"] = policy["type_floor"]["data_u"] * 16
    layout_contract["page_types"] = {name: {"known": True} for name in layout_contract["page_templates"]}
    rec = {"id": "p-test", "type": "statement", "fill_ratio": .7, "density": .7, "blocks": [], "min_body_font": 16, "min_data_font": 13, "min_text_contrast": 5, "min_mark_contrast": 2.5, "greyscale_issues": 1}
    perception, _ = layout_gate.judge(rec, layout_contract, {"p-test"})
    assert {"V.01", "V.02", "V.03"} <= {item["code"] for item in perception}
    rec.update(min_body_font=None, min_data_font=16, min_mark_contrast=4, greyscale_issues=0)
    data_only, _ = layout_gate.judge(rec, layout_contract, {"p-test"})
    assert "V.03" not in {item["code"] for item in data_only}
    pages = []
    intent = {
        "pareto": "ranking", "slope": "ranking", "line-dual": "change-over-time", "calendar": "change-over-time",
        "waterfall": "deviation", "diverging-bar": "deviation", "treemap": "part-to-whole", "funnel": "part-to-whole",
        "venn": "part-to-whole", "hist-cdf": "distribution", "heatmap": "distribution", "bubble": "correlation",
        "quadrant": "correlation", "radar": "correlation", "sankey": "flow", "network": "flow",
    }
    provenance = {"dataset": "golden fixture", "query_hash": "12345678abcd", "as_of": "2026-08-19", "transform_chain": ["golden"], "owner": "test"}
    for index, viz in enumerate(LOCKED_L3, 1):
        fig = figure_for_page(viz, TABLE, preset_fill=viz)
        assert fig and fig.fill == viz and "<svg" in fig.svg, viz
        assert ">n=" not in fig.svg, viz
        assert fig.table_html, f"{viz} needs a table fallback"
        pages.append({
            "id": f"p-{index:03d}",
            "template": "chart",
            "title": f"{viz} golden",
            "source": "golden fixture",
            "takeaway": "The selected recipe remains identifiable.",
            "visualization": viz,
            "node": {"role": "claim" if index == 1 else "evidence", "supports": None if index == 1 else "p-001"},
            "claim": {"subject": {"field": "label", "selector": "Alpha"}, "measure": "value", "direction": "describe", "magnitude": {"value": 42, "unit": "count"}, "period": "2026", "scope": "golden", "render": "Alpha is the emphasized datum."},
            "intent": intent[viz],
            "evidence": [{"kind": "chart", "profile": {"rows": 4, "series": 2, "measures": ["value", "peer"], "dims": ["nominal"], "negatives": False, "sums_to_whole": viz in {"treemap", "funnel", "venn"}, "magnitude_ratio": 5.25, "missingness": 0}, "encoding": {"preset": viz, "mapping": {"x": "label", "y": "value"}, "geom": [viz], "stat": ["identity"], "position": "identity", "scale": {"y": {"zero": True}}, "coord": "cartesian", "facet": None, "emphasis": {"target": "Alpha", "mode": "accent+label", "annotation": "Alpha"}}, "source": provenance}],
            "layout": {"solved": "fig-rail", "grid": "12x8", "trace": ["golden"]},
            "pack": "mid",
            "units": [f"u-{index:04d}"],
            "overflow_of": None,
            "content": {"blocks": [{"kind": "fig", "viz": viz, "fallback": {"columns": ["label", "value", "peer"], "rows": [["Alpha", 42, 18]]}, "data": {
                "columns": ["label", "value", "peer"],
                "rows": [["Alpha", 42, 18], ["Beta", 31, 27], ["Gamma", 19, 35], ["Delta", 8, 20]],
            }}]},
        })
    translated = [
        {"id": f"p-{100 + i:03d}", "template": old, "title": old, "source": "legacy", "takeaway": "", "visualization": None,
         "node": {"role": "situation", "supports": None}, "claim": {"subject": {"field": "topic", "selector": old}, "measure": "content", "direction": "describe", "magnitude": None, "period": "source", "scope": "legacy", "render": old}, "intent": None, "evidence": [],
         "layout": {"solved": "full", "grid": "12x8", "trace": ["legacy translation"]}, "pack": "mid", "content": {"blocks": [{"kind": "text", "text": "ok"}]}}
        for i, old in enumerate(("quote", "playbook", "gallery", "interactive"))
    ]
    all_pages = pages + translated
    plan = {"contract_version": "2.0.0", "title": "golden", "mode": "slides", "aspect": "16:9", "argument": {"root": "p-001", "nodes": [{"id": p["id"], **p["node"]} for p in all_pages]}, "pages": all_pages}
    findings = gate.validate(plan)
    assert not [item for item in findings if item[3] == "hard"], findings
    pyramid = copy.deepcopy(plan)
    pyramid["pages"][1]["node"] = {"role": "claim", "supports": "p-001"}
    pyramid["pages"][2]["node"]["supports"] = "p-002"
    pyramid["argument"]["nodes"] = [{"id": page["id"], **page["node"]} for page in pyramid["pages"]]
    pyramid_findings = gate.validate(pyramid)
    assert not [item for item in pyramid_findings if item[3] == "hard"], pyramid_findings

    inconsistent = copy.deepcopy(plan)
    inconsistent["pages"][1]["claim"]["magnitude"]["value"] = 999
    inconsistent["pages"][2]["claim"]["subject"]["field"] = "does-not-exist"
    truth_codes = {code for _, code, _, severity in gate.validate(inconsistent) if severity == "hard"}
    assert {"P.02", "R.01", "R.02"} <= truth_codes, truth_codes
    bad_codes = {code for _, code, _, _ in gate.validate({"title": "bad", "pages": [{
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
        assert "sd-audit-copy" not in html
        assert 'data-skin="TIANSIGHT"' in html
        assert 'data-contract="2.0.0"' in html

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

        blocked = subprocess.run([
            sys.executable, str(HERE / "export_pdf.py"), "--html", str(old_out),
            "--schema-report", str(old_plan / "missing-schema.json"),
            "--layout-report", str(old_plan / "missing-layout.json"),
            "--out", str(old_plan / "slides" / "blocked.pdf"),
        ], capture_output=True, text=True)
        assert blocked.returncode and "schema report missing" in (blocked.stdout + blocked.stderr)
    print("test_contract.py ok · 16 SVG recipes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
