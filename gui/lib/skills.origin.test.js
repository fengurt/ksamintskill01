import assert from "node:assert/strict";
import { skillAgent, skillOrigin } from "./skills.js";

assert.equal(skillOrigin({ kind: "authored" }), "ksamint");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "agents-skills-local" }), "matt");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "cursor-skills-cursor" }), "system");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "anthropics-skills" }), "system");
assert.equal(skillOrigin({ kind: "vendored", sourceId: "composio-awesome-claude-skills" }), "other");
assert.equal(skillAgent({ sourceId: "cc-switch-skills" }), "cc");
assert.equal(skillAgent({ sourceId: "cursor-public-plugins" }), "cursor");
console.log("skills.origin.test.js ok");
