#!/usr/bin/env python3
"""
Generate curated SVG illustrations for the 增城太子坑森林公园沉香目的地 deck.
Each SVG is semantic to the project (太子坑森林公园, 沉香, 顺科智连, etc.).
Written to content/zengcheng-taizikeng/images/*.svg.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'content' / 'zengcheng-taizikeng' / 'images'
OUT.mkdir(parents=True, exist_ok=True)

# Color tokens (Table AI brand)
INK = '#0A1626'      # deep navy
ACCENT = '#A88B52'   # sundial gold
ACCENT_BRIGHT = '#C9A86B'
PAPER = '#FFFFFF'
INK_2 = '#44474C'
INK_3 = '#75777D'
GREY_1 = '#F5F3F4'
GREY_2 = '#DCD9DB'

def write(name: str, content: str):
    path = OUT / f'{name}.svg'
    path.write_text(content, encoding='utf-8')
    print(f'wrote {path.name} ({len(content):,} bytes)')

# ----------------------------------------------------------------------
# 1. COVER · 太子坑森林公园远眺 (artistic landscape with mountain + trees + sun)
# ----------------------------------------------------------------------
write('cover-太子坑远眺.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF"/>
      <stop offset="1" stop-color="#F5F3F4"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{ACCENT}"/>
      <stop offset="1" stop-color="{ACCENT_BRIGHT}"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="900" fill="url(#sky)"/>
  <!-- Sun -->
  <circle cx="1180" cy="220" r="90" fill="url(#gold)" opacity="0.85"/>
  <!-- Far mountain -->
  <path d="M 0 560 L 200 380 L 380 470 L 540 360 L 720 480 L 880 350 L 1080 460 L 1240 380 L 1400 470 L 1600 400 L 1600 900 L 0 900 Z" fill="{INK}" opacity="0.18"/>
  <!-- Mid mountain -->
  <path d="M 0 640 L 180 520 L 320 600 L 480 510 L 640 600 L 800 520 L 980 600 L 1140 520 L 1320 590 L 1480 530 L 1600 600 L 1600 900 L 0 900 Z" fill="{INK}" opacity="0.34"/>
  <!-- Front tree line (abstract 太子坑 silhouette) -->
  <g fill="{INK}">
    <ellipse cx="120" cy="730" rx="50" ry="80"/>
    <ellipse cx="180" cy="700" rx="40" ry="60"/>
    <rect x="115" y="730" width="6" height="60"/>
    <rect x="175" y="690" width="5" height="100"/>
    <ellipse cx="1500" cy="720" rx="80" ry="100"/>
    <ellipse cx="1420" cy="740" rx="55" ry="70"/>
    <rect x="1495" y="720" width="8" height="80"/>
    <rect x="1417" y="735" width="5" height="60"/>
  </g>
  <!-- Forest floor (faint) -->
  <line x1="0" y1="780" x2="1600" y2="780" stroke="{INK}" stroke-width="1" opacity="0.15"/>
  <line x1="0" y1="820" x2="1600" y2="820" stroke="{INK}" stroke-width="1" opacity="0.08"/>
  <!-- Chinese title overlay -->
  <text x="80" y="100" font-family="Songti SC, STSong, serif" font-size="48" font-weight="600" fill="{INK}" letter-spacing="6">太子坑</text>
  <text x="80" y="160" font-family="Songti SC, STSong, serif" font-size="32" font-weight="400" fill="{ACCENT}" letter-spacing="4">沉香森林 · 静待知音</text>
  <line x1="80" y1="180" x2="220" y2="180" stroke="{ACCENT}" stroke-width="2"/>
</svg>
''')

# ----------------------------------------------------------------------
# 2. TAIZIKENG · 太子坑森林公园资源平面图 (simplified master plan)
# ----------------------------------------------------------------------
write('site-太子坑总平面图.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid meet">
  <rect width="1200" height="800" fill="{PAPER}"/>
  <!-- Forest boundary -->
  <path d="M 100 400 Q 200 100 600 80 Q 1000 100 1100 400 Q 1100 700 600 720 Q 200 700 100 400 Z" fill="{GREY_1}" stroke="{INK}" stroke-width="2"/>
  <!-- Forest texture (tree dots) -->
  <g fill="{INK}" opacity="0.6">
    <circle cx="200" cy="200" r="4"/><circle cx="280" cy="180" r="4"/><circle cx="350" cy="220" r="4"/>
    <circle cx="430" cy="180" r="4"/><circle cx="500" cy="240" r="4"/><circle cx="580" cy="200" r="4"/>
    <circle cx="650" cy="160" r="4"/><circle cx="720" cy="200" r="4"/><circle cx="800" cy="240" r="4"/>
    <circle cx="880" cy="200" r="4"/><circle cx="950" cy="180" r="4"/><circle cx="1020" cy="240" r="4"/>
    <circle cx="200" cy="320" r="4"/><circle cx="280" cy="350" r="4"/><circle cx="380" cy="380" r="4"/>
    <circle cx="450" cy="320" r="4"/><circle cx="550" cy="360" r="4"/><circle cx="650" cy="380" r="4"/>
    <circle cx="750" cy="340" r="4"/><circle cx="850" cy="380" r="4"/><circle cx="950" cy="340" r="4"/>
    <circle cx="180" cy="480" r="4"/><circle cx="280" cy="500" r="4"/><circle cx="380" cy="520" r="4"/>
    <circle cx="480" cy="480" r="4"/><circle cx="580" cy="520" r="4"/><circle cx="680" cy="500" r="4"/>
    <circle cx="780" cy="480" r="4"/><circle cx="880" cy="520" r="4"/><circle cx="980" cy="500" r="4"/>
  </g>
  <!-- Site boundary (项目用地) -->
  <rect x="480" y="320" width="240" height="180" fill="{ACCENT}" fill-opacity="0.18" stroke="{ACCENT}" stroke-width="2.5" stroke-dasharray="8 4"/>
  <text x="600" y="380" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="700" fill="{INK}" letter-spacing="0.06em">项目用地</text>
  <text x="600" y="400" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}" letter-spacing="0.04em">约 30 亩</text>
  <text x="600" y="416" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}" letter-spacing="0.04em">点状供地</text>
  <!-- Roads -->
  <line x1="50" y1="650" x2="1150" y2="650" stroke="{INK_3}" stroke-width="1.5" stroke-dasharray="6 6"/>
  <text x="50" y="668" font-family="var(--sans-tab)" font-size="10" font-weight="600" fill="{INK_2}">现状主路 · 增城 → 太子坑</text>
  <line x1="600" y1="60" x2="600" y2="120" stroke="{INK_3}" stroke-width="1" stroke-dasharray="3 3"/>
  <text x="612" y="100" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">N ↑</text>
  <!-- Legend -->
  <g transform="translate(80,720)">
    <rect width="160" height="60" fill="{PAPER}" stroke="{GREY_2}"/>
    <rect x="10" y="12" width="14" height="14" fill="{ACCENT}" fill-opacity="0.3" stroke="{ACCENT}" stroke-width="1.5" stroke-dasharray="3 2"/>
    <text x="30" y="23" font-family="var(--sans-tab)" font-size="9" fill="{INK}">项目用地边界</text>
    <circle cx="17" cy="42" r="3" fill="{INK}"/>
    <text x="30" y="45" font-family="var(--sans-tab)" font-size="9" fill="{INK}">现状林分</text>
  </g>
  <text x="600" y="780" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}" letter-spacing="0.18em">太子坑森林公园 · 沉香目的地 平面图 (示意)</text>
</svg>
''')

# ----------------------------------------------------------------------
# 3. 沉香树 (Agarwood tree, stylized icon)
# ----------------------------------------------------------------------
write('tree-沉香.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600">
  <rect width="400" height="600" fill="{PAPER}"/>
  <!-- Trunk -->
  <path d="M 200 600 Q 195 480 200 380 Q 205 320 195 280" stroke="#5C4033" stroke-width="22" fill="none" stroke-linecap="round"/>
  <!-- Branches -->
  <path d="M 200 380 Q 150 360 100 320" stroke="#5C4033" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M 200 340 Q 260 320 320 280" stroke="#5C4033" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M 200 300 Q 145 285 95 250" stroke="#5C4033" stroke-width="8" fill="none" stroke-linecap="round"/>
  <path d="M 200 280 Q 255 260 295 220" stroke="#5C4033" stroke-width="8" fill="none" stroke-linecap="round"/>
  <!-- Foliage clusters (深绿 + 金色树脂纹路) -->
  <g fill="{INK}">
    <ellipse cx="100" cy="320" rx="65" ry="50"/>
    <ellipse cx="320" cy="280" rx="70" ry="55"/>
    <ellipse cx="95" cy="250" rx="55" ry="45"/>
    <ellipse cx="295" cy="220" rx="60" ry="50"/>
    <ellipse cx="200" cy="160" rx="80" ry="60"/>
  </g>
  <!-- Resin veins (金色) - 沉香树脂象征 -->
  <g fill="none" stroke="{ACCENT_BRIGHT}" stroke-width="2.5" stroke-linecap="round">
    <path d="M 120 290 Q 140 310 130 340"/>
    <path d="M 290 250 Q 310 270 295 295"/>
    <path d="M 110 240 Q 130 260 120 285"/>
    <path d="M 280 220 Q 305 240 285 260"/>
    <path d="M 170 130 Q 200 160 220 175"/>
    <path d="M 200 170 Q 180 195 165 210"/>
  </g>
  <!-- Drops (黄金树脂) -->
  <g fill="{ACCENT}">
    <circle cx="135" cy="335" r="4"/>
    <circle cx="305" cy="290" r="3.5"/>
    <circle cx="115" cy="280" r="3.5"/>
    <circle cx="200" cy="180" r="3"/>
  </g>
  <text x="200" y="555" text-anchor="middle" font-family="Songti SC, STSong, serif" font-size="22" font-weight="600" fill="{INK}">沉香</text>
  <text x="200" y="582" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" letter-spacing="0.18em" fill="{ACCENT}">AGARWOOD · AQUILARIA</text>
</svg>
''')

# ----------------------------------------------------------------------
# 4. 顺科智连 logo (stylized mark)
# ----------------------------------------------------------------------
write('logo-顺科智连.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240">
  <rect width="400" height="240" fill="{PAPER}"/>
  <!-- Logo mark: stylized "S" connected nodes (network) -->
  <g transform="translate(40,40)">
    <circle cx="20" cy="20" r="10" fill="{INK}"/>
    <circle cx="60" cy="60" r="10" fill="{INK}"/>
    <circle cx="100" cy="20" r="10" fill="{ACCENT}"/>
    <circle cx="100" cy="100" r="10" fill="{INK}"/>
    <circle cx="140" cy="60" r="10" fill="{ACCENT}"/>
    <line x1="20" y1="20" x2="60" y2="60" stroke="{INK_3}" stroke-width="2"/>
    <line x1="60" y1="60" x2="100" y2="20" stroke="{ACCENT}" stroke-width="2"/>
    <line x1="60" y1="60" x2="100" y2="100" stroke="{INK_3}" stroke-width="2"/>
    <line x1="100" y1="20" x2="140" y2="60" stroke="{ACCENT}" stroke-width="2"/>
    <line x1="100" y1="100" x2="140" y2="60" stroke="{INK_3}" stroke-width="2"/>
  </g>
  <!-- Wordmark -->
  <text x="200" y="100" font-family="var(--sans-tab)" font-size="36" font-weight="700" fill="{INK}" letter-spacing="2">顺科智连</text>
  <text x="200" y="130" font-family="var(--sans-tab)" font-size="11" font-weight="500" fill="{ACCENT}" letter-spacing="0.2em">SHUNKÉ · SMART CONNECT</text>
  <text x="200" y="160" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">技术股份有限公司</text>
</svg>
''')

# ----------------------------------------------------------------------
# 5. 三层架构图 (3-layer architecture for the project: industry / ops / experience)
# ----------------------------------------------------------------------
write('framework-3层架构.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800">
  <rect width="1200" height="800" fill="{PAPER}"/>
  <!-- Layer 1 (Top: industry / 一产) -->
  <rect x="200" y="80" width="800" height="120" fill="{INK}"/>
  <text x="600" y="125" text-anchor="middle" font-family="var(--sans-tab)" font-size="18" font-weight="700" fill="{PAPER}" letter-spacing="0.16em">LAYER 01 · 产业根</text>
  <text x="600" y="155" text-anchor="middle" font-family="var(--sans-tab)" font-size="13" fill="{PAPER}" opacity="0.7">沉香种植 · 树木认养 · 林下生态</text>
  <text x="600" y="178" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{ACCENT_BRIGHT}" letter-spacing="0.18em">AGARWOOD FORESTRY · 700+ 亩</text>
  <!-- Arrow -->
  <path d="M 600 200 L 600 240 M 595 235 L 600 245 L 605 235" stroke="{ACCENT}" stroke-width="2" fill="none"/>
  <!-- Layer 2 (Mid: ops / 二产) -->
  <rect x="200" y="250" width="800" height="160" fill="{ACCENT}"/>
  <text x="600" y="295" text-anchor="middle" font-family="var(--sans-tab)" font-size="18" font-weight="700" fill="{PAPER}" letter-spacing="0.16em">LAYER 02 · 产品与运营</text>
  <text x="600" y="325" text-anchor="middle" font-family="var(--sans-tab)" font-size="13" fill="{PAPER}" opacity="0.85">香品 · 精油 · 线香 · 茶席 · 文创 · 大健康衍生</text>
  <text x="600" y="350" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" letter-spacing="0.12em">企业学院 · 团建 · 培训 · 体检 · 康养</text>
  <text x="600" y="378" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.6" letter-spacing="0.18em">SMART OPERATIONS · ACADEMY</text>
  <!-- Arrow -->
  <path d="M 600 410 L 600 450 M 595 445 L 600 455 L 605 445" stroke="{ACCENT}" stroke-width="2" fill="none"/>
  <!-- Layer 3 (Bottom: experience / 三产) -->
  <rect x="200" y="460" width="800" height="160" fill="{INK_2}"/>
  <text x="600" y="505" text-anchor="middle" font-family="var(--sans-tab)" font-size="18" font-weight="700" fill="{PAPER}" letter-spacing="0.16em">LAYER 03 · 体验层</text>
  <text x="600" y="535" text-anchor="middle" font-family="var(--sans-tab)" font-size="13" fill="{PAPER}" opacity="0.85">高端接待 · 私宴 · 私董会 · 家族活动</text>
  <text x="600" y="560" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.6" letter-spacing="0.18em">PRIVATE EVENTS · LEGACY HOSPITALITY</text>
  <!-- Arrows from outside (input) -->
  <g stroke="{ACCENT_BRIGHT}" stroke-width="2" fill="none">
    <path d="M 120 140 Q 180 140 195 140"/>
    <path d="M 120 330 Q 180 330 195 330"/>
    <path d="M 120 540 Q 180 540 195 540"/>
  </g>
  <g fill="{ACCENT_BRIGHT}">
    <polygon points="195,140 188,135 188,145"/>
    <polygon points="195,330 188,325 188,335"/>
    <polygon points="195,540 188,535 188,545"/>
  </g>
  <!-- Input labels (left) -->
  <text x="40" y="135" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}">业主自有需求</text>
  <text x="40" y="148" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">Captive demand</text>
  <text x="40" y="325" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}">外部企业客户</text>
  <text x="40" y="338" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">External B2B</text>
  <text x="40" y="535" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}">高端散客 / 会员</text>
  <text x="40" y="548" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">Premium / Member</text>
  <!-- Output (right) -->
  <g stroke="{ACCENT_BRIGHT}" stroke-width="2" fill="none">
    <path d="M 1000 140 Q 1060 140 1080 140"/>
    <path d="M 1000 330 Q 1060 330 1080 330"/>
    <path d="M 1000 540 Q 1060 540 1080 540"/>
  </g>
  <g fill="{ACCENT_BRIGHT}">
    <polygon points="1080,140 1073,135 1073,145"/>
    <polygon points="1080,330 1073,325 1073,335"/>
    <polygon points="1080,540 1073,535 1073,545"/>
  </g>
  <text x="1100" y="135" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}">复合现金流</text>
  <text x="1100" y="148" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">Mixed cashflow</text>
  <text x="1100" y="325" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}">资产增值</text>
  <text x="1100" y="338" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">Asset appreciation</text>
  <text x="1100" y="535" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}">品牌与关系</text>
  <text x="1100" y="548" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">Brand &amp; relations</text>
  <!-- Caption -->
  <text x="600" y="730" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}" letter-spacing="0.18em">三产融合架构 · 业主自有需求 + 外部市场 + 长期持有</text>
  <text x="600" y="755" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">AGARWOOD DESTINATION · CONCEPT FRAMEWORK</text>
</svg>
''')

# ----------------------------------------------------------------------
# 6. 6-cell core definitions (6-cell numbered grid)
# ----------------------------------------------------------------------
write('grid-6功能.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800">
  <rect width="1200" height="800" fill="{PAPER}"/>
  <g font-family="var(--sans-tab)" font-size="20" font-weight="700">
    <g transform="translate(60,60)">
      <text x="0" y="0" font-size="64" fill="{ACCENT}" font-weight="700">01</text>
      <text x="0" y="36" font-size="20" fill="{INK}">入口展示</text>
      <text x="0" y="60" font-size="13" fill="{INK_3}" font-weight="400">入口门厅 · 接待大堂</text>
      <text x="0" y="80" font-size="13" fill="{INK_3}" font-weight="400">沉香文化展厅 · 零售</text>
      <text x="0" y="120" font-size="11" fill="{INK_2}">300-500 ㎡</text>
    </g>
    <g transform="translate(450,60)">
      <text x="0" y="0" font-size="64" fill="{ACCENT}" font-weight="700">02</text>
      <text x="0" y="36" font-size="20" fill="{INK}">精品住宿</text>
      <text x="0" y="60" font-size="13" fill="{INK_3}" font-weight="400">90-100 间客房</text>
      <text x="0" y="80" font-size="13" fill="{INK_3}" font-weight="400">森林景观房 / 套房</text>
      <text x="0" y="120" font-size="11" fill="{INK_2}">7,000-9,500 ㎡</text>
    </g>
    <g transform="translate(840,60)">
      <text x="0" y="0" font-size="64" fill="{ACCENT}" font-weight="700">03</text>
      <text x="0" y="36" font-size="20" fill="{INK}">餐饮与宴会</text>
      <text x="0" y="60" font-size="13" fill="{INK_3}" font-weight="400">全日餐厅 · 包房</text>
      <text x="0" y="80" font-size="13" fill="{INK_3}" font-weight="400">私宴 · 茶席</text>
      <text x="0" y="120" font-size="11" fill="{INK_2}">1,800-2,800 ㎡</text>
    </g>
    <g transform="translate(60,360)">
      <text x="0" y="0" font-size="64" fill="{ACCENT}" font-weight="700">04</text>
      <text x="0" y="36" font-size="20" fill="{INK}">企业学院</text>
      <text x="0" y="60" font-size="13" fill="{INK_3}" font-weight="400">多功能厅 · 培训室</text>
      <text x="0" y="80" font-size="13" fill="{INK_3}" font-weight="400">家族传承书院</text>
      <text x="0" y="120" font-size="11" fill="{INK_2}">2,000-3,500 ㎡</text>
    </g>
    <g transform="translate(450,360)">
      <text x="0" y="0" font-size="64" fill="{ACCENT}" font-weight="700">05</text>
      <text x="0" y="36" font-size="20" fill="{INK}">康养体检</text>
      <text x="0" y="60" font-size="13" fill="{INK_3}" font-weight="400">基础体检 · 咨询</text>
      <text x="0" y="80" font-size="13" fill="{INK_3}" font-weight="400">森林康养 · 睡眠管理</text>
      <text x="0" y="120" font-size="11" fill="{INK_2}">800-1,500 ㎡</text>
    </g>
    <g transform="translate(840,360)">
      <text x="0" y="0" font-size="64" fill="{ACCENT}" font-weight="700">06</text>
      <text x="0" y="36" font-size="20" fill="{INK}">沉香产业</text>
      <text x="0" y="60" font-size="13" fill="{INK_3}" font-weight="400">种植示范 · 科普</text>
      <text x="0" y="80" font-size="13" fill="{INK_3}" font-weight="400">工坊 · 礼品 · 零售</text>
      <text x="0" y="120" font-size="11" fill="{INK_2}">1,000-2,000 ㎡</text>
    </g>
  </g>
  <line x1="60" y1="240" x2="1140" y2="240" stroke="{GREY_2}"/>
  <line x1="60" y1="540" x2="1140" y2="540" stroke="{GREY_2}"/>
  <line x1="395" y1="60" x2="395" y2="700" stroke="{GREY_2}"/>
  <line x1="785" y1="60" x2="785" y2="700" stroke="{GREY_2}"/>
  <text x="600" y="770" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}" letter-spacing="0.18em">六大功能大区 · FACILITY PROGRAM (Q01-Q06)</text>
</svg>
''')

# ----------------------------------------------------------------------
# 7. Process timeline (4 phases)
# ----------------------------------------------------------------------
write('process-分期建设.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 500">
  <rect width="1400" height="500" fill="{PAPER}"/>
  <line x1="100" y1="250" x2="1300" y2="250" stroke="{INK}" stroke-width="3"/>
  <g font-family="var(--sans-tab)">
    <g transform="translate(180,250)">
      <circle cx="0" cy="0" r="20" fill="{ACCENT}"/>
      <text x="0" y="6" text-anchor="middle" font-size="14" font-weight="700" fill="{PAPER}">1</text>
      <text x="0" y="-50" text-anchor="middle" font-size="14" font-weight="700" fill="{INK}">PHASE 01</text>
      <text x="0" y="-30" text-anchor="middle" font-size="12" fill="{INK_2}">可研深化 + 合规锁定</text>
      <text x="0" y="50" text-anchor="middle" font-size="11" fill="{INK_3}">0 - 3 月</text>
      <text x="0" y="65" text-anchor="middle" font-size="10" fill="{INK_3}">业主需求调研</text>
      <text x="0" y="80" text-anchor="middle" font-size="10" fill="{INK_3}">用地合规核验</text>
      <text x="0" y="95" text-anchor="middle" font-size="10" fill="{INK_3}">医疗合作预沟通</text>
    </g>
    <g transform="translate(490,250)">
      <circle cx="0" cy="0" r="20" fill="{ACCENT}"/>
      <text x="0" y="6" text-anchor="middle" font-size="14" font-weight="700" fill="{PAPER}">2</text>
      <text x="0" y="-50" text-anchor="middle" font-size="14" font-weight="700" fill="{INK}">PHASE 02</text>
      <text x="0" y="-30" text-anchor="middle" font-size="12" fill="{INK_2}">概念规划 + 政府申报</text>
      <text x="0" y="50" text-anchor="middle" font-size="11" fill="{INK_3}">3 - 6 月</text>
      <text x="0" y="65" text-anchor="middle" font-size="10" fill="{INK_3}">概念规划</text>
      <text x="0" y="80" text-anchor="middle" font-size="10" fill="{INK_3}">投委会模型</text>
      <text x="0" y="95" text-anchor="middle" font-size="10" fill="{INK_3}">设计任务书</text>
    </g>
    <g transform="translate(800,250)">
      <circle cx="0" cy="0" r="20" fill="{ACCENT}"/>
      <text x="0" y="6" text-anchor="middle" font-size="14" font-weight="700" fill="{PAPER}">3</text>
      <text x="0" y="-50" text-anchor="middle" font-size="14" font-weight="700" fill="{INK}">PHASE 03</text>
      <text x="0" y="-30" text-anchor="middle" font-size="12" fill="{INK_2}">方案设计 + 筹建准备</text>
      <text x="0" y="50" text-anchor="middle" font-size="11" fill="{INK_3}">6 - 12 月</text>
      <text x="0" y="65" text-anchor="middle" font-size="10" fill="{INK_3}">建筑方案设计</text>
      <text x="0" y="80" text-anchor="middle" font-size="10" fill="{INK_3}">运营方签署</text>
      <text x="0" y="95" text-anchor="middle" font-size="10" fill="{INK_3}">学院课程开发</text>
    </g>
    <g transform="translate(1110,250)">
      <circle cx="0" cy="0" r="20" fill="{ACCENT}"/>
      <text x="0" y="6" text-anchor="middle" font-size="14" font-weight="700" fill="{PAPER}">4</text>
      <text x="0" y="-50" text-anchor="middle" font-size="14" font-weight="700" fill="{INK}">PHASE 04</text>
      <text x="0" y="-30" text-anchor="middle" font-size="12" fill="{INK_2}">建设 + 开业筹备</text>
      <text x="0" y="50" text-anchor="middle" font-size="11" fill="{INK_3}">12 - 24 月</text>
      <text x="0" y="65" text-anchor="middle" font-size="10" fill="{INK_3}">工程建设</text>
      <text x="0" y="80" text-anchor="middle" font-size="10" fill="{INK_3}">SOP 建立</text>
      <text x="0" y="95" text-anchor="middle" font-size="10" fill="{INK_3}">试运营 + 开业</text>
    </g>
  </g>
  <text x="700" y="450" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}" letter-spacing="0.18em">24-MONTH IMPLEMENTATION ROADMAP · 0-3 / 3-6 / 6-12 / 12-24 月</text>
</svg>
''')

# ----------------------------------------------------------------------
# 8. Risk matrix (2x2 with severity)
# ----------------------------------------------------------------------
write('matrix-风险评估.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 700">
  <rect width="800" height="700" fill="{PAPER}"/>
  <text x="400" y="40" text-anchor="middle" font-family="var(--sans-tab)" font-size="16" font-weight="700" fill="{INK}" letter-spacing="0.16em">RISK MATRIX · 风险评估</text>
  <text x="400" y="62" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">影响 × 可能性 · IMPACT × LIKELIHOOD</text>
  <line x1="120" y1="100" x2="120" y2="600" stroke="{INK}"/>
  <line x1="120" y1="600" x2="700" y2="600" stroke="{INK}"/>
  <!-- Y axis label -->
  <text x="80" y="350" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}" transform="rotate(-90, 80, 350)">影响 · IMPACT</text>
  <text x="730" y="350" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}" transform="rotate(-90, 730, 350)">可能性 · LIKELIHOOD</text>
  <!-- Quadrant fills -->
  <rect x="120" y="100" width="290" height="250" fill="{ACCENT}" fill-opacity="0.10" stroke="{ACCENT}" stroke-width="1.5"/>
  <rect x="410" y="100" width="290" height="250" fill="{ACCENT_BRIGHT}" fill-opacity="0.05" stroke="{ACCENT_BRIGHT}" stroke-width="1.5"/>
  <rect x="120" y="350" width="290" height="250" fill="{INK_2}" fill-opacity="0.04" stroke="{INK_2}" stroke-width="1.5"/>
  <rect x="410" y="350" width="290" height="250" fill="{ACCENT_BRIGHT}" fill-opacity="0.05" stroke="{ACCENT_BRIGHT}" stroke-width="1.5"/>
  <!-- Quadrant labels -->
  <text x="265" y="130" text-anchor="middle" font-family="var(--sans-tab)" font-size="12" font-weight="700" fill="{ACCENT}">高影响 · 高概率</text>
  <text x="265" y="148" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_2}">CRITICAL · 优先处理</text>
  <text x="555" y="130" text-anchor="middle" font-family="var(--sans-tab)" font-size="12" font-weight="600" fill="{INK_2}">高影响 · 低概率</text>
  <text x="555" y="148" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">SERIOUS · 预案</text>
  <text x="265" y="380" text-anchor="middle" font-family="var(--sans-tab)" font-size="12" font-weight="600" fill="{INK_2}">低影响 · 高概率</text>
  <text x="265" y="398" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">FREQUENT · 监控</text>
  <text x="555" y="380" text-anchor="middle" font-family="var(--sans-tab)" font-size="12" font-weight="600" fill="{INK_2}">低影响 · 低概率</text>
  <text x="555" y="398" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">MINOR · 接受</text>
  <!-- Risk markers (4 risks) -->
  <g font-family="var(--sans-tab)">
    <g transform="translate(220, 200)">
      <circle r="22" fill="{ACCENT}"/>
      <text text-anchor="middle" font-size="11" font-weight="700" fill="{PAPER}" y="4">R1</text>
      <text x="32" y="-2" font-size="10" font-weight="600" fill="{INK}">合规边界</text>
      <text x="32" y="12" font-size="9" fill="{INK_2}">被识别为私人庄园</text>
    </g>
    <g transform="translate(335, 280)">
      <circle r="22" fill="{ACCENT}"/>
      <text text-anchor="middle" font-size="11" font-weight="700" fill="{PAPER}" y="4">R2</text>
      <text x="32" y="-2" font-size="10" font-weight="600" fill="{INK}">CAPEX</text>
      <text x="32" y="12" font-size="9" fill="{INK_2}">建设成本失控</text>
    </g>
    <g transform="translate(490, 220)">
      <circle r="22" fill="{ACCENT_BRIGHT}"/>
      <text text-anchor="middle" font-size="11" font-weight="700" fill="{PAPER}" y="4">R3</text>
      <text x="32" y="-2" font-size="10" font-weight="600" fill="{INK}">医疗资质</text>
      <text x="32" y="12" font-size="9" fill="{INK_2}">体检合规边界</text>
    </g>
    <g transform="translate(640, 320)">
      <circle r="22" fill="{INK_2}"/>
      <text text-anchor="middle" font-size="11" font-weight="700" fill="{PAPER}" y="4">R4</text>
      <text x="-90" y="-2" font-size="10" font-weight="600" fill="{INK}">品牌与关系</text>
      <text x="-90" y="12" font-size="9" fill="{INK_2}">沉香文化空心化</text>
    </g>
    <g transform="translate(380, 480)">
      <circle r="22" fill="{INK_2}"/>
      <text text-anchor="middle" font-size="11" font-weight="700" fill="{PAPER}" y="4">R5</text>
      <text x="32" y="-2" font-size="10" font-weight="600" fill="{INK}">团队能力</text>
      <text x="32" y="12" font-size="9" fill="{INK_2}">多业态运营复杂度</text>
    </g>
    <g transform="translate(630, 530)">
      <circle r="22" fill="{INK_2}"/>
      <text text-anchor="middle" font-size="11" font-weight="700" fill="{PAPER}" y="4">R6</text>
      <text x="-90" y="-2" font-size="10" font-weight="600" fill="{INK}">外部市场</text>
      <text x="-90" y="12" font-size="9" fill="{INK_2}">企业客户复购</text>
    </g>
  </g>
  <text x="400" y="680" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">R1 合规边界 · R2 CAPEX · R3 医疗资质 · R4 品牌与关系 · R5 团队能力 · R6 外部市场</text>
</svg>
''')

# ----------------------------------------------------------------------
# 9. Hero stat illustration: Q3 2026 NorthStar Q3-style key numbers
# ----------------------------------------------------------------------
write('hero-关键数字.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 700">
  <rect width="1200" height="700" fill="{PAPER}"/>
  <g font-family="var(--sans-tab)">
    <text x="60" y="60" font-size="12" font-weight="600" fill="{ACCENT}" letter-spacing="0.18em">PROJECT KEY METRICS · 项目关键数字</text>
    <line x1="60" y1="76" x2="200" y2="76" stroke="{ACCENT}" stroke-width="2"/>
  </g>
  <g font-family="var(--sans-tab)" text-anchor="middle">
    <g transform="translate(280,280)">
      <text font-size="11" font-weight="600" fill="{INK_3}" letter-spacing="0.12em">客房规模</text>
      <text y="80" font-size="84" font-weight="700" fill="{INK}" letter-spacing="-0.04em">90–100</text>
      <text y="116" font-size="11" fill="{INK_3}">间 · rooms</text>
      <line x1="-90" y1="160" x2="90" y2="160" stroke="{GREY_2}"/>
      <text y="190" font-size="11" fill="{INK_2}">首期建议基准</text>
    </g>
    <g transform="translate(600,280)">
      <text font-size="11" font-weight="600" fill="{INK_3}" letter-spacing="0.12em">总投资估算</text>
      <text y="80" font-size="84" font-weight="700" fill="{ACCENT}" letter-spacing="-0.04em">¥2.4–3.0</text>
      <text y="116" font-size="11" fill="{INK_3}">亿元 · CAPEX</text>
      <line x1="-90" y1="160" x2="90" y2="160" stroke="{GREY_2}"/>
      <text y="190" font-size="11" fill="{INK_2}">基准情景</text>
    </g>
    <g transform="translate(920,280)">
      <text font-size="11" font-weight="600" fill="{INK_3}" letter-spacing="0.12em">稳定期 NOI</text>
      <text y="80" font-size="84" font-weight="700" fill="{INK}" letter-spacing="-0.04em">¥1,000–1,600</text>
      <text y="116" font-size="11" fill="{INK_3}">万 / 年 · NOI</text>
      <line x1="-90" y1="160" x2="90" y2="160" stroke="{GREY_2}"/>
      <text y="190" font-size="11" fill="{INK_2}">基准情景</text>
    </g>
    <g transform="translate(440,540)">
      <text font-size="11" font-weight="600" fill="{INK_3}" letter-spacing="0.12em">点状供地上限</text>
      <text y="60" font-size="64" font-weight="700" fill="{INK}" letter-spacing="-0.04em">30 亩</text>
      <text y="88" font-size="11" fill="{INK_3}">约 20,000 ㎡</text>
    </g>
    <g transform="translate(760,540)">
      <text font-size="11" font-weight="600" fill="{INK_3}" letter-spacing="0.12em">静态回收期</text>
      <text y="60" font-size="64" font-weight="700" fill="{INK}" letter-spacing="-0.04em">14–18 年</text>
      <text y="88" font-size="11" fill="{INK_3}">基准情景</text>
    </g>
  </g>
  <line x1="60" y1="430" x2="1140" y2="430" stroke="{GREY_2}"/>
  <text x="600" y="675" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}" letter-spacing="0.12em">PRIMARY METRICS · 11 KV metrics across 5 categories</text>
</svg>
''')

# ----------------------------------------------------------------------
# 10. Decision tree: A vs B vs Hybrid (3-way option compare)
# ----------------------------------------------------------------------
write('compare-3路径.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600">
  <rect width="1200" height="600" fill="{PAPER}"/>
  <text x="600" y="50" text-anchor="middle" font-family="var(--sans-tab)" font-size="16" font-weight="700" fill="{INK}" letter-spacing="0.18em">3 PATHS · Q2 vs Q3 GTM</text>
  <text x="600" y="72" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" fill="{INK_3}">从纯 PLG 到 Hybrid GTM 的三个选择</text>
  <!-- Start node -->
  <g transform="translate(600,140)">
    <circle r="42" fill="{INK}"/>
    <text y="-2" text-anchor="middle" font-family="var(--sans-tab)" font-size="12" font-weight="700" fill="{PAPER}">START</text>
    <text y="14" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.7">Q2 模式</text>
  </g>
  <!-- Three branches -->
  <line x1="600" y1="182" x2="240" y2="260" stroke="{GREY_2}" stroke-width="2"/>
  <line x1="600" y1="182" x2="600" y2="260" stroke="{INK_2}" stroke-width="2.5"/>
  <line x1="600" y1="182" x2="960" y2="260" stroke="{ACCENT}" stroke-width="2.5"/>
  <!-- Option A: continue PLG -->
  <g transform="translate(240,300)">
    <rect x="-130" y="-40" width="260" height="100" fill="{PAPER}" stroke="{GREY_2}" stroke-width="1.5"/>
    <text x="0" y="-18" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="700" fill="{INK}" letter-spacing="0.12em">OPTION A · PURE PLG</text>
    <text x="0" y="2" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_2}">Pure self-serve only</text>
    <text x="0" y="20" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">所有流量自注册</text>
    <text x="0" y="34" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">Sales 仅接 inbound</text>
    <text x="0" y="48" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">Mid-market 真空</text>
  </g>
  <text x="240" y="370" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" font-weight="600" fill="{GREY_2}">同 Q2 表现</text>
  <text x="240" y="385" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">ARR 增长 ≈ 5-8% / 季</text>
  <!-- Option B: big investment -->
  <g transform="translate(600,300)">
    <rect x="-130" y="-40" width="260" height="100" fill="{PAPER}" stroke="{INK_2}" stroke-width="1.5"/>
    <text x="0" y="-18" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="700" fill="{INK_2}" letter-spacing="0.12em">OPTION B · BIG BET</text>
    <text x="0" y="2" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_2}">全 enterprise 押注</text>
    <text x="0" y="20" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">12 个 AE/SE 一次到位</text>
    <text x="0" y="34" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">放弃 SMB 流量</text>
    <text x="0" y="48" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">高风险 · 高回报</text>
  </g>
  <text x="600" y="370" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" font-weight="600" fill="{INK_2}">30–45% 增长 / 季</text>
  <text x="600" y="385" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">但 culture shock 高</text>
  <!-- Option C: hybrid (recommended) -->
  <g transform="translate(960,300)">
    <rect x="-130" y="-40" width="260" height="100" fill="{ACCENT}" fill-opacity="0.10" stroke="{ACCENT}" stroke-width="2.5"/>
    <text x="0" y="-18" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="700" fill="{ACCENT}" letter-spacing="0.12em">OPTION C · HYBRID ✓</text>
    <text x="0" y="2" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_2}">三轨并行 (推荐)</text>
    <text x="0" y="20" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">PLG 继续 · SDR 打 Ent</text>
    <text x="0" y="34" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">SC 跟 Mid-market</text>
    <text x="0" y="48" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">月度合并复盘</text>
  </g>
  <text x="960" y="370" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" font-weight="600" fill="{ACCENT}">20–35% 增长 / 季 ✓</text>
  <text x="960" y="385" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">稳定 + 自有需求托底</text>
  <!-- Arrows from options to outcomes -->
  <g transform="translate(600,500)">
    <rect x="-180" y="-30" width="360" height="60" fill="{INK_2}" fill-opacity="0.04" stroke="{INK_2}" stroke-width="1.5" stroke-dasharray="3 3"/>
    <text y="-8" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="700" fill="{INK}">RECOMMENDATION</text>
    <text y="14" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_2}">走 Option C · Hybrid GTM</text>
  </g>
  <path d="M 240 410 L 410 470 M 600 410 L 600 470 M 960 410 L 790 470" stroke="{INK_2}" stroke-width="1.5" stroke-dasharray="2 2"/>
</svg>
''')

# ----------------------------------------------------------------------
# 11. Forest trail (process flow)
# ----------------------------------------------------------------------
write('forest-步道.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 500">
  <rect width="1200" height="500" fill="{PAPER}"/>
  <text x="600" y="50" text-anchor="middle" font-family="var(--sans-tab)" font-size="14" font-weight="700" fill="{INK}" letter-spacing="0.18em">FOREST TRAIL · 森林步道动线</text>
  <text x="600" y="72" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">从入口到 VIP 接待的内部动线</text>
  <!-- Path (winding) -->
  <path d="M 100 250 Q 250 150 400 250 T 700 250 T 1000 250 T 1100 200" stroke="{INK_2}" stroke-width="2" fill="none" stroke-dasharray="6 6"/>
  <!-- Tree icons along path -->
  <g font-family="var(--sans-tab)">
    <g transform="translate(100,250)">
      <circle r="12" fill="{ACCENT}"/>
      <text y="4" text-anchor="middle" font-size="10" font-weight="700" fill="{PAPER}">1</text>
      <text x="0" y="40" text-anchor="middle" font-size="11" font-weight="600" fill="{INK}">入口大堂</text>
      <text x="0" y="55" text-anchor="middle" font-size="9" fill="{INK_3}">ARRIVAL</text>
    </g>
    <g transform="translate(280,200)">
      <circle r="12" fill="{ACCENT}"/>
      <text y="4" text-anchor="middle" font-size="10" font-weight="700" fill="{PAPER}">2</text>
      <text x="0" y="-30" text-anchor="middle" font-size="11" font-weight="600" fill="{INK}">沉香展示厅</text>
      <text x="0" y="-15" text-anchor="middle" font-size="9" fill="{INK_3}">AGARWOOD MUSEUM</text>
    </g>
    <g transform="translate(450,250)">
      <circle r="12" fill="{ACCENT}"/>
      <text y="4" text-anchor="middle" font-size="10" font-weight="700" fill="{PAPER}">3</text>
      <text x="0" y="40" text-anchor="middle" font-size="11" font-weight="600" fill="{INK}">企业学院</text>
      <text x="0" y="55" text-anchor="middle" font-size="9" fill="{INK_3}">ACADEMY</text>
    </g>
    <g transform="translate(620,200)">
      <circle r="12" fill="{ACCENT}"/>
      <text y="4" text-anchor="middle" font-size="10" font-weight="700" fill="{PAPER}">4</text>
      <text x="0" y="-30" text-anchor="middle" font-size="11" font-weight="600" fill="{INK}">康养体检</text>
      <text x="0" y="-15" text-anchor="middle" font-size="9" fill="{INK_3}">WELLNESS</text>
    </g>
    <g transform="translate(800,250)">
      <circle r="12" fill="{ACCENT}"/>
      <text y="4" text-anchor="middle" font-size="10" font-weight="700" fill="{PAPER}">5</text>
      <text x="0" y="40" text-anchor="middle" font-size="11" font-weight="600" fill="{INK}">团建草坪</text>
      <text x="0" y="55" text-anchor="middle" font-size="9" fill="{INK_3}">TEAMBUILDING</text>
    </g>
    <g transform="translate(1000,250)">
      <circle r="12" fill="{ACCENT}"/>
      <text y="4" text-anchor="middle" font-size="10" font-weight="700" fill="{PAPER}">6</text>
      <text x="0" y="40" text-anchor="middle" font-size="11" font-weight="600" fill="{INK}">精品住宿</text>
      <text x="0" y="55" text-anchor="middle" font-size="9" fill="{INK_3}">LODGING</text>
    </g>
    <g transform="translate(1100,200)">
      <circle r="14" fill="{INK}"/>
      <text y="4" text-anchor="middle" font-size="10" font-weight="700" fill="{PAPER}">★</text>
      <text x="-30" y="-30" text-anchor="middle" font-size="11" font-weight="700" fill="{INK}">VIP</text>
      <text x="-30" y="-15" text-anchor="middle" font-size="9" fill="{INK_3}">独立入口</text>
    </g>
  </g>
  <text x="600" y="430" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">GUEST CIRCULATION · 客流动线 · 普通客流 + VIP 独立</text>
  <line x1="950" y1="220" x2="1050" y2="200" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3 3"/>
</svg>
''')

# ----------------------------------------------------------------------
# 12. Quote callout: 顺科智连创始人 quote
# ----------------------------------------------------------------------
write('quote-创始人.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500">
  <rect width="1000" height="500" fill="{PAPER}"/>
  <!-- Background pattern -->
  <g opacity="0.10" fill="{ACCENT}">
    <circle cx="100" cy="100" r="2"/><circle cx="200" cy="80" r="2"/><circle cx="300" cy="120" r="2"/>
    <circle cx="400" cy="100" r="2"/><circle cx="500" cy="80" r="2"/><circle cx="600" cy="120" r="2"/>
    <circle cx="700" cy="100" r="2"/><circle cx="800" cy="80" r="2"/><circle cx="900" cy="120" r="2"/>
    <circle cx="100" cy="400" r="2"/><circle cx="200" cy="380" r="2"/><circle cx="300" cy="420" r="2"/>
    <circle cx="400" cy="400" r="2"/><circle cx="500" cy="380" r="2"/><circle cx="600" cy="420" r="2"/>
    <circle cx="700" cy="400" r="2"/><circle cx="800" cy="380" r="2"/><circle cx="900" cy="420" r="2"/>
  </g>
  <!-- Big quote mark -->
  <text x="80" y="200" font-family="Georgia, serif" font-size="200" font-weight="700" fill="{ACCENT}" opacity="0.32">"</text>
  <!-- Quote text -->
  <text x="500" y="230" text-anchor="middle" font-family="Songti SC, STSong, serif" font-size="22" font-weight="600" fill="{INK}">沉香是一片森林的事,</text>
  <text x="500" y="270" text-anchor="middle" font-family="Songti SC, STSong, serif" font-size="22" font-weight="600" fill="{INK}">不是一家酒店的事。</text>
  <text x="500" y="320" text-anchor="middle" font-family="var(--sans-tab)" font-size="14" font-weight="400" fill="{INK_2}">—— 内部备忘录, 2026 Q2</text>
  <line x1="450" y1="350" x2="550" y2="350" stroke="{ACCENT}" stroke-width="2"/>
  <text x="500" y="385" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{ACCENT}" letter-spacing="0.18em">PRINCIPLE · 原则</text>
  <text x="500" y="410" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">AGARWOOD IS A FOREST STORY, NOT A HOTEL STORY</text>
</svg>
''')

# ----------------------------------------------------------------------
# 13. Pyramid (3-tier hierarchy)
# ----------------------------------------------------------------------
write('pyramid-3层.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700">
  <rect width="1000" height="700" fill="{PAPER}"/>
  <text x="500" y="50" text-anchor="middle" font-family="var(--sans-tab)" font-size="16" font-weight="700" fill="{INK}" letter-spacing="0.18em">3-TIER HIERARCHY · 资源/产品/体验</text>
  <text x="500" y="72" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">塔型定位: 基础层 → 中间层 → 顶层</text>
  <!-- Top (smallest) -->
  <polygon points="350,160 650,160 600,240 400,240" fill="{ACCENT}"/>
  <text x="500" y="200" text-anchor="middle" font-family="var(--sans-tab)" font-size="14" font-weight="700" fill="{PAPER}">顶层 · TIP</text>
  <text x="500" y="218" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.85">高端接待 · 私董会 · 家族传承</text>
  <!-- Middle -->
  <polygon points="380,260 620,260 580,360 420,360" fill="{INK}"/>
  <text x="500" y="305" text-anchor="middle" font-family="var(--sans-tab)" font-size="14" font-weight="700" fill="{PAPER}">中间层 · BODY</text>
  <text x="500" y="323" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.85">企业学院 · 团建 · 培训</text>
  <text x="500" y="340" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.7">康养 · 体检</text>
  <!-- Bottom (largest) -->
  <polygon points="250,380 750,380 800,540 200,540" fill="{INK_2}"/>
  <text x="500" y="440" text-anchor="middle" font-family="var(--sans-tab)" font-size="14" font-weight="700" fill="{PAPER}">基础层 · BASE</text>
  <text x="500" y="460" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.85">沉香种植 · 一产 · 产业根</text>
  <text x="500" y="478" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.7">森林体验 · 步道 · 公共开放</text>
  <text x="500" y="496" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.7">公共科普 · 农文旅融合</text>
  <text x="500" y="600" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">顶层高价值, 中间层运营, 基础层公共</text>
  <text x="500" y="618" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_3}">PYRAMID LOGIC · 资产价值与公共性平衡</text>
</svg>
''')

# ----------------------------------------------------------------------
# 14. Donut chart: 收入结构
# ----------------------------------------------------------------------
write('donut-收入结构.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 700">
  <rect width="800" height="700" fill="{PAPER}"/>
  <text x="400" y="50" text-anchor="middle" font-family="var(--sans-tab)" font-size="16" font-weight="700" fill="{INK}" letter-spacing="0.18em">REVENUE MIX · 收入结构</text>
  <text x="400" y="72" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">稳定期基准情景 · 7 项收入</text>
  <!-- Donut chart (centered at 400, 350) -->
  <g transform="translate(400, 350)">
    <!-- 客房 30% (top-right) -->
    <path d="M 0 -150 A 150 150 0 0 1 142.66 -46.35 L 71.33 -23.18 A 75 75 0 0 0 0 -75 Z" fill="{INK}"/>
    <!-- 餐饮 25% (right) -->
    <path d="M 142.66 -46.35 A 150 150 0 0 1 117.13 94.16 L 58.56 47.08 A 75 75 0 0 0 71.33 -23.18 Z" fill="{INK_2}"/>
    <!-- 会议 15% (bottom-right) -->
    <path d="M 117.13 94.16 A 150 150 0 0 1 -25.65 147.80 L -12.82 73.90 A 75 75 0 0 0 58.56 47.08 Z" fill="{ACCENT}"/>
    <!-- 康养 15% (bottom) -->
    <path d="M -25.65 147.80 A 150 150 0 0 1 -130.66 71.30 L -65.33 35.65 A 75 75 0 0 0 -12.82 73.90 Z" fill="{ACCENT_BRIGHT}"/>
    <!-- 学院 10% (bottom-left) -->
    <path d="M -130.66 71.30 A 150 150 0 0 1 -117.13 -94.16 L -58.56 -47.08 A 75 75 0 0 0 -65.33 35.65 Z" fill="{INK_3}"/>
    <!-- 零售 3% (left) -->
    <path d="M -117.13 -94.16 A 150 150 0 0 1 0 -150 L 0 -75 A 75 75 0 0 0 -58.56 -47.08 Z" fill="{GREY_2}"/>
    <!-- 其他 2% (top-left) -->
    <path d="M 0 -150 A 150 150 0 0 1 142.66 -46.35 L 71.33 -23.18 A 75 75 0 0 0 0 -75 Z" fill="{INK}"/>
    <text y="-10" text-anchor="middle" font-family="var(--sans-tab)" font-size="42" font-weight="700" fill="{INK}">¥6M+</text>
    <text y="22" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{ACCENT}">稳定期年收入</text>
  </g>
  <!-- Legend -->
  <g font-family="var(--sans-tab)" font-size="11">
    <g transform="translate(600,200)">
      <rect x="0" y="0" width="14" height="14" fill="{INK}"/>
      <text x="22" y="11" fill="{INK}">客房 · Rooms</text>
      <text x="22" y="26" font-size="9" fill="{INK_3}">30% · ~¥2.0M</text>
    </g>
    <g transform="translate(600,240)">
      <rect x="0" y="0" width="14" height="14" fill="{INK_2}"/>
      <text x="22" y="11" fill="{INK}">餐饮 · F&amp;B</text>
      <text x="22" y="26" font-size="9" fill="{INK_3}">25% · ~¥1.5M</text>
    </g>
    <g transform="translate(600,280)">
      <rect x="0" y="0" width="14" height="14" fill="{ACCENT}"/>
      <text x="22" y="11" fill="{INK}">会议 · Events</text>
      <text x="22" y="26" font-size="9" fill="{INK_3}">15% · ~¥0.9M</text>
    </g>
    <g transform="translate(600,320)">
      <rect x="0" y="0" width="14" height="14" fill="{ACCENT_BRIGHT}"/>
      <text x="22" y="11" fill="{INK}">康养 · Wellness</text>
      <text x="22" y="26" font-size="9" fill="{INK_3}">15% · ~¥0.9M</text>
    </g>
    <g transform="translate(600,360)">
      <rect x="0" y="0" width="14" height="14" fill="{INK_3}"/>
      <text x="22" y="11" fill="{INK}">学院 · Academy</text>
      <text x="22" y="26" font-size="9" fill="{INK_3}">10% · ~¥0.6M</text>
    </g>
    <g transform="translate(600,400)">
      <rect x="0" y="0" width="14" height="14" fill="{GREY_2}"/>
      <text x="22" y="11" fill="{INK}">零售 · Retail</text>
      <text x="22" y="26" font-size="9" fill="{INK_3}">3% · ~¥0.2M</text>
    </g>
    <g transform="translate(600,440)">
      <rect x="0" y="0" width="14" height="14" fill="{INK}"/>
      <text x="22" y="11" fill="{INK}">其他 · Other</text>
      <text x="22" y="26" font-size="9" fill="{INK_3}">2% · ~¥0.1M</text>
    </g>
  </g>
  <text x="400" y="620" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">MIX STRATEGY · 客房 30% + 餐饮 25% = 55% 核心, 康养/学院/会议 30% 高毛利</text>
</svg>
''')

# ----------------------------------------------------------------------
# 15. AGARWOOD product showcase
# ----------------------------------------------------------------------
write('product-沉香制品.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600">
  <rect width="1200" height="600" fill="{PAPER}"/>
  <text x="600" y="50" text-anchor="middle" font-family="var(--sans-tab)" font-size="16" font-weight="700" fill="{INK}" letter-spacing="0.18em">AGARWOOD PRODUCTS · 沉香制品矩阵</text>
  <text x="600" y="72" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">二产衍生: 30+ SKU · 文化体验 + 礼赠 + 大健康</text>
  <g font-family="var(--sans-tab)">
    <!-- Card 1: 线香 (incense sticks) -->
    <g transform="translate(200,300)">
      <rect x="-90" y="-90" width="180" height="180" fill="{GREY_1}" stroke="{INK}"/>
      <line x1="-50" y1="-30" x2="50" y2="-30" stroke="{ACCENT}" stroke-width="3"/>
      <line x1="-50" y1="0" x2="50" y2="0" stroke="{ACCENT}" stroke-width="3"/>
      <line x1="-50" y1="30" x2="50" y2="30" stroke="{ACCENT}" stroke-width="3"/>
      <line x1="-50" y1="60" x2="50" y2="60" stroke="{ACCENT}" stroke-width="3"/>
      <text y="-105" text-anchor="middle" font-size="13" font-weight="700" fill="{INK}">线香</text>
      <text y="115" text-anchor="middle" font-size="10" fill="{INK_2}">INCENSE STICKS</text>
      <text y="130" text-anchor="middle" font-size="9" fill="{INK_3}">¥ 80-300 / 盒</text>
    </g>
    <!-- Card 2: 精油 (essential oil) -->
    <g transform="translate(420,300)">
      <rect x="-90" y="-90" width="180" height="180" fill="{GREY_1}" stroke="{INK}"/>
      <circle cx="0" cy="0" r="35" fill="{ACCENT_BRIGHT}"/>
      <rect x="-5" y="20" width="10" height="50" fill="{INK}"/>
      <text y="-105" text-anchor="middle" font-size="13" font-weight="700" fill="{INK}">精油</text>
      <text y="115" text-anchor="middle" font-size="10" fill="{INK_2}">ESSENTIAL OIL</text>
      <text y="130" text-anchor="middle" font-size="9" fill="{INK_3}">¥ 480-1,200 / 5ml</text>
    </g>
    <!-- Card 3: 茶席 (tea ceremony) -->
    <g transform="translate(640,300)">
      <rect x="-90" y="-90" width="180" height="180" fill="{GREY_1}" stroke="{INK}"/>
      <ellipse cx="0" cy="0" rx="50" ry="20" fill="{INK}"/>
      <ellipse cx="0" cy="0" rx="40" ry="14" fill="{ACCENT}"/>
      <line x1="-30" y1="0" x2="30" y2="0" stroke="{INK_2}" stroke-width="2"/>
      <text y="-105" text-anchor="middle" font-size="13" font-weight="700" fill="{INK}">沉香茶</text>
      <text y="115" text-anchor="middle" font-size="10" fill="{INK_2}">AGARWOOD TEA</text>
      <text y="130" text-anchor="middle" font-size="9" fill="{INK_3}">¥ 280-680 / 罐</text>
    </g>
    <!-- Card 4: 文创 (cultural product) -->
    <g transform="translate(860,300)">
      <rect x="-90" y="-90" width="180" height="180" fill="{GREY_1}" stroke="{INK}"/>
      <rect x="-40" y="-50" width="80" height="60" fill="{INK}"/>
      <rect x="-35" y="-45" width="70" height="50" fill="{ACCENT}"/>
      <text x="0" y="-10" text-anchor="middle" font-size="20" font-weight="700" fill="{PAPER}">·</text>
      <text y="-105" text-anchor="middle" font-size="13" font-weight="700" fill="{INK}">文创礼盒</text>
      <text y="115" text-anchor="middle" font-size="10" fill="{INK_2}">GIFT BOX</text>
      <text y="130" text-anchor="middle" font-size="9" fill="{INK_3}">¥ 380-2,800 / 套</text>
    </g>
    <!-- Card 5: 雕件 (carvings) -->
    <g transform="translate(1080,300)">
      <rect x="-90" y="-90" width="180" height="180" fill="{GREY_1}" stroke="{INK}"/>
      <path d="M -40 -40 Q -20 -60 0 -40 Q 20 -60 40 -40 L 30 40 L -30 40 Z" fill="{ACCENT}"/>
      <circle cx="0" cy="0" r="8" fill="{INK}"/>
      <text y="-105" text-anchor="middle" font-size="13" font-weight="700" fill="{INK}">雕件</text>
      <text y="115" text-anchor="middle" font-size="10" fill="{INK_2}">CARVINGS</text>
      <text y="130" text-anchor="middle" font-size="9" fill="{INK_3}">¥ 1,200-15,000+</text>
    </g>
  </g>
  <text x="600" y="490" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}" letter-spacing="0.18em">30+ SKU · 30% 零售毛利 · 企业礼赠 + 个人体验</text>
  <text x="600" y="510" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">零售 3% / 收入 · 但 30% 毛利</text>
</svg>
''')

# ----------------------------------------------------------------------
# 16. The four principles (金字塔下层)
# ----------------------------------------------------------------------
write('principles-4.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600">
  <rect width="1200" height="600" fill="{PAPER}"/>
  <text x="600" y="60" text-anchor="middle" font-family="var(--sans-tab)" font-size="16" font-weight="700" fill="{INK}" letter-spacing="0.18em">FOUR PRINCIPLES · 四原则</text>
  <text x="600" y="84" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" fill="{INK_3}">项目判断的四个底层原则</text>
  <g font-family="var(--sans-tab)">
    <g transform="translate(300,300)">
      <circle r="60" fill="{ACCENT}"/>
      <text y="-12" text-anchor="middle" font-size="32" font-weight="700" fill="{PAPER}">P1</text>
      <text y="14" text-anchor="middle" font-size="11" font-weight="700" fill="{PAPER}">真实需求</text>
      <text y="30" text-anchor="middle" font-size="9" fill="{PAPER}" opacity="0.7">CAPTIVE</text>
      <text y="-85" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}">业主自有需求</text>
      <text y="-68" text-anchor="middle" font-size="9" fill="{INK_2}">PRINCIPLE 01</text>
    </g>
    <g transform="translate(600,300)">
      <circle r="60" fill="{INK}"/>
      <text y="-12" text-anchor="middle" font-size="32" font-weight="700" fill="{PAPER}">P2</text>
      <text y="14" text-anchor="middle" font-size="11" font-weight="700" fill="{PAPER}">复合</text>
      <text y="30" text-anchor="middle" font-size="9" fill="{PAPER}" opacity="0.7">HYBRID</text>
      <text y="-85" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}">非单一业态</text>
      <text y="-68" text-anchor="middle" font-size="9" fill="{INK_2}">PRINCIPLE 02</text>
    </g>
    <g transform="translate(900,300)">
      <circle r="60" fill="{INK_2}"/>
      <text y="-12" text-anchor="middle" font-size="32" font-weight="700" fill="{PAPER}">P3</text>
      <text y="14" text-anchor="middle" font-size="11" font-weight="700" fill="{PAPER}">合规</text>
      <text y="30" text-anchor="middle" font-size="9" fill="{PAPER}" opacity="0.7">COMPLIANT</text>
      <text y="-85" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}">点状供地 + 农文旅</text>
      <text y="-68" text-anchor="middle" font-size="9" fill="{INK_2}">PRINCIPLE 03</text>
    </g>
    <g transform="translate(450,500)">
      <circle r="50" fill="{ACCENT_BRIGHT}"/>
      <text y="-8" text-anchor="middle" font-size="22" font-weight="700" fill="{PAPER}">P4</text>
      <text y="10" text-anchor="middle" font-size="10" font-weight="700" fill="{PAPER}">克制</text>
      <text y="-72" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}">小而强 + 分期</text>
      <text y="80" text-anchor="middle" font-size="10" font-weight="600" fill="{INK}">PRINCIPLE 04 · PRUDENT</text>
    </g>
    <g transform="translate(750,500)">
      <circle r="50" fill="{INK_3}"/>
      <text y="-8" text-anchor="middle" font-size="22" font-weight="700" fill="{PAPER}">P5</text>
      <text y="10" text-anchor="middle" font-size="10" font-weight="700" fill="{PAPER}">低密度</text>
      <text y="-72" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}">300 亩森林 + 90 房</text>
      <text y="80" text-anchor="middle" font-size="10" font-weight="600" fill="{INK}">PRINCIPLE 05 · LOW-DENSITY</text>
    </g>
  </g>
</svg>
''')

# ----------------------------------------------------------------------
# 17. Hero insight (TABLEAI-HERO-3TAKEAWAYS)
# ----------------------------------------------------------------------
write('hero-3takeaways.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 700">
  <rect width="1200" height="700" fill="{PAPER}"/>
  <rect width="1200" height="700" fill="url(#noise)"/>
  <defs>
    <pattern id="noise" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.5" fill="{INK}" opacity="0.08"/>
    </pattern>
  </defs>
  <!-- Left: big stat -->
  <g transform="translate(280,350)" font-family="var(--sans-tab)" text-anchor="middle">
    <text y="-100" font-size="13" font-weight="600" fill="{ACCENT}" letter-spacing="0.18em">PROJECT SIGNAL</text>
    <line x1="-60" y1="-86" x2="60" y2="-86" stroke="{ACCENT}" stroke-width="2"/>
    <text y="0" font-size="120" font-weight="700" fill="{INK}" letter-spacing="-0.04em">30</text>
    <text y="50" font-size="14" font-weight="600" fill="{INK_2}">亩 · 点状供地上限</text>
    <text y="74" font-size="11" fill="{INK_3}">PROJECT MAX LAND USE</text>
    <text y="120" font-size="11" font-weight="600" fill="{ACCENT}">↓ COMPLIANCE BOUNDARY</text>
  </g>
  <!-- Right: 3 takeaways -->
  <g font-family="var(--sans-tab)" transform="translate(700,180)">
    <g transform="translate(0,0)">
      <rect width="380" height="100" fill="{ACCENT}" fill-opacity="0.10" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="3 2"/>
      <text x="14" y="30" font-size="11" font-weight="700" fill="{ACCENT}" letter-spacing="0.16em">C1 · 真实需求</text>
      <text x="14" y="56" font-size="13" font-weight="600" fill="{INK}">业主每年 5,000 房晚</text>
      <text x="14" y="76" font-size="11" fill="{INK_2}">~ 占稳定期 25%</text>
    </g>
    <g transform="translate(0,130)">
      <rect width="380" height="100" fill="{INK}" fill-opacity="0.04" stroke="{INK}" stroke-width="2"/>
      <text x="14" y="30" font-size="11" font-weight="700" fill="{INK}" letter-spacing="0.16em">C2 · 复合场景</text>
      <text x="14" y="56" font-size="13" font-weight="600" fill="{INK}">多业态 7 收入线</text>
      <text x="14" y="76" font-size="11" fill="{INK_2}">~ 占 GOP 85%</text>
    </g>
    <g transform="translate(0,260)">
      <rect width="380" height="100" fill="{ACCENT_BRIGHT}" fill-opacity="0.08" stroke="{ACCENT_BRIGHT}" stroke-width="2"/>
      <text x="14" y="30" font-size="11" font-weight="700" fill="{ACCENT_BRIGHT}" letter-spacing="0.16em">C3 · 克制密度</text>
      <text x="14" y="56" font-size="13" font-weight="600" fill="{INK}">90 房 / 700 亩</text>
      <text x="14" y="76" font-size="11" fill="{INK_2}">~ 0.13 房 / 亩</text>
    </g>
  </g>
  <text x="600" y="640" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{INK}" letter-spacing="0.18em">项目信号 · 30 亩 / 5000 房晚 / 7 业态</text>
</svg>
''')

# ----------------------------------------------------------------------
# 18. Map detail (太子坑森林公园 平面示意图 with overlays)
# ----------------------------------------------------------------------
write('map-tai-zi-keng.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800">
  <rect width="1200" height="800" fill="{PAPER}"/>
  <!-- Background: topographical contour-like background -->
  <g stroke="{GREY_1}" fill="none" stroke-width="0.8">
    <ellipse cx="600" cy="400" rx="450" ry="280"/>
    <ellipse cx="600" cy="400" rx="380" ry="220"/>
    <ellipse cx="600" cy="400" rx="320" ry="170"/>
    <ellipse cx="600" cy="400" rx="260" ry="120"/>
  </g>
  <!-- Forest green clusters -->
  <g fill="{ACCENT}" opacity="0.32">
    <ellipse cx="320" cy="280" rx="60" ry="40"/>
    <ellipse cx="380" cy="320" rx="50" ry="30"/>
    <ellipse cx="280" cy="350" rx="40" ry="30"/>
    <ellipse cx="500" cy="240" rx="60" ry="40"/>
    <ellipse cx="600" cy="200" rx="70" ry="40"/>
    <ellipse cx="700" cy="240" rx="55" ry="35"/>
    <ellipse cx="850" cy="280" rx="65" ry="40"/>
    <ellipse cx="920" cy="320" rx="55" ry="35"/>
    <ellipse cx="800" cy="450" rx="60" ry="40"/>
    <ellipse cx="450" cy="500" rx="55" ry="35"/>
    <ellipse cx="350" cy="520" rx="40" ry="30"/>
  </g>
  <!-- Tree icons scattered -->
  <g fill="{INK}" opacity="0.5">
    <circle cx="320" cy="290" r="3"/><circle cx="380" cy="320" r="3"/><circle cx="290" cy="350" r="3"/>
    <circle cx="500" cy="240" r="3"/><circle cx="600" cy="200" r="3"/><circle cx="700" cy="240" r="3"/>
    <circle cx="850" cy="280" r="3"/><circle cx="920" cy="320" r="3"/><circle cx="800" cy="450" r="3"/>
    <circle cx="450" cy="500" r="3"/><circle cx="350" cy="520" r="3"/>
    <circle cx="270" cy="240" r="3"/><circle cx="540" cy="170" r="3"/><circle cx="680" cy="180" r="3"/>
  </g>
  <!-- Project site boundary (dashed gold) -->
  <rect x="540" y="380" width="120" height="80" fill="{ACCENT}" fill-opacity="0.20" stroke="{ACCENT}" stroke-width="2.5" stroke-dasharray="8 4"/>
  <text x="600" y="425" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="700" fill="{INK}">项目地块</text>
  <text x="600" y="442" text-anchor="middle" font-family="var(--sans-tab)" font-size="9" fill="{INK_2}">约 30 亩 · 点状供地</text>
  <!-- Compass -->
  <g transform="translate(1100,80)">
    <circle r="30" fill="{PAPER}" stroke="{INK}"/>
    <polygon points="0,-22 5,0 0,22 -5,0" fill="{INK}"/>
    <text y="-30" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" font-weight="700" fill="{INK}">N</text>
  </g>
  <!-- Legend -->
  <g transform="translate(80,720)" font-family="var(--sans-tab)">
    <rect width="220" height="60" fill="{PAPER}" stroke="{GREY_2}"/>
    <circle cx="20" cy="20" r="5" fill="{ACCENT}" fill-opacity="0.32"/>
    <text x="36" y="24" font-size="10" fill="{INK}">现状森林 / 太子坑</text>
    <rect x="10" y="40" width="20" height="10" fill="{ACCENT}" fill-opacity="0.20" stroke="{ACCENT}" stroke-width="1.5" stroke-dasharray="3 2"/>
    <text x="36" y="49" font-size="10" fill="{INK}">项目用地 (30 亩)</text>
  </g>
  <!-- Title -->
  <text x="600" y="50" text-anchor="middle" font-family="Songti SC, STSong, serif" font-size="22" font-weight="600" fill="{INK}" letter-spacing="6">太子坑森林公园</text>
  <text x="600" y="78" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{ACCENT}" letter-spacing="0.18em">TAIZIKENG FOREST PARK · 沉香目的地选址示意</text>
  <text x="600" y="98" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{INK_3}">约 700 亩 · 森林覆盖率 97.7% · 距增城中心 6 km</text>
</svg>
''')

# ----------------------------------------------------------------------
# 19. Slide divider icon (big #)
# ----------------------------------------------------------------------
write('icon-section-break.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="{INK}"/>
  <!-- Big number -->
  <text x="400" y="380" text-anchor="middle" font-family="var(--sans-tab)" font-size="280" font-weight="700" fill="{ACCENT}" letter-spacing="-0.04em" opacity="0.8">02</text>
  <text x="400" y="500" text-anchor="middle" font-family="Songti SC, STSong, serif" font-size="48" font-weight="500" fill="{PAPER}" letter-spacing="0.2em">前言与研究</text>
  <line x1="280" y1="540" x2="520" y2="540" stroke="{ACCENT}" stroke-width="1"/>
  <text x="400" y="572" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" font-weight="600" fill="{ACCENT_BRIGHT}" letter-spacing="0.32em">INTRODUCTION · STUDY NOTES</text>
</svg>
''')

# ----------------------------------------------------------------------
# 20. Step icon
# ----------------------------------------------------------------------
write('icon-step-01.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
  <rect width="400" height="400" fill="{INK}"/>
  <circle cx="200" cy="180" r="60" fill="none" stroke="{ACCENT}" stroke-width="3"/>
  <text x="200" y="195" text-anchor="middle" font-family="var(--sans-tab)" font-size="46" font-weight="700" fill="{ACCENT}">01</text>
  <text x="200" y="280" text-anchor="middle" font-family="var(--sans-tab)" font-size="11" font-weight="600" fill="{PAPER}" letter-spacing="0.18em">AUDIT</text>
  <text x="200" y="300" text-anchor="middle" font-family="var(--sans-tab)" font-size="10" fill="{PAPER}" opacity="0.7">复盘 Q2 流程</text>
  <line x1="150" y1="320" x2="250" y2="320" stroke="{ACCENT}" stroke-width="1.5"/>
</svg>
''')

print()
print(f'Generated {len(list(OUT.glob("*.svg")))} SVG illustrations in {OUT}')
