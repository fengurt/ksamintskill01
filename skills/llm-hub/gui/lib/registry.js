// Registry loader. Resolves registry.tsv from REGISTRY_PATH, then ../registry.tsv,
// then ./registry.tsv (Docker copies it next to the app).
import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const APP_DIR = dirname(__dirname); // gui/

export function registryPath() {
  const candidates = [
    process.env.REGISTRY_PATH,
    join(APP_DIR, "..", "registry.tsv"),
    join(APP_DIR, "registry.tsv"),
  ].filter(Boolean);
  return candidates.find((p) => existsSync(p)) || candidates[candidates.length - 1];
}

export async function loadRegistry() {
  const text = await readFile(registryPath(), "utf8");
  const rows = [];
  for (const line of text.split("\n")) {
    if (!line.trim() || line.startsWith("#")) continue;
    const [provider, group, base_url, protocol, op_ref, default_model] = line.split("\t");
    if (!provider) continue;
    rows.push({
      provider, group, base_url, protocol,
      op_ref, default_model: (default_model || "").trim(),
      configured: !!op_ref && op_ref !== "EMPTY",
    });
  }
  return rows;
}

// Public view (no secret references)
export function publicRow(r) {
  const { op_ref, ...rest } = r;
  return rest;
}
