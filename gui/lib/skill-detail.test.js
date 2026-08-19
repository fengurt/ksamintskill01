import assert from "node:assert/strict";
import { GF_THEME_DEFAULTS } from "./showcase.js";
import { labDocument, labWarnings, parseLabMarkdown, sandboxDocument } from "../public/views/skill-detail.js";

const valid = `# Fewer handoffs improve delivery confidence

> One owner keeps the decision visible.

- 17 reviews
- 4 decisions
- 2 gates

| Option | Reviews |
|---|---:|
| Named owner | 2 |
| Shared queue | 4 |

Source: GF fictional sample.`;
const parsed = parseLabMarkdown(valid);
assert.equal(parsed.title, "Fewer handoffs improve delivery confidence");
assert.equal(parsed.table.length, 2);
assert.equal(parsed.source, "GF fictional sample.");

const templates = ["cover", "toc", "chapter", "readme", "statement", "verdict", "kpi", "roster", "chart", "chart-table", "matrix", "compare"];
for (const template of templates) {
  const html = labDocument(parsed, template, GF_THEME_DEFAULTS);
  assert.match(html, /class="slide"/);
  assert.match(html, new RegExp(parsed.title));
}
assert.deepEqual(labWarnings(parseLabMarkdown(""), "cover"), [
  "Add Markdown to render a layout smoke test.",
  "Add one level-one heading for the slide title.",
]);
assert.ok(labWarnings(parseLabMarkdown("# Title\n\n| Bad | table |"), "matrix").some((warning) => warning.includes("separator")));
assert.ok(labWarnings(parseLabMarkdown("# Title\n\n- text only"), "chart").some((warning) => warning.includes("numeric")));
assert.ok(labWarnings(parseLabMarkdown("# Title\n" + "x".repeat(2300)), "cover").some((warning) => warning.includes("overflow")));
const controlled = sandboxDocument(
  '<html><head></head><body><div class="recipe"><svg></svg><span>sankey</span></div></body></html>',
  "",
  "",
  "none",
  { template: "chart", layout: "split-2", pack: "tight", visualization: "sankey" }
);
assert.match(controlled, /chart · split-2 · tight · sankey/);
assert.match(controlled, /data-viz="sankey"/);
assert.match(controlled, /padding:4\.5%/);
console.log("skill-detail.test.js ok");
