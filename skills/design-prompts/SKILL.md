---
name: design-prompts
description: Master index of 50+ UI/UX design prompts from 7 curated sources. Use when the user wants to generate a website/UI in a specific design style, needs design inspiration, or wants to apply a design aesthetic to their project. Triggers: "design style", "UI prompt", "website style", "设计风格", "界面设计".
---

# Design Prompts — Master Index

50+ curated AI design prompts from 7 sources. Each prompt is a complete design system spec (colors, typography, components, layout) ready to paste into Claude, ChatGPT, v0.dev, Cursor, or any AI coding tool.

## Quick Reference: All 22 Styles from designprompts.dev

| # | Style | Mode | Description |
|---|-------|------|-------------|
| 1 | **SaaS** | light | Bold modern, Electric Blue gradients, Calistoga+Inter fonts, animated hero |
| 2 | **Monochrome** | light | Black & white editorial, dramatic contrast, no accent colors |
| 3 | **Cyberpunk** | dark | Neon on black, glitch animations, terminal fonts, tech decorations |
| 4 | **Claymorphism** | light | Soft 3D inflatable clay, multi-layered shadows, playful rounded |
| 5 | **Luxury** | light | Elegant serif, gold accents, monochromatic palette, ultra-slow animations |
| 6 | **Kinetic** | dark | Motion-first, typography as visual medium, infinite marquees |
| 7 | **Academia** | dark | University aesthetic, old libraries, warm paper, serifs, gold/crimson |
| 8 | **Maximalism** | dark | MORE IS MORE — clashing patterns, dense layouts, oversaturated colors |
| 9 | **Retro** | light | 90s nostalgia, Windows 95 beveled UI, system fonts, primary colors |
| 10 | **Neumorphism** | light | Extruded/inset elements, dual shadows, soft tactile monochromatic |
| 11 | **Professional** | light | Editorial-minimalist, elegant serif, warm ivory, gold accents |
| 12 | **Industrial** | light | Dieter Rams & Teenage Engineering, high-fidelity industrial skeuomorphism |
| 13 | **Newsprint** | light | Newspaper aesthetic, stark B&W, tight grids, editorial depth |
| 14 | **Web3/Crypto** | dark | Bitcoin DeFi aesthetic, deep void backgrounds, holographic gradients |
| 15 | **Vaporwave** | dark | 80s retro-futurism, neon pink/cyan, chrome, synthwave |
| 16 | **Botanical** | light | Nature-inspired, organic shapes, rounded corners, soft earthy |
| 17 | **Organic** | light | Moss greens + terracotta + sand, organic blob shapes |
| 18 | **Sketch** | light | Wobbly borders, handwritten typography, paper textures, imperfect |
| 19 | **Enterprise** | light | Modern SaaS, indigo/violet gradients, professional but approachable |
| 20 | **Terminal** | dark | CLI aesthetic, monospaced, high contrast, green-on-black, retro-futuristic |
| 21 | **Bauhaus** | light | Bold geometric modernism, circles/squares/triangles, primary colors |
| 22 | **Glassmorphism** | dark | Apple-inspired, rich mesh gradients, premium blur, constrained layouts |

## Available Design Prompt Sources

### 1. DesignPrompts.dev ⭐ Primary
- **URL:** https://www.designprompts.dev/
- **Styles:** 22 extracted (see catalog above)
- **Format:** Complete design system spec with colors, typography, components, layout
- **Best for:** Full-page website generation with AI coding tools
- **Local ref:** `designref/designprompts-dev-catalog.json`

### 2. MotionSites.ai ⭐ Best Overall
- **URL:** https://motionsites.ai/
- **Styles:** Premium hero section prompts, motion-focused
- **Format:** Hero-specific prompts with animation guidance
- **Best for:** Stunning landing page hero sections

### 3. UI Prompt Explorer
- **URL:** https://uiprompt.art/
- **Styles:** UI themes from playful sketch to elegant minimalism
- **Format:** Visual elements + AI prompts, custom prompt generation
- **Best for:** Lovable, Bolt.new, maintaining visual consistency across projects

### 4. HuggingPT UI Prompts
- **URL:** https://huggingpt.com/ui-prompts
- **Styles:** 230+ PC styles + 43 mobile styles
- **Format:** Chinese-language prompts with interactive examples
- **Best for:** Chinese users, mobile design prompts, color/industry filtering

### 5. UIDatabase
- **URL:** https://uidatabase.com/
- **Styles:** Login/Auth, SaaS dashboards, pricing, onboarding, settings, e-commerce
- **Format:** Context-aware prompts with component breakdowns
- **Best for:** Complete page layouts and component-level prompts
- **Pricing:** Free tier + Pro ($9/mo)

### 6. Items.Design
- **URL:** https://items.design/
- **Styles:** Free AI-generated design assets, UI components, page templates
- **Format:** Each asset with complete generation prompt
- **Best for:** Free commercial-use design assets

### 7. PromptBase UI Design
- **URL:** https://promptbase.com/prompts/ui-design
- **Styles:** 1000+ professional-grade prompts, marketplace
- **Format:** Free + paid, rated by users, tool-specific filtering
- **Best for:** Professional, battle-tested prompts

### 8. FlowGPT UI Design
- **URL:** https://flowgpt.com/tags/ui-design
- **Styles:** Community-driven, v0.dev focused
- **Format:** User-shared, rated, tool-specific
- **Best for:** v0.dev, Figma AI integration

## How to Use Design Prompts

1. **Browse** — Visit any source above, find a style you like
2. **Copy** — Click "Get Prompt" or "Copy" button
3. **Paste** — Paste into Claude, ChatGPT, v0.dev, Cursor, or Bolt.new
4. **Customize** — Ask AI to adapt colors, content, or components to your needs

### Example: Using with Claude Code
```
"Generate a landing page in the [STYLE] design style for a [product description].
Use the design system from designprompts.dev's [STYLE] prompt."
```

### Example: Using with v0.dev
```
"Create a SaaS dashboard using the Monochrome design system.
Apply the full typography, color, and component specs."
```

## Prompt Structure (What Each Prompt Contains)

Every prompt from designprompts.dev includes:
- **Role context** — AI as expert frontend engineer + UI/UX designer
- **Color system** — Primary, secondary, accent, background, surface, text
- **Typography** — Font families, sizes, weights, line heights, hierarchy
- **Components** — Button, Card, Input, Navbar specs with `cva` patterns
- **Spacing & Layout** — Grid system, responsive breakpoints, white space
- **Animation** — Motion tokens, transitions, hover states
- **Implementation** — HTML/CSS/Tailwind/React/Next.js guidance

## Backup & Reference

All extracted design prompts and catalogs are backed up at:
```
~/.claude/projects/-Users-af/memory/designref/
```
And pushed to: `https://github.com/fengurt/claudememo01/tree/main/designref`
