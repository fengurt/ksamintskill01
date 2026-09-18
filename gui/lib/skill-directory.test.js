import assert from "node:assert/strict";
import { loadSkillDirectory } from "./skill-directory.js";
import { listSkills, loadSkillAliases, getSkillDetail, searchSkills } from "./skills.js";
import { qualityReviewHtml } from "../public/views/skill-detail.js";

const rows = Object.values(loadSkillDirectory());
assert.equal(rows.length, 68);
assert.equal(rows.filter((r) => r.commandId.startsWith("k")).length, 33);
assert.equal(new Set(rows.map((r) => r.commandId)).size, 68);
assert.equal(new Set(rows.map((r) => r.command)).size, 68);
const { authored, vendored } = await listSkills();
assert.ok(authored.every((s) => s.commandId && s.qualityReview.current));
const matt = vendored.filter((s) => s.sourceId === "mattpocock-skills");
if (matt.length) {
  assert.equal(matt.length, 35);
  assert.ok(matt.every((s) => s.commandId && s.qualityReview.current));
}
assert.equal(loadSkillAliases().orche, "orchestrate-development");
assert.equal((await getSkillDetail("authored", "k023")).name, "orchestrate-development");
assert.ok((await searchSkills("k023")).some((s) => s.name === "orchestrate-development"));
assert.match(qualityReviewHtml({qualityReview:{...rows[0], current:false}}), /Review outdated/);
assert.match(qualityReviewHtml({qualityReview:{...rows[0], quality:"<script>bad</script>",current:true}}), /&lt;script&gt;/);
