import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { randomBytes } from "node:crypto";
import { DATA_DIR, safeWorkDir, safeResolve, relToRepo } from "./paths.js";
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
  return load().projects.sort((a, b) => (b.updated_at || 0) - (a.updated_at || 0));
}

export function getProject(id) {
  return load().projects.find((p) => p.id === id) || null;
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
