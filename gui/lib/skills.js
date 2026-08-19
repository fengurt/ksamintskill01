import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { REPO_ROOT } from "./paths.js";
import { pathVersion } from "./repo.js";
import { loadSources } from "./registry.js";
import { skillRuntimeExtras, skillZipName } from "./archive.js";

const FRONTMATTER_RE = /^---\s*\n([\s\S]*?)\n---\s*\n/;

function parseFrontmatter(text) {
  const m = text.match(FRONTMATTER_RE);
  const meta = {};
  if (!m) return { meta, body: text };
  for (const line of m[1].split("\n")) {
    if (!line.includes(":")) continue;
    const i = line.indexOf(":");
    const k = line.slice(0, i).trim();
    const v = line.slice(i + 1).trim().replace(/^["']|["']$/g, "");
    meta[k] = v;
  }
  return { meta, body: text.slice(m[0].length) };
}

function licenseHint(dir) {
  for (const cand of ["LICENSE", "LICENSE.txt", "LICENSE.md", "NOTICE"]) {
    if (existsSync(join(dir, cand))) return cand;
  }
  return null;
}

export function loadInstallMap() {
  const path = join(REPO_ROOT, "scripts/install-map.txt");
  const map = {};
  if (!existsSync(path)) return map;
  for (const line of readFileSync(path, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const [name, targets] = t.split(/\t+/);
    if (!name) continue;
    map[name] = (targets || "").split(",").map((s) => s.trim()).filter(Boolean);
  }
  return map;
}

function walkSkillMd(root, maxDepth = 8) {
  const found = [];
  if (!existsSync(root)) return found;
  function walk(dir, depth) {
    if (depth > maxDepth) return;
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const ent of entries) {
      if (ent.name === "node_modules" || ent.name === ".git" || ent.name === "__pycache__") continue;
      const p = join(dir, ent.name);
      let isDir = ent.isDirectory();
      if (ent.isSymbolicLink()) {
        try {
          isDir = statSync(p).isDirectory();
        } catch {
          continue;
        }
      }
      if (isDir) walk(p, depth + 1);
      else if (ent.name === "SKILL.md") found.push(p);
    }
  }
  walk(root, 0);
  return found;
}

function fileTree(dir, depth = 0, maxDepth = 3) {
  if (depth > maxDepth || !existsSync(dir)) return [];
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return [];
  }
  const out = [];
  for (const ent of entries) {
    if (ent.name.startsWith(".") || ent.name === "node_modules" || ent.name === "__pycache__") continue;
    const p = join(dir, ent.name);
    if (ent.isDirectory()) {
      out.push({ name: ent.name, type: "dir", children: fileTree(p, depth + 1, maxDepth) });
    } else {
      let size = 0;
      try {
        size = statSync(p).size;
      } catch {
        /* */
      }
      out.push({ name: ent.name, type: "file", size });
    }
  }
  return out.sort((a, b) => {
    if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
    return a.name.localeCompare(b.name);
  });
}

function vendorSourceFor(skillMdPath, sources) {
  const rel = relative(join(REPO_ROOT, "vendor"), skillMdPath);
  if (rel.startsWith("..")) return null;
  const top = rel.split(sep)[0];
  const src = sources.find((s) => s.id === top);
  return src || { id: top };
}

/** ksamint = this repo. matt = ~/.agents (Matt Pocock). system = Cursor/CC shipped. */
export const ORIGIN_RANK = { ksamint: 0, matt: 1, other: 2, system: 3 };

const SYSTEM_SOURCES = new Set([
  "cursor-skills-cursor",
  "cursor-public-plugins",
  "cc-switch-skills",
  "anthropics-skills",
]);

export function skillOrigin(skill) {
  if (skill.kind === "authored") return "ksamint";
  const id = skill.sourceId || skill.source || "";
  if (id === "agents-skills-local") return "matt";
  if (SYSTEM_SOURCES.has(id)) return "system";
  return "other";
}

export function skillAgent(skill) {
  const id = skill.sourceId || "";
  if (id === "cursor-skills-cursor" || id === "cursor-public-plugins") return "cursor";
  if (id === "cc-switch-skills" || id === "anthropics-skills") return "cc";
  return "";
}

function withOrigin(skill) {
  const origin = skillOrigin(skill);
  return { ...skill, origin, agent: skillAgent(skill) };
}

export async function listSkills({ includeVendored = true } = {}) {
  const installMap = loadInstallMap();
  const sources = loadSources();
  const authored = [];
  const vendored = [];

  for (const skillMd of walkSkillMd(join(REPO_ROOT, "skills"), 4)) {
    const dir = join(skillMd, "..");
    const text = readFileSync(skillMd, "utf8");
    const { meta } = parseFrontmatter(text);
    const folder = relative(join(REPO_ROOT, "skills"), dir).split(sep)[0];
    const name = meta.name || folder;
    const ver = await pathVersion(`skills/${folder}`);
    authored.push({
      name,
      folder,
      kind: "authored",
      source: "this repo",
      sourceId: null,
      path: relative(REPO_ROOT, dir),
      skillMd: relative(REPO_ROOT, skillMd),
      description: meta.description || "",
      license: licenseHint(dir),
      installTargets: installMap[folder] || installMap[name] || [],
      version: ver,
    });
    authored[authored.length - 1] = withOrigin(authored[authored.length - 1]);
  }

  if (includeVendored) {
    for (const skillMd of walkSkillMd(join(REPO_ROOT, "vendor"), 10)) {
      const dir = join(skillMd, "..");
      let text = "";
      try {
        text = readFileSync(skillMd, "utf8");
      } catch {
        continue;
      }
      const { meta } = parseFrontmatter(text);
      const name = meta.name || relative(join(REPO_ROOT, "vendor"), dir).split(sep).pop();
      const src = vendorSourceFor(skillMd, sources);
      vendored.push({
        name,
        folder: relative(join(REPO_ROOT, "vendor"), dir),
        kind: "vendored",
        source: src?.id || "vendor",
        sourceId: src?.id || null,
        path: relative(REPO_ROOT, dir),
        skillMd: relative(REPO_ROOT, skillMd),
        description: meta.description || "",
        license: licenseHint(dir),
        installTargets: [],
        version: {
          hash: src?.synced_commit?.slice(0, 7) || null,
          date: null,
          subject: src?.synced_commit || null,
          dirty: false,
          synced_commit: src?.synced_commit || null,
        },
      });
      vendored[vendored.length - 1] = withOrigin(vendored[vendored.length - 1]);
    }
  }

  const byOrigin = { ksamint: 0, matt: 0, system: 0, other: 0 };
  for (const s of [...authored, ...vendored]) byOrigin[s.origin] = (byOrigin[s.origin] || 0) + 1;
  return {
    authored,
    vendored,
    totals: { authored: authored.length, vendored: vendored.length, ...byOrigin },
  };
}

export async function getSkillDetail(kind, id) {
  const { authored, vendored } = await listSkills();
  const pool = kind === "vendored" ? vendored : authored;
  const skill =
    pool.find((s) => s.folder === id || s.name === id || s.path === id) ||
    [...authored, ...vendored].find((s) => s.folder === id || s.name === id || s.path === id);
  if (!skill) return null;
  const abs = join(REPO_ROOT, skill.path);
  const skillMdAbs = join(REPO_ROOT, skill.skillMd);
  const text = readFileSync(skillMdAbs, "utf8");
  const { meta, body } = parseFrontmatter(text);
  return {
    ...skill,
    meta,
    body,
    raw: text,
    tree: fileTree(abs),
    zip: `/api/skills/${skill.kind}/${encodeURIComponent(skill.folder)}.zip`,
    zipName: skillZipName(skill.folder),
    runtime: skillRuntimeExtras(skill.folder),
  };
}

export async function skillGraph() {
  const { authored } = await listSkills({ includeVendored: false });
  const names = new Set(authored.map((s) => s.name).concat(authored.map((s) => s.folder)));
  const nodes = authored.map((s) => ({ id: s.folder, name: s.name }));
  const edges = [];
  for (const s of authored) {
    const abs = join(REPO_ROOT, s.skillMd);
    let text = "";
    try {
      text = readFileSync(abs, "utf8");
    } catch {
      continue;
    }
    for (const other of names) {
      if (other === s.name || other === s.folder) continue;
      const re = new RegExp(`\\b${other.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`);
      if (re.test(text)) {
        const target = authored.find((a) => a.name === other || a.folder === other);
        if (target) edges.push({ from: s.folder, to: target.folder });
      }
    }
  }
  // dedupe
  const seen = new Set();
  const uniq = [];
  for (const e of edges) {
    const k = `${e.from}->${e.to}`;
    if (seen.has(k)) continue;
    seen.add(k);
    uniq.push(e);
  }
  return { nodes, edges: uniq };
}

export async function searchSkills(q) {
  const query = String(q || "").trim().toLowerCase();
  if (!query) return [];
  const { authored, vendored } = await listSkills();
  const hits = [];
  for (const s of [...authored, ...vendored]) {
    const abs = join(REPO_ROOT, s.skillMd);
    let text = "";
    try {
      text = readFileSync(abs, "utf8");
    } catch {
      continue;
    }
    const hay = `${s.name}\n${s.description}\n${text}`.toLowerCase();
    if (!hay.includes(query)) continue;
    const idx = hay.indexOf(query);
    const start = Math.max(0, idx - 40);
    const snippet = text.slice(start, start + 120).replace(/\s+/g, " ");
    hits.push({ ...s, snippet });
    if (hits.length >= 80) break;
  }
  return hits;
}
