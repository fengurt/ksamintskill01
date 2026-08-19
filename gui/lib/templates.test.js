import assert from "node:assert/strict";
import { resolveStep } from "./templates.js";

const step = resolveStep("audit-html", { workAbs: "/tmp/run", htmlAbs: null });
assert.deepEqual(step.args.slice(-2), ["--dump-slides", "/tmp/run/slides.json"]);
assert.equal(step.args[step.args.indexOf("--html") + 1], "/tmp/run/slides/deck.html");
