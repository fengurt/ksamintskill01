import assert from "node:assert/strict";
import { hasStar, pickCanonical, skillAgent, skillCredit, skillOrigin, sortSkills, starId, unifySkills } from "./skills.js";

assert.equal(skillOrigin({ kind: "authored" }), "ksamint");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "agents-skills-local", declaredOrigin: "ksamint" }), "ksamint");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "mattpocock-skills" }), "mattpocock");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "agents-skills-local" }), "mattpocock");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "cursor-skills-cursor" }), "system");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "anthropics-skills" }), "system");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "composio-awesome-claude-skills" }), "other");
assert.equal(skillAgent({ sourceId: "cc-switch-skills" }), "cc");
assert.equal(skillAgent({ sourceId: "cursor-public-plugins" }), "cursor");
assert.deepEqual(skillCredit({ kind: "authored" }), { author: "ksamint", repo: "fengurt/ksamintskill01" });
assert.deepEqual(
  skillCredit(
    { kind: "vendored", sourceId: "mattpocock-skills", origin: "mattpocock" },
    { url: "https://github.com/mattpocock/skills.git" }
  ),
  { author: "Matt Pocock", repo: "mattpocock/skills" }
);
assert.deepEqual(skillCredit({ kind: "vendored", sourceId: "agents-skills-local" }), { author: "Matt Pocock", repo: "~/.agents/skills" });
assert.deepEqual(
  skillCredit({ kind: "vendored", sourceId: "agents-skills-local", origin: "ksamint", declaredAuthor: "ksamint", declaredRepository: "fengurt/ksamintskill01" }),
  { author: "ksamint", repo: "fengurt/ksamintskill01" }
);
assert.deepEqual(
  skillCredit({ kind: "vendored", sourceId: "obra-superpowers" }, { url: "https://github.com/obra/superpowers.git" }),
  { author: "obra", repo: "obra/superpowers" }
);
const sorted = sortSkills([
  { name: "old", starred: false, updatedAt: 10 },
  { name: "star", starred: true, updatedAt: 1 },
  { name: "new", starred: false, updatedAt: 20 },
]);
assert.deepEqual(
  sorted.map((s) => s.name),
  ["star", "new", "old"]
);
assert.equal(starId("authored/mdpages2htmlslides"), "mdpages2htmlslides");
assert.equal(
  hasStar(new Set(["authored/mdpages2htmlslides"]), {
    name: "mdpages2htmlslides",
    kind: "authored",
    folder: "mdpages2htmlslides",
  }),
  true
);
const authored = {
  name: "brand-guidelines",
  kind: "authored",
  origin: "ksamint",
  path: "skills/brand-guidelines",
  folder: "brand-guidelines",
  source: "this repo",
  updatedAt: 1,
  starred: false,
};
const shipped = {
  name: "brand-guidelines",
  kind: "vendored",
  origin: "system",
  path: "vendor/anthropics-skills/skills/brand-guidelines",
  folder: "anthropics-skills/skills/brand-guidelines",
  source: "anthropics-skills",
  sourceId: "anthropics-skills",
  updatedAt: 9,
  starred: true,
};
assert.equal(pickCanonical(authored, shipped), authored);
const one = unifySkills([shipped, authored]);
assert.equal(one.length, 1);
assert.equal(one[0].path, "skills/brand-guidelines");
assert.equal(one[0].copies.length, 2);
assert.equal(one[0].starred, true);
assert.equal(one[0].zip, "/api/skills/authored/brand-guidelines.zip");
console.log("skills.origin.test.js ok");
