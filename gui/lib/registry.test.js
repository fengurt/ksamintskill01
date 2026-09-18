import assert from "node:assert/strict";
import { join } from "node:path";
import { loadSources } from "./registry.js";
import { VENDOR_ROOT, relToWorkspace, resolveWorkspacePath } from "./paths.js";
import { listSkills, getSkillDetail } from "./skills.js";

assert.ok(loadSources().some((s) => s.id === "mattpocock-skills"));
const path = join(VENDOR_ROOT, "mattpocock-skills", "example", "SKILL.md");
assert.equal(resolveWorkspacePath(relToWorkspace(path)), path);
const { items } = await listSkills();
assert.ok(items.some((s) => s.name === "self-hosted-github-runner"));
assert.ok((await getSkillDetail("authored", "self-hosted-github-runner")).raw);
