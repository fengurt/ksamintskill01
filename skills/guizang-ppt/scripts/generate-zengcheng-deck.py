#!/usr/bin/env python3
"""
Generate a 200+ page Style C deck from source.md for the
增城太子坑森林公园沉香目的地项目 可行性研究报告.

v2: layout-aware. Avoids font overflow by enforcing:
  - max 4 bullets per paragraph slide, each ≤78 chars
  - title font shrinks dynamically with content
  - tables scroll within fixed height
  - infographics (bar / donut / timeline / process / compare) auto-detected
    from numeric content
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'content' / 'zengcheng-taizikeng' / 'source.md'
TEMPLATE = ROOT / 'assets' / 'template-tableai.html'
OUT = ROOT / 'content' / 'zengcheng-taizikeng' / 'deck.html'

# Read template
html = TEMPLATE.read_text(encoding='utf-8')

# Find SLIDES 插入区 marker
marker_re = re.compile(
    r'(<!--\s*={3,}\s*\n\s*SLIDES 插入区.*?={3,}\s*-->\s*\n)(.*?)(\n</div>\s*\n\s*<div id="nav">)',
    re.DOTALL,
)
m = marker_re.search(html)
if not m:
    raise SystemExit('Could not find SLIDES 插入区 marker in template-tableai.html')

# ---- Constants ----
MAX_BULLET_CHARS = 78
MAX_BULLETS_PER_SLIDE = 4
CHARS_PER_SLIDE = 200
SECTION_LABELS = {
    '00': '封面', '01': '行政综述', '02': '前言', '03': '宏观',
    '04': '地块', '05': '供需', '06': '定位', '07': '设施',
    '08': '动线', '09': '现金流', '10': '回报', '11': '品牌',
    '12': '落地', 'A': '附件',
}

# ---- Helpers ----
def esc(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def trim_bullet(s: str, max_chars: int = MAX_BULLET_CHARS) -> str:
    """Trim a long bullet to max_chars at a word boundary, add …"""
    s = s.strip()
    if len(s) <= max_chars:
        return s
    # Try to cut at the last space before max_chars
    cut = s[:max_chars]
    sp = cut.rfind(' ')
    if sp > max_chars * 0.5:
        cut = cut[:sp]
    return cut.rstrip('，,;；。、 ') + '…'

def parse_table_rows(md_table: str):
    lines = [l for l in md_table.strip().split('\n') if l.strip()]
    if len(lines) < 2:
        return [], []
    headers = [c.strip() for c in lines[0].strip('|').split('|')]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) == len(headers):
            rows.append([trim_bullet(c, 100) for c in cells])
    return headers, rows

def chunk_text(content: str, target_chars: int = CHARS_PER_SLIDE) -> list[str]:
    """Split content into chunks of ~target_chars each, respecting paragraphs."""
    paras = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]
    out, buf = [], ''
    for p in paras:
        if len(buf) + len(p) > target_chars and buf.strip():
            out.append(buf.strip())
            buf = p + '\n\n'
        else:
            buf += p + '\n\n'
    if buf.strip():
        out.append(buf.strip())
    return out

def clean_title(raw: str, kicker: str = '', max_chars: int = 56) -> str:
    """Clean a candidate slide title. Strips markdown noise, list markers, blockquotes, and chooses the most informative phrase.
    Returns: a clean, PPT-scene-appropriate title.
    """
    if not raw:
        return kicker or ''
    s = raw.strip()
    # Strip leading markdown noise
    s = re.sub(r'^#{1,6}\s*', '', s)           # heading markers
    s = re.sub(r'^\d+[.、)]\s*[\d.]*\s*', '', s)  # numbered list markers like "1.", "1)", "1、", "1.1"
    s = re.sub(r'^[-*+]\s+', '', s)             # bullet markers
    s = re.sub(r'^>\s*', '', s)                  # blockquote marker
    s = re.sub(r'^\*\*(.+?)\*\*$', r'\1', s)    # wrap-around bold only
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)      # remove inline bold markers
    s = s.strip().rstrip('，,;；。、:：')
    # Truncate
    if len(s) > max_chars:
        cut = s[:max_chars]
        sp = cut.rfind(' ')
        if sp > max_chars * 0.4:
            cut = cut[:sp]
        s = cut.rstrip('，,;；。、:：') + '…'
    return s or (kicker or '未命名')

def bullets_from(chunk: str, max_n: int = MAX_BULLETS_PER_SLIDE, max_chars: int = MAX_BULLET_CHARS) -> list[str]:
    """Pull bullets from a chunk, capped at max_n and trimmed."""
    out = []
    lines = [l for l in chunk.split('\n') if l.strip()]
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith('- ') or s.startswith('* '):
            out.append(trim_bullet(s[2:].lstrip(), max_chars))
        elif re.match(r'^\d+\.\s', s):
            out.append(trim_bullet(re.sub(r'^\d+\.\s+', '', s), max_chars))
        else:
            out.append(trim_bullet(s, max_chars))
        if len(out) >= max_n:
            break
    if not out:
        out = [trim_bullet(chunk, max_chars)]
    return out

def detect_infographic_kind(chunk: str) -> str | None:
    """Heuristic: detect whether a chunk is best shown as a chart."""
    if not chunk:
        return None
    text = chunk
    # Bar chart: percent values like 11.27%, 138%, 90-100
    pct = len(re.findall(r'\d+(?:\.\d+)?\s*%', text))
    if pct >= 2:
        return 'hbar'
    # Year/range timeline: many 4-digit year mentions
    years = len(re.findall(r'\b20\d{2}\b', text))
    if years >= 3:
        return 'timeline'
    # Numbered process steps
    n_list = len(re.findall(r'^\s*\d+\.\s', text, re.MULTILINE))
    if n_list >= 3:
        return 'process'
    # Compare pairs
    if re.search(r'旧.*?新|before.*?after|vs\.?|对比', text, re.IGNORECASE):
        return 'compare'
    return None

def extract_hbar_data(chunk: str, max_n: int = 6) -> list[tuple[str, float]]:
    """Extract label + percent from a chunk like 'Foo: 11.27%'."""
    pairs = []
    # Pattern: "label ... number%" — try multiple regexes
    pat = re.compile(r'([一-鿿\w][一-鿿\w\s、/·\-\(\)]{0,20}?)\s*[:：]\s*(\d+(?:\.\d+)?)\s*%')
    for m in pat.finditer(chunk):
        label = m.group(1).strip().rstrip('，,、 ')
        if len(label) > 24 or len(label) < 2:
            continue
        try:
            v = float(m.group(2))
            if 0 < v < 200:
                pairs.append((label, v))
        except ValueError:
            pass
    # Dedupe by label, keep first
    seen = set()
    out = []
    for l, v in pairs:
        if l not in seen:
            out.append((l, v))
            seen.add(l)
        if len(out) >= max_n:
            break
    return out

def extract_year_data(chunk: str, max_n: int = 6) -> list[tuple[str, float]]:
    """Extract year + adjacent number for timeline chart."""
    out = []
    pat = re.compile(r'\b(20\d{2})\b[^0-9\n]{0,40}?(\d+(?:\.\d+)?)\s*%?')
    seen = set()
    for m in pat.finditer(chunk):
        yr = m.group(1)
        if yr in seen:
            continue
        try:
            v = float(m.group(2))
            if 0 < v < 200:
                out.append((yr, v))
                seen.add(yr)
        except ValueError:
            pass
        if len(out) >= max_n:
            break
    return out

def extract_process_steps(chunk: str, max_n: int = 6) -> list[str]:
    """Extract numbered list as process steps."""
    out = []
    for line in chunk.split('\n'):
        m = re.match(r'^\s*(\d+)\.\s+(.+)', line)
        if m:
            out.append(trim_bullet(m.group(2), 60))
        if len(out) >= max_n:
            break
    return out

# ---- Slide templates ----

def slide_cover() -> str:
    return '''<!-- ============ Cover ============ -->
<section class="slide dark" data-layout="TABLEAI-COVER-ASCII" data-animate="hero">
  <div class="canvas-card">
    <canvas class="ascii-bg" aria-hidden="true"></canvas>
    <div class="chrome-min">
      <div class="l">增城太子坑森林公园 · 沉香目的地项目</div>
      <div class="r">SS · 26.10.07 · 00 / NN</div>
    </div>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:2.6vh">
      <div data-anim="kicker" class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em">第一阶段可行性研究 · 文字版初稿</div>
      <h1 data-anim="title" style="align-self:center;font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(7.6vw,12vh);line-height:.94;letter-spacing:-.025em;color:#fff">沉香森林<br/><span style="font-style:italic;font-weight:500;color:var(--accent-bright)">康养目的地</span><br/>可行性研究报告</h1>
      <div data-anim="bottom" style="display:grid;grid-template-rows:auto auto;gap:1.6vh;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh">
        <div data-anim="lead" class="lead" style="max-width:60ch;color:rgba(255,255,255,.86);font-weight:400">顺科智连技术股份有限公司 · 广东省广州市增城区太子坑森林公园 / 太子片区附近</div>
        <div style="display:flex;justify-content:space-between;align-items:end">
          <div class="t-meta" style="color:rgba(255,255,255,.6)">2026.10 · 300+ 页 deck</div>
          <div class="t-meta" style="color:rgba(255,255,255,.6)">→ swipe / arrow keys</div>
        </div>
      </div>
    </div>
  </div>
</section>
'''

def slide_toc() -> str:
    items = [
        ('00', 'cover', '封面'),
        ('01', 'sec-01', '行政综述'),
        ('02', 'sec-02', '前言与研究说明'),
        ('03', 'sec-03', '宏观环境分析'),
        ('04', 'sec-04', '地块特征分析'),
        ('05', 'sec-05', '供需分析与预测'),
        ('06', 'sec-06', '定位建议'),
        ('07', 'sec-07', '功能性设施建议'),
        ('08', 'sec-08', '功能分区与动线规划'),
        ('09', 'sec-09', '运营现金流测算'),
        ('10', 'sec-10', '投资回报分析'),
        ('11', 'sec-11', '品牌与运营模式建议'),
        ('12', 'sec-12', '落地筹建可执行建议'),
        ('A', 'sec-a', '附件'),
    ]
    rows = '\n'.join(
        f'<li style="display:grid;grid-template-columns:5em 1fr auto;gap:1.6vw;padding:1.4vh 0;border-top:1px solid var(--border-subtle);align-items:baseline">'
        f'<a href="#{anchor}" style="text-decoration:none;color:var(--accent);font-family:var(--mono);font-weight:600;font-size:max(12px,.85vw);letter-spacing:.04em;cursor:pointer">{n}</a>'
        f'<a href="#{anchor}" style="text-decoration:none;color:var(--ink);font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(14px,1.3vw);letter-spacing:-.01em;cursor:pointer">{esc(t)}</a>'
        f'<span class="t-meta" style="color:var(--text-helper)">→</span>'
        f'</li>'
        for n, anchor, t in items
    )
    return f'''<!-- ============ TOC ============ -->
<section class="slide light" data-layout="TABLEAI-TOC" data-animate="grid-reveal">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">目录 · Table of Contents</div>
      <div class="r">300+ 页 · 13 节</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh">
        <div class="t-meta">CONTENTS · 目录</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(4.6vw,8vh);line-height:1.04;letter-spacing:-.035em">沉香森林康养目的地</h2>
      </div>
      <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:0;overflow-y:auto">{rows}</ul>
    </div>
  </div>
</section>
'''

def slide_section_div(num: str, title: str) -> str:
    return f'''<!-- ============ Section divider: {title} ============ -->
<section id="sec-{num.lower()}" class="slide dark" data-layout="TABLEAI-SECTION-{num}" data-animate="matrix-statement">
  <div class="canvas-card">
    <canvas class="ascii-bg" aria-hidden="true"></canvas>
    <div class="chrome-min">
      <div class="l">{num} · {esc(title)}</div>
      <div class="r">SECTION</div>
    </div>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:2.6vh">
      <div data-anim="kicker" class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em">{num}</div>
      <h1 data-anim="title" style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(8vw,13vh);line-height:.94;letter-spacing:-.025em;color:#fff">{esc(title)}</h1>
      <div data-anim="bottom" style="display:grid;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh">
        <div class="t-meta" style="color:rgba(255,255,255,.6)">↓ 下页开始本节内容</div>
      </div>
    </div>
  </div>
</section>
'''

def slide_section_close() -> str:
    return '''<!-- ============ Section closer ============ -->
<section class="slide light" data-layout="TABLEAI-SECTION-END" data-animate="matrix-statement">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">Section End · 章节小结</div>
      <div class="r">END</div>
    </header>
    <span class="ring-mat" style="left:5vw;bottom:5vh;width:18vw;height:18vw;position:absolute;color:var(--text-helper)"></span>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;position:relative;z-index:1;max-width:78vw">
      <div class="t-meta" style="margin-bottom:2vh">END OF SECTION</div>
      <h1 class="h-statement" style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(5vw,9vh);line-height:.94;letter-spacing:-.04em">
        以上是本节核心要点。<br>下一节继续展开。
      </h1>
    </div>
    <span class="dot-mat lg" style="right:0;top:0;width:36vw;height:36vw;position:absolute;color:var(--accent);opacity:.5"></span>
    <div class="t-meta" style="color:var(--text-helper);margin-top:auto;text-align:right">→ 下一节 · 按 → 继续</div>
  </div>
</section>
'''

def slide_closing() -> str:
    return '''<!-- ============ Conclusion / Closing ============ -->
<section class="slide dark" data-layout="TABLEAI-CONCLUSION" data-animate="split-statement">
  <div class="canvas-card">
    <div class="split-half">
      <div class="half b-ink" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between;position:relative;overflow:hidden">
        <canvas class="ascii-bg" aria-hidden="true"></canvas>
        <div class="chrome-min" style="margin-bottom:0;position:relative;z-index:1">
          <div class="l">END</div>
          <div class="r">CLOSING</div>
        </div>
        <div data-anim="manifesto" style="display:flex;flex-direction:column;gap:2vh;position:relative;z-index:1">
          <div class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em;margin-bottom:1.6vh">CLOSING · CONCLUSION</div>
          <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-size:min(5.6vw,9.6vh);line-height:.94;letter-spacing:-.025em;font-weight:700;color:#fff">沉香为产业根,<br>森林为<span style="font-style:italic;font-weight:500;color:var(--accent-bright)">疗愈场</span>。<br>真实需求为底盘。</h2>
          <div style="font-family:var(--sans-tab),var(--sans-zh);font-size:max(13px,1vw);line-height:1.6;color:rgba(255,255,255,.82);font-weight:400;max-width:36ch;margin-top:1.4vh">建议先做小而强的首期产品,通过企业团建、员工体检、学院课程、高端接待和沉香产品形成复合现金流。</div>
        </div>
        <div data-anim="signature" style="display:flex;justify-content:space-between;align-items:end;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh;position:relative;z-index:1">
          <div class="t-meta" style="color:rgba(255,255,255,.62)">歸藏 · 顺科智连 · 2026.10</div>
          <div class="t-meta" style="color:rgba(255,255,255,.62)">→ END</div>
        </div>
      </div>
      <div class="half" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between">
        <div class="chrome-min">
          <div class="l">NEXT STEPS</div>
          <div class="r">04 ACTIONS</div>
        </div>
        <div data-anim="rules" style="display:flex;flex-direction:column;gap:0">
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2vh 0;border-top:1px solid var(--border-subtle)">
            <div style="font-family:var(--sans-tab);font-weight:700;font-size:min(3.6vw,6.4vh);line-height:.9;color:var(--text-primary)">01</div>
            <div>
              <h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(14px,1.2vw);line-height:1.2;letter-spacing:-.015em;color:var(--text-primary);margin-bottom:.4vh">地块合规资料</h3>
              <p style="font-family:var(--sans-tab),var(--sans-zh);font-size:max(10px,.78vw);line-height:1.55;color:var(--text-secondary);font-weight:400">红线、林地、生态红线、点状供地合规报告。</p>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2vh 0;border-top:1px solid var(--border-subtle)">
            <div style="font-family:var(--sans-tab);font-weight:700;font-size:min(3.6vw,6.4vh);line-height:.9;color:var(--text-primary)">02</div>
            <div>
              <h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(14px,1.2vw);line-height:1.2;letter-spacing:-.015em;color:var(--text-primary);margin-bottom:.4vh">业主年度需求数据</h3>
              <p style="font-family:var(--sans-tab),var(--sans-zh);font-size:max(10px,.78vw);line-height:1.55;color:var(--text-secondary);font-weight:400">员工人数、团建参与率、体检预算、培训频次、接待场次。</p>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2vh 0;border-top:1px solid var(--border-subtle)">
            <div style="font-family:var(--sans-tab);font-weight:700;font-size:min(3.6vw,6.4vh);line-height:.9;color:var(--text-primary)">03</div>
            <div>
              <h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(14px,1.2vw);line-height:1.2;letter-spacing:-.015em;color:var(--text-primary);margin-bottom:.4vh">建设指标与投资上限</h3>
              <p style="font-family:var(--sans-tab),var(--sans-zh);font-size:max(10px,.78vw);line-height:1.55;color:var(--text-secondary);font-weight:400">容积率、密度、高度、绿地率、停车配比、CAPEX 上限。</p>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:auto 1fr;gap:2vw;align-items:start;padding:2vh 0;border-top:1px solid var(--border-subtle);border-bottom:2px solid var(--accent)">
            <div style="font-family:var(--sans-tab);font-weight:700;font-size:min(3.6vw,6.4vh);line-height:.9;color:var(--accent)">04</div>
            <div>
              <h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(14px,1.2vw);line-height:1.2;letter-spacing:-.015em;color:var(--accent);margin-bottom:.4vh">医疗 + 运营合作方</h3>
              <p style="font-family:var(--sans-tab),var(--sans-zh);font-size:max(10px,.78vw);line-height:1.55;color:var(--text-secondary);font-weight:400">持证医疗机构、专业运营管理方意向书与初步合作框架。</p>
            </div>
          </div>
        </div>
        <div data-anim="foot" class="t-meta" style="color:var(--text-helper);text-align:right">→ 完 · END OF FEASIBILITY DRAFT</div>
      </div>
    </div>
  </div>
</section>
'''

# ---- Content slides ----

def slide_paragraph(num: int, kicker: str, title: str, bullets: list[str], color: str = 'light') -> str:
    bg = 'slide ' + color
    # Pick a decorative background pattern based on title hash
    patterns = ['dots', 'grid', 'stripes', 'wave']
    pat = patterns[num % 4]
    # Alternate bg color of first bullet for visual emphasis
    accent_color = 'var(--accent)' if (num % 6) < 3 else 'var(--ink)'
    # Detect blockquote / pull-quote patterns (bullets starting with > )
    rendered = []
    for idx_b, b in enumerate(bullets):
        s = b
        is_quote = s.startswith('> ')
        if is_quote:
            s = s[2:].strip()
            s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
            rendered.append(
                f'<li style="padding:1.2vh 0;border-top:1px solid var(--border-subtle)">'
                f'<blockquote style="margin:0;padding:1.4vh 1.2vw;border-left:3px solid var(--accent);background:var(--gold-mist);border-radius:2px;font-family:var(--sans-zh);font-weight:600;font-size:max(13px,.95vw);line-height:1.55;color:var(--text-primary)">{s}</blockquote>'
                f'</li>'
            )
        else:
            s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
            # First bullet gets accent color; rest get ink
            this_color = accent_color if idx_b == 0 else 'var(--ink)'
            # Add a small accent dot/number marker
            marker = f'<span style="display:inline-flex;align-items:center;justify-content:center;width:1.6vw;height:1.6vw;border-radius:50%;background:{this_color};color:var(--accent-on);font-family:var(--mono);font-size:max(9px,.65vw);font-weight:700;margin-right:.8em;flex:0 0 auto;vertical-align:middle">{idx_b+1}</span>'
            rendered.append(
                f'<li style="display:flex;gap:0;align-items:flex-start;padding:1.2vh 0;border-top:1px solid var(--border-subtle)">{marker}<span style="font-family:var(--sans-tab),var(--sans-zh);font-weight:{"600" if idx_b == 0 else "500"};font-size:max(13px,.95vw);line-height:1.55;color:{("var(--ink)" if idx_b == 0 else "var(--text-primary)")};flex:1">{s}</span></li>'
            )
    body_html = '\n'.join(rendered)
    return f'''<!-- ============ #{num:03d} Paragraph ============ -->
<section class="{bg}" data-layout="S19" data-animate="grid-reveal">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    <div style="position:absolute;inset:0;pointer-events:none;opacity:.35">{svg_pattern(pat, 1920, 1080, 'var(--ink)')}</div>
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;position:relative;z-index:1;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3.6vw,6.6vh);line-height:1.04;letter-spacing:-.035em">{esc(title)}</h2>
      </div>
      <ul data-anim="up" style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:0;overflow-y:auto">{body_html}</ul>
    </div>
  </div>
</section>
'''

def slide_intro(num: int, kicker: str, title: str, lead: str, supporting: list[str]) -> str:
    """H2 intro: lead + 3 supporting bullets, full-bleed light slide."""
    body_html = '\n'.join(
        f'<li style="font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(13px,.95vw);line-height:1.55;color:var(--text-secondary);padding:1vh 0;border-top:1px solid var(--border-subtle)">{esc(s)}</li>'
        for s in supporting
    )
    return f'''<!-- ============ #{num:03d} Intro ============ -->
<section class="slide light" data-layout="TABLEAI-INTRO" data-animate="statement">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:5vw;align-items:center">
      <div data-anim="up" style="display:flex;flex-direction:column;gap:2vh;align-self:start">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3.2vw,5.8vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
        <p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(15px,1.2vw);line-height:1.6;color:var(--text-primary);max-width:44ch;margin-top:1.5vh">{esc(lead)}</p>
      </div>
      <ul data-anim="up" style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:0">{body_html}</ul>
    </div>
  </div>
</section>
'''

def slide_hbar(num: int, kicker: str, title: str, data: list[tuple[str, float]], unit: str = '%', color: str = 'light') -> str:
    """Horizontal bar chart with values."""
    bg = 'slide ' + color
    if not data:
        return ''
    max_v = max(v for _, v in data) or 100
    rows = ''
    for i, (label, v) in enumerate(data, 1):
        pct = min(100, (v / max_v) * 100)
        is_top = i == 1
        color_bar = 'var(--accent)' if is_top else 'var(--ink)'
        rows += (
            f'<div style="display:grid;grid-template-columns:14em 1fr 6em;gap:1.2vw;align-items:center;padding:1.2vh 0;border-top:1px solid var(--border-subtle)">'
            f'<div class="t-meta" style="color:var(--text-helper)">·{i:02d} {esc(label)}</div>'
            f'<div style="height:1.6vh;background:var(--grey-1);border-radius:1px;position:relative;overflow:hidden">'
            f'<div style="position:absolute;left:0;top:0;bottom:0;width:{pct:.1f}%;background:{color_bar}"></div>'
            f'</div>'
            f'<div style="font-family:var(--sans-tab);font-weight:700;font-size:max(13px,1vw);line-height:1;color:{color_bar};text-align:right">{v}{unit}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Horizontal Bar Chart ============ -->
<section class="{bg}" data-layout="S07" data-animate="bar-grow">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3.2vw,5.8vh);line-height:1.05;letter-spacing:-.035em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:0;overflow-y:auto">{rows}</div>
    </div>
  </div>
</section>
'''

def slide_vbar(num: int, kicker: str, title: str, data: list[tuple[str, float]], unit: str = '%', color: str = 'light') -> str:
    """Vertical bar chart (KPI tower)."""
    bg = 'slide ' + color
    if not data:
        return ''
    max_v = max(v for _, v in data) or 100
    bars = ''
    for i, (label, v) in enumerate(data, 1):
        pct = min(100, (v / max_v) * 100)
        is_top = i == 1
        color_bar = 'var(--accent)' if is_top else 'var(--ink)'
        bars += (
            f'<div style="display:flex;flex-direction:column;gap:.6vh;align-items:flex-start;padding-top:1.4vh;border-top:2px solid currentColor">'
            f'<div class="t-meta" style="opacity:.6">{i:02d}</div>'
            f'<div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(13px,1vw);line-height:1.2">{esc(label)}</div>'
            f'<div style="width:100%;height:2vh;background:var(--grey-1);border-radius:1px;position:relative;overflow:hidden;margin-top:.6vh">'
            f'<div style="position:absolute;left:0;top:0;bottom:0;width:{pct:.1f}%;background:{color_bar}"></div>'
            f'</div>'
            f'<div style="font-family:var(--sans-tab);font-weight:700;font-size:max(15px,1.4vw);line-height:1;color:{color_bar}">{v}{unit}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Vertical Bar Chart ============ -->
<section class="{bg}" data-layout="S06" data-animate="measure-up">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3.2vw,5.8vh);line-height:1.05;letter-spacing:-.035em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat({len(data)},1fr);gap:1.6vw;align-items:start">{bars}</div>
    </div>
  </div>
</section>
'''

def slide_timeline(num: int, kicker: str, title: str, data: list[tuple[str, float]], color: str = 'light') -> str:
    """Horizontal timeline chart with year markers."""
    bg = 'slide ' + color
    if not data:
        return ''
    n = len(data)
    markers = ''
    for i, (yr, v) in enumerate(data):
        x_pct = (i / max(1, n - 1)) * 90 + 5
        is_top = v == max(d[1] for d in data)
        color_dot = 'var(--accent)' if is_top else 'var(--ink)'
        markers += (
            f'<div style="position:absolute;left:{x_pct:.1f}%;top:50%;transform:translate(-50%,-50%)">'
            f'<div style="width:1.4vh;height:1.4vh;background:{color_dot};border-radius:50%;border:2px solid var(--paper);box-shadow:0 0 0 1px var(--ink)"></div>'
            f'<div style="position:absolute;left:50%;bottom:1.6vh;transform:translateX(-50%);font-family:var(--mono);font-size:max(10px,.74vw);color:var(--text-helper);white-space:nowrap">{yr}</div>'
            f'<div style="position:absolute;left:50%;top:1.6vh;transform:translateX(-50%);font-family:var(--sans-tab);font-weight:700;font-size:max(13px,1vw);color:{color_dot};white-space:nowrap">{v}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Timeline ============ -->
<section class="{bg}" data-layout="S11" data-animate="timeline-walk">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3.2vw,5.8vh);line-height:1.05;letter-spacing:-.035em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="position:relative;height:60%;align-self:center;margin:0 4vw">
        <div style="position:absolute;left:0;right:0;top:50%;height:1px;background:var(--grey-2);transform:translateY(-50%)"></div>
        {markers}
      </div>
    </div>
  </div>
</section>
'''

def slide_process(num: int, kicker: str, title: str, steps: list[str], color: str = 'light') -> str:
    """Process flow with steps connected by arrows."""
    bg = 'slide ' + color
    n = len(steps)
    cells = ''
    for i, s in enumerate(steps, 1):
        arrow = (
            f'<div style="align-self:center;color:var(--accent);font-size:max(18px,2.4vw);font-weight:700;line-height:1;display:flex;align-items:center">{svg_icon("arrow", 32, "var(--accent)", 2)}</div>'
            if i < n else ''
        )
        icon = pick_icon(s[:20])
        cells += (
            f'<div style="display:flex;flex-direction:column;gap:.6vh;padding:1.4vh 1.2vw;background:var(--grey-1);border-radius:4px;border-left:3px solid var(--accent);min-width:0">'
            f'<div style="display:flex;align-items:center;gap:.6em">'
            f'<div style="width:2.6vh;height:2.6vh;color:var(--accent);display:flex;align-items:center">{svg_icon(icon, 22, "currentColor", 1.5)}</div>'
            f'<div class="t-meta" style="color:var(--accent);font-size:max(10px,.72vw)">STEP {i:02d}</div>'
            f'</div>'
            f'<div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(12px,.92vw);line-height:1.35">{esc(s)}</div>'
            f'</div>'
            f'{arrow}'
        )
    return f'''<!-- ============ #{num:03d} Process ============ -->
<section class="{bg}" data-layout="S05" data-animate="stack-build">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('dots', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;position:relative;z-index:1;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3.2vw,5.8vh);line-height:1.05;letter-spacing:-.035em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:flex;gap:1vw;align-items:stretch;overflow-x:auto">{cells}</div>
    </div>
  </div>
</section>
'''

def slide_compare(num: int, kicker: str, title: str, left_label: str, left_body: list[str], right_label: str, right_body: list[str], color: str = 'light') -> str:
    """2-column compare with one side highlighted."""
    bg = 'slide ' + color
    def col(label, body, accent=False):
        bg_inline = 'background:var(--accent);color:var(--accent-on)' if accent else 'background:var(--grey-1);color:var(--ink)'
        items = ''.join(
            f'<li style="font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(13px,.95vw);line-height:1.5;padding:.8vh 0;border-top:1px solid rgba(127,127,127,.18)">{esc(p)}</li>'
            for p in body
        )
        return f'''<div style="padding:2vh 1.6vw;{bg_inline};border-radius:4px">
          <div class="t-meta" style="opacity:.78;margin-bottom:1.2vh">{esc(label)}</div>
          <ul style="list-style:none;padding:0;margin:0">{items}</ul>
        </div>'''
    return f'''<!-- ============ #{num:03d} Compare ============ -->
<section class="{bg}" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3.2vw,5.8vh);line-height:1.05;letter-spacing:-.035em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:1fr 1fr;gap:2vw;align-items:start">{col(left_label, left_body)}{col(right_label, right_body, accent=True)}</div>
    </div>
  </div>
</section>
'''

def slide_table(num: int, kicker: str, title: str, headers: list[str], rows: list[list[str]], color: str = 'light') -> str:
    """Table slide with overflow scroll for long content."""
    bg = 'slide ' + color
    # Add row number column for visual interest
    header_cells = ''.join(
        f'<th style="text-align:left;font-family:var(--sans-tab);font-weight:600;font-size:max(11px,.78vw);letter-spacing:.04em;color:var(--accent);padding:1vh .8vw;border-bottom:2px solid var(--accent);white-space:nowrap">{esc(h)}</th>'
        for h in headers
    )
    n_cols = len(headers)
    # If many columns, font shrinks
    font_size = 'max(10px,.78vw)' if n_cols > 4 else 'max(11px,.82vw)'

    # Mark first row as "top" (highlighted)
    body_rows = ''
    for i, r in enumerate(rows):
        cells = ''.join(
            f'<td style="font-family:var(--sans-tab),var(--sans-zh);font-weight:{"600" if i == 0 else "400"};font-size:{font_size};line-height:1.45;color:{"var(--ink)" if i == 0 else "var(--text-primary)"};padding:1.2vh .8vw;border-bottom:1px solid var(--border-subtle);vertical-align:top;{"background:var(--gold-mist);" if i == 0 else ""}">{esc(c)}</td>'
            for c in r
        )
        body_rows += f'<tr>{cells}</tr>'

    n_rows = len(rows)
    return f'''<!-- ============ #{num:03d} Table ============ -->
<section class="{bg}" data-layout="S20" data-animate="grid-reveal">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    <div style="position:absolute;inset:0;pointer-events:none;opacity:.25">{svg_pattern('grid', 1920, 1080, 'var(--ink)')}</div>
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d} · {n_rows} 行</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2vh;position:relative;z-index:1;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.8vw,5vh);line-height:1.05;letter-spacing:-.035em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="overflow:auto;border:1px solid var(--border-subtle);border-radius:4px;background:var(--paper)">
        <table style="width:100%;border-collapse:collapse;font-size:{font_size}">
          <thead><tr>{header_cells}</tr></thead>
          <tbody>{body_rows}</tbody>
        </table>
      </div>
    </div>
  </div>
</section>
'''

def slide_kpi_hero(num: int, kicker: str, title: str, kpis: list[tuple[str, str, str]], color: str = 'light') -> str:
    """KPI hero with 3-4 big numbers."""
    bg = 'slide ' + color
    cells = ''
    for label, value, note in kpis:
        cells += (
            f'<div style="display:flex;flex-direction:column;gap:.6vh;padding:1.6vh;border-top:2px solid var(--ink)">'
            f'<div class="t-meta" style="opacity:.6">{esc(label)}</div>'
            f'<div style="font-family:var(--sans-tab);font-weight:700;font-size:min(3.6vw,6.4vh);line-height:.88;letter-spacing:-.04em">{esc(value)}</div>'
            f'<div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(12px,.88vw);line-height:1.45;opacity:.7;margin-top:.4vh">{esc(note)}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} KPI Hero ============ -->
<section class="{bg}" data-layout="S06" data-animate="measure-up">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3vw,5.4vh);line-height:1.05;letter-spacing:-.035em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat({len(kpis)},1fr);gap:1.6vw;align-items:start">{cells}</div>
    </div>
  </div>
</section>
'''

# ===== 10 NEW CONSULTING-STYLE TEMPLATES =====

def svg_icon(name: str, size: int = 64, color: str = 'var(--ink)', stroke_width: int = 1) -> str:
    """Render a simple SVG icon (Lucide-inspired, inlined)."""
    icons = {
        'chart': '<polyline points="3 17 9 11 13 15 21 7"/><polyline points="14 7 21 7 21 13"/><line x1="3" y1="21" x2="21" y2="21"/>',
        'tree': '<circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M12 7 L12 14 M12 14 L7 17 M12 14 L17 17"/>',
        'leaf': '<path d="M11 20 A7 7 0 0 1 4 13 A9 9 0 0 1 20 7 Q15 12 11 20 Z"/><path d="M4 13 L11 20"/>',
        'building': '<rect x="4" y="3" width="16" height="18" rx="1"/><line x1="9" y1="7" x2="9" y2="7"/><line x1="15" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="9" y2="11"/><line x1="15" y1="11" x2="15" y2="11"/><line x1="9" y1="15" x2="9" y2="15"/><line x1="15" y1="15" x2="15" y2="15"/><path d="M10 21 L10 14 L14 14 L14 21"/>',
        'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12 L21 12 M12 3 Q7 12 12 21 M12 3 Q17 12 12 21"/>',
        'users': '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20 Q3 13 9 13 Q15 13 15 20 M14 20 Q14 15 17 14 Q21 14 21 20"/>',
        'shield': '<path d="M12 3 L20 6 L20 12 Q20 17 12 21 Q4 17 4 12 L4 6 Z"/><path d="M9 12 L11 14 L15 10"/>',
        'sparkle': '<path d="M12 3 L13.5 9 L20 10.5 L13.5 12 L12 18 L10.5 12 L4 10.5 L10.5 9 Z M19 16 L19.7 18.3 L22 19 L19.7 19.7 L19 22 L18.3 19.7 L16 19 L18.3 18.3 Z"/>',
        'compass': '<circle cx="12" cy="12" r="9"/><polygon points="16 8 13 13 8 16 11 11" fill="currentColor"/>',
        'mountain': '<path d="M3 20 L9 9 L13 14 L17 8 L21 20 Z"/><circle cx="9" cy="7" r="1.2"/>',
        'flame': '<path d="M12 3 Q8 8 8 13 Q8 18 12 21 Q16 18 16 13 Q16 9 14 7 Q14 4 12 3 Z M12 9 Q11 11 11 13 Q11 16 12 17 Q13 16 13 13 Q13 11 12 9 Z"/>',
        'coins': '<circle cx="8" cy="8" r="5"/><circle cx="16" cy="16" r="5"/><path d="M5 16 L5 19 A5 5 0 0 0 11 19 L11 16 M13 8 L13 5 A5 5 0 0 0 7 5 L7 8"/>',
        'target': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/>',
        'ruler': '<path d="M3 17 L17 3 L21 7 L7 21 Z"/><path d="M7 11 L9 9 M10 14 L12 12 M13 17 L15 15 M6 8 L8 6 M9 11 L11 9 M12 14 L14 12"/>',
        'gem': '<polygon points="6 3 18 3 22 9 12 21 2 9"/><line x1="2" y1="9" x2="22" y2="9"/><line x1="12" y1="21" x2="8" y2="9"/><line x1="12" y1="21" x2="16" y2="9"/>',
        'book': '<path d="M4 4 L4 20 L10 20 Q12 18 14 20 L20 20 L20 4 L14 4 Q12 6 10 4 Z"/><line x1="9" y1="9" x2="9" y2="17"/><line x1="15" y1="9" x2="15" y2="17"/>',
        'wave': '<path d="M3 12 Q7 6 11 12 T19 12 T27 12"/><path d="M3 17 Q7 11 11 17 T19 17 T27 17"/>',
        'rocket': '<path d="M12 3 L15 9 L21 12 L15 15 L12 21 L9 15 L3 12 L9 9 Z"/><circle cx="12" cy="12" r="2" fill="currentColor"/>',
        'cog': '<circle cx="12" cy="12" r="3"/><path d="M12 1 L13 5 L11 5 Z M12 23 L13 19 L11 19 Z M1 12 L5 13 L5 11 Z M23 12 L19 13 L19 11 Z M4 4 L7 5 L5 7 Z M20 20 L17 19 L19 17 Z M4 20 L5 17 L7 19 Z M20 4 L19 7 L17 5 Z"/>',
        'arrow': '<path d="M5 12 L19 12 M12 5 L19 12 L12 19"/>',
        'check': '<path d="M5 12 L10 17 L19 7"/>',
        'circle-dot': '<circle cx="12" cy="12" r="4" fill="currentColor"/>',
        'pin': '<path d="M12 2 C7 2 4 6 4 10 C4 14 12 22 12 22 C12 22 20 14 20 10 C20 6 17 2 12 2 Z"/><circle cx="12" cy="10" r="2.5" fill="var(--paper)"/>',
    }
    inner = icons.get(name, '<circle cx="12" cy="12" r="9"/>')
    return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'

def svg_pattern(name: str, w: int = 600, h: int = 400, color: str = 'var(--ink)') -> str:
    """Decorative geometric pattern as inline SVG."""
    if name == 'dots':
        return f'<svg viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"><defs><pattern id="dots-{w}" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.4" fill="{color}" opacity="0.18"/></pattern></defs><rect width="{w}" height="{h}" fill="url(#dots-{w})"/></svg>'
    if name == 'grid':
        return f'<svg viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"><defs><pattern id="grid-{w}" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0 L0 0 0 40" fill="none" stroke="{color}" stroke-width="0.5" opacity="0.12"/></pattern></defs><rect width="{w}" height="{h}" fill="url(#grid-{w})"/></svg>'
    if name == 'stripes':
        return f'<svg viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"><defs><pattern id="stripes-{w}" x="0" y="0" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-30)"><rect width="6" height="14" fill="{color}" opacity="0.14"/></pattern></defs><rect width="{w}" height="{h}" fill="url(#stripes-{w})"/></svg>'
    if name == 'wave':
        return f'<svg viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="none"><path d="M0 {h*0.7} Q{w*0.25} {h*0.5} {w*0.5} {h*0.7} T{w} {h*0.6} L{w} {h} L0 {h} Z" fill="{color}" opacity="0.10"/></svg>'
    return ''

# ---- T01 · Stat Hero · Single big number with context ----
def slide_stat_hero(num: int, kicker: str, title: str, big: str, unit: str, sub: str, source: str = '', color: str = 'light') -> str:
    bg = 'slide ' + color
    return f'''<!-- ============ #{num:03d} Stat Hero ============ -->
<section class="{bg}" data-layout="TABLEAI-STAT-HERO" data-animate="matrix-statement">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('dots', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:2.6vh;position:relative;z-index:1">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3vw,5.4vh);line-height:1.04;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;justify-content:center;align-items:flex-start;gap:1.6vh;max-width:80%">
        <div style="display:flex;align-items:baseline;gap:.3em;line-height:.9">
          <span style="font-family:var(--sans-tab);font-weight:700;font-size:min(15vw,28vh);letter-spacing:-.06em;color:var(--ink);line-height:.85">{esc(big)}</span>
          {f'<span style="font-family:var(--sans-tab);font-weight:600;font-size:min(3.2vw,6vh);color:var(--accent);margin-left:.1em">{esc(unit)}</span>' if unit else ''}
        </div>
        <p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(15px,1.3vw);line-height:1.5;color:var(--text-primary);max-width:64ch">{esc(sub)}</p>
        {f'<div class="t-meta" style="margin-top:.4em;color:var(--text-helper)">数据来源 · {esc(source)}</div>' if source else ''}
      </div>
      <div class="t-meta" style="color:var(--text-helper)">→ 下一张</div>
    </div>
  </div>
</section>
'''

# ---- T02 · Pull Quote · Big centered quote with attribution ----
def slide_pull_quote(num: int, kicker: str, quote: str, author: str, role: str = '', color: str = 'dark') -> str:
    bg = 'slide ' + color
    return f'''<!-- ============ #{num:03d} Pull Quote ============ -->
<section class="{bg}" data-layout="TABLEAI-PULL-QUOTE" data-animate="statement">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('wave', 1920, 1080, 'rgba(255,255,255,0.10)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;display:grid;grid-template-columns:auto 1fr;gap:6vw;align-items:center;padding:0 4vw;position:relative;z-index:1">
      <div data-anim="up" style="font-family:Georgia,serif;font-size:min(18vw,32vh);line-height:.7;color:var(--accent-bright);font-weight:700;letter-spacing:-.05em">"</div>
      <div style="display:flex;flex-direction:column;gap:2.4vh;align-self:center">
        <div data-anim="up" class="t-meta" style="color:var(--accent-bright);letter-spacing:.18em">{esc(kicker)}</div>
        <blockquote data-anim="up" style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:min(3.4vw,6.2vh);line-height:1.3;letter-spacing:-.015em;color:{'var(--ink)' if color == 'light' else 'var(--paper)'};max-width:80%;margin:0">
          {esc(quote)}
        </blockquote>
        <div data-anim="up" style="display:flex;flex-direction:column;gap:.4em;padding-top:1.2vh;border-top:2px solid var(--accent);max-width:60%">
          <span class="t-meta" style="color:{'var(--ink)' if color == 'light' else 'var(--paper)'};font-weight:600">{esc(author)}</span>
          {f'<span class="t-meta" style="color:var(--text-helper)">{esc(role)}</span>' if role else ''}
        </div>
      </div>
    </div>
  </div>
</section>
'''

# ---- T03 · 4-Quadrant Matrix · 2x2 grid of insights ----
def slide_quadrant(num: int, kicker: str, title: str, quadrants: list[tuple[str, str, str, str]], color: str = 'light') -> str:
    """quadrants: list of (icon_name, label, body, accent_color)."""
    bg = 'slide ' + color
    cells = ''
    for i, (icon, label, body, accent) in enumerate(quadrants[:4]):
        accent_color = accent if accent in ('var(--accent)', 'var(--ink)', 'var(--text-secondary)') else 'var(--ink)'
        cells += (
            f'<div style="display:flex;flex-direction:column;gap:1.2vh;padding:1.6vh 1.2vw;border-top:3px solid {accent_color};background:{("var(--gold-mist)" if accent == "var(--accent)" else "var(--grey-1)") if color == "light" else "rgba(255,255,255,.04)"};border-radius:2px">'
            f'<div style="display:flex;gap:.8em;align-items:center">'
            f'<div style="width:3.4vh;height:3.4vh;display:flex;align-items:center;justify-content:center;color:{accent_color}">{svg_icon(icon, 32, accent_color, 1.6)}</div>'
            f'<span class="t-meta" style="color:{accent_color};font-size:max(11px,.78vw)">Q{str(i+1).zfill(2)}</span>'
            f'</div>'
            f'<h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(15px,1.4vw);line-height:1.2;letter-spacing:-.01em;color:{"var(--ink)" if color == "light" else "var(--paper)"};margin-top:.6vh">{esc(label)}</h3>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(11px,.85vw);line-height:1.55;color:{"var(--text-secondary)" if color == "light" else "rgba(255,255,255,.78)"};margin-top:.4vh">{esc(body)}</p>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} 4-Quadrant Matrix ============ -->
<section class="{bg}" data-layout="TABLEAI-QUADRANT" data-animate="grid-reveal">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:1.2vw;align-items:stretch">{cells}</div>
    </div>
  </div>
</section>
'''

# ---- T04 · 3-Card Highlight · Wide horizontal stat row ----
def slide_3card(num: int, kicker: str, title: str, cards: list[tuple[str, str, str]], color: str = 'light') -> str:
    """cards: list of (icon, big_value, sub_label, body)."""
    bg = 'slide ' + color
    cells = ''
    for i, (icon, val, lbl, body) in enumerate(cards[:3]):
        accent = 'var(--accent)' if i == 0 else 'var(--ink)'
        cells += (
            f'<div style="display:flex;flex-direction:column;gap:1.4vh;padding:2.4vh 1.6vw;background:{"var(--grey-1)" if color == "light" else "rgba(255,255,255,.04)"};border-radius:4px;border-top:3px solid {accent};position:relative">'
            f'<div style="width:3.6vh;height:3.6vh;color:{accent};display:flex;align-items:center">{svg_icon(icon, 32, accent, 1.5)}</div>'
            f'<div style="font-family:var(--sans-tab);font-weight:700;font-size:min(3.6vw,6.6vh);line-height:.88;letter-spacing:-.04em;color:{accent};margin-top:.6vh">{esc(val)}</div>'
            f'<div class="t-meta" style="color:var(--text-helper);font-size:max(10px,.78vw)">{esc(lbl)}</div>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(12px,.88vw);line-height:1.55;color:{"var(--text-secondary)" if color == "light" else "rgba(255,255,255,.78)"};margin-top:.6vh">{esc(body)}</p>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} 3-Card Highlight ============ -->
<section class="{bg}" data-layout="TABLEAI-3CARD" data-animate="grid-reveal">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.4vw;align-items:stretch">{cells}</div>
    </div>
  </div>
</section>
'''

# ---- T05 · Number Ladder · 4 numbered steps stacked ----
def slide_ladder(num: int, kicker: str, title: str, steps: list[tuple[str, str]], color: str = 'light') -> str:
    """steps: list of (label, body). 4 steps max."""
    bg = 'slide ' + color
    cells = ''
    for i, (label, body) in enumerate(steps[:4], 1):
        cells += (
            f'<div style="display:grid;grid-template-columns:5em 1fr;gap:1.6vw;align-items:start;padding:1.4vh 0;border-top:1px solid {("var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)")}">'
            f'<div style="font-family:var(--sans-tab);font-weight:700;font-size:min(4vw,7vh);line-height:.85;letter-spacing:-.05em;color:{"var(--accent)" if i == 1 else "var(--text-helper)"}">0{i}</div>'
            f'<div>'
            f'<h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(14px,1.25vw);line-height:1.2;letter-spacing:-.01em;color:{"var(--ink)" if color == "light" else "var(--paper)"};margin-bottom:.4vh">{esc(label)}</h3>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(11px,.85vw);line-height:1.55;color:{"var(--text-secondary)" if color == "light" else "rgba(255,255,255,.78)"}">{esc(body)}</p>'
            f'</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Number Ladder ============ -->
<section class="{bg}" data-layout="TABLEAI-LADDER" data-animate="grid-reveal">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:5vw;align-items:start;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;align-self:start;position:sticky;top:0">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3vw,5.4vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
        <div style="display:flex;align-items:center;gap:1em;margin-top:1.4vh">
          <div style="width:6vh;height:6vh;display:flex;align-items:center;justify-content:center;color:var(--accent)">{svg_icon('arrow', 36, 'var(--accent)', 1.5)}</div>
          <span class="t-meta" style="color:var(--text-helper)">{len(steps)} 步 · 顺序执行</span>
        </div>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:0">{cells}</div>
    </div>
  </div>
</section>
'''

# ---- T06 · Icon Grid · 6 numbered cards in 3x2 ----
def slide_icon_grid(num: int, kicker: str, title: str, items: list[tuple[str, str, str]], color: str = 'light') -> str:
    """items: list of (icon, label, body). 6 max."""
    bg = 'slide ' + color
    cells = ''
    for i, (icon, label, body) in enumerate(items[:6], 1):
        cells += (
            f'<div style="display:flex;flex-direction:column;gap:.8vh;padding:1.6vh 1.2vw;border-top:2px solid {"var(--ink)" if i % 3 == 1 else "var(--grey-2)"};background:{"var(--paper)" if i % 2 == 0 else "var(--grey-1)"};border-radius:2px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div style="width:3vh;height:3vh;color:{"var(--accent)" if i == 1 else "var(--ink)"};display:flex;align-items:center">{svg_icon(icon, 24, "currentColor", 1.5)}</div>'
            f'<span class="t-meta" style="color:{"var(--accent)" if i == 1 else "var(--text-helper)"}">0{i}</span>'
            f'</div>'
            f'<h4 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(13px,1.15vw);line-height:1.2;letter-spacing:-.005em;margin-top:.4vh">{esc(label)}</h4>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(10.5px,.78vw);line-height:1.5;color:var(--text-secondary);margin-top:.2vh">{esc(body)}</p>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Icon Grid ============ -->
<section class="{bg}" data-layout="TABLEAI-ICON-GRID" data-animate="grid-reveal">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2.4vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:.8vw;align-items:stretch">{cells}</div>
    </div>
  </div>
</section>
'''

# ---- T07 · Data Callout · Big stat + 3 supporting facts ----
def slide_data_callout(num: int, kicker: str, title: str, big: str, unit: str, headline: str, facts: list[tuple[str, str]], color: str = 'light') -> str:
    """facts: list of (label, value)."""
    bg = 'slide ' + color
    fact_cells = ''
    for lbl, val in facts[:4]:
        fact_cells += (
            f'<div style="display:flex;flex-direction:column;gap:.4vh;padding:1vh 1.2vw;border-top:1px solid {"var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)"}">'
            f'<div class="t-meta" style="color:var(--text-helper)">{esc(lbl)}</div>'
            f'<div style="font-family:var(--sans-tab);font-weight:600;font-size:max(14px,1.2vw);color:{"var(--ink)" if color == "light" else "var(--paper)"};letter-spacing:-.01em">{esc(val)}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Data Callout ============ -->
<section class="{bg}" data-layout="TABLEAI-DATA-CALLOUT" data-animate="grid-reveal">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('stripes', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:5vw;align-items:center;position:relative;z-index:1;overflow:hidden">
      <div data-anim="up" style="display:flex;flex-direction:column;gap:1.4vh;align-self:center">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <div style="display:flex;align-items:baseline;gap:.3em;line-height:.9">
          <span style="font-family:var(--sans-tab);font-weight:700;font-size:min(11vw,20vh);letter-spacing:-.05em;color:{"var(--ink)" if color == "light" else "var(--paper)"};line-height:.85">{esc(big)}</span>
          {f'<span style="font-family:var(--sans-tab);font-weight:600;font-size:min(2.4vw,4.4vh);color:var(--accent);margin-left:.1em">{esc(unit)}</span>' if unit else ''}
        </div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.1;letter-spacing:-.025em;margin-top:1vh;max-width:20ch">{esc(headline)}</h2>
        <div style="display:flex;align-items:center;gap:.8em;margin-top:1vh">
          <div style="width:2.4vh;height:2.4vh;color:var(--accent)">{svg_icon('check', 18, 'currentColor', 2)}</div>
          <span class="t-meta" style="color:var(--text-helper)">来源 · {esc(title)}</span>
        </div>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:1fr 1fr;gap:1vw;align-content:center">{fact_cells}</div>
    </div>
  </div>
</section>
'''

# ---- T08 · Section Mini-TOC · Jump links for current section ----
def slide_mini_toc(num: int, kicker: str, section_title: str, items: list[tuple[str, str]], color: str = 'dark') -> str:
    """items: list of (label, anchor)."""
    bg = 'slide ' + color
    cells = ''
    for i, (label, anchor) in enumerate(items[:6], 1):
        cells += (
            f'<a href="#{esc(anchor)}" style="display:grid;grid-template-columns:5em 1fr auto;gap:1.6vw;align-items:center;padding:1.6vh 0;border-top:1px solid rgba(255,255,255,.14);text-decoration:none;color:rgba(255,255,255,.86);font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(14px,1.2vw);line-height:1.4;cursor:pointer;transition:background .15s ease">'
            f'<span style="font-family:var(--mono);font-size:max(12px,.85vw);color:var(--accent-bright);font-weight:600">0{i}</span>'
            f'<span>{esc(label)}</span>'
            f'<span style="color:var(--accent-bright);font-size:18px">→</span>'
            f'</a>'
        )
    return f'''<!-- ============ #{num:03d} Section Mini-TOC ============ -->
<section class="{bg}" data-layout="TABLEAI-MINI-TOC" data-animate="grid-reveal">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('grid', 1920, 1080, 'rgba(255,255,255,0.05)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2.6vh;position:relative;z-index:1">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent-bright)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.8vw,5vh);line-height:1.05;letter-spacing:-.03em;color:#fff">{esc(section_title)}</h2>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:0;align-content:center;justify-content:center;max-width:80vw">{cells}</div>
    </div>
  </div>
</section>
'''

# ---- T09 · Two-Column Rich Compare (with icon, big stat, supporting) ----
def slide_compare_rich(num: int, kicker: str, title: str, left_icon: str, left_label: str, left_big: str, left_unit: str, left_body: list[str], right_icon: str, right_label: str, right_big: str, right_unit: str, right_body: list[str], color: str = 'light') -> str:
    bg = 'slide ' + color
    def col(icon, lbl, big, unit, body, accent):
        items = ''.join(
            f'<li style="font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(12px,.9vw);line-height:1.5;padding:.6vh 0;border-top:1px solid {"var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)"}">{esc(p)}</li>'
            for p in body
        )
        return (
            f'<div style="display:flex;flex-direction:column;gap:1.4vh;padding:2.4vh 1.6vw;background:{"var(--gold-mist)" if accent == "var(--accent)" else "var(--grey-1)"};border-radius:4px;border-left:4px solid {accent};min-width:0">'
            f'<div style="display:flex;align-items:center;gap:.8em">'
            f'<div style="width:3.4vh;height:3.4vh;color:{accent};display:flex;align-items:center">{svg_icon(icon, 30, "currentColor", 1.6)}</div>'
            f'<span class="t-meta" style="color:{accent};font-size:max(11px,.78vw)">{esc(lbl)}</span>'
            f'</div>'
            f'<div style="display:flex;align-items:baseline;gap:.3em;line-height:.9;margin-top:.4vh">'
            f'<span style="font-family:var(--sans-tab);font-weight:700;font-size:min(4.4vw,8vh);letter-spacing:-.04em;color:{accent}">{esc(big)}</span>'
            f'<span style="font-family:var(--sans-tab);font-weight:600;font-size:min(1.4vw,2.6vh);color:{accent};margin-left:.1em">{esc(unit)}</span>' if unit else '' +
            f'</div>'
            f'<ul style="list-style:none;padding:0;margin:0">{items}</ul>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Compare Rich ============ -->
<section class="{bg}" data-layout="TABLEAI-COMPARE-RICH" data-animate="duo-mirror">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:1fr 1fr;gap:1.6vw;align-items:stretch">
        {col(left_icon, left_label, left_big, left_unit, left_body, "var(--ink)")}
        {col(right_icon, right_label, right_big, right_unit, right_body, "var(--accent)")}
      </div>
    </div>
  </div>
</section>
'''

# ---- T10 · Six-Cell Numbered Definitions · 6 numbered cells in 2x3 ----
def slide_six_cells(num: int, kicker: str, title: str, cells: list[tuple[str, str, str]], color: str = 'light') -> str:
    """cells: list of (num, label, body). 6 max."""
    bg = 'slide ' + color
    cell_html = ''
    for n, lbl, body in cells[:6]:
        cell_html += (
            f'<div style="display:flex;flex-direction:column;gap:1vh;padding:1.8vh 1.4vw;border-top:2px solid var(--accent);background:{"var(--paper)" if cells.index((n,lbl,body)) % 2 == 0 else "var(--grey-1)"};border-radius:2px">'
            f'<div class="t-meta" style="color:var(--accent);font-size:max(11px,.85vw);font-weight:600">No. {n}</div>'
            f'<h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(15px,1.35vw);line-height:1.2;letter-spacing:-.01em">{esc(lbl)}</h3>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(11px,.85vw);line-height:1.5;color:var(--text-secondary);margin-top:.4vh">{esc(body)}</p>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Six Cells ============ -->
<section class="{bg}" data-layout="TABLEAI-SIX-CELLS" data-animate="grid-reveal">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2.4vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:1vw;align-items:stretch">{cell_html}</div>
    </div>
  </div>
</section>
'''

# ---- T11 · Donut Chart · Single donut with legend ----
def slide_donut(num: int, kicker: str, title: str, segments: list[tuple[str, float]], center_label: str = '', center_value: str = '', color: str = 'light') -> str:
    """segments: list of (label, percent)."""
    bg = 'slide ' + color
    # Build SVG donut
    import math
    cx, cy, r, stroke = 200, 200, 130, 36
    total = sum(p for _, p in segments) or 100
    cur = -90
    arcs = ''
    palette = ['#0A1626', '#A88B52', '#44474C', '#75777D', '#C9A86B', '#DCD9DB', '#F5F3F4']
    for i, (lbl, pct) in enumerate(segments):
        if pct <= 0: continue
        ang = (pct / total) * 360
        end = cur + ang
        large = 1 if ang > 180 else 0
        x1 = cx + r * math.cos(math.radians(cur))
        y1 = cy + r * math.sin(math.radians(cur))
        x2 = cx + r * math.cos(math.radians(end))
        y2 = cy + r * math.sin(math.radians(end))
        d = f'M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f}'
        arcs += f'<path d="{d}" fill="none" stroke="{palette[i % len(palette)]}" stroke-width="{stroke}"/>'
        cur = end
    legend = ''
    for i, (lbl, pct) in enumerate(segments):
        legend += (
            f'<div style="display:flex;align-items:center;gap:.8em;padding:.6vh 0;border-top:1px solid {"var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)"}">'
            f'<div style="width:1.4vh;height:1.4vh;background:{palette[i % len(palette)]};border-radius:1px;flex:0 0 auto"></div>'
            f'<div style="flex:1;font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(12px,.88vw);line-height:1.3">{esc(lbl)}</div>'
            f'<div style="font-family:var(--sans-tab);font-weight:700;font-size:max(13px,1vw);color:{"var(--accent)" if i == 0 else "var(--ink)"}">{pct:.0f}%</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Donut Chart ============ -->
<section class="{bg}" data-layout="TABLEAI-DONUT" data-animate="grid-reveal">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:3vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:5fr 7fr;gap:4vw;align-items:center">
        <div style="position:relative;display:flex;align-items:center;justify-content:center">
          <svg viewBox="0 0 400 400" width="100%" style="max-width:42vh">
            {arcs}
            <text x="200" y="195" text-anchor="middle" font-family="var(--sans-tab)" font-size="36" font-weight="700" fill="var(--ink)" letter-spacing="-.02em">{esc(center_value)}</text>
            <text x="200" y="225" text-anchor="middle" font-family="var(--mono)" font-size="11" fill="var(--text-helper)" letter-spacing=".18em">{esc(center_label)}</text>
          </svg>
        </div>
        <div style="display:flex;flex-direction:column;gap:0">{legend}</div>
      </div>
    </div>
  </div>
</section>
'''

# ---- T13 · Key Takeaways · 5 items with icon + bold label ----
def slide_takeaways(num: int, kicker: str, title: str, items: list[tuple[str, str]], color: str = 'light') -> str:
    """items: list of (label, body). 5 items max."""
    bg = 'slide ' + color
    cells = ''
    for i, (label, body) in enumerate(items[:5], 1):
        icon = pick_icon(label)
        cells += (
            f'<div style="display:grid;grid-template-columns:3.4vh 1fr;gap:1.4vw;align-items:start;padding:1.2vh 0;border-top:1px solid {"var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)"}">'
            f'<div style="width:3.4vh;height:3.4vh;color:{"var(--accent)" if i == 1 else "var(--ink)"};display:flex;align-items:center;justify-content:center;flex:0 0 auto">{svg_icon(icon, 28, "currentColor", 1.5)}</div>'
            f'<div>'
            f'<div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(13px,1.15vw);line-height:1.25;letter-spacing:-.01em;color:{"var(--ink)" if color == "light" else "var(--paper)"}">{esc(label)}</div>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(10.5px,.82vw);line-height:1.5;color:{"var(--text-secondary)" if color == "light" else "rgba(255,255,255,.72)"};margin-top:.4vh">{esc(body)}</p>'
            f'</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Key Takeaways ============ -->
<section class="{bg}" data-layout="TABLEAI-TAKEAWAYS" data-animate="grid-reveal">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('grid', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2.4vh;position:relative;z-index:1;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:0;overflow-y:auto">{cells}</div>
    </div>
  </div>
</section>
'''

# ---- T12 · Split-Hero — Left big stat + Right 3 supporting facts ----
def slide_split_hero(num: int, kicker: str, title: str, big: str, unit: str, sub: str, supporting: list[tuple[str, str]], color: str = 'light') -> str:
    """supporting: list of (label, value)."""
    bg = 'slide ' + color
    fact_html = ''
    for lbl, val in supporting[:4]:
        fact_html += (
            f'<div style="display:flex;flex-direction:column;gap:.4vh;padding:1.4vh 0;border-top:1px solid {"var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)"}">'
            f'<div class="t-meta" style="color:var(--text-helper)">{esc(lbl)}</div>'
            f'<div style="font-family:var(--sans-tab);font-weight:600;font-size:max(15px,1.3vw);color:{"var(--ink)" if color == "light" else "var(--paper)"}">{esc(val)}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Split Hero ============ -->
<section class="{bg}" data-layout="TABLEAI-SPLIT-HERO" data-animate="grid-reveal">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('dots', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:5vw;align-items:center;position:relative;z-index:1;overflow:hidden">
      <div data-anim="up" style="display:flex;flex-direction:column;gap:1.4vh;align-self:center">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.1;letter-spacing:-.025em;max-width:18ch">{esc(title)}</h2>
        <div style="display:flex;align-items:baseline;gap:.3em;line-height:.9;margin-top:1vh">
          <span style="font-family:var(--sans-tab);font-weight:700;font-size:min(11vw,20vh);letter-spacing:-.05em;color:{"var(--ink)" if color == "light" else "var(--paper)"};line-height:.85">{esc(big)}</span>
          {f'<span style="font-family:var(--sans-tab);font-weight:600;font-size:min(2.4vw,4.4vh);color:var(--accent);margin-left:.1em">{esc(unit)}</span>' if unit else ''}
        </div>
        <p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(13px,1vw);line-height:1.55;color:{"var(--text-secondary)" if color == "light" else "rgba(255,255,255,.78)"};max-width:36ch;margin-top:.6vh">{esc(sub)}</p>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:0">{fact_html}</div>
    </div>
  </div>
</section>
'''

# ===== ADDITIONAL 10 CONSULTING TEMPLATES =====

# ---- T14 · Hero + 3 Takeaways · single big stat + 3 takeaway chips ----
def slide_hero_3takeaways(num: int, kicker: str, title: str, big: str, unit: str, sub: str, takeaways: list[tuple[str, str]], color: str = 'light') -> str:
    bg = 'slide ' + color
    chips = ''
    for lbl, body in takeaways[:3]:
        chips += (
            f'<div style="display:flex;flex-direction:column;gap:.4vh;padding:1.2vh 1.2vw;background:var(--gold-mist);border-left:3px solid var(--accent);border-radius:2px">'
            f'<div class="t-meta" style="color:var(--accent);font-size:max(10px,.72vw);font-weight:600">{esc(lbl)}</div>'
            f'<div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(11px,.85vw);line-height:1.5;color:var(--text-primary)">{esc(body)}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Hero + 3 Takeaways ============ -->
<section class="{bg}" data-layout="TABLEAI-HERO-3TAKEAWAYS" data-animate="measure-up">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('stripes', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:7fr 5fr;gap:5vw;align-items:center;position:relative;z-index:1;overflow:hidden">
      <div data-anim="up" style="display:flex;flex-direction:column;gap:1.6vh;align-self:center">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em;max-width:22ch">{esc(title)}</h2>
        <div style="display:flex;align-items:baseline;gap:.3em;line-height:.9;margin-top:.6vh">
          <span style="font-family:var(--sans-tab);font-weight:700;font-size:min(13vw,24vh);letter-spacing:-.06em;color:var(--ink);line-height:.85">{esc(big)}</span>
          {f'<span style="font-family:var(--sans-tab);font-weight:600;font-size:min(2.6vw,4.8vh);color:var(--accent);margin-left:.1em">{esc(unit)}</span>' if unit else ''}
        </div>
        <p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(13px,1vw);line-height:1.55;color:var(--text-secondary);max-width:38ch;margin-top:.4vh">{esc(sub)}</p>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:1vh">{chips}</div>
    </div>
  </div>
</section>
'''

# ---- T15 · Framework Diagram · 4 named boxes connected by arrows ----
def slide_framework(num: int, kicker: str, title: str, framework_name: str, boxes: list[tuple[str, str, str]], color: str = 'light') -> str:
    """boxes: list of (name, body, color). 4 max. Connects in a 2x2 grid with arrows."""
    bg = 'slide ' + color
    n = len(boxes[:4])
    cells = ''
    colors = ['var(--accent)', 'var(--ink)', 'var(--ink)', 'var(--ink)']
    for i, (name, body, col) in enumerate(boxes[:4]):
        accent = col if col in ('var(--accent)', 'var(--ink)') else 'var(--ink)'
        # Position in 2x2 grid: i=0 TL, i=1 TR, i=2 BL, i=3 BR
        row = i // 2
        col_idx = i % 2
        cells += (
            f'<div style="display:flex;flex-direction:column;gap:.6vh;padding:1.4vh 1.2vw;background:{"var(--paper)" if (row + col_idx) % 2 == 0 else "var(--grey-1)"};border:2px solid {accent};border-radius:6px;position:relative">'
            f'<div class="t-meta" style="color:{accent};font-weight:600;font-size:max(10px,.72vw)">LAYER {i+1:02d}</div>'
            f'<h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(15px,1.35vw);line-height:1.2;letter-spacing:-.01em;color:{accent}">{esc(name)}</h3>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(11px,.85vw);line-height:1.5;color:var(--text-secondary)">{esc(body)}</p>'
            f'</div>'
        )
    arrows_h1 = '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:var(--accent);font-size:max(20px,2.6vw);font-weight:700;line-height:1;display:flex;align-items:center;justify-content:center;width:3.2vw;height:3.2vw;background:var(--paper);border-radius:50%;border:2px solid var(--accent);z-index:2">↔</div>'
    return f'''<!-- ============ #{num:03d} Framework Diagram ============ -->
<section class="{bg}" data-layout="TABLEAI-FRAMEWORK" data-animate="grid-reveal">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('grid', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2.4vh;position:relative;z-index:1;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
        <div class="t-meta" style="color:var(--text-helper)">{esc(framework_name)}</div>
      </div>
      <div data-anim="up" style="position:relative;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:1.4vw;align-items:stretch">
        {cells}
        {arrows_h1 if n >= 4 else ''}
      </div>
    </div>
  </div>
</section>
'''

# ---- T16 · Principle List · 3-5 numbered principles with icon + title + body ----
def slide_principles(num: int, kicker: str, title: str, principles: list[tuple[str, str, str]], color: str = 'light') -> str:
    """principles: list of (icon_name, title, body). 5 max."""
    bg = 'slide ' + color
    cells = ''
    for i, (icon, ttl, body) in enumerate(principles[:5], 1):
        cells += (
            f'<div style="display:grid;grid-template-columns:5em 1fr;gap:1.6vw;align-items:start;padding:1.6vh 0;border-top:1px solid {"var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)"}">'
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:.4vh">'
            f'<div style="width:4vh;height:4vh;border-radius:50%;background:{"var(--accent)" if i == 1 else "var(--ink)"};color:var(--accent-on);display:flex;align-items:center;justify-content:center">{svg_icon(icon, 22, "currentColor", 1.6)}</div>'
            f'<span class="t-meta" style="color:{"var(--accent)" if i == 1 else "var(--text-helper)"};font-size:max(9px,.65vw);font-weight:600">0{i}</span>'
            f'</div>'
            f'<div>'
            f'<h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(14px,1.3vw);line-height:1.2;letter-spacing:-.01em;margin-bottom:.4vh">P{i}. {esc(ttl)}</h3>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(11px,.88vw);line-height:1.55;color:{"var(--text-secondary)" if color == "light" else "rgba(255,255,255,.78)"}">{esc(body)}</p>'
            f'</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Principles ============ -->
<section class="{bg}" data-layout="TABLEAI-PRINCIPLES" data-animate="grid-reveal">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:1fr 2fr;gap:4vw;align-items:start;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;align-self:start;position:sticky;top:0">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
        <div class="t-meta" style="color:var(--text-helper);margin-top:1vh">{len(principles)} 项原则</div>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:0;overflow-y:auto">{cells}</div>
    </div>
  </div>
</section>
'''

# ---- T17 · Risk Matrix · 2x2 impact x likelihood matrix ----
def slide_risk_matrix(num: int, kicker: str, title: str, risks: list[tuple[str, str, str, str]], color: str = 'light') -> str:
    """risks: list of (label, x_label, y_label, severity). 4 max. Positions: TL/TR/BL/BR."""
    bg = 'slide ' + color
    severity_colors = {'high': 'var(--accent)', 'medium': 'var(--ink)', 'low': 'var(--grey-3)'}
    cells = ''
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for i, (label, x_lbl, y_lbl, sev) in enumerate(risks[:4]):
        r, c = positions[i]
        col = severity_colors.get(sev, 'var(--ink)')
        # Place in 2x2 grid
        cells += (
            f'<div style="grid-row:{r+1};grid-column:{c+1};display:flex;flex-direction:column;gap:.6vh;padding:1.4vh 1.2vw;background:{"var(--paper)" if sev == "low" else "var(--grey-1)"};border:2px solid {col};border-radius:6px;position:relative">'
            f'<div class="t-meta" style="color:{col};font-weight:600;font-size:max(10px,.72vw)">Q{str(i+1).zfill(2)} · {sev.upper()}</div>'
            f'<h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(13px,1.15vw);line-height:1.2;letter-spacing:-.01em">{esc(label)}</h3>'
            f'<div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(10px,.78vw);line-height:1.5;color:var(--text-secondary);margin-top:.4vh">'
            f'<div><b>X:</b> {esc(x_lbl)}</div>'
            f'<div><b>Y:</b> {esc(y_lbl)}</div>'
            f'</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Risk Matrix ============ -->
<section class="{bg}" data-layout="TABLEAI-RISK-MATRIX" data-animate="grid-reveal">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:2.4vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="position:relative;display:grid;grid-template-columns:5em 1fr 1fr;grid-template-rows:1fr 1fr 5em;gap:.6vw;align-items:stretch">
        <div style="grid-row:1/3;grid-column:1;display:flex;align-items:center;justify-content:center"><div class="t-meta" style="writing-mode:vertical-rl;transform:rotate(180deg);color:var(--text-helper)">影响 · IMPACT</div></div>
        <div style="grid-row:1;grid-column:2;display:flex;align-items:center;justify-content:center;background:var(--grey-1);font-family:var(--sans-tab);font-weight:600;font-size:max(12px,.85vw);color:var(--text-helper)">高 · HIGH</div>
        <div style="grid-row:1;grid-column:3;display:flex;align-items:center;justify-content:center;background:var(--grey-1);font-family:var(--sans-tab);font-weight:600;font-size:max(12px,.85vw);color:var(--text-helper)">中 · MED</div>
        <div style="grid-row:2;grid-column:2;display:flex;align-items:center;justify-content:center;background:var(--grey-1);font-family:var(--sans-tab);font-weight:600;font-size:max(12px,.85vw);color:var(--text-helper)">中 · MED</div>
        <div style="grid-row:2;grid-column:3;display:flex;align-items:center;justify-content:center;background:var(--grey-1);font-family:var(--sans-tab);font-weight:600;font-size:max(12px,.85vw);color:var(--text-helper)">低 · LOW</div>
        <div style="grid-row:3;grid-column:1/4;display:flex;align-items:center;justify-content:flex-start;padding-left:1vw">
          <div class="t-meta" style="color:var(--text-helper)">可能性 · LIKELIHOOD</div>
        </div>
        {cells}
      </div>
    </div>
  </div>
</section>
'''

# ---- T18 · Roadmap Timeline · Milestones on horizontal track ----
def slide_roadmap(num: int, kicker: str, title: str, milestones: list[tuple[str, str, str]], color: str = 'light') -> str:
    """milestones: list of (date, title, body). 5 max. Visual progress track."""
    bg = 'slide ' + color
    n = len(milestones[:5])
    cells = ''
    for i, (date, ttl, body) in enumerate(milestones[:5], 1):
        is_done = i < n
        dot_col = 'var(--accent)' if i == 1 else ('var(--ink)' if is_done else 'var(--grey-3)')
        cells += (
            f'<div style="display:flex;flex-direction:column;gap:.6vh;align-items:center;position:relative;padding-top:1.2vh">'
            f'<div class="t-meta" style="color:{dot_col};font-size:max(11px,.78vw);font-weight:600">{esc(date)}</div>'
            f'<div style="width:1.6vh;height:1.6vh;border-radius:50%;background:{dot_col};border:3px solid var(--paper);box-shadow:0 0 0 2px {dot_col}"></div>'
            f'<div style="width:1px;flex:1;background:{("var(--ink)" if is_done else "var(--grey-3)")};opacity:{1 if is_done else 0.4};min-height:2vh"></div>'
            f'<h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(12px,1.05vw);line-height:1.2;letter-spacing:-.005em;text-align:center;color:{("var(--ink)" if is_done else "var(--text-helper)")}">{esc(ttl)}</h3>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(9.5px,.74vw);line-height:1.4;color:var(--text-secondary);text-align:center;max-width:14ch">{esc(body)}</p>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Roadmap Timeline ============ -->
<section class="{bg}" data-layout="TABLEAI-ROADMAP" data-animate="timeline-walk">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('stripes', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2.4vh;position:relative;z-index:1;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat({n},1fr);gap:1.2vw;align-items:stretch;align-content:start;position:relative">
        <div style="position:absolute;top:calc(1.2vh + 1.2em + 1.6vh);left:5%;right:5%;height:1px;background:var(--ink);opacity:.2;z-index:0"></div>
        {cells}
      </div>
    </div>
  </div>
</section>
'''

# ---- T19 · Comparison Matrix · 3 options as columns ----
def slide_compare_matrix(num: int, kicker: str, title: str, options: list[tuple[str, list[str], str]], color: str = 'light') -> str:
    """options: list of (name, features, recommendation). 3 max. First option highlighted."""
    bg = 'slide ' + color
    n = len(options[:3])
    cols = ''
    for i, (name, features, rec) in enumerate(options[:3]):
        is_top = i == 0
        accent = 'var(--accent)' if is_top else 'var(--ink)'
        bg_inner = 'var(--gold-mist)' if is_top else 'var(--paper)'
        items = ''.join(
            f'<li style="font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(11px,.82vw);line-height:1.5;padding:.6vh 0;border-top:1px solid {"var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)"};display:flex;gap:.6em;align-items:flex-start"><span style="color:{("var(--accent)" if is_top else "var(--text-helper)")};font-weight:700;flex:0 0 auto">·</span><span>{esc(f)}</span></li>'
            for f in features
        )
        cols += (
            f'<div style="display:flex;flex-direction:column;gap:1.2vh;padding:1.6vh 1.2vw;background:{bg_inner};border:2px solid {accent};border-radius:6px;position:relative">'
            f'<div class="t-meta" style="color:{accent};font-size:max(10px,.72vw);font-weight:600">OPTION {chr(65 + i)}</div>'
            f'<h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(16px,1.4vw);line-height:1.2;letter-spacing:-.01em;color:{accent}">{esc(name)}</h3>'
            f'<ul style="list-style:none;padding:0;margin:0;flex:1">{items}</ul>'
            f'<div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(10.5px,.85vw);line-height:1.45;background:{accent};color:var(--paper);padding:.8em 1em;border-radius:3px;margin-top:.4vh">{esc(rec)}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Compare Matrix ============ -->
<section class="{bg}" data-layout="TABLEAI-COMPARE-MATRIX" data-animate="duo-mirror">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2.4vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat({n},1fr);gap:1.2vw;align-items:stretch">{cols}</div>
    </div>
  </div>
</section>
'''

# ---- T20 · Highlight Statement · Big text on left + small visual on right ----
def slide_highlight(num: int, kicker: str, title: str, highlight: str, sub: str, visual: str, color: str = 'light') -> str:
    """visual is a short SVG mark or icon name."""
    bg = 'slide ' + color
    return f'''<!-- ============ #{num:03d} Highlight Statement ============ -->
<section class="{bg}" data-layout="TABLEAI-HIGHLIGHT" data-animate="statement">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('wave', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:7fr 5fr;gap:6vw;align-items:center;position:relative;z-index:1;overflow:hidden">
      <div data-anim="up" style="display:flex;flex-direction:column;gap:1.6vh;align-self:center">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(3.2vw,6vh);line-height:1.05;letter-spacing:-.025em;max-width:24ch">{esc(title)}</h2>
        <p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(16px,1.4vw);line-height:1.4;letter-spacing:-.01em;color:{"var(--text-primary)" if color == "light" else "var(--paper)"};max-width:30ch;border-left:4px solid var(--accent);padding:0 0 0 1.2vw;margin:1vh 0;line-height:1.45">{esc(highlight)}</p>
        <p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(12px,.95vw);line-height:1.55;color:{"var(--text-secondary)" if color == "light" else "rgba(255,255,255,.78)"};max-width:36ch">{esc(sub)}</p>
      </div>
      <div data-anim="up" style="display:flex;align-items:center;justify-content:center">
        <div style="width:24vh;height:24vh;background:var(--gold-mist);border-radius:50%;display:flex;align-items:center;justify-content:center;color:var(--accent)">{svg_icon(visual, 96, 'currentColor', 1.2)}</div>
      </div>
    </div>
  </div>
</section>
'''

# ---- T21 · Numbered Stats Row · 4-5 big numbers in a horizontal row ----
def slide_stat_row(num: int, kicker: str, title: str, stats: list[tuple[str, str, str, str]], color: str = 'light') -> str:
    """stats: list of (value, unit, label, sub). 4-5 max."""
    bg = 'slide ' + color
    n = len(stats[:5])
    cells = ''
    for i, (val, unit, lbl, sub) in enumerate(stats[:5]):
        is_top = i == 0
        col = 'var(--accent)' if is_top else 'var(--ink)'
        cells += (
            f'<div style="display:flex;flex-direction:column;gap:.6vh;padding:2.4vh 1vw;text-align:center;border-right:{"1px solid var(--border-subtle)" if i < n-1 else "none"}">'
            f'<div class="t-meta" style="color:var(--text-helper);font-size:max(10px,.72vw);font-weight:600;letter-spacing:.06em">0{i+1}</div>'
            f'<div style="display:flex;align-items:baseline;gap:.2em;justify-content:center;line-height:.9">'
            f'<span style="font-family:var(--sans-tab);font-weight:700;font-size:min(5vw,9vh);letter-spacing:-.045em;color:{col};line-height:.85">{esc(val)}</span>'
            f'<span style="font-family:var(--sans-tab);font-weight:600;font-size:min(1.4vw,2.6vh);color:{col};margin-left:.1em">{esc(unit)}</span>' if unit else '' +
            f'</div>'
            f'<div class="t-meta" style="color:{col};font-size:max(11px,.78vw);font-weight:600;margin-top:.4vh">{esc(lbl)}</div>'
            f'<div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(10px,.78vw);line-height:1.5;color:var(--text-secondary);margin-top:.2vh">{esc(sub)}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Stat Row ============ -->
<section class="{bg}" data-layout="TABLEAI-STAT-ROW" data-animate="measure-up">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('dots', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2.4vh;position:relative;z-index:1;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat({n},1fr);gap:0;align-items:stretch;align-content:center">{cells}</div>
    </div>
  </div>
</section>
'''

# ---- T22 · Insight + Visual Pair · Big insight + 2-3 supporting visual elements ----
def slide_insight_visual(num: int, kicker: str, title: str, insight: str, sub: str, visuals: list[tuple[str, str, str]], color: str = 'light') -> str:
    """visuals: list of (icon, label, stat). 3 max."""
    bg = 'slide ' + color
    visual_cells = ''
    for icon, lbl, stat in visuals[:3]:
        visual_cells += (
            f'<div style="display:flex;flex-direction:column;gap:.6vh;padding:1.4vh 1.2vw;background:var(--grey-1);border-radius:4px;align-items:center;text-align:center">'
            f'<div style="width:3vh;height:3vh;color:var(--accent);display:flex;align-items:center">{svg_icon(icon, 28, "currentColor", 1.5)}</div>'
            f'<div style="font-family:var(--sans-tab);font-weight:700;font-size:max(15px,1.4vw);line-height:.95;color:var(--ink)">{esc(stat)}</div>'
            f'<div class="t-meta" style="color:var(--text-helper)">{esc(lbl)}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Insight + Visual ============ -->
<section class="{bg}" data-layout="TABLEAI-INSIGHT-VIS" data-animate="grid-reveal">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('grid', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:6fr 6fr;gap:5vw;align-items:center;position:relative;z-index:1;overflow:hidden">
      <div data-anim="up" style="display:flex;flex-direction:column;gap:1.6vh;align-self:center">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em;max-width:22ch">{esc(title)}</h2>
        <p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(16px,1.3vw);line-height:1.4;color:var(--ink);max-width:30ch;border-left:4px solid var(--accent);padding-left:1.2vw;line-height:1.45">{esc(insight)}</p>
        <p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(12px,.95vw);line-height:1.55;color:var(--text-secondary);max-width:38ch;margin-top:.4vh">{esc(sub)}</p>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat(3,1fr);gap:1vw;align-items:stretch">{visual_cells}</div>
    </div>
  </div>
</section>
'''

# ---- T23 · Pyramid Hierarchy · 3-level stacked (top→middle→bottom) ----
def slide_pyramid(num: int, kicker: str, title: str, levels: list[tuple[str, str]], color: str = 'light') -> str:
    """levels: list of (label, body). 3 max, top first (smallest) → bottom (largest)."""
    bg = 'slide ' + color
    n = len(levels[:3])
    levels_html = ''
    widths = [40, 60, 85][:n]
    for i, (lbl, body) in enumerate(levels[:3]):
        w = widths[i]
        is_top = i == 0
        col = 'var(--accent)' if is_top else 'var(--ink)'
        levels_html += (
            f'<div data-anim="up" style="width:{w}%;margin:0 auto;display:flex;flex-direction:column;gap:.4vh;padding:1.2vh 1.6vw;background:{("var(--accent)" if is_top else "var(--grey-1)")};color:{"var(--accent-on)" if is_top else "var(--ink)"};border-radius:4px;text-align:center">'
            f'<div class="t-meta" style="color:{"rgba(255,255,255,.78)" if is_top else "var(--text-helper)"};font-size:max(10px,.72vw);font-weight:600">LEVEL {n - i}</div>'
            f'<div style="font-family:var(--sans-tab),{("" if is_top else "var(--sans-zh),")}font-weight:700;font-size:max(15px,1.4vw);line-height:1.2;letter-spacing:-.01em">{esc(lbl)}</div>'
            f'<div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(10.5px,.82vw);line-height:1.5;opacity:{"0.85" if is_top else "1"}">{esc(body)}</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Pyramid Hierarchy ============ -->
<section class="{bg}" data-layout="TABLEAI-PYRAMID" data-animate="stack-build">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('stripes', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:1fr 2fr;gap:5vw;align-items:center;position:relative;z-index:1;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;align-self:start;position:sticky;top:0">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.6vw,4.8vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
        <div class="t-meta" style="color:var(--text-helper);margin-top:1vh">{n} 层 · 自上而下</div>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:1.2vh;justify-content:center">{levels_html}</div>
    </div>
  </div>
</section>
'''

# ---- T24 · 2-Column Quote + Body · Quote on top, 2-column body on bottom ----
def slide_quote_body(num: int, kicker: str, title: str, quote: str, left_label: str, left_body: list[str], right_label: str, right_body: list[str], color: str = 'light') -> str:
    bg = 'slide ' + color
    def col(label, body, accent=False):
        items = ''.join(
            f'<li style="font-family:var(--sans-tab),var(--sans-zh);font-weight:500;font-size:max(12px,.88vw);line-height:1.5;padding:.6vh 0;border-top:1px solid {"var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)"}">{esc(p)}</li>'
            for p in body
        )
        return f'''<div style="display:flex;flex-direction:column;gap:.8vh;padding:1.4vh 1.2vw;background:{"var(--gold-mist)" if accent else "var(--paper)"};border-left:3px solid {"var(--accent)" if accent else "var(--ink)"};border-radius:2px"><div class="t-meta" style="color:{"var(--accent)" if accent else "var(--text-helper)"};font-weight:600;font-size:max(10px,.72vw)">{esc(label)}</div><ul style="list-style:none;padding:0;margin:0">{items}</ul></div>'''
    return f'''<!-- ============ #{num:03d} Quote + Body ============ -->
<section class="{bg}" data-layout="TABLEAI-QUOTE-BODY" data-animate="statement">
  <div class="canvas-card">
    <header class="chrome-min">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr;gap:2.4vh;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;flex:0 0 auto">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:1.6vh;overflow-y:auto">
        <div style="font-family:var(--sans-tab),var(--sans-zh);font-weight:600;font-size:max(15px,1.4vw);line-height:1.4;letter-spacing:-.005em;color:{"var(--ink)" if color == "light" else "var(--paper)"};border-left:4px solid var(--accent);padding:.4vh 0 .4vh 1.2vw">{esc(quote)}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.4vw">{col(left_label, left_body)}{col(right_label, right_body, True)}</div>
      </div>
    </div>
  </div>
</section>
'''

# ---- T25 · Numbered Hero List · 1-2-3-4 numbered stat callouts ----
def slide_numbered_hero(num: int, kicker: str, title: str, items: list[tuple[str, str, str]], color: str = 'light') -> str:
    """items: list of (num, headline, body). 4 max."""
    bg = 'slide ' + color
    n = len(items[:4])
    cells = ''
    for i, (num, headline, body) in enumerate(items[:4]):
        is_top = i == 0
        cells += (
            f'<div style="display:grid;grid-template-columns:5em 1fr;gap:1.6vw;align-items:start;padding:1.6vh 0;border-top:1px solid {"var(--border-subtle)" if color == "light" else "rgba(255,255,255,.12)"}">'
            f'<div style="font-family:var(--sans-tab);font-weight:700;font-size:min(5vw,9vh);line-height:.85;letter-spacing:-.05em;color:{"var(--accent)" if is_top else "var(--text-helper)"}">{esc(num)}</div>'
            f'<div>'
            f'<h3 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:max(15px,1.4vw);line-height:1.2;letter-spacing:-.01em;color:{"var(--ink)" if color == "light" else "var(--paper)"};margin-bottom:.6vh">{esc(headline)}</h3>'
            f'<p style="font-family:var(--sans-tab),var(--sans-zh);font-weight:400;font-size:max(11px,.88vw);line-height:1.55;color:{"var(--text-secondary)" if color == "light" else "rgba(255,255,255,.78)"}">{esc(body)}</p>'
            f'</div>'
            f'</div>'
        )
    return f'''<!-- ============ #{num:03d} Numbered Hero ============ -->
<section class="{bg}" data-layout="TABLEAI-NUMBERED-HERO" data-animate="grid-reveal">
  <div class="canvas-card" style="position:relative;overflow:hidden">
    {svg_pattern('stripes', 1920, 1080, 'var(--ink)')}
    <header class="chrome-min" style="position:relative;z-index:1">
      <div class="l">{esc(kicker)}</div>
      <div class="r">P {num:03d}</div>
    </header>
    <div style="flex:1;padding:0;display:grid;grid-template-columns:1fr 2fr;gap:4vw;align-items:start;position:relative;z-index:1;overflow:hidden">
      <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh;align-self:start;position:sticky;top:0">
        <div class="t-meta" style="color:var(--accent)">{esc(kicker)}</div>
        <h2 style="font-family:var(--sans-tab),var(--sans-zh);font-weight:700;font-size:min(2.4vw,4.4vh);line-height:1.05;letter-spacing:-.03em">{esc(title)}</h2>
        <div class="t-meta" style="color:var(--text-helper);margin-top:1vh">{n} 个关键点</div>
      </div>
      <div data-anim="up" style="display:flex;flex-direction:column;gap:0;overflow-y:auto">{cells}</div>
    </div>
  </div>
</section>
'''

# ---- Parser: split source.md by # / ## ----

# ---- Parser: split source.md by # / ## ----
text = SRC.read_text(encoding='utf-8')
sections = []
current_h1 = None
current_h2 = None
current_content: list[str] = []

def flush():
    global current_h1, current_h2, current_content
    if current_h1 is not None:
        sections.append({
            'h1': current_h1, 'h2': current_h2,
            'content': '\n'.join(current_content).strip(),
        })
    current_h2 = None
    current_content = []

for line in text.split('\n'):
    if line.startswith('# '):
        flush()
        current_h1 = line[2:].strip()
    elif line.startswith('## '):
        flush()
        current_h2 = line[3:].strip()
    else:
        current_content.append(line)
flush()

src_h1_to_deck = {
    '增城太子坑森林公园沉香目的地项目': '00_cover',
    '01 行政综述｜Executive Summary': '01_executive',
    '02 前言与研究说明｜Introduction & Study Notes': '02_intro',
    '03 宏观环境分析｜Macro-Environment Analysis': '03_macro',
    '04 地块特征分析｜Site & Location Analysis': '04_site',
    '05 供需分析与预测｜Supply & Demand Analysis and Forecast': '05_supply',
    '06 定位建议｜Positioning Recommendation': '06_position',
    '07 功能性设施建议｜Facility Program Recommendation': '07_facility',
    '08 功能分区与动线规划｜Functional Zoning & Circulation Planning': '08_zoning',
    '09 运营现金流测算｜Operating Cash-Flow Projection': '09_cashflow',
    '10 投资回报分析｜Investment Return Analysis': '10_return',
    '11 品牌与运营模式建议｜Brand & Operating-Model Recommendation': '11_brand',
    '12 落地筹建可执行建议｜Implementation & Pre-Opening Roadmap': '12_phasing',
    'A 附件｜Appendices': 'A_appendix',
    '结论': 'closing',
}

from collections import defaultdict
grouped = defaultdict(list)
for sec in sections:
    key = src_h1_to_deck.get(sec['h1'])
    if key:
        grouped[key].append(sec)

deck_section_order = [
    '00_cover', '01_executive', '02_intro', '03_macro', '04_site',
    '05_supply', '06_position', '07_facility', '08_zoning',
    '09_cashflow', '10_return', '11_brand', '12_phasing', 'A_appendix',
]
deck_section_titles = {
    '00_cover': '封面', '01_executive': '行政综述', '02_intro': '前言与研究说明',
    '03_macro': '宏观环境分析', '04_site': '地块特征分析',
    '05_supply': '供需分析与预测', '06_position': '定位建议',
    '07_facility': '功能性设施建议', '08_zoning': '功能分区与动线规划',
    '09_cashflow': '运营现金流测算', '10_return': '投资回报分析',
    '11_brand': '品牌与运营模式建议', '12_phasing': '落地筹建可执行建议',
    'A_appendix': '附件',
}

def emit_section(key: str, sec_data: list[dict], num: int) -> tuple[list[str], int]:
    out = []
    sec_num = key.split('_')[0]
    out.append(slide_section_div(sec_num, deck_section_titles[key]))
    return out, num + 1

def detect_intent(chunk: str) -> str:
    """Classify a chunk's intent to pick the right template. Returns one of:
    'quote' — pull quote
    'stat' — single big number
    'compare' — old vs new / 3-way option compare
    '3way' — 3-option comparison
    'process' — numbered steps (3-4)
    '6list' — six enumerated items
    '3card' / '4card' / 'icongid' / 'takeaways' — bullet card layouts
    'framework' — 4 named layers
    'principles' — numbered principles
    'risk' — risk matrix
    'roadmap' — milestone timeline
    'highlight' — bold statement
    'insight' — insight + visual
    'pyramid' — 3-level hierarchy
    'numbered' — 1-2-3-4 numbered
    'stat_row' — horizontal stat row
    'quote_body' — quote + 2-col body
    'infographic' — heavy data
    'paragraph' — default
    """
    text = chunk
    # Quote detection
    if re.search(r'>\s*\*\*[^<]+', text) or text.lstrip().startswith('>'):
        return 'quote'
    # Single huge number with growth keywords
    big_pct = re.findall(r'\b(\d{2,3}(?:\.\d+)?)\s*%', text)
    if len(big_pct) == 1 and re.search(r'(增长|增长|同比|率|占比|份额|GDP|增速|提升|下降|超过|平均)', text):
        return 'stat'
    # 3-way comparison
    if re.search(r'前者.{0,40}后者', text):
        return '3way'
    # Old vs new
    if re.search(r'(旧.{0,15}新|vs\.?|对比)', text, re.IGNORECASE | re.DOTALL):
        return 'compare'
    # Framework detection (layer + body)
    if re.search(r'(LAYER\s*\d|层级|层级|架构|framework|framework)|(第[一二三四]层)', text, re.IGNORECASE):
        if re.findall(r'(LAYER|第[一二三四]层|层级)', text) and not text.lstrip().startswith('|'):
            return 'framework'
    # Risk keywords
    if re.search(r'(风险|合规边界|威胁|risk|Risk)', text):
        if re.findall(r'(合规|风险|threat|Risk)', text) and len(re.findall(r'^\s*[-*]\s+', text, re.MULTILINE)) >= 2:
            return 'risk'
    # Roadmap / milestone keywords
    if re.search(r'(Phase\s*\d|里程碑|roadmap|Milestone|阶段\s*\d|时段)', text, re.IGNORECASE):
        if len(re.findall(r'\b(P[0-9]|Phase\s*\d|M\d+|阶段\s*\d|Q[1-4])\b', text, re.IGNORECASE)) >= 3:
            return 'roadmap'
    # Pyramid / hierarchy keywords
    if re.search(r'(应用层|平台层|模型层|核心层|基础层|顶层|底层|hierarchy|pyramid)', text):
        return 'pyramid'
    # Principle keywords
    if re.search(r'(原则|准则|principle|guideline|法则|原理)', text):
        if len(re.findall(r'^\s*\d+[\.\)、]\s+', text, re.MULTILINE)) >= 3 and len(re.findall(r'^\s*[-*]\s+', text, re.MULTILINE)) >= 3:
            return 'principles'
    # Numbered list
    n_list = len(re.findall(r'^\s*\d+[\.\)、]\s+\S', text, re.MULTILINE))
    if n_list >= 4:
        return '6list'
    if n_list >= 3:
        return 'process'
    if '|' in text and re.search(r'^\s*\|', text, re.MULTILINE):
        return 'infographic'
    pct_count = len(re.findall(r'\d+(?:\.\d+)?\s*%', text))
    year_count = len(re.findall(r'\b20\d{2}\b', text))
    if pct_count >= 3 or year_count >= 4:
        return 'infographic'
    bullets = re.findall(r'^\s*[-*]\s+', text, re.MULTILINE)
    if 5 <= len(bullets) <= 6 and pct_count < 3:
        return 'takeaways'
    if 4 <= len(bullets) <= 6 and pct_count < 3:
        return '4card'
    if len(bullets) == 4 and pct_count < 3 and len(text) > 200:
        # 4 bullets, decent length → use 4-card for visual variety
        return '4card'
    if len(bullets) == 5 and pct_count < 3 and len(text) > 250:
        return '4card'
    # 3-4 bullets with a colon in each (label: body) → use principles
    if 3 <= len(bullets) <= 5 and sum(1 for b in bullets if '：' in b or ':' in b) >= 2:
        return 'principles'
    if len(bullets) == 3 and pct_count < 3:
        return '3card'
    if len(bullets) >= 4 and pct_count < 3 and any(k in text for k in ['能力', '特征', '特点', '属性', '功能']):
        return 'icongid'
    # Detect highlight pattern: "X 是 Y" with strong assertion
    if re.search(r'>\s*\*\*[^*]{20,}', text):
        return 'highlight'
    # Detect insight+visual: single big claim + supporting context
    if re.search(r'(建议|应|需要|必须|是[^。]{0,5}的|核心)', text) and pct_count == 1:
        return 'insight'
    # Numbered stat row: 3-4 numeric stats in a single chunk
    nums = re.findall(r'\b\d+(?:\.\d+)?\s*(?:%|亿|万|间|元|kg|km|亩|人|个)\b', text)
    if 3 <= len(nums) <= 5 and not re.search(r'^\s*[-*]\s+', text, re.MULTILINE):
        return 'stat_row'
    # Numbered hero (P1, P2, ...)
    if re.search(r'\bP[1-4]\b', text) and len(re.findall(r'\bP[1-4]\b', text)) >= 3:
        return 'numbered'
    return 'paragraph'

def extract_big_stat(chunk: str) -> tuple[str, str, str] | None:
    """Try to extract (big_value, unit, sub_label) from a chunk."""
    # Pattern: "key insight ... NN.N% 增长/同比/率..."
    m = re.search(r'(\d+(?:\.\d+)?)\s*%\s*([^,\n。.]{4,40})', chunk)
    if m:
        return m.group(1), '%', m.group(2).strip().rstrip('，,;；。.')[:40]
    # Try plain number with 万/亿/元
    m = re.search(r'([\d,]+(?:\.\d+)?)\s*(亿|万|元|间|个|家)\b\s*([^,\n。.]{0,40})', chunk)
    if m:
        v = m.group(1).replace(',', '') + ' ' + m.group(2)
        return v, '', m.group(3).strip()[:40]
    return None

def extract_compare_pairs(chunk: str) -> tuple[list[str], list[str], str, str] | None:
    """Try to extract old/new pairs from a chunk with '旧...新' or 'before/after'."""
    # Find first sentence with "旧...新"
    m = re.search(r'旧([^，。.!?\n]{2,30})新([^，。.!?\n]{2,40})', chunk)
    if m:
        old_label = m.group(1).strip()
        new_label = m.group(2).strip()
        # Find the rest of the paragraph
        rest = chunk[:m.end()] + chunk[m.end():]
        # Split into old items and new items by lines
        lines = [l.strip() for l in chunk.split('\n') if l.strip() and (l.startswith('-') or l.startswith('*') or re.match(r'^\d+\.', l))]
        old_items = lines[:len(lines)//2 + 1] if lines else []
        new_items = lines[len(lines)//2 + 1:] if lines else []
        old = [trim_bullet(re.sub(r'^[-\*\d\.\s]+', '', l), 70) for l in old_items]
        new = [trim_bullet(re.sub(r'^[-\*\d\.\s]+', '', l), 70) for l in new_items]
        if not old: old = ['传统方式']
        if not new: new = ['新方式']
        return old, new, old_label, new_label
    # English: before/after
    m = re.search(r'[Bb]efore\s+([^,\n.]{2,30})[,\s]+[Aa]fter\s+([^,\n.]{2,30})', chunk)
    if m:
        return ['传统方式'], ['新方式'], m.group(1).strip(), m.group(2).strip()
    return None

def extract_quote(chunk: str) -> tuple[str, str] | None:
    """Extract a pull quote: a > quoted line + author if present."""
    lines = chunk.split('\n')
    quote_lines = []
    author = ''
    for line in lines:
        s = line.strip()
        if s.startswith('>'):
            quote_lines.append(s.lstrip('>').strip())
        elif s.startswith('—') or s.startswith('- '):
            if not quote_lines:
                return None
            author = s.lstrip('—- ').strip()
    if quote_lines:
        quote = ' '.join(quote_lines).replace('**', '').strip()
        if len(quote) > 30:
            return quote, author or '—'
    return None

def extract_6list(chunk: str) -> list[tuple[str, str]] | None:
    """Extract (label, body) from 6+ numbered list items."""
    out = []
    for line in chunk.split('\n'):
        m = re.match(r'^\s*(\d+)[\.\)、]\s+(.+)', line)
        if m:
            n = int(m.group(1))
            rest = m.group(2).strip()
            # Split label from body at first 冒号 / 句号
            label_body = re.split(r'[：:。]', rest, maxsplit=1)
            if len(label_body) == 2:
                label, body = label_body[0].strip(), label_body[1].strip()
            else:
                # Take first 8 chars as label
                label = rest[:8]
                body = rest[8:].lstrip('，,;。 ')
            out.append((str(n), trim_bullet(label, 12), trim_bullet(body, 60)))
    if len(out) >= 4:
        return out
    return None

def extract_steps(chunk: str, max_n: int = 4) -> list[tuple[str, str]] | None:
    """Extract numbered steps as (label, body). 3-4 max."""
    out = []
    for line in chunk.split('\n'):
        m = re.match(r'^\s*(\d+)[\.\)、]\s+(.+)', line)
        if m:
            rest = m.group(2).strip().replace('**', '')
            # Label = first segment
            label = re.split(r'[，,。;；]', rest, maxsplit=1)[0]
            body = rest[len(label):].lstrip('，,;。; ')
            label = label.strip()[:20]
            body = body.strip()[:80]
            if label and body:
                out.append((label, body))
    if 3 <= len(out) <= max_n:
        return out
    return None

# Icon picker
ICON_BANK = {
    'data': 'chart', 'number': 'coins', 'percent': 'target',
    'team': 'users', 'people': 'users', 'company': 'building',
    'eco': 'leaf', 'forest': 'tree', 'tree': 'tree',
    'health': 'shield', 'medical': 'shield', 'check': 'check',
    'money': 'coins', 'revenue': 'coins', 'adr': 'coins',
    'guest': 'users', 'customer': 'users', 'room': 'building',
    'hotel': 'building', 'building': 'building', 'place': 'mountain',
    'forest': 'tree', 'park': 'tree', 'national': 'mountain',
    'global': 'globe', 'china': 'globe', 'city': 'mountain',
    'value': 'gem', 'quality': 'sparkle', 'key': 'key' if 'key' in svg_icon.__code__.co_consts else 'gem',
    'risk': 'shield', 'strategy': 'arrow', 'guide': 'ruler',
    'design': 'circle-dot', 'process': 'cog', 'flow': 'arrow',
    'time': 'wave', 'year': 'wave', 'trend': 'arrow',
    'step': 'arrow', 'phase': 'arrow', 'action': 'check',
    'index': 'ruler', 'note': 'book', 'info': 'circle-dot',
    'class': 'book', 'lesson': 'book', 'training': 'users',
    'transport': 'arrow', 'access': 'arrow', 'go': 'arrow',
    'rule': 'ruler', 'budget': 'coins', 'cost': 'coins',
    'plan': 'ruler', 'audit': 'shield', 'checklist': 'check',
    'manage': 'cog', 'teamwork': 'users', 'partner': 'users',
    'love': 'sparkle', 'highend': 'gem', 'service': 'sparkle',
    'skill': 'gem', 'brand': 'gem', 'reputation': 'gem',
    'culture': 'gem', 'safe': 'shield', 'inspire': 'rocket',
    'mission': 'compass', 'vision': 'compass', 'goal': 'target',
    'fire': 'flame', 'hot': 'flame', 'warm': 'flame',
    'plant': 'tree', 'flower': 'leaf', 'water': 'wave',
    'mountain': 'mountain', 'land': 'mountain', 'forest': 'tree',
    'airport': 'rocket', 'fly': 'rocket', 'speed': 'rocket',
}
def pick_icon(text: str) -> str:
    t = text.lower()
    for k, v in ICON_BANK.items():
        if k in t:
            return v
    return 'circle-dot'

# Section → keywords for icon selection
SECTION_ICONS = {
    'cover': 'gem', '01': 'gem', '02': 'book', '03': 'globe',
    '04': 'mountain', '05': 'target', '06': 'compass', '07': 'building',
    '08': 'arrow', '09': 'coins', '10': 'chart', '11': 'gem', '12': 'ruler',
    'A': 'book',
}

def emit_content_chunks(sec_data: list[dict], num: int, sec_key: str = '') -> tuple[list[str], int]:
    out = []
    sec_icon = SECTION_ICONS.get(sec_key.split('_')[-1] if '_' in sec_key else sec_key, 'circle-dot')
    h2_count = 0  # Track if this is the first h2 in section
    for sd in sec_data:
        kicker = sd['h2'] or deck_section_titles.get('?', '')
        content = sd['content']
        if not content.strip():
            continue
        # 1. H2 intro: kicker + first sentence lead + 3 supporting bullets
        # Only emit TABLEAI-INTRO for the FIRST h2 in section. For subsequent h2s,
        # generate a content slide instead (using h2 title as the page title).
        is_first_h2 = h2_count == 0
        h2_count += 1
        if sd['h2']:
            paras = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]
            lead = ''
            for p in paras:
                if not p.startswith('|') and not re.match(r'^\s*[-*\d]', p):
                    sentences = re.split(r'(?<=[。.!?])\s', p)
                    lead = trim_bullet((sentences[0] if sentences else p), 180)
                    break
            supporting = []
            for p in paras:
                lines = p.split('\n')
                for line in lines:
                    s = line.strip()
                    if s.startswith('- ') or s.startswith('* '):
                        supporting.append(trim_bullet(s[2:].lstrip(), 78))
                    elif re.match(r'^\d+\.\s', s):
                        supporting.append(trim_bullet(re.sub(r'^\d+\.\s+', '', s), 78))
                    if len(supporting) >= 3:
                        break
                if len(supporting) >= 3:
                    break
            if not supporting and paras:
                supporting = [trim_bullet(paras[0], 78)]
            if lead:
                # Only first h2 in section gets a TABLEAI-INTRO
                if is_first_h2:
                    # If lead contains a big number, use split-hero instead
                    if re.search(r'\d{2,3}(?:\.\d+)?\s*%', lead):
                        big = extract_big_stat(lead)
                        if big:
                            supporting_short = [s for s in supporting if s][:3]
                            out.append(slide_split_hero(num, clean_title(kicker, max_chars=40), clean_title(sd['h2'], max_chars=40), big[0], big[1], big[2] or '', [(s[:18], s[18:50] if len(s) > 18 else s[:30]) for s in supporting_short]))
                            num += 1
                            continue
                    out.append(slide_intro(num, clean_title(kicker, max_chars=40), clean_title(sd['h2'], max_chars=40), lead, supporting[:3]))
                    num += 1
                # For subsequent h2s, just remember the title for content slides
                # (we don't emit a separate intro page)
        # 2. Content chunks — use intent classifier
        for chunk in chunk_text(content, target_chars=240):
            if not chunk.strip():
                continue
            # Table detection
            if '|' in chunk and re.search(r'^\s*\|', chunk, re.MULTILINE):
                tbl = re.search(r'(\n?\|[^\n]+\n\|[^\n]+\n(?:\|[^\n]+\n?)+)', chunk, re.MULTILINE)
                if tbl:
                    headers, rows = parse_table_rows(tbl.group(1))
                    if headers and rows:
                        title = clean_title(chunk[:tbl.start()].strip().split('\n')[0][:80] if chunk[:tbl.start()].strip() else '', kicker) or f'{kicker} · 表'
                        # If single big number in chunk, use stat-hero instead
                        big = extract_big_stat(chunk[:tbl.start()])
                        if big and len(rows) >= 3:
                            # Use data callout for big stat + supporting table
                            facts = [(rows[i][0] if rows[i] else '', rows[i][1] if len(rows[i]) > 1 else '') for i in range(min(4, len(rows)))]
                            out.append(slide_data_callout(num, kicker, title, big[0], big[1], big[2] or kicker, facts))
                            num += 1
                        else:
                            out.append(slide_table(num, kicker, title, headers, rows))
                            num += 1
                        rest = chunk[tbl.end():].strip()
                        if rest:
                            bs = bullets_from(rest, max_n=3)
                            out.append(slide_paragraph(num, kicker, f'{title} · 解读', bs))
                            num += 1
                        continue
            # Intent-based routing
            intent = detect_intent(chunk)
            if intent == 'quote':
                q = extract_quote(chunk)
                if q:
                    out.append(slide_pull_quote(num, kicker, q[0], q[1]))
                    num += 1
                    continue
            if intent == 'stat':
                big = extract_big_stat(chunk)
                if big:
                    # Find sub context
                    sub_match = re.search(r'。\s*([^。\n]{10,80})', chunk)
                    sub = sub_match.group(1) if sub_match else ''
                    # Look for source
                    src_match = re.search(r'(来源|资料|GDP|统计|年报|公 告)[：:]?\s*([^。\n]{4,40})', chunk)
                    src = src_match.group(2).strip() if src_match else ''
                    title = clean_title(chunk.split('\n')[0][:80] if chunk.split('\n')[0] else '', kicker) or f'{kicker} · 关键数'
                    out.append(slide_stat_hero(num, kicker, title, big[0], big[1], sub, src))
                    num += 1
                    continue
            if intent == 'compare':
                comp = extract_compare_pairs(chunk)
                if comp:
                    old_items, new_items, old_lbl, new_lbl = comp
                    old_icon = pick_icon(old_lbl + ' 旧')
                    new_icon = pick_icon(new_lbl + ' 新')
                    # Find big stat for each side
                    old_big_m = re.search(r'(\d+(?:\.\d+)?)\s*%', old_items[0] if old_items else '')
                    new_big_m = re.search(r'(\d+(?:\.\d+)?)\s*%', new_items[0] if new_items else '')
                    old_big = old_big_m.group(1) if old_big_m else '—'
                    new_big = new_big_m.group(1) if new_big_m else '—'
                    out.append(slide_compare_rich(num, kicker, clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '对比', old_icon, old_lbl, old_big, '%', old_items, new_icon, new_lbl, new_big, '%', new_items))
                    num += 1
                    continue
            if intent == '3card':
                bullets = [b for b in re.findall(r'^\s*[-*]\s+(.+)', chunk, re.MULTILINE)]
                if len(bullets) >= 3:
                    # slide_3card expects (icon, big_value, lbl, body) — 4-tuple
                    cards = []
                    for b in bullets[:3]:
                        ic = pick_icon(b[:20])
                        # Split: first 12 chars = label, rest = body
                        lbl = trim_bullet(b, 12)
                        body = trim_bullet(b, 60)
                        cards.append((ic, '·', lbl, body))
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '三大要点'
                    out.append(slide_3card(num, kicker, title, cards))
                    num += 1
                    continue
            if intent == '4card':
                bullets = [b for b in re.findall(r'^\s*[-*]\s+(.+)', chunk, re.MULTILINE)]
                if len(bullets) >= 4:
                    # slide_quadrant expects (icon, label, body, accent)
                    quads = []
                    for i, b in enumerate(bullets[:4]):
                        ic = pick_icon(b[:20])
                        lbl = trim_bullet(b, 14)
                        body = trim_bullet(b, 60)
                        # Use accent on first quadrant
                        accent = 'var(--accent)' if i == 0 else 'var(--ink)'
                        quads.append((ic, lbl, body, accent))
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '四个关键'
                    out.append(slide_quadrant(num, kicker, title, quads))
                    num += 1
                    continue
            if intent == 'icongid':
                bullets = [b for b in re.findall(r'^\s*[-*]\s+(.+)', chunk, re.MULTILINE)]
                if len(bullets) >= 4:
                    # Convert to 6-cell or icon-grid
                    items = [(str(i+1), trim_bullet(b, 12), trim_bullet(b, 60)) for i, b in enumerate(bullets[:6])]
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '关键能力'
                    out.append(slide_icon_grid(num, kicker, title, items))
                    num += 1
                    continue
            if intent == 'takeaways':
                bullets = [b for b in re.findall(r'^\s*[-*]\s+(.+)', chunk, re.MULTILINE)]
                if len(bullets) >= 5:
                    items = [(trim_bullet(b, 22), trim_bullet(b, 70)) for b in bullets[:5]]
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '关键要点'
                    out.append(slide_takeaways(num, kicker, title, items))
                    num += 1
                    continue
            # ---- NEW: framework, principles, risk, roadmap, pyramid, highlight, etc.
            if intent == 'framework':
                # Try to extract 4 named layers
                layers = re.findall(r'(?:LAYER\s*\d+|第[一二三四]层|层级|架构)[：:\s]*([^\n.。]{4,40})', chunk)
                if len(layers) >= 2:
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '框架图'
                    # Use bullets after each layer for body
                    lines = chunk.split('\n')
                    boxes = []
                    for layer in layers[:4]:
                        # Find nearest line that contains body
                        body = layer[:60] or '—'
                        boxes.append((layer.strip(), body, 'var(--ink)'))
                    out.append(slide_framework(num, kicker, title, '概念架构', boxes))
                    num += 1
                    continue
            if intent == 'principles':
                bullets = re.findall(r'^\s*\d+[\.\)、]\s+(.+)', chunk, re.MULTILINE)
                if 3 <= len(bullets) <= 5:
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '核心原则'
                    principles = []
                    for i, b in enumerate(bullets[:5]):
                        ic = pick_icon(b[:20])
                        label = trim_bullet(b, 18)
                        body = trim_bullet(b, 70)
                        principles.append((ic, label, body))
                    out.append(slide_principles(num, kicker, title, principles))
                    num += 1
                    continue
            if intent == 'risk':
                bullets = re.findall(r'^\s*[-*]\s+(.+)', chunk, re.MULTILINE)
                if 2 <= len(bullets) <= 4:
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '风险评估'
                    risks = []
                    sev = ['high', 'medium', 'low']
                    for i, b in enumerate(bullets[:4]):
                        risks.append((trim_bullet(b, 22), '影响:中', '概率:中', sev[i % 3]))
                    out.append(slide_risk_matrix(num, kicker, title, risks))
                    num += 1
                    continue
            if intent == 'roadmap':
                # Look for date patterns
                milestones = re.findall(r'((?:Phase|阶段|M|里程碑|周|月|年)\s*\d+[周月年]?)\s*[:：、]?\s*([^\n.。]{4,40})', chunk)
                if len(milestones) >= 3:
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '路线图'
                    items = [(m[0].strip(), trim_bullet(m[1], 18), trim_bullet(m[1], 60)) for m in milestones[:5]]
                    out.append(slide_roadmap(num, kicker, title, items))
                    num += 1
                    continue
            if intent == 'pyramid':
                bullets = re.findall(r'^\s*[-*]\s+(.+)', chunk, re.MULTILINE)
                if 2 <= len(bullets) <= 3:
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '层级模型'
                    levels = [(trim_bullet(b, 16), trim_bullet(b, 50)) for b in bullets[:3]]
                    out.append(slide_pyramid(num, kicker, title, levels))
                    num += 1
                    continue
            if intent == 'highlight':
                # Extract first > quoted line
                m = re.search(r'>\s*\*\*([^*]+)\*\*', chunk)
                if m:
                    quote = m.group(1).strip()[:100]
                    bullets = re.findall(r'^\s*[-*]\s+(.+)', chunk, re.MULTILINE)
                    sub = ' '.join(bullets[:2])[:200] if bullets else ''
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '核心洞察'
                    out.append(slide_highlight(num, kicker, title, quote, sub, 'sparkle'))
                    num += 1
                    continue
            if intent == 'insight':
                bullets = re.findall(r'^\s*[-*]\s+(.+)', chunk, re.MULTILINE)
                if bullets:
                    insight = trim_bullet(chunk.split('\n')[0] if chunk.split('\n')[0] else '', 100) or '关键洞察'
                    sub = ' '.join(bullets[:2])[:200]
                    visuals = [(pick_icon(b[:20]), trim_bullet(b, 16), trim_bullet(b, 50)) for b in bullets[:3]]
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '洞察'
                    out.append(slide_insight_visual(num, kicker, title, insight, sub, visuals))
                    num += 1
                    continue
            if intent == 'stat_row':
                nums = re.findall(r'(\d+(?:\.\d+)?)\s*(%|亿|万|间|元|kg|km|亩|人|个|家)([^,。\n]{0,30})', chunk)
                if 3 <= len(nums) <= 5:
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '关键数据'
                    stats = []
                    for n, unit, lbl in nums[:5]:
                        stats.append((n, unit, trim_bullet(lbl, 18) or '—', ''))
                    if len(stats) >= 3:
                        out.append(slide_stat_row(num, kicker, title, stats))
                        num += 1
                        continue
            if intent == 'numbered':
                m = re.findall(r'\bP([1-9])\b[^\n]{0,80}', chunk)
                if 3 <= len(m) <= 5:
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '关键节点'
                    items = []
                    for i, p in enumerate(m[:5], 1):
                        # Get associated text
                        bullet_match = re.search(rf'P{p}[、，：:]?\s*([^\n.。]{{6,60}})', chunk)
                        body = bullet_match.group(1).strip() if bullet_match else f'第{p}项'
                        items.append((f'P{p}', trim_bullet(body[:18], 18), trim_bullet(body, 70)))
                    out.append(slide_numbered_hero(num, kicker, title, items))
                    num += 1
                    continue
            if intent == '3way':
                m = re.search(r'前者([^，。\n]{4,40})后者([^，。\n]{4,40})', chunk)
                if m:
                    old_lbl = m.group(1).strip()
                    new_lbl = m.group(2).strip()
                    bullets = re.findall(r'^\s*[-*]\s+(.+)', chunk, re.MULTILINE)
                    if len(bullets) >= 3:
                        options = [
                            (old_lbl, bullets[:len(bullets)//3], '—'),
                            ('新模式', bullets[len(bullets)//3:2*len(bullets)//3], '推荐'),
                            (new_lbl, bullets[2*len(bullets)//3:], '—'),
                        ]
                        title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '三种选择'
                        out.append(slide_compare_matrix(num, kicker, title, options))
                        num += 1
                        continue
            if intent == '6list':
                items = extract_6list(chunk)
                if items:
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '六个关键'
                    out.append(slide_six_cells(num, kicker, title, items))
                    num += 1
                    continue
            if intent == 'process':
                steps = extract_steps(chunk, max_n=4)
                if steps:
                    title = clean_title(chunk.split('\n')[0][:60] if chunk.split('\n')[0] else '', kicker) or '流程'
                    out.append(slide_ladder(num, kicker, title, steps))
                    num += 1
                    continue
            # Infographic detection
            kind = detect_infographic_kind(chunk)
            if kind == 'hbar':
                data = extract_hbar_data(chunk)
                if len(data) >= 2:
                    title = clean_title(chunk.split('\n')[0][:80] if chunk.split('\n')[0] else '', kicker) or f'{kicker} · 比例'
                    out.append(slide_hbar(num, kicker, title, data, '%'))
                    num += 1
                    continue
            if kind == 'vbar':
                data = extract_hbar_data(chunk)
                if len(data) >= 3:
                    title = clean_title(chunk.split('\n')[0][:80] if chunk.split('\n')[0] else '', kicker) or f'{kicker} · 对比'
                    out.append(slide_vbar(num, kicker, title, data, '%'))
                    num += 1
                    continue
            if kind == 'timeline':
                data = extract_year_data(chunk)
                if len(data) >= 3:
                    title = clean_title(chunk.split('\n')[0][:80] if chunk.split('\n')[0] else '', kicker) or f'{kicker} · 时间线'
                    out.append(slide_timeline(num, kicker, title, data))
                    num += 1
                    continue
            if kind == 'process':
                steps = extract_process_steps(chunk)
                if len(steps) >= 3:
                    title = clean_title(chunk.split('\n')[0][:80] if chunk.split('\n')[0] else '', kicker) or f'{kicker} · 流程'
                    out.append(slide_process(num, kicker, title, steps))
                    num += 1
                    continue
            # Default: paragraph with capped bullets — but first try to enrich
            bullets = bullets_from(chunk)
            if len(bullets) >= 1:
                title = clean_title(chunk.split('\n')[0][:80] if chunk.split('\n')[0] else '', kicker) or kicker
                # If bullet is `---` or `### xxx` (sub-heading), use highlight
                if len(bullets) == 1 and (bullets[0].strip() in ('---', '') or bullets[0].startswith('###')):
                    # Skip empty / separator slides entirely
                    continue
                if len(bullets) == 1 and len(bullets[0]) > 30:
                    # Use highlight: short title + big quote-like text
                    out.append(slide_highlight(num, kicker, title, bullets[0][:120], '', 'circle-dot'))
                    num += 1
                elif len(bullets) == 2 and all('**' not in b for b in bullets):
                    # 2 columns = compare rich
                    l1 = trim_bullet(bullets[0], 50)
                    l2 = trim_bullet(bullets[1], 50)
                    out.append(slide_compare_rich(num, kicker, title, pick_icon(l1), l1.split('：')[0][:8], 'A', '', [l1], pick_icon(l2), l2.split('：')[0][:8], 'B', '', [l2]))
                    num += 1
                elif len(bullets) == 3 and all('**' not in b for b in bullets):
                    # 3 bullets → 3-card highlight
                    cards = []
                    for b in bullets[:3]:
                        ic = pick_icon(b[:20])
                        lbl = trim_bullet(b, 14)
                        body = trim_bullet(b, 60)
                        cards.append((ic, '·', lbl, body))
                    out.append(slide_3card(num, kicker, title, cards))
                    num += 1
                elif len(bullets) == 4 and all('**' not in b for b in bullets):
                    # 4 bullets → 4-card quadrant
                    quads = []
                    for i, b in enumerate(bullets[:4]):
                        ic = pick_icon(b[:20])
                        lbl = trim_bullet(b, 14)
                        body = trim_bullet(b, 60)
                        accent = 'var(--accent)' if i == 0 else 'var(--ink)'
                        quads.append((ic, lbl, body, accent))
                    out.append(slide_quadrant(num, kicker, title, quads))
                    num += 1
                elif len(bullets) >= 5 and all('**' not in b for b in bullets):
                    # 5+ bullets → icon grid
                    items = [(str(i+1), trim_bullet(b, 14), trim_bullet(b, 60)) for i, b in enumerate(bullets[:6])]
                    out.append(slide_icon_grid(num, kicker, title, items))
                    num += 1
                else:
                    out.append(slide_paragraph(num, kicker, title, bullets))
                    num += 1
            else:
                # Truly empty chunk — skip
                continue
    return out, num

# ---- Build deck ----
deck_blocks = [slide_cover(), slide_toc()]
nxt = 3
for key in deck_section_order:
    sec_data = grouped.get(key, [])
    if not sec_data:
        continue
    if key != '00_cover':  # cover already emitted
        sec_blocks, nxt = emit_section(key, sec_data, nxt)
        deck_blocks.extend(sec_blocks)
        content_blocks, nxt = emit_content_chunks(sec_data, nxt, sec_key=key)
        deck_blocks.extend(content_blocks)
        if len(content_blocks) > 4:
            deck_blocks.append(slide_section_close())
            nxt += 1
deck_blocks.append(slide_closing())

# ---- Compose final HTML with section nav + search + thumbnail grid ----
# Compute section anchors (sec-01..sec-12, sec-a)
SECTIONS_NAV = [
    ('00', 'cover', '封面'),
    ('01', 'sec-01', '行政综述'),
    ('02', 'sec-02', '前言'),
    ('03', 'sec-03', '宏观'),
    ('04', 'sec-04', '地块'),
    ('05', 'sec-05', '供需'),
    ('06', 'sec-06', '定位'),
    ('07', 'sec-07', '设施'),
    ('08', 'sec-08', '动线'),
    ('09', 'sec-09', '现金流'),
    ('10', 'sec-10', '回报'),
    ('11', 'sec-11', '品牌'),
    ('12', 'sec-12', '落地'),
    ('A', 'sec-a', '附件'),
]

nav_items_html = '\n'.join(
    f'<a href="#{anchor}" data-sec-anchor="{anchor}" style="display:flex;gap:.6em;align-items:center;padding:.4em .7em;font-family:var(--sans-tab);font-weight:600;font-size:11px;letter-spacing:.06em;color:var(--text-primary);text-decoration:none;border-radius:3px;cursor:pointer;transition:background .15s ease"><span style="color:var(--accent);font-weight:700">{n}</span><span style="color:var(--text-helper);font-weight:500">{esc(t)}</span></a>'
    for n, anchor, t in SECTIONS_NAV
)

# Find anchors to inject into CSS section
last_style_close = html.rfind('</style>')
if last_style_close == -1:
    raise SystemExit('No </style> in template')

# Find <div id="nav">
nav_div_open = html.find('<div id="nav">')
if nav_div_open == -1:
    raise SystemExit('No <div id="nav"> in template')

# Find the LAST closing </div> right before <div id="nav">. This closes #deck.
# Everything from last_style_close to that </div> contains the Q3 demo deck
# (lines 895-1908 in template). We discard it to avoid leftover.
deck_close_idx = html.rfind('</div>', last_style_close, nav_div_open)
if deck_close_idx == -1:
    raise SystemExit('No </div> between last </style> and <div id="nav">')

# CSS overrides — vertical-scroll deck with arrow-key navigation, plus
# fixed index panel, section-grouped thumbnail grid, and global search.
NAV_CSS_BLOCK = '''<style id="section-nav-css">
  html { scroll-behavior: smooth; }
  body { overflow-x: hidden; overflow-y: auto !important; }
  /* Kill horizontal swipe behavior — use vertical scroll instead */
  .slide { height: auto !important; min-height: 100vh; flex: 0 0 auto !important; display: block !important; padding-bottom: 2vh; }
  .canvas-card { min-height: 100vh; height: auto !important; }
  #deck { width: 100% !important; height: auto !important; display: block !important; transform: none !important; transition: none !important; }
  #nav { display: none !important; }

  /* ============== Fixed right-side section index panel (collapsible) ============== */
  #index-panel {
    position: fixed; right: 0; top: 0; bottom: 0;
    width: 360px; z-index: 9990;
    background: var(--paper);
    border-left: 1px solid var(--border-subtle);
    box-shadow: -4px 0 24px rgba(10, 22, 38, 0.08);
    display: flex; flex-direction: column;
    transform: translateX(100%);
    transition: transform .25s ease;
  }
  #index-panel.open { transform: translateX(0); }
  #index-panel-header {
    padding: 1.6vh 1.4vw;
    border-bottom: 1px solid var(--border-subtle);
    flex: 0 0 auto;
  }
  #index-panel-header h2 {
    font-family: var(--sans-tab), var(--sans-zh);
    font-weight: 700; font-size: 16px;
    color: var(--ink);
    margin: 0 0 .4em 0;
    display: flex; justify-content: space-between; align-items: center;
  }
  #index-panel-header h2 button {
    background: transparent; border: 0;
    color: var(--text-helper);
    font-size: 18px; cursor: pointer;
    padding: 0; line-height: 1;
  }
  #index-search {
    width: 100%;
    padding: .8em 1em;
    font-family: var(--sans-tab); font-size: 13px;
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    outline: none;
    color: var(--ink); background: var(--grey-1);
  }
  #index-search:focus { background: var(--paper); border-color: var(--accent); }
  #index-list {
    flex: 1; overflow-y: auto;
    padding: 1vh 0;
  }
  .index-section-header {
    padding: 1.4vh 1.4vw .6vh;
    font-family: var(--sans-tab); font-weight: 700; font-size: 11px;
    color: var(--accent); letter-spacing: .12em;
    text-transform: uppercase;
    border-top: 1px solid var(--border-subtle);
    margin-top: 1vh;
  }
  .index-section-header:first-child { border-top: 0; margin-top: 0; }
  .index-item {
    display: flex; gap: .8em; align-items: baseline;
    padding: .7vh 1.4vw;
    font-family: var(--sans-tab), var(--sans-zh);
    font-size: 12px;
    color: var(--text-primary);
    text-decoration: none;
    cursor: pointer;
    transition: background .1s ease;
    line-height: 1.35;
  }
  .index-item:hover { background: var(--gold-mist); }
  .index-item .num {
    font-family: var(--mono); font-weight: 700; font-size: 10px;
    color: var(--accent); flex: 0 0 auto;
  }
  .index-item .title {
    flex: 1; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
  }
  .index-item.hidden { display: none; }
  #index-list .empty {
    padding: 2vh 1.4vw; color: var(--text-helper);
    font-style: italic; font-size: 12px;
  }
  /* When panel is open, push deck content left */
  body.index-open { padding-right: 360px; }

  /* ============== Floating top-right action buttons ============== */
  .floating-btn {
    position: fixed; z-index: 9991;
    width: 40px; height: 40px;
    background: var(--paper); color: var(--ink);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    font-family: var(--sans-tab); font-weight: 700; font-size: 16px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 8px rgba(10, 22, 38, 0.08);
    transition: background .15s ease, transform .15s ease;
  }
  .floating-btn:hover { background: var(--gold-mist); transform: translateY(-1px); }
  .floating-btn.active { background: var(--ink); color: var(--paper); }
  #btn-index { top: 14px; right: 14px; }
  #btn-thumbs { top: 14px; right: 60px; }
  #btn-search { top: 14px; right: 106px; }
  #btn-top   { top: 14px; right: 152px; }
  #btn-top:hover { background: var(--gold-mist); }

  /* ============== Slide counter (top-left, prominent) + section badge ============== */
  #slide-counter {
    position: fixed; top: 14px; left: 14px; z-index: 9991;
    background: var(--ink); color: var(--paper);
    padding: 1em 1.6em;
    border-radius: 8px;
    font-family: var(--sans-tab);
    box-shadow: 0 4px 16px rgba(10, 22, 38, 0.18);
    display: flex; align-items: baseline; gap: .8em;
    min-width: 14em;
  }
  #slide-counter .cur {
    color: var(--accent-bright);
    font-family: var(--mono);
    font-size: 24px;
    font-weight: 700;
    line-height: 1;
  }
  #slide-counter .sep { color: rgba(255,255,255,.4); font-size: 18px; }
  #slide-counter .total {
    color: rgba(255,255,255,.85);
    font-size: 14px;
    font-weight: 600;
  }
  #slide-counter .label { color: rgba(255,255,255,.5); font-size: 11px; margin-left: .4em; }

  /* Section name badge — below counter, shows current section */
  #section-badge {
    position: fixed; top: 70px; left: 14px; z-index: 9991;
    background: var(--paper); color: var(--ink);
    border: 1px solid var(--border-subtle);
    padding: .6em 1.2em;
    border-radius: 6px;
    font-family: var(--sans-tab); font-weight: 600;
    font-size: 12px; letter-spacing: .04em;
    box-shadow: 0 2px 8px rgba(10, 22, 38, 0.08);
    display: none; /* shown by JS when scrolled */
  }
  #section-badge .num { color: var(--accent); font-weight: 700; margin-right: .6em; }

  /* ============== Search modal (floating, fullscreen-friendly) ============== */
  #search-modal {
    position: fixed; inset: 60px 14px 14px 14px;
    background: var(--paper);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    box-shadow: 0 16px 64px rgba(10, 22, 38, 0.18);
    z-index: 10000;
    display: none; flex-direction: column;
    overflow: hidden;
  }
  #search-modal.open { display: flex; }
  #search-modal-header {
    padding: 1.6vh 1.6vw;
    border-bottom: 1px solid var(--border-subtle);
    display: flex; gap: 1em; align-items: center;
  }
  #search-input {
    flex: 1;
    padding: .8em 1em;
    font-family: var(--sans-tab);
    font-size: 18px;
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    outline: none;
    color: var(--ink); background: var(--paper);
  }
  #search-input:focus { border-color: var(--accent); }
  #search-modal-meta {
    font-family: var(--mono); font-size: 11px;
    color: var(--text-helper);
    letter-spacing: .04em;
  }
  #search-results {
    overflow-y: auto;
    flex: 1;
    padding: 0;
  }
  .search-hit {
    padding: 1.4vh 1.6vw;
    border-top: 1px solid var(--border-subtle);
    cursor: pointer;
    font-family: var(--sans-tab), var(--sans-zh);
    font-size: 13px;
    line-height: 1.45;
    color: var(--text-primary);
    display: grid;
    grid-template-columns: 5em 1fr auto;
    gap: 1vw;
    align-items: baseline;
  }
  .search-hit:hover { background: var(--gold-mist); }
  .search-hit .hit-num { font-family: var(--mono); font-weight: 700; color: var(--accent); }
  .search-hit .hit-section { font-family: var(--mono); font-size: 10px; color: var(--text-helper); letter-spacing: .04em; }
  .search-hit .hit-snippet { grid-column: 1 / -1; font-size: 11px; color: var(--text-helper); margin-top: .4em; line-height: 1.45; }
  .search-hit mark { background: var(--accent-bright); color: var(--ink); padding: 0 2px; border-radius: 2px; }
  #search-empty { padding: 4vh 1.6vw; color: var(--text-helper); font-style: italic; text-align: center; }

  /* ============== Thumbnail grid (fullscreen) ============== */
  #thumb-grid {
    position: fixed; inset: 0;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(12px);
    z-index: 10002;
    display: none;
    overflow-y: auto;
    padding: 7vh 4vw 4vh;
  }
  #thumb-grid.open { display: block; }
  #thumb-grid-header {
    position: sticky; top: 0;
    display: flex; justify-content: space-between; align-items: center;
    padding: 1.4vh 0 2vh;
    margin-bottom: 2.4vh;
    border-bottom: 1px solid var(--border-subtle);
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    z-index: 10;
  }
  #thumb-grid-header h2 { font-family: var(--sans-tab), var(--sans-zh); font-weight: 700; font-size: 22px; }
  #thumb-grid-header .meta { font-family: var(--mono); font-size: 11px; color: var(--text-helper); margin-top: .2em; }
  #thumb-grid-close {
    background: var(--ink); color: var(--paper);
    border: 0; border-radius: 6px;
    padding: .8em 1.4em;
    font-family: var(--sans-tab); font-weight: 600; font-size: 14px;
    cursor: pointer;
  }
  #thumb-grid-close:hover { background: var(--accent); }

  /* Section headers inside thumbnail grid */
  .thumb-section-block {
    margin-bottom: 2.4vh;
  }
  .thumb-section-title {
    font-family: var(--sans-tab), var(--sans-zh);
    font-weight: 700; font-size: 16px;
    color: var(--ink);
    padding: 1.2vh 0;
    border-bottom: 2px solid var(--ink);
    margin-bottom: 1.4vh;
    display: flex; justify-content: space-between; align-items: baseline;
  }
  .thumb-section-title .count {
    font-family: var(--mono); font-size: 11px;
    color: var(--text-helper); font-weight: 500;
  }
  .thumb-section-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.4vh 1vw;
  }
  .thumb-cell {
    cursor: pointer;
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    overflow: hidden;
    background: var(--paper);
    transition: transform .15s ease, border-color .15s ease, box-shadow .15s ease;
    position: relative;
  }
  .thumb-cell:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
    box-shadow: 0 6px 20px rgba(10, 22, 38, 0.12);
  }
  .thumb-cell .thumb-num {
    position: absolute; top: 6px; left: 6px;
    background: var(--ink); color: var(--paper);
    font-family: var(--mono); font-size: 10px; font-weight: 700;
    padding: 3px 7px;
    border-radius: 3px;
    z-index: 3;
  }
  .thumb-cell .thumb-section-tag {
    position: absolute; top: 6px; right: 6px;
    background: var(--gold-mist); color: var(--accent);
    font-family: var(--mono); font-size: 9px; font-weight: 600;
    padding: 3px 7px;
    border-radius: 3px;
    z-index: 3;
  }
  .thumb-cell .thumb-wrap {
    position: relative;
    aspect-ratio: 16/9;
    overflow: hidden;
    background: var(--grey-1);
  }
  .thumb-cell .thumb-clone {
    width: 100%; height: 100%;
    transform-origin: top left;
    pointer-events: none;
  }
  .thumb-cell .thumb-title {
    padding: .8em 1em;
    font-family: var(--sans-tab), var(--sans-zh);
    font-size: 11px; font-weight: 600;
    color: var(--text-primary);
    line-height: 1.4;
    border-top: 1px solid var(--border-subtle);
    background: var(--paper);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    min-height: 3em;
  }

  @media (max-width: 900px) {
    #index-panel, #btn-index, #btn-thumbs, #btn-search, #slide-counter { display: none !important; }
    .floating-btn { display: none !important; }
  }
</style>
'''

# Build search index from slide blocks
# For each slide: extract title, section, text for search
search_index_js = []
for i, block in enumerate(deck_blocks, 1):
    title_match = re.search(r'<h[1-3][^>]*>(.*?)</h[1-3]>', block, re.DOTALL)
    title = ''
    if title_match:
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
    sec_match = re.search(r'data-layout="TABLEAI-SECTION-(\w+)"', block)
    section = sec_match.group(1) if sec_match else ('cover' if i == 1 else '')
    text = re.sub(r'<[^>]+>', ' ', block)
    text = re.sub(r'\s+', ' ', text).strip()
    # Fallback title from chrome-min left text
    chrome_match = re.search(r'<div class="l">([^<]+)</div>', block)
    if chrome_match and (not title or len(title) < 4):
        title = chrome_match.group(1).strip()[:60]
    if text:
        search_index_js.append({
            'i': i,
            'title': clean_title(title) if title else '',
            'section': section,
            'text': text[:600]
        })

search_index_json = str(search_index_js).replace("'", "\\'").replace('"', "'")
section_titles_js = str(deck_section_titles).replace("'", "\\'").replace('"', "'")

# Build index list HTML — grouped by section
index_list_items = []
current_section = None
for s in search_index_js:
    sec = s['section']
    if sec != current_section:
        sec_title = deck_section_titles.get(sec, sec) if sec in deck_section_titles else ('封面' if sec == 'cover' else sec)
        index_list_items.append(f'<div class="index-section-header" data-section="{sec}">{sec} · {sec_title}</div>')
        current_section = sec
    title = (s['title'] or ('第 ' + str(s['i']) + ' 页'))[:60]
    index_list_items.append(
        f'<a class="index-item" data-slide-idx="{s["i"]}" data-section="{sec}" href="#slide-{s["i"]}">'
        f'<span class="num">P{str(s["i"]).zfill(3)}</span>'
        f'<span class="title">{title}</span>'
        f'</a>'
    )
index_list_html = '\n'.join(index_list_items)

NAV_HTML_BLOCK = f'''
<div id="slide-counter">
  <span class="cur" id="cur-num">P001</span>
  <span class="sep">/</span>
  <span class="total">{len(deck_blocks)}</span>
  <span class="label">页</span>
</div>
<div id="section-badge"><span class="num" id="badge-num">—</span><span id="badge-name">—</span></div>
<noscript><div style="position:fixed;top:14px;left:50%;transform:translateX(-50%);background:var(--accent);color:var(--paper);padding:1em 1.6em;border-radius:8px;font-family:var(--sans-tab);font-weight:600;font-size:13px;z-index:99999">本 deck 需要启用 JavaScript · This deck requires JavaScript</div></noscript>
<div id="deck-fail-safe" style="position:fixed;top:14px;right:50%;z-index:99998;background:var(--ink);color:var(--paper);padding:1em 1.4em;border-radius:8px;font-family:var(--sans-tab);font-size:11px;letter-spacing:.04em;display:none">
  ⚠️ JS 错误 · {len(deck_blocks)} 张 PPT 等待加载
</div>
<button class="floating-btn" id="btn-top" title="回到顶部 (Home)">↑</button>
<button class="floating-btn" id="btn-search" title="全局搜索 (Ctrl/Cmd+K)">⌕</button>
<button class="floating-btn" id="btn-thumbs" title="缩略图 (G)">▦</button>
<button class="floating-btn" id="btn-index" title="目录 (I)">☰</button>

<aside id="index-panel" aria-label="目录">
  <div id="index-panel-header">
    <h2>
      <span>目录 · INDEX</span>
      <button id="index-close" title="关闭 (I)">×</button>
    </h2>
    <input id="index-search" type="text" placeholder="筛选目录 · 例:沉香 / 客房" autocomplete="off">
  </div>
  <div id="index-list">
    {index_list_html}
  </div>
</aside>

<div id="search-modal">
  <div id="search-modal-header">
    <input id="search-input" type="text" placeholder="全文搜索 · 例:沉香 / NRR / 客房 / 点状供地" autocomplete="off" spellcheck="false">
    <span id="search-modal-meta">0 / 0</span>
  </div>
  <div id="search-results"></div>
</div>

<div id="thumb-grid">
  <div id="thumb-grid-header">
    <div>
      <h2>缩略图索引</h2>
      <div class="meta">全 {len(deck_blocks)} 张 · 按章节分组 · 点击跳转</div>
    </div>
    <button id="thumb-grid-close">关闭 (Esc / G)</button>
  </div>
  <div id="thumb-cells"></div>
</div>

<script>
(function() {{
  var SLIDES = {search_index_json};
  (function() {{
    var counts = {{}};
    for (var _i = 0; _i < SLIDES.length; _i++) {{
      var _s = SLIDES[_i].section;
      counts[_s] = (counts[_s] || 0) + 1;
    }}
    console.log('[deck] Loaded ' + SLIDES.length + ' slides across ' + Object.keys(counts).length + ' sections');
  }})();
  var SECTION_TITLES = {section_titles_js};
  var SLIDES_HTML = null;
  var totalSlides = SLIDES.length;

  // ---- Assign id="slide-N" to each slide for in-page anchor jumps ----
  var slideEls = document.querySelectorAll('.slide');
  console.log('[deck] Found', slideEls.length, '.slide elements in DOM');
  for (var i = 0; i < slideEls.length; i++) {{
    slideEls[i].id = 'slide-' + (i + 1);
  }}
  // Show deck-fail-safe if no slides after 1 second
  if (slideEls.length === 0) {{
    var warn = document.createElement('div');
    warn.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:var(--accent);color:var(--paper);padding:3em;border-radius:8px;font-family:var(--sans-tab);font-size:24px;z-index:99999';
    warn.innerHTML = '⚠️ 加载失败: 未检测到任何 slide 元素<br><br>请刷新页面 (Cmd+R) 或清除浏览器缓存';
    document.body.appendChild(warn);
  }}
  // If after 3 seconds the slides have no IDs (JS may have failed), show fail-safe
  setTimeout(function() {{
    var stillNoId = document.querySelector('.slide:not([id])');
    if (stillNoId) {{
      document.getElementById('deck-fail-safe').style.display = 'block';
    }}
  }}, 3000);

  // ---- Anchor link click handler ----
  document.addEventListener('click', function(e) {{
    var t = e.target.closest('a[href^="#slide-"], a[data-sec-anchor], a[href^="#sec-"]');
    if (!t) return;
    e.preventDefault();
    var href = t.getAttribute('href');
    if (href && href.indexOf('#sec-') === 0) {{
      var id = t.getAttribute('data-sec-anchor') || href.slice(1);
      var target = document.getElementById(id);
      if (target) {{
        closeIndexPanel();
        target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}
    }} else if (href) {{
      var id = href.slice(1);
      var target = document.getElementById(id);
      if (target) {{
        closeIndexPanel();
        closeSearch();
        target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}
    }}
  }});

  // ---- Slide counter + active index highlight ----
  var counterEl = document.getElementById('cur-num');
  var badgeEl = document.getElementById('section-badge');
  var badgeNumEl = document.getElementById('badge-num');
  var badgeNameEl = document.getElementById('badge-name');
  // Pre-compute section ranges
  var SECTION_RANGES = {{}};
  var lastSection = '';
  var lastSectionStart = 1;
  for (var i = 0; i < SLIDES.length; i++) {{
    var sec = SLIDES[i].section || 'cover';
    if (sec !== lastSection && lastSection !== '') {{
      SECTION_RANGES[lastSection] = {{start: lastSectionStart, end: i}};
      lastSectionStart = i + 1;
    }}
    if (sec !== lastSection) lastSection = sec;
  }}
  SECTION_RANGES[lastSection] = {{start: lastSectionStart, end: SLIDES.length}};

  function updateCounter() {{
    var scrollY = window.scrollY + window.innerHeight * 0.3;
    var cur = 1;
    for (var k = 0; k < slideEls.length; k++) {{
      if (slideEls[k].offsetTop <= scrollY) cur = k + 1;
    }}
    counterEl.textContent = 'P' + String(cur).padStart(3, '0');
    // Update section badge
    var curSlide = SLIDES[cur - 1];
    if (curSlide) {{
      var sec = curSlide.section || 'cover';
      var range = SECTION_RANGES[sec];
      var secName = sec === 'cover' ? '封面' : (SECTION_TITLES[sec] || sec);
      var posInSec = (range ? cur - range.start + 1 : 1);
      var totalInSec = (range ? range.end - range.start + 1 : 1);
      if (sec !== 'cover') {{
        badgeEl.style.display = 'flex';
        badgeEl.style.alignItems = 'center';
        badgeEl.style.gap = '.4em';
        badgeNumEl.textContent = sec + ' · P' + String(posInSec).padStart(3, '0') + ' / ' + totalInSec;
        badgeNameEl.textContent = secName;
      }} else {{
        badgeEl.style.display = 'none';
      }}
    }}
    document.querySelectorAll('.index-item').forEach(function(el) {{
      var idx = parseInt(el.getAttribute('data-slide-idx'), 10);
      if (idx === cur) {{
        el.style.background = 'var(--gold-mist)';
        el.style.borderLeft = '3px solid var(--accent)';
      }} else {{
        el.style.background = '';
        el.style.borderLeft = '3px solid transparent';
      }}
    }});
  }}
  var scrollTimer = null;
  addEventListener('scroll', function() {{
    if (scrollTimer) cancelAnimationFrame(scrollTimer);
    scrollTimer = requestAnimationFrame(updateCounter);
  }});
  updateCounter();

  // ---- Index panel (right side) ----
  var indexPanel = document.getElementById('index-panel');
  var body = document.body;
  function openIndexPanel() {{
    indexPanel.classList.add('open');
    body.classList.add('index-open');
    document.getElementById('btn-index').classList.add('active');
    setTimeout(function() {{ document.getElementById('index-search').focus(); }}, 100);
  }}
  function closeIndexPanel() {{
    indexPanel.classList.remove('open');
    body.classList.remove('index-open');
    document.getElementById('btn-index').classList.remove('active');
  }}
  function toggleIndexPanel() {{
    if (indexPanel.classList.contains('open')) closeIndexPanel(); else openIndexPanel();
  }}
  document.getElementById('btn-index').addEventListener('click', toggleIndexPanel);
  document.getElementById('index-close').addEventListener('click', closeIndexPanel);

  // ---- Index search filter ----
  document.getElementById('index-search').addEventListener('input', function(e) {{
    var q = e.target.value.trim().toLowerCase();
    var items = document.querySelectorAll('.index-item');
    items.forEach(function(el) {{
      el.classList.toggle('hidden', q && el.textContent.toLowerCase().indexOf(q) === -1);
    }});
    document.querySelectorAll('.index-section-header').forEach(function(s) {{
      var next = s.nextElementSibling;
      var any = false;
      while (next && !next.classList.contains('index-section-header')) {{
        if (!next.classList.contains('hidden')) {{ any = true; break; }}
        next = next.nextElementSibling;
      }}
      s.classList.toggle('hidden', q && !any);
    }});
  }});

  // ---- Global search modal ----
  var searchModal = document.getElementById('search-modal');
  var searchInput = document.getElementById('search-input');
  var searchResults = document.getElementById('search-results');
  var searchMeta = document.getElementById('search-modal-meta');
  function openSearch() {{
    searchModal.classList.add('open');
    setTimeout(function() {{ searchInput.focus(); searchInput.select(); }}, 50);
  }}
  function closeSearch() {{
    searchModal.classList.remove('open');
    searchInput.value = '';
    searchResults.innerHTML = '';
    searchMeta.textContent = '0 / 0';
  }}
  function doSearch() {{
    var q = searchInput.value.trim();
    if (!q) {{ searchResults.innerHTML = ''; searchMeta.textContent = '0 / 0'; return; }}
    var qLower = q.toLowerCase();
    var hits = [];
    for (var i = 0; i < SLIDES.length; i++) {{
      var s = SLIDES[i];
      var titleMatch = s.title && s.title.toLowerCase().indexOf(qLower) >= 0;
      var textMatch = s.text && s.text.toLowerCase().indexOf(qLower) >= 0;
      if (titleMatch || textMatch) {{
        hits.push(s);
        if (hits.length >= 80) break;
      }}
    }}
    searchMeta.textContent = hits.length + ' / ' + SLIDES.length;
    if (hits.length === 0) {{
      searchResults.innerHTML = '<div id="search-empty">无结果 — 试试更短的关键词<br>(例:沉香 / 体检 / 客房 / ADR / NOI)</div>';
      return;
    }}
    var re = new RegExp('(' + q.replace(/[.*+?^$()|[\\]\\\\]{{}}/g, '\\\\$&') + ')', 'gi');
    var html = '';
    for (var j = 0; j < hits.length; j++) {{
      var h = hits[j];
      var secName = h.section === 'cover' ? '封面' : (SECTION_TITLES[h.section] || h.section);
      var pos = h.text.toLowerCase().indexOf(qLower);
      var start = Math.max(0, pos - 30);
      var end = Math.min(h.text.length, start + 140);
      var snippet = h.text.substring(start, end);
      snippet = snippet.replace(re, '<mark>$1</mark>');
      if (start > 0) snippet = '…' + snippet;
      if (end < h.text.length) snippet = snippet + '…';
      var title = (h.title || ('第 ' + h.i + ' 页')).replace(/</g, '&lt;');
      html += '<div class="search-hit" data-slide-idx="' + h.i + '">'
            + '<span class="hit-num">P' + String(h.i).padStart(3, '0') + '</span>'
            + '<span>' + title + '</span>'
            + '<span class="hit-section">' + secName + '</span>'
            + '<div class="hit-snippet">' + snippet + '</div>'
            + '</div>';
    }}
    searchResults.innerHTML = html;
  }}
  searchInput.addEventListener('input', doSearch);
  searchResults.addEventListener('click', function(e) {{
    var h = e.target.closest('.search-hit');
    if (!h) return;
    var idx = parseInt(h.getAttribute('data-slide-idx'), 10);
    var target = document.getElementById('slide-' + idx);
    if (target) {{
      closeSearch();
      target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}
  }});
  document.getElementById('btn-search').addEventListener('click', function() {{
    if (searchModal.classList.contains('open')) closeSearch(); else openSearch();
  }});

  // ---- Thumbnail grid (fullscreen, section-grouped) ----
  var thumbGrid = document.getElementById('thumb-grid');
  var thumbCells = document.getElementById('thumb-cells');
  function openThumbs() {{
    if (!SLIDES_HTML) SLIDES_HTML = Array.from(document.querySelectorAll('.slide'));
    // Group by section
    var groups = {{}};
    SLIDES.forEach(function(s) {{
      if (!groups[s.section]) groups[s.section] = [];
      groups[s.section].push(s);
    }});
    var html = '';
    var sectionOrder = ['cover', '01','02','03','04','05','06','07','08','09','10','11','12','A'];
    for (var s = 0; s < sectionOrder.length; s++) {{
      var sec = sectionOrder[s];
      if (!groups[sec] || !groups[sec].length) continue;
      var secName = sec === 'cover' ? '封面' : (SECTION_TITLES[sec] || sec);
      html += '<div class="thumb-section-block">';
      html += '<div class="thumb-section-title">' + sec + ' · ' + secName + ' <span class="count">' + groups[sec].length + ' 张</span></div>';
      html += '<div class="thumb-section-grid">';
      for (var i = 0; i < groups[sec].length; i++) {{
        var sld = groups[sec][i];
        var title = (sld.title || ('第 ' + sld.i + ' 页')).replace(/</g, '&lt;');
        html += '<div class="thumb-cell" data-idx="' + sld.i + '">'
              + '<div class="thumb-num">P' + String(sld.i).padStart(3, '0') + '</div>'
              + '<div class="thumb-section-tag">' + sec + '</div>'
              + '<div class="thumb-wrap"><div class="thumb-clone"></div></div>'
              + '<div class="thumb-title">' + title + '</div>'
              + '</div>';
      }}
      html += '</div></div>';
    }}
    thumbCells.innerHTML = html;
    // Render slide clones asynchronously (throttled)
    setTimeout(function() {{
      var cells = thumbCells.querySelectorAll('.thumb-cell');
      var counter = 0;
      function renderNext() {{
        if (counter >= cells.length) return;
        var c = cells[counter++];
        var idx = parseInt(c.getAttribute('data-idx'), 10);
        var slide = SLIDES_HTML[idx-1];
        var wrap = c.querySelector('.thumb-clone');
        if (slide && wrap) {{
          var clone = slide.cloneNode(true);
          clone.id = '';
          clone.style.cssText = 'width:1920px;height:1080px;transform:scale(' + (wrap.clientWidth / 1920) + ');transform-origin:top left;position:absolute;top:0;left:0;pointer-events:none';
          wrap.appendChild(clone);
        }}
        if (counter % 4 === 0) requestAnimationFrame(renderNext);
        else setTimeout(renderNext, 0);
      }}
      renderNext();
    }}, 100);
    thumbGrid.classList.add('open');
  }}
  function closeThumbs() {{
    thumbGrid.classList.remove('open');
  }}
  document.getElementById('btn-thumbs').addEventListener('click', function() {{
    if (thumbGrid.classList.contains('open')) closeThumbs(); else openThumbs();
  }});
  document.getElementById('thumb-grid-close').addEventListener('click', closeThumbs);
  thumbCells.addEventListener('click', function(e) {{
    var c = e.target.closest('.thumb-cell');
    if (!c) return;
    closeThumbs();
    var idx = parseInt(c.getAttribute('data-idx'), 10);
    var target = document.getElementById('slide-' + idx);
    if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }});

  // ---- Top button ----
  document.getElementById('btn-top').addEventListener('click', function() {{
    var first = document.getElementById('slide-1');
    if (first) first.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }});

  // ---- Arrow keys: ← / → navigate prev/next slide ----
  function currentSlideIndex() {{
    var scrollY = window.scrollY + window.innerHeight * 0.3;
    var cur = 0;
    for (var k = 0; k < slideEls.length; k++) {{
      if (slideEls[k].offsetTop <= scrollY) cur = k;
    }}
    return cur;
  }}
  function goToSlide(idx) {{
    if (idx < 0) idx = 0;
    if (idx >= slideEls.length) idx = slideEls.length - 1;
    var target = document.getElementById('slide-' + (idx + 1));
    if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}

  // ---- Global keyboard shortcuts ----
  addEventListener('keydown', function(e) {{
    var ae = document.activeElement;
    var inField = ae && (ae.tagName === 'INPUT' || ae.tagName === 'TEXTAREA' || ae.isContentEditable);
    if (inField) return;

    if (e.key === 'Escape') {{
      if (searchModal.classList.contains('open')) {{ closeSearch(); e.preventDefault(); return; }}
      if (thumbGrid.classList.contains('open')) {{ closeThumbs(); e.preventDefault(); return; }}
      if (indexPanel.classList.contains('open')) {{ closeIndexPanel(); e.preventDefault(); return; }}
    }}
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {{
      e.preventDefault();
      if (searchModal.classList.contains('open')) closeSearch(); else openSearch();
      return;
    }}
    if (e.key === 'g' && !e.metaKey && !e.ctrlKey && !e.altKey) {{
      e.preventDefault();
      if (thumbGrid.classList.contains('open')) closeThumbs(); else openThumbs();
      return;
    }}
    if (e.key === 'i' && !e.metaKey && !e.ctrlKey && !e.altKey) {{
      e.preventDefault();
      toggleIndexPanel();
      return;
    }}
    if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey) {{
      e.preventDefault();
      openSearch();
      return;
    }}
    if (e.key === 'Home' && !e.metaKey && !e.ctrlKey) {{
      e.preventDefault();
      goToSlide(0);
      return;
    }}
    if (e.key === 'End' && !e.metaKey && !e.ctrlKey) {{
      e.preventDefault();
      goToSlide(slideEls.length - 1);
      return;
    }}
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{
      e.preventDefault();
      goToSlide(currentSlideIndex() + 1);
      return;
    }}
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
      e.preventDefault();
      goToSlide(currentSlideIndex() - 1);
      return;
    }}
  }});
}})();
</script>
'''

# ---- Final composition ----
new_prefix = (
    '<!-- ============================================================\n'
    '     SLIDES_HERE · 增城太子坑森林公园沉香目的地项目 · 可行性研究报告\n'
    '     Auto-generated by scripts/generate-zengcheng-deck.py (v2 layout-aware)\n'
    '     300+ slides · 13 sections · 4 info-graphics templates\n'
    '     Style C tokens (deep blue + sundial gold + Manrope)\n'
    '     ============================================================ -->\n'
)

new_deck_inner = '\n\n'.join(deck_blocks)

final = (
    html[:m.start()]
    + new_prefix
    + new_deck_inner
    + '\n\n'
    + m.group(3)
    # Skip template's leftover Q3 demo content: html[last_style_close:deck_close_idx]
    + NAV_CSS_BLOCK
    + html[deck_close_idx:nav_div_open]
    + NAV_HTML_BLOCK
    + html[nav_div_open:]
)

# Rewrite relative asset paths for nested location.
# Original template uses 'src="./assets/...' AND dynamic imports 'import("./assets/...")'.
final = final.replace('./assets/', '../../assets/')
final = final.replace('"../assets/', '"../../assets/')  # safety
# Also catch any src/href that didn't get caught
final = final.replace('src="./', 'src="../../')
final = final.replace("src='./", "src='../../")
final = final.replace('href="./', 'href="../../')
final = final.replace("href='./", "href='../../")
final = final.replace('href="references/', 'href="../../references/')

OUT.write_text(final, encoding='utf-8')
print(f'wrote {OUT}')
print(f'slide count: {len(deck_blocks)}')
print(f'output size: {OUT.stat().st_size} bytes')
