import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { discoverHistoryProjects } from "./projects.js";

test("discovers one canonical Baslide report and its existing PDF", () => {
  const base = mkdtempSync(join(tmpdir(), "baslide-history-test-"));
  const first = join(base, "first");
  const second = join(base, "second");
  try {
    for (const root of [first, second]) {
      mkdirSync(join(root, "decks/example"), { recursive: true });
      writeFileSync(join(root, "decks/example/presentation.html"), "<title>Example report</title>");
    }
    mkdirSync(join(first, "export/pdf"), { recursive: true });
    writeFileSync(join(first, "export/pdf/example.pdf"), "%PDF-1.4\n");
    const projects = discoverHistoryProjects([first, second]);
    assert.equal(projects.length, 1);
    assert.equal(projects[0].name, "Example report");
    assert.equal(projects[0].history, true);
    assert.match(projects[0].pdf, /example\.pdf$/);
  } finally {
    rmSync(base, { recursive: true, force: true });
  }
});
