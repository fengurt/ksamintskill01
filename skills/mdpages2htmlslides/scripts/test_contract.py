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

from baslide_viz import LOCKED_L3, assign_page_fill, figure_for_page


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
    promoted = assign_page_fill("门店评分比较", TABLE, "roster")
    assert promoted["fill"], promoted
    assert not assign_page_fill("普通表格", TABLE, "roster")["fill"]
    long_roster = TABLE + "| Epsilon | 7 | 19 |\n| Zeta | 6 | 18 |\n| Eta | 5 | 17 |\n| Theta | 4 | 16 |\n| Iota | 3 | 15 |\n"
    assert not assign_page_fill("方法论路径矩阵", long_roster, "roster")["fill"]
    semantic_md = "- 品牌根系\n- 体验触点\n- 传播接口\n"
    semantic = assign_page_fill("三层接口关系", semantic_md, "statement")
    assert semantic["fill"] == "network", semantic
    semantic_figure = figure_for_page("三层接口关系", semantic_md, preset_fill="network")
    assert semantic_figure and all(label in semantic_figure.svg for label in ("品牌根系", "体验触点", "传播接口"))
    assert "1家" not in semantic_figure.svg
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
        renderer = load("render_deck", "render-deck.py")
        assert renderer.scrub_internal_copy({"takeaway": "（溢出链末页）", "items": ["保留"]}) == {"takeaway": "", "items": ["保留"]}
        editorial = renderer.editorial_figure(
            {"id": "p-editorial", "title": "先把账算清", "takeaway": "先把账算清，再谈策略。", "content": {"blocks": [{"kind": "bullets", "items": ["看清结构", "锁定瓶颈", "验证动作"]}]}},
            "",
        )
        assert 'class="sd-quote"' in editorial and all(item in editorial for item in ("看清结构", "锁定瓶颈", "验证动作"))
        insight = renderer.insight_figure(
            {"id": "p-insight", "title": "洞察 12｜数据质量侵蚀收入"},
            "现象：32.1% 的堂食单人数为 0。\n\n证据：最高门店缺失率 35.4%。\n\n商业含义：年化漏收在 67 万元以上。",
        )
        assert all(item in insight for item in ("32.1%", "35.4%", "67 万元", "现象", "证据", "width:32.1%"))
        data_quality = renderer.data_quality_insight_html()
        assert all(item in data_quality for item in ("56,710 / 176,886", "67.49 万元", "门店原始值（10 店）", "不存在稳定的单变量关系", "尚不能识别各因素的因果贡献", "各抽 20 桌"))
        assert data_quality.count("<table") == 2
        assert "更像" not in data_quality and "必须现场核实" not in data_quality
        chaofa_chart = {"id": "p-0033", "title": "洞察 4", "content": {}}
        assert renderer.chaofa_insight_visual_page(chaofa_chart, Path(tmp) / "chaofa")
        assert chaofa_chart["fill"] == "diverging-bar" and chaofa_chart["content"]["rows"][1] == ["平台外卖营收", "3.9%"]
        inferred = renderer.insight_figure(
            {"id": "p-case", "title": "餐具选择与摆盘建议"},
            "当前状态：报损记录过少，无法分析。\n\n可从数据推断的一条摆盘线索：新店位上菜渗透率 11.9%，是老店的 5 倍。",
        )
        assert all(item in inferred for item in ("当前状态", "11.9%", "5 倍"))
        argument = {"id": "p-long-kpi", "role": "kpi", "title": "长标签 KPI", "content": {"blocks": [
            {"kind": "kpi-card", "label": "这是一段需要完整表达因果关系的证据标签", "value": "31 元"},
            {"kind": "kpi-card", "label": "另一个关键市场基准", "value": "83 元"},
        ]}}
        assert renderer.metric_value("−44.5%") == -44.5 and renderer.metric_unit("31 元") == "元"
        table = renderer.structured_html({"content": {"blocks": [{"kind": "table", "columns": ["#", "资产", "体量", "来源", "时点", "用途", "可信度"], "rows": [["1", "202604广州.parquet", "195,900 行 × 38 列", "大众点评", "2026-04", "商圈诊断", "高"]]}]}})
        assert all(item in table for item in ("sd-table--7", "sd-table--wide", "<colgroup>", 'class="col-index num"', 'class="col-key"', 'class="col-status"'))
        assert 'class="col-measure num"' not in table
        text_rows = [["T1", "品牌梯队.csv", "按品牌聚合，并保留店数、评论合计、人均中位、评分均、四维子评分均、上榜数、榜首数与全天店数等完整口径说明；同时保留查询条件、派生字段和主报告引用关系。"], ["T2", "门店明细.csv", "按门店全字段生成，并增加营业时段带、商场店、明厨亮灶和推荐菜数量等派生列，供主报告多个章节引用。"]]
        text_heatmap = {"id": "p-text-table", "role": "chart-table", "fill": "heatmap", "visualization": "heatmap", "title": "派生表", "content": {"columns": ["编号", "文件", "来源"], "rows": text_rows, "blocks": [{"kind": "fig"}, {"kind": "table", "columns": ["编号", "文件", "来源"], "rows": text_rows}]}}
        text_heatmap = renderer.prepare_visual_page(text_heatmap, Path(tmp), {}, REPO / "modules/baslide01")
        assert text_heatmap["_render_job"] == "roster" and not text_heatmap["fill"] and all(block["kind"] != "fig" for block in text_heatmap["content"]["blocks"])
        prepared = renderer.prepare_visual_page(argument, Path(tmp), {}, REPO / "modules/baslide01")
        assert prepared["_argument_kpi"] and all(item in renderer.argument_kpi_html(prepared) for item in ("31 元", "83 元", "sd-argument-grid", "sd-argument-meter", "is-generic"))
        curated = {**prepared, "_argument_thesis": "不说菜系，说地方：红桥", "_argument_question": "叫什么？", "_argument_support": "桥是画面。"}
        assert all(item in renderer.argument_kpi_html(curated) for item in ("100%", "4.1×", "54%", "market-band"))
        dish = {**argument, "id": "p-dish", "title": "5.1.5 餐具选择与摆盘建议"}
        dish_prepared = renderer.prepare_visual_page(dish, Path(tmp), {}, REPO / "modules/baslide01")
        assert dish_prepared["_dish_example"] and all(item in renderer.argument_kpi_html(dish_prepared) for item in ("8.2%", "1.8%", "287.5 份"))
        opportunity = {"id": "p-opportunity", "role": "kpi", "title": "机会 1｜包间午市使用率提升 — 年化 946,708 元", "content": {}}
        assert renderer.opportunity_visual_page(opportunity, "假设：老店使用率 23.7% → 30.9%；新店 35.4% → 43.8%。")
        assert opportunity["fill"] == "slope" and opportunity["content"]["rows"] == [["老店", "23.7%", "30.9%"], ["新店", "35.4%", "43.8%"]]
        opportunity_with_ticket = {"id": "p-opportunity-ticket", "role": "kpi", "title": "机会 1｜包间午市使用率提升 — 年化 946,708 元", "content": {}}
        renderer.opportunity_visual_page(opportunity_with_ticket, "现状：老店客单 1,253.8 元；新店客单 1,339.9 元。假设：老店使用率 23.7% → 30.9%；新店 35.4% → 43.8%。")
        assert opportunity_with_ticket["content"]["columns"][-1] == "午市包间客单"
        contribution = {"id": "p-contribution", "role": "chart-table", "title": "机会 7｜漏损减半 — 年化 70,254 元", "content": {"columns": ["门店", "年化节约"], "rows": [["老店", "40,549 元"], ["新店", "29,705 元"], ["合计", "70,254 元"]]}}
        assert renderer.opportunity_visual_page(contribution, "") and contribution["fill"] == "pareto"
        transparent_logo = REPO / "modules/baslide01/templates/TIANSIGHT/logo/侍天.png"
        selected_logo, _ = renderer.verified_brand_logo(Path(tmp), "TIANSIGHT", transparent_logo)
        assert selected_logo == transparent_logo
        work = Path(tmp) / "plan"
        work.mkdir()
        (work / "deck-plan.json").write_text(json.dumps(plan), encoding="utf-8")
        out = work / "slides" / "deck.html"
        subprocess.run([sys.executable, str(HERE / "render-deck.py"), "--work", str(work), "--theme", "TIANSIGHT", "--baslide", str(REPO / "modules/baslide01"), "-o", str(out)], check=True)
        html = out.read_text(encoding="utf-8")
        assert 'class="sd-data"' not in html
        assert "sd-audit-copy" not in html
        assert "溢出链末页" not in html
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
