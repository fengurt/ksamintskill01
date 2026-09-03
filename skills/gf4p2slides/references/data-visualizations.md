# Data visualization registry

Choose the data question first. Each recipe has one owning question family so the registry stays MECE, even when a recipe can answer secondary questions.

| Question family | Recipe ids | Expected data shape |
|---|---|---|
| Magnitude | `diverging-bar`, `bubble` | categories with one value; bubble adds x, y, and size |
| Ranking | `pareto`, `slope` | ordered categories; slope compares two points |
| Distribution | `hist-cdf`, `heatmap` | numeric samples or a two-dimensional value grid |
| Change over time | `line-dual`, `calendar` | ordered time series or dated events |
| Part to whole | `treemap`, `funnel`, `waterfall`, `venn` | hierarchy, stages, signed contributions, or sets |
| Flow | `sankey`, `network` | weighted edges or entities and relationships |
| Correlation | `quadrant`, `radar` | paired measures or normalized multivariate profiles |

Spatial data is intentionally unsupported in the first registry. Add maps only with a real geographic use case, projection choice, and accessible fallback.

## Renderer contract

Every visualization renderer must declare:

```text
id
question
input columns and types
required and optional fields
scale and sorting rules
label collision strategy
empty, zero, negative, missing, and overflow behavior
brand tokens consumed
text alternative
table fallback
```

Renderer output must be self-contained SVG or semantic HTML. It must not fetch a chart library, font, or remote image at view time.

## Shared brand tokens

Visualization recipes consume semantic tokens instead of brand-specific color names:

```css
--gf-surface
--gf-ink
--gf-muted
--gf-grid
--gf-accent
--gf-positive
--gf-negative
--gf-warning
--gf-font-body
--gf-font-number
```

Use patterns, labels, or direct annotation when two states would otherwise differ only by color.

## Definition of done per recipe

- One realistic golden input and one rendered output.
- One runnable check for malformed or missing data.
- A stable viewBox and no clipped labels at the target slide size.
- Explicit handling for zero, negative, missing, and long-label cases where relevant.
- A concise text alternative that states the visible pattern.
- A table or raw-data fallback available in HTML and document modes.
- No unexplained axes, dual scales, 3D perspective, or decorative marks.

## Suggested build order

1. `diverging-bar`, `line-dual`, `pareto`, `heatmap`: highest reuse and simplest validation.
2. `waterfall`, `treemap`, `quadrant`, `bubble`: common analytical decisions with moderate layout work.
3. `slope`, `hist-cdf`, `calendar`, `funnel`, `radar`, `venn`: narrower input contracts.
4. `sankey`, `network`: last, because routing and label collision need stronger tests.

Do not add a recipe id for a visual style variant. Brand packs restyle the same recipe; they do not fork the taxonomy.
