import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { DATA_DIR, REPO_ROOT } from "./paths.js";
import { pathVersion } from "./repo.js";
import { loadSources } from "./registry.js";
import { skillRuntimeExtras, skillZipName } from "./archive.js";
import { loadShowcase, readShowcaseAsset } from "./showcase.js";

const STARS_FILE = join(DATA_DIR, "stars.json");

export function skillKey(skill) {
  return `${skill.kind}/${skill.folder}`;
}

export function skillId(skill) {
  return String(skill.name || skill.folder || "")
    .toLowerCase()
    .trim();
}

export function starId(key) {
  return (
    String(key || "")
      .trim()
      .toLowerCase()
      .split("/")
      .filter(Boolean)
      .pop() || ""
  );
}

export function loadStars() {
  try {
    const data = JSON.parse(readFileSync(STARS_FILE, "utf8"));
    return new Set(data.keys || []);
  } catch {
    return new Set();
  }
}

export function hasStar(stars, skill) {
  const id = skillId(skill);
  if (!id) return false;
  if (stars.has(id) || stars.has(skillKey(skill))) return true;
  for (const k of stars) {
    if (starId(k) === id) return true;
  }
  return false;
}

export function toggleStar(key, on) {
  const id = starId(key);
  if (!id) throw new Error("missing skill key");
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });
  const set = loadStars();
  const has = [...set].some((k) => starId(k) === id);
  const next = on == null ? !has : Boolean(on);
  for (const k of [...set]) {
    if (starId(k) === id) set.delete(k);
  }
  if (next) set.add(id);
  writeFileSync(STARS_FILE, JSON.stringify({ version: 1, keys: [...set] }, null, 2) + "\n");
  return { key: id, starred: next, keys: [...set] };
}

const FRONTMATTER_RE = /^---\s*\n([\s\S]*?)\n---\s*\n/;

function parseFrontmatter(text) {
  const m = text.match(FRONTMATTER_RE);
  const meta = {};
  if (!m) return { meta, body: text };
  let section = null;
  for (const line of m[1].split("\n")) {
    if (!line.includes(":")) continue;
    const i = line.indexOf(":");
    const k = line.slice(0, i).trim();
    const v = line.slice(i + 1).trim().replace(/^["']|["']$/g, "");
    if (!line.startsWith(" ") && !v) {
      section = k;
      meta[k] = {};
      continue;
    }
    if (line.startsWith(" ") && section && typeof meta[section] === "object") meta[section][k] = v;
    else {
      section = null;
      meta[k] = v;
    }
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

/** ksamint = this repo. mattpocock = canonical repo or ~/.agents. system = Cursor/CC shipped. */
export const ORIGIN_RANK = { ksamint: 0, mattpocock: 1, other: 2, system: 3 };

const SYSTEM_SOURCES = new Set([
  "cursor-skills-cursor",
  "cursor-public-plugins",
  "cc-switch-skills",
  "anthropics-skills",
]);

export function skillOrigin(skill) {
  if (["ksamint", "mattpocock", "system", "other"].includes(skill.declaredOrigin)) return skill.declaredOrigin;
  if (skill.kind === "authored") return "ksamint";
  const id = skill.sourceId || skill.source || "";
  if (id === "mattpocock-skills" || id === "agents-skills-local") return "mattpocock";
  if (SYSTEM_SOURCES.has(id)) return "system";
  return "other";
}

export function skillAgent(skill) {
  const id = skill.sourceId || "";
  if (id === "cursor-skills-cursor" || id === "cursor-public-plugins") return "cursor";
  if (id === "cc-switch-skills" || id === "anthropics-skills") return "cc";
  return "";
}

export function skillCredit(skill, src = null) {
  if (skill.declaredAuthor || skill.declaredRepository) {
    return {
      author: skill.declaredAuthor || skill.origin || "vendor",
      repo: skill.declaredRepository || skill.sourceId || skill.source || "vendor",
    };
  }
  if (skill.kind === "authored" || skill.origin === "ksamint") {
    return { author: "ksamint", repo: "fengurt/ksamintskill01" };
  }
  const id = skill.sourceId || "";
  if (id === "mattpocock-skills") return { author: "Matt Pocock", repo: "mattpocock/skills" };
  if (id === "agents-skills-local") return { author: "Matt Pocock", repo: "~/.agents/skills" };
  if (id === "cursor-skills-cursor") return { author: "cursor", repo: "Cursor built-in" };
  if (id === "cursor-public-plugins") return { author: "cursor", repo: "cursor-public plugins" };
  if (id === "cc-switch-skills") return { author: "cc", repo: "~/.cc-switch/skills" };
  const url = src?.url || "";
  const gh = String(url).match(/github\.com\/([^/]+\/[^/.]+)/);
  if (gh) {
    const owner = gh[1].split("/")[0];
    return { author: owner, repo: gh[1] };
  }
  return { author: skill.origin || "vendor", repo: id || skill.source || "vendor" };
}

export function skillUpdatedAt(skillMdAbs, gitDate) {
  if (gitDate) {
    const t = Date.parse(gitDate);
    if (!Number.isNaN(t)) return t;
  }
  try {
    return statSync(skillMdAbs).mtimeMs;
  } catch {
    return 0;
  }
}

export function sortSkills(list) {
  return [...list].sort((a, b) => {
    if (!!b.starred !== !!a.starred) return a.starred ? -1 : 1;
    return (b.updatedAt || 0) - (a.updatedAt || 0);
  });
}

function decorate(skill, src, skillMdAbs, stars) {
  const origin = skillOrigin(skill);
  const credit = skillCredit({ ...skill, origin }, src);
  return {
    ...skill,
    origin,
    agent: skillAgent(skill),
    author: credit.author,
    repo: credit.repo,
    updatedAt: skillUpdatedAt(skillMdAbs, skill.version?.date),
    starred: hasStar(stars, skill),
  };
}

export function pickCanonical(a, b) {
  const ra = ORIGIN_RANK[a.origin] ?? 9;
  const rb = ORIGIN_RANK[b.origin] ?? 9;
  if (ra !== rb) return ra < rb ? a : b;
  return (a.updatedAt || 0) >= (b.updatedAt || 0) ? a : b;
}

export function unifySkills(rows) {
  const map = new Map();
  for (const s of rows) {
    const id = skillId(s);
    if (!id) continue;
    const loc = { path: s.path, source: s.source, sourceId: s.sourceId, kind: s.kind, folder: s.folder };
    const cur = map.get(id);
    if (!cur) {
      map.set(id, { ...s, id, copies: [loc] });
      continue;
    }
    cur.copies.push(loc);
    if (pickCanonical(s, cur) === s) {
      map.set(id, { ...s, id, copies: cur.copies, starred: cur.starred || s.starred });
    } else {
      cur.starred = cur.starred || s.starred;
    }
  }
  return [...map.values()].map((s) => ({
    ...s,
    zip: `/api/skills/${s.kind}/${encodeURIComponent(s.folder)}.zip`,
    zipName: skillZipName(s.folder),
  }));
}

export async function listSkills({ includeVendored = true } = {}) {
  const installMap = loadInstallMap();
  const sources = loadSources();
  const stars = loadStars();
  const authored = [];
  const vendored = [];

  for (const skillMd of walkSkillMd(join(REPO_ROOT, "skills"), 4)) {
    const dir = join(skillMd, "..");
    const text = readFileSync(skillMd, "utf8");
    const { meta } = parseFrontmatter(text);
    const declared = typeof meta.metadata === "object" ? meta.metadata : {};
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
      declaredAuthor: declared.author || meta.author || null,
      declaredOrigin: declared.origin || meta.origin || null,
      declaredRepository: declared.repository || meta.repository || null,
      showcasePath: declared.showcase || meta.showcase || null,
      license: licenseHint(dir),
      installTargets: installMap[folder] || installMap[name] || [],
      version: ver,
    });
    authored[authored.length - 1] = decorate(authored[authored.length - 1], null, skillMd, stars);
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
      const declared = typeof meta.metadata === "object" ? meta.metadata : {};
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
        declaredAuthor: declared.author || meta.author || null,
        declaredOrigin: declared.origin || meta.origin || null,
        declaredRepository: declared.repository || meta.repository || null,
        showcasePath: declared.showcase || meta.showcase || null,
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
      vendored[vendored.length - 1] = decorate(vendored[vendored.length - 1], src, skillMd, stars);
    }
  }

  const items = sortSkills(unifySkills([...authored, ...vendored]));
  const byOrigin = { ksamint: 0, mattpocock: 0, system: 0, other: 0 };
  for (const s of items) byOrigin[s.origin] = (byOrigin[s.origin] || 0) + 1;
  return {
    authored,
    vendored,
    items,
    totals: {
      authored: authored.length,
      vendored: vendored.length,
      copies: authored.length + vendored.length,
      unique: items.length,
      ...byOrigin,
    },
  };
}

export async function getSkillDetail(kind, id) {
  const { items } = await listSkills();
  const needle = String(id || "").toLowerCase();
  const skill = items.find((s) => {
    if (s.id === needle || s.folder === id || s.name === id || s.path === id) return true;
    if (s.kind === kind && (s.folder === id || s.name === id)) return true;
    return (s.copies || []).some(
      (c) => c.folder === id || c.path === id || `${c.kind}/${c.folder}` === `${kind}/${id}`
    );
  });
  if (!skill) return null;
  const abs = join(REPO_ROOT, skill.path);
  const skillMdAbs = join(REPO_ROOT, skill.skillMd);
  const text = readFileSync(skillMdAbs, "utf8");
  const { meta, body } = parseFrontmatter(text);
  const declared = typeof meta.metadata === "object" ? meta.metadata : {};
  let showcase = null;
  let showcaseError = null;
  try {
    showcase = loadShowcase(abs, declared.showcase || meta.showcase || skill.showcasePath);
  } catch (error) {
    showcaseError = error.message;
  }
  return {
    ...skill,
    meta,
    body,
    raw: text,
    showcase,
    showcaseError,
    tree: fileTree(abs),
    zip: `/api/skills/${skill.kind}/${encodeURIComponent(skill.folder)}.zip`,
    zipName: skillZipName(skill.folder),
    runtime: skillRuntimeExtras(skill.folder),
  };
}

export async function getSkillShowcaseAsset(kind, id, file) {
  const skill = await getSkillDetail(kind, id);
  if (!skill) return null;
  return readShowcaseAsset(join(REPO_ROOT, skill.path), skill.showcase, file);
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
  const { items } = await listSkills();
  const hits = [];
  for (const s of items) {
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
