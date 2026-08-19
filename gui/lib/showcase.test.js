import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { assembleBrandSubskillStage, getShowcasePreset, loadShowcase, readShowcaseAsset, saveShowcasePreset, validateBrandSubskillInput } from "./showcase.js";

const temp = mkdtempSync(join(tmpdir(), "showcase-test-"));
const skill = join(temp, "skill");
mkdirSync(join(skill, "showcase", "samples"), { recursive: true });
writeFileSync(join(skill, "showcase", "demo.html"), "<h1>demo</h1>");
writeFileSync(join(skill, "showcase", "samples", "input.md"), "# Input\n");
writeFileSync(
  join(skill, "showcase", "showcase.json"),
  JSON.stringify({ version: 1, demo: { html: "demo.html" }, samples: [{ file: "samples/input.md" }] })
);
try {
  assert.equal(loadShowcase(skill, null), null);
  let showcase = loadShowcase(skill, "showcase/showcase.json");
  assert.equal(showcase.version, 1);
  assert.equal(readShowcaseAsset(skill, showcase, "demo.html").text, "<h1>demo</h1>");
  assert.throws(() => readShowcaseAsset(skill, showcase, "../secret.txt"), /not declared/);

  writeFileSync(join(skill, "showcase", "showcase.json"), JSON.stringify({
    version: 1,
    demo: { html: "demo.html" },
    controls: { theme: ["TIANSIGHT", "swiss"], logo: ["none", "compact"] },
  }));
  showcase = loadShowcase(skill, "showcase/showcase.json");
  const key = `test/${Date.now()}`;
  const saved = saveShowcasePreset(key, { theme: "swiss", logo: "compact", tokens: { accent: "#123456" } }, showcase);
  assert.equal(saved.theme, "swiss");
  assert.equal(getShowcasePreset(key).tokens.accent, "#123456");
  assert.throws(() => saveShowcasePreset(key, { theme: "unknown" }, showcase), /invalid theme/);

  writeFileSync(join(temp, "outside.md"), "outside");
  writeFileSync(join(skill, "showcase", "showcase.json"), JSON.stringify({ version: 1, samples: [{ file: "../../outside.md" }] }));
  assert.throws(() => loadShowcase(skill, "showcase/showcase.json"), /path denied/);

  writeFileSync(join(skill, "showcase", "too-big.md"), Buffer.alloc(2 * 1024 * 1024 + 1));
  writeFileSync(join(skill, "showcase", "showcase.json"), JSON.stringify({ version: 1, samples: [{ file: "too-big.md" }] }));
  assert.throws(() => loadShowcase(skill, "showcase/showcase.json"), /too large/);
} finally {
  rmSync(temp, { recursive: true, force: true });
}

assert.throws(() => validateBrandSubskillInput({}), /brand name/);
assert.throws(
  () => validateBrandSubskillInput({ brandName: "Brand", skillId: "Bad Name", sourceUrl: "https://apuch.art/brand" }),
  /skill id/
);
assert.throws(
  () => validateBrandSubskillInput({ brandName: "Brand", skillId: "brand-gf4p2slides", sourceUrl: "file:///tmp/guide" }),
  /http or https/
);
assert.throws(
  () => validateBrandSubskillInput({ brandName: "Brand", skillId: "brand-gf4p2slides", sourceUrl: "https://apuch.art/brand", logoDataUrl: "data:image/svg+xml;base64,PHN2Zz4=" }),
  /PNG, JPEG, or WebP/
);

const generated = assembleBrandSubskillStage({
  brandName: "North Harbor",
  skillId: "north-harbor-gf4p2slides",
  sourceUrl: "https://apuch.art/north-harbor",
  sourceDate: "2026-08-19",
  tokens: { accent: "#135f7a" },
  logoDataUrl: "data:image/png;base64,iVBORw0KGgo=",
});
try {
  assert.ok(existsSync(join(generated.root, "SKILL.md")));
  assert.ok(existsSync(join(generated.root, "agents", "openai.yaml")));
  assert.ok(existsSync(join(generated.root, "assets", "theme.css")));
  assert.ok(existsSync(join(generated.root, "assets", "logo.png")));
  assert.ok(existsSync(join(generated.root, "references", "brand-guide.md")));
  assert.match(readFileSync(join(generated.root, "SKILL.md"), "utf8"), /metadata:\n  author: ksamint/);
  assert.match(readFileSync(join(generated.root, "assets", "theme.css"), "utf8"), /--gf-accent: #135f7a/);
} finally {
  const stage = generated.stage;
  generated.cleanup();
  assert.equal(existsSync(stage), false);
}
console.log("showcase.test.js ok");
