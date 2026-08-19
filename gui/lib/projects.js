import { existsSync, mkdirSync, readFileSync, readdirSync, realpathSync, statSync, writeFileSync } from "node:fs";
import { basename, dirname, join, relative } from "node:path";
import { createHash, randomBytes } from "node:crypto";
import { ALLOWED_DOC_ROOTS, BASLIDE_ROOT, DATA_DIR, REPO_ROOT, safeWorkDir, safeResolve, relToRepo, underRoot } from "./paths.js";
import { normalizeStandards } from "./templates.js";

const FILE = join(DATA_DIR, "projects.json");

function ensure() {
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });
  if (!existsSync(FILE)) {
    writeFileSync(FILE, JSON.stringify({ version: 1, projects: [] }, null, 2) + "\n");
  }
}

function load() {
  ensure();
  try {
    return JSON.parse(readFileSync(FILE, "utf8"));
  } catch {
    return { version: 1, projects: [] };
  }
}

function save(data) {
  ensure();
  writeFileSync(FILE, JSON.stringify(data, null, 2) + "\n");
}

export function listProjects() {
  const saved = load().projects.map(decorateReport);
  return [...saved, ...discoverHistoryProjects(historyRoots(), saved)].sort(
    (a, b) => (b.updated_at || 0) - (a.updated_at || 0)
  );
}

export function getProject(id) {
  return listProjects().find((p) => p.id === id) || null;
}

function historyRoots() {
  return [...new Set([BASLIDE_ROOT, ...ALLOWED_DOC_ROOTS].map((p) => realpathOr(p)))]
    .filter((p) => existsSync(join(p, "decks")) || existsSync(join(p, "ref/htmls")))
    .sort((a, b) => Number(existsSync(join(b, "export/pdf"))) - Number(existsSync(join(a, "export/pdf"))));
}

function realpathOr(path) {
  try {
    return realpathSync(path);
  } catch {
    return path;
  }
}

function reportLocation(html) {
  if (!html) return null;
  let abs;
  try {
    abs = safeResolve(html, { mustExist: true });
  } catch {
    return null;
  }
  const root = [REPO_ROOT, ...ALLOWED_DOC_ROOTS]
    .map(realpathOr)
    .filter((p) => underRoot(abs, p))
    .sort((a, b) => b.length - a.length)[0];
  return root ? { root, path: relative(root, abs) } : null;
}

function decorateReport(project) {
  const at = reportLocation(project.html);
  if (!at) return project;
  return {
    ...project,
    report_root: at.root,
    report_path: at.path,
    report_href: `/reports/${encodeURIComponent(project.id)}/${at.path.split("/").map(encodeURIComponent).join("/")}`,
  };
}

function htmlTitle(path) {
  const raw = readFileSync(path, "utf8").slice(0, 256 * 1024);
  const match = raw.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  return (match?.[1] || "")
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/\s+/g, " ")
    .trim();
}

function historyFiles(root) {
  const out = [];
  const decks = join(root, "decks");
  if (existsSync(decks)) {
    for (const ent of readdirSync(decks, { withFileTypes: true })) {
      if (!ent.isDirectory()) continue;
      for (const name of ["presentation.html", "deck.html", "html-v1.html"]) {
        const path = join(decks, ent.name, name);
        if (existsSync(path)) out.push(path);
      }
    }
  }
  const refs = join(root, "ref/htmls");
  if (existsSync(refs)) {
    for (const ent of readdirSync(refs, { withFileTypes: true })) {
      if (ent.isFile() && ent.name.endsWith(".html")) out.push(join(refs, ent.name));
    }
  }
  return out;
}

function matchingPdf(root, reportPath) {
  const parts = reportPath.split("/");
  let stem = basename(reportPath, ".html");
  if (parts[0] === "decks" && (stem === "presentation" || stem === "deck")) stem = parts[1];
  else if (parts[0] === "decks" && stem === "html-v1") stem = `${parts[1]}-html-v1`;
  const pdf = join(root, "export/pdf", `${stem}.pdf`);
  return existsSync(pdf) ? pdf : null;
}

export function discoverHistoryProjects(roots, saved = []) {
  const seen = new Set(saved.map((p) => reportLocation(p.html)?.path).filter(Boolean));
  const out = [];
  for (const root of roots.map(realpathOr)) {
    for (const html of historyFiles(root)) {
      const reportPath = relative(root, html);
      if (seen.has(reportPath)) continue;
      seen.add(reportPath);
      const stat = statSync(html);
      const id = `hist_${createHash("sha256").update(reportPath).digest("hex").slice(0, 10)}`;
      out.push(decorateReport({
        id,
        name: htmlTitle(html) || basename(dirname(html)) || basename(html, ".html"),
        template: "baslide-history",
        html,
        pdf: matchingPdf(root, reportPath),
        work: null,
        source: null,
        theme: null,
        notes: "Imported from Baslide01 HTML history",
        history: true,
        read_only: true,
        created_at: stat.birthtimeMs || stat.mtimeMs,
        updated_at: stat.mtimeMs,
      }));
    }
  }
  return out;
}

export function createProject(input) {
  const data = load();
  const id = `prj_${randomBytes(4).toString("hex")}`;
  const now = Date.now();
  let source = null;
  let html = null;
  let work = null;
  if (input.source) source = relToRepo(safeResolve(input.source));
  if (input.html) html = relToRepo(safeResolve(input.html));
  if (input.work) work = relToRepo(safeWorkDir(input.work));
  else if (input.work_id) work = relToRepo(safeWorkDir(input.work_id));
  else {
    const slug = String(input.name || id)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 40);
    work = relToRepo(safeWorkDir(slug || id));
  }
  const project = {
    id,
    name: String(input.name || id).trim(),
    template: input.template || "long4hslides",
    source,
    html,
    work,
    skin: input.skin || input.theme || null,
    theme: input.theme || input.skin || "TIANSIGHT",
    standards: normalizeStandards(input.standards),
    genre: input.genre || "diagnosis",
    notes: input.notes || "",
    page_pack_approved: false,
    gate_history: [],
    created_at: now,
    updated_at: now,
  };
  data.projects.push(project);
  save(data);
  return project;
}

export function updateProject(id, patch) {
  const data = load();
  const i = data.projects.findIndex((p) => p.id === id);
  if (i < 0) return null;
  const cur = data.projects[i];
  const next = { ...cur, ...patch, id: cur.id, updated_at: Date.now() };
  if (patch.source) next.source = relToRepo(safeResolve(patch.source));
  if (patch.html) next.html = relToRepo(safeResolve(patch.html));
  if (patch.work) next.work = relToRepo(safeWorkDir(patch.work));
  if (patch.theme) next.theme = patch.theme;
  if (patch.standards) next.standards = normalizeStandards(patch.standards);
  if (typeof patch.page_pack_approved === "boolean") next.page_pack_approved = patch.page_pack_approved;
  data.projects[i] = next;
  save(data);
  return next;
}

export function deleteProject(id) {
  const data = load();
  const before = data.projects.length;
  data.projects = data.projects.filter((p) => p.id !== id);
  save(data);
  return before !== data.projects.length;
}

export function appendGate(id, gate) {
  const data = load();
  const i = data.projects.findIndex((p) => p.id === id);
  if (i < 0) return null;
  const entry = { ...gate, at: Date.now() };
  data.projects[i].gate_history = [...(data.projects[i].gate_history || []), entry].slice(-40);
  data.projects[i].updated_at = Date.now();
  save(data);
  return data.projects[i];
}
