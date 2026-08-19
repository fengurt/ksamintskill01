/* ============================================================================
 * 侍天 TIANSIGHT · 字段对齐引擎 (Field Alignment Engine)
 * ----------------------------------------------------------------------------
 * 系统的「智能」全在这一层。客户给什么列名都行，这里负责对齐到规范字段。
 *
 * 双通道打分：
 *   通道 1  列名匹配  = 别名精确 / 归一化 / 词元包含 / 编辑距离
 *   通道 2  值特征匹配 = dtype / 基数比 / 正则签名 / 数值分布 / 枚举值域
 *   总分 = 0.55 × 列名分 + 0.45 × 值特征分  （值特征权重高，因为列名可以乱起）
 *
 * 置信度处置：≥0.85 自动绑定 ｜ 0.60–0.85 人工裁定 ｜ <0.60 未识别
 * ========================================================================== */

(function (global) {
'use strict';

/* ---------------------------------------------------------------------------
 * 1. 规范字段字典
 * ------------------------------------------------------------------------ */
const CANON = [
  /* ---- T1 账单表头 ---- */
  { id:'store', cn:'门店', table:'bill_header', kind:'dim', required:true,
    alias:['门店','门店名称','店铺','店铺名称','分店','店名','机构','机构名称','组织','营业点','store','shop','branch'],
    sig:{ dtype:'string', cardMax:200, cardRatioMax:0.02 } },

  { id:'bill_no', cn:'营业流水号', table:'bill_header|bill_detail', kind:'key', required:true,
    alias:['营业流水号','流水号','账单号','订单号','单号','单据号','结账单号','消费单号','billno','order_no','orderid','ticket'],
    sig:{ dtype:'string', cardRatioMin:0.05, pattern:/^[A-Za-z0-9\-_]{6,}$/ } },

  { id:'received', cn:'实收金额', table:'bill_header', kind:'measure', required:true,
    alias:['实收金额','实收','实付金额','实付','结算金额','收款金额','净额','实收合计','paid','received'],
    sig:{ dtype:'number', min:0, decimals:2 } },

  { id:'receivable', cn:'应收金额', table:'bill_header', kind:'measure',
    alias:['应收金额','应收','原价金额','消费金额','账单金额','总金额','应付金额','amount','total'],
    sig:{ dtype:'number', min:0, decimals:2 } },

  /* 折让必须单列。缺此字段则 A02 路径③与路径①的差额无法拆解为
     「折让 + 期间差 + SKU 覆盖差」，三路对账只能给出总差额而不能归因。 */
  { id:'discount', cn:'优惠金额', table:'bill_header', kind:'measure',
    alias:['优惠金额','优惠','折扣金额','折让','减免金额','抹零','会员优惠','活动优惠','discount'],
    sig:{ dtype:'number', min:0, decimals:2, zeroHeavy:true } },

  { id:'open_time', cn:'开台时间', table:'bill_header', kind:'time', required:true,
    alias:['开台时间','开台','开单时间','下单时间','就餐时间','入座时间','开始时间','opentime','start_time'],
    sig:{ dtype:'datetime' } },

  { id:'settle_time', cn:'结算时间', table:'bill_header', kind:'time',
    alias:['结算时间','结账时间','买单时间','完成时间','离台时间','付款时间','endtime','settle_time','close_time'],
    sig:{ dtype:'datetime' } },

  { id:'guest_count', cn:'就餐人数', table:'bill_header', kind:'measure',
    alias:['就餐人数','人数','客数','用餐人数','就餐客数','顾客数','人数合计','guest','pax','headcount'],
    sig:{ dtype:'integer', min:0, max:60, cardMax:60 } },

  { id:'sale_type', cn:'销售类型', table:'bill_header', kind:'enum',
    alias:['销售类型','消费类型','订单类型','就餐方式','用餐方式','单据类型','业务类型','order_type'],
    sig:{ dtype:'string', cardMax:10, domain:['堂食','外卖','外带','自提','打包','到店','配送','团购'] } },

  { id:'area', cn:'消费区域', table:'bill_header', kind:'dim',
    alias:['消费区域','区域','餐区','就餐区域','包间','楼层','区域名称','台位区域','area','zone','section'],
    sig:{ dtype:'string', cardMax:120 } },

  { id:'seat_name', cn:'客位名称', table:'bill_header', kind:'dim',
    alias:['客位名称','台号','桌号','台位','桌台','餐台','客位','table_no','seat'],
    sig:{ dtype:'string', cardMax:800 } },

  { id:'meal_period', cn:'市别', table:'bill_header', kind:'enum',
    alias:['市别','餐段','班次','时段','餐次','营业时段','meal','period','shift'],
    sig:{ dtype:'string', cardMax:8, domain:['午市','晚市','夜市','早市','下午茶','午餐','晚餐','宵夜'] } },

  { id:'member_phone', cn:'会员手机号', table:'bill_header|member_tx', kind:'key',
    alias:['会员手机号','手机号','手机号码','会员卡号','客户电话','联系电话','会员编号','会员ID','phone','mobile','member_id'],
    sig:{ dtype:'string', pattern:/^1[3-9]\d{9}$/, cardRatioMax:0.6 } },

  /* ---- T2 账单明细 ---- */
  { id:'item_name', cn:'品项名称', table:'bill_detail|item_index', kind:'dim', required:true,
    alias:['品项名称','菜品名称','商品名称','产品名称','菜名','品名','品项','商品名','菜品','item_name','product'],
    sig:{ dtype:'string', cardMin:10, cardMax:5000, avgLenMin:2 } },

  { id:'item_code', cn:'品项代码', table:'bill_detail|item_index', kind:'key',
    alias:['品项代码','菜品编码','商品编码','商品码','菜品代码','编码','货号','SKU','sku','item_code','product_code'],
    sig:{ dtype:'string', pattern:/^[A-Za-z0-9\-]{2,}$/ } },

  { id:'spec', cn:'规格', table:'bill_detail|item_index', kind:'dim',
    alias:['规格','规格名称','单位','做法','份量','口味规格','规格属性','spec','unit','size'],
    sig:{ dtype:'string', cardMax:200 } },

  { id:'category', cn:'小类', table:'bill_detail', kind:'dim',
    alias:['小类','分类','菜类','类别','品类','子类','二级分类','category','sub_category'],
    sig:{ dtype:'string', cardMax:120 } },

  { id:'qty', cn:'数量', table:'bill_detail', kind:'measure', required:true,
    alias:['数量','份数','销量','数量合计','点单数量','销售数量','件数','qty','quantity','count'],
    sig:{ dtype:'number', min:0, max:2000 } },

  { id:'unit_price', cn:'销售单价', table:'bill_detail', kind:'measure',
    alias:['销售单价','单价','售价','价格','菜品单价','实际单价','price','unit_price'],
    sig:{ dtype:'number', min:0, decimals:2 } },

  { id:'line_amount', cn:'小计金额', table:'bill_detail', kind:'measure', required:true,
    alias:['小计金额','小计','金额','行金额','实收金额','消费金额','菜品金额','合计','subtotal','line_amount'],
    sig:{ dtype:'number', min:0, decimals:2 } },

  { id:'is_gift', cn:'赠品标记', table:'bill_detail', kind:'flag',
    alias:['赠品','是否赠品','赠送','优惠类型','赠送标记','是否赠送','gift','is_gift'],
    sig:{ dtype:'string', cardMax:6, domain:['是','否','Y','N','1','0','true','false','赠送','正常'] } },

  { id:'waiter', cn:'点菜员', table:'bill_detail', kind:'dim',
    alias:['点菜员','服务员','开单人','收银员','点单人','操作员','员工','waiter','staff','cashier'],
    sig:{ dtype:'string', cardMax:500 } },

  /* ---- T3 品项索引表 ---- */
  { id:'series', cn:'系列', table:'item_index', kind:'dim',
    alias:['系列','大类','品类','菜系','一级分类','产品线','系列名称','series','line'],
    sig:{ dtype:'string', cardMax:60 } },

  { id:'role', cn:'主辅佐引', table:'item_index', kind:'enum',
    alias:['主辅佐引','角色','菜品定位','产品角色','君臣佐使','定位','菜品角色','role'],
    sig:{ dtype:'string', cardMax:6, domain:['主','辅','佐','引'] } },

  { id:'std_price', cn:'标准售价', table:'item_index', kind:'measure',
    alias:['标准售价','售价','标价','菜单价','原价','挂牌价','标准价','list_price','std_price'],
    sig:{ dtype:'number', min:0 } },

  { id:'std_cost', cn:'实际成本', table:'item_index', kind:'measure',
    alias:['实际成本','成本','标准成本','原料成本','菜品成本','食材成本','成本价','cost','food_cost'],
    sig:{ dtype:'number', min:0 } },

  { id:'qty_period', cn:'期间销量', table:'item_index', kind:'measure',
    alias:['销量','期间销量','销售数量','销售量','累计销量','出品数','total_qty'],
    sig:{ dtype:'number', min:0 } },

  { id:'flavor', cn:'味型', table:'item_index', kind:'dim',
    alias:['味型','口味','风味','味道','口味类型','flavor','taste'],
    sig:{ dtype:'string', cardMax:40 } },

  { id:'craft', cn:'工艺', table:'item_index', kind:'dim',
    alias:['工艺','烹饪方式','做法','工序','烹调方法','制作工艺','craft','cooking'],
    sig:{ dtype:'string', cardMax:40 } },

  { id:'ingredient', cn:'食材', table:'item_index', kind:'dim',
    alias:['食材','主料','原料','食材大类','主要食材','材料','ingredient','material'],
    sig:{ dtype:'string', cardMax:60 } },

  { id:'station', cn:'档口', table:'item_index', kind:'dim',
    alias:['档口','出品部门','厨房','工位','出品档口','制作部门','station','kitchen'],
    sig:{ dtype:'string', cardMax:40 } },

  /* ---- T4 会员消费 ---- */
  { id:'tx_time', cn:'操作时间', table:'member_tx', kind:'time',
    alias:['操作时间','消费时间','交易时间','发生时间','时间','tx_time','trade_time'],
    sig:{ dtype:'datetime' } },

  { id:'tx_amount', cn:'交易金额', table:'member_tx', kind:'measure',
    alias:['账单金额','消费金额','交易金额','实付','支付金额','tx_amount'],
    sig:{ dtype:'number', min:0 } }
];

/* ---------------------------------------------------------------------------
 * 2. 字符串归一化与相似度
 * ------------------------------------------------------------------------ */
const FULL2HALF = s => s.replace(/[\uFF01-\uFF5E]/g, c => String.fromCharCode(c.charCodeAt(0) - 0xFEE0))
                        .replace(/\u3000/g, ' ');

function norm(s) {
  return FULL2HALF(String(s == null ? '' : s))
    .toLowerCase()
    .replace(/[\s_\-/\\()（）\[\]{}·.、,，:：;；'"]/g, '')
    .replace(/名称$|字段$|信息$/g, '');
}

function levenshtein(a, b) {
  if (a === b) return 0;
  const m = a.length, n = b.length;
  if (!m) return n; if (!n) return m;
  let prev = Array.from({ length: n + 1 }, (_, i) => i), cur = new Array(n + 1);
  for (let i = 1; i <= m; i++) {
    cur[0] = i;
    for (let j = 1; j <= n; j++) {
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    }
    [prev, cur] = [cur, prev];
  }
  return prev[n];
}

const simRatio = (a, b) => !a.length && !b.length ? 1 : 1 - levenshtein(a, b) / Math.max(a.length, b.length);

/* bigram Dice 系数 —— 中文短词比编辑距离更稳 */
function dice(a, b) {
  if (a.length < 2 || b.length < 2) return a === b ? 1 : 0;
  const grams = s => { const g = new Map(); for (let i = 0; i < s.length - 1; i++) { const k = s.slice(i, i + 2); g.set(k, (g.get(k) || 0) + 1); } return g; };
  const ga = grams(a), gb = grams(b);
  let hit = 0, total = 0;
  ga.forEach((v, k) => { total += v; hit += Math.min(v, gb.get(k) || 0); });
  gb.forEach(v => total += v);
  return total ? 2 * hit / total : 0;
}

/* ---------------------------------------------------------------------------
 * 3. 值特征剖析 (Profiling)
 * ------------------------------------------------------------------------ */
const DATE_RE = /^\d{4}[-/年]\d{1,2}[-/月]\d{1,2}/;

function profile(values) {
  const raw = values.filter(v => v !== null && v !== undefined && String(v).trim() !== '');
  const n = values.length || 1;
  const p = {
    n, nonNull: raw.length, nullRate: 1 - raw.length / n,
    uniq: new Set(raw.map(String)).size,
    cardRatio: raw.length ? new Set(raw.map(String)).size / raw.length : 0,
    sample: raw.slice(0, 12).map(String)
  };
  if (!raw.length) { p.dtype = 'empty'; return p; }

  const nums = raw.filter(v => v !== '' && !isNaN(Number(v))).map(Number);
  const dates = raw.filter(v => DATE_RE.test(String(v)) || (String(v).length > 7 && !isNaN(Date.parse(v))));

  if (dates.length / raw.length > 0.8) p.dtype = 'datetime';
  else if (nums.length / raw.length > 0.9) {
    p.dtype = nums.every(x => Number.isInteger(x)) ? 'integer' : 'number';
    p.min = Math.min(...nums); p.max = Math.max(...nums);
    p.mean = nums.reduce((a, b) => a + b, 0) / nums.length;
    p.decimals = nums.some(x => Math.round(x * 100) !== Math.round(x * 1000) / 10) ? 2 : 0;
    p.hasDecimal = nums.some(x => !Number.isInteger(x));
    p.zeroRate = nums.filter(x => x === 0).length / (nums.length || 1);
  } else {
    p.dtype = 'string';
    p.avgLen = raw.reduce((a, v) => a + String(v).length, 0) / raw.length;
    p.domain = p.uniq <= 20 ? [...new Set(raw.map(String))] : null;
  }
  return p;
}

/* ---------------------------------------------------------------------------
 * 4. 双通道打分
 * ------------------------------------------------------------------------ */
function scoreName(colName, canon) {
  const c = norm(colName);
  if (!c) return 0;
  let best = 0;
  for (const a of canon.alias) {
    const na = norm(a);
    if (c === na) return 1.0;                              // 精确别名
    if (c.includes(na) || na.includes(c)) best = Math.max(best, 0.88); // 包含
    best = Math.max(best, dice(c, na) * 0.92, simRatio(c, na) * 0.85);
  }
  return Math.min(best, 0.98);
}

function scoreSignature(prof, canon) {
  const s = canon.sig || {};
  if (prof.dtype === 'empty') return 0.15;
  let score = 0.5, checks = 0, pass = 0;

  /* 形态优先：手机号、流水号等「全数字字符串」会被值剖析判成 integer，
     若规范字段带 pattern 且样本高度命中，则形态证据压过 dtype 否决。 */
  const patHit = s.pattern
    ? prof.sample.filter(v => s.pattern.test(String(v).trim())).length / (prof.sample.length || 1)
    : 0;
  const patternRules = s.pattern && patHit >= 0.8;

  const want = s.dtype;
  if (want && !patternRules) {
    checks++;
    const numeric = prof.dtype === 'number' || prof.dtype === 'integer';
    if (want === prof.dtype) pass++;
    else if (want === 'number' && numeric) pass += 0.9;
    else if (want === 'integer' && prof.dtype === 'number') pass += 0.5;
    else if ((want === 'string' || want === 'enum') && prof.dtype === 'string') pass += 0.9;
    else return 0.05;                                      // dtype 冲突直接否决
  }
  if (s.pattern) { checks++; pass += patHit; }
  if (s.domain)  { checks++; const dom = new Set(s.domain.map(norm));
                   const hit = prof.sample.filter(v => dom.has(norm(v))).length / (prof.sample.length || 1); pass += hit; }
  if (s.cardMax != null) { checks++; pass += prof.uniq <= s.cardMax ? 1 : Math.max(0, 1 - (prof.uniq - s.cardMax) / (s.cardMax * 4)); }
  if (s.cardMin != null) { checks++; pass += prof.uniq >= s.cardMin ? 1 : prof.uniq / s.cardMin; }
  if (s.cardRatioMin != null) { checks++; pass += prof.cardRatio >= s.cardRatioMin ? 1 : prof.cardRatio / s.cardRatioMin; }
  if (s.cardRatioMax != null) { checks++; pass += prof.cardRatio <= s.cardRatioMax ? 1 : Math.max(0, 1 - (prof.cardRatio - s.cardRatioMax)); }
  if (s.min != null && prof.min != null) { checks++; pass += prof.min >= s.min ? 1 : 0.2; }
  if (s.max != null && prof.max != null) { checks++; pass += prof.max <= s.max ? 1 : 0.2; }
  if (s.zeroHeavy && prof.zeroRate != null) { checks++; pass += prof.zeroRate >= 0.4 ? 1 : prof.zeroRate / 0.4; }
  if (s.avgLenMin != null && prof.avgLen != null) { checks++; pass += prof.avgLen >= s.avgLenMin ? 1 : 0.3; }

  score = checks ? pass / checks : 0.5;
  return Math.max(0, Math.min(1, score));
}

/* ---------------------------------------------------------------------------
 * 5. 对齐主函数
 * ------------------------------------------------------------------------ */
const W_NAME = 0.55, W_SIG = 0.45;
const AUTO = 0.85, ASK = 0.60;

/**
 * @param {Array<Object>} rows  已解析的数据行
 * @param {string} tableHint    表角色提示（可选）
 * @returns {{bindings:Array, unresolved:Array, summary:Object}}
 */
function align(rows, tableHint) {
  if (!rows || !rows.length) return { bindings: [], unresolved: [], summary: { auto: 0, ask: 0, none: 0 } };
  const cols = Object.keys(rows[0]);
  const profiles = {};
  cols.forEach(c => profiles[c] = profile(rows.map(r => r[c])));

  /* 逐列 × 逐规范字段打分 */
  const grid = [];
  cols.forEach(col => {
    CANON.forEach(canon => {
      const sn = scoreName(col, canon);
      const ss = scoreSignature(profiles[col], canon);
      let total = W_NAME * sn + W_SIG * ss;
      /* 表角色先验：表提示匹配则小幅加权 */
      if (tableHint && canon.table.includes(tableHint)) total *= 1.06;
      /* 列名毫无线索时，纯靠值特征不足以自动绑定 */
      if (sn < 0.35) total *= 0.72;
      grid.push({ col, canon, score: Math.min(total, 1), sn, ss });
    });
  });

  /* 贪心一对一分配（分数降序，列与规范字段各用一次） */
  grid.sort((a, b) => b.score - a.score);
  const usedCol = new Set(), usedCanon = new Set(), bindings = [];
  for (const g of grid) {
    if (g.score < ASK) break;
    if (usedCol.has(g.col) || usedCanon.has(g.canon.id)) continue;
    usedCol.add(g.col); usedCanon.add(g.canon.id);
    bindings.push({
      column: g.col, field: g.canon.id, cn: g.canon.cn, kind: g.canon.kind,
      confidence: +g.score.toFixed(3),
      status: g.score >= AUTO ? 'auto' : 'ask',
      nameScore: +g.sn.toFixed(2), sigScore: +g.ss.toFixed(2),
      profile: profiles[g.col],
      why: explain(g, profiles[g.col]),
      candidates: topCandidates(grid, g.col, g.canon.id)
    });
  }

  /* 未识别列分两类：整列为空（客户导出了但没填）与真歧义（需人工裁定）。
     二者的处置完全不同——前者进「向客户索要」清单，后者进「人工裁定」队列。 */
  const unresolved = cols.filter(c => !usedCol.has(c)).map(c => {
    const empty = profiles[c].dtype === 'empty' || profiles[c].nullRate >= 0.995;
    return {
      column: c, profile: profiles[c], status: 'none',
      reason: empty ? 'empty' : 'ambiguous',
      note: empty ? '整列为空 → 进入数据缺口清单，不做候选推断'
                  : '值特征与列名均不足以判定 → 需人工裁定',
      candidates: empty ? [] : topCandidates(grid, c, null)
    };
  });

  return {
    bindings: bindings.sort((a, b) => b.confidence - a.confidence),
    unresolved,
    summary: {
      auto: bindings.filter(b => b.status === 'auto').length,
      ask: bindings.filter(b => b.status === 'ask').length,
      none: unresolved.length,
      columns: cols.length
    }
  };
}

function topCandidates(grid, col, exclude) {
  return grid.filter(g => g.col === col && g.canon.id !== exclude)
             .slice(0, 3)
             .map(g => ({ field: g.canon.id, cn: g.canon.cn, score: +g.score.toFixed(2) }));
}

function explain(g, prof) {
  const bits = [];
  if (g.sn >= 0.99) bits.push('列名精确命中别名');
  else if (g.sn >= 0.85) bits.push('列名高度相近');
  else if (g.sn >= 0.5) bits.push('列名部分相似');
  else bits.push('列名无线索');
  bits.push(`值类型 ${prof.dtype}`);
  if (prof.uniq != null) bits.push(`唯一值 ${prof.uniq}`);
  if (prof.nullRate > 0.05) bits.push(`缺失 ${(prof.nullRate * 100).toFixed(1)}%`);
  if (g.ss >= 0.8) bits.push('值特征吻合');
  else if (g.ss < 0.5) bits.push('值特征偏离');
  return bits.join(' · ');
}

/* ---------------------------------------------------------------------------
 * 6. 表角色识别 —— 你给了几张表、各是什么表
 * ------------------------------------------------------------------------ */
function detectTable(rows) {
  const res = align(rows);
  const has = id => res.bindings.some(b => b.field === id && b.confidence >= ASK);

  /* 强证据（结构性特征）与弱证据（辅助字段）分开计分。
     客户导出的表经常缺一两个必填列——这时应判为「是这张表但不完整」，
     而不是判为 unknown。unknown 会让缺口清单失去指向性。 */
  const evidence = {
    bill_detail: { strong: [has('bill_no') && has('item_name'), has('qty') && has('line_amount')],
                   weak: [has('unit_price'), has('spec'), has('category')] },
    bill_header: { strong: [has('bill_no') && !has('item_name'), has('received') || has('receivable')],
                   weak: [has('guest_count'), has('discount'), has('settle_time'), has('seat_name')] },
    item_index:  { strong: [has('item_name') && has('std_price'), has('qty_period') || has('role')],
                   weak: [has('std_cost'), has('flavor'), has('craft'), has('series')] },
    member_tx:   { strong: [has('member_phone'), has('tx_time')],
                   weak: [has('tx_amount')] }
  };

  const score = {};
  Object.entries(evidence).forEach(([k, e]) => {
    const s = e.strong.filter(Boolean).length / e.strong.length;
    const w = e.weak.filter(Boolean).length / (e.weak.length || 1);
    score[k] = s * 0.8 + w * 0.2;                    // 强证据主导，弱证据只做区分
  });

  const ranked = Object.entries(score).sort((a, b) => b[1] - a[1]);
  const [table, conf] = ranked[0];

  /* 该表角色的必填字段中，哪些没到位——这直接就是向客户索要的清单 */
  const required = CANON.filter(c => c.required && c.table.includes(table)).map(c => c.id);
  const missingRequired = required.filter(id => !has(id));

  return {
    table: conf >= 0.4 ? table : 'unknown',
    confidence: +conf.toFixed(2),
    runnerUp: ranked[1] ? { table: ranked[1][0], confidence: +ranked[1][1].toFixed(2) } : null,
    missingRequired,
    alignment: res
  };
}

/* ---------------------------------------------------------------------------
 * 7. 覆盖度 → 分析点解锁判定
 * ------------------------------------------------------------------------ */
function coverage(boundFields, registry, ctx) {
  ctx = ctx || {};
  const have = new Set(boundFields);
  const rows = registry.points.map(p => {
    const missing = (p.need || []).filter(f => !f.startsWith('__') && !have.has(f));
    const missOpt = (p.opt  || []).filter(f => !f.startsWith('__') && !have.has(f));
    const external = (p.need || []).some(f => f.startsWith('__external'));

    /* 门禁判定 */
    const fired = (p.gates || []).filter(gid => {
      const g = registry.gates[gid]; if (!g) return false;
      try { return !!evalGate(g.test, ctx); } catch (e) { return false; }
    });
    const blocking = fired.filter(gid => ['stop','block'].includes(registry.gates[gid].sev));

    let state = 'ready', reason = '';
    if (external)            { state = 'pending'; reason = '外部数据待采集'; }
    else if (missing.length) { state = 'blocked'; reason = '缺字段：' + missing.join('、'); }
    else if (blocking.length){ state = 'blocked'; reason = blocking.map(g => registry.gates[g].msg).join('；'); }
    else if (fired.length || missOpt.length) {
      state = 'degraded';
      reason = [...fired.map(g => registry.gates[g].msg),
                missOpt.length ? '缺可选字段：' + missOpt.join('、') : ''].filter(Boolean).join('；');
    }
    return { id: p.id, m: p.m, name: p.name, imp: p.imp, freq: p.freq, state, reason, missing, gates: fired };
  });

  const tally = rows.reduce((a, r) => (a[r.state] = (a[r.state] || 0) + 1, a), {});
  return { rows, tally };
}

/* 极简安全求值：只支持 `ident op number` 与 `!ident` / `ident` */
function evalGate(expr, ctx) {
  expr = expr.trim();
  if (expr.startsWith('!')) return !ctx[expr.slice(1).trim()];
  const m = expr.match(/^([A-Za-z_]\w*)\s*(>=|<=|>|<|==|!=)\s*(-?[\d.]+)$/);
  if (!m) return !!ctx[expr];
  const [, k, op, num] = m, v = ctx[k], x = parseFloat(num);
  if (v == null) return false;
  switch (op) {
    case '>':  return v >  x; case '<':  return v <  x;
    case '>=': return v >= x; case '<=': return v <= x;
    case '==': return v == x; case '!=': return v != x;
  }
  return false;
}

/* ---------------------------------------------------------------------------
 * 8. 口径守卫 —— 六条禁止操作的计算层实现
 * ------------------------------------------------------------------------ */
class BasisMismatchError extends Error {
  constructor(a, b) { super(`跨口径运算被拒绝：${a} ÷ ${b} —— 期间或分母不同`); this.name = 'BasisMismatchError'; }
}

/** 带口径标签的量。相除前强制校验分母一致性。 */
class Q {
  constructor(value, basis, denom) { this.value = value; this.basis = basis; this.denom = denom || null; }
  div(other) {
    if (other instanceof Q) {
      if (other.denom && this.denom && other.denom !== this.denom) throw new BasisMismatchError(this.denom, other.denom);
      if (this.basis && other.basis && this.basis !== other.basis && this.basis !== 'A+B' && other.basis !== 'A+B')
        throw new BasisMismatchError(this.basis, other.basis);
      return new Q(this.value / other.value, this.basis, null);
    }
    return new Q(this.value / other, this.basis, this.denom);
  }
  valueOf() { return this.value; }
}

global.TIANSIGHTSchema = {
  CANON, align, profile, detectTable, coverage, norm, dice, simRatio,
  Q, BasisMismatchError, THRESHOLD: { AUTO, ASK }
};

})(typeof window !== 'undefined' ? window : globalThis);
