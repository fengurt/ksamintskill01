import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { basename, dirname, join } from "node:path";
import { REPO_ROOT, safeResolve, safeWorkDir, underRoot } from "./paths.js";

/** Extra files a skill zip must carry because SKILL.md only points at them. */
export const SKILL_RUNTIME = {
  "md-to-html-slides": [
    { from: "modules/baslide01/templates/TIANSIGHT", to: "runtime/templates/TIANSIGHT", why: "L2 HTML 壳 + TIANSIGHT CSS" },
    { from: "modules/baslide01/prompts/loop", to: "runtime/prompts/loop", why: "brand.md + 各 job 循环规范" },
    { from: "modules/baslide01/scripts/build-TIANSIGHT-deck.py", to: "runtime/scripts/build-TIANSIGHT-deck.py", why: "L3 svg_figure" },
  ],
};

const PACK_ENTRIES = [
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
  "fit-report.json",
];

/** HTML slides plus the files another agent needs to review / give feedback. */
const SLIDES_ENTRIES = [
  "slides",
  "slide-plan.json",
  "slides.json",
  "audit-html.json",
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

function resolvePackSource(abs, source) {
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
    `- 原文：\`${srcName}\` → 包内 \`source.md\``,
    `- 单元：${index.total_units ?? "—"} · 分页：${deck.pages?.length ?? pageFiles} （\`pages/*.md\` ${pageFiles} 个）`,
    `- hop1 原文→分页：hard **${hard}** · warn **${warn}**`,
    `- 结论：${ok ? "可交给开发（hop1 hard=0，逐页 md 已齐）" : "先修 hop1 hard / 补齐 pages/"}`,
    "",
    "## 包内必读",
    "",
    "- `source.md` — 原始长文档",
    "- `pages/` — 无损分页后的逐页素材",
    "- `REVIEW.md` — 本简要审阅",
    "- `slide-plan.json` — 后续 md-to-html-slides 输入",
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

export function streamPackZip(runId, res, { source = null } = {}) {
  if (!zipHasBin()) throw new Error("zip command not found");
  const abs = safeWorkDir(runId);
  const found = presentEntries(abs, PACK_ENTRIES);
  const sourcePath = resolvePackSource(abs, source);
  if (!found.length && !sourcePath) throw new Error("pack empty");
  const stage = join(tmpdir(), `ksamint-pack-${safeStem(basename(abs))}-${Date.now()}`);
  mkdirSync(stage, { recursive: true });
  try {
    for (const e of found) {
      symlinkSync(join(abs, e), join(stage, e));
    }
    if (sourcePath) copyFileSync(sourcePath, join(stage, "source.md"));
    writeFileSync(join(stage, "REVIEW.md"), buildPackReviewMd(abs, sourcePath), "utf8");
    const entries = [...found];
    if (sourcePath) entries.unshift("source.md");
    entries.unshift("REVIEW.md");
    const name = packZipName(basename(abs));
    const child = streamZipFrom(stage, entries, res, name);
    const done = () => {
      try {
        rmSync(stage, { recursive: true, force: true });
      } catch {
        /* ignore */
      }
    };
    child.on("close", done);
    child.on("error", (err) => {
      done();
      if (!res.writableEnded) {
        if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
  } catch (e) {
    try {
      rmSync(stage, { recursive: true, force: true });
    } catch {
      /* ignore */
    }
    throw e;
  }
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

export function skillZipName(folder) {
  return `${safeStem(String(folder).split("/").pop())}-skill.zip`;
}

export function skillRuntimeExtras(folder) {
  const key = String(folder || "").split("/").pop();
  return SKILL_RUNTIME[key] || SKILL_RUNTIME[folder] || [];
}

export function assembleSkillZipStage({ path, folder, name }) {
  const abs = join(REPO_ROOT, path);
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
