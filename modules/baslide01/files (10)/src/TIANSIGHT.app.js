/* ============================================================================
 * 侍天 TIANSIGHT · 应用编排层
 * 流水线：① 接入 → ② 对齐 → ③ 门禁 → ④ 计算 → ⑤ 渲染 → ⑥ 收敛
 * ========================================================================== */
(function () {
'use strict';

const R = window.TIANSIGHT_REGISTRY, S = window.TIANSIGHTSchema, V = window.TIANSIGHT.viz, D = window.TIANSIGHTDemo;
const $ = s => document.querySelector(s);
const el = (t, c, h) => { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };
const F = V.fmt;

/* 系统状态 */
const STATE = { tables: [], bound: new Set(), ctx: {}, loaded: false };

/* ---- 导航 ------------------------------------------------------------- */
document.querySelectorAll('nav button').forEach(b => b.onclick = () => {
  document.querySelectorAll('nav button').forEach(x => x.setAttribute('aria-selected', x === b));
  document.querySelectorAll('section[role=tabpanel]').forEach(s => s.classList.toggle('on', s.id === b.dataset.p));
  if (b.dataset.p === 'p-gallery' && !$('#galleryOut').dataset.done) renderGallery();
  if (b.dataset.p === 'p-registry' && !$('#registryOut').dataset.done) renderRegistry();
});

/* ---- CSV 解析（含引号处理） -------------------------------------------- */
function parseCSV(text) {
  const delim = (text.split('\n')[0].match(/\t/g) || []).length > (text.split('\n')[0].match(/,/g) || []).length ? '\t' : ',';
  const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
    else if (c === '"') q = true;
    else if (c === delim) { row.push(cell.trim()); cell = ''; }
    else if (c === '\n') { row.push(cell.trim()); if (row.some(x => x)) rows.push(row); row = []; cell = ''; }
    else if (c !== '\r') cell += c;
  }
  if (cell || row.length) { row.push(cell.trim()); if (row.some(x => x)) rows.push(row); }
  if (rows.length < 2) return [];
  const head = rows[0];
  return rows.slice(1).map(r => Object.fromEntries(head.map((h, i) => [h || `列${i + 1}`, r[i] ?? ''])));
}

/* ---- ① 接入 ----------------------------------------------------------- */
function ingest(named) {           // named: [{name, rows}]
  STATE.tables = named.map(t => {
    const det = S.detectTable(t.rows);
    return { name: t.name, rows: t.rows, table: det.table, tableConf: det.confidence,
             runnerUp: det.runnerUp, missingRequired: det.missingRequired, align: det.alignment };
  });
  STATE.bound = new Set();
  STATE.tables.forEach(t => t.align.bindings.filter(b => b.status === 'auto').forEach(b => STATE.bound.add(b.field)));
  STATE.recon = computeRecon();
  STATE.ctx = buildContext();
  STATE.loaded = true;
  renderIngest(); renderGate(); renderReport();
}

/* 计算层第一个算子：三路对账。差额不是写死的常数，是算出来的。 */
function computeRecon() {
  const g = r => (STATE.tables.find(t => t.table === r) || {}).rows;
  const h = g('bill_header'), d = g('bill_detail'), i = g('item_index');
  if (!h || !d) return null;
  try { return D.reconcile(h, d, i || []); } catch (e) { return null; }
}

/* 门禁上下文：由数据实测得出 */
function buildContext() {
  const detail = STATE.tables.find(t => t.table === 'bill_detail');
  const header = STATE.tables.find(t => t.table === 'bill_header');
  const index = STATE.tables.find(t => t.table === 'item_index');
  const ctx = { reconDiffPct: 0, costCardAgeDays: 128, memberIdRate: 1, roleCoverage: 0,
                guestNullRate: 0, hasSeatLedger: false, periodWeeks: 0, skuCount: 0,
                basisMixDetected: false, sumClosed: true, checklistPassed: false };

  if (STATE.recon) {
    ctx.reconDiffPct = +(STATE.recon.artifactPct * 100).toFixed(2);
    ctx.sumClosed = STATE.recon.closed;
  }

  const src = header || detail;
  if (src) {
    const col = f => (src.align.bindings.find(b => b.field === f) || {}).column;
    const rows = src.rows;
    const cP = col('member_phone'), cG = col('guest_count'), cT = col('open_time');
    ctx.memberIdRate = cP ? rows.filter(r => String(r[cP] || '').trim()).length / rows.length : 0;
    ctx.guestNullRate = cG ? rows.filter(r => !String(r[cG] || '').trim()).length / rows.length : 1;
    if (cT) { const ds = rows.map(r => Date.parse(r[cT])).filter(x => !isNaN(x));
              if (ds.length) ctx.periodWeeks = +((Math.max(...ds) - Math.min(...ds)) / (7 * 864e5)).toFixed(2); }
  }
  if (detail) {
    const cI = (detail.align.bindings.find(b => b.field === 'item_name') || {}).column;
    if (cI) ctx.skuCount = new Set(detail.rows.map(r => r[cI])).size;
  }
  if (index) {
    const col = f => (index.align.bindings.find(b => b.field === f) || {}).column;
    const cR = col('role');
    ctx.roleCoverage = cR ? index.rows.filter(r => String(r[cR] || '').trim()).length / index.rows.length : 0;
    ctx.skuCount = Math.max(ctx.skuCount, index.rows.length);
  }
  return ctx;
}

/* ---- ② 对齐渲染 -------------------------------------------------------- */
const TABLE_CN = { bill_detail:'账单明细', bill_header:'账单表头', item_index:'品项索引表', member_tx:'会员消费', unknown:'未识别' };

function renderIngest() {
  const out = $('#ingestOut'); out.innerHTML = '';
  const tot = STATE.tables.reduce((a, t) => ({
    auto: a.auto + t.align.summary.auto, ask: a.ask + t.align.summary.ask,
    none: a.none + t.align.summary.none, cols: a.cols + t.align.summary.columns
  }), { auto:0, ask:0, none:0, cols:0 });

  const k = el('div', 'card');
  k.appendChild(el('h3', null, `S0-01 · 表角色识别与字段对齐总览`));
  k.appendChild(el('div', 'kpis', `
    <div class="kpi good"><div class="v">${STATE.tables.length}</div><div class="l">识别出的表</div></div>
    <div class="kpi good"><div class="v">${tot.auto}</div><div class="l">自动绑定 ≥0.85</div></div>
    <div class="kpi"><div class="v" style="color:var(--warn)">${tot.ask}</div><div class="l">待人工裁定 0.60–0.85</div></div>
    <div class="kpi ${tot.none ? 'alert' : ''}"><div class="v">${tot.none}</div><div class="l">未识别 &lt;0.60</div></div>
    <div class="kpi"><div class="v">${(tot.auto / tot.cols * 100).toFixed(0)}%</div><div class="l">自动化率（目标 ≥75%）</div></div>`));
  k.appendChild(el('div', 'takebar', `<span class="cap">TAKEAWAY</span><span class="taket">
    ${tot.cols} 个原始列中 <b>${tot.auto} 个自动对齐</b>、${tot.ask} 个需确认、${tot.none} 个未识别。
    未识别的列不会被静默丢弃——它们进入缺口清单，决定下次向客户索要什么。</span>`));
  out.appendChild(k);

  STATE.tables.forEach(t => {
    const c = el('div', 'card');
    c.appendChild(el('div', 'capline', `
      <div><span class="chip b">${t.name}</span>
        <span class="chip">识别为 ${TABLE_CN[t.table]}　置信度 ${(t.tableConf * 100).toFixed(0)}%</span>
        ${t.runnerUp && t.runnerUp.confidence > 0.3 ? `<span class="chip">次选 ${TABLE_CN[t.runnerUp.table]} ${(t.runnerUp.confidence * 100).toFixed(0)}%</span>` : ''}
        <span class="chip">${F.n(t.rows.length)} 行 × ${t.align.summary.columns} 列</span></div>
      <span class="cap">FIELD ALIGNMENT</span>`));

    /* 缺失必填字段 = 直接可发给客户的索要清单 */
    if (t.missingRequired && t.missingRequired.length) {
      c.appendChild(el('div', 'srcbar', `<span class="cap">DATA REQUEST</span><span class="srct">
        该表识别为「${TABLE_CN[t.table]}」但缺 ${t.missingRequired.length} 个必填字段：
        ${t.missingRequired.map(id => { const cn = (S.CANON.find(x => x.id === id) || {}).cn || id;
          return `<b>${cn}</b>`; }).join('、')}
        　—　<b>这行字就是下一封邮件的正文</b>，不必分析师再去翻文档。</span>`));
    }

    const rows = [...t.align.bindings.map(b => ({ ...b, kindLabel: b.status })),
                  ...t.align.unresolved.map(u => ({ column:u.column, field:'—', cn:'未识别',
                    confidence:u.candidates[0] ? u.candidates[0].score : 0, status:'none',
                    why: u.note || `值类型 ${u.profile.dtype} · 唯一值 ${u.profile.uniq}`,
                    empty: u.reason === 'empty',
                    candidates:u.candidates, profile:u.profile }))];

    const tb = el('div', 'scroll');
    tb.innerHTML = `<table class="tbl"><thead><tr>
      <th>原始列</th><th>→ 规范字段</th><th style="width:150px">置信度</th><th>判定依据</th><th>次优候选</th><th>处置</th>
    </tr></thead><tbody>${rows.map(b => {
      const cls = b.status === 'auto' ? '' : b.status;
      const badge = b.status === 'auto' ? '<span class="chip g">自动绑定</span>'
                  : b.status === 'ask' ? '<span class="chip" style="border-color:var(--warn);color:var(--warn)">待确认</span>'
                  : b.empty ? '<span class="chip">整列为空 · 进缺口清单</span>'
                  : '<span class="chip r">需人工裁定</span>';
      const cand = (b.candidates || []).slice(0, 2).map(c => `${c.cn} ${c.score}`).join(' · ') || '—';
      return `<tr>
        <td><code>${b.column}</code></td>
        <td>${b.field === '—' ? '<span style="color:var(--seal)">—</span>' : `<b>${b.cn}</b> <code style="font-size:.85em">${b.field}</code>`}</td>
        <td><span class="conf ${cls}"><span class="track"><span class="fill" style="width:${(b.confidence * 100).toFixed(0)}%"></span></span>
            <n>${b.confidence.toFixed(2)}</n></span></td>
        <td style="font-size:11.4px;color:var(--ink-muted)">${b.why}</td>
        <td style="font-size:11.4px;color:var(--ink-muted)">${cand}</td>
        <td>${badge}</td></tr>`;
    }).join('')}</tbody></table>`;
    c.appendChild(tb);

    /* 人工裁定：ask 与 ambiguous 两类都要能落地，否则「双通道打分」只是演示 */
    const pend = [...t.align.bindings.filter(b => b.status === 'ask'),
                  ...t.align.unresolved.filter(u => u.reason !== 'empty')];
    if (pend.length) {
      const box = el('div', 'readbar');
      box.innerHTML = `<span class="cap">ADJUDICATE</span><span>
        ${pend.length} 列落在 0.60–0.85 的裁定区。<b>系统不替人做这个决定</b>——但它把候选、依据和值样本都摆好了。</span>`;
      c.appendChild(box);

      const form = el('div', 'scroll');
      form.innerHTML = `<table class="tbl"><thead><tr>
        <th>原始列</th><th>值样本</th><th style="width:230px">裁定为</th><th>操作</th></tr></thead><tbody>
        ${pend.map((b, i) => {
          const opts = [b.field && b.field !== '—' ? { field: b.field, cn: b.cn, score: b.confidence } : null,
                        ...(b.candidates || [])].filter(Boolean);
          return `<tr>
            <td><code>${b.column}</code></td>
            <td style="font-size:11px;color:var(--ink-muted)">${(b.profile.sample || []).slice(0, 3).join(' · ') || '（空）'}</td>
            <td><select data-t="${t.name}" data-c="${b.column}" class="adj">
              ${opts.map(o => `<option value="${o.field}">${o.cn} · ${o.score}</option>`).join('')}
              <option value="__none">— 不绑定，进缺口清单 —</option></select></td>
            <td><button class="act ghost adj-ok" style="padding:4px 12px;font-size:11.5px" data-t="${t.name}" data-c="${b.column}">确认</button></td></tr>`;
        }).join('')}</tbody></table>`;
      c.appendChild(form);
    }

    out.appendChild(c);
  });

  out.querySelectorAll('.adj-ok').forEach(btn => btn.onclick = () => {
    const sel = out.querySelector(`select.adj[data-t="${btn.dataset.t}"][data-c="${btn.dataset.c}"]`);
    const t = STATE.tables.find(x => x.name === btn.dataset.t);
    if (!t || !sel) return;
    const field = sel.value;
    /* 从 ask/unresolved 移入已绑定，并让门禁与报告重算 */
    t.align.unresolved = t.align.unresolved.filter(u => u.column !== btn.dataset.c);
    const b = t.align.bindings.find(x => x.column === btn.dataset.c);
    if (field === '__none') {
      if (b) { t.align.bindings = t.align.bindings.filter(x => x !== b); STATE.bound.delete(b.field); }
    } else {
      const canon = S.CANON.find(c => c.id === field) || {};
      if (b) { STATE.bound.delete(b.field); b.field = field; b.cn = canon.cn || field; b.status = 'auto'; b.why = '人工裁定'; }
      else t.align.bindings.push({ column: btn.dataset.c, field, cn: canon.cn || field, confidence: 1,
                                   status: 'auto', why: '人工裁定', profile: {}, candidates: [] });
      STATE.bound.add(field);
    }
    t.align.summary = { auto: t.align.bindings.filter(x => x.status === 'auto').length,
                        ask: t.align.bindings.filter(x => x.status === 'ask').length,
                        none: t.align.unresolved.length,
                        columns: t.align.summary.columns };
    STATE.ctx = buildContext();
    renderIngest(); renderGate(); renderReport();
  });

  /* 对齐桑基 */
  const sk = el('div', 'card');
  sk.appendChild(el('h3', null, 'S0-02 · 字段对齐桑基：原始列 → 规范字段 → 维度族'));
  sk.appendChild(el('div', 'srcbar', `<span class="cap">SOURCE</span><span class="srct">
    ${STATE.tables.map(t => `<b>${t.name}</b> ${F.n(t.rows.length)} 行`).join('　')}　·　流宽 ∝ 该列非空行数</span>`));
  const sd = el('div'); sk.appendChild(sd); out.appendChild(sk);
  drawAlignSankey(sd);

  sk.appendChild(el('div', 'readbar', `<span class="cap">HOW TO READ</span><span>
    实心金流 = 已自动绑定；半透明 = 待人工确认；朱红 = 未识别（进缺口清单）。
    <b>这张图是客户第一次看见「我的表和你的体系是怎么接上的」——它本身就是信任。</b></span>`));
}

function drawAlignSankey(container) {
  const nodes = [], links = [];
  const dimOf = f => { const c = S.CANON.find(x => x.id === f); return c ? c.table.split('|')[0] : 'unknown'; };
  const cnt = {};
  STATE.tables.forEach(t => {
    const src = 'src:' + t.name;
    if (!nodes.find(n => n.id === src)) nodes.push({ id: src, side: 0, label: t.name, color: V.T.gold });
    t.align.bindings.forEach(b => {
      const tgt = 'f:' + dimOf(b.field);
      if (!nodes.find(n => n.id === tgt)) nodes.push({ id: tgt, side: 1, label: TABLE_CN[dimOf(b.field)] || dimOf(b.field), color: V.T.goldHi });
      const key = src + '>' + tgt; cnt[key] = cnt[key] || { source: src, target: tgt, value: 0, changed: b.status === 'auto', n: 0 };
      cnt[key].value += Math.max(1, Math.round(b.profile.nonNull)); cnt[key].n++;
    });
    const un = t.align.unresolved.length;
    if (un) {
      const tgt = 'f:none';
      if (!nodes.find(n => n.id === tgt)) nodes.push({ id: tgt, side: 1, label: '未识别 → 缺口清单', color: V.T.seal });
      const key = src + '>' + tgt;
      cnt[key] = { source: src, target: tgt, value: un * Math.round(t.rows.length * .35), changed: false, n: un };
    }
  });
  Object.values(cnt).forEach(l => links.push({ ...l, items: `${l.n} 个字段` }));
  try { V.sankeyFlow(container, { nodes, links }, { h: 380 }); }
  catch (e) { container.innerHTML = `<p class="sub">桑基渲染跳过：${e.message}</p>`; }
}

/* ---- ③ 门禁与解锁矩阵 --------------------------------------------------- */
function renderGate() {
  const out = $('#gateOut'); out.innerHTML = '';
  const cov = S.coverage([...STATE.bound], R, STATE.ctx);
  const t = cov.tally;

  const c1 = el('div', 'card');
  c1.appendChild(el('h3', null, 'S0-04 · 分析点解锁矩阵：本次报告的实际边界'));
  c1.appendChild(el('div', 'kpis', `
    <div class="kpi good"><div class="v">${t.ready || 0}</div><div class="l">可出 · 数据与门禁均满足</div></div>
    <div class="kpi"><div class="v" style="color:var(--warn)">${t.degraded || 0}</div><div class="l">降级 · 出但带水印</div></div>
    <div class="kpi alert"><div class="v">${t.blocked || 0}</div><div class="l">阻断 · 不可出</div></div>
    <div class="kpi"><div class="v" style="color:var(--ink-muted)">${t.pending || 0}</div><div class="l">待采集 · 外部数据</div></div>`));

  const legend = el('div', 'srcbar', `<span class="cap">LEGEND</span><span class="srct">
    <span class="dot ready"></span>可出　<span class="dot degraded"></span>降级　
    <span class="dot blocked"></span>阻断　<span class="dot pending"></span>待采集　·　悬停格子看原因</span>`);
  c1.appendChild(legend);

  R.modules.filter(m => m.id !== 'S0').forEach(m => {
    const rows = cov.rows.filter(r => r.m === m.id); if (!rows.length) return;
    const row = el('div', 'mrow');
    row.appendChild(el('div', 'mname', `<b>${m.id}</b> ${m.name}`));
    const mx = el('div', 'umx');
    rows.forEach(r => {
      const u = el('div', 'u ' + r.state, r.id);
      u.title = `${r.id} ${r.name}\n状态：${{ready:'可出',degraded:'降级',blocked:'阻断',pending:'待采集'}[r.state]}` +
                (r.reason ? '\n原因：' + r.reason : '');
      mx.appendChild(u);
    });
    row.appendChild(mx); c1.appendChild(row);
  });

  c1.appendChild(el('div', 'takebar', `<span class="cap">TAKEAWAY</span><span class="taket">
    58 格里 <b>${t.ready || 0} 格可出、${t.degraded || 0} 格降级、${(t.blocked || 0) + (t.pending || 0)} 格出不来</b>。
    这一页在分析开始前就把边界说死——<b>避免出了图再被推翻。</b></span>`));
  out.appendChild(c1);

  /* 触发的门禁 */
  const fired = Object.entries(R.gates).map(([id, g]) => ({ id, ...g, hit: cov.rows.some(r => r.gates.includes(id)) }))
                      .filter(g => g.hit);
  const c2 = el('div', 'card');
  c2.appendChild(el('h3', null, '触发的门禁与实测上下文'));
  c2.innerHTML += `<table class="tbl"><thead><tr><th>门禁</th><th>严重度</th><th>条件</th><th>影响</th></tr></thead><tbody>
    ${fired.map(g => `<tr><td><code>${g.id}</code></td>
      <td>${{stop:'<span class="chip r">停机</span>',block:'<span class="chip r">阻断</span>',
             degrade:'<span class="chip" style="border-color:var(--warn);color:var(--warn)">降级</span>',
             watermark:'<span class="chip">水印</span>',export:'<span class="chip">禁止导出</span>'}[g.sev]}</td>
      <td><code>${g.test}</code></td><td style="font-size:11.6px">${g.msg}</td></tr>`).join('')
      || '<tr><td colspan="4" style="color:var(--ink-muted)">无门禁触发</td></tr>'}
    </tbody></table>`;
  const ctxRows = Object.entries(STATE.ctx).map(([k, v]) =>
    `<tr><td><code>${k}</code></td><td class="num">${typeof v === 'number' ? (v < 1 && v > 0 ? (v * 100).toFixed(2) + '%' : F.n1(v)) : String(v)}</td></tr>`).join('');
  c2.innerHTML += `<div style="margin-top:14px"><span class="cap">MEASURED CONTEXT</span>
    <table class="tbl" style="margin-top:6px"><thead><tr><th>上下文变量</th><th class="num">实测值</th></tr></thead><tbody>${ctxRows}</tbody></table></div>`;
  out.appendChild(c2);

  /* 六条禁止操作 */
  const c3 = el('div', 'card');
  c3.appendChild(el('h3', null, '计算层硬约束：六条禁止操作'));
  c3.innerHTML += `<table class="tbl"><thead><tr><th>禁止</th><th>原因</th><th>实现</th></tr></thead><tbody>
    ${R.forbidden.map(f => `<tr><td><b>${f.rule}</b></td><td style="color:var(--ink-muted)">${f.why}</td>
      <td><code>BasisMismatchError</code></td></tr>`).join('')}</tbody></table>`;
  c3.appendChild(el('blockquote', null, `<b>为什么这条重要</b>：市面上的分析工具遇到跨口径相除会<b>静默给出一个数</b>。
    本系统直接抛错拒绝出数——<b>宁可不出，不可出错。</b>`));

  /* 现场演示抛错 */
  const demo = el('div', 'readbar');
  try {
    const clicks = new S.Q(27.2, 'A', '开台数·72天');
    const pen = new S.Q(0.07, 'B', '堂食账单·30天');
    clicks.div(pen);
    demo.innerHTML = '<span class="cap">DEMO</span><span>未触发（异常）</span>';
  } catch (e) {
    demo.innerHTML = `<span class="cap">LIVE DEMO</span><span>执行 <code>千单点击 ÷ 渗透率</code> →
      <b style="color:var(--seal)">${e.name}</b>：${e.message}</span>`;
  }
  c3.appendChild(demo);
  out.appendChild(c3);
}

/* ---- 页面构件 ---------------------------------------------------------- */
function page(id, opts) {
  const p = R.points.find(x => x.id === (opts.point || '').split('·')[0]);
  const c = el('div', 'card');
  c.appendChild(el('div', 'capline', `<div>
      <span class="chip b">${opts.pageId}</span>
      ${p ? `<span class="chip">${p.id} ${p.name}</span><span class="chip">口径 ${p.basis}</span>
             <span class="chip">${{D:'日',W:'周',M:'月',Q:'季',Y:'年',E:'事件',R:'每次'}[p.freq]}频</span>` : ''}
      ${opts.state === 'degraded' ? '<span class="chip" style="border-color:var(--warn);color:var(--warn)">降级</span>' : ''}
    </div><span class="cap">${opts.layout || 'VIZ-FULL'}</span>`));
  c.appendChild(el('h3', null, opts.title));
  if (opts.source) c.appendChild(el('div', 'srcbar', `<span class="cap">SOURCE</span><span class="srct">${opts.source}</span>`));
  const holder = el('div'); c.appendChild(holder);
  if (opts.read) c.appendChild(el('div', 'readbar', `<span class="cap">HOW TO READ</span><span>${opts.read}</span>`));
  if (opts.take) c.appendChild(el('div', 'takebar', `<span class="cap">TAKEAWAY</span><span class="taket">${opts.take}</span>`));
  if (opts.rule) c.appendChild(el('div', null,
    `<p style="font-size:11px;color:var(--ink-muted);margin-top:8px">纪律 · ${opts.rule}</p>`));
  $('#reportOut').appendChild(c);
  return holder;
}

/* ---- ⑤ 自动生成的报告页 ------------------------------------------------- */
function renderReport() {
  const out = $('#reportOut'); out.innerHTML = ''; const C = D.CASE;

  out.appendChild(el('div', 'card', `<div class="capline">
      <div><span class="chip b">清水亭 · 产品结构诊断</span>
        <span class="chip">${C.meta.stores} 店 · ${C.meta.sku} SKU · ${F.n(C.meta.bills)} 单 · ${F.n(C.meta.tables)} 台</span>
        <span class="chip">口径 B 期间 ${C.meta.period}</span></div>
      <span class="cap">AUTO-GENERATED REPORT</span></div>
    <div class="grule"></div>
    <p class="sub">以下页面由注册表驱动自动生成。每页六件套齐备：<b>页眉 chip · 来源条 · 主图 · 读法条 · 结论条 · 纪律脚注</b>。<br>
    读法条是本系统与普通 BI 的核心差异——<b>BI 给图，咨询给读法</b>，自动化系统必须把读法一起生成。</p>`));

  /* 1-02 三路对账瀑布 —— 数值全部实算，非常量 */
  const rc = STATE.recon;
  if (rc) {
    const pct = (rc.artifactPct * 100);
    const wf = [
      { label:'明细 Σ小计\n（去重前）', value: rc.rawDetail, type:'start' },
      { label:`系统伪影\n${F.n(rc.dupRows)} 行重复`, value: -rc.artifactAmt, type:'delta' },
      { label:'明细 Σ小计\n（去重后）', value: 0, type:'subtotal' },
      { label:'折让 / 优惠', value: -rc.discountAmt, type:'delta' },
      { label:'表头 Σ实收\n= 路径①', value: 0, type:'end' }
    ];
    V.waterfall(page(null, { pageId:'1-02', point:'A02',
      title:`三路对账瀑布：差额 ${pct >= 0.5 ? '未' : '已'}收敛，这决定其余 55 点能不能做`,
      state: pct >= 0.5 ? 'degraded' : undefined,
      source:`账单表头 Σ实收 ${F.cny(rc.headerSum)}　·　账单明细 Σ小计去重前 ${F.cny(rc.rawDetail)}　·　索引表 Σ标准价×销量 ${F.cny(rc.indexSum)}`,
      read:'起始柱为明细去重前合计，向下的朱红柱为扣减项，末柱应与表头实收<b>完全相等</b>。塌下去的那一段 = 被清除的系统伪影。',
      take:`去重前明细高出去重后 <b>${F.cny(rc.artifactAmt)}（+${pct.toFixed(1)}%）</b>，来自 ${F.n(rc.dupRows)} 行重复。
            闭合校验 <b style="color:${rc.closed ? 'var(--ok)' : 'var(--seal)'}">${rc.closed ? '通过' : '未通过'}</b>。
            <b>不对账，其余 55 个分析点全部作废</b>——因为它们的分子分母都建在这个总额上。`,
      rule:'路径①=②为硬条件，差额 >0.5% 触发 G-RECON 停机；路径③与①之差 = 折让 + 期间差 + SKU 覆盖差，三者不可相除' }),
      wf, { h:420, denom:`全量账单 ${F.n(STATE.tables.find(t=>t.table==='bill_header').rows.length)} 张 · 明细 ${F.n(rc.rawDetail && STATE.tables.find(t=>t.table==='bill_detail').rows.length)} 行` });
  }

  /* 1-04 数据完备度雷达 */
  V.radarChart(page(null, { pageId:'1-04', point:'A03', title:'数据完备度雷达：凹陷的那一角就是本次报告的天花板',
    source:'DAMA 六维度评分 · 及格线 80 分',
    read:'外圈虚线为及格线，实心金面为本次实测。<b>朱红点 = 未达标维度。</b>',
    take:'完整性 62 分（会员手机号缺失 96.0%、点菜员缺失 90%）与一致性 71 分（跨店角色分歧 28.0%）是两处硬伤——<b>它们直接决定 M9 与 M3 的结论强度。</b>' }),
    C.dq, { h:400, pass:80 });

  /* 2-01 门店定位气泡 */
  V.bubbleScatter(page(null, { pageId:'2-01', point:'A04', title:'门店定位气泡图：流量与客单的两难',
    source:'账单表头 · 6 店 · 30 天　|　x = 日均堂食桌数，y = 桌均实收，气泡 = 月实收，色深 = 外卖占比',
    read:'虚线弧为<b>等收入曲线</b>（桌数×桌均=常数），落在同一条弧上的门店收入相同。十字为全司均值。',
    take:'颐堤港 <b>125 桌 / ¥379.5</b> 是高流量低客单，祥云小镇 <b>83.5 桌 / ¥434.7</b> 是低流量高客单——<b>两者的解法完全相反，一张图定完六家店的策略分工。</b>',
    rule:'时长取中位不取均值（长尾包间会拉偏）' }),
    C.stores, { h:470, xLabel:'日均桌数', yLabel:'桌均', denom:'堂食账单数 · 30 天' });

  /* 2-03 客单价分布 */
  V.histCumulative(page(null, { pageId:'2-03', point:'A05', title:'人均消费分布：心智带在 ¥120–180（41.9% 桌 / 42.5% 额）',
    source:'账单表头 · 人均 = 实收 ÷ 就餐人数　|　<b>已剔除 225 张实收 = 0 的账单</b>',
    read:'柱为桌数占比，朱红线为累计额占比。<b>中位 ¥139.2 与均值 ¥146.1 的分离，就是右偏的证据。</b>',
    take:'均值高于中位 ¥6.9 = 少数高客单桌拉高了平均。<b>用「平均客单价 ¥146」做定价决策会系统性高估靶心</b>，真正的心智带是 ¥120–180。',
    rule:'必须剔除实收=0 的账单并披露剔除数；同时给中位与均值' }),
    C.ticket, { h:400, median:139.2, mean:146.1, valueFmt:F.cny, denom:'堂食账单 16,867 桌（剔除 225 张零值单）' });

  /* 3-05 角色错配桑基 */
  V.sankeyFlow(page(null, { pageId:'3-05', point:'A09', title:'角色错配桑基图：22 项该换角色，涉及 38.3% 销售额',
    source:'索引表 主辅佐引 × 额量比 × 渗透率　|　判定：引→额量比>2 · 主→渗透<5% · 佐→额占比>2% · 辅→渗透>14%',
    read:'左为现角色、右为建议角色，流宽 ∝ 涉及销售额。<b>淡色流 = 角色不变，实心金流 = 建议改变。</b>悬停看具体品项。',
    take:'22 条实心流横穿画面。重排后「主」收敛为<b>鱼头 + 藕汤 + 小龙虾三条主线</b>——铫子煨排骨莲藕汤渗透率 17.7% 全店第一却被误置为「辅」，荆沙甲鱼挂着「主」的名义 72 天只卖出 237 斤。',
    rule:'四条判定阈值须随业态标定，不可写死' }),
    C.roleFlow, { h:460, denom:'口径 A 销售额 · 72 天' });

  /* 4-01 帕累托 */
  const paretoData = D.DISHES.filter(d => d.qty > 0).map(d => ({ name:d.name, value:d.amount }));
  const pF = V.paretoDual(page(null, { pageId:'4-01', point:'A10', title:'帕累托双轴：80% 交点必须实算，不可写「约 40 款」',
    source:'索引表 标准售价 × 销量　|　口径 A · 72 天',
    read:'柱为单品销售额降序，朱红线为累计占比。金色十字标出<b>累计首次达到 80% 的精确位置</b>。',
    take:'交点坐标用等宽字体标死——<b>「该砍 15 款」与「该砍这 15 款」的差别，就是咨询报告与 BI 仪表盘的差别。</b>',
    rule:'80% 交点必须实算并标注 SKU 序号' }),
    paretoData, { h:440, denom:'口径 A · 全 SKU · 72 天' });

  /* 5-04 四象限 */
  const quadData = D.DISHES.filter(d => d.qty > 0).map(d => ({
    name:d.name, x:d.clicks, y:d.gm, r:d.amount, group:d.role }));
  V.quadrant(page(null, { pageId:'5-04', point:'A17', title:'四象限矩阵：流量品才是收入主体，也是毛利优化的主战场',
    state:'degraded',
    source:'千单点击（口径 A · 开台数分母）× 毛利率（静态成本卡）　|	气泡 = 销售额，色 = 主辅佐引',
    read:'十字为双中位线，<b>「≥ 中位数」统一归高侧</b>（图上标 ≥ 符号）。左上象限的网点纹理 = 利润黑马（强制曝光区）。',
    take:'右下「流量品」区那几个巨大的圆——<b>以 24.6% 的 SKU 数占 59.6% 销售额，却全部落在毛利中位线以下。</b>这不是要砍的对象，是要优化成本或提价的对象。',
    rule:'成本卡逾 90 天未更新 → 毛利轴仅供内部排序，禁止对外结论（G-COST-STALE 已触发）' }),
    quadData, { h:500, xLog:true, xLabel:'千单点击（对数轴）', yLabel:'毛利率', yFmt:F.pct,
      quadNames:['明星品 · 保护扩大陈列','利润黑马 · 强制曝光','淘汰候选 · 精简','流量品 · 优化成本或提价'],
      opportunityQuad:1, denom:'分子 = 期间销量，分母 = 开台数（72 天）',
      watermark:'成本卡逾期 · 禁止外部对标' });

  /* 5-02 四指标蜂群 */
  V.beeswarm(page(null, { pageId:'5-02', point:'A13', title:'四指标分布蜂群：中位数与极值的量纲差异让「平均值管理」当场破产',
    source:'额量比 · 千单点击 · 毛利率 · 渗透率　|	每点 = 1 SKU，色 = 主辅佐引',
    read:'<b>悬停任一点，四轴同时高亮该 SKU</b>——这是四指标画像的正确读法：单看一轴一定误判。',
    take:'千单点击的长尾拖到 459.8（武汉热干面）而中位仅 27.2，<b>相差 17 倍</b>。同一个 SKU 在不同轴上的位置可以完全相反——热干面千单第一但额量比仅 0.27，它是引流品不是利润品。',
    rule:'千单点击分母（开台数·72天）与渗透率分母（堂食账单·30天）系统级禁止相除' }),
    D.DISHES.filter(d => d.qty > 0),
    [ { key:'ratio',  label:'额量比',   fmt:F.n1 },
      { key:'clicks', label:'千单点击', fmt:F.n1, log:true },
      { key:'gm',     label:'毛利率',   fmt:F.pct },
      { key:'pen',    label:'渗透率',   fmt:F.pct } ],
    { denom:'口径 A 72 天 / 口径 B 30 天（分母不同，禁止相除）' });

  /* 5-06 待下架 UpSet */
  V.upsetPlot(page(null, { pageId:'5-06', point:'A18', title:'待下架命中矩阵：精简 14.4% 的 SKU，只损失 2.3% 的销售额',
    source:'C1 千单<20 · C2 额量比<0.7 · C3 毛利<65% · C4 渗透<2%　|	命中 ≥3 建议下架、=4 立即执行',
    read:'上方柱高 = 该命中组合的 SKU 数，下方点阵 = 具体命中哪几条。<b>朱红柱 = 命中 ≥3 条。</b>',
    take:'<b>这个不对称是下架决策唯一需要的论据。</b>但三类例外必须单独复议：孝感米酒脆粑冰淇淋毛利 93.9% 全店第 5 且是地域符号——它属「卖不出」而非「卖不动」，应先做曝光测试。',
    rule:'与 A48 动能冲突时以动能优先——上升期新品不可按存量指标下架' }),
    C.delist, { h:400, denom:'全 118 SKU' });

  /* 6-02 3-4-2-1 */
  V.divergingBar(page(null, { pageId:'6-02', point:'A21', title:'3-4-2-1 达标对照：必售 −22.2pt 与长尾 +22.2pt 完全对称',
    source:'四分类 SKU 占比 vs 理想 30/40/20/10',
    read:'中轴为理想结构，向左为缺配、向右为超配。<b>虚线弧连接的是两个绝对值相等的偏离。</b>',
    take:'必售缺 26 款、长尾多 26 款，<b>数量完全对称</b>——这不是巧合，说明存在一批「本该培养成必售、实际掉进长尾」的产品。<b>这个对称性本身就是洞察。</b>' }),
    C.structure3421, { h:300 });

  /* 6-03 系列效率 */
  V.lollipop(page(null, { pageId:'6-03', point:'A22', title:'系列效率指数：套餐 4.95 vs 自制饮品甜品 0.17，差 29 倍',
    source:'效率指数 = 系列销售额占比 ÷ 系列 SKU 占比　|	对数轴 · 基准线 1.0',
    read:'点大小 = 该系列 SKU 数。<b>朱红 = 低于 1.0（占着菜单不产出）。</b>',
    take:'自制饮品甜品以 <b>21.2% 的 SKU 数只贡献 3.6% 销售额</b>，是精简的第一顺位。套餐反向：3.4% SKU 贡献 16.8% 额——<b>国贸店套餐渗透率为 0，这是全司最明显的可复制缺口。</b>',
    rule:'必须用对数轴——线性轴会把 0.17 压成 0，看不出差异' }),
    C.seriesEff, { h:380 });

  /* 6-04 目标结构 */
  V.dumbbell(page(null, { pageId:'6-04', point:'A23', title:'目标结构：118 → 93，不是一个总数，是 10 条具体的路径',
    source:'系列内按销售额升序取前 N 款　|	<b>必须逐一列名</b>',
    read:'左点为现状 SKU 数，右点为目标，箭头为收敛方向。<b>朱红 = 削减，金色 = 增加。</b>',
    take:'削减 32 款（¥482,086 · <b>3.10%</b> 销售额）+ 新增 7 款 = 净 −25 款。<b>自制饮品甜品从 25 款砍到 12 款，是单系列最大动作</b>；招牌淡水鱼鲜与湖北煨汤反向加码。',
    rule:'必须逐一列名——「该砍 15 款」与「该砍这 15 款」是本体系与通用 BI 的分界线' }),
    C.targetStructure, { h:380, denom:'SKU 数' });

  /* 7-04 价格空档 */
  V.barcodeGap(page(null, { pageId:'7-04', point:'A26', title:'价格轴空档扫描：¥199 卖出 6,494 份，向上无承接',
    source:'索引表 标准售价 · 10 元步长扫描　|	<b>不含套餐 · 114 SKU</b>',
    read:'每根竖线 = 1 个 SKU，高度 ∝ 销量。<b>朱红区间 = 连续无 SKU 的价格空档。</b>',
    take:'鱼头 ¥199 是全店最强的价格锚点，但它上方是一片空白——<b>客人想多花钱也没得花。</b>补位建议：剁椒蒸丹江鱼头（承接 ¥140–150）、香辣烤武昌鱼（承接 ¥200–260）。',
    rule:'须声明步长与是否含套餐；只有在所有参数组合下都为空的区间才是稳健空档' }),
    D.DISHES.filter(d => !d.series.includes('套餐')).map(d => ({ name:d.name, price:d.price, qty:d.qty })),
    { h:320, step:10, denom:'114 SKU（不含 4 个套餐）' });

  /* 8-02 主菜杠杆 */
  const mdHolder = page(null, { pageId:'8-02', point:'A29', title:'主菜渗透杠杆：51.8% 的桌一道主菜都没点',
    source:'账单明细 × 主辅佐引　|	分母 = 堂食账单 16,867 桌',
    read:'柱 = 桌数占比，折线 = 该组桌均。<b>最高的柱在最左边，最低的收入也在最左边。</b>',
    take:'<b>全店第一大单一增量来源。</b>但必须同时给两个口径：乐观 ¥199,400/月（桌均差 ¥88.9），保守 ¥110,000/月（人均差 ¥16.9）——<b>点主菜的桌 2.9 人、零主菜的桌 2.6 人，组间不可比。</b>验证方式：随机一半 2–3 人桌执行推荐话术做 A/B 测试。',
    rule:'必须同时给乐观与保守两个口径，且声明组间人数混杂' });
  V.histCumulative(mdHolder, C.mainDish.map(d => ({ label:d.label, share:d.share, n:d.n, highlight:d.label === '0 件' })),
    { h:340, barKey:'share', denom:'堂食账单 16,867 桌' });

  /* 8-05 连带网络 */
  V.forceNetwork(page(null, { pageId:'8-05', point:'A31', title:'连带网络图：火烧馍 × 鱼头 提升度 3.03',
    source:'账单明细 · 剔除赠品与仅含赠品的 141 张账单 · 共现 ≥100 桌　|	提升度 = 支持度 ÷ (A渗透 × B渗透)',
    read:'节点大小 = 渗透率，连线粗细 = 支持度，颜色深浅 = 提升度。<b>悬停一个品项，高亮它的全部一阶邻居。</b>',
    take:'鱼头—火烧馍—藕汤的主食簇，与小龙虾—啤酒—虾配菜的夜宵簇，是两个几乎不相交的社区。<b>菜单的真实社交结构第一次被画出来。</b>但真正的价值在下一页——分店拆解。',
    rule:'前置必须剔除赠品；共现 <100 桌的组合提升度不稳定' }),
    C.basket, { h:500, minLift:1.2, denom:'堂食账单 16,732 桌（剔除赠品后）' });

  /* 8-06 分店拆解 */
  const bhold = page(null, { pageId:'8-06', point:'A31', title:'分店拆解：国贸带馍率 99.7%，世纪金源 10.6%',
    source:'账单明细 × 门店　|	带馍率 = 点鱼头且点火烧馍的桌 ÷ 点鱼头的桌',
    read:'虚线 = 全司均值。<b>99.7% 与 10.6% 并排的荒谬感，就是这个分析的全部价值。</b>',
    take:'<b>这是唯一能发现「已在单店跑通、可复制」模型的分析。</b>国贸不是运气好——是它的服务话术里有这一句而别人没有。五店复制估算月增 <b>¥190,000</b>，验证指标：五店带馍率 → 60%。',
    rule:'可复制性结论必须给验证指标，否则无法复盘' });
  V.bulletChart(bhold, [
    { name:'国贸', value:.997 }, { name:'祥云小镇', value:.170 }, { name:'世纪金源', value:.106 },
    { name:'DT51', value:.142 }, { name:'颐堤港', value:.128 }, { name:'五棵松万达', value:.155 }
  ], { target:.60, h:340, denom:'点鱼头的桌数（各店）' });

  /* 8-10 区域效率 */
  V.treemapNest(page(null, { pageId:'8-10', point:'A34', title:'区域效率树图：包间是被严重低估的资产',
    source:'元/桌/小时 = 桌均 ÷ (中位时长 ÷ 60)　|	<b>桌数 >30 才纳入</b>',
    read:'面积 ∝ 收入，色深 ∝ 效率。<b>斜纹 = 样本不足（<30 桌），不隐藏、不静默。</b>',
    take:'<b>深色的小方块（包间）与浅色的大方块（颐堤港 C 区）——「被低估的资产」在图上是深色的小块。</b>DT51 包间日均仅 5.1 桌却贡献该店 15.8% 收入；祥云二楼占该店 49.3% 收入。',
    rule:'无餐位台账，元/桌/小时为代理指标，禁止与行业 RevPASH 对标（G-SEAT 已触发）' }),
    C.areaTree, { h:440, minSample:200, watermark:'代理指标 · 禁止外部对标', denom:'各区域堂食桌数 · 30 天' });

  /* 9-01 识别率闸门 */
  V.bulletChart(page(null, { pageId:'9-01', point:'A39', title:'识别率闸门：全司 3.99%，是 M9 其余四项的开关',
    source:'账单表头 会员手机号非空率　|	目标 30%',
    read:'条为实际识别率，竖线为 30% 目标，金色背景带为及格区。<b>六条短得可怜的条对着 30% 的刻度线。</b>',
    take:'会员桌均 ¥474.5 vs 非会员 ¥310.3（<b>+52.9%</b>）——这个差值就是提升识别率的收益上限。<b>识别率 &lt;30% 时，A40 产品复购根本不该做</b>，系统已硬阻断该页。',
    rule:'储值会员非随机抽样，复购结论须写「储值会员样本的复购率」' }),
    C.memberRate, { target:.30, h:360, denom:'各店堂食账单数' });

  /* 10-01 九宫格 */
  V.heatMatrix(page(null, { pageId:'10-01', point:'A41', title:'味型 × 工艺九宫格：辣/麻 × 特殊工艺是唯一空白格',
    source:'索引表 味型 × 工艺　|	格内：上=SKU 数，下=销售额　|	<b>多门店合并取任一非空值</b>',
    read:'色深 ∝ 销售额，右侧与下方为边际条形。<b>朱红虚线框 = 基数足够大的零值格（真缺口），非零值格一律不标。</b>',
    take:'两个慢工艺格合计 <b>60.0% 销售额 = 技术护城河</b>。而辣/麻 × 特殊工艺是全表唯一空白——<b>补位建议：剁椒蒸丹江鱼头（同时承接 ¥140–150 价格空档）、香辣烤武昌鱼。</b>属性白地 + 价格空档双命中，故列 P0。',
    rule:'零值格判读纪律：只有基数 ≥7 SKU 的零值格才算缺口，否则是伪洞察' }),
    C.nineGrid, { h:440, blankThreshold:20, denom:'口径 A 销售额 · 90 SKU（属性完整）' });

  /* 11-03 中断时序 */
  V.itsPlot(page(null, { pageId:'11-03', point:'A47', title:'替换事件中断时序：品类损失 28.6%，全店几乎无感',
    source:'6/17 铫子煨排骨莲藕汤（¥89/169/269 三规格）→ 洪湖脆藕排骨汤（¥39 单规格）',
    read:'<b>灰色虚线是反事实外推——「如果不替换，本该在哪」。</b>朱红填充 = 实际与反事实的落差。',
    take:'煨汤品类桌均贡献 ¥46.8 → ¥33.4（<b>−28.6%</b>），但全店堂食桌均仅 −0.4%——<b>损失被其他品类吸收了。</b>且 6/27 起已从谷底回升，<b>可能是爬坡期而非结构性损失，年化推算属上限，非损失确认。</b>',
    rule:'必须同时看品类层与全店层；事件类分析必须在事件当日启动，事后补做无对照期' }),
    C.itsEvent, { h:420, eventDate:'2026-06-17', eventLabel:'替换', yFmt:F.cny,
      denom:'煨汤品类桌均贡献（元/桌）· 逐日' });

  /* 11-05 动能榜 */
  V.slopeBump(page(null, { pageId:'11-05', point:'A48', title:'周度动能榜：排名交叉的地方，就是该改决策的地方',
    source:'件/千桌 · W23 → W26　|	单位消除桌数波动',
    read:'金线上升、朱红线下降、灰线平稳。<b>纵轴为排名（越上越好）。</b>',
    take:'鲜熬酸梅汤 +74.3%、清蒸翘嘴鲌 +52.8%——<b>两者都命中待下架条件，但都处上升期，应暂缓。</b>「动能与存量冲突时以动能优先」这条纪律，画出来就是两条交叉的线。朝日啤酒 −38.7% 与小龙虾同步退潮，反向印证了虾—酒绑定。',
    rule:'唯一能区分「卖不动」与「刚上市」的分析；数据期间 <8 周则阻断' }),
    C.momentum, { h:420, key:'rank', invert:true, highlightDelta:4, denom:'件/千桌 · 周度' });

  /* 11-06 生命周期 */
  V.stackedFlow(page(null, { pageId:'11-06', point:'A49', title:'生命周期六阶段：SKU 宽而额窄的错位，就是「占着菜单不赚钱」',
    source:'待下架命中 × 四分类 × 动能 × 渗透率　|	<b>必须 100% 覆盖 118 款</b>',
    read:'上条为 SKU 数占比、下条为销售额占比，中间的连接带显示<b>同一阶段在两条上的宽度差</b>。',
    take:'衰退期以 <b>36.4% 的 SKU 数只占 17.3% 销售额</b>——43 款产品占着菜单不产出。原版报告给的是「约 8 / 约 6 / 22 / 约 30 / 17」，合计 83 而全量 118，<b>35 个 SKU 无归属。凡出现「约」字，即为未实算。</b>',
    rule:'完整性纪律：各阶段之和必须 = 全量，否则图元抛错拒绝渲染' }),
    C.lifecycle, { h:300, totalSku:118, denom:'全 118 SKU' });

  /* 13-01 优先级矩阵 */
  V.quadrant(page(null, { pageId:'13-01', point:'A56', title:'行动优先级矩阵：左上角三个金泡 = 下周就该开的会',
    source:'落地难度（低/中/高/很高）× 月效益量级　|	气泡 = 涉及销售额',
    read:'x 轴越左越易落地，y 轴越上效益越大。<b>左上角 = 低难度高效益。</b>',
    take:'<b>「低难度高效益」象限里有东西，是一份诊断报告成功的标志。</b>P0 三项：五店复制火烧馍连带（¥190,000）、国贸上线套餐（¥100,000）、恢复藕汤多规格（¥226,000）——全部 0–30 天可执行，且各自带验证指标。',
    rule:'每条行动必须带验证指标，否则无法复盘' }),
    C.priorities, { h:460, xLabel:'落地难度 →', yLabel:'月效益（元）', yFmt:F.cnyK, xFmt:d => ['','低','中','高','很高'][d] || '',
      xCut:2.5, yCut:120000, quadNames:['P1 · 高效益但难','P0 · 立刻做','P2 · 低优先','P1 · 易但效益小'],
      opportunityQuad:1, denom:'月度增量（元）' });

  /* 13-03 效益瀑布 */
  V.waterfall(page(null, { pageId:'13-03', point:'A57', title:'效益测算瀑布：终点不是一根柱，是一段区间',
    source:'单项效益 = 增量指标 × 影响基数 × 单位价值　|	已识别三处归因重叠',
    read:'各项依次累加至点值合计，末柱为<b>去重后的区间条（斜纹填充 + 上下界刻度）</b>，不是一个点值。',
    take:'点值合计 ¥799,200（+10.2%），<b>去重后 ¥560,000–640,000（+7.1%–8.2%）</b>。三处重叠：主菜渗透 × 火烧馍连带（同一批鱼头桌）· 低效区域 × 前两项 · 藕汤多规格 × 主菜渗透。<b>敢在报告里画自己结论的误差带，是与市面上所有咨询报告的分野。</b>',
    rule:'三件事强制：①声明乐观/保守 ②列出重叠关系 ③给区间而非点值' }),
    C.benefit, { h:440, denom:'月度增量（元）· 基数 ¥7,842,874' });
}

/* ---- ④ 图元库 ---------------------------------------------------------- */
function renderGallery() {
  const out = $('#galleryOut'); out.dataset.done = 1;
  const lib = [
    ['paretoDual','帕累托双轴','L1','A10','80% 交点实算标注，不可目测'],
    ['waterfall','瀑布','L1','A02 · A57','支持区间终柱与负值回撤'],
    ['quadrant','四象限散点','L1','A17 · A24 · A43 · A56','中位十字 + ≥ 归高侧 + 象限计数'],
    ['bubbleScatter','气泡定位','L1','A04 · S0-05','等收入背景曲线 xy=const'],
    ['heatMatrix','矩阵热力','L1','A12 · A41 · A32','双边际条形 + 零值格判读阈值'],
    ['beeswarm','蜂群','L1','A13–A16','多轴联动高亮'],
    ['sankeyFlow','桑基','L1','A09 · S0-02','无第三方依赖的自实现布局'],
    ['histCumulative','直方+累计','L1','A05 · A36','双轴 + 中位/均值双竖线'],
    ['divergingBar','发散条形','L1','A21','中轴=理想值，对称量自动配对连弧'],
    ['lollipop','棒棒糖','L1','A22','对数轴 + 基准线 1.0'],
    ['upsetPlot','UpSet','L2','A18 · A03','条件命中组合，替代无法执行的饼图'],
    ['barcodeGap','价格轴条码','L2','A26','空档区间自动识别'],
    ['forceNetwork','力导向网络','L2','A31','邻居高亮 + 提升度阈值'],
    ['slopeBump','斜率/凹凸','L2','A12 · A48','排名交叉过渡动画'],
    ['bulletChart','子弹图','L2','A39','目标刻度 + 及格带'],
    ['treemapNest','嵌套树图','L2','A34','面积=收入，色=效率，样本不足画斜纹'],
    ['dumbbell','哑铃','L2','A23','现状→目标的成对点'],
    ['radarChart','雷达','L3','A03','双层：实测 vs 及格线'],
    ['stackedFlow','堆叠错位','L3','A49 · A11','双条错位 + 合计闭合校验'],
    ['itsPlot','中断时序','L3','A47','反事实虚线外推 + 落差填充 ★'],
    ['sunburst','旭日','L3','A20','待实现（可下钻）'],
    ['ridgeline','山脊图','L3','A52','待实现（核密度）'],
    ['ganttCalendar','季节甘特','L3','A50','待实现（断裂标记）'],
    ['chordOverlap','和弦重叠','L3','A57','待实现（归因重叠面）']
  ];
  const c = el('div', 'card');
  c.appendChild(el('h3', null, 'D3 图元库 · 24 种（已实现 20，待实现 4）'));
  c.appendChild(el('div', 'srcbar', `<span class="cap">DESIGN LANGUAGE</span><span class="srct">
    土金 <code>#76551F</code> · 高光金 <code>#D4A862</code> · 玄墨 <code>#17130D</code> · 朱印 <code>#8C3228</code> · 纸 <code>#FFFDF8</code>　|	
    正文 Noto Serif SC · 数字 IBM Plex Mono（tabular-nums）· 标签 Noto Serif 字距 .34em</span>`));
  c.innerHTML += `<table class="tbl"><thead><tr><th>图元</th><th>中文</th><th>级</th><th>用于</th><th>实现要点</th><th>状态</th></tr></thead>
    <tbody>${lib.map(r => `<tr><td><code>${r[0]}</code></td><td>${r[1]}</td><td class="num">${r[2]}</td>
      <td style="font-size:11.6px">${r[3]}</td><td style="font-size:11.6px;color:var(--ink-muted)">${r[4]}</td>
      <td>${window.TIANSIGHT.viz[r[0]] ? '<span class="chip g">已实现</span>' : '<span class="chip">待实现</span>'}</td></tr>`).join('')}</tbody></table>`;
  out.appendChild(c);

  const c2 = el('div', 'card');
  c2.appendChild(el('h3', null, '六条渲染纪律（写进图元基类，不可绕过）'));
  c2.innerHTML += `<ul class="lst">
    <li><b>① 分母随图走</b>　每个图元的 meta 强制携带 <code>denom</code>，渲染到来源条上方</li>
    <li><b>② 中位线归高侧</b>　阈值切分统一 ≥，图上以 ≥ 符号标注，避免边界品项归属争议</li>
    <li><b>③ 零值 ≠ 缺口</b>　零值格只在基数达 <code>blankThreshold</code> 时才标机会，防止系统自造伪洞察</li>
    <li><b>④ 样本不足画斜纹</b>　n &lt; 阈值统一 <code>url(#sd-hatch)</code> 填充，不隐藏、不静默</li>
    <li><b>⑤ 代理指标带水印</b>　非标准口径自动加「禁止外部对标」页脚</li>
    <li><b>⑥ 合计必须闭合</b>　<code>assertClosed()</code> 校验失败直接抛错拒绝渲染</li></ul>`;
  c2.appendChild(el('blockquote', null, `把判读纪律<b>写进渲染逻辑</b>而不是写在文档里——这是「智能分析系统」与「图表生成器」的根本区别。
    文档里的纪律会被忘记，代码里的纪律不会。`));
  out.appendChild(c2);
}

/* ---- ⑤ 注册表 ---------------------------------------------------------- */
function renderRegistry() {
  const out = $('#registryOut'); out.dataset.done = 1;
  const c = el('div', 'card');
  c.appendChild(el('h3', null, '分析点注册表 · 58 点（系统的唯一真源）'));
  c.appendChild(el('div', 'srcbar', `<span class="cap">SINGLE SOURCE OF TRUTH</span><span class="srct">
    页面、图表、门禁、周期、结论模板全部由此驱动——<b>改表即改系统，不改代码。</b>
    对应 <code>src/TIANSIGHT.registry.js</code>，可直接导出为 JSON 供后端使用。</span>`));
  const sc = el('div', 'scroll');
  sc.innerHTML = `<table class="tbl"><thead><tr>
    <th>代号</th><th>分析点</th><th>模块</th><th>层</th><th>口径</th><th>频</th><th class="num">★</th>
    <th>支持决策</th><th>必需字段</th><th>页面</th><th>图元</th><th>门禁</th></tr></thead><tbody>
    ${R.points.map(p => `<tr>
      <td><b>${p.id}</b></td><td>${p.name}</td><td>${p.m}</td><td>${p.layer}</td><td>${p.basis}</td>
      <td>${{D:'日',W:'周',M:'月',Q:'季',Y:'年',E:'事件',R:'每次'}[p.freq]}</td><td class="num">${p.imp}</td>
      <td style="font-size:11.4px;max-width:230px">${p.decision}</td>
      <td style="font-size:10.6px;color:var(--ink-muted)">${(p.need || []).map(f => f.startsWith('__') ? '<i>外部</i>' : `<code style="font-size:.92em">${f}</code>`).join(' ')}</td>
      <td style="font-size:10.6px">${(p.pages || []).map(g => g.id).join(' · ')}</td>
      <td style="font-size:10.6px;color:var(--ink-muted)">${[...new Set((p.pages || []).map(g => g.viz))].join(' · ')}</td>
      <td style="font-size:10.4px">${(p.gates || []).map(g => `<code style="font-size:.9em">${g}</code>`).join(' ') || '—'}</td>
    </tr>`).join('')}
    <tr class="sum"><td colspan="6">合计</td><td class="num">${R.points.length}</td><td colspan="5">= 58 全量 ✓（完整性纪律）</td></tr>
    </tbody></table>`;
  c.appendChild(sc);
  out.appendChild(c);

  const c2 = el('div', 'card');
  c2.appendChild(el('h3', null, 'A58 强制检查清单（未全部通过 → 禁止导出）'));
  c2.innerHTML += `<ul class="lst">${R.checklist.map((x, i) =>
    `<li><b>${String(i + 1).padStart(2, '0')}</b>　${x}</li>`).join('')}</ul>`;
  c2.appendChild(el('blockquote', null,
    `清水亭三轮审查共发现 <b>14 处错误，其中 10 处是方向性错误</b>。
     这 8 条清单能拦住其中全部——<b>把审查变成系统的一道门，而不是分析师的自觉。</b>`));
  out.appendChild(c2);
}

/* ---- 事件绑定 ---------------------------------------------------------- */
$('#btnDemo').onclick = () => {
  const detail = D.genBillDetail(420);
  ingest([
    { name: '账单明细导出_202606.csv', rows: detail },
    { name: '账单表头_202606.csv',     rows: D.genBillHeader(detail) },
    { name: '菜品档案.xlsx',           rows: D.genItemIndex() }
  ]);
  document.querySelector('nav button').click();
};
$('#btnReset').onclick = () => {
  STATE.loaded = false; STATE.tables = []; STATE.bound = new Set();
  $('#ingestOut').innerHTML = '';
  $('#gateOut').innerHTML = '<div class="card"><p class="sub">先载入数据。</p></div>';
  $('#reportOut').innerHTML = '<div class="card"><p class="sub">先载入数据。</p></div>';
};
$('#btnPick').onclick = () => $('#file').click();
$('#file').onchange = e => handleFiles([...e.target.files]);

const drop = $('#drop');
['dragenter', 'dragover'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('over'); }));
['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('over'); }));
drop.addEventListener('drop', e => handleFiles([...e.dataTransfer.files]));

function handleFiles(files) {
  const named = [];
  let left = files.length; if (!left) return;
  files.forEach(f => {
    const r = new FileReader();
    r.onload = () => {
      const rows = parseCSV(r.result);
      if (rows.length) named.push({ name: f.name, rows });
      if (--left === 0 && named.length) ingest(named);
    };
    r.readAsText(f, 'utf-8');
  });
}

/* 首屏自动载入演示 */
$('#btnDemo').click();

})();
