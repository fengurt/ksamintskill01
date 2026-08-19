import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join } from "node:path";
import { assemblePackZipStage, buildPackReviewMd, packZipName, slidesZipName, skillZipName, assembleSkillZipStage } from "./archive.js";
import { REPO_ROOT } from "./paths.js";

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
assert.match(md, /original\/doc\.md/);
assert.match(md, /pages\/\*\.md` 1/);
assert.match(md, /hard \*\*0\*\*/);
assert.match(md, /可交给开发/);
writeFileSync(join(dir, "book.md"), "# book\n");
writeFileSync(join(dir, "audit.md"), "# audit\n");
writeFileSync(join(dir, "MANIFEST.md"), "# manifest\n");
const packed = assemblePackZipStage(dir, { source: join(dir, "book.md") });
try {
  assert.ok(existsSync(join(packed.stage, "README.md")));
  assert.ok(existsSync(join(packed.stage, "MANIFEST.md")));
  assert.equal(readFileSync(join(packed.stage, "WORK-MANIFEST.md"), "utf8"), "# manifest\n");
  assert.match(readFileSync(join(packed.stage, "MANIFEST.md"), "utf8"), /`pages\/`/);
  assert.match(readFileSync(join(packed.stage, "MANIFEST.md"), "utf8"), /`WORK-MANIFEST\.md`/);
  assert.ok(existsSync(join(packed.stage, "original", "book.md")));
  assert.ok(existsSync(join(packed.stage, "pages", "p-0001.md")));
  assert.ok(existsSync(join(packed.stage, "pages", "deck.json")));
  assert.ok(existsSync(join(packed.stage, "audit", "REVIEW.md")));
  assert.ok(existsSync(join(packed.stage, "audit", "audit.md")));
  assert.equal(existsSync(join(packed.stage, "source.md")), false);
  assert.equal(existsSync(join(packed.stage, "REVIEW.md")), false);
} finally {
  packed.cleanup();
}

const empty = mkdtempSync(join(tmpdir(), "ksamint-empty-pack-"));
try {
  assert.throws(() => assemblePackZipStage(empty), /pack empty/);
} finally {
  rmSync(empty, { recursive: true, force: true });
}

assert.equal(skillZipName("mdpages2htmlslides"), "mdpages2htmlslides-skill.zip");
const staged = assembleSkillZipStage({
  path: "skills/mdpages2htmlslides",
  folder: "mdpages2htmlslides",
  name: "mdpages2htmlslides",
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

mkdirSync(join(REPO_ROOT, "vendor"), { recursive: true });
const source = mkdtempSync(join(REPO_ROOT, "vendor", "archive-test-"));
const sourceId = basename(source);
mkdirSync(join(source, "skills", "example"), { recursive: true });
writeFileSync(join(source, "LICENSE"), "upstream license\n");
writeFileSync(join(source, "skills", "example", "SKILL.md"), "# Example\n");
const vendored = assembleSkillZipStage({
  path: `vendor/${sourceId}/skills/example`,
  folder: `${sourceId}/skills/example`,
  name: "example",
  sourceId,
});
try {
  assert.equal(readFileSync(join(vendored.stage, "example", "LICENSE"), "utf8"), "upstream license\n");
} finally {
  vendored.cleanup();
  rmSync(source, { recursive: true, force: true });
}
console.log("archive.test.js ok");
