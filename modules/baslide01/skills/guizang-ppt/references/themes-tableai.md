# Table AI 主题色预设（Style C · Table AI Design System）

Table AI 视觉系统是 Style B 瑞士国际主义的 **品牌化变体**。结构、22 个版式、动效系统、网格逻辑全部继承自 Style B —— 只重写配色、字体、卡片圆角，保留单锚点色的硬规则。

> 🆕 **Style C = Style B · 换色版**
> 原仓库：[fengurt/tableai_designaha](https://github.com/fengurt/tableai_designaha)
> 当前 fork 保留 Style B 的全部 22 个锁定版式 `S01-S22`，只重写颜色 / 字体 / 圆角。

---

## 设计哲学（来自 design.md）

1. **利他 (Altruistic)** — 界面直观，操作高效。
2. **真实 (Authentic)** — 拒绝过度装饰，展现材质与结构美。
3. **艺术 (Artistic)** — 比例、对齐、留白的艺术平衡。
4. **优雅 (Elegant)** — 色彩与细节传递高端质感。

斯堪的纳维亚极简 + 微圆角（2-4px）+ 严格 8px 网格。

---

## 颜色系统

**严守品牌色值**。基础 hex 全部来自 Table AI Design System：

| 角色 | Token | Hex | 用途 |
|------|-------|-----|------|
| 底色 | `--paper` | `#FFFFFF` | 主背景、大面积留白 |
| 主色 | `--ink` | `#0A1626` | 文字主色、结构线条、重要功能块、品牌标识 |
| 点缀色 | `--accent` | `#A88B52` | CTA、交互反馈、关键数据、精细装饰（**日晷暗金**） |
| 表面 | `--paper-rgb` | `255, 255, 255` | 透明背景色用 |
| 文字次级 | `--ink-rgb` | `10, 22, 38` | 透明文字用 |
| 暗灰装饰 | `--gold-mist` | `rgba(168, 139, 82, 0.08)` | 极细金色微光（hover/active 装饰） |

**核心约束**（与 Style B 一致）：
- ❌ 不允许用户自定义 hex 值
- ❌ 不允许混搭多个高亮色（Table AI 体系只有金色 1 个 accent）
- ✅ 一份 deck 只用一套主色
- ✅ 微圆角 2-4px，卡片稳定感优先

---

## 使用方法

1. 打开 `assets/template-tableai.html`
2. 替换 `<style>` 开头 `:root{}` 中的颜色 token（见下方默认块）
3. 其他 CSS 已经全部走 `var(--paper)` / `var(--ink)` / `var(--accent)`，无需逐处修改
4. 字体链接会自动加载 Manrope + Noto Sans SC，无需额外操作

---

## 默认颜色块（Style C 默认主题：寰宇深蓝 + 日晷暗金）

```css
--paper:#FFFFFF;          /* 主底色：纯白 */
--paper-rgb:255,255,255;
--ink:#0A1626;            /* 文字主色：寰宇深蓝 */
--ink-rgb:10,22,38;
--grey-1:#F5F3F4;         /* 浅灰底（少量使用）*/
--grey-2:#DCD9DB;         /* 中灰分割线 */
--grey-3:#75777D;         /* 暗灰辅助文字 */
--accent:#A88B52;         /* 高亮色：日晷暗金 */
--accent-rgb:168,139,82;
--accent-on:#FFFFFF;      /* accent 上的反色文字 */
--accent-bright:#C9A86B;  /* 暗底高亮：金色提亮版 */
--gold-mist:rgba(168,139,82,0.08); /* 极细金色微光 */

--text-primary:#0A1626;
--text-secondary:#44474C;
--text-helper:#75777D;
--text-placeholder:#A3A3A3;
--text-on-color:#FFFFFF;
--border-subtle:#E4E2E3;  /* 比 Style B 的 #e0e0e0 更偏暖 */
--border-strong:#C5C6CD;
```

---

## 与 Style B 的关键差异

| 维度 | Style B 瑞士 | Style C Table AI |
|------|-------------|------------------|
| 主色 | 克莱因蓝 `#002FA7` | 寰宇深蓝 `#0A1626`（更暗、更接近黑） |
| Accent | IKB 蓝 / 黄 / 绿 / 橙（4 选 1） | 日晷暗金 `#A88B52`（仅 1 套） |
| 底色 | 高级灰白 `#fafaf8`（暖） | 纯白 `#FFFFFF`（冷） |
| 圆角 | 严格直角 0px | **微圆角 2-4px**（卡片稳定感） |
| 字体 | Inter (vw 流式) | Manrope（px 定值，详见 typography） |
| 灰阶层级 | 3 阶灰 | 5 阶灰（surface container 系） |
| 数据大屏标准 | Inter `font-weight:200` | Manrope `font-weight:700/600` |
| 装饰阴影 | 严禁 | 严禁（保留斯堪的纳维亚极简） |
| 渐变 | 严禁 | 严禁 |

---

## 字体系统（typography · 来自 design.md）

Style C 默认加载 `Manrope`（拉丁）+ `Noto Sans SC`（中文）。所有 Manrope 字号走 **px 定值**，不是 vw 流式——这是与 Style B 最大的版式差异。

| Token | 字号 | 字重 | 行高 | letter-spacing | 用途 |
|-------|------|------|------|----------------|------|
| `headline-xl` | 40px | 700 | 1.2 | -0.02em | 副标题 / 章内大标题 |
| `headline-lg` | 32px | 600 | 1.25 | 默认 | 大标题兜底 |
| `headline-md` | 24px | 600 | 1.3 | 默认 | 小节标题 |
| `body-lg` | 18px | 400 | 1.6 | 默认 | 引子段落 |
| `body-md` | 16px | 400 | 1.6 | 默认 | 正文主块 |
| `label-sm` | 12px | 600 | 1 | 0.05em（caps） | kicker / chrome |

> 💡 **请勿直接把 Style B 的 `var(--sans)` 重命名成 Manrope**。Style C 是 fork，不是替换。template-tableai.html 顶部已经单独引入 `Manrope:wght@400;500;600;700;800`，并通过新的 `--sans-tab` token 注入。

---

## 间距系统（spacing · 来自 design.md）

**8px 基线对齐**（与 Style B 共享 Carbon 2x Grid 模数）：

| Token | 值 | 用途 |
|-------|----|------|
| `xs` | 4px | 极小间距 |
| `sm` | 8px | 卡片内图与文 |
| `md` | 16px | 段落间距 / 卡片 padding |
| `lg` | 24px | 节内分隔 |
| `xl` | 40px | 节间分隔 |
| `xxl` | 80px | 页面边距 |

`template-tableai.html` 在 `:root{}` 里已经映射成 `--sp-3` 到 `--sp-12`（继承 Style B 命名）。

---

## 组件状态（component-states · 来自 design.md）

| 状态 | 视觉 |
|------|------|
| Default | 深蓝边框或文字，背景纯白 |
| Hover | 文字 / 边框深度微调，或出现极细暗金装饰线 |
| Active | 边框切换为日晷暗金，或背景出现 5-10% 不透明度的金色微光 |
| Loading | 极简深蓝骨架屏，避免复杂动画 |

template-tableai.html 通过 `.gold-mist` 类 + `hover` 伪类实现 hover/active 的暗金微光。

---

## 圆角策略

**微圆角 = 2-4px**。与 Style B 严格直角的差异如下：

| 元素 | Style B | Style C |
|------|---------|---------|
| 卡片 fill | 0px | `border-radius:4px` |
| 按钮 / 标签 | 0px | `border-radius:2px` |
| 数据 stat-card | 0px | `border-radius:3px` |
| 图片 frame | 0px | 0px（保留瑞士风硬度） |
| 分隔线 / hairline | 0px | 0px |
| Badge / chip | 0px | `border-radius:9999px`（pill） |
| 横条 chart | 0px | `border-radius:2px`（首尾） |

> 卡片微圆让数据 / UI 元素更"产品级"，但图像主视觉仍保持直角——视觉重量不丢。

---

## 推荐选择参考

| 如果是... | 推荐主题 |
|-----------|----------|
| 不知道选啥 / AI 产品 / 数据产品 / SaaS | Style C 默认（寰宇深蓝 + 日晷暗金） |
| 内容是 dashboard / 财务 / KPI | Style C 默认 |
| 用户提供了 Table AI 品牌物料 | Style C 默认 |
| 想要"瑞士风"但不是 Table AI | Style B（IKB 黄绿橙） |
| 想要"杂志感"叙事 | Style A |

---

## ❌ 不要做的事

- ❌ 不允许把 `--accent` 从金色改成蓝/绿/红
- ❌ 不允许把 `--ink` 从 `#0A1626` 改成纯黑 `#000000`——深蓝是品牌灵魂
- ❌ 不允许用户在 Table AI 风格里要求"和瑞士风混搭"
- ❌ 不允许把 `--paper` 从 `#FFFFFF` 改成 cream / 暖灰——斯堪的纳维亚极简要求纯白
- ❌ 不允许在卡片上加 `box-shadow`（设计哲学明确禁止阴影）
- ❌ 不允许给 component 加渐变
- ❌ 不允许脱离 Manrope 改用其他西文字体

---

## 切换原则

Style C 主题只支持**一套**（寰宇深蓝 + 日晷暗金）。如需要多 accent，请回到 Style B 的 4 套体系。

`currentColor` 驱动的 border / icon 会自动适配深蓝底 / 白底，无需额外调整。
