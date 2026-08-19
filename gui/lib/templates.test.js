import assert from "node:assert/strict";
import { resolveStep } from "./templates.js";
import { baslideSummary } from "./themes.js";

const step = resolveStep("audit-html", { workAbs: "/tmp/run", htmlAbs: null });
assert.deepEqual(step.args.slice(-2), ["--dump-slides", "/tmp/run/slides.json"]);
assert.equal(step.args[step.args.indexOf("--html") + 1], "/tmp/run/slides/deck.html");

assert.deepEqual(
  (({ skins, genres, shells, jobs, fills }) => ({ skins, genres, shells, jobs, fills }))(baslideSummary()),
  { skins: 5, genres: 5, shells: 4, jobs: 12, fills: 16 }
);
