/* ============================================================================
 * 侍天 TIANSIGHT · 分析点注册表 (Analysis Point Registry)
 * ----------------------------------------------------------------------------
 * 这是整个系统的唯一真源 (single source of truth)。
 * 页面、图表、门禁、周期、结论模板全部由此驱动 —— 改表即改系统，不改代码。
 *
 * 字段说明：
 *   id        分析点代号
 *   m         所属模块 M1–M13
 *   layer     依赖层级 L0 地基 / L1 基础 / L2 合成 / L3 行为 / L4 属性 / L5 外部 / L6 收敛
 *   dims      涉及维度族
 *   basis     口径 A(标准价) / B(账单实收) / A+B / EXT(外部)
 *   freq      D日 W周 M月 Q季 Y年 E事件 R每次
 *   imp       重要度 1–5
 *   decision  这一页支持的核心决策（看完明天做什么）
 *   need      必需规范字段（缺任一 → 阻断）
 *   opt       可选字段（缺则降级）
 *   dep       依赖的上游分析点
 *   gates     门禁 ID 列表
 *   pages     [{ id, layout, title, viz }]
 *   rule      计算/判读纪律（渲染到页脚）
 *   say       结论模板（{}内为指标占位符，由计算层填充）
 * ========================================================================== */

window.TIANSIGHT_REGISTRY = {
  meta: {
    name: '侍天 TIANSIGHT 分析体系 Part 1',
    version: '1.0.0',
    basedOn: '方法论手册 v2.0 · 2026-07-27',
    points: 58, modules: 13,
    generated: '2026-08-11'
  },

  /* ---- 模块定义 -------------------------------------------------------- */
  modules: [
    { id:'S0', name:'数据接入与对齐诊断', layer:'L0', desc:'这份数据能出哪些页' },
    { id:'M1', name:'认知层',            layer:'L0', desc:'数据可不可信' },
    { id:'M2', name:'经营基本盘',        layer:'L1', desc:'流量问题还是客单问题' },
    { id:'M3', name:'主辅佐引角色',      layer:'L2', desc:'每道菜扮演什么角色' },
    { id:'M4', name:'ABC 与二八',        layer:'L2', desc:'哪些不能动、哪些先砍' },
    { id:'M5', name:'四大单品指标',      layer:'L2', desc:'每个 SKU 四选一' },
    { id:'M6', name:'结构树',            layer:'L2', desc:'菜单该长成什么形状' },
    { id:'M7', name:'品类倾向与价格',    layer:'L2', desc:'该在哪个价格带补什么' },
    { id:'M8', name:'客单组合与小票',    layer:'L3', desc:'一桌客人该怎么点' },
    { id:'M9', name:'复购与客户资产',    layer:'L3', desc:'会员体系值不值得投' },
    { id:'M10',name:'属性九宫格',        layer:'L4', desc:'该开发什么新品' },
    { id:'M11',name:'季节性与生命周期',  layer:'L2', desc:'该上什么、该下什么' },
    { id:'M12',name:'商圈与竞品',        layer:'L5', desc:'在市场上处于什么位置' },
    { id:'M13',name:'行动与效益',        layer:'L6', desc:'先做哪三件事、值多少钱' }
  ],

  /* ---- 门禁定义 -------------------------------------------------------- */
  gates: {
    'G-RECON':      { sev:'stop',    test:'reconDiffPct > 0.5',      msg:'三路对账不平，全部金额类结论不可信' },
    'G-COST-STALE': { sev:'degrade', test:'costCardAgeDays > 90',    msg:'成本卡逾 90 天未更新，毛利轴仅供内部排序，禁止对外结论' },
    'G-MEMBER':     { sev:'block',   test:'memberIdRate < 0.30',     msg:'会员识别率低于 30%，产品复购分析不可做；其余会员结论为储值样本' },
    'G-ROLE':       { sev:'block',   test:'roleCoverage < 0.80',     msg:'主辅佐引覆盖不足，角色类分析阻断，结构树降级为两层' },
    'G-GUEST':      { sev:'degrade', test:'guestNullRate > 0.20',    msg:'就餐人数缺失过高，人均口径降级为桌均口径' },
    'G-SEAT':       { sev:'watermark',test:'!hasSeatLedger',         msg:'无餐位台账，元/桌/小时为代理指标，禁止与行业 RevPASH 对标' },
    'G-PERIOD-8W':  { sev:'block',   test:'periodWeeks < 8',         msg:'数据期间不足 8 周，无法计算动能趋势' },
    'G-SKU-40':     { sev:'block',   test:'skuCount < 40',           msg:'SKU 数不足，价格空档为噪声' },
    'G-BASIS-MIX':  { sev:'stop',    test:'basisMixDetected',        msg:'检测到跨口径相除，计算层拒绝出数' },
    'G-SUM-CLOSE':  { sev:'stop',    test:'!sumClosed',              msg:'分类各部分之和不等于全量，图元拒绝渲染' },
    'G-CHECKLIST':  { sev:'export',  test:'!checklistPassed',        msg:'A58 八条强制检查未全部通过，禁止导出' }
  },

  /* ---- 58 个分析点 ------------------------------------------------------ */
  points: [

  /* ===== M1 认知层 ===== */
  { id:'A01', m:'M1', layer:'L0', dims:[], basis:'—', freq:'Q', imp:4,
    name:'数据资产盘点',
    decision:'本次报告的边界在哪；下次让客户补什么最值',
    need:['__meta__'], opt:[], dep:[], gates:[],
    pages:[{id:'1-01',layout:'matrix-full',title:'数据资产地图',viz:'heatMatrix'},
           {id:'S0-05',layout:'viz-table',title:'数据缺口与解锁价值排序',viz:'bubbleScatter'}],
    rule:'分 A(已具备)/B(须补齐)/C(外部空缺) 三类；缺口必须按「解锁价值÷获取难度」排序',
    say:'本次识别 {gapP0} 项 P0 缺口，影响 {blockedPoints} 个分析点' },

  { id:'A02', m:'M1', layer:'L0', dims:['D5'], basis:'A+B', freq:'D', imp:5,
    name:'口径定义与三路对账',
    decision:'是否允许出具本次报告',
    need:['received','line_amount','std_price','qty_period'], opt:['receivable'], dep:[], gates:['G-RECON'],
    pages:[{id:'1-02',layout:'viz-full',title:'三路对账瀑布',viz:'waterfall'}],
    rule:'路径①=②为硬条件，差额>0.5% 停机；路径③与①的差 = 折让+期间差+SKU覆盖差，不可相除',
    say:'去重后路径①=②={p1}，差额 {diff}（{diffPct}）' },

  { id:'A03', m:'M1', layer:'L0', dims:['D5'], basis:'B', freq:'D', imp:5,
    name:'数据质量检测',
    decision:'哪些行删、哪些行留、哪些结论要降级',
    need:['bill_no','item_code','qty','unit_price','line_amount'], opt:['guest_count','member_phone','waiter','area'], dep:['A02'],
    gates:['G-GUEST'],
    pages:[{id:'1-03',layout:'roster',title:'去重决策台',viz:'upsetPlot'},
           {id:'1-04',layout:'viz-duo',title:'数据完备度雷达',viz:'radarChart'},
           {id:'1-05',layout:'kpi-grid',title:'缺失率与枚举完整性记分卡',viz:'kpiGrid'}],
    rule:'五类检测；组内规格不同的重复组必须人工确认；枚举字段必须穷举',
    say:'{dupGroups} 组重复中 {artifactRows} 行判为伪影，{keepRows} 行为真实加点' },

  /* ===== M2 经营基本盘 ===== */
  { id:'A04', m:'M2', layer:'L1', dims:['D4','D5'], basis:'B', freq:'M', imp:4,
    name:'门店经营对比',
    decision:'这家店是流量问题还是客单问题——两者解法完全相反',
    need:['store','bill_no','received'], opt:['guest_count','qty','open_time','settle_time','sale_type'], dep:['A02'], gates:['G-GUEST'],
    pages:[{id:'2-01',layout:'viz-full',title:'门店定位气泡图：流量与客单的两难',viz:'bubbleScatter'},
           {id:'2-02',layout:'roster',title:'门店基本盘全表',viz:'rosterTable'},
           {id:'2-05',layout:'viz-full',title:'用餐时长分布与翻台压缩迹象',viz:'histCumulative'}],
    rule:'时长取中位不取均值；气泡图须画等收入背景曲线',
    say:'{hiTraffic} 为高流量低客单，{hiTicket} 为低流量高客单，两者策略相反' },

  { id:'A05', m:'M2', layer:'L1', dims:['D5'], basis:'B', freq:'M', imp:4,
    name:'客单价分布',
    decision:'定价与套餐设计的靶心价格带',
    need:['received','guest_count'], opt:[], dep:['A02'], gates:['G-GUEST'],
    pages:[{id:'2-03',layout:'viz-table',title:'人均消费分布：心智带在哪',viz:'histCumulative'}],
    rule:'必须剔除实收=0 的账单并披露剔除数；同时给中位与均值',
    say:'心智带 {bandLo}–{bandHi}：{bandTablePct} 桌 / {bandAmtPct} 额；中位 {median} · 均值 {mean}（已剔除 {zeroBills} 张零值单）' },

  { id:'A06', m:'M2', layer:'L1', dims:['D5'], basis:'B', freq:'M', imp:4,
    name:'桌型结构',
    decision:'主菜规格该按几人份设计',
    need:['guest_count','received','qty'], opt:['role'], dep:['A02'],
    pages:[{id:'2-04',layout:'viz-duo',title:'桌型结构与主菜渗透的正相关',viz:'barLineCombo'}],
    rule:'桌占比与额占比必须并列',
    say:'{smallTablePct} 的桌为 2–3 人桌，贡献 {smallAmtPct} 收入 → 主菜规格必须为此设计' },

  /* ===== M3 主辅佐引角色 ===== */
  { id:'A07', m:'M3', layer:'L2', dims:['D1','D2'], basis:'A', freq:'Q', imp:5,
    name:'角色分类与一致性校验',
    decision:'角色定义是否可跨店复制',
    need:['role','item_name','qty_period'], opt:['store'], dep:[], gates:['G-ROLE'],
    pages:[{id:'3-02',layout:'matrix-full',title:'跨店角色分歧矩阵',viz:'heatMatrix'},
           {id:'3-03',layout:'roster',title:'分歧全表与合并裁定',viz:'rosterTable'}],
    rule:'合并规则=销量加权多数，必须明示规则并单列分歧全表交管理层裁定',
    say:'{divergeN}/{totalN}（{divergePct}）品项跨店角色不一致' },

  { id:'A08', m:'M3', layer:'L2', dims:['D2'], basis:'A+B', freq:'M', imp:4,
    name:'角色画像',
    decision:'角色定位与实际表现是否一致',
    need:['role','std_price','qty_period'], opt:['std_cost'], dep:['A07','A16'], gates:['G-ROLE','G-COST-STALE'],
    pages:[{id:'3-04',layout:'viz-table',title:'角色画像四指标对照',viz:'parallelCoords'}],
    rule:'五轴必须含渗透率——「主」的失格只在渗透轴上暴露',
    say:'{failRoles} 未达定位标准' },

  { id:'A09', m:'M3', layer:'L2', dims:['D2'], basis:'A+B', freq:'Q', imp:5,
    name:'角色错配识别',
    decision:'哪些菜该换角色',
    need:['role','std_price','qty_period'], opt:[], dep:['A08','A13','A16'], gates:['G-ROLE'],
    pages:[{id:'3-05',layout:'viz-full',title:'角色错配桑基图',viz:'sankeyFlow'},
           {id:'3-06',layout:'roster',title:'错配全量名录',viz:'rosterTable'}],
    rule:'四条判定阈值须随业态标定，不可写死',
    say:'{misN} 项错配，涉及 {misAmtPct} 销售额' },

  /* ===== M4 ABC 与二八 ===== */
  { id:'A10', m:'M4', layer:'L1', dims:['D1'], basis:'A', freq:'M', imp:5,
    name:'ABC 贡献分析',
    decision:'哪些 SKU 是收入主干',
    need:['item_name','std_price','qty_period'], opt:['spec','std_cost'], dep:['A02'],
    pages:[{id:'4-01',layout:'viz-full',title:'帕累托双轴：80% 交点在第几款',viz:'paretoDual'},
           {id:'4-02',layout:'roster',title:'ABC 分级全量名录',viz:'rosterTable'}],
    rule:'80% 交点必须实算并标注 SKU 序号，不可写「约 N 款」',
    say:'{topPct} 的 SKU 贡献 {topAmtPct} 销售额；第 {p80Index} 款处累计达 80%' },

  { id:'A11', m:'M4', layer:'L2', dims:['D1'], basis:'A', freq:'M', imp:5,
    name:'S1/S2 与四分类',
    decision:'哪些绝对不能动、哪些可以先砍',
    need:['item_name','std_price','qty_period'], opt:['std_cost'], dep:['A10'], gates:['G-SUM-CLOSE'],
    pages:[{id:'4-03',layout:'viz-duo',title:'S1/S2 集合韦恩图',viz:'vennArea'},
           {id:'4-04',layout:'viz-table',title:'四分类结构对照',viz:'stackedFlow'},
           {id:'4-05',layout:'roster',title:'四分类全量名录（逐一列名）',viz:'rosterTable'}],
    rule:'完整性纪律：四类之和=全量，且必须逐一列名。只给计数不给名录=没有结论',
    say:'首选 {c1} · 必售 {c2} · 观察 {c3} · 长尾 {c4}，合计 {total} = 全量 ✓' },

  { id:'A12', m:'M4', layer:'L2', dims:['D1'], basis:'A+B', freq:'M', imp:4,
    name:'双口径迁移矩阵',
    decision:'用标准价做结构决策是否安全',
    need:['item_name','std_price','qty_period','line_amount'], opt:[], dep:['A11'],
    pages:[{id:'4-06',layout:'matrix-full',title:'双口径迁移矩阵',viz:'heatMatrix'},
           {id:'4-07',layout:'viz-full',title:'双口径排名斜率图',viz:'slopeBump'}],
    rule:'一致率<80% → 折让或按斤计价已严重扭曲判断，口径 A 全部结论须加警示',
    say:'一致率 {consistency}（{agree}/{comparable}），{crossLevel}' },

  /* ===== M5 四大单品指标 ===== */
  { id:'A13', m:'M5', layer:'L1', dims:['D1'], basis:'A', freq:'M', imp:3,
    name:'额量比',
    decision:'价格定位（不是销售表现）',
    need:['std_price'], opt:[], dep:['A10'],
    pages:[{id:'5-02a',layout:'viz-full',title:'额量比分布',viz:'beeswarm'}],
    rule:'数学上 ≡ 售价÷全店均价，与销量无关。当销售表现指标用属禁止操作',
    say:'全店单品均价 {avgPrice} = 1.0 基准' },

  { id:'A14', m:'M5', layer:'L1', dims:['D1'], basis:'A', freq:'M', imp:4,
    name:'千单点击',
    decision:'曝光转化效率',
    need:['qty_period','bill_no'], opt:[], dep:['A10'], gates:['G-BASIS-MIX'],
    pages:[{id:'5-02b',layout:'viz-full',title:'千单点击分布',viz:'beeswarm'}],
    rule:'分母=开台数(口径A期间)。会被一桌多件放大，必须与 A16 并看',
    say:'中位 {median}，极值 {max}（{maxItem}）' },

  { id:'A15', m:'M5', layer:'L1', dims:['D1'], basis:'A', freq:'M', imp:5,
    name:'毛利率',
    decision:'利润贡献',
    need:['std_price','std_cost'], opt:[], dep:[], gates:['G-COST-STALE'],
    pages:[{id:'5-02c',layout:'viz-full',title:'毛利率分布',viz:'beeswarm'}],
    rule:'成本卡>90天未更新 → 全部下游结论打水印。静态成本已导致「大份高毛利」方向性误判',
    say:'加权毛利率 {weighted}，中位 {median}' },

  { id:'A16', m:'M5', layer:'L1', dims:['D1','D5'], basis:'B', freq:'M', imp:5,
    name:'渗透率',
    decision:'有多少桌真的点了它',
    need:['bill_no','item_name'], opt:['sale_type'], dep:['A02'], gates:['G-BASIS-MIX'],
    pages:[{id:'5-02d',layout:'viz-full',title:'渗透率分布',viz:'beeswarm'}],
    rule:'分母=堂食账单数(口径B期间)。与 A14 分母不同，系统级禁止相除',
    say:'中位 {median}，最高 {max}（{maxItem}）' },

  { id:'A17', m:'M5', layer:'L2', dims:['D1'], basis:'A+B', freq:'M', imp:5,
    name:'四象限矩阵',
    decision:'每个 SKU 四选一：保护 / 强制曝光 / 优化成本 / 精简',
    need:['std_price','std_cost','qty_period','bill_no'], opt:[], dep:['A14','A15'], gates:['G-COST-STALE','G-SUM-CLOSE'],
    pages:[{id:'5-04',layout:'viz-full',title:'四象限矩阵',viz:'quadrant'},
           {id:'5-05',layout:'roster',title:'四象限全量名录 ×4',viz:'rosterTable'}],
    rule:'「≥中位数」统一归高侧，图上标 ≥ 符号',
    say:'流量品以 {flowSkuPct} 的 SKU 数占 {flowAmtPct} 销售额——它才是毛利优化的主战场' },

  { id:'A18', m:'M5', layer:'L2', dims:['D1'], basis:'A+B', freq:'Q', imp:5,
    name:'待下架筛选',
    decision:'精简哪几款',
    need:['std_price','std_cost','qty_period','bill_no'], opt:[], dep:['A13','A14','A15','A16'], gates:['G-COST-STALE'],
    pages:[{id:'5-06',layout:'viz-table',title:'待下架命中矩阵',viz:'upsetPlot'},
           {id:'5-07',layout:'roster',title:'例外复议台',viz:'rosterTable'}],
    rule:'命中≥3 建议下架、=4 立即执行。三类例外须复议：必售品/高毛利地域符号品/上升期新品',
    say:'精简 {n} 款释放 {skuPct} SKU 数，仅损失 {amtPct} 销售额' },

  { id:'A19', m:'M5', layer:'L2', dims:['D1'], basis:'A+B', freq:'Q', imp:5,
    name:'高潜品识别',
    decision:'投入最低、见效最快的毛利池',
    need:['std_price','std_cost','qty_period'], opt:[], dep:['A17','A18'], gates:['G-COST-STALE'],
    pages:[{id:'5-08',layout:'viz-table',title:'高潜品 TOP 20：产品已存在，只缺曝光',viz:'bubbleArrow'}],
    rule:'建议必须落到具体曝光动作（菜单版位/话术/陈列），否则是空头结论',
    say:'{n} 款高潜品，潜在毛利增量 {upside}' },

  /* ===== M6 结构树 ===== */
  { id:'A20', m:'M6', layer:'L2', dims:['D1','D2'], basis:'A', freq:'Q', imp:4,
    name:'菜单结构树',
    decision:'一页看清菜单形状',
    need:['role','series','item_name','std_price','qty_period'], opt:['std_cost'], dep:['A07'], gates:['G-ROLE'],
    pages:[{id:'6-01',layout:'viz-full',title:'菜单结构旭日图',viz:'sunburst'}],
    rule:'三层展开；明度编码毛利，让「大而薄」的系列发白',
    say:'主 {r1} · 辅 {r2} · 佐 {r3} · 引 {r4}' },

  { id:'A21', m:'M6', layer:'L2', dims:['D1'], basis:'A', freq:'Q', imp:3,
    name:'3-4-2-1 达标',
    decision:'结构失衡在哪一类',
    need:['item_name','std_price','qty_period'], opt:[], dep:['A11'],
    pages:[{id:'6-02',layout:'viz-duo',title:'3-4-2-1 达标对照',viz:'divergingBar'}],
    rule:'缺配与超配数量对称，说明存在「本该培养成必售、实际掉进长尾」的产品',
    say:'必售 {d2}pt · 长尾 {d4}pt，{symmetryNote}' },

  { id:'A22', m:'M6', layer:'L2', dims:['D1'], basis:'A', freq:'Q', imp:4,
    name:'系列效率指数',
    decision:'该砍哪个系列',
    need:['series','std_price','qty_period'], opt:[], dep:['A10'],
    pages:[{id:'6-03',layout:'viz-table',title:'系列效率指数',viz:'lollipop'}],
    rule:'必须用对数轴（极值可差 20–30 倍），基准线 1.0',
    say:'{best} {bestVal} vs {worst} {worstVal}，差 {ratio} 倍' },

  { id:'A23', m:'M6', layer:'L2', dims:['D1'], basis:'A+B', freq:'Q', imp:5,
    name:'目标结构与精简清单',
    decision:'从现有 SKU 收敛到哪些',
    need:['series','item_name','std_price','qty_period'], opt:[], dep:['A11','A18','A19','A22'], gates:['G-SUM-CLOSE'],
    pages:[{id:'6-04',layout:'viz-full',title:'目标结构：削减与新增',viz:'dumbbell'},
           {id:'6-05',layout:'roster',title:'精简清单全表（逐一列名）',viz:'rosterTable'}],
    rule:'必须逐一列名。从「该砍 15 款」变成「该砍这 15 款」是本体系与通用 BI 的分界线',
    say:'削减 {cut} 款（{cutAmt} · {cutPct}）+ 新增 {add} 款 = 净 {net}，{from} → {to}' },

  /* ===== M7 品类倾向与价格 ===== */
  { id:'A24', m:'M7', layer:'L2', dims:['D1','D5'], basis:'B', freq:'M', imp:4,
    name:'品类倾向系数',
    decision:'哪个品类有加购空间',
    need:['series','bill_no','qty','line_amount'], opt:[], dep:['A02'],
    pages:[{id:'7-01',layout:'viz-full',title:'渗透率 × 倾向系数散点',viz:'quadrant'},
           {id:'7-02',layout:'roster',title:'品类倾向全表',viz:'rosterTable'}],
    rule:'两指标必须并看：高渗透+低倾向=每桌只点一件，加购空间最大',
    say:'{must} 是唯一倾向系数 >1 的品类 = 真正的必点层' },

  { id:'A25', m:'M7', layer:'L2', dims:['D1'], basis:'A', freq:'Q', imp:4,
    name:'价格带分布',
    decision:'各系列的价格跨度与集中度',
    need:['series','std_price'], opt:[], dep:[],
    pages:[{id:'7-03',layout:'viz-table',title:'价格带分布',viz:'boxStrip'}],
    rule:'单一价格点的系列须单独标记，属定价惰性',
    say:'跨度最大 {widest}，单一价格点系列 {flatN} 个' },

  { id:'A26', m:'M7', layer:'L2', dims:['D1'], basis:'A', freq:'Q', imp:4,
    name:'价格空档扫描',
    decision:'该在哪个价格带补产品',
    need:['std_price','item_name'], opt:['series'], dep:[], gates:['G-SKU-40'],
    pages:[{id:'7-04',layout:'viz-full',title:'价格轴空档扫描',viz:'barcodeGap'},
           {id:'7-05',layout:'viz-duo',title:'空档参数敏感性检验',viz:'smallMultiples'}],
    rule:'10 元步长，须声明是否含套餐与 SKU 数。只有在所有参数组合下都为空的区间才是稳健空档',
    say:'稳健空档：{robustGaps}；最宽 {widestGap}' },

  { id:'A27', m:'M7', layer:'L2', dims:['D1'], basis:'A', freq:'Q', imp:3,
    name:'价格带 × 品类交叉',
    decision:'空档该由哪个品类补位',
    need:['series','std_price','qty_period'], opt:[], dep:['A25','A26'],
    pages:[{id:'7-06',layout:'matrix-full',title:'价格带 × 品类交叉',viz:'heatMatrix'}],
    rule:'与 A44 联合出结论，才能落到具体菜名',
    say:'{band} 带由 {n} 个 SKU 贡献 {series} 的 {pct} 销售额' },

  /* ===== M8 客单组合与小票 ===== */
  { id:'A28', m:'M8', layer:'L3', dims:['D2','D5'], basis:'B', freq:'M', imp:5,
    name:'角色组合结构',
    decision:'各店点单结构差异在哪一层',
    need:['bill_no','role','qty','line_amount'], opt:['store'], dep:['A07'], gates:['G-ROLE'],
    pages:[{id:'8-01',layout:'viz-table',title:'角色组合结构',viz:'stackedBar'}],
    rule:'件/桌须拆到角色层，否则店间差异无法归因',
    say:'{best} {bestQty} 件/桌 vs {worst} {worstQty}（差 {gap}）' },

  { id:'A29', m:'M8', layer:'L3', dims:['D2','D5'], basis:'B', freq:'M', imp:5,
    name:'主菜渗透杠杆',
    decision:'全店第一大单一增量来源',
    need:['bill_no','role','received'], opt:['guest_count'], dep:['A28'], gates:['G-ROLE','G-GUEST'],
    pages:[{id:'8-02',layout:'viz-full',title:'主菜渗透杠杆',viz:'stepArea'},
           {id:'8-03',layout:'verdict',title:'因果边界：乐观与保守双口径',viz:'rangeBar'}],
    rule:'必须同时给乐观与保守两个口径；组间不可比（人数混杂）。验证方式=A/B 测试',
    say:'{zeroPct} 的桌一道主菜都没点；增量区间 {consLo}–{optHi}/月' },

  { id:'A30', m:'M8', layer:'L3', dims:['D2','D5'], basis:'B', freq:'Q', imp:4,
    name:'点单公式标定',
    decision:'把数据结论翻译成服务话术',
    need:['bill_no','role','qty','guest_count'], opt:[], dep:['A28','A06'], gates:['G-ROLE'],
    pages:[{id:'8-04',layout:'concept',title:'点单公式标定',viz:'formulaCard'}],
    rule:'目标组合须可执行，不可给小数',
    say:'2 人桌目标：{formula2}，桌均 {cur2} → {tgt2}' },

  { id:'A31', m:'M8', layer:'L3', dims:['D1','D5'], basis:'B', freq:'M', imp:5,
    name:'连带分析',
    decision:'唯一能发现「已跑通、可复制」模型的分析',
    need:['bill_no','item_name'], opt:['is_gift','store'], dep:['A16'],
    pages:[{id:'8-05',layout:'viz-full',title:'连带网络图',viz:'forceNetwork'},
           {id:'8-06',layout:'viz-duo',title:'分店拆解：可复制的单店模型',viz:'barBenchmark'},
           {id:'8-07',layout:'roster',title:'连带规则全表',viz:'rosterTable'}],
    rule:'前置剔除赠品与仅含赠品账单；过滤共现≥100 桌。分店拆解才是真正价值',
    say:'{a}×{b} 提升度 {lift}；{topStore} 达 {topRate}，其余店 {otherRate} → 复制估算月增 {upside}' },

  { id:'A32', m:'M8', layer:'L3', dims:['D4','D5'], basis:'B', freq:'M', imp:4,
    name:'时段分析',
    decision:'高峰期是否在压缩客单',
    need:['open_time','received','bill_no'], opt:['meal_period','settle_time'], dep:['A02'],
    pages:[{id:'8-08',layout:'matrix-full',title:'时段热力矩阵',viz:'heatMatrix'}],
    rule:'桌数、桌均、时长三层须叠加，才能识别「翻台压缩客单」',
    say:'双高峰 {peak1} 与 {peak2}；{crunchHour} 时桌数最多但桌均降至 {crunchAvg}' },

  { id:'A33', m:'M8', layer:'L3', dims:['D4','D5'], basis:'B', freq:'M', imp:3,
    name:'星期 / 周末分析',
    decision:'周末靠桌数还是靠客单',
    need:['open_time','received','bill_no'], opt:[], dep:['A02'],
    pages:[{id:'8-09',layout:'viz-duo',title:'星期结构',viz:'groupedBar'}],
    rule:'日均桌数须除以该月实际天数（周末天数不等）',
    say:'周末桌均 {weAvg} vs 工作日 {wdAvg}；日均桌 {weTables} vs {wdTables}（{tableGap}）' },

  { id:'A34', m:'M8', layer:'L3', dims:['D4','D5'], basis:'B', freq:'M', imp:4,
    name:'区域效率',
    decision:'哪块空间被低估',
    need:['area','received','open_time','settle_time'], opt:['store'], dep:['A02'], gates:['G-SEAT'],
    pages:[{id:'8-10',layout:'viz-full',title:'区域效率树图',viz:'treemapNest'}],
    rule:'元/桌/小时 = 桌均÷(中位时长÷60)；桌数>30 才纳入；代理指标禁止外部对标',
    say:'{topArea} {topEff} 元/桌/小时（日均仅 {topTables} 桌）vs {lowArea} {lowEff}' },

  { id:'A35', m:'M8', layer:'L3', dims:['D1','D5'], basis:'B', freq:'M', imp:4,
    name:'外卖结构',
    decision:'外卖是蚕食还是互补',
    need:['sale_type','line_amount','item_name'], opt:[], dep:['A02'],
    pages:[{id:'8-11',layout:'viz-table',title:'外卖结构',viz:'stackedBar'}],
    rule:'sale_type 必须穷举全部取值（堂食/外卖/外带/自提）',
    say:'{n} 单 · {amt}（{pct} 收入）· 单均 {avg}；{keyDiff}' },

  /* ===== M9 复购与客户资产 ===== */
  { id:'A39', m:'M9', layer:'L3', dims:['D6'], basis:'B', freq:'W', imp:5,
    name:'会员识别率',
    decision:'M9 其余四项的开关',
    need:['bill_no','member_phone'], opt:['store'], dep:['A02'], gates:['G-MEMBER'],
    pages:[{id:'9-01',layout:'viz-full',title:'识别率闸门',viz:'bulletChart'}],
    rule:'<30% → A40 硬阻断。这是运营动作的直接反馈指标，故为周频',
    say:'全司 {rate}，目标 30%；会员桌均 {mAvg} vs 非会员 {nAvg}（{gap}）' },

  { id:'A36', m:'M9', layer:'L3', dims:['D6'], basis:'B', freq:'M', imp:5,
    name:'复购率与次数分布',
    decision:'会员资产的真实厚度',
    need:['member_phone','tx_time'], opt:['tx_amount','store'], dep:['A39'], gates:['G-MEMBER'],
    pages:[{id:'9-03',layout:'viz-table',title:'复购率与次数分布',viz:'histCumulative'}],
    rule:'样本偏差强制披露：储值会员非随机抽样，禁止写「本品牌的复购率」',
    say:'储值会员样本复购率 {rate}，复购贡献 {contrib} 消费额（价值倍数 {mult}）' },

  { id:'A37', m:'M9', layer:'L3', dims:['D6'], basis:'B', freq:'M', imp:4,
    name:'复购间隔',
    decision:'营销触达的时间窗',
    need:['member_phone','tx_time'], opt:[], dep:['A39'], gates:['G-MEMBER'],
    pages:[{id:'9-04',layout:'viz-full',title:'复购间隔分布',viz:'histCumulative'}],
    rule:'取中位，不取均值',
    say:'中位间隔 {median} 天 → 触达窗口设在第 {window} 天' },

  { id:'A38', m:'M9', layer:'L3', dims:['D6','D5'], basis:'B', freq:'M', imp:4,
    name:'会员价值对比',
    decision:'提升识别率的 ROI 依据',
    need:['member_phone','received'], opt:[], dep:['A39'], gates:['G-MEMBER'],
    pages:[{id:'9-02',layout:'viz-duo',title:'会员价值对比',viz:'groupedBar'}],
    rule:'差值即 A39 投入的收益上限',
    say:'会员桌均高出 {gap}' },

  { id:'A40', m:'M9', layer:'L3', dims:['D1','D6'], basis:'B', freq:'Q', imp:4,
    name:'产品复购能力',
    decision:'区分「产品力」与「单店执行」',
    need:['member_phone','item_name','tx_time'], opt:[], dep:['A39'], gates:['G-MEMBER'],
    pages:[{id:'9-05',layout:'verdict',title:'产品复购【识别率不足时不可做】+ 替代指标',viz:'boxPlot'}],
    rule:'识别率<30% 时系统拒绝渲染；替代指标=渗透率跨门店稳定性（箱宽）',
    say:'替代指标：{stable} 跨店稳定（{stableRange}）；{unstable} 极不稳（{unstableRange}）→ 后者是执行问题不是产品问题' },

  /* ===== M10 属性九宫格 ===== */
  { id:'A41', m:'M10', layer:'L4', dims:['D3'], basis:'A', freq:'Q', imp:4,
    name:'味型 × 工艺九宫格',
    decision:'技术护城河在哪、白地在哪',
    need:['flavor','craft','std_price','qty_period'], opt:[], dep:[],
    pages:[{id:'10-01',layout:'matrix-full',title:'味型 × 工艺九宫格',viz:'heatMatrix'}],
    rule:'多门店合并必须取任一非空值，不可取第一条（否则空值覆盖真值）',
    say:'{moatCells} 合计 {moatPct} 销售额 = 技术护城河；{blankCell} 是唯一空白格' },

  { id:'A42', m:'M10', layer:'L4', dims:['D3'], basis:'A', freq:'Q', imp:4,
    name:'味型 × 食材矩阵',
    decision:'食材覆盖缺口',
    need:['flavor','ingredient'], opt:['std_price','qty_period'], dep:[],
    pages:[{id:'10-02',layout:'matrix-full',title:'味型 × 食材矩阵',viz:'bubbleMatrix'}],
    rule:'零值格判读纪律：只有该列基数≥7 SKU 或≥5% 额占比的零值格才算缺口',
    say:'{zeroCells} 个零值格中仅 {realGaps} 个基数足够，构成真实缺口' },

  { id:'A43', m:'M10', layer:'L4', dims:['D3'], basis:'A', freq:'Q', imp:3,
    name:'工艺—毛利关系',
    decision:'哪类工艺该推、哪类该压成本',
    need:['craft','std_price','std_cost','qty_period'], opt:[], dep:[], gates:['G-COST-STALE'],
    pages:[{id:'10-03',layout:'viz-full',title:'工艺—毛利散点',viz:'quadrant'}],
    rule:'高额低毛利与低额高毛利是两类完全不同的动作',
    say:'{riskCraft} 高额低毛利（{riskPct}/{riskGm}）；{oppCraft} 低额高毛利（{oppPct}/{oppGm}）' },

  { id:'A44', m:'M10', layer:'L4', dims:['D3'], basis:'A', freq:'Q', imp:4,
    name:'九宫格补漏建议',
    decision:'该开发什么新品（具体到菜名）',
    need:['flavor','craft','ingredient','std_price'], opt:[], dep:['A41','A42','A26'],
    pages:[{id:'10-04',layout:'roster',title:'补漏建议清单',viz:'rosterTable'}],
    rule:'建议必须同时满足「属性白地 + 价格空档」两个条件才标 P0',
    say:'P0 {p0N} 项、P1 {p1N} 项' },

  /* ===== M11 季节性与生命周期 ===== */
  { id:'A45', m:'M11', layer:'L2', dims:['D1','D4'], basis:'B', freq:'W', imp:5,
    name:'季节性品类走势',
    decision:'品类是否在退潮',
    need:['open_time','series','line_amount'], opt:[], dep:['A02'], gates:['G-PERIOD-8W'],
    pages:[{id:'11-01',layout:'viz-full',title:'季节性品类走势',viz:'areaTrend'}],
    rule:'旬度或周度粒度，月度粒度会错过接棒窗口',
    say:'{series} 占比 {from} → {to}（{trend}）' },

  { id:'A46', m:'M11', layer:'L2', dims:['D1','D4'], basis:'B', freq:'E', imp:3,
    name:'节日产品窗口',
    decision:'节令品的上下架节奏',
    need:['open_time','item_name','qty'], opt:['menu_log'], dep:['A02'],
    pages:[{id:'11-02',layout:'viz-duo',title:'节日产品窗口',viz:'ganttCalendar'}],
    rule:'提前 14 天上、节后 2 天下为基准模板',
    say:'{item} 在售 {days} 天、售出 {qty} 件，{verdict}' },

  { id:'A47', m:'M11', layer:'L2', dims:['D1','D4'], basis:'B', freq:'E', imp:5,
    name:'产品替换事件分析',
    decision:'这次换品到底亏没亏',
    need:['open_time','item_name','line_amount','series'], opt:[], dep:['A02'],
    pages:[{id:'11-03',layout:'viz-full',title:'替换事件中断时序',viz:'itsPlot'},
           {id:'11-04',layout:'verdict',title:'因果边界：爬坡期还是结构性损失',viz:'rangeBar'}],
    rule:'必须同时看品类层与全店层；须判断爬坡期 vs 结构性损失；年化推算属上限，非损失确认',
    say:'品类桌均贡献 {catBefore} → {catAfter}（{catDelta}），全店桌均 {allDelta}——损失被其他品类吸收' },

  { id:'A48', m:'M11', layer:'L2', dims:['D1','D4'], basis:'B', freq:'W', imp:5,
    name:'周度动能榜',
    decision:'区分「卖不动」与「刚上市」',
    need:['open_time','item_name','qty','bill_no'], opt:[], dep:['A02'], gates:['G-PERIOD-8W'],
    pages:[{id:'11-05',layout:'viz-table',title:'周度动能榜',viz:'slopeBump'}],
    rule:'单位=件/千桌（消除桌数波动）。与 A18 冲突时以动能优先',
    say:'上升 TOP：{up}；下降 TOP：{down}。{conflictNote}' },

  { id:'A49', m:'M11', layer:'L2', dims:['D1'], basis:'A+B', freq:'Q', imp:4,
    name:'生命周期分级',
    decision:'每款产品处在哪个阶段',
    need:['item_name','std_price','qty_period'], opt:[], dep:['A11','A16','A18','A48'], gates:['G-SUM-CLOSE'],
    pages:[{id:'11-06',layout:'viz-full',title:'生命周期六阶段',viz:'stackedFlow'},
           {id:'11-07',layout:'roster',title:'生命周期全量名录 ×6',viz:'rosterTable'}],
    rule:'必须 100% 覆盖全量。凡出现「约」字即为未实算。粒度局限：动能在品项级，多规格共享',
    say:'导入 {s1} · 成长 {s2} · 成熟 {s3} · 平稳 {s4} · 衰退 {s5} · 淘汰 {s6}，合计 {total} = 全量 ✓' },

  { id:'A50', m:'M11', layer:'L2', dims:['D1','D4'], basis:'—', freq:'Q', imp:4,
    name:'季节性产品日历',
    decision:'退潮后谁接棒',
    need:['series','item_name'], opt:['open_time'], dep:['A45'],
    pages:[{id:'11-08',layout:'viz-full',title:'季节产品日历',viz:'ganttCalendar'}],
    rule:'缺口须与本地物产结合，才能落到具体品类',
    say:'{gapSeason} 完全空白；{peakSeason} 退潮后无接棒品类' },

  /* ===== M12 商圈与竞品 ===== */
  { id:'A51', m:'M12', layer:'L5', dims:['D14'], basis:'EXT', freq:'Q', imp:3,
    name:'商圈定位', decision:'定价与商圈是否错配',
    need:['__external_trade_area__'], opt:[], dep:[], gates:[],
    pages:[{id:'12-01',layout:'viz-full',title:'商圈定位散点',viz:'bubbleScatter'}],
    rule:'45° 参考线 = 与商圈同频', say:'【待采集】自身基准：人均 {ownRange}' },

  { id:'A52', m:'M12', layer:'L5', dims:['D14'], basis:'EXT', freq:'Q', imp:4,
    name:'竞品价格带对比', decision:'空档是结构缺失还是份额流失',
    need:['__external_competitor__'], opt:[], dep:['A26'], gates:[],
    pages:[{id:'12-02',layout:'viz-full',title:'竞品价格带山脊图',viz:'ridgeline'}],
    rule:'与 A26 联合，才能判断空档的商业含义', say:'【待采集】自身分布：{ownBands}' },

  { id:'A53', m:'M12', layer:'L5', dims:['D14'], basis:'EXT', freq:'Q', imp:3,
    name:'竞品结构对比', decision:'结构差异在哪一层',
    need:['__external_competitor__'], opt:[], dep:['A20'], gates:[],
    pages:[{id:'12-03',layout:'viz-duo',title:'竞品结构对比',viz:'stackedBar'}],
    rule:'—', say:'【待采集】自身配比：{ownRoles}' },

  { id:'A54', m:'M12', layer:'L5', dims:['D14'], basis:'EXT', freq:'Y', imp:2,
    name:'榜单分析', decision:'上榜差距',
    need:['__external_ranking__'], opt:[], dep:[], gates:[],
    pages:[{id:'12-04',layout:'viz-table',title:'榜单分析',viz:'rosterTable'}],
    rule:'变动慢，年频足够', say:'【待采集】' },

  { id:'A55', m:'M12', layer:'L5', dims:['D5'], basis:'EXT', freq:'Q', imp:3,
    name:'对标店客单反证', decision:'逆推竞品菜单结构',
    need:['__external_receipts__'], opt:[], dep:[], gates:[],
    pages:[{id:'12-05',layout:'roster',title:'对标店客单反证',viz:'rosterTable'}],
    rule:'—', say:'【待采集】自身基准：桌均 {ownAvg}' },

  /* ===== M13 行动与效益 ===== */
  { id:'A56', m:'M13', layer:'L6', dims:[], basis:'A+B', freq:'Q', imp:5,
    name:'行动优先级矩阵',
    decision:'未来 90 天先做哪三件事',
    need:['__all_conclusions__'], opt:[], dep:['A09','A18','A19','A23','A29','A31','A34','A44','A47'], gates:[],
    pages:[{id:'13-01',layout:'viz-full',title:'行动优先级矩阵',viz:'quadrant'},
           {id:'13-02',layout:'roster',title:'P0 行动卡',viz:'rosterTable'}],
    rule:'每条行动必须带验证指标，否则无法复盘',
    say:'P0 {p0} 项（0–30 天）· P1 {p1} 项 · P2 {p2} 项' },

  { id:'A57', m:'M13', layer:'L6', dims:[], basis:'B', freq:'Q', imp:5,
    name:'效益测算与归因去重',
    decision:'预计带来多少钱（区间）',
    need:['__all_conclusions__'], opt:[], dep:['A56'], gates:[],
    pages:[{id:'13-03',layout:'viz-full',title:'效益测算瀑布',viz:'waterfall'},
           {id:'13-04',layout:'viz-duo',title:'归因重叠',viz:'chordOverlap'}],
    rule:'三件事强制：①声明乐观/保守 ②列出重叠关系 ③给区间而非点值。各项直接相加属禁止操作',
    say:'点值合计 {point}，去重后区间 {lo}–{hi}（{pctLo}–{pctHi}）' },

  { id:'A58', m:'M13', layer:'L6', dims:[], basis:'—', freq:'R', imp:5,
    name:'结论审查与证伪登记',
    decision:'如果错了怎么知道',
    need:['__all_conclusions__'], opt:[], dep:['A57'], gates:['G-CHECKLIST'],
    pages:[{id:'13-05',layout:'verdict',title:'争议点与证伪登记',viz:'cardGrid'},
           {id:'13-06',layout:'roster',title:'强制检查清单执行记录',viz:'rosterTable'}],
    rule:'四段结构：争议点/事实/处理/证伪条件。八条检查未全勾 → 禁止导出',
    say:'登记 {n} 处分析师判断，{verified} 处已证实，{pending} 处待验证' }

  ],

  /* ---- A58 强制检查清单 ------------------------------------------------- */
  checklist: [
    '所有表格的行合计 = 表内标注的合计',
    '所有分类的 SKU 数之和 = 全量',
    '文中出现「约」「大致」的地方，均已实算',
    '只给了计数的结论，均已列出名录',
    '同一指标在不同章节的分母一致',
    '图表数值逐一回溯源数据（非从正文抄或区间插值）',
    '枚举型字段已穷举全部取值',
    '多源合并使用「取非空值」而非「取第一条」'
  ],

  /* ---- 六条禁止操作（计算层硬约束） ------------------------------------- */
  forbidden: [
    { rule:'口径A金额 ÷ 口径B金额', why:'期间、价格基准、SKU 覆盖三者皆不同' },
    { rule:'额量比当销售表现指标', why:'数学上 ≡ 售价÷全店均价，与销量无关' },
    { rule:'元/桌/小时 与行业 RevPASH 对标', why:'分母不含空置时间与餐位数' },
    { rule:'用储值会员复购率代表全店', why:'样本存在正向选择偏差' },
    { rule:'各项效益直接相加', why:'作用于重叠的桌，须归因去重' },
    { rule:'千单点击分母 与 渗透率分母 混用', why:'期间与口径均不同' }
  ]
};
