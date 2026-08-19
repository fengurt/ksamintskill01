import { existsSync, readFileSync } from "node:fs";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { join } from "node:path";
import { REPO_ROOT } from "./paths.js";
import { remoteHead } from "./repo.js";

const execFileAsync = promisify(execFile);

/** Minimal YAML subset parser for registry/sources.yaml (list of maps). */
export function loadSources() {
  const path = join(REPO_ROOT, "registry/sources.yaml");
  if (!existsSync(path)) return [];
  const text = readFileSync(path, "utf8");
  const sources = [];
  let cur = null;
  for (const raw of text.split("\n")) {
    const line = raw.replace(/\t/g, "  ");
    if (/^\s*#/.test(line) || !line.trim()) continue;
    const item = line.match(/^\s*-\s+id:\s*(.+)\s*$/);
    if (item) {
      if (cur) sources.push(cur);
      cur = { id: strip(item[1]), exclude_paths: [] };
      continue;
    }
    if (!cur) continue;
    const kv = line.match(/^\s{2,}([a-z_]+):\s*(.*)$/);
    if (kv) {
      const key = kv[1];
      let val = strip(kv[2]);
      if (key === "exclude_paths") {
        cur.exclude_paths = [];
        continue;
      }
      if (val === "" || val === "|" || val === ">") continue;
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      if (key === "depth") cur[key] = Number(val) || 1;
      else cur[key] = val;
      continue;
    }
    const listItem = line.match(/^\s{4,}-\s+(.+)\s*$/);
    if (listItem && Array.isArray(cur.exclude_paths)) {
      cur.exclude_paths.push(strip(listItem[1]));
    }
  }
  if (cur) sources.push(cur);
  return sources;
}

function strip(s) {
  return String(s || "").trim();
}

export async function registryStatus() {
  const sources = loadSources();
  const rows = [];
  for (const s of sources) {
    const vendorPath = join(REPO_ROOT, "vendor", s.id);
    const present = existsSync(vendorPath);
    let head = null;
    if (present && s.kind === "git") {
      try {
        const { stdout } = await execFileAsync("git", ["-C", vendorPath, "rev-parse", "HEAD"], {
          maxBuffer: 1024 * 1024,
        });
        head = stdout.trim();
      } catch {
        head = null;
      }
    }
    const pinned = s.synced_commit || null;
    rows.push({
      id: s.id,
      kind: s.kind || "git",
      url: s.url || null,
      path: s.path || null,
      pin: s.pin || null,
      synced_commit: pinned,
      vendor_head: head,
      present,
      match: pinned && head ? pinned === head || head.startsWith(pinned.slice(0, 7)) : null,
      notes: s.notes || null,
    });
  }
  return { sources: rows };
}

export async function checkUpstreamDrift(sourceId) {
  const sources = loadSources();
  const s = sources.find((x) => x.id === sourceId);
  if (!s) throw new Error(`unknown source: ${sourceId}`);
  if (s.kind !== "git" || !s.url) throw new Error(`source ${sourceId} is not a git remote`);
  const vendorPath = join(REPO_ROOT, "vendor", s.id);
  if (!existsSync(vendorPath)) throw new Error(`vendor/${s.id} missing — run sync-vendor first`);
  const remote = await remoteHead(vendorPath, "origin", s.pin || "HEAD");
  let local = null;
  try {
    const { stdout } = await execFileAsync("git", ["-C", vendorPath, "rev-parse", "HEAD"]);
    local = stdout.trim();
  } catch {
    /* */
  }
  return {
    id: s.id,
    local,
    remote: remote.hash || null,
    synced_commit: s.synced_commit || null,
    drifted: remote.hash && local ? !remote.hash.startsWith(local.slice(0, 7)) && remote.hash !== local : null,
    error: remote.error || null,
  };
}
