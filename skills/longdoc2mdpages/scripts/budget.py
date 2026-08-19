#!/usr/bin/env python3
"""Typographic height budget for a page, in canvas px.

Replaces `chars <= 1600`, which predicts nothing about layout. Heights come
from the same type stair the CSS uses, plus real CJK/Latin advance widths.

CALIBRATION is updated from `gate_layout.py --calibrate` output. That closes
the loop: pagination predictions improve every render instead of staying wrong.
"""
from __future__ import annotations
import json, sys, unicodedata

CANVAS_W, CANVAS_H = 2880, 1620
MARGIN = CANVAS_W * 0.032
BAND_H = CANVAS_H * (0.944 - 0.148)          # 1290 px of usable content height
BAND_W = CANVAS_W - 2 * MARGIN

CALIBRATION = 1.1211                           # <- set from suggested_scale

PACK = {"air":   {"em": 0.028,  "quote": 0.048, "h3": 0.026, "small": 0.020},
        "mid":   {"em": 0.0245, "quote": 0.036, "h3": 0.024, "small": 0.0175},
        "tight": {"em": 0.020,  "quote": 0.030, "h3": 0.020, "small": 0.015}}


def advance(ch: str) -> float:
    """Advance width as a multiple of font-size."""
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 1.00                            # CJK is square
    return 0.52                                # Latin/digit average


def text_lines(s: str, size: float, width: float) -> int:
    if not s:
        return 0
    return max(1, int(sum(advance(c) for c in s) * size / width + 0.999))


def block_height(b: dict, pack: str, width: float) -> float:
    p = PACK[pack]
    em, quote, h3, small = (CANVAS_H * p[k] for k in ("em", "quote", "h3", "small"))
    k = b.get("kind")
    if k == "claim":
        return text_lines(b.get("text", ""), quote, width) * quote * 1.34
    if k == "lede":
        return text_lines(b.get("text", ""), em, width) * em * 1.62
    if k == "quote":
        return text_lines(b.get("text", ""), quote, width) * quote * 1.44 + CANVAS_H * 0.088
    if k == "bullets":
        items = b.get("items") or []
        gap = CANVAS_H * 0.018 * max(0, len(items) - 1)
        return sum(text_lines(i if isinstance(i, str) else i.get("text", ""), em, width * 0.96)
                   * em * 1.5 for i in items) + gap
    if k == "kpi-card":
        return CANVAS_H * 0.060 + em * 1.6 + small * 2.2
    if k == "table":
        cols = len(b.get("columns") or []) or 1
        colw = width / cols
        rh = 0.0
        for r in b.get("rows") or []:
            worst = max((text_lines(str(c), small, colw * 0.94) for c in r), default=1)
            rh += worst * small * 1.5 + CANVAS_H * 0.024
        if b.get("sum"):
            rh += small * 1.5 + CANVAS_H * 0.024
        return small * 1.4 + CANVAS_H * 0.024 + rh
    if k in ("fig", "embed"):
        return BAND_H * 0.74
    if k in ("callout", "step", "profile"):
        return (text_lines(b.get("text", ""), em, width * 0.92) * em * 1.5
                + h3 * 1.5 + CANVAS_H * 0.052)
    if k == "media":
        num, den = (b.get("ratio") or "16:9").split(":")
        return width / (float(num) / float(den)) + small * 1.6
    if k == "toc-item":
        return h3 * 1.35 + CANVAS_H * 0.020
    return em * 1.6


REGION_W = {"full": 1.0, "table-full": 1.0, "hero-band": 1.0, "fig-strip": 1.0,
            "split-2": 0.486, "split-2-62": 0.606, "split-3": 0.317,
            "grid-2x2": 0.486, "grid-3x2": 0.317, "fig-rail": 0.666}
ROWS = {"full": 1, "table-full": 1, "hero-band": 2, "fig-strip": 2, "split-2": 1,
        "split-2-62": 1, "split-3": 1, "grid-2x2": 2, "grid-3x2": 2, "fig-rail": 1}


def predict(page: dict, layout: str, pack: str = "mid") -> float:
    """Predicted ink height in canvas px. Compare against BAND_H."""
    w = BAND_W * REGION_W.get(layout, 1.0)
    blocks = (page.get("content") or {}).get("blocks") or page.get("blocks") or []
    hs = [block_height(b, pack, w) for b in blocks]
    if not hs:
        return 0.0
    if layout in ("grid-2x2", "grid-3x2"):
        per = 2 if layout == "grid-2x2" else 3
        total = sum(max(hs[i:i + per], default=0) for i in range(0, len(hs), per))
    elif ROWS.get(layout, 1) == 1 and layout not in ("full", "table-full"):
        total = max(hs)                        # side by side
    else:
        total = sum(hs)
    return total * CALIBRATION


def fits(page, layout, pack="mid"):
    h = predict(page, layout, pack)
    return h, h / BAND_H


if __name__ == "__main__":
    plan = json.loads(open(sys.argv[1], encoding="utf-8").read())
    for p in plan["pages"]:
        h, r = fits(p, p.get("layout") or "full", p.get("pack") or "mid")
        p["predicted_h"] = round(h, 1)
        p["predicted_fill"] = round(r, 3)
    open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(plan, ensure_ascii=False, indent=1))
    over = sum(1 for p in plan["pages"] if p["predicted_fill"] > 0.95)
    under = sum(1 for p in plan["pages"] if p["predicted_fill"] < 0.62)
    print(f"budget: {len(plan['pages'])} pages · predicted over {over} · under {under} "
          f"· band {BAND_H:.0f}px · calibration {CALIBRATION}")
