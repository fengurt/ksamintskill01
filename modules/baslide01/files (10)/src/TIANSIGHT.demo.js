/* ============================================================================
 * 侍天 TIANSIGHT · 演示数据
 * ----------------------------------------------------------------------------
 * 两部分：
 *  A. 合成 POS 导出（列名故意起得「不规范」，用于演示字段对齐引擎的真实能力）
 *  B. 清水亭案例聚合值（用于驱动图元库；来源：分析体系 Part 1 v2.0 样例数据）
 * ========================================================================== */
(function (global) {
'use strict';

/* ---- 品项主数据（取自清水亭案例，节选并补齐至可演示规模） -------------- */
const DISHES = [
  // name, role, series, price, cost, flavor, craft, ingredient, qty72d, penetration, clicks1k
  ['【鱼头+藕汤】招牌双人餐','引','套餐',316,142,'咸鲜','煨','淡水鱼',4374,.079,107.1],
  ['山茶油丹江大鱼头','主','招牌淡水鱼鲜',199,82.6,'咸鲜','烧','淡水鱼',5231,.159,128.1],
  ['【鱼头+藕汤】经典四人餐','引','套餐',549,247,'咸鲜','煨','淡水鱼',1203,.031,29.5],
  ['铫子煨排骨莲藕汤·迷你份','辅','湖北煨汤',89,17.5,'咸鲜','煨','猪',6338,.177,155.2],
  ['金奖麻辣油焖小龙虾·招牌99/斤','辅','小龙虾',99,38.6,'辣麻','焖','海鲜',4517,.132,110.6],
  ['武汉热干面','佐','小吃点心主食',16,2.8,'咸鲜','煮','面食点心',18770,.333,459.8],
  ['铫子煨排骨莲藕汤·大份','辅','湖北煨汤',269,52.5,'咸鲜','煨','猪',604,.177,14.8],
  ['铫子煨手打鱼丸汤·小份','辅','湖北煨汤',99,14.4,'咸鲜','煨','淡水鱼',882,.102,21.6],
  ['武汉街头绿豆沙·扎','引','自制饮品甜品',59,1.2,'甜酸','熬','甜品',568,.097,13.9],
  ['沔阳珍珠丸子·大份','佐','湖北烟火热菜',69,6.6,'咸鲜','蒸','猪',600,.131,14.7],
  ['鲜榨西瓜汁·扎','引','自制饮品甜品',79,6.6,'甜酸','榨','水果',666,.028,16.3],
  ['黄金蒜蓉小龙虾','辅','小龙虾',109,44.7,'咸鲜','蒸','海鲜',3820,.118,93.5],
  ['老家火烧馍','佐','小吃点心主食',22,3.5,'咸鲜','炕',  '面食点心',10770,.158,263.7],
  ['洪湖脆藕排骨汤','辅','湖北煨汤',39,7.8,'咸鲜','煨','猪',5038,.142,123.4],
  ['清蒸鲜活丹江口翘嘴鲌','主','招牌淡水鱼鲜',238,105,'咸鲜','蒸','淡水鱼',388,.015,9.5],
  ['荆沙甲鱼','主','招牌淡水鱼鲜',299,148,'咸鲜','烧','淡水鱼',237,.002,5.8],
  ['蟹肉蒸茼蒿','佐','湖北烟火热菜',69,31.1,'咸鲜','蒸','素绿叶',312,.021,7.6],
  ['孝感米酒脆粑冰淇淋','佐','自制饮品甜品',39,2.4,'甜酸','炸','甜品',420,.032,10.3],
  ['【工作日超值】双人餐','引','套餐',239,116,'咸鲜','煨','淡水鱼',356,.018,8.7],
  ['鲜熬酸梅汤·扎','引','自制饮品甜品',49,2.1,'甜酸','熬','水果',1104,.088,27.0],
  ['武当山笋炒腊肉','佐','湖北烟火热菜',78,21.8,'咸鲜','炒','猪',1420,.086,34.8],
  ['鲜藕带尖','佐','湖北烟火热菜',58,17.4,'咸鲜','炒','素绿叶',1680,.101,41.1],
  ['朝日啤酒','引','酒水',28,14.0,'其他','—','饮品',1120,.062,27.4],
  ['洪湖藕夹','佐','湖北烟火热菜',48,11.5,'咸鲜','炸','素绿叶',2240,.112,54.9],
  ['干煸鳝丝','佐','湖北烟火热菜',88,32.6,'辣麻','炒','淡水鱼',960,.058,23.5],
  ['桂花醪糟汤圆','佐','自制饮品甜品',29,2.6,'甜酸','煮','甜品',1360,.077,33.3],
  ['剁椒鱼头·小份','辅','招牌淡水鱼鲜',128,52.5,'辣麻','蒸','淡水鱼',740,.044,18.1],
  ['虾配菜·藕带','佐','小龙虾配菜',13,3.9,'咸鲜','拌','素绿叶',3200,.096,78.4],
  ['虾配菜·毛豆','佐','小龙虾配菜',13,3.4,'咸鲜','煮','素绿叶',2880,.088,70.5],
  ['粉蒸肉','佐','湖北烟火热菜',56,18.5,'咸鲜','蒸','猪',1540,.092,37.7],
  ['三鲜豆皮','佐','小吃点心主食',26,5.2,'咸鲜','煎','面食点心',4200,.148,102.8],
  ['糯米包油条','佐','小吃点心主食',18,3.1,'咸鲜','煎','面食点心',3600,.126,88.1],
  ['清水粽·蜜枣','佐','小吃点心主食',18,4.0,'甜酸','煮','面食点心',729,.028,17.8],
  ['蒜蓉粉丝蒸扇贝','佐','湖北烟火热菜',68,29.9,'咸鲜','蒸','海鲜',680,.041,16.6],
  ['泡椒牛蛙','辅','湖北烟火热菜',98,39.2,'辣麻','焖','其他',1280,.075,31.3],
  ['农家小炒肉','佐','湖北烟火热菜',52,17.7,'辣麻','炒','猪',1980,.108,48.5],
  ['时蔬（季节）','佐','湖北烟火热菜',32,9.6,'咸鲜','炒','素绿叶',2560,.132,62.7],
  ['冰镇糖水梨','佐','自制饮品甜品',26,1.8,'甜酸','煮','水果',890,.049,21.8],
  ['蒸三样','佐','湖北烟火热菜',62,21.7,'咸鲜','蒸','猪',1120,.068,27.4],
  ['香辣烤武昌鱼','主','招牌淡水鱼鲜',158,71.1,'辣麻','烤','淡水鱼',0,0,0]  // 空白格补漏建议品，尚未上架
].map(a => ({
  name:a[0], role:a[1], series:a[2], price:a[3], cost:a[4],
  flavor:a[5], craft:a[6], ingredient:a[7], qty:a[8], pen:a[9], clicks:a[10],
  amount:a[3]*a[8], gm:(a[3]-a[4])/a[3], ratio:a[3]/59.55
}));

const STORES = ['国贸','颐堤港','祥云小镇','DT51','世纪金源','五棵松万达'];
const AREAS  = { '国贸':['大厅A','大厅B','卡座'], '颐堤港':['C区','大厅','窗边'],
                 '祥云小镇':['一楼','二楼'], 'DT51':['大厅','包间'],
                 '世纪金源':['大厅','包间'], '五棵松万达':['大厅','卡座'] };

/* ---- A. 合成 POS 导出（列名故意不规范） -------------------------------- */
function randn(mu, sd){ let u=0,v=0; while(!u)u=Math.random(); while(!v)v=Math.random();
  return mu + sd*Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v); }
const pick = a => a[Math.floor(Math.random()*a.length)];
const pad  = n => String(n).padStart(2,'0');

function genBillDetail(nBills, artifact){
  if (artifact === undefined) artifact = true;
  const rows=[];
  for(let b=0;b<nBills;b++){
    const store = pick(STORES);
    const day   = 1+Math.floor(Math.random()*30);
    const hour  = Math.random()<.42 ? 11+Math.floor(Math.random()*3) : 17+Math.floor(Math.random()*4);
    const min   = Math.floor(Math.random()*60);
    const open  = `2026-06-${pad(day)} ${pad(hour)}:${pad(min)}:00`;
    const dur   = Math.max(22, Math.round(randn(58,18)));
    const end   = new Date(new Date(open).getTime()+dur*6e4);
    const settle= `${end.getFullYear()}-${pad(end.getMonth()+1)}-${pad(end.getDate())} ${pad(end.getHours())}:${pad(end.getMinutes())}:00`;
    const guests= Math.max(1, Math.round(randn(2.9,1.4)));
    const bill  = `${store.slice(0,2)}${day}${pad(hour)}${String(b).padStart(5,'0')}`;
    const nItem = Math.max(2, Math.round(randn(6.5+guests*0.7, 2.2)));
    const type  = Math.random()<.885 ? '堂食' : (Math.random()<.8 ? '外卖' : (Math.random()<.9?'外带':'自提'));
    const phone = Math.random()<.04 ? '1'+pick(['3','5','7','8','9'])+String(Math.floor(Math.random()*1e9)).padStart(9,'0') : '';
    const used  = new Set();
    for(let i=0;i<nItem;i++){
      const d = DISHES[Math.floor(Math.pow(Math.random(),1.7)*DISHES.length)];
      if(!d || d.qty===0) continue;
      const key=d.name; if(used.has(key)&&Math.random()<.7) continue; used.add(key);
      const q = Math.random()<.86?1:2;
      rows.push({
        '店铺名称': store,                    // → store
        '结账单号': bill,                     // → bill_no
        '菜品名称': d.name,                   // → item_name
        '规格属性': d.name.includes('·')?d.name.split('·')[1]:'—',  // → spec
        '菜类':     d.series,                 // → category
        '份数':     q,                        // → qty
        '菜品单价': d.price,                  // → unit_price
        '小计':     d.price*q,                // → line_amount
        '开单时间': open,                     // → open_time
        '结账时间': settle,                   // → settle_time
        '用餐客数': guests,                   // → guest_count
        '餐区':     pick(AREAS[store]),       // → area
        '消费类型': type,                     // → sale_type
        '手机号码': phone,                    // → member_phone
        '开单人':   Math.random()<.1?'员工'+Math.floor(Math.random()*40):'',  // → waiter（90% 空）
        '是否赠送': Math.random()<.02?'是':'否',  // → is_gift
        '备注':     ''                        // → 未识别列（演示 unresolved）
      });
    }
  }
  /* 系统伪影注入：POS 导出常见的行级重复（清水亭为 5,597 行 / +10.6%）。
     账单表头按去重后计算，明细去重前偏高——三路对账的差额由此真实产生，
     而不是写死一个数字。关掉 artifact 即可看到差额归零。 */
  if (artifact) {
    const n = Math.round(rows.length * 0.106);
    for (let i = 0; i < n; i++) rows.push({ ...rows[Math.floor(Math.random() * rows.length)] });
  }
  return rows;
}

/* 账单表头：由明细「去重后」聚合而成 —— 这是路径① */
function genBillHeader(detail){
  const seen = new Set(), byBill = new Map();
  detail.forEach(r => {
    const line = [r['结账单号'], r['菜品名称'], r['规格属性'], r['份数'], r['菜品单价']].join('|');
    if (seen.has(line)) return;                    // 去重：伪影行不计入表头
    seen.add(line);
    const b = r['结账单号'];
    if (!byBill.has(b)) byBill.set(b, {
      '门店名称': r['店铺名称'], '营业流水号': b, '开台时间': r['开单时间'],
      '结账时间': r['结账时间'], '就餐人数': r['用餐客数'], '台号': r['餐区'],
      '订单类型': r['消费类型'], '会员手机': r['手机号码'], '应收金额': 0, '实收金额': 0, '优惠金额': 0
    });
    byBill.get(b)['应收金额'] += Number(r['小计']) || 0;
  });
  const out = [...byBill.values()];
  out.forEach(h => {
    const disc = Math.random() < .18 ? Math.round(h['应收金额'] * (0.05 + Math.random() * 0.15)) : 0;
    h['优惠金额'] = disc;
    h['实收金额'] = Math.max(0, h['应收金额'] - disc);
    if (Math.random() < .013) h['实收金额'] = 0;   // 零值单：A05 必须剔除并披露
    h['应收金额'] = +h['应收金额'].toFixed(2);
    h['实收金额'] = +h['实收金额'].toFixed(2);
  });
  return out;
}

/* 路径①②③ 实算 —— 计算层的第一个算子 */
function reconcile(header, detail, index){
  const seen = new Set();
  let rawDetail = 0, dedupDetail = 0;
  detail.forEach(r => {
    const v = Number(r['小计']) || 0; rawDetail += v;
    const line = [r['结账单号'], r['菜品名称'], r['规格属性'], r['份数'], r['菜品单价']].join('|');
    if (seen.has(line)) return; seen.add(line); dedupDetail += v;
  });
  const headerSum = header.reduce((a, h) => a + (Number(h['实收金额']) || 0), 0);
  const headerDue = header.reduce((a, h) => a + (Number(h['应收金额']) || 0), 0);
  const indexSum  = (index || []).reduce((a, r) => a + (Number(r['挂牌价']) || 0) * (Number(r['销售量']) || 0), 0);
  const dupRows   = detail.length - seen.size;
  return {
    headerSum, headerDue, rawDetail, dedupDetail, indexSum, dupRows,
    artifactAmt: rawDetail - dedupDetail,
    artifactPct: dedupDetail ? (rawDetail - dedupDetail) / dedupDetail : 0,
    discountAmt: headerDue - headerSum,
    closed: Math.abs(dedupDetail - headerDue) < Math.max(1, headerDue * 0.0001)
  };
}

function genItemIndex(){
  return DISHES.map(d=>({
    '产品名称': d.name,          // → item_name
    '一级分类': d.series,        // → series
    '菜品定位': d.role,          // → role
    '挂牌价':   d.price,         // → std_price
    '原料成本': d.cost,          // → std_cost
    '销售量':   d.qty,           // → qty_period
    '口味':     d.flavor,        // → flavor
    '烹饪方式': d.craft,         // → craft
    '主料':     d.ingredient,    // → ingredient
    '出品部门': d.series.includes('汤')?'炖品档':(d.series.includes('饮')?'水吧':'热菜档')  // → station
  }));
}

/* ---- B. 清水亭案例聚合值（驱动图元库） --------------------------------- */
const CASE = {
  meta:{ stores:6, sku:118, bills:24752, tables:40840, period:'2026-06-01 → 06-30', periodA:'05-01 → 07-10' },

  recon:[
    { label:'① 账单表头 Σ实收', value:7842874, type:'base', sub:'基准口径' },
    { label:'② 明细去重前 差额', value:830889, type:'delta', sub:'5,597 行系统伪影' },
    { label:'去重：小龙虾伪影', value:-830889, type:'delta', sub:'删除 5,597 行' },
    { label:'② 明细 Σ小计（去重后）', value:7842874, type:'total', sub:'差额 = ¥0 ✓' }
  ],

  dq:[ {axis:'完整性',value:62},{axis:'唯一性',value:74},{axis:'有效性',value:88},
       {axis:'一致性',value:71},{axis:'准确性',value:93},{axis:'时效性',value:96} ],

  stores:[
    { name:'祥云小镇', x:83.5, y:434.7, r:1088000, c:.155 },
    { name:'DT51',    x:73.9, y:432.0, r: 958000, c:.179 },
    { name:'国贸',    x:123.0,y:422.5, r:1559000, c:0    },
    { name:'颐堤港',  x:125.1,y:379.5, r:1425000, c:.125 },
    { name:'世纪金源',x:96.4, y:401.2, r:1160000, c:.098 },
    { name:'五棵松万达',x:88.2,y:396.8, r:1049000, c:.112 }
  ],

  ticket:[
    { label:'≤100',   share:.194, cum:.103, n:3227, upper:100 },
    { label:'100–120',share:.152, cum:.216, n:2530, upper:120 },
    { label:'120–150',share:.224, cum:.444, n:3734, upper:150, highlight:true },
    { label:'150–180',share:.195, cum:.652, n:3248, upper:180, highlight:true },
    { label:'180–300',share:.204, cum:.946, n:3392, upper:300 },
    { label:'>300',   share:.025, cum:1.00, n: 412, upper:9999 }
  ],

  roleFlow:{
    nodes:[
      {id:'s主',side:0,label:'现·主 13',color:'#76551F'},{id:'s辅',side:0,label:'现·辅 29',color:'#A8823C'},
      {id:'s佐',side:0,label:'现·佐 56',color:'#C9A46A'},{id:'s引',side:0,label:'现·引 20',color:'#8C3228'},
      {id:'t主',side:1,label:'建议·主',color:'#76551F'},{id:'t辅',side:1,label:'建议·辅',color:'#A8823C'},
      {id:'t佐',side:1,label:'建议·佐',color:'#C9A46A'},{id:'t引',side:1,label:'建议·引',color:'#8C3228'},
      {id:'t观',side:1,label:'建议·降观察',color:'#706758'}
    ],
    links:[
      {source:'s主',target:'t主',value:2650000},
      {source:'s主',target:'t观',value:400000,changed:true,items:'荆沙甲鱼等 3 款'},
      {source:'s辅',target:'t辅',value:3800000},
      {source:'s辅',target:'t主',value:790000,changed:true,items:'铫子煨排骨莲藕汤（渗透 17.7% 全店第一）'},
      {source:'s佐',target:'t佐',value:4100000},
      {source:'s佐',target:'t引',value:480000,changed:true,items:'武汉热干面（渗透 33.3%）等'},
      {source:'s引',target:'t引',value:2130000},
      {source:'s引',target:'t主',value:1180000,changed:true,items:'【鱼头+藕汤】招牌双人餐（全店销售额第一）'}
    ]
  },

  migration:(()=>{ const cls=['首选品','必售品','观察品','长尾品'];
    const m=[[23,0,0,0],[4,15,0,0],[1,2,12,0],[0,0,7,15]];
    const out=[]; cls.forEach((r,i)=>cls.forEach((c,j)=>out.push({row:r,col:c,v:m[i][j],n:m[i][j]}))); return out; })(),

  nineGrid:[
    {row:'咸鲜/本味/香',col:'快工艺',v:1815000,n:16,base:28},
    {row:'咸鲜/本味/香',col:'慢工艺',v:4021000,n:24,base:40},
    {row:'咸鲜/本味/香',col:'特殊工艺',v:1643000,n:17,base:22},
    {row:'甜/酸',      col:'快工艺',v:275000, n:4, base:28},
    {row:'甜/酸',      col:'慢工艺',v:105000, n:3, base:40},
    {row:'甜/酸',      col:'特殊工艺',v:423000,n:5, base:22},
    {row:'辣/麻',      col:'快工艺',v:746000, n:8, base:28},
    {row:'辣/麻',      col:'慢工艺',v:3470000,n:13,base:40},
    {row:'辣/麻',      col:'特殊工艺',v:0,    n:0, base:22}   // 唯一空白格
  ],

  lifecycle:[
    {name:'导入期',sku:10,amount:490656},{name:'成长期',sku:6,amount:652189},
    {name:'成熟期',sku:18,amount:6161734},{name:'平稳期',sku:24,amount:5197190},
    {name:'衰退期',sku:43,amount:2681066},{name:'淘汰期',sku:17,amount:350468}
  ],

  seriesEff:[
    {name:'套餐',value:4.95,n:4},{name:'湖北煨汤',value:1.89,n:9},{name:'招牌淡水鱼鲜',value:1.78,n:13},
    {name:'小吃点心主食',value:1.12,n:14},{name:'湖北烟火热菜',value:0.94,n:22},{name:'小龙虾',value:0.86,n:14},
    {name:'酒水',value:0.61,n:6},{name:'虾配菜',value:0.19,n:6},{name:'自制饮品甜品',value:0.17,n:25},{name:'凉菜',value:0.01,n:5}
  ],

  structure3421:[
    {name:'首选品',actual:25.4,ideal:30,delta:-4.6},{name:'必售品',actual:17.8,ideal:40,delta:-22.2},
    {name:'观察品',actual:24.6,ideal:20,delta:+4.6},{name:'长尾品',actual:32.2,ideal:10,delta:+22.2}
  ],

  delist:{ sets:[{key:'C1',label:'C1 千单点击 <20'},{key:'C2',label:'C2 额量比 <0.7'},
                 {key:'C3',label:'C3 毛利率 <65%'},{key:'C4',label:'C4 渗透率 <2%'}],
           combos:[{keys:['C1','C2','C3'],n:9,amount:186000},{keys:['C1','C3','C4'],n:5,amount:98000},
                   {keys:['C1','C2','C4'],n:3,amount:66468},{keys:['C1','C2'],n:8,amount:212000},
                   {keys:['C1','C3'],n:6,amount:198000},{keys:['C3','C4'],n:4,amount:129672},
                   {keys:['C1','C2','C3','C4'],n:0,amount:0}] },

  basket:{ nodes:[
      {id:'火烧馍',r:.158,group:'佐'},{id:'丹江大鱼头',r:.160,group:'主'},{id:'排骨藕汤',r:.177,group:'辅'},
      {id:'热干面',r:.333,group:'佐'},{id:'油焖小龙虾',r:.132,group:'辅'},{id:'朝日啤酒',r:.062,group:'引'},
      {id:'蒜蓉小龙虾',r:.118,group:'辅'},{id:'三鲜豆皮',r:.148,group:'佐'},{id:'招牌双人餐',r:.079,group:'引'},
      {id:'虾配菜藕带',r:.096,group:'佐'},{id:'时蔬',r:.132,group:'佐'},{id:'洪湖藕夹',r:.112,group:'佐'}],
    links:[
      {source:'火烧馍',target:'丹江大鱼头',lift:3.03,support:.0766},
      {source:'排骨藕汤',target:'丹江大鱼头',lift:2.14,support:.0512},
      {source:'热干面',target:'排骨藕汤',lift:1.62,support:.0721},
      {source:'油焖小龙虾',target:'朝日啤酒',lift:2.88,support:.0341},
      {source:'油焖小龙虾',target:'蒜蓉小龙虾',lift:2.41,support:.0398},
      {source:'油焖小龙虾',target:'虾配菜藕带',lift:3.31,support:.0455},
      {source:'蒜蓉小龙虾',target:'朝日啤酒',lift:2.02,support:.0246},
      {source:'招牌双人餐',target:'火烧馍',lift:1.85,support:.0198},
      {source:'三鲜豆皮',target:'热干面',lift:1.74,support:.0612},
      {source:'时蔬',target:'丹江大鱼头',lift:1.31,support:.0288},
      {source:'洪湖藕夹',target:'排骨藕汤',lift:1.44,support:.0301}]},

  mainDish:[
    {label:'0 件',n:8731,share:.518,avg:334.9,pax:2.6},
    {label:'1 件',n:5998,share:.356,avg:423.8,pax:2.9},
    {label:'2 件',n:1467,share:.087,avg:646.6,pax:3.9},
    {label:'3 件+',n:278, share:.016,avg:1240.8,pax:5.9}
  ],

  areaTree:{ name:'全司', children:STORES.map(s=>({
    name:s, children:(AREAS[s]||['大厅']).map((a,i)=>({
      name:a, value:Math.round(200000+Math.random()*420000),
      eff: a.includes('包间')?600+Math.random()*60 : (a==='C区'?356: 380+Math.random()*170),
      n: a.includes('包间')? Math.round(120+Math.random()*40) : Math.round(600+Math.random()*700)
    })) })) },

  memberRate:[
    {name:'五棵松万达',value:.0881},{name:'颐堤港',value:.0512},{name:'国贸',value:.0439},
    {name:'祥云小镇',value:.0334},{name:'世纪金源',value:.0287},{name:'DT51',value:.0176},
    {name:'全司',value:.0399}
  ],

  itsEvent:(()=>{ const out=[];
    for(let d=1;d<=30;d++){
      const date=`2026-06-${String(d).padStart(2,'0')}`;
      let v;
      if(d<17) v = 46.8 + Math.sin(d/3)*3.2 + (Math.random()-.5)*3.4 - d*0.12;
      else     v = 33.4 + (d>=27 ? (d-26)*1.6 : 0) + (Math.random()-.5)*3.0;
      out.push({date, value:+v.toFixed(2)});
    } return out; })(),

  momentum:[
    {name:'鲜熬酸梅汤', values:[{t:'W23',rank:24},{t:'W24',rank:18},{t:'W25',rank:11},{t:'W26',rank:6}]},
    {name:'清蒸翘嘴鲌', values:[{t:'W23',rank:19},{t:'W24',rank:16},{t:'W25',rank:14},{t:'W26',rank:9}]},
    {name:'洪湖脆藕排骨汤',values:[{t:'W23',rank:12},{t:'W24',rank:9},{t:'W25',rank:7},{t:'W26',rank:5}]},
    {name:'黄金蒜蓉小龙虾',values:[{t:'W23',rank:2},{t:'W24',rank:3},{t:'W25',rank:6},{t:'W26',rank:11}]},
    {name:'朝日啤酒',   values:[{t:'W23',rank:7},{t:'W24',rank:10},{t:'W25',rank:15},{t:'W26',rank:20}]},
    {name:'油焖小龙虾', values:[{t:'W23',rank:1},{t:'W24',rank:1},{t:'W25',rank:2},{t:'W26',rank:4}]},
    {name:'热干面',     values:[{t:'W23',rank:3},{t:'W24',rank:2},{t:'W25',rank:1},{t:'W26',rank:1}]},
    {name:'排骨藕汤',   values:[{t:'W23',rank:5},{t:'W24',rank:6},{t:'W25',rank:5},{t:'W26',rank:3}]}
  ],

  benefit:[
    {label:'国贸上线套餐',    value:100000,type:'delta',sub:'按五店桌均贡献 ¥74.1 折算'},
    {label:'五店复制火烧馍连带',value:190000,type:'delta',sub:'带馍率 14% → 60%'},
    {label:'恢复藕汤多规格',   value:226000,type:'delta',sub:'煨汤桌均贡献回补 ¥13.4'},
    {label:'主菜渗透 +13.3pt', value:199400,type:'delta',sub:'乐观口径（保守 ¥110,000）'},
    {label:'低效区域桌均提升', value:113000,type:'delta',sub:'颐堤港 C 区 ¥317.7 → ¥408.2'},
    {label:'减：下架 17 款',   value:-29200,type:'delta',sub:'损失 2.3% 销售额'},
    {label:'去重后区间',       value:600000,type:'range',lo:560000,hi:640000,sub:'重叠 20–30%'}
  ],

  targetStructure:[
    {name:'自制饮品甜品',from:25,to:12},{name:'湖北烟火热菜',from:22,to:20},
    {name:'小龙虾',from:14,to:12},{name:'小吃点心主食',from:14,to:13},
    {name:'招牌淡水鱼鲜',from:13,to:15},{name:'湖北煨汤',from:9,to:11},
    {name:'虾配菜',from:6,to:3},{name:'酒水',from:6,to:5},{name:'凉菜',from:5,to:2},{name:'套餐',from:4,to:6}
  ],

  priorities:[
    {name:'五店复制火烧馍连带',x:1,y:190000,r:190000,color:'#76551F'},
    {name:'国贸上线套餐',      x:1,y:100000,r:100000,color:'#76551F'},
    {name:'恢复藕汤多规格',    x:2,y:226000,r:226000,color:'#76551F'},
    {name:'主菜推荐话术',      x:2,y:155000,r:155000,color:'#A8823C'},
    {name:'颐堤港C区改造',     x:3,y:113000,r:113000,color:'#A8823C'},
    {name:'下架 17 款',        x:1,y:29200, r:29200, color:'#A8823C'},
    {name:'辣麻×特殊工艺新品', x:3,y:88000, r:88000, color:'#C9A46A'},
    {name:'会员识别率 →30%',   x:4,y:320000,r:320000,color:'#C9A46A'},
    {name:'秋季螃蟹线开发',    x:4,y:210000,r:210000,color:'#C9A46A'}
  ]
};

global.TIANSIGHTDemo = { DISHES, STORES, AREAS, CASE, genBillDetail, genBillHeader, genItemIndex, reconcile };

})(typeof window !== 'undefined' ? window : globalThis);
