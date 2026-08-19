#!/usr/bin/env python3
"""
Inject curated SVG images into specific slides in the generated deck.
Matches slides by chrome-min left text (kicker) and inserts an <img>
block in the .canvas-card body, right after the canvas-card open tag.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / 'content' / 'zengcheng-taizikeng' / 'deck.html'

# (kicker_substring, image_filename, image_position)
# image_position: 'top-right' | 'full'
INJECTIONS = [
    # COVER
    ('增城太子坑森林公园 · 沉香目的地项目', 'cover-太子坑远眺.svg', 'full'),
    # SECTION DIVIDERS (10, 02, 03, ...)
    ('01 · 行政综述', 'icon-section-break.svg', 'corner'),
    ('02 · 前言', 'icon-section-break.svg', 'corner'),
    ('03 · 宏观环境分析', 'icon-section-break.svg', 'corner'),
    ('04 · 地块特征分析', 'icon-section-break.svg', 'corner'),
    ('05 · 供需分析与预测', 'icon-section-break.svg', 'corner'),
    ('06 · 定位建议', 'icon-section-break.svg', 'corner'),
    ('07 · 功能性设施建议', 'icon-section-break.svg', 'corner'),
    ('08 · 功能分区与动线规划', 'icon-section-break.svg', 'corner'),
    ('09 · 运营现金流测算', 'icon-section-break.svg', 'corner'),
    ('10 · 投资回报分析', 'icon-section-break.svg', 'corner'),
    ('11 · 品牌与运营模式建议', 'icon-section-break.svg', 'corner'),
    ('12 · 落地筹建可执行建议', 'icon-section-break.svg', 'corner'),
    ('A · 附件', 'icon-section-break.svg', 'corner'),
    # SPECIFIC SLIDES
    ('1.1 项目概况与核心结论', 'map-tai-zi-keng.svg', 'full'),
    ('1.1 项目概况与核心结论', 'hero-关键数字.svg', 'top'),
    ('1.1 项目概况与核心结论', 'tree-沉香.svg', 'corner'),
    ('1.1 项目概况与核心结论', 'logo-顺科智连.svg', 'corner'),
    ('1.4 投资建议与关键考量', 'principles-4.svg', 'full'),
    ('2.1 研究背景、目的与范围', 'quote-创始人.svg', 'full'),
    ('3.1 国家及广东省宏观经济与 GDP', 'forest-步道.svg', 'corner'),
    ('3.4 空间规划与产业规划', 'framework-3层架构.svg', 'full'),
    ('4.1 地理区位与区域能级', 'map-tai-zi-keng.svg', 'full'),
    ('4.2 地块现状实拍与现状条件', 'site-太子坑总平面图.svg', 'full'),
    ('5.1 住宿与接待市场历史数据', 'donut-收入结构.svg', 'full'),
    ('5.3 市场周期性与季节性', 'forest-步道.svg', 'corner'),
    ('5.7 客源驱动力需求分析', 'hero-3takeaways.svg', 'full'),
    ('5.10 供需平衡与渗透率测算', 'donut-收入结构.svg', 'corner'),
    ('6.1 定位推导逻辑', 'pyramid-3层.svg', 'full'),
    ('6.2 三大核心定位的需求支撑论证', 'framework-3层架构.svg', 'full'),
    ('6.3 目标客群与产品组合', 'framework-3层架构.svg', 'corner'),
    ('7.1 设施建议推导逻辑', 'grid-6功能.svg', 'full'),
    ('7.2 对标项目设施启示', 'icon-step-01.svg', 'corner'),
    ('7.3 本项目功能大区设施建议', 'grid-6功能.svg', 'full'),
    ('8.1 按三大定位的功能分区方案', 'forest-步道.svg', 'full'),
    ('8.2 宾客动线', 'forest-步道.svg', 'corner'),
    ('8.8 面积配比与建筑容量建议', 'grid-6功能.svg', 'corner'),
    ('9.6 各业态收入预测', 'donut-收入结构.svg', 'full'),
    ('9.4 ADR 与项目单价', 'product-沉香制品.svg', 'corner'),
    ('10.1 开发建造成本', 'hero-关键数字.svg', 'corner'),
    ('10.5 自用占比 / 对外开放度情景与敏感性', 'matrix-风险评估.svg', 'full'),
    ('11.3 品牌建议结论', 'logo-顺科智连.svg', 'full'),
    ('11.5 自营 / 委托管理', 'framework-3层架构.svg', 'corner'),
    ('12.1 分期开发与开业节奏', 'process-分期建设.svg', 'full'),
    ('12.3 关键筹建里程碑与时间表', 'process-分期建设.svg', 'corner'),
    ('12.4 设计任务书纲要', 'icon-section-break.svg', 'corner'),
    ('A1 设施建议详细总表', 'grid-6功能.svg', 'full'),
    ('A4 功能分区与动线示意文字版', 'forest-步道.svg', 'full'),
    ('4.10 SWOT 分析', 'matrix-风险评估.svg', 'full'),
]


def build_image_html(image_filename: str, image_position: str) -> str:
    """Build the <img> block to inject."""
    if image_position == 'corner':
        return (
            f'<img src="../../content/zengcheng-taizikeng/images/{image_filename}" '
            f'style="position:absolute;top:30px;right:32px;width:auto;height:18vh;max-height:130px;'
            f'max-width:28%;object-fit:contain;z-index:3;opacity:.92;'
            f'filter:drop-shadow(0 2px 8px rgba(10,22,38,.12))" '
            f'alt=""/>'
        )
    if image_position == 'top':
        return (
            f'<img src="../../content/zengcheng-taizikeng/images/{image_filename}" '
            f'style="position:absolute;top:14vh;right:32px;width:auto;height:32vh;max-height:260px;'
            f'max-width:48%;object-fit:contain;z-index:3;opacity:.95;'
            f'filter:drop-shadow(0 2px 12px rgba(10,22,38,.14))" '
            f'alt=""/>'
        )
    # 'full' - large image fills upper portion
    return (
        f'<div style="position:absolute;top:0;right:0;width:48%;height:62%;z-index:0;'
        f'background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(245,243,244,.96));'
        f'display:flex;align-items:center;justify-content:center;'
        f'padding:3vh 2vw;border-bottom-left-radius:6px;'
        f'box-sizing:border-box">'
        f'<img src="../../content/zengcheng-taizikeng/images/{image_filename}" '
        f'style="width:100%;max-height:100%;object-fit:contain;'
        f'filter:drop-shadow(0 4px 16px rgba(10,22,38,.10))" '
        f'alt=""/></div>'
    )


def inject_into_html(html: str) -> tuple[str, int, int]:
    """Walk every <section>...</section> in the deck and inject images by kicker match.
    Returns (new_html, total_injected, total_skipped)."""
    slide_re = re.compile(r'(<section\b[^>]*>)([\s\S]*?)(</section>)')

    out = []
    last = 0
    injected = 0
    skipped = 0

    for m in slide_re.finditer(html):
        out.append(html[last:m.start()])
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)

        # Skip slides that already have an injected image
        if 'zengcheng-taizikeng/images/' in body:
            out.append(open_tag + body + close_tag)
            last = m.end()
            skipped += 1
            continue

        chrome_m = re.search(r'<div class="l">([^<]+)</div>', body)
        if not chrome_m:
            out.append(open_tag + body + close_tag)
            last = m.end()
            continue
        kicker = chrome_m.group(1).strip()

        # Find all matching injections for this kicker, in order
        matches_for_kicker = [m for m in INJECTIONS if m[0] in kicker]
        if not matches_for_kicker:
            out.append(open_tag + body + close_tag)
            last = m.end()
            continue

        # Cap at 2 images per slide
        matches_for_kicker = matches_for_kicker[:2]

        # Find canvas-card open tag once
        cc_m = re.search(r'(<div class="canvas-card"[^>]*>)', body)
        if not cc_m:
            out.append(open_tag + body + close_tag)
            last = m.end()
            continue

        new_body = body
        for (kicker_kw, image_filename, position) in matches_for_kicker:
            img_html = build_image_html(image_filename, position)
            new_body = new_body[:cc_m.end()] + img_html + new_body[cc_m.end():]
            injected += 1
            # Subsequent insertions need the offset to remain correct
            cc_m_pos = cc_m.end() + len(img_html)
        out.append(open_tag + new_body + close_tag)
        last = m.end()

    out.append(html[last:])
    return ''.join(out), injected, skipped


def main():
    html = DECK.read_text(encoding='utf-8')
    print(f'Initial: {html.count("canvas-card")} canvas-cards')

    final, injected, skipped = inject_into_html(html)
    DECK.write_text(final, encoding='utf-8')
    print(f'Injected: {injected} image blocks')
    print(f'Skipped (already had image): {skipped}')
    print(f'File size: {DECK.stat().st_size:,} bytes')
    print(f'Image refs in deck: {final.count("zengcheng-taizikeng/images/")}')


if __name__ == '__main__':
    main()
