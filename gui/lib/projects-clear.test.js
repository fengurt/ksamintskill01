import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const dir = mkdtempSync(join(tmpdir(), "project-clear-"));
process.env.DATA_DIR = join(dir, "data");
process.env.BASLIDE_ROOT = join(dir, "reports");
process.env.ALLOWED_DOC_ROOTS = process.env.BASLIDE_ROOT;
try {
  const report = join(dir, "reports/decks/example/presentation.html");
  mkdirSync(join(dir, "reports/decks/example"), { recursive: true });
  mkdirSync(process.env.DATA_DIR);
  writeFileSync(report, "<title>Keep report</title>");
  writeFileSync(join(process.env.DATA_DIR, "projects.json"), JSON.stringify({ version: 1, projects: [{ id: "prj_test", name: "Saved project" }] }));
  const { listProjects, clearProjects, createProject } = await import("./projects.js");
  assert.equal(listProjects().length, 2);
  const result = clearProjects();
  assert.equal(result.removed, 2);
  assert.deepEqual(listProjects(), []);
  assert.equal(readFileSync(report, "utf8"), "<title>Keep report</title>");
  const backup = JSON.parse(readFileSync(result.backup, "utf8"));
  assert.equal(backup.projects.length, 1);
  assert.equal(backup.visibleProjects.length, 2);
  createProject({name:"New project"});
  assert.equal(listProjects().length, 1);
} finally {
  rmSync(dir, { recursive:true, force:true });
}
