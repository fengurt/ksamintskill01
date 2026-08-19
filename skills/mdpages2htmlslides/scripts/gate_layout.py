#!/usr/bin/env python3
"""Gate 3 — render the deck headlessly and measure every slide.

This is the check the old pipeline never had. It does not read the plan's
opinion of whether a page fits; it renders and measures.

Emits audit-layout.json:
  { summary, histogram, pages:[{id, type, fill_ratio, findings:[{code, sev, msg}],
                                actions:[...]}] }

Exit 1 if any HARD finding remains. The agent's job is to consume `actions`
and edit deck-plan.json — never to hand-edit the HTML.

Usage:
  python3 gate_layout.py --html slides/deck.html --design ../design \
      --out audit-layout.json [--calibrate calibration.json]
"""
from __future__ import annotations
import argparse, json, statistics, sys
from pathlib import Path
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

MEASURE_JS = r"""
() => {
  // Slides are display:none unless .on — force them visible or every box is 0.
  const st = document.createElement('style');
  st.textContent = 'html.sd-present .sd-slide{display:block!important}';
  document.head.appendChild(st);

  // "Ink" = the union of leaf boxes that actually paint something. A grid
  // block always fills its region, so measuring the block box tells you
  // nothing; measuring the ink inside it tells you whether the page is full.
  const INK = new Set(['SVG','IMG','TABLE','IFRAME','CANVAS','HR']);
  function rgb(value) {
    const m = String(value || '').match(/rgba?\((\d+)[, ]+(\d+)[, ]+(\d+)/);
    return m ? [+m[1], +m[2], +m[3]] : null;
  }
  function colorAlpha(value) {
    const m = String(value || '').match(/rgba?\([^)]*?(?:[, /]\s*([\d.]+))?\)$/);
    return m && m[1] !== undefined ? +m[1] : 1;
  }
  function painted(value, bg, opacity=1) {
    const fg = rgb(value);
    if (!fg || !bg) return fg;
    const a = Math.max(0, Math.min(1, colorAlpha(value) * opacity));
    return fg.map((channel, index) => channel * a + bg[index] * (1 - a));
  }
  function lum(c) {
    const v = c.map(x => { x /= 255; return x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4; });
    return .2126 * v[0] + .7152 * v[1] + .0722 * v[2];
  }
  function contrast(a, b) {
    const hi = Math.max(lum(a), lum(b)), lo = Math.min(lum(a), lum(b));
    return (hi + .05) / (lo + .05);
  }
  function background(el) {
    for (let p = el; p; p = p.parentElement) {
      const value = getComputedStyle(p).backgroundColor;
      if (value && !value.endsWith(', 0)') && value !== 'rgba(0, 0, 0, 0)') return rgb(value);
    }
    return [255, 255, 255];
  }
  function inkBounds(root) {
    let top = Infinity, bottom = -Infinity, left = Infinity, right = -Infinity, found = false;
    (function walk(el) {
      const tag = el.tagName ? el.tagName.toUpperCase() : '';
      const leaf = el.children.length === 0 || INK.has(tag);
      if (leaf) {
        const paints = INK.has(tag) || (el.textContent || '').trim().length > 0;
        if (paints) {
          const r = el.getBoundingClientRect();
          if (r.width > 0 && r.height > 0) {
            found = true;
            if (r.top < top) top = r.top;
            if (r.bottom > bottom) bottom = r.bottom;
            if (r.left < left) left = r.left;
            if (r.right > right) right = r.right;
          }
        }
        if (INK.has(tag)) return;
      }
      for (const c of el.children) walk(c);
    })(root);
    return found ? {top, bottom, left, right} : null;
  }

  const out = [];
  document.querySelectorAll('section.sd-slide').forEach((s, i) => {
    const rec = {
      index: i,
      id: s.dataset.pageId || ('#' + i),
      type: s.dataset.pageType || s.dataset.type || null,
      layout: s.dataset.layout || null,
      pack: s.dataset.pack || 'mid',
      overflow_of: s.dataset.overflowOf || null,
      blocks: [],
    };
    const sr = s.getBoundingClientRect();
    const c = s.querySelector('.sd-content');
    if (c) {
      const cr = c.getBoundingClientRect();
      rec.box_h = Math.round(cr.height);
      rec.missing = c.querySelectorAll('[data-block="MISSING"]').length;

      let inkTop = Infinity, inkBottom = -Infinity, inkRight = -Infinity;
      let worstBlock = 0, blockOverflow = 0;

      // Fall back to the content box itself so the gate can measure any deck,
      // including one produced before the block contract existed.
      let regions = [...c.querySelectorAll(':scope > .sd-block')];
      if (regions.length === 0) regions = [c];
      regions.forEach(bl => {
        const br = bl.getBoundingClientRect();
        const ib = inkBounds(bl);
        const b = {kind: bl.dataset.block || '?', box_h: Math.round(br.height)};
        if (ib) {
          b.ink_h = Math.round(ib.bottom - ib.top);
          b.fill = br.height ? +((ib.bottom - ib.top) / br.height).toFixed(3) : 0;
          // ink escaping its own region = the block is over-stuffed
          b.over = +(Math.max(0, ib.bottom - br.bottom) / (br.height || 1)).toFixed(3);
          if (b.over > 0.01) blockOverflow++;
          if (b.fill > worstBlock) worstBlock = b.fill;
          if (ib.top < inkTop) inkTop = ib.top;
          if (ib.bottom > inkBottom) inkBottom = ib.bottom;
          if (ib.right > inkRight) inkRight = ib.right;
        } else {
          b.ink_h = 0; b.fill = 0; b.over = 0;
        }
        rec.blocks.push(b);
      });

      if (inkBottom > -Infinity) {
        // Page fill: how much of the content band carries ink, measured from
        // the top of the band (leading whitespace counts against the page).
        rec.ink_h = Math.round(inkBottom - cr.top);
        rec.fill_ratio = cr.height ? +((inkBottom - cr.top) / cr.height).toFixed(3) : 0;
        rec.h_ratio = cr.width ? +((inkRight - cr.left) / cr.width).toFixed(3) : 0;
        // density: mean ink fill across blocks — catches "one line per card"
        const fills = rec.blocks.filter(b => b.ink_h > 0).map(b => b.fill);
        rec.density = fills.length ? +(fills.reduce((a, b) => a + b, 0) / fills.length).toFixed(3) : 0;
      } else {
        rec.ink_h = 0; rec.fill_ratio = 0; rec.h_ratio = 0; rec.density = 0;
      }
      rec.block_overflow = blockOverflow;

      const visibleRegions = [...c.children].filter(el => {
        const r = el.getBoundingClientRect();
        const style = getComputedStyle(el);
        return r.width > 1 && r.height > 1 && style.display !== 'none' && style.visibility !== 'hidden';
      });
      rec.overlaps = [];
      for (let a = 0; a < visibleRegions.length; a++) for (let b = a + 1; b < visibleRegions.length; b++) {
        const ar = visibleRegions[a].getBoundingClientRect(), br = visibleRegions[b].getBoundingClientRect();
        const iw = Math.max(0, Math.min(ar.right, br.right) - Math.max(ar.left, br.left));
        const ih = Math.max(0, Math.min(ar.bottom, br.bottom) - Math.max(ar.top, br.top));
        const area = iw * ih, floor = Math.min(ar.width * ar.height, br.width * br.height);
        if (floor > 0 && area / floor > .03) rec.overlaps.push([a, b, +(area / floor).toFixed(3)]);
      }

      const tb = c.querySelector('table');
      if (tb) {
        rec.cols = (tb.querySelector('tr') || {children: []}).children.length;
        rec.rows = tb.querySelectorAll('tbody tr').length;
      }
    }

    // Body copy and compact data labels have separate policy floors.
    let minBodyFont = 1e9, minBodyDetail = null, minDataFont = 1e9;
    let minContrast = 1e9, minTextDetail = null;
    s.querySelectorAll('.sd-content *').forEach(el => {
      if (el.closest('svg')) return;
      if (el.children.length) return;
      if (!(el.textContent || '').trim()) return;
      const cs = getComputedStyle(el), f = parseFloat(cs.fontSize);
      const dataLabel = !!el.closest('table,.sd-kpi,figure') || el.matches('.num,th,td') || /mono|menlo/i.test(cs.fontFamily);
      if (f && dataLabel && f < minDataFont) minDataFont = f;
      if (f && !dataLabel && f < minBodyFont) {
        minBodyFont = f;
        minBodyDetail = el.tagName.toLowerCase() + ':' + (el.className || '') + ':' + (el.textContent || '').trim().slice(0, 40) + ':' + cs.fontFamily;
      }
      const bg = background(el), fg = painted(cs.color, bg, parseFloat(cs.opacity || '1'));
      if (fg && bg) {
        const ratio = contrast(fg, bg);
        if (ratio < minContrast) { minContrast = ratio; minTextDetail = el.tagName.toLowerCase() + ':' + (el.textContent || '').trim().slice(0, 40); }
      }
    });

    let minMarkContrast = 1e9, minMarkDetail = null, greyscaleIssues = 0;
    s.querySelectorAll('.sd-content svg').forEach(svg => {
      const shapes = [...svg.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon')];
      function textBackground(text) {
        const r = text.getBoundingClientRect(), x = (r.left + r.right) / 2, y = (r.top + r.bottom) / 2;
        let color = null;
        for (const mark of shapes) {
          if (!(mark.compareDocumentPosition(text) & Node.DOCUMENT_POSITION_FOLLOWING)) continue;
          const mr = mark.getBoundingClientRect(), cs = getComputedStyle(mark);
          const alpha = parseFloat(cs.opacity || '1') * parseFloat(cs.fillOpacity || '1');
          const fill = rgb(cs.fill);
          if (fill && alpha * colorAlpha(cs.fill) >= .1 && x >= mr.left && x <= mr.right && y >= mr.top && y <= mr.bottom) color = painted(cs.fill, background(svg), alpha);
        }
        return color || background(svg);
      }
      svg.querySelectorAll('text').forEach(el => {
        if (!(el.textContent || '').trim()) return;
        const cs = getComputedStyle(el), ctm = el.getScreenCTM();
        const scale = ctm ? Math.hypot(ctm.a, ctm.b) : 1;
        const f = parseFloat(cs.fontSize) * scale;
        if (f && f < minDataFont) minDataFont = f;
        const bg = textBackground(el), fg = painted(cs.fill || cs.color, bg, parseFloat(cs.opacity || '1') * parseFloat(cs.fillOpacity || '1'));
        if (fg && bg) {
          let ratio = contrast(fg, bg);
          if (parseFloat(cs.strokeWidth || '0') >= 2) {
            const stroke = painted(cs.stroke, bg, parseFloat(cs.opacity || '1') * parseFloat(cs.strokeOpacity || '1'));
            if (stroke) ratio = Math.max(ratio, contrast(stroke, bg));
          }
          if (ratio < minContrast) { minContrast = ratio; minTextDetail = 'svg-text:' + (el.textContent || '').trim().slice(0, 40) + ':bg=' + bg.join(','); }
        }
      });
      const colors = new Set(), forms = new Set();
      shapes.forEach(mark => {
        const cs = getComputedStyle(mark), bg = background(svg);
        const box = mark.getBBox(), view = svg.viewBox && svg.viewBox.baseVal;
        const backdrop = mark.tagName.toLowerCase() === 'rect' && view && view.width && view.height && box.width * box.height > view.width * view.height * .65;
        for (const [prop, alphaProp] of [['fill','fillOpacity'],['stroke','strokeOpacity']]) {
          if (prop === 'fill' && backdrop) continue;
          if (prop === 'stroke' && parseFloat(cs.strokeWidth || '0') <= 4) continue;
          const color = rgb(cs[prop]), alpha = parseFloat(cs.opacity || '1') * parseFloat(cs[alphaProp] || '1') * colorAlpha(cs[prop]);
          if (!color || alpha < .5 || !bg) continue;
          const ratio = contrast(painted(cs[prop], bg, parseFloat(cs.opacity || '1') * parseFloat(cs[alphaProp] || '1')), bg);
          if (ratio < minMarkContrast) {
            minMarkContrast = ratio;
            minMarkDetail = mark.tagName.toLowerCase() + ':' + prop + ':' + color.join(',');
          }
          colors.add(color.join(','));
          forms.add(mark.tagName + ':' + (cs.strokeDasharray || 'solid'));
        }
      });
      if (colors.size > 1 && !svg.querySelector('text') && forms.size < 2) greyscaleIssues++;
    });
    rec.min_body_font = minBodyFont === 1e9 ? null : +minBodyFont.toFixed(1);
    rec.min_body_detail = minBodyDetail;
    rec.min_data_font = minDataFont === 1e9 ? null : +minDataFont.toFixed(1);
    rec.min_text_contrast = minContrast === 1e9 ? null : +minContrast.toFixed(2);
    rec.min_text_detail = minTextDetail;
    rec.min_mark_contrast = minMarkContrast === 1e9 ? null : +minMarkContrast.toFixed(2);
    rec.min_mark_detail = minMarkDetail;
    rec.greyscale_issues = greyscaleIssues;

    let escapes = 0;
    s.querySelectorAll('.sd-content *').forEach(el => {
      if (el.closest('svg')) return;
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) return;
      if (r.bottom > sr.bottom + 1 || r.right > sr.right + 1 || r.left < sr.left - 1) escapes++;
    });
    rec.escapes = escapes;

    const h2 = (s.querySelector('.sd-h2') || {textContent: ''}).textContent.trim();
    const first = (s.querySelector('.sd-content .sd-block') || {textContent: ''}).textContent.trim();
    rec.title_echo = !!(h2.length > 5 && first.startsWith(h2.slice(0, Math.min(12, h2.length))));
    rec.ellipsis = [...s.querySelectorAll('.sd-content *')].some(el => {
      const cs = getComputedStyle(el);
      return cs.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth + 1;
    });

    const txt = (s.querySelector('.sd-content') || {textContent: ''}).textContent;
    rec.md_leak = (txt.match(/\*\*|^\s*#{1,6}\s|`[^`]+`|\[[^\]]*\]\(/gm) || []).length;

    const raw = s.outerHTML.replace(/<script[\s\S]*?<\/script>/g, '');
    rec.hex_literals = (raw.match(/#[0-9a-fA-F]{3,8}\b/g) || []).length;
    rec.px_literals = (raw.match(/:\s*-?\d+px/g) || []).length;
    out.push(rec);
  });
  return out;
}
"""

HARD, WARN = "hard", "warn"


def judge(rec, ct, ids):
    f, a = [], []
    pt = ct["page_types"].get(rec.get("type"))
    band = (pt or {}).get("fill_ratio") or ct["fill_ratio"]
    lo = band["min"]; hi = band["max"]; tgt = ct["fill_ratio"]["target"]
    ratio = rec.get("fill_ratio")

    def add(code, sev, msg, action=None):
        f.append({"code": code, "sev": sev, "msg": msg})
        if action: a.append(action)

    if rec.get("missing"):
        add("BLOCK_MISSING", HARD, f"{rec['missing']} block(s) failed to bind",
            {"op": "fix_block", "page": rec["id"], "why": "block did not validate"})
    if not pt:
        add("TYPE_UNKNOWN", HARD, f"type {rec.get('type')!r} not in contract",
            {"op": "set_type", "page": rec["id"]})
    if ratio is None:
        return f, a

    if rec.get("escapes"):
        add("V.03", HARD, f"{rec['escapes']} element(s) outside the slide frame",
            {"op": "split_page", "page": rec["id"]})
    if rec.get("block_overflow"):
        thin = [b["kind"] for b in rec.get("blocks", []) if b.get("over", 0) > 0.01]
        add("BLOCK_OVERFULL", HARD, f"ink escapes {rec['block_overflow']} block(s): {','.join(thin)}",
            {"op": "split_page", "page": rec["id"], "hint": "move trailing blocks to an overflow page"})
    if rec.get("overlaps"):
        add("OVERLAP", HARD, f"{len(rec['overlaps'])} sibling region overlap(s)",
            {"op": "solve_layout", "page": rec["id"], "hint": "re-solve the 12x8 regions; do not layer content blocks"})
    if ratio > hi:
        add("OVERFULL", WARN, f"page ink reaches {ratio} of the band", None)
    elif ratio < lo:
        sev = HARD if ratio < lo * 0.65 else WARN
        add("UNDERFULL", sev, f"page ink {ratio} < {lo} (target {tgt})",
            {"op": "densify", "page": rec["id"],
             "hint": "raise pack to air, merge with the neighbouring page, or promote a block to fig"})
    dens = rec.get("density")
    if dens is not None and dens < 0.45 and ratio >= lo:
        add("SPARSE_BLOCKS", WARN, f"mean block ink density {dens} — regions are mostly empty",
            {"op": "densify", "page": rec["id"], "hint": "fewer, larger regions or a tighter layout"})
    if rec.get("h_ratio", 0) > 1.005:
        add("HOVERFLOW", HARD, f"horizontal overflow {rec['h_ratio']}",
            {"op": "reduce_cols", "page": rec["id"]})
    if rec.get("cols") and rec["cols"] > ct["blocks"]["table"]["cols"]["max"]:
        add("WIDE_TABLE", HARD, f"{rec['cols']} columns > {ct['blocks']['table']['cols']['max']}",
            {"op": "appendix_bypass", "page": rec["id"],
             "hint": "keep a fig + TOP-N here; full table goes to assets/tables/"})
    if rec.get("rows") and rec["rows"] > ct["blocks"]["table"]["rows"]["max"]:
        add("LONG_TABLE", WARN, f"{rec['rows']} rows > {ct['blocks']['table']['rows']['max']}",
            {"op": "split_page", "page": rec["id"]})
    body_floor = ct.get("_body_floor_px", 18)
    data_floor = ct.get("_data_floor_px", 14.4)
    if rec.get("min_body_font") and rec["min_body_font"] < body_floor:
        add("V.03", HARD, f"body font {rec['min_body_font']}px below {body_floor:g}px floor",
            {"op": "densify", "page": rec["id"], "hint": "cut content; do not shrink type"})
    if rec.get("min_data_font") and rec["min_data_font"] < data_floor:
        add("V.03", HARD, f"data font {rec['min_data_font']}px below {data_floor:g}px floor",
            {"op": "densify", "page": rec["id"], "hint": "cut content; do not shrink type"})
    if rec.get("min_text_contrast") and rec["min_text_contrast"] < float((ct.get("contrast") or {}).get("text", 4.5)):
        add("V.01", HARD, f"text contrast {rec['min_text_contrast']}:1 below policy",
            {"op": "use_token", "page": rec["id"], "hint": "use a semantic text token with sufficient contrast"})
    if rec.get("min_mark_contrast") and rec["min_mark_contrast"] < float((ct.get("contrast") or {}).get("marks", 3)):
        add("V.01", HARD, f"mark contrast {rec['min_mark_contrast']}:1 below policy",
            {"op": "use_token", "page": rec["id"], "hint": "use a semantic mark token with sufficient contrast"})
    if rec.get("greyscale_issues"):
        add("V.02", HARD, f"{rec['greyscale_issues']} chart(s) rely on colour without labels or shape redundancy",
            {"op": "label_marks", "page": rec["id"]})
    if rec.get("title_echo"):
        add("TITLE_ECHO", WARN, "first block repeats the slide title",
            {"op": "drop_block", "page": rec["id"], "index": 0})
    if rec.get("ellipsis"):
        add("ELLIPSIS", HARD, "truncation marker on the canvas",
            {"op": "split_page", "page": rec["id"]})
    if rec.get("md_leak"):
        add("MD_LEAK", HARD, f"{rec['md_leak']} raw markdown marker(s) rendered as text",
            {"op": "clean_slot", "page": rec["id"],
             "hint": "slot values are plain text; strip **, `, # in the planner, not the renderer"})
    if rec.get("hex_literals"):
        add("HEX_LITERAL", HARD, f"{rec['hex_literals']} literal colour(s) in slide markup",
            {"op": "use_token", "page": rec["id"]})
    if rec.get("px_literals"):
        add("PX_LITERAL", WARN, f"{rec['px_literals']} literal px value(s)", None)
    if rec.get("overflow_of") and rec["overflow_of"] not in ids:
        add("ORPHAN_CONT", HARD, f"overflow_of={rec['overflow_of']} does not exist",
            {"op": "fix_link", "page": rec["id"]})
    return f, a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--design", required=True)
    ap.add_argument("--out", default="audit-layout.json")
    ap.add_argument("--calibrate", default=None,
                    help="deck-plan.json with predicted_h per page; writes calibration stats")
    a = ap.parse_args()

    ct = json.loads((Path(a.design) / "page-types.json").read_text(encoding="utf-8"))
    policy_path = Path(a.design) / str(ct.get("policy") or "policy-v2.json")
    policy = json.loads(policy_path.read_text(encoding="utf-8")) if policy_path.is_file() else {}
    ct["contrast"] = policy.get("contrast") or {}
    ct["_body_floor_px"] = float((policy.get("type_floor") or {}).get("body_u", 1.125)) * 16
    ct["_data_floor_px"] = float((policy.get("type_floor") or {}).get("data_u", .9)) * 16
    if isinstance(ct.get("page_templates"), list):
        ct["page_types"] = {name: {"known": True} for name in ct["page_templates"]}
    for name, band in (ct.get("page_type_fill") or {}).items():
        ct["page_types"].setdefault(name, {})["fill_ratio"] = band
    ct["_viewport_h"] = 900
    if sync_playwright is None:
        ap.error("Python Playwright is required: python3 -m pip install playwright")
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="chrome")
        except Exception:
            b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 900})
        pg.goto("file://" + str(Path(a.html).resolve()), wait_until="load", timeout=180_000)
        pg.wait_for_timeout(2500)          # webfont settle
        recs = pg.evaluate(MEASURE_JS)
        b.close()

    ids = {r["id"] for r in recs}
    pages, hard, warn = [], 0, 0
    for r in recs:
        fs, acts = judge(r, ct, ids)
        hard += sum(1 for x in fs if x["sev"] == HARD)
        warn += sum(1 for x in fs if x["sev"] == WARN)
        pages.append({**r, "findings": fs, "actions": acts})

    ratios = [p["fill_ratio"] for p in pages if p.get("fill_ratio")]
    def _band(p):
        b = (ct["page_types"].get(p.get("type")) or {}).get("fill_ratio") or ct["fill_ratio"]
        return b["min"], b["max"]
    in_band = sum(1 for p in pages if p.get("fill_ratio")
                  and _band(p)[0] <= p["fill_ratio"] <= _band(p)[1])
    bins = {f"{i/10:.1f}-{(i+1)/10:.1f}": 0 for i in range(0, 12)}
    for r in ratios:
        bins[f"{min(int(r*10),11)/10:.1f}-{(min(int(r*10),11)+1)/10:.1f}"] += 1

    summary = {
        "pages": len(pages), "hard": hard, "warn": warn,
        "fill_ratio_median": round(statistics.median(ratios), 3) if ratios else None,
        "fill_ratio_mean": round(statistics.fmean(ratios), 3) if ratios else None,
        "in_band": in_band,
        "in_band_pct": round(100 * in_band / len(ratios), 1) if ratios else None,
    }

    calib = None
    if a.calibrate:
        plan = json.loads(Path(a.calibrate).read_text(encoding="utf-8"))
        pred = {p["id"]: p.get("predicted_h") for p in plan["pages"] if p.get("predicted_h")}
        errs = [(pg["ink_h"] - pred[pg["id"]]) / pred[pg["id"]]
                for pg in pages
                if pg.get("id") in pred and pred[pg["id"]] and pg.get("ink_h")]
        if errs:
            calib = {"n": len(errs), "mean_err": round(statistics.fmean(errs), 4),
                     "abs_p90": round(sorted(abs(e) for e in errs)[int(.9 * len(errs)) - 1], 4),
                     "suggested_scale": round(1 + statistics.fmean(errs), 4)}

    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(
        {"summary": summary, "histogram": bins, "calibration": calib, "pages": pages},
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"gate_layout: {summary['pages']} pages · hard {hard} · warn {warn} · "
          f"median fill {summary['fill_ratio_median']} · in-band {summary['in_band_pct']}%")
    for p in pages:
        for fnd in p["findings"]:
            if fnd["sev"] == HARD:
                print(f"  HARD {p['id']:>8} {fnd['code']:<14} {fnd['msg']}")
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
