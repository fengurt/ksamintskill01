import { readFileSync } from "node:fs";
import { join } from "node:path";
import { REPO_ROOT } from "./paths.js";

export function loadSkillDirectory() {
  const rows = ["reviews-authored.json", "reviews-mattpocock.json"].flatMap((file) =>
    JSON.parse(readFileSync(join(REPO_ROOT, "registry", file), "utf8"))
  );
  const keys = new Map();
  const labels = new Set();
  for (const row of rows) {
    if (!/^[km]\d{3}$/.test(row.commandId) || !/^[a-z][a-z0-9-]*$/.test(row.command)) throw new Error("Invalid skill command identifier");
    for (const key of [row.name, row.commandId, row.command]) {
      const previous = keys.get(key.toLowerCase());
      if (previous && previous !== row) throw new Error(`Duplicate skill identifier: ${key}`);
      keys.set(key.toLowerCase(), row);
    }
    const label = row.shortName.toLowerCase();
    if (labels.has(label)) throw new Error(`Duplicate short name: ${row.shortName}`);
    labels.add(label);
    if (!["keep", "improve", "merge-candidate", "retire-candidate"].includes(row.recommendation) || !row.purpose || !row.quality || !row.evidence?.length || !/^[a-f0-9]{64}$/.test(row.reviewedHash)) throw new Error(`Incomplete skill review: ${row.name}`);
  }
  return Object.fromEntries(rows.map((row) => [row.name, row]));
}
