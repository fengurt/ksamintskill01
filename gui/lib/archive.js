import { existsSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import { basename, join } from "node:path";
import { safeWorkDir } from "./paths.js";

const ZIP_ENTRIES = [
  "MANIFEST.md",
  "pack.json",
  "slide-plan.json",
  "deck.json",
  "pages",
  "outline.md",
  "index.json",
  "index.md",
  "units.json",
  "anchors.json",
  "audit-source.json",
  "audit.md",
  "fit-report.json",
];

export function packZipName(runId) {
  return `${String(runId).replace(/[^a-zA-Z0-9._-]/g, "_")}-pack.zip`;
}

export function streamPackZip(runId, res) {
  if (spawnSync("zip", ["-v"], { stdio: "ignore" }).error) {
    throw new Error("zip command not found");
  }
  const abs = safeWorkDir(runId);
  const entries = ZIP_ENTRIES.filter((e) => existsSync(join(abs, e)));
  if (!entries.length) {
    throw new Error("pack empty");
  }
  const name = packZipName(basename(abs));
  res.writeHead(200, {
    "content-type": "application/zip",
    "content-disposition": `attachment; filename="${name}"`,
    "cache-control": "no-store",
  });
  const child = spawn("zip", ["-r", "-q", "-", ...entries], { cwd: abs });
  child.stdout.pipe(res);
  child.stderr.on("data", () => {});
  child.on("error", (err) => {
    if (!res.writableEnded) {
      if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: err.message }));
    }
  });
}
