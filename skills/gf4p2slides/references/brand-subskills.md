# Brand sub-skills

A brand sub-skill is a thin adapter over `gf4p2slides`. It owns official brand facts and assets. It does not copy the generic page taxonomy or visualization logic.

## Required structure

```text
<brand>-gf4p2slides/
  SKILL.md
  agents/openai.yaml
  assets/
    theme.css
    <official-logo-file>
  references/
    brand-guide.md
```

Use a lowercase hyphenated skill name. Keep the human-facing brand spelling in `agents/openai.yaml`.

## Source resolution

1. Resolve the brand through `https://apuch.art/` and use the latest published guide, tokens, and official assets.
2. If it is absent, ask for or locate an official first-party guide supplied by the user.
3. Record the source URL, version or publication date, and asset provenance in `references/brand-guide.md`.
4. Do not infer missing logo variants, colors, fonts, or voice rules.

## SKILL.md contract

The brand skill should contain only brand-specific decisions and this operative instruction:

```markdown
Call the Skill tool with "gf4p2slides" for page classification, the page-plan interface, output-mode rules, and visualization selection. Then apply this brand pack's official tokens and assets.
```

Its description should trigger only for that brand's slides, HTML presentations, or documents.

## Theme contract

`assets/theme.css` must define the shared semantic tokens:

```css
:root {
  --gf-surface: <official value>;
  --gf-ink: <official value>;
  --gf-muted: <official value>;
  --gf-grid: <derived accessible neutral>;
  --gf-accent: <official value>;
  --gf-positive: <accessible semantic value>;
  --gf-negative: <accessible semantic value>;
  --gf-warning: <accessible semantic value>;
  --gf-font-body: <official stack>;
  --gf-font-number: <official or compatible numeric stack>;
}
```

Add mode-specific layout rules only when the guide requires them. Slides, responsive HTML, and print documents may use different spacing and geometry, but must share the same semantic tokens and source assets.

## Allowed overrides

- Logo placement, clear space, and permitted variants.
- Typography scale within official font rules.
- Color and data-visualization palette.
- Image treatment, icon style, voice, and citation style.
- A page-template override required by a real brand pattern.

## Forbidden duplication

- Do not copy the 12-template registry.
- Do not rename generic page or visualization ids.
- Do not bundle a second renderer.
- Do not add decorative brand rules that are absent from the guide.

Validate the generated skill with the standard skill validator and test at least `cover`, `chart`, `compare`, and `verdict` with realistic content before calling the brand pack ready.
