import assert from "node:assert/strict";
import { RESOURCE_GROUPS, renderHome } from "../public/views/home.js";
import { skillGithubUrl, listSkills } from "./skills.js";

const root = { classList: { remove() {} }, innerHTML: "" };
await renderHome(root);
assert.match(root.innerHTML, /Benchmark skill sources/);
assert.match(root.innerHTML, /Latest updates, at the source/);
assert.doesNotMatch(root.innerHTML, /run-sync|Reading workspace|Repository status/);
for (const group of RESOURCE_GROUPS) for (const [, url] of group.items) {
  assert.equal(new URL(url).protocol, "https:");
  assert.ok(root.innerHTML.includes(url));
}
assert.equal(skillGithubUrl({kind:"authored",skillMd:"skills/hello world/SKILL.md"}), "https://github.com/fengurt/ksamintskill01/blob/main/skills/hello%20world/SKILL.md");
const pin = "a".repeat(40);
assert.equal(skillGithubUrl({folder:"matt/skills/engineering/tdd"}, {id:"matt",kind:"git",url:"https://github.com/mattpocock/skills.git",synced_commit:pin}), `https://github.com/mattpocock/skills/blob/${pin}/skills/engineering/tdd/SKILL.md`);
assert.equal(skillGithubUrl({declaredRepository:"javascript:alert(1)"}), null);
assert.equal(skillGithubUrl({declaredRepository:"https://github.com.evil.test/a/b"}), null);
assert.equal(skillGithubUrl({sourceId:"local"}), null);
assert.equal(skillGithubUrl({}, {id:"agents-skills-local",kind:"local"}), "https://github.com/mattpocock/skills");
assert.equal(skillGithubUrl({declaredRepository:"owner/repo"}), "https://github.com/owner/repo");
const { authored } = await listSkills({includeVendored:false});
assert.ok(authored.length);
assert.ok(authored.every((skill) => skill.githubUrl?.endsWith("/SKILL.md")));
