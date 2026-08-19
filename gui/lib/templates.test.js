import assert from "node:assert/strict";
import { getTemplate, listTemplates, resolveStep } from "./templates.js";
import { baslideSummary } from "./themes.js";
import { startJob } from "./jobs.js";

const step = resolveStep("audit-html", { workAbs: "/tmp/run", htmlAbs: null });
assert.deepEqual(step.args.slice(-2), ["--dump-slides", "/tmp/run/slides.json"]);
assert.equal(step.args[step.args.indexOf("--html") + 1], "/tmp/run/slides/deck.html");
assert.equal(getTemplate("alongslides").id, "long4hslides");
assert.equal(getTemplate("longdoc-to-deck").id, "long4hslides");
assert.equal(getTemplate("baslide-slides").id, "long4hslides-slides");
assert.equal(listTemplates().filter((item) => item.id === "long4hslides").length, 1);
assert.equal(listTemplates().some((item) => item.id === "long4hslides-slides"), false);
assert.equal(resolveStep("segment", { workAbs: "/tmp/run", sourceAbs: "/tmp/source.zip" }).args[1], "/tmp/run/source.md");
await assert.rejects(
  startJob({ templateId: "long4hslides-slides", work: "test-no-approval" }),
  /approve the completed page pack/
);

assert.deepEqual(
  (({ skins, genres, shells, jobs, fills }) => ({ skins, genres, shells, jobs, fills }))(baslideSummary()),
  { skins: 5, genres: 5, shells: 4, jobs: 12, fills: 16 }
);
