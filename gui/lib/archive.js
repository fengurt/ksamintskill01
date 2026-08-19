import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { basename, dirname, join } from "node:path";
import { REPO_ROOT, safeResolve, safeWorkDir, underRoot } from "./paths.js";
import { assembleBrandSubskillStage } from "./showcase.js";

/** Extra files a skill zip must carry because SKILL.md only points at them. */
export const SKILL_RUNTIME = {
  "mdpages2htmlslides": [
    { from: "modules/baslide01/templates/TIANSIGHT", to: "runtime/templates/TIANSIGHT", why: "L2 HTML 壳 + TIANSIGHT CSS" },
    { from: "modules/baslide01/prompts/loop", to: "runtime/prompts/loop", why: "brand.md + 各 job 循环规范" },
    { from: "modules/baslide01/scripts/build-TIANSIGHT-deck.py", to: "runtime/scripts/build-TIANSIGHT-deck.py", why: "L3 svg_figure" },
  ],
};

/** Zip / studio folders. Work dir on disk stays flat for the Python gates. */
export const PACK_FOLDERS = [
  {
    id: "original",
    title: "原文",
    files: ["index.json", "index.md", "units.json", "anchors.json", "source-manifest.json"],
    source: true,
  },
  {
    id: "pages",
    title: "逐页 md · HTML slides 开发",
    files: ["deck.json", "outline.md", "deck-plan.json", "slide-plan.json", "pack.json"],
    pages: true,
    assets: true,
  },
  {
    id: "audit",
    title: "审阅",
    files: ["audit.md", "audit-source.json", "fit-report.json", "fidelity.json", "schema-report.json", "audit-layout.json", "audit-pdf.json"],
    review: true,
  },
];

/** HTML slides plus the files another agent needs to review / give feedback. */
const SLIDES_ENTRIES = [
  "slides",
  "deck-plan.json",
  "slide-plan.json",
  "slides.json",
  "audit-html.json",
  "audit-layout.json",
  "audit-pdf.json",
  "audit.md",
];

function zipHasBin() {
  return !spawnSync("zip", ["-v"], { stdio: "ignore" }).error;
}

function safeStem(runId) {
  return String(runId).replace(/[^a-zA-Z0-9._-]/g, "_");
}

function readJsonSafe(p) {
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

function presentEntries(abs, entries) {
  return entries.filter((e) => existsSync(join(abs, e)));
}

export function resolvePackSource(abs, source) {
  const named = join(abs, "source.md");
  if (existsSync(named)) return named;
  const candidates = [source, readJsonSafe(join(abs, "index.json"))?.source, readJsonSafe(join(abs, "pack.json"))?.source];
  for (const c of candidates) {
    if (!c) continue;
    try {
      const real = safeResolve(String(c), { mustExist: true });
      if (existsSync(real)) return real;
    } catch {
      if (existsSync(c)) return c;
    }
  }
  return null;
}

export function buildPackReviewMd(abs, sourcePath) {
  const index = readJsonSafe(join(abs, "index.json")) || {};
  const deck = readJsonSafe(join(abs, "deck.json")) || {};
  const hop1 = readJsonSafe(join(abs, "audit-source.json")) || {};
  const pagesDir = join(abs, "pages");
  const pageFiles = existsSync(pagesDir) ? readdirSync(pagesDir).filter((f) => f.endsWith(".md")).length : 0;
  const counts = hop1.counts || {};
  const hard = Number(counts.hard ?? 0);
  const warn = Number(counts.warn ?? 0);
  const findings = (hop1.findings || []).filter((f) => f.severity === "hard").slice(0, 12);
  const srcName = sourcePath ? basename(sourcePath) : "—";
  const ok = hard === 0 && pageFiles > 0;
  const lines = [
    "# 审阅报告（简要）",
    "",
    `- 原文：\`${srcName}\` → 包内 \`original/${srcName}\``,
    `- 单元：${index.total_units ?? "—"} · 分页：${deck.pages?.length ?? pageFiles} （\`pages/*.md\` ${pageFiles} 个）`,
    `- hop1 原文→分页：hard **${hard}** · warn **${warn}**`,
    `- 结论：${ok ? "可交给开发（hop1 hard=0，逐页 md 已齐）" : "先修 hop1 hard / 补齐 pages/"}`,
    "",
    "## 包内必读",
    "",
    "- `original/` — 原始长文档（及切分账本）",
    "- `pages/` — 逐页 Markdown + slide-plan，给 HTML slides 开发",
    "- `audit/REVIEW.md` — 本简要审阅",
    "",
  ];
  if (findings.length) {
    lines.push("## hop1 hard（最多 12 条）", "");
    for (const f of findings) {
      lines.push(`- \`${f.page || "?"}\` ${f.code || ""} ${f.detail || f.anchor || ""}`.trim());
    }
    lines.push("");
  }
  return lines.join("\n");
}

function streamZipFrom(cwd, entries, res, name) {
  res.writeHead(200, {
    "content-type": "application/zip",
    "content-disposition": `attachment; filename="${name}"`,
    "cache-control": "no-store",
  });
  const child = spawn("zip", ["-r", "-q", "-", ...entries], { cwd });
  child.stdout.pipe(res);
  child.stderr.on("data", () => {});
  return child;
}

export function streamBrandSubskillZip(input, res) {
  if (!zipHasBin()) throw new Error("zip command not found");
  const { stage, rootName, cleanup } = assembleBrandSubskillStage(input);
  const child = streamZipFrom(stage, [rootName], res, `${rootName}-skill.zip`);
  child.on("close", cleanup);
  child.on("error", (err) => {
    cleanup();
    if (!res.writableEnded) {
      if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: err.message }));
    }
  });
  return child;
}

function streamWorkZip(runId, res, { entries, suffix, emptyError }) {
  if (!zipHasBin()) throw new Error("zip command not found");
  const abs = safeWorkDir(runId);
  const found = presentEntries(abs, entries);
  if (!found.length) throw new Error(emptyError);
  const name = `${safeStem(basename(abs))}-${suffix}.zip`;
  const child = streamZipFrom(abs, found, res, name);
  child.on("error", (err) => {
    if (!res.writableEnded) {
      if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: err.message }));
    }
  });
}

export function packZipName(runId) {
  return `${safeStem(runId)}-pack.zip`;
}

export function slidesZipName(runId) {
  return `${safeStem(runId)}-slides-review.zip`;
}

function linkIfPresent(from, to) {
  if (!existsSync(from) || existsSync(to)) return false;
  mkdirSync(dirname(to), { recursive: true });
  symlinkSync(from, to);
  return true;
}

export function assemblePackZipStage(abs, { source = null } = {}) {
  const sourcePath = resolvePackSource(abs, source);
  const stage = join(tmpdir(), `ksamint-pack-${safeStem(basename(abs))}-${Date.now()}`);
  mkdirSync(stage, { recursive: true });
  let linked = 0;
  try {
    for (const folder of PACK_FOLDERS) {
      const dest = join(stage, folder.id);
      if (folder.source && sourcePath && existsSync(sourcePath)) {
        const name = basename(sourcePath) || "source.md";
        mkdirSync(dest, { recursive: true });
        copyFileSync(sourcePath, join(dest, name));
        linked += 1;
      }
      if (folder.pages) {
        const pagesAbs = join(abs, "pages");
        if (existsSync(pagesAbs)) {
          mkdirSync(dest, { recursive: true });
          for (const ent of readdirSync(pagesAbs)) {
            if (ent.startsWith(".")) continue;
            if (linkIfPresent(join(pagesAbs, ent), join(dest, ent))) linked += 1;
          }
        }
      }
      if (folder.assets) {
        const assetsAbs = join(abs, "assets");
        if (existsSync(assetsAbs) && linkIfPresent(assetsAbs, join(dest, "assets"))) linked += 1;
      }
      for (const rel of folder.files) {
        if (linkIfPresent(join(abs, rel), join(dest, rel))) linked += 1;
      }
    }
    const hasWorkManifest = linkIfPresent(join(abs, "MANIFEST.md"), join(stage, "WORK-MANIFEST.md"));
    if (hasWorkManifest) linked += 1;
    if (!linked) {
      rmSync(stage, { recursive: true, force: true });
      throw new Error("pack empty");
    }
    mkdirSync(join(stage, "audit"), { recursive: true });
    writeFileSync(join(stage, "audit", "REVIEW.md"), buildPackReviewMd(abs, sourcePath), "utf8");
    const readme = [
      "# 文件包",
      "",
      ...PACK_FOLDERS.map((f) => `- \`${f.id}/\` — ${f.title}`),
      "",
    ].join("\n");
    writeFileSync(join(stage, "README.md"), readme, "utf8");
    const manifest = [
      "# ZIP manifest",
      "",
      "This archive reorganizes the flat work-directory outputs for handoff.",
      "",
      "- `README.md` — folder guide",
      ...(hasWorkManifest ? ["- `WORK-MANIFEST.md` — original `emit-pack.py` work-directory manifest"] : []),
      ...PACK_FOLDERS.filter((f) => existsSync(join(stage, f.id))).map((f) => `- \`${f.id}/\` — ${f.title}`),
      "",
    ].join("\n");
    writeFileSync(join(stage, "MANIFEST.md"), manifest, "utf8");
    const entries = ["README.md", "MANIFEST.md", "WORK-MANIFEST.md", ...PACK_FOLDERS.map((f) => f.id)].filter((e) => existsSync(join(stage, e)));
    return {
      stage,
      entries,
      cleanup() {
        try {
          rmSync(stage, { recursive: true, force: true });
        } catch {
          /* ignore */
        }
      },
    };
  } catch (e) {
    try {
      rmSync(stage, { recursive: true, force: true });
    } catch {
      /* ignore */
    }
    throw e;
  }
}

export function streamPackZip(runId, res, { source = null } = {}) {
  if (!zipHasBin()) throw new Error("zip command not found");
  const abs = safeWorkDir(runId);
  const { stage, entries, cleanup } = assemblePackZipStage(abs, { source });
  const name = packZipName(basename(abs));
  const child = streamZipFrom(stage, entries, res, name);
  child.on("close", cleanup);
  child.on("error", (err) => {
    cleanup();
    if (!res.writableEnded) {
      if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: err.message }));
    }
  });
}

export function streamSlidesZip(runId, res) {
  const abs = safeWorkDir(runId);
  if (!existsSync(join(abs, "slides/deck.html"))) throw new Error("slides not ready");
  streamWorkZip(runId, res, {
    entries: SLIDES_ENTRIES,
    suffix: "slides-review",
    emptyError: "slides empty",
  });
}

function projectHtml(project) {
  if (project.html) return safeResolve(project.html, { mustExist: true });
  if (project.work) {
    const html = join(safeWorkDir(project.work), "slides/deck.html");
    if (existsSync(html)) return html;
  }
  throw new Error(`${project.name || project.id}: no HTML report`);
}

function renderProjectPdf(project, dest) {
  if (!project.work) throw new Error(`${project.name || project.id}: verified PDF export requires a managed work directory`);
  const work = safeWorkDir(project.work);
  const py = process.env.PYTHON || "python3";
  // ponytail: synchronous local export keeps the endpoint tiny; move to a job if large batch exports become common.
  const result = spawnSync(py, [
    join(REPO_ROOT, "skills/mdpages2htmlslides/scripts/export_pdf.py"),
    "--html", projectHtml(project),
    "--schema-report", join(work, "schema-report.json"),
    "--layout-report", join(work, "audit-layout.json"),
    "--out", dest,
    "--report", join(work, "audit-pdf.json"),
  ], { encoding: "utf8", timeout: 120_000 });
  if (result.error || result.status !== 0 || !existsSync(dest)) {
    throw new Error(`${project.name || project.id}: ${result.stderr?.trim() || "PDF export failed"}`);
  }
}

export function assembleProjectsPdfStage(projects) {
  if (!projects.length) throw new Error("no projects selected");
  const stage = mkdtempSync(join(tmpdir(), "ksamint-project-pdfs-"));
  const entries = [];
  const used = new Set();
  try {
    for (const project of projects) {
      const label = String(project.name || "").replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_").trim().slice(0, 70);
      let stem = `${safeStem(project.id)}${label ? `-${label}` : ""}`;
      let name = `${stem}.pdf`;
      for (let i = 2; used.has(name); i += 1) name = `${stem}-${i}.pdf`;
      used.add(name);
      renderProjectPdf(project, join(stage, name));
      entries.push(name);
    }
    writeFileSync(join(stage, "projects.json"), JSON.stringify(projects.map(({ report_root, ...p }) => p), null, 2) + "\n");
    entries.push("projects.json");
    return {
      stage,
      entries,
      cleanup() { rmSync(stage, { recursive: true, force: true }); },
    };
  } catch (e) {
    rmSync(stage, { recursive: true, force: true });
    throw e;
  }
}

export function streamProjectsPdfZip(projects, res) {
  if (!zipHasBin()) throw new Error("zip command not found");
  const { stage, entries, cleanup } = assembleProjectsPdfStage(projects);
  const child = streamZipFrom(stage, entries, res, "projects-pdf.zip");
  child.on("close", cleanup);
  child.on("error", (err) => {
    cleanup();
    if (!res.writableEnded) res.end(JSON.stringify({ error: err.message }));
  });
  return child;
}

export function skillZipName(folder) {
  return `${safeStem(String(folder).split("/").pop())}-skill.zip`;
}

export function skillRuntimeExtras(folder) {
  const key = String(folder || "").split("/").pop();
  return SKILL_RUNTIME[key] || SKILL_RUNTIME[folder] || [];
}

export function assembleSkillZipStage({ path, folder, name, sourceId }) {
  const abs = join(REPO_ROOT, path);
  const vendorRoot = join(REPO_ROOT, "vendor");
  if (!existsSync(abs)) throw new Error("skill folder missing");
  if (!underRoot(abs, join(REPO_ROOT, "skills")) && !underRoot(abs, join(REPO_ROOT, "vendor"))) {
    throw new Error("skill path denied");
  }
  const rootName = safeStem(name || String(folder).split("/").pop() || "skill");
  const extras = skillRuntimeExtras(folder);
  const stage = join(tmpdir(), `ksamint-skill-${rootName}-${Date.now()}`);
  const root = join(stage, rootName);
  mkdirSync(root, { recursive: true });
  for (const ent of readdirSync(abs)) {
    if (ent.startsWith(".") || ent === "runtime") continue;
    symlinkSync(join(abs, ent), join(root, ent));
  }
  const sourceRoot = sourceId ? join(vendorRoot, sourceId) : null;
  if (sourceRoot && underRoot(sourceRoot, vendorRoot)) {
    for (const license of ["LICENSE", "LICENSE.txt", "LICENSE.md", "NOTICE"]) {
      const from = join(sourceRoot, license);
      const to = join(root, license);
      if (existsSync(from) && !existsSync(to)) symlinkSync(from, to);
    }
  }
  const included = [];
  for (const extra of extras) {
    const from = join(REPO_ROOT, extra.from);
    if (!existsSync(from)) continue;
    const to = join(root, extra.to);
    mkdirSync(dirname(to), { recursive: true });
    symlinkSync(from, to);
    included.push(extra);
  }
  if (included.length) {
    const lines = [
      "# Runtime (not in SKILL.md alone)",
      "",
      ...included.map((e) => `- \`${e.to}\` — ${e.why}`),
      "",
    ];
    writeFileSync(join(root, "RUNTIME.md"), lines.join("\n"), "utf8");
  }
  return {
    stage,
    rootName,
    extras: included,
    cleanup() {
      try {
        rmSync(stage, { recursive: true, force: true });
      } catch {
        /* ignore */
      }
    },
  };
}

export function streamSkillZip(skill, res) {
  if (!zipHasBin()) throw new Error("zip command not found");
  const { stage, rootName, cleanup } = assembleSkillZipStage(skill);
  const name = skillZipName(skill.folder || skill.name);
  const child = streamZipFrom(stage, [rootName], res, name);
  child.on("close", cleanup);
  child.on("error", (err) => {
    cleanup();
    if (!res.writableEnded) {
      if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: err.message }));
    }
  });
}

export function streamSkillsBundleZip(skills, res, name = "skills-starred.zip") {
  if (!zipHasBin()) throw new Error("zip command not found");
  if (!skills.length) throw new Error("no skills to export");
  if (skills.length === 1) return streamSkillZip(skills[0], res);
  const stage = join(tmpdir(), `ksamint-skills-${Date.now()}`);
  mkdirSync(stage, { recursive: true });
  const parts = [];
  const names = [];
  const cleanup = () => {
    for (const p of parts) p.cleanup();
    try {
      rmSync(stage, { recursive: true, force: true });
    } catch {
      /* ignore */
    }
  };
  try {
    for (const s of skills) {
      const part = assembleSkillZipStage(s);
      parts.push(part);
      const dest = join(stage, part.rootName);
      if (existsSync(dest)) continue;
      symlinkSync(join(part.stage, part.rootName), dest);
      names.push(part.rootName);
    }
    const child = streamZipFrom(stage, names, res, name);
    child.on("close", cleanup);
    child.on("error", (err) => {
      cleanup();
      if (!res.writableEnded) {
        if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
  } catch (e) {
    cleanup();
    throw e;
  }
}
