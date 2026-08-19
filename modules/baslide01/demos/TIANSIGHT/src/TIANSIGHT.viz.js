/* ============================================================================
 * 侍天 TIANSIGHT · D3 图元库 (Visualization Primitives)
 * ----------------------------------------------------------------------------
 * 依赖：d3 v7
 * 调用：TIANSIGHT.viz.<name>(selector, data, opts)
 *
 * 六条渲染纪律（写进基类，不可绕过）：
 *   ① 分母随图走      opts.denom 强制渲染到来源条
 *   ② 中位线归高侧    阈值切分统一 ≥，图上标 ≥ 符号
 *   ③ 零值 ≠ 缺口     零值格仅在基数达阈值时标机会
 *   ④ 样本不足画斜纹  n < 阈值统一斜纹填充，不隐藏不静默
 *   ⑤ 代理指标带水印  非标准口径自动加「禁止外部对标」页脚
 *   ⑥ 合计必须闭合    分类之和 ≠ 全量 → 抛错拒绝渲染
 * ========================================================================== */

(function (global) {
'use strict';

/* ---- 设计令牌 --------------------------------------------------------- */
const T = {
  surface:'#F4F0E7', paper:'#FFFDF8', ink:'#17130D', inkSoft:'#706758',
  gold:'#76551F', goldHi:'#D4A862', goldPale:'#EFE6D2', seal:'#8C3228',
  hair:'rgba(23,19,13,.18)', hair2:'rgba(23,19,13,.34)', gridline:'rgba(118,85,31,.14)',
  serif:'"Noto Serif SC","Songti SC",serif',
  mono:'"IBM Plex Mono",ui-monospace,monospace',
  role: { '主':'#76551F', '辅':'#A8823C', '佐':'#C9A46A', '引':'#8C3228' },
  seq: ['#EFE6D2','#DFCDA6','#C9A46A','#A8823C','#87682B','#76551F','#5A3F15']
};

const fmt = {
  n:  d3.format(',.0f'),
  n1: d3.format(',.1f'),
  pct:d3.format('.1%'),
  pct0:d3.format('.0%'),
  cny:d => '¥' + d3.format(',.0f')(d),
  cnyK:d => Math.abs(d) >= 10000 ? '¥' + d3.format(',.1f')(d / 10000) + '万' : '¥' + d3.format(',.0f')(d)
};

/* ---- 通用画框 ---------------------------------------------------------- */
/* 路径长度：getTotalLength 是浏览器 SVG API，在无布局引擎的环境（jsdom、
   服务端预渲染、导出为静态图）中不存在。取不到就跳过描边动画而不是让整张图挂掉——
   动画是锦上添花，图本身才是交付物。 */
function pathLen(node) {
  try { return (node && typeof node.getTotalLength === 'function') ? node.getTotalLength() : 0; }
  catch (e) { return 0; }
}

function frame(sel, opts) {
  const o = Object.assign({ w: 900, h: 460, m: { t: 26, r: 26, b: 46, l: 62 }, denom: '', note: '', watermark: '' }, opts);
  const root = (typeof sel === 'string' || (sel && sel.nodeType === 1)) ? d3.select(sel) : sel;
  root.selectAll('*').remove();

  const wrap = root.append('div').attr('class', 'sd-viz');

  if (o.denom) wrap.append('div').attr('class', 'sd-denom').html('<span class="sd-cap">分母 / DENOMINATOR</span>' + o.denom);

  const svg = wrap.append('svg')
    .attr('viewBox', `0 0 ${o.w} ${o.h}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .attr('class', 'sd-svg')
    .attr('role', 'img');

  /* 斜纹图案：样本不足 */
  const defs = svg.append('defs');
  defs.append('pattern').attr('id', 'sd-hatch').attr('width', 6).attr('height', 6)
      .attr('patternUnits', 'userSpaceOnUse').attr('patternTransform', 'rotate(45)')
      .append('line').attr('x1', 0).attr('y1', 0).attr('x2', 0).attr('y2', 6)
      .attr('stroke', T.gold).attr('stroke-width', 2).attr('opacity', .45);
  /* 网点图案：机会象限 */
  const dots = defs.append('pattern').attr('id','sd-dots').attr('width',7).attr('height',7).attr('patternUnits','userSpaceOnUse');
  dots.append('circle').attr('cx',2).attr('cy',2).attr('r',1).attr('fill',T.gold).attr('opacity',.28);

  const g = svg.append('g').attr('transform', `translate(${o.m.l},${o.m.t})`);
  const iw = o.w - o.m.l - o.m.r, ih = o.h - o.m.t - o.m.b;

  if (o.watermark) {
    svg.append('text').attr('x', o.w - 10).attr('y', 16).attr('text-anchor', 'end')
       .attr('class', 'sd-watermark').text(o.watermark);
  }
  if (o.note) wrap.append('div').attr('class', 'sd-note').text(o.note);

  return { root, wrap, svg, g, iw, ih, o, defs };
}

function axisStyle(g) {
  g.selectAll('path,line').attr('stroke', T.hair);
  g.selectAll('text').attr('fill', T.inkSoft).attr('font-family', T.mono).attr('font-size', 10.5);
  return g;
}

/* 轻量 tooltip */
let TIP;
function tip() {
  if (!TIP) TIP = d3.select('body').append('div').attr('class', 'sd-tip').style('opacity', 0);
  return TIP;
}
function showTip(html, ev) {
  tip().html(html).style('opacity', 1)
       .style('left', (ev.pageX + 14) + 'px').style('top', (ev.pageY - 12) + 'px');
}
const hideTip = () => tip().style('opacity', 0);

/* 纪律 ⑥：合计闭合校验 */
/* 纪律⑥ 合计必须闭合。
   parts 可以是数值数组，也可以是对象数组 + 取值器；label 只用于报错文案。
   校验失败直接抛错——「拒绝渲染」比「渲染一张少了 35 个 SKU 的图」安全得多。 */
function assertClosed(parts, total, accessor, label) {
  if (typeof accessor === 'string') { label = accessor; accessor = null; }
  const s = d3.sum(parts, accessor || (d => (typeof d === 'number' ? d : (d && d.value) || 0)));
  if (total != null && Math.abs(s - total) > 1e-6) {
    throw new Error(`[G-SUM-CLOSE] ${label || '各分类'}之和 ${(+s.toFixed(4))} ≠ 全量 ${total}，` +
                    `差额 ${(+(total - s).toFixed(4))}。图元拒绝渲染。`);
  }
  return s;
}

/* ==========================================================================
 * 1. waterfall —— 三路对账瀑布 / 效益测算瀑布  (A02 · A57)
 *    data: [{label, value, type:'base'|'delta'|'total'|'range', lo, hi}]
 * ======================================================================== */
function waterfall(sel, data, opts) {
  const F = frame(sel, Object.assign({ h: 440 }, opts));
  const { g, iw, ih } = F;

  let cum = 0;
  const bars = data.map(d => {
    if (d.type === 'base' || d.type === 'total' || d.type === 'range') {
      const b = { ...d, y0: 0, y1: d.type === 'range' ? d.hi : d.value };
      cum = d.type === 'range' ? d.hi : d.value; return b;
    }
    const b = { ...d, y0: cum, y1: cum + d.value }; cum += d.value; return b;
  });

  const maxV = d3.max(bars, b => Math.max(b.y0, b.y1, b.hi || 0)) * 1.12;
  const x = d3.scaleBand().domain(data.map(d => d.label)).range([0, iw]).padding(.34);
  const y = d3.scaleLinear().domain([0, maxV]).range([ih, 0]);

  g.append('g').call(d3.axisLeft(y).ticks(6).tickFormat(fmt.cnyK).tickSize(-iw))
   .call(axisStyle).selectAll('.tick line').attr('stroke', T.gridline);
  g.append('g').attr('transform', `translate(0,${ih})`).call(d3.axisBottom(x)).call(axisStyle)
   .selectAll('text').attr('font-family', T.serif).attr('font-size', 11.5).attr('fill', T.ink);

  const grp = g.selectAll('.wf').data(bars).join('g').attr('class', 'wf');

  /* 连接虚线 */
  grp.filter((d, i) => i < bars.length - 1).append('line')
     .attr('x1', d => x(d.label) + x.bandwidth()).attr('x2', (d, i) => x(bars[i + 1].label))
     .attr('y1', d => y(d.y1)).attr('y2', d => y(d.y1))
     .attr('stroke', T.hair2).attr('stroke-dasharray', '2 3');

  grp.append('rect')
     .attr('x', d => x(d.label)).attr('width', x.bandwidth())
     .attr('y', d => y(Math.max(d.y0, d.y1)))
     .attr('height', d => Math.max(1.5, Math.abs(y(d.y0) - y(d.y1))))
     .attr('fill', d => d.type === 'delta' ? (d.value < 0 ? T.seal : T.goldHi)
                      : d.type === 'range' ? 'url(#sd-hatch)' : T.gold)
     .attr('stroke', d => d.type === 'range' ? T.gold : 'none')
     .attr('opacity', 0)
     .on('mousemove', (e, d) => showTip(`<b>${d.label}</b><br>${fmt.cny(d.value)}${d.sub ? '<br>' + d.sub : ''}`, e))
     .on('mouseleave', hideTip)
     .transition().duration(750).delay((d, i) => i * 110).attr('opacity', 1);

  /* 区间终柱的上下界标注（A57：给区间而非点值） */
  grp.filter(d => d.type === 'range').each(function (d) {
    d3.select(this).append('line').attr('x1', x(d.label) - 6).attr('x2', x(d.label) + x.bandwidth() + 6)
      .attr('y1', y(d.lo)).attr('y2', y(d.lo)).attr('stroke', T.gold).attr('stroke-width', 1.5);
    d3.select(this).append('text').attr('x', x(d.label) + x.bandwidth() / 2).attr('y', y(d.lo) + 14)
      .attr('text-anchor', 'middle').attr('class', 'sd-num').text(fmt.cnyK(d.lo));
  });

  grp.append('text')
     .attr('x', d => x(d.label) + x.bandwidth() / 2)
     .attr('y', d => y(Math.max(d.y0, d.y1)) - 7)
     .attr('text-anchor', 'middle').attr('class', 'sd-num')
     .attr('fill', d => d.type === 'delta' && d.value < 0 ? T.seal : T.ink)
     .text(d => d.type === 'range' ? fmt.cnyK(d.hi) : (d.type === 'delta' && d.value > 0 ? '+' : '') + fmt.cnyK(d.value))
     .attr('opacity', 0).transition().duration(600).delay((d, i) => 300 + i * 110).attr('opacity', 1);

  return F;
}

/* ==========================================================================
 * 2. paretoDual —— 帕累托双轴，80% 交点实算标注  (A10)
 *    data: [{name, value}]  已降序或内部排序
 * ======================================================================== */
function paretoDual(sel, data, opts) {
  const o = Object.assign({ h: 460, threshold: .8, colorBy: null }, opts);
  const F = frame(sel, o); const { g, iw, ih } = F;
  const rows = [...data].sort((a, b) => b.value - a.value);
  const total = d3.sum(rows, d => d.value);
  let acc = 0; rows.forEach(d => { acc += d.value; d.cum = acc / total; });
  const idx = rows.findIndex(d => d.cum >= o.threshold);        /* 纪律：实算，不目测 */

  const x = d3.scaleBand().domain(rows.map((d, i) => i)).range([0, iw]).padding(.12);
  const y = d3.scaleLinear().domain([0, d3.max(rows, d => d.value) * 1.05]).range([ih, 0]);
  const y2 = d3.scaleLinear().domain([0, 1]).range([ih, 0]);

  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(fmt.cnyK).tickSize(-iw)).call(axisStyle)
   .selectAll('.tick line').attr('stroke', T.gridline);
  g.append('g').attr('transform', `translate(${iw},0)`).call(d3.axisRight(y2).ticks(5).tickFormat(fmt.pct0)).call(axisStyle);

  g.selectAll('.bar').data(rows).join('rect').attr('class', 'bar')
   .attr('x', (d, i) => x(i)).attr('width', x.bandwidth())
   .attr('y', ih).attr('height', 0)
   .attr('fill', (d, i) => o.colorBy ? o.colorBy(d, i) : (i <= idx ? T.gold : T.goldPale))
   .on('mousemove', (e, d, i) => showTip(`<b>${d.name}</b><br>${fmt.cny(d.value)} · 累计 ${fmt.pct(d.cum)}`, e))
   .on('mouseleave', hideTip)
   .transition().duration(700).delay((d, i) => i * 6)
   .attr('y', d => y(d.value)).attr('height', d => ih - y(d.value));

  const line = d3.line().x((d, i) => x(i) + x.bandwidth() / 2).y(d => y2(d.cum)).curve(d3.curveMonotoneX);
  const path = g.append('path').datum(rows).attr('fill', 'none').attr('stroke', T.seal).attr('stroke-width', 1.8).attr('d', line);
  const L = pathLen(path.node());
  if (L) path.attr('stroke-dasharray', `${L} ${L}`).attr('stroke-dashoffset', L)
             .transition().duration(1100).delay(300).attr('stroke-dashoffset', 0);

  /* 80% 交点：横线 + 竖线 + 圆点 + 坐标标注 */
  const cx = x(idx) + x.bandwidth() / 2, cy = y2(rows[idx].cum);
  const mark = g.append('g').attr('opacity', 0);
  mark.append('line').attr('x1', 0).attr('x2', cx).attr('y1', cy).attr('y2', cy)
      .attr('stroke', T.gold).attr('stroke-dasharray', '4 3');
  mark.append('line').attr('x1', cx).attr('x2', cx).attr('y1', cy).attr('y2', ih)
      .attr('stroke', T.gold).attr('stroke-dasharray', '4 3');
  mark.append('circle').attr('cx', cx).attr('cy', cy).attr('r', 5).attr('fill', T.paper)
      .attr('stroke', T.seal).attr('stroke-width', 2);
  mark.append('text').attr('x', cx + 10).attr('y', cy - 10).attr('class', 'sd-callout')
      .text(`第 ${idx + 1} 款 / 共 ${rows.length} 款 → 累计 ${fmt.pct(rows[idx].cum)}`);
  mark.transition().duration(500).delay(1300).attr('opacity', 1);

  F.p80 = { index: idx + 1, cum: rows[idx].cum, total: rows.length };
  return F;
}

/* ==========================================================================
 * 3. quadrant —— 四象限散点  (A17 · A24 · A43 · A56)
 *    data: [{name, x, y, r, group}]
 * ======================================================================== */
function quadrant(sel, data, opts) {
  const o = Object.assign({
    h: 500, xLabel: 'X', yLabel: 'Y', xLog: false,
    xCut: null, yCut: null, quadNames: ['明星品', '利润黑马', '淘汰候选', '流量品'],
    xFmt: fmt.n1, yFmt: fmt.pct, opportunityQuad: 1
  }, opts);
  const F = frame(sel, o); const { g, iw, ih } = F;

  const xCut = o.xCut != null ? o.xCut : d3.median(data, d => d.x);
  const yCut = o.yCut != null ? o.yCut : d3.median(data, d => d.y);

  const x = (o.xLog ? d3.scaleLog() : d3.scaleLinear())
    .domain(o.xLog ? [Math.max(0.1, d3.min(data, d => d.x) * .8), d3.max(data, d => d.x) * 1.15]
                   : [0, d3.max(data, d => d.x) * 1.08]).range([0, iw]).nice();
  const y = d3.scaleLinear().domain(d3.extent(data, d => d.y)).nice().range([ih, 0]);
  const r = d3.scaleSqrt().domain([0, d3.max(data, d => d.r || 1)]).range([3, 26]);

  /* 象限底色：机会象限用网点纹理 */
  const quads = [
    { x0: x(xCut), x1: iw, y0: 0, y1: y(yCut), i: 0 },
    { x0: 0, x1: x(xCut), y0: 0, y1: y(yCut), i: 1 },
    { x0: 0, x1: x(xCut), y0: y(yCut), y1: ih, i: 2 },
    { x0: x(xCut), x1: iw, y0: y(yCut), y1: ih, i: 3 }
  ];
  g.selectAll('.q').data(quads).join('rect').attr('class', 'q')
   .attr('x', d => d.x0).attr('y', d => d.y0)
   .attr('width', d => Math.max(0, d.x1 - d.x0)).attr('height', d => Math.max(0, d.y1 - d.y0))
   .attr('fill', d => d.i === o.opportunityQuad ? 'url(#sd-dots)' : (d.i % 2 ? 'rgba(118,85,31,.03)' : 'transparent'));

  g.append('g').call(d3.axisLeft(y).ticks(6).tickFormat(o.yFmt).tickSize(-iw)).call(axisStyle)
   .selectAll('.tick line').attr('stroke', T.gridline);
  g.append('g').attr('transform', `translate(0,${ih})`)
   .call(d3.axisBottom(x).ticks(6, o.xLog ? '~s' : null).tickFormat(o.xLog ? d3.format('~s') : o.xFmt)).call(axisStyle);

  /* 中位十字 —— 纪律②：标 ≥ 符号 */
  g.append('line').attr('x1', x(xCut)).attr('x2', x(xCut)).attr('y1', 0).attr('y2', ih)
   .attr('stroke', T.gold).attr('stroke-width', 1.2).attr('stroke-dasharray', '5 4');
  g.append('line').attr('x1', 0).attr('x2', iw).attr('y1', y(yCut)).attr('y2', y(yCut))
   .attr('stroke', T.gold).attr('stroke-width', 1.2).attr('stroke-dasharray', '5 4');
  g.append('text').attr('x', x(xCut) + 5).attr('y', 12).attr('class', 'sd-cut').text(`中位 ≥ ${o.xFmt(xCut)}`);
  g.append('text').attr('x', 4).attr('y', y(yCut) - 6).attr('class', 'sd-cut').text(`中位 ≥ ${o.yFmt(yCut)}`);

  /* 象限名 + 计数 */
  const counts = [0, 0, 0, 0];
  data.forEach(d => { const q = d.x >= xCut ? (d.y >= yCut ? 0 : 3) : (d.y >= yCut ? 1 : 2); d._q = q; counts[q]++; });
  const anchors = [[iw - 6, 16, 'end'], [6, 16, 'start'], [6, ih - 8, 'start'], [iw - 6, ih - 8, 'end']];
  o.quadNames.forEach((nm, i) => {
    g.append('text').attr('x', anchors[i][0]).attr('y', anchors[i][1]).attr('text-anchor', anchors[i][2])
     .attr('class', 'sd-quad').text(`${nm} · ${counts[i]}`);
  });

  g.selectAll('.pt').data(data).join('circle').attr('class', 'pt')
   .attr('cx', d => x(d.x)).attr('cy', d => y(d.y)).attr('r', 0)
   .attr('fill', d => d.color || T.role[d.group] || T.gold).attr('fill-opacity', .62)
   .attr('stroke', T.paper).attr('stroke-width', .8)
   .on('mousemove', (e, d) => showTip(
      `<b>${d.name}</b><br>${o.xLabel} ${o.xFmt(d.x)} · ${o.yLabel} ${o.yFmt(d.y)}` +
      (d.r ? `<br>销售额 ${fmt.cnyK(d.r)}` : ''), e))
   .on('mouseleave', hideTip)
   .transition().duration(650).delay((d, i) => i * 4).attr('r', d => r(d.r || 1));

  g.append('text').attr('x', iw).attr('y', ih + 34).attr('text-anchor', 'end').attr('class', 'sd-axis-l').text(o.xLabel);
  g.append('text').attr('transform', 'rotate(-90)').attr('x', 0).attr('y', -46).attr('class', 'sd-axis-l').text(o.yLabel);

  F.cuts = { xCut, yCut, counts };
  return F;
}

/* ==========================================================================
 * 4. bubbleScatter —— 定位气泡图 + 等收入背景曲线  (A04)
 * ======================================================================== */
function bubbleScatter(sel, data, opts) {
  const o = Object.assign({ h: 480, xLabel: '日均桌数', yLabel: '桌均', isoCurves: true,
                            xFmt: fmt.n1, yFmt: fmt.cny }, opts);
  const F = frame(sel, o); const { g, iw, ih } = F;
  const x = d3.scaleLinear().domain([0, d3.max(data, d => d.x) * 1.18]).range([0, iw]).nice();
  const y = d3.scaleLinear().domain([d3.min(data, d => d.y) * .88, d3.max(data, d => d.y) * 1.08]).range([ih, 0]).nice();
  const r = d3.scaleSqrt().domain([0, d3.max(data, d => d.r)]).range([6, 42]);
  const c = d3.scaleSequential(d3.interpolateRgbBasis([T.goldPale, T.goldHi, T.gold, T.ink]))
              .domain(d3.extent(data, d => d.c || 0));

  /* 等收入曲线 xy = const —— 落在同一条线上的门店收入相同 */
  if (o.isoCurves) {
    const levels = d3.range(1, 6).map(i => d3.mean(data, d => d.x * d.y) * (0.5 + i * 0.35));
    const iso = g.append('g').attr('class', 'iso');
    levels.forEach(k => {
      const pts = d3.range(x.domain()[0] + 1, x.domain()[1], 1).map(xx => [xx, k / xx]).filter(p => p[1] >= y.domain()[0] && p[1] <= y.domain()[1]);
      if (pts.length < 2) return;
      iso.append('path').datum(pts).attr('fill', 'none').attr('stroke', T.gold).attr('stroke-opacity', .16)
         .attr('stroke-dasharray', '3 4')
         .attr('d', d3.line().x(p => x(p[0])).y(p => y(p[1])).curve(d3.curveBasis));
      const last = pts[pts.length - 1];
      iso.append('text').attr('x', x(last[0]) - 4).attr('y', y(last[1]) - 4).attr('text-anchor', 'end')
         .attr('class', 'sd-iso').text(fmt.cnyK(k) + '/日');
    });
  }

  g.append('g').call(d3.axisLeft(y).ticks(6).tickFormat(o.yFmt).tickSize(-iw)).call(axisStyle)
   .selectAll('.tick line').attr('stroke', T.gridline);
  g.append('g').attr('transform', `translate(0,${ih})`).call(d3.axisBottom(x).ticks(6)).call(axisStyle);

  const mx = d3.mean(data, d => d.x), my = d3.mean(data, d => d.y);
  g.append('line').attr('x1', x(mx)).attr('x2', x(mx)).attr('y1', 0).attr('y2', ih).attr('stroke', T.hair2).attr('stroke-dasharray', '5 4');
  g.append('line').attr('x1', 0).attr('x2', iw).attr('y1', y(my)).attr('y2', y(my)).attr('stroke', T.hair2).attr('stroke-dasharray', '5 4');

  const node = g.selectAll('.bub').data(data).join('g').attr('class', 'bub')
    .attr('transform', d => `translate(${x(d.x)},${y(d.y)})`);
  node.append('circle').attr('r', 0).attr('fill', d => c(d.c || 0)).attr('fill-opacity', .78)
      .attr('stroke', T.gold).attr('stroke-width', 1)
      .on('mousemove', (e, d) => showTip(`<b>${d.name}</b><br>${o.xLabel} ${o.xFmt(d.x)}<br>${o.yLabel} ${o.yFmt(d.y)}<br>月实收 ${fmt.cnyK(d.r)}`, e))
      .on('mouseleave', hideTip)
      .transition().duration(800).delay((d, i) => i * 70).attr('r', d => r(d.r));
  node.append('text').attr('class', 'sd-lab').attr('text-anchor', 'middle')
      .attr('dy', d => -r(d.r) - 7).text(d => d.name);

  g.append('text').attr('x', iw).attr('y', ih + 34).attr('text-anchor', 'end').attr('class', 'sd-axis-l').text(o.xLabel + ' →');
  g.append('text').attr('transform', 'rotate(-90)').attr('y', -46).attr('class', 'sd-axis-l').text('↑ ' + o.yLabel);
  return F;
}

/* ==========================================================================
 * 5. heatMatrix —— 矩阵热力 + 双边际条形  (A12 · A27 · A32 · A41 · S0-04)
 *    data: [{row, col, v, n, blank}]
 * ======================================================================== */
function heatMatrix(sel, data, opts) {
  const o = Object.assign({ h: 460, rows: null, cols: null, vFmt: fmt.cnyK, nFmt: fmt.n,
                            marginals: true, blankThreshold: 0, cellLabel: true, diagonal: false }, opts);
  const F = frame(sel, Object.assign({ m: { t: 62, r: 96, b: 56, l: 108 } }, o));
  const { g, iw, ih } = F;
  const rows = o.rows || [...new Set(data.map(d => d.row))];
  const cols = o.cols || [...new Set(data.map(d => d.col))];
  const mW = o.marginals ? 74 : 0, mH = o.marginals ? 44 : 0;
  const gw = iw - mW, gh = ih - mH;

  const x = d3.scaleBand().domain(cols).range([0, gw]).padding(.055);
  const y = d3.scaleBand().domain(rows).range([0, gh]).padding(.055);
  const maxV = d3.max(data, d => d.v) || 1;
  const col = d3.scaleQuantize().domain([0, maxV]).range(T.seq);

  const cell = g.selectAll('.cell').data(data).join('g').attr('class', 'cell')
    .attr('transform', d => `translate(${x(d.col)},${y(d.row)})`);

  cell.append('rect').attr('width', x.bandwidth()).attr('height', y.bandwidth())
    .attr('fill', d => d.v > 0 ? col(d.v) : T.paper)
    /* 纪律③：零值格只在基数达阈值时才标为缺口 */
    .attr('stroke', d => (d.v === 0 && (d.base || 0) >= o.blankThreshold) ? T.seal : T.hair)
    .attr('stroke-width', d => (d.v === 0 && (d.base || 0) >= o.blankThreshold) ? 1.6 : .6)
    .attr('stroke-dasharray', d => (d.v === 0 && (d.base || 0) >= o.blankThreshold) ? '4 3' : null)
    .attr('opacity', 0)
    .on('mousemove', (e, d) => showTip(`<b>${d.row} × ${d.col}</b><br>${o.vFmt(d.v)}${d.n != null ? '<br>' + o.nFmt(d.n) + ' SKU' : ''}`, e))
    .on('mouseleave', hideTip)
    .transition().duration(520).delay((d, i) => i * 12).attr('opacity', 1);

  if (o.diagonal) cell.filter(d => rows.indexOf(d.row) === cols.indexOf(d.col))
    .append('rect').attr('width', x.bandwidth()).attr('height', y.bandwidth())
    .attr('fill', 'none').attr('stroke', T.gold).attr('stroke-width', 2);

  if (o.cellLabel) {
    cell.append('text').attr('x', x.bandwidth() / 2).attr('y', y.bandwidth() / 2 - 2)
      .attr('text-anchor', 'middle').attr('class', 'sd-cellnum')
      .attr('fill', d => d.v > maxV * .55 ? T.paper : T.ink)
      .text(d => d.n != null ? o.nFmt(d.n) : (d.v ? o.vFmt(d.v) : ''));
    cell.filter(d => d.n != null).append('text').attr('x', x.bandwidth() / 2).attr('y', y.bandwidth() / 2 + 13)
      .attr('text-anchor', 'middle').attr('class', 'sd-cellsub')
      .attr('fill', d => d.v > maxV * .55 ? 'rgba(255,253,248,.8)' : T.inkSoft)
      .text(d => d.v ? o.vFmt(d.v) : '—');
    cell.filter(d => d.v === 0 && (d.base || 0) >= o.blankThreshold)
      .append('text').attr('x', x.bandwidth() / 2).attr('y', y.bandwidth() / 2 + 4)
      .attr('text-anchor', 'middle').attr('class', 'sd-blank').text('白地');
  }

  g.append('g').call(d3.axisLeft(y).tickSize(0)).call(axisStyle)
   .selectAll('text').attr('font-family', T.serif).attr('font-size', 12).attr('fill', T.ink);
  g.append('g').attr('transform', `translate(0,${gh})`).call(d3.axisBottom(x).tickSize(0)).call(axisStyle)
   .selectAll('text').attr('font-family', T.serif).attr('font-size', 12).attr('fill', T.ink);
  g.selectAll('.domain').remove();

  if (o.marginals) {
    const rowSum = rows.map(r => ({ k: r, v: d3.sum(data.filter(d => d.row === r), d => d.v) }));
    const colSum = cols.map(c => ({ k: c, v: d3.sum(data.filter(d => d.col === c), d => d.v) }));
    const rx = d3.scaleLinear().domain([0, d3.max(rowSum, d => d.v)]).range([0, mW - 14]);
    const cy = d3.scaleLinear().domain([0, d3.max(colSum, d => d.v)]).range([0, mH - 12]);
    const mg = g.append('g').attr('transform', `translate(${gw + 12},0)`);
    mg.selectAll('rect').data(rowSum).join('rect')
      .attr('y', d => y(d.k) + y.bandwidth() * .22).attr('height', y.bandwidth() * .56)
      .attr('width', 0).attr('fill', T.goldHi).attr('opacity', .8)
      .transition().duration(600).delay(400).attr('width', d => rx(d.v));
    const mgc = g.append('g').attr('transform', `translate(0,${gh + 30})`);
    mgc.selectAll('rect').data(colSum).join('rect')
      .attr('x', d => x(d.k) + x.bandwidth() * .22).attr('width', x.bandwidth() * .56)
      .attr('y', 0).attr('height', 0).attr('fill', T.goldHi).attr('opacity', .8)
      .transition().duration(600).delay(400).attr('height', d => cy(d.v));
  }
  return F;
}

/* ==========================================================================
 * 6. beeswarm —— 四指标分布蜂群，多轴联动  (A13–A16)
 *    axes: [{key, label, fmt, log}]   data: [{name, ...values}]
 * ======================================================================== */
function beeswarm(sel, data, axes, opts) {
  const o = Object.assign({ h: 90 * axes.length + 60 }, opts);
  const F = frame(sel, Object.assign({ m: { t: 24, r: 34, b: 34, l: 118 } }, o));
  const { g, iw } = F;
  const lane = 88;

  axes.forEach((ax, ai) => {
    const vals = data.map(d => d[ax.key]).filter(v => v != null);
    const scale = (ax.log ? d3.scaleLog() : d3.scaleLinear())
      .domain(ax.log ? [Math.max(.1, d3.min(vals)), d3.max(vals)] : [0, d3.max(vals) * 1.04])
      .range([0, iw]).nice();
    const yc = ai * lane + 40;
    const med = d3.median(vals);

    const row = g.append('g').attr('transform', `translate(0,${yc})`);
    row.append('line').attr('x1', 0).attr('x2', iw).attr('stroke', T.hair);
    row.append('g').attr('transform', 'translate(0,22)')
       .call(d3.axisBottom(scale).ticks(6, ax.log ? '~s' : null).tickFormat(ax.fmt || fmt.n1)).call(axisStyle);
    row.append('text').attr('x', -12).attr('y', 4).attr('text-anchor', 'end')
       .attr('class', 'sd-axname').text(ax.label);
    row.append('line').attr('x1', scale(med)).attr('x2', scale(med)).attr('y1', -26).attr('y2', 12)
       .attr('stroke', T.gold).attr('stroke-width', 1.3).attr('stroke-dasharray', '4 3');
    row.append('text').attr('x', scale(med) + 5).attr('y', -30).attr('class', 'sd-cut')
       .text(`中位 ${(ax.fmt || fmt.n1)(med)}`);

    const nodes = data.filter(d => d[ax.key] != null)
      .map(d => ({ ...d, _x: scale(d[ax.key]), _y: 0 }));
    d3.forceSimulation(nodes)
      .force('x', d3.forceX(d => d._x).strength(1))
      .force('y', d3.forceY(0).strength(.09))
      .force('collide', d3.forceCollide(4.2))
      .stop().tick(140);

    row.selectAll('circle').data(nodes).join('circle')
      .attr('cx', d => d.x).attr('cy', d => Math.max(-24, Math.min(10, d.y)))
      .attr('r', 3.4).attr('fill', d => T.role[d.role] || T.gold).attr('fill-opacity', .68)
      .attr('data-name', d => d.name)
      .on('mousemove', (e, d) => {
        g.selectAll('circle').attr('r', c => c.name === d.name ? 6 : 3.4)
         .attr('fill-opacity', c => c.name === d.name ? 1 : .22);
        showTip(`<b>${d.name}</b>` + axes.map(a => `<br>${a.label} ${(a.fmt || fmt.n1)(d[a.key])}`).join(''), e);
      })
      .on('mouseleave', () => { g.selectAll('circle').attr('r', 3.4).attr('fill-opacity', .68); hideTip(); });
  });
  return F;
}

/* ==========================================================================
 * 7. sankeyFlow —— 双层桑基（自实现，无外部依赖）  (A09 · S0-02)
 *    data: {nodes:[{id,side,label,color}], links:[{source,target,value,changed}]}
 * ======================================================================== */
function sankeyFlow(sel, data, opts) {
  const o = Object.assign({ h: 470, nodeW: 16, pad: 12 }, opts);
  const F = frame(sel, Object.assign({ m: { t: 26, r: 150, b: 30, l: 150 } }, o));
  const { g, iw, ih } = F;

  const L = data.nodes.filter(n => n.side === 0), R = data.nodes.filter(n => n.side === 1);
  const val = n => d3.sum(data.links.filter(l => (n.side === 0 ? l.source : l.target) === n.id), l => l.value);
  const layout = (arr) => {
    const tot = d3.sum(arr, val);
    const avail = ih - o.pad * (arr.length - 1);
    let yy = 0;
    return arr.map(n => { const h = Math.max(6, avail * val(n) / tot); const b = { ...n, y0: yy, y1: yy + h, total: val(n) }; yy += h + o.pad; return b; });
  };
  const ln = layout(L), rn = layout(R);
  const byId = Object.fromEntries([...ln, ...rn].map(n => [n.id, n]));

  const off = {};
  const links = data.links.map(l => {
    const s = byId[l.source], t = byId[l.target];
    const sh = (s.y1 - s.y0) * l.value / s.total, th = (t.y1 - t.y0) * l.value / t.total;
    const sy = s.y0 + (off['s' + l.source] = (off['s' + l.source] || 0)) ; off['s' + l.source] += sh;
    const ty = t.y0 + (off['t' + l.target] = (off['t' + l.target] || 0)) ; off['t' + l.target] += th;
    return { ...l, sy, sh, ty, th, s, t };
  });

  const x0 = 0, x1 = iw - o.nodeW;
  const ribbon = d => {
    const xa = x0 + o.nodeW, xb = x1, mid = (xa + xb) / 2;
    return `M${xa},${d.sy} C${mid},${d.sy} ${mid},${d.ty} ${xb},${d.ty}
            L${xb},${d.ty + d.th} C${mid},${d.ty + d.th} ${mid},${d.sy + d.sh} ${xa},${d.sy + d.sh} Z`;
  };

  g.selectAll('.rib').data(links).join('path').attr('class', 'rib').attr('d', ribbon)
   .attr('fill', d => d.changed ? T.gold : T.goldPale)
   .attr('fill-opacity', d => d.changed ? .62 : .38)
   .attr('stroke', 'none').attr('opacity', 0)
   .on('mousemove', (e, d) => showTip(`<b>${d.s.label} → ${d.t.label}</b><br>${fmt.cnyK(d.value)}${d.items ? '<br>' + d.items : ''}`, e))
   .on('mouseover', function () { d3.select(this).attr('fill-opacity', .85); })
   .on('mouseout', function (e, d) { d3.select(this).attr('fill-opacity', d.changed ? .62 : .38); hideTip(); })
   .transition().duration(800).delay((d, i) => i * 45).attr('opacity', 1);

  const drawNodes = (arr, xx, anchor) => {
    const n = g.selectAll(null).data(arr).join('g');
    n.append('rect').attr('x', xx).attr('y', d => d.y0).attr('width', o.nodeW)
     .attr('height', d => d.y1 - d.y0).attr('fill', d => d.color || T.gold);
    n.append('text').attr('x', anchor === 'end' ? xx - 9 : xx + o.nodeW + 9)
     .attr('y', d => (d.y0 + d.y1) / 2).attr('dy', '.32em').attr('text-anchor', anchor)
     .attr('class', 'sd-node').text(d => d.label);
    n.append('text').attr('x', anchor === 'end' ? xx - 9 : xx + o.nodeW + 9)
     .attr('y', d => (d.y0 + d.y1) / 2 + 14).attr('text-anchor', anchor)
     .attr('class', 'sd-nodesub').text(d => fmt.cnyK(d.total));
  };
  drawNodes(ln, x0, 'end'); drawNodes(rn, x1, 'start');
  return F;
}

/* ==========================================================================
 * 8. barcodeGap —— 价格轴条码 + 空档识别  (A26)
 *    data: [{name, price, qty, series}]
 * ======================================================================== */
function barcodeGap(sel, data, opts) {
  const o = Object.assign({ h: 320, step: 10, maxPrice: null, minGapWidth: 20 }, opts);
  const F = frame(sel, Object.assign({ m: { t: 40, r: 30, b: 52, l: 46 } }, o));
  const { g, iw, ih } = F;
  const maxP = o.maxPrice || d3.max(data, d => d.price) * 1.05;
  const x = d3.scaleLinear().domain([0, maxP]).range([0, iw]);
  const h = d3.scaleSqrt().domain([0, d3.max(data, d => d.qty || 1)]).range([8, ih - 30]);

  /* 空档扫描 */
  const bins = d3.range(0, maxP, o.step).map(b => ({ lo: b, hi: b + o.step, n: data.filter(d => d.price >= b && d.price < b + o.step).length }));
  const gaps = []; let cur = null;
  bins.forEach(b => {
    if (b.n === 0) { cur = cur || { lo: b.lo, hi: b.hi }; cur.hi = b.hi; }
    else { if (cur && cur.hi - cur.lo >= o.minGapWidth) gaps.push(cur); cur = null; }
  });
  if (cur && cur.hi - cur.lo >= o.minGapWidth) gaps.push(cur);

  g.selectAll('.gap').data(gaps).join('rect').attr('class', 'gap')
   .attr('x', d => x(d.lo)).attr('width', d => x(d.hi) - x(d.lo))
   .attr('y', 0).attr('height', ih - 22).attr('fill', T.seal).attr('opacity', 0)
   .transition().duration(700).delay(600).attr('opacity', .1);
  g.selectAll('.gaplab').data(gaps).join('text').attr('class', 'gaplab')
   .attr('x', d => (x(d.lo) + x(d.hi)) / 2).attr('y', 14).attr('text-anchor', 'middle')
   .attr('fill', T.seal).attr('font-size', 10).attr('font-family', T.mono)
   .text(d => `空档 ¥${d.lo}–${d.hi}`).attr('opacity', 0)
   .transition().duration(500).delay(900).attr('opacity', 1);

  g.selectAll('.bc').data(data).join('line').attr('class', 'bc')
   .attr('x1', d => x(d.price)).attr('x2', d => x(d.price))
   .attr('y1', ih - 22).attr('y2', ih - 22)
   .attr('stroke', d => d.color || T.gold).attr('stroke-width', 1.6).attr('stroke-opacity', .72)
   .on('mousemove', (e, d) => showTip(`<b>${d.name}</b><br>¥${d.price} · ${fmt.n(d.qty || 0)} 件`, e))
   .on('mouseleave', hideTip)
   .transition().duration(600).delay((d, i) => i * 5)
   .attr('y2', d => ih - 22 - h(d.qty || 1));

  g.append('g').attr('transform', `translate(0,${ih - 22})`)
   .call(d3.axisBottom(x).ticks(12).tickFormat(d => '¥' + d)).call(axisStyle);
  g.append('text').attr('x', iw).attr('y', ih + 22).attr('text-anchor', 'end').attr('class', 'sd-axis-l')
   .text(`步长 ¥${o.step} · ${data.length} SKU · 竖线高度 ∝ 销量`);

  F.gaps = gaps;
  return F;
}

/* ==========================================================================
 * 9. forceNetwork —— 连带网络  (A31)
 *    data: {nodes:[{id,r,group}], links:[{source,target,lift,support}]}
 * ======================================================================== */
function forceNetwork(sel, data, opts) {
  const o = Object.assign({ h: 520, minLift: 1.2 }, opts);
  const F = frame(sel, Object.assign({ m: { t: 14, r: 14, b: 14, l: 14 } }, o));
  const { g, iw, ih } = F;
  const nodes = data.nodes.map(d => ({ ...d }));
  const links = data.links.filter(l => l.lift >= o.minLift).map(d => ({ ...d }));

  const r = d3.scaleSqrt().domain([0, d3.max(nodes, d => d.r)]).range([5, 30]);
  const w = d3.scaleLinear().domain(d3.extent(links, d => d.support)).range([1, 9]);
  const lc = d3.scaleSequential(d3.interpolateRgbBasis([T.goldPale, T.goldHi, T.seal]))
               .domain(d3.extent(links, d => d.lift));

  const link = g.append('g').selectAll('line').data(links).join('line')
    .attr('stroke', d => lc(d.lift)).attr('stroke-width', d => w(d.support)).attr('stroke-opacity', .5);

  const node = g.append('g').selectAll('g').data(nodes).join('g').style('cursor', 'pointer');
  node.append('circle').attr('r', d => r(d.r)).attr('fill', d => T.role[d.group] || T.gold)
      .attr('fill-opacity', .82).attr('stroke', T.paper).attr('stroke-width', 1.4);
  node.append('text').attr('class', 'sd-lab').attr('text-anchor', 'middle')
      .attr('dy', d => -r(d.r) - 6).text(d => d.id);

  node.on('mouseover', (e, d) => {
    const nb = new Set(links.filter(l => l.source.id === d.id || l.target.id === d.id)
                            .flatMap(l => [l.source.id, l.target.id]));
    node.attr('opacity', n => nb.has(n.id) ? 1 : .16);
    link.attr('stroke-opacity', l => (l.source.id === d.id || l.target.id === d.id) ? .95 : .06);
    const top = links.filter(l => l.source.id === d.id || l.target.id === d.id)
                     .sort((a, b) => b.lift - a.lift).slice(0, 4)
                     .map(l => `${l.source.id === d.id ? l.target.id : l.source.id} · 提升度 ${l.lift.toFixed(2)}`).join('<br>');
    showTip(`<b>${d.id}</b><br>渗透 ${fmt.pct(d.r)}<br><span style="opacity:.7">${top}</span>`, e);
  }).on('mouseout', () => { node.attr('opacity', 1); link.attr('stroke-opacity', .5); hideTip(); });

  d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(d => 130 - d.lift * 14).strength(.42))
    .force('charge', d3.forceManyBody().strength(-320))
    .force('center', d3.forceCenter(iw / 2, ih / 2))
    .force('collide', d3.forceCollide(d => r(d.r) + 14))
    .on('tick', () => {
      link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
  return F;
}

/* ==========================================================================
 * 10. itsPlot —— 中断时间序列 + 反事实外推  (A47) ★技术含量最高
 *     data: [{date, value}]  opts.eventDate
 * ======================================================================== */
function itsPlot(sel, data, opts) {
  const o = Object.assign({ h: 420, eventDate: null, eventLabel: '替换事件', yFmt: fmt.cny }, opts);
  const F = frame(sel, Object.assign({ m: { t: 30, r: 90, b: 46, l: 66 } }, o));
  const { g, iw, ih } = F;
  const parse = d => d instanceof Date ? d : new Date(d);
  const rows = data.map(d => ({ ...d, date: parse(d.date) })).sort((a, b) => a.date - b.date);
  const ev = parse(o.eventDate);
  const pre = rows.filter(d => d.date < ev), post = rows.filter(d => d.date >= ev);

  const x = d3.scaleTime().domain(d3.extent(rows, d => d.date)).range([0, iw]);
  const y = d3.scaleLinear().domain([0, d3.max(rows, d => d.value) * 1.15]).range([ih, 0]).nice();

  /* 前段线性拟合 → 向后外推（反事实） */
  const t0 = +pre[0].date, sx = d => (+d.date - t0) / 864e5;
  const n = pre.length, sX = d3.sum(pre, sx), sY = d3.sum(pre, d => d.value);
  const sXY = d3.sum(pre, d => sx(d) * d.value), sXX = d3.sum(pre, d => sx(d) ** 2);
  const b = (n * sXY - sX * sY) / (n * sXX - sX * sX || 1), a = (sY - b * sX) / n;
  const cf = post.map(d => ({ date: d.date, value: Math.max(0, a + b * sx(d)) }));

  g.append('g').call(d3.axisLeft(y).ticks(6).tickFormat(o.yFmt).tickSize(-iw)).call(axisStyle)
   .selectAll('.tick line').attr('stroke', T.gridline);
  g.append('g').attr('transform', `translate(0,${ih})`).call(d3.axisBottom(x).ticks(8).tickFormat(d3.timeFormat('%m/%d'))).call(axisStyle);

  /* 落差面积 = 反事实 − 实际 */
  const area = d3.area().x(d => x(d.date)).y0((d, i) => y(post[i].value)).y1(d => y(d.value)).curve(d3.curveMonotoneX);
  g.append('path').datum(cf).attr('fill', T.seal).attr('opacity', 0).attr('d', area)
   .transition().duration(900).delay(1000).attr('opacity', .14);

  const line = d3.line().x(d => x(d.date)).y(d => y(d.value)).curve(d3.curveMonotoneX);
  const drawLine = (dat, color, dash, delay) => {
    const p = g.append('path').datum(dat).attr('fill', 'none').attr('stroke', color)
      .attr('stroke-width', 2).attr('stroke-dasharray', dash).attr('d', line);
    if (!dash) { const L = pathLen(p.node());
      if (L) p.attr('stroke-dasharray', `${L} ${L}`).attr('stroke-dashoffset', L)
              .transition().duration(900).delay(delay).attr('stroke-dashoffset', 0); }
    else { p.attr('opacity', 0).transition().duration(600).delay(delay).attr('opacity', .85); }
    return p;
  };
  drawLine(pre, T.gold, null, 0);
  drawLine(post, T.gold, null, 700);
  drawLine(cf, T.inkSoft, '5 4', 1000);

  g.append('line').attr('x1', x(ev)).attr('x2', x(ev)).attr('y1', -6).attr('y2', ih)
   .attr('stroke', T.seal).attr('stroke-width', 1.6);
  g.append('text').attr('x', x(ev) + 6).attr('y', -10).attr('class', 'sd-callout').attr('fill', T.seal)
   .text(`${o.eventLabel} ${d3.timeFormat('%m/%d')(ev)}`);
  const last = cf[cf.length - 1];
  g.append('text').attr('x', x(last.date) + 6).attr('y', y(last.value)).attr('class', 'sd-cut')
   .attr('fill', T.inkSoft).text('反事实：若不替换');

  const lostPct = (d3.mean(post, d => d.value) - d3.mean(cf, d => d.value)) / d3.mean(cf, d => d.value);
  F.counterfactual = { slope: b, intercept: a, lostPct };
  return F;
}

/* ==========================================================================
 * 11. bulletChart —— 识别率闸门  (A39)
 * ======================================================================== */
function bulletChart(sel, data, opts) {
  const o = Object.assign({ h: 46 * data.length + 60, target: .30, fmt: fmt.pct }, opts);
  const F = frame(sel, Object.assign({ m: { t: 26, r: 110, b: 40, l: 108 } }, o));
  const { g, iw } = F;
  const x = d3.scaleLinear().domain([0, Math.max(o.target * 1.25, d3.max(data, d => d.value) * 1.2)]).range([0, iw]);
  const rowH = 40;

  g.append('rect').attr('x', x(o.target)).attr('width', iw - x(o.target)).attr('y', -4)
   .attr('height', data.length * rowH + 8).attr('fill', T.gold).attr('opacity', .06);

  const row = g.selectAll('.bl').data(data).join('g').attr('transform', (d, i) => `translate(0,${i * rowH})`);
  row.append('text').attr('x', -12).attr('y', 16).attr('text-anchor', 'end')
     .attr('class', 'sd-axname').text(d => d.name);
  row.append('rect').attr('y', 6).attr('height', 16).attr('width', x.range()[1]).attr('fill', T.goldPale).attr('opacity', .5);
  row.append('rect').attr('y', 6).attr('height', 16).attr('width', 0)
     .attr('fill', d => d.value >= o.target ? T.gold : T.seal).attr('opacity', .85)
     .transition().duration(800).delay((d, i) => i * 90).attr('width', d => x(d.value));
  row.append('text').attr('x', d => x(d.value) + 8).attr('y', 19).attr('class', 'sd-num')
     .text(d => `${o.fmt(d.value)}  ·  距目标 ${(o.target / d.value).toFixed(1)}×`);

  g.append('line').attr('x1', x(o.target)).attr('x2', x(o.target)).attr('y1', -4)
   .attr('y2', data.length * rowH).attr('stroke', T.gold).attr('stroke-width', 2);
  g.append('text').attr('x', x(o.target)).attr('y', -10).attr('text-anchor', 'middle')
   .attr('class', 'sd-cut').text(`目标 ${o.fmt(o.target)}`);
  return F;
}

/* ==========================================================================
 * 12. divergingBar —— 3-4-2-1 达标偏离  (A21)
 * ======================================================================== */
function divergingBar(sel, data, opts) {
  const o = Object.assign({ h: 56 * data.length + 60, fmt: d => (d > 0 ? '+' : '') + d.toFixed(1) + 'pt' }, opts);
  const F = frame(sel, Object.assign({ m: { t: 30, r: 60, b: 40, l: 100 } }, o));
  const { g, iw } = F;
  const m = d3.max(data, d => Math.abs(d.delta)) * 1.2;
  const x = d3.scaleLinear().domain([-m, m]).range([0, iw]);
  const rowH = 52, mid = x(0);

  g.append('line').attr('x1', mid).attr('x2', mid).attr('y1', -8).attr('y2', data.length * rowH).attr('stroke', T.gold).attr('stroke-width', 1.6);
  g.append('text').attr('x', mid).attr('y', -14).attr('text-anchor', 'middle').attr('class', 'sd-cut').text('理想结构');

  const row = g.selectAll('.db').data(data).join('g').attr('transform', (d, i) => `translate(0,${i * rowH})`);
  row.append('text').attr('x', -12).attr('y', 20).attr('text-anchor', 'end').attr('class', 'sd-axname')
     .text(d => `${d.name} ${d.actual.toFixed(1)}% / ${d.ideal}%`);
  row.append('rect').attr('y', 6).attr('height', 22)
     .attr('x', d => d.delta < 0 ? mid : mid).attr('width', 0)
     .attr('fill', d => d.delta < 0 ? T.seal : T.gold).attr('opacity', .78)
     .transition().duration(750).delay((d, i) => i * 100)
     .attr('x', d => d.delta < 0 ? x(d.delta) : mid)
     .attr('width', d => Math.abs(x(d.delta) - mid));
  row.append('text').attr('x', d => d.delta < 0 ? x(d.delta) - 8 : x(d.delta) + 8)
     .attr('y', 22).attr('text-anchor', d => d.delta < 0 ? 'end' : 'start')
     .attr('class', 'sd-num').attr('fill', d => d.delta < 0 ? T.seal : T.gold).text(d => o.fmt(d.delta));

  /* 对称性弧线：缺配与超配数量相等 → 存在「本该培养成必售、实际掉进长尾」的产品 */
  const pos = data.map((d, i) => ({ ...d, i })).filter(d => d.delta > 0).sort((a, b) => b.delta - a.delta)[0];
  const neg = data.map((d, i) => ({ ...d, i })).filter(d => d.delta < 0).sort((a, b) => a.delta - b.delta)[0];
  if (pos && neg && Math.abs(Math.abs(pos.delta) - Math.abs(neg.delta)) < 1.5) {
    const y1 = pos.i * rowH + 17, y2 = neg.i * rowH + 17;
    g.append('path').attr('fill', 'none').attr('stroke', T.gold).attr('stroke-width', 1.2).attr('stroke-dasharray', '3 3')
     .attr('d', `M${x(pos.delta) + 4},${y1} C${x(pos.delta) + 62},${y1} ${x(neg.delta) - 62},${y2} ${x(neg.delta) - 4},${y2}`)
     .attr('opacity', 0).transition().duration(700).delay(900).attr('opacity', .8);
    g.append('text').attr('x', iw / 2).attr('y', (y1 + y2) / 2 - 8).attr('text-anchor', 'middle')
     .attr('class', 'sd-callout').text('数量对称 → 一批本该培养成必售的产品掉进了长尾')
     .attr('opacity', 0).transition().duration(600).delay(1200).attr('opacity', 1);
  }
  return F;
}

/* ==========================================================================
 * 13. lollipop —— 系列效率指数（对数轴 + 基准线 1.0）  (A22)
 * ======================================================================== */
function lollipop(sel, data, opts) {
  const o = Object.assign({ h: 34 * data.length + 70, baseline: 1, log: true }, opts);
  const F = frame(sel, Object.assign({ m: { t: 28, r: 78, b: 42, l: 138 } }, o));
  const { g, iw } = F;
  const rows = [...data].sort((a, b) => b.value - a.value);
  const x = (o.log ? d3.scaleLog() : d3.scaleLinear())
    .domain([d3.min(rows, d => d.value) * .7, d3.max(rows, d => d.value) * 1.25]).range([0, iw]);
  const r = d3.scaleSqrt().domain([0, d3.max(rows, d => d.n || 1)]).range([4, 14]);
  const rowH = 30;

  g.append('line').attr('x1', x(o.baseline)).attr('x2', x(o.baseline)).attr('y1', -10)
   .attr('y2', rows.length * rowH).attr('stroke', T.gold).attr('stroke-width', 1.6).attr('stroke-dasharray', '5 4');
  g.append('text').attr('x', x(o.baseline)).attr('y', -16).attr('text-anchor', 'middle').attr('class', 'sd-cut').text('基准 1.0');

  const row = g.selectAll('.lp').data(rows).join('g').attr('transform', (d, i) => `translate(0,${i * rowH + 8})`);
  row.append('text').attr('x', -12).attr('y', 4).attr('text-anchor', 'end').attr('class', 'sd-axname').text(d => d.name);
  row.append('line').attr('x1', x(o.baseline)).attr('x2', x(o.baseline)).attr('y1', 0).attr('y2', 0)
     .attr('stroke', d => d.value < o.baseline ? T.seal : T.gold).attr('stroke-width', 1.6).attr('opacity', .5)
     .transition().duration(700).delay((d, i) => i * 55).attr('x2', d => x(d.value));
  row.append('circle').attr('cx', x(o.baseline)).attr('cy', 0).attr('r', d => r(d.n || 1))
     .attr('fill', d => d.value < o.baseline ? T.seal : T.gold).attr('fill-opacity', .82)
     .on('mousemove', (e, d) => showTip(`<b>${d.name}</b><br>效率 ${d.value.toFixed(2)}<br>${d.n} SKU`, e))
     .on('mouseleave', hideTip)
     .transition().duration(700).delay((d, i) => i * 55).attr('cx', d => x(d.value));
  row.append('text').attr('x', d => x(d.value)).attr('y', -12).attr('text-anchor', 'middle')
     .attr('class', 'sd-num').text(d => d.value.toFixed(2))
     .attr('opacity', 0).transition().duration(400).delay((d, i) => 500 + i * 55).attr('opacity', 1);

  g.append('g').attr('transform', `translate(0,${rows.length * rowH + 8})`)
   .call(d3.axisBottom(x).ticks(6, '~g')).call(axisStyle);
  return F;
}

/* ==========================================================================
 * 14. histCumulative —— 直方 + 累计曲线  (A05 · A36 · A37)
 * ======================================================================== */
function histCumulative(sel, data, opts) {
  const o = Object.assign({ h: 400, xLabel: '', valueFmt: fmt.n, median: null, mean: null,
                            barKey: 'share', cumKey: 'cum' }, opts);
  const F = frame(sel, Object.assign({ m: { t: 30, r: 56, b: 52, l: 58 } }, o));
  const { g, iw, ih } = F;
  const x = d3.scaleBand().domain(data.map(d => d.label)).range([0, iw]).padding(.22);
  const y = d3.scaleLinear().domain([0, d3.max(data, d => d[o.barKey]) * 1.15]).range([ih, 0]);
  const y2 = d3.scaleLinear().domain([0, 1]).range([ih, 0]);

  g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(fmt.pct0).tickSize(-iw)).call(axisStyle)
   .selectAll('.tick line').attr('stroke', T.gridline);
  g.append('g').attr('transform', `translate(${iw},0)`).call(d3.axisRight(y2).ticks(5).tickFormat(fmt.pct0)).call(axisStyle);
  g.append('g').attr('transform', `translate(0,${ih})`).call(d3.axisBottom(x)).call(axisStyle)
   .selectAll('text').attr('font-family', T.serif).attr('font-size', 11.5).attr('fill', T.ink);

  g.selectAll('.hb').data(data).join('rect').attr('class', 'hb')
   .attr('x', d => x(d.label)).attr('width', x.bandwidth()).attr('y', ih).attr('height', 0)
   .attr('fill', d => d.highlight ? T.gold : T.goldPale)
   .attr('stroke', d => d.highlight ? T.gold : 'none')
   .on('mousemove', (e, d) => showTip(`<b>${d.label}</b><br>${fmt.pct(d[o.barKey])}${d.n ? '<br>' + fmt.n(d.n) : ''}`, e))
   .on('mouseleave', hideTip)
   .transition().duration(700).delay((d, i) => i * 55)
   .attr('y', d => y(d[o.barKey])).attr('height', d => ih - y(d[o.barKey]));

  if (data[0][o.cumKey] != null) {
    const line = d3.line().x(d => x(d.label) + x.bandwidth() / 2).y(d => y2(d[o.cumKey])).curve(d3.curveMonotoneX);
    const p = g.append('path').datum(data).attr('fill', 'none').attr('stroke', T.seal).attr('stroke-width', 1.8).attr('d', line);
    const L = pathLen(p.node());
    if (L) p.attr('stroke-dasharray', `${L} ${L}`).attr('stroke-dashoffset', L)
            .transition().duration(1000).delay(400).attr('stroke-dashoffset', 0);
  }
  /* 中位与均值双竖线：右偏即证明「平均数骗人」 */
  [['median', o.median, T.gold, '中位'], ['mean', o.mean, T.inkSoft, '均值']].forEach(([k, v, c, lab]) => {
    if (v == null) return;
    const i = data.findIndex(d => d.upper != null && v <= d.upper);
    const px = i < 0 ? iw : x(data[i].label) + x.bandwidth() / 2;
    g.append('line').attr('x1', px).attr('x2', px).attr('y1', 0).attr('y2', ih)
     .attr('stroke', c).attr('stroke-width', 1.2).attr('stroke-dasharray', '4 3');
    g.append('text').attr('x', px + 4).attr('y', k === 'median' ? 12 : 26).attr('class', 'sd-cut')
     .attr('fill', c).text(`${lab} ${o.valueFmt(v)}`);
  });
  return F;
}

/* ==========================================================================
 * 15. slopeBump —— 斜率图 / 凹凸图  (A12 · A48)
 *     data: [{name, values:[{t, rank|value}]}]
 * ======================================================================== */
function slopeBump(sel, data, opts) {
  const o = Object.assign({ h: 460, key: 'rank', invert: true, highlightDelta: 5, tFmt: d => d }, opts);
  const F = frame(sel, Object.assign({ m: { t: 34, r: 168, b: 40, l: 168 } }, o));
  const { g, iw, ih } = F;
  const ts = data[0].values.map(v => v.t);
  const x = d3.scalePoint().domain(ts).range([0, iw]);
  const all = data.flatMap(d => d.values.map(v => v[o.key]));
  const y = d3.scaleLinear().domain(o.invert ? [d3.max(all), d3.min(all)] : d3.extent(all)).range([ih, 0]).nice();

  ts.forEach(t => {
    g.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', 0).attr('y2', ih).attr('stroke', T.hair);
    g.append('text').attr('x', x(t)).attr('y', -12).attr('text-anchor', 'middle').attr('class', 'sd-cut').text(o.tFmt(t));
  });

  const line = d3.line().x(d => x(d.t)).y(d => y(d[o.key])).curve(d3.curveMonotoneX);
  const delta = d => d.values[0][o.key] - d.values[d.values.length - 1][o.key];

  const s = g.selectAll('.sl').data(data).join('g');
  s.append('path').datum(d => d.values).attr('fill', 'none')
   .attr('stroke', (d, i) => Math.abs(delta(data[i])) >= o.highlightDelta ? (delta(data[i]) > 0 ? T.gold : T.seal) : T.hair2)
   .attr('stroke-width', (d, i) => Math.abs(delta(data[i])) >= o.highlightDelta ? 2.4 : 1)
   .attr('d', line).attr('opacity', 0).transition().duration(800).delay((d, i) => i * 35).attr('opacity', .9);
  s.selectAll('circle').data(d => d.values.map(v => ({ ...v, name: d.name }))).join('circle')
   .attr('cx', d => x(d.t)).attr('cy', d => y(d[o.key])).attr('r', 3.4).attr('fill', T.paper)
   .attr('stroke', T.gold).attr('stroke-width', 1.4);
  s.append('text').attr('x', -10).attr('y', d => y(d.values[0][o.key])).attr('dy', '.32em')
   .attr('text-anchor', 'end').attr('class', 'sd-lab').text(d => d.name);
  s.append('text').attr('x', iw + 10).attr('y', d => y(d.values[d.values.length - 1][o.key])).attr('dy', '.32em')
   .attr('class', 'sd-lab').attr('fill', d => Math.abs(delta(d)) >= o.highlightDelta ? T.gold : T.inkSoft)
   .text(d => d.name + (Math.abs(delta(d)) >= o.highlightDelta ? `  ${delta(d) > 0 ? '↑' : '↓'}${Math.abs(delta(d))}` : ''));
  return F;
}

/* ==========================================================================
 * 16. upsetPlot —— 条件命中组合  (A18 · A03)
 *     data: {sets:[{key,label}], combos:[{keys:[], n, amount}]}
 * ======================================================================== */
function upsetPlot(sel, data, opts) {
  const o = Object.assign({ h: 420 }, opts);
  const F = frame(sel, Object.assign({ m: { t: 26, r: 96, b: 30, l: 130 } }, o));
  const { g, iw, ih } = F;
  const combos = [...data.combos].sort((a, b) => b.n - a.n);
  const barH = ih * .58, dotH = ih - barH - 16;
  const x = d3.scaleBand().domain(combos.map((d, i) => i)).range([0, iw]).padding(.28);
  const y = d3.scaleLinear().domain([0, d3.max(combos, d => d.n) * 1.15]).range([barH, 0]);
  const ys = d3.scalePoint().domain(data.sets.map(s => s.key)).range([barH + 26, barH + 26 + dotH - 20]);

  g.append('g').call(d3.axisLeft(y).ticks(5).tickSize(-iw)).call(axisStyle)
   .selectAll('.tick line').attr('stroke', T.gridline);

  g.selectAll('.ub').data(combos).join('rect')
   .attr('x', (d, i) => x(i)).attr('width', x.bandwidth()).attr('y', barH).attr('height', 0)
   .attr('fill', d => d.keys.length >= 3 ? T.seal : T.gold).attr('opacity', .82)
   .on('mousemove', (e, d) => showTip(`命中 ${d.keys.length} 条<br><b>${d.n} 款</b>${d.amount ? '<br>' + fmt.cnyK(d.amount) : ''}`, e))
   .on('mouseleave', hideTip)
   .transition().duration(700).delay((d, i) => i * 70).attr('y', d => y(d.n)).attr('height', d => barH - y(d.n));
  g.selectAll('.ubl').data(combos).join('text')
   .attr('x', (d, i) => x(i) + x.bandwidth() / 2).attr('y', d => y(d.n) - 7)
   .attr('text-anchor', 'middle').attr('class', 'sd-num').text(d => d.n);

  data.sets.forEach(s => {
    g.append('text').attr('x', -12).attr('y', ys(s.key)).attr('dy', '.32em').attr('text-anchor', 'end')
     .attr('class', 'sd-axname').text(s.label);
    g.append('line').attr('x1', 0).attr('x2', iw).attr('y1', ys(s.key)).attr('y2', ys(s.key)).attr('stroke', T.hair);
  });
  combos.forEach((c, i) => {
    const cx = x(i) + x.bandwidth() / 2;
    const on = data.sets.filter(s => c.keys.includes(s.key));
    if (on.length > 1) g.append('line').attr('x1', cx).attr('x2', cx)
      .attr('y1', ys(on[0].key)).attr('y2', ys(on[on.length - 1].key)).attr('stroke', T.gold).attr('stroke-width', 2);
    data.sets.forEach(s => g.append('circle').attr('cx', cx).attr('cy', ys(s.key)).attr('r', 5)
      .attr('fill', c.keys.includes(s.key) ? T.gold : T.hair));
  });
  return F;
}

/* ==========================================================================
 * 17. treemapNest —— 区域效率树图（面积=收入，色=效率）  (A34)
 * ======================================================================== */
function treemapNest(sel, data, opts) {
  const o = Object.assign({ h: 460, minSample: 30, colorLabel: '元/桌/小时' }, opts);
  const F = frame(sel, Object.assign({ m: { t: 10, r: 10, b: 10, l: 10 } }, o));
  const { g, iw, ih } = F;
  const root = d3.hierarchy(data).sum(d => d.value).sort((a, b) => b.value - a.value);
  d3.treemap().size([iw, ih]).paddingInner(2).paddingTop(20).round(true)(root);
  const eff = root.leaves().map(d => d.data.eff).filter(v => v != null);
  const c = d3.scaleQuantize().domain(d3.extent(eff)).range(T.seq);

  const leaf = g.selectAll('.lf').data(root.leaves()).join('g').attr('transform', d => `translate(${d.x0},${d.y0})`);
  leaf.append('rect').attr('width', d => d.x1 - d.x0).attr('height', d => d.y1 - d.y0)
      .attr('fill', d => d.data.n != null && d.data.n < o.minSample ? 'url(#sd-hatch)' : c(d.data.eff))
      .attr('stroke', T.paper).attr('opacity', 0)
      .on('mousemove', (e, d) => showTip(`<b>${d.data.name}</b><br>收入 ${fmt.cnyK(d.data.value)}<br>${o.colorLabel} ${fmt.cny(d.data.eff)}<br>桌数 ${fmt.n(d.data.n)}${d.data.n < o.minSample ? ' <span style="color:#D4A862">样本不足</span>' : ''}`, e))
      .on('mouseleave', hideTip)
      .transition().duration(650).delay((d, i) => i * 22).attr('opacity', 1);
  leaf.filter(d => (d.x1 - d.x0) > 62 && (d.y1 - d.y0) > 30).each(function (d) {
    const sel2 = d3.select(this), dark = c(d.data.eff) === T.seq[T.seq.length - 1] || c(d.data.eff) === T.seq[T.seq.length - 2];
    sel2.append('text').attr('x', 6).attr('y', 15).attr('class', 'sd-lab')
        .attr('fill', dark ? T.paper : T.ink).text(d.data.name);
    sel2.append('text').attr('x', 6).attr('y', 30).attr('class', 'sd-cellsub')
        .attr('fill', dark ? 'rgba(255,253,248,.85)' : T.inkSoft).text(fmt.cny(d.data.eff));
  });
  g.selectAll('.pn').data(root.children || []).join('text').attr('class', 'sd-node')
   .attr('x', d => d.x0 + 4).attr('y', d => d.y0 + 14).text(d => d.data.name);
  return F;
}

/* ==========================================================================
 * 18. radarChart —— 数据完备度雷达（双层：实测 vs 及格线）  (A03)
 * ======================================================================== */
function radarChart(sel, data, opts) {
  const o = Object.assign({ h: 420, pass: 80, max: 100 }, opts);
  const F = frame(sel, o); const { svg, iw, ih, g } = F;
  const R = Math.min(iw, ih) / 2 - 34, cx = iw / 2, cy = ih / 2;
  const ang = i => i * 2 * Math.PI / data.length - Math.PI / 2;
  const rs = d3.scaleLinear().domain([0, o.max]).range([0, R]);
  const c = g.append('g').attr('transform', `translate(${cx},${cy})`);

  d3.range(1, 5).forEach(k => c.append('circle').attr('r', R * k / 4).attr('fill', 'none').attr('stroke', T.gridline));
  data.forEach((d, i) => {
    c.append('line').attr('x2', Math.cos(ang(i)) * R).attr('y2', Math.sin(ang(i)) * R).attr('stroke', T.gridline);
    c.append('text').attr('x', Math.cos(ang(i)) * (R + 20)).attr('y', Math.sin(ang(i)) * (R + 20))
     .attr('text-anchor', 'middle').attr('dy', '.32em').attr('class', 'sd-axname').text(d.axis);
  });

  const path = arr => d3.lineRadial().angle((d, i) => ang(i) + Math.PI / 2).radius(d => rs(d)).curve(d3.curveLinearClosed)(arr);
  c.append('path').attr('d', path(data.map(() => o.pass))).attr('fill', 'none')
   .attr('stroke', T.inkSoft).attr('stroke-dasharray', '4 3').attr('stroke-width', 1.2);
  c.append('path').attr('d', path(data.map(d => d.value)))
   .attr('fill', T.gold).attr('fill-opacity', .2).attr('stroke', T.gold).attr('stroke-width', 2)
   .attr('opacity', 0).transition().duration(800).attr('opacity', 1);
  data.forEach((d, i) => {
    const fail = d.value < o.pass;
    c.append('circle').attr('cx', Math.cos(ang(i)) * rs(d.value)).attr('cy', Math.sin(ang(i)) * rs(d.value))
     .attr('r', 4).attr('fill', fail ? T.seal : T.gold);
    c.append('text').attr('x', Math.cos(ang(i)) * (rs(d.value) - 14)).attr('y', Math.sin(ang(i)) * (rs(d.value) - 14))
     .attr('text-anchor', 'middle').attr('class', 'sd-num').attr('fill', fail ? T.seal : T.ink).text(d.value);
  });
  return F;
}

/* ==========================================================================
 * 19. stackedFlow —— 生命周期六阶段双条错位对照  (A49 · A11)
 *     data: [{name, sku, amount}]  纪律⑥：合计闭合校验
 * ======================================================================== */
function stackedFlow(sel, data, opts) {
  const o = Object.assign({ h: 300, labels: ['SKU 数占比', '销售额占比'], totalSku: null, totalAmt: null }, opts);
  if (o.totalSku != null) assertClosed(data.map(d => d.sku), o.totalSku, 'SKU');
  const F = frame(sel, Object.assign({ m: { t: 40, r: 24, b: 60, l: 96 } }, o));
  const { g, iw } = F;
  const tS = d3.sum(data, d => d.sku), tA = d3.sum(data, d => d.amount);
  const c = d3.scaleOrdinal().domain(data.map(d => d.name)).range(T.seq.slice(1));
  const barH = 58;

  [['sku', tS, 0], ['amount', tA, barH + 46]].forEach(([key, tot, yy], row) => {
    let acc = 0;
    const seg = g.selectAll(null).data(data).join('g');
    seg.append('rect').attr('y', yy).attr('height', barH)
       .attr('x', d => { const x0 = acc / tot * iw; acc += d[key]; d['_x' + row] = x0; return x0; })
       .attr('width', d => d[key] / tot * iw).attr('fill', d => c(d.name))
       .attr('stroke', T.paper).attr('opacity', 0)
       .on('mousemove', (e, d) => showTip(`<b>${d.name}</b><br>${fmt.n(d[key])}（${fmt.pct(d[key] / tot)}）`, e))
       .on('mouseleave', hideTip)
       .transition().duration(650).delay((d, i) => i * 70 + row * 250).attr('opacity', 1);
    seg.filter(d => d[key] / tot > .07).append('text')
       .attr('x', d => d['_x' + row] + d[key] / tot * iw / 2).attr('y', yy + barH / 2 + 4)
       .attr('text-anchor', 'middle').attr('class', 'sd-cellnum')
       .attr('fill', (d, i) => i > 2 ? T.paper : T.ink).text(d => fmt.pct0(d[key] / tot));
    g.append('text').attr('x', -12).attr('y', yy + barH / 2 + 4).attr('text-anchor', 'end')
     .attr('class', 'sd-axname').text(o.labels[row]);
  });

  /* 错位连接线：SKU 宽而额窄 = 占着菜单不赚钱 */
  data.forEach(d => {
    g.append('path').attr('fill', c(d.name)).attr('opacity', .16)
     .attr('d', `M${d._x0},${barH} L${d._x0 + d.sku / tS * iw},${barH}
                 L${d._x1 + d.amount / tA * iw},${barH + 46} L${d._x1},${barH + 46} Z`);
  });
  const lg = g.append('g').attr('transform', `translate(0,${barH * 2 + 76})`);
  data.forEach((d, i) => {
    const gx = i * (iw / data.length);
    lg.append('rect').attr('x', gx).attr('y', 0).attr('width', 11).attr('height', 11).attr('fill', c(d.name));
    lg.append('text').attr('x', gx + 16).attr('y', 9).attr('class', 'sd-lab').text(d.name);
  });
  g.append('text').attr('x', 0).attr('y', -16).attr('class', 'sd-cut')
   .text(`合计 ${fmt.n(tS)} = 全量 ✓（完整性纪律）`);
  return F;
}

/* ==========================================================================
 * 20. dumbbell —— 现状 → 目标  (A23)
 * ======================================================================== */
function dumbbell(sel, data, opts) {
  const o = Object.assign({ h: 32 * data.length + 60, fmt: fmt.n }, opts);
  const F = frame(sel, Object.assign({ m: { t: 34, r: 70, b: 40, l: 130 } }, o));
  const { g, iw } = F;
  const x = d3.scaleLinear().domain([0, d3.max(data, d => Math.max(d.from, d.to)) * 1.15]).range([0, iw]);
  const rowH = 30;
  const row = g.selectAll('.dm').data(data).join('g').attr('transform', (d, i) => `translate(0,${i * rowH + 8})`);
  row.append('text').attr('x', -12).attr('y', 4).attr('text-anchor', 'end').attr('class', 'sd-axname').text(d => d.name);
  row.append('line').attr('x1', d => x(d.from)).attr('x2', d => x(d.from)).attr('y1', 0).attr('y2', 0)
     .attr('stroke', d => d.to < d.from ? T.seal : T.gold).attr('stroke-width', 2.4).attr('opacity', .6)
     .transition().duration(700).delay((d, i) => i * 60).attr('x2', d => x(d.to));
  row.append('circle').attr('cx', d => x(d.from)).attr('r', 5).attr('fill', T.paper).attr('stroke', T.inkSoft).attr('stroke-width', 1.5);
  row.append('circle').attr('cx', d => x(d.from)).attr('r', 5).attr('fill', d => d.to < d.from ? T.seal : T.gold)
     .transition().duration(700).delay((d, i) => i * 60).attr('cx', d => x(d.to));
  row.append('text').attr('x', d => x(Math.max(d.from, d.to)) + 10).attr('y', 4).attr('class', 'sd-num')
     .attr('fill', d => d.to < d.from ? T.seal : T.gold)
     .text(d => `${o.fmt(d.from)} → ${o.fmt(d.to)}  (${d.to - d.from > 0 ? '+' : ''}${d.to - d.from})`);
  g.append('g').attr('transform', `translate(0,${data.length * rowH + 12})`).call(d3.axisBottom(x).ticks(6)).call(axisStyle);
  return F;
}

/* ---- 导出 -------------------------------------------------------------- */
global.TIANSIGHT = global.TIANSIGHT || {};
global.TIANSIGHT.viz = {
  T, fmt, frame, assertClosed,
  waterfall, paretoDual, quadrant, bubbleScatter, heatMatrix, beeswarm, sankeyFlow,
  barcodeGap, forceNetwork, itsPlot, bulletChart, divergingBar, lollipop,
  histCumulative, slopeBump, upsetPlot, treemapNest, radarChart, stackedFlow, dumbbell
};

})(typeof window !== 'undefined' ? window : globalThis);
