# Style C Layout Lock · Table AI Design System

本文件是 Style C 的硬约束。本文件 fork 自 `references/swiss-layout-lock.md`,与 Style B 的 `S01-S22` 版式 ID 完全一致 —— 只在文末追加 Style C 专属的视觉/排版约束。

---

## Golden Source

原始参考文件 (Style B golden source,Style C 完全继承其版式骨架):

`/Users/guohao/Documents/op7418的仓库/项目/Thin-Harness-Fat-Skills/ppt/index.html`

Style C 主题生成时,除用户明确要求实验版式外,**只能从 `references/layouts-tableai.md` 登记的 22 个版式中选择 (S01-S22)**。这份 lock 文件与 Style B 的 lock 文件共用同一份 ID 集合,只是在结尾加了 Style C 的视觉约束。

---

## Style C 版式 ID 与 Style B 完全对齐

Style C 不发明任何新 S 编号。验证脚本 `scripts/validate-tableai-deck.mjs` 与 Style B 的 `scripts/validate-swiss-deck.mjs` 共用同一份 `allowedLayouts` Set。

---

## 生成前硬规则 (与 Style B 完全一致)

1. 每个正文页都必须先选一个登记版式,并在 `<section>` 上写 `data-layout="Sxx"` (S01-S22) 或 `data-layout="TABLEAI-COVER"` / `data-layout="TABLEAI-CLOSING"`。
2. 不允许临时发明 P23/P24 这类未出现在原始 22P 的正文结构。需要图片时,优先使用 `S22 Image Hero`;多图时使用 `S15/S16` 的原始网格骨架做图片格改造,不要发明新的证据墙。唯一登记的交互扩展是 `S08 + Swiss Map Component`,详见 `references/swiss-map-component.md`(该地图组件在 Style C 中保留,使用深蓝 / 金调色)。
3. 顶部中文标题默认左对齐并贴近左上内容轴。除原始 `S03/S09/S10` 这种 statement/split 版式外,不要把大标题放到页面水平中心。
4. SVG 只能负责几何线条、圆、箭头、路径。不要在 SVG 里写可见文字;所有文字标签用 HTML 放在网格、卡片或 caption 里。
5. 图片槽位和图片生成比例必须绑定。先确定版式和槽位,再生成图片。

---

## Style C 专属视觉约束 (与 Style B 的差异)

> 以下条款**仅**在 Style C (`template-tableai.html`) 下生效。Style B 用户请忽略。

### C1 · 圆角策略

| 元素 | 圆角 |
|------|------|
| `.canvas-card` 主画布 | 0 |
| `.card-fill` / `.card-ink` / `.card-accent` | `4px` |
| `.sub-card` / `.stack-block` | `4px` |
| `.bar-tower .body-block` / `.bar-tower .cap` | `4px` (cap 顶部圆角) |
| `.stat-card` | `3px` |
| `.accent-block` / `.ink-block` / `.grey-block` | `4px` |
| `.tag` / `.label-sm` 标签 | `2px` (允许 pill: `9999px`) |
| `.frame-img` (图片容器) | 0 - 保留瑞士风硬度 |
| `.rule` / `.hatch` / 发丝线 | 0 |

❌ **禁止**:在 hero dark/hero accent 满屏 slide 上给整张 `.canvas-card` 加 `border-radius`(会破坏 100vh 满屏对齐)。

### C2 · 字体策略

| 元素 | 字体 | 字重 |
|------|------|------|
| 全部大标题 (`h-hero` / `h-xl` / `h-xl-zh` / `h-md` / `h-sub`) | `var(--sans-tab)` (Manrope) | 700 / 600 / 500 |
| 全部正文 (`lead` / `body` / `body-sm`) | `var(--sans-tab)` (Manrope) | 400 |
| `.kicker` / `.t-meta` / `.t-cat` / `.chrome-min` | `var(--sans-tab)` + `var(--mono)` | 600 caps |
| `.kpi-hero` / `.kpi-big` / `.kpi-mid` / `.num-mega` / `.name-mega` | `var(--sans-tab)` | 700 |
| mono 数据 (`stat-label` / `.step-nb` / `.pipeline-label`) | `var(--mono)` 保留 | 500/600 |

❌ **禁止**:在 Style C 主题里继续用 Inter `font-weight:200` —— 字重太轻,会让 Manrope SemiBold 更现代的产品级质感丢失。

### C3 · 颜色约束

| 角色 | 值 | 禁止替换为 |
|------|----|-----------|
| 主色 `--ink` | `#0A1626` 寰宇深蓝 | 任何其他 |
| Accent `--accent` | `#A88B52` 日晷暗金 | 任何其他 |
| 底色 `--paper` | `#FFFFFF` 纯白 | 任何 cream / 暖灰 |
| 微光 `--gold-mist` | `rgba(168,139,82,0.08)` | 任何非金色 rgba |

❌ **Style C 唯一禁用**:除 IKB / 黄绿橙之外的多 accent 配色。Table AI 体系只接受金 1 个 accent。

### C4 · Hero 满屏变体

- Style B 默认: `.slide.accent` (IKB 满屏蓝)
- **Style C 默认**: `.slide.dark` (寰宇深蓝满屏 `#0A1626`)
- ASCII 字符场调色板: Style B = 白字符 on IKB 蓝;**Style C = 金字符 on 深蓝** (`rgba(201,168,107, alpha)`)
- hero dark 强调字:Style B = 斜体白字;Style C = **斜体浅金色** (`var(--accent-bright)` `#C9A86B`)
- Closing right-bottom accent takeaway 第 03 条强调字: Style B = IKB 蓝;**Style C = 暗金**

### C5 · Hero 经典变体 (左 ink + 右 paper 对开)

- Style C 接受:`.slide` + `.canvas-card.cover-split` + 左 `.cover-ink` (深蓝) + 右 `.cover-paper` (白)
- 与满屏 dark hero 形成两套开局,看场景选择

### C6 · 间距与字号 (继承,无变化)

8px 网格 + Carbon 2x Grid token + 中文标题降字号逻辑全部继承自 Style B。

---

## 禁止清单 (Style C 专用,继承自 Style B)

- 禁止 `text-align:center` 用在顶部中文大标题
- 禁止将顶部标题写进右侧 7.8fr 栏,造成视觉居中
- 禁止未登记正文页 (P23/P24 等)
- 禁止图片容器灰底包白底信息图
- 禁止 SVG 中出现 `<text>` 作为可见标签
- 禁止图片默认 `object-position:top center` 用于照片
- **禁止** Style C 用任何 `font-weight: 200` 或 `300` 在主标题(超出 Manrope 体验)
- **禁止** 给 Style C 卡片加 `box-shadow`(Table AI design.md 明令禁止)
- **禁止** 把 `--accent` 从 `#A88B52` 改成其他高亮色

---

## 验证

```bash
node scripts/validate-tableai-deck.mjs path/to/index.html
node scripts/validate-tableai-deck.mjs path/to/index.html --allow-experimental
```

验证脚本与 `scripts/validate-swiss-deck.mjs` **共用同一份 `allowedLayouts` 集合**(S01-S22 + 封面/收尾命名)。
