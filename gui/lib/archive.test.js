import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { buildPackReviewMd, packZipName, slidesZipName, skillZipName, assembleSkillZipStage } from "./archive.js";

assert.equal(packZipName("yun1980"), "yun1980-pack.zip");
assert.equal(slidesZipName("yun1980"), "yun1980-slides-review.zip");
assert.equal(slidesZipName("a/../x y"), "a_.._x_y-slides-review.zip");

const dir = mkdtempSync(join(tmpdir(), "ksamint-review-"));
mkdirSync(join(dir, "pages"));
writeFileSync(join(dir, "pages", "p-0001.md"), "# p\n");
writeFileSync(
  join(dir, "index.json"),
  JSON.stringify({ total_units: 3, source: "/tmp/doc.md" })
);
writeFileSync(join(dir, "deck.json"), JSON.stringify({ pages: [{ id: "p-0001" }] }));
writeFileSync(
  join(dir, "audit-source.json"),
  JSON.stringify({ counts: { hard: 0, warn: 1 }, findings: [] })
);
const md = buildPackReviewMd(dir, "/repo/fixtures/local/doc.md");
assert.match(md, /source\.md/);
assert.match(md, /pages\/\*\.md` 1/);
assert.match(md, /hard \*\*0\*\*/);
assert.match(md, /可交给开发/);

assert.equal(skillZipName("md-to-html-slides"), "md-to-html-slides-skill.zip");
const staged = assembleSkillZipStage({
  path: "skills/md-to-html-slides",
  folder: "md-to-html-slides",
  name: "md-to-html-slides",
});
try {
  const root = join(staged.stage, staged.rootName);
  assert.ok(existsSync(join(root, "SKILL.md")));
  assert.ok(existsSync(join(root, "samples/fill-viz/pareto.md")));
  assert.ok(existsSync(join(root, "runtime/prompts/loop/brand.md")));
  assert.ok(existsSync(join(root, "runtime/templates/TIANSIGHT/TIANSIGHT-v2.css")));
  assert.ok(existsSync(join(root, "runtime/scripts/build-TIANSIGHT-deck.py")));
  assert.ok(existsSync(join(root, "RUNTIME.md")));
} finally {
  staged.cleanup();
}
console.log("archive.test.js ok");
