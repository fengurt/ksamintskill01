// Skill Hub — local control panel for ksamintskill01.
// Binds 127.0.0.1 only. No auth. No free-form shell.
import { createServer } from "node:http";
import { readFile, mkdir } from "node:fs/promises";
import { existsSync, createReadStream, statSync } from "node:fs";
import { dirname, join, extname, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { PORT, DATA_DIR, REPO_ROOT, GUI_ROOT, safeResolve, isDeniedPath, relToRepo, safeWorkDir } from "./lib/paths.js";
import { repoStatus } from "./lib/repo.js";
import { listSkills, getSkillDetail, skillGraph, searchSkills } from "./lib/skills.js";
import { registryStatus, checkUpstreamDrift } from "./lib/registry.js";
import {
  listRuns,
  getRun,
  getPageMaterial,
  getAuditPage,
  listAuditPages,
  agentBrief,
  getUnitTexts,
} from "./lib/runs.js";
import {
  listProjects,
  getProject,
  createProject,
  updateProject,
  deleteProject,
} from "./lib/projects.js";
import { listTemplates, getTemplate } from "./lib/templates.js";
import { listJobs, getJob, startJob, cancelJob, subscribe } from "./lib/jobs.js";
import { healthSnapshot, symlinkIntegrity } from "./lib/health.js";
import { baslideSummary, listThemes } from "./lib/themes.js";
import { getPack, skillStagesFor, VIEW_STAGES, stageReady, getStageView } from "./lib/pack.js";
import { streamPackZip, streamSlidesZip } from "./lib/archive.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PUBLIC = join(__dirname, "public");

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".md": "text/markdown; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".webp": "image/webp",
};

function send(res, code, data, type = "application/json") {
  const buf = typeof data === "string" || Buffer.isBuffer(data) ? data : JSON.stringify(data);
  res.writeHead(code, { "content-type": type, "cache-control": "no-store" });
  res.end(buf);
}

function readBody(req) {
  return new Promise((resolve) => {
    let b = "";
    req.on("data", (c) => (b += c));
    req.on("end", () => {
      try {
        resolve(b ? JSON.parse(b) : {});
      } catch {
        resolve({});
      }
    });
  });
}

async function serveStatic(req, res, path) {
  let file = path === "/" ? "/index.html" : path;
  if (file.includes("..")) return send(res, 400, { error: "bad path" });
  const abs = join(PUBLIC, file);
  if (!abs.startsWith(PUBLIC) || !existsSync(abs) || !statSync(abs).isFile()) {
    return send(res, 404, { error: "not found" });
  }
  const type = MIME[extname(abs)] || "application/octet-stream";
  res.writeHead(200, { "content-type": type, "cache-control": "no-store" });
  createReadStream(abs).pipe(res);
}

const server = createServer(async (req, res) => {
  const u = new URL(req.url, `http://127.0.0.1:${PORT}`);
  const path = u.pathname;
  const method = req.method || "GET";

  try {
    if (path.startsWith("/api/")) {
      await handleApi(req, res, method, path, u);
      return;
    }
    if (method === "GET" && path.startsWith("/slides/")) {
      await serveDeck(res, path);
      return;
    }
    await serveStatic(req, res, path);
  } catch (e) {
    console.error(e);
    if (!res.headersSent) send(res, 500, { error: e.message || String(e) });
  }
});

async function handleApi(req, res, method, path, u) {
  // Home / status
  if (method === "GET" && path === "/api/status") {
    const [repo, skills, registry, projects, jobs, runs] = await Promise.all([
      repoStatus(),
      listSkills({ includeVendored: false }),
      registryStatus(),
      Promise.resolve(listProjects()),
      Promise.resolve(listJobs()),
      Promise.resolve(listRuns()),
    ]);
    let links;
    try {
      links = symlinkIntegrity();
    } catch (e) {
      links = { error: e.message };
    }
    return send(res, 200, {
      repo,
      skills: skills.totals,
      registry,
      links,
      recentProjects: projects.slice(0, 8),
      recentJobs: jobs.slice(0, 8),
      recentRuns: runs.slice(0, 8),
      totals: {
        projects: projects.length,
        jobs: jobs.length,
        runs: runs.length,
        templates: listTemplates().length,
        sources: registry.sources.length,
      },
      baslide: baslideSummary(),
      port: PORT,
      repoRoot: REPO_ROOT,
    });
  }

  if (method === "GET" && path === "/api/health") {
    return send(res, 200, await healthSnapshot());
  }

  // Skills
  if (method === "GET" && path === "/api/skills") {
    const includeVendored = u.searchParams.get("vendored") !== "0";
    return send(res, 200, await listSkills({ includeVendored }));
  }
  if (method === "GET" && path === "/api/skills/graph") {
    return send(res, 200, await skillGraph());
  }
  if (method === "GET" && path === "/api/skills/search") {
    return send(res, 200, { hits: await searchSkills(u.searchParams.get("q") || "") });
  }
  {
    const m = path.match(/^\/api\/skills\/([^/]+)\/(.+)$/);
    if (method === "GET" && m) {
      const detail = await getSkillDetail(decodeURIComponent(m[1]), decodeURIComponent(m[2]));
      if (!detail) return send(res, 404, { error: "skill not found" });
      return send(res, 200, detail);
    }
  }

  // Registry
  if (method === "GET" && path === "/api/registry") {
    return send(res, 200, await registryStatus());
  }
  {
    const m = path.match(/^\/api\/registry\/([^/]+)\/drift$/);
    if (method === "POST" && m) {
      return send(res, 200, await checkUpstreamDrift(decodeURIComponent(m[1])));
    }
  }

  // Runs
  if (method === "GET" && path === "/api/runs") {
    return send(res, 200, { runs: listRuns() });
  }
  {
    const m = path.match(/^\/api\/runs\/([^/]+)$/);
    if (method === "GET" && m) {
      const run = getRun(decodeURIComponent(m[1]));
      if (!run) return send(res, 404, { error: "run not found" });
      return send(res, 200, run);
    }
  }
  {
    const m = path.match(/^\/api\/runs\/([^/]+)\/pages\/([^/]+)$/);
    if (method === "GET" && m) {
      const page = getPageMaterial(decodeURIComponent(m[1]), decodeURIComponent(m[2]));
      if (!page) return send(res, 404, { error: "page not found" });
      return send(res, 200, page);
    }
  }
  {
    const m = path.match(/^\/api\/runs\/([^/]+)\/units\/([^/]+)$/);
    if (method === "GET" && m) {
      const texts = getUnitTexts(decodeURIComponent(m[1]), [decodeURIComponent(m[2])]);
      const unit = texts[decodeURIComponent(m[2])];
      if (!unit) return send(res, 404, { error: "unit not found" });
      return send(res, 200, unit);
    }
  }
  {
    const m = path.match(/^\/api\/runs\/([^/]+)\/audit$/);
    if (method === "GET" && m) {
      return send(res, 200, { pages: listAuditPages(decodeURIComponent(m[1])) });
    }
  }
  {
    const m = path.match(/^\/api\/runs\/([^/]+)\/audit\/([^/]+)$/);
    if (method === "GET" && m) {
      const page = getAuditPage(decodeURIComponent(m[1]), decodeURIComponent(m[2]));
      if (!page) return send(res, 404, { error: "page not found" });
      return send(res, 200, page);
    }
  }
  {
    const m = path.match(/^\/api\/runs\/([^/]+)\/brief$/);
    if (method === "GET" && m) {
      const brief = agentBrief(decodeURIComponent(m[1]));
      if (!brief) return send(res, 404, { error: "run not found" });
      return send(res, 200, { markdown: brief });
    }
  }

  // Projects
  if (method === "GET" && path === "/api/projects") {
    const projects = listProjects().map((p) => {
      const runId = (p.work || "").replace(/^\.work\//, "");
      return { ...p, pack: runId ? getPack(runId) : null };
    });
    return send(res, 200, { projects });
  }
  if (method === "POST" && path === "/api/projects") {
    const body = await readBody(req);
    return send(res, 201, createProject(body));
  }
  {
    const m = path.match(/^\/api\/projects\/([^/]+)\/(pack|slides)\.zip$/);
    if (method === "GET" && m) {
      const p = getProject(decodeURIComponent(m[1]));
      if (!p) return send(res, 404, { error: "not found" });
      const runId = (p.work || "").replace(/^\.work\//, "");
      if (!runId) return send(res, 400, { error: "no work dir" });
      try {
        if (m[2] === "slides") streamSlidesZip(runId, res);
        else streamPackZip(runId, res, { source: p.source });
      } catch (e) {
        return send(res, 400, { error: e.message });
      }
      return;
    }
  }
  {
    const m = path.match(/^\/api\/projects\/([^/]+)\/stage\/([^/]+)$/);
    if (method === "GET" && m) {
      const p = getProject(decodeURIComponent(m[1]));
      if (!p) return send(res, 404, { error: "not found" });
      const runId = (p.work || "").replace(/^\.work\//, "");
      const stageId = decodeURIComponent(m[2]);
      return send(res, 200, getStageView(runId, stageId, { source: p.source }));
    }
  }
  {
    const m = path.match(/^\/api\/projects\/([^/]+)$/);
    if (m) {
      const id = decodeURIComponent(m[1]);
      if (method === "GET") {
        const p = getProject(id);
        if (!p) return send(res, 404, { error: "not found" });
        const runId = (p.work || "").replace(/^\.work\//, "");
        const pack = runId ? getPack(runId) : null;
        const { skills, laterSkills } = skillStagesFor(p, pack);
        let run = null;
        try {
          run = runId ? getRun(runId) : null;
        } catch {
          run = null;
        }
        return send(res, 200, {
          ...p,
          pack,
          skills,
          laterSkills,
          run: run
            ? {
                id: run.id,
                page_count: run.deck?.page_count,
                total_units: run.index?.total_units,
                hop1: run.auditSource?.counts || null,
                hop2: run.auditHtml?.counts || null,
                deckHref: run.deckHref,
              }
            : null,
          templateMeta: getTemplate(p.template),
          viewStages: VIEW_STAGES.map((s) => {
            let abs = null;
            try {
              abs = runId ? safeWorkDir(runId) : null;
            } catch {
              abs = null;
            }
            const ready = stageReady(abs, s.id, { pack, source: p.source });
            return {
              ...s,
              status: ready ? "ok" : s.later ? "later" : "pending",
            };
          }),
        });
      }
      if (method === "PATCH") {
        const body = await readBody(req);
        const p = updateProject(id, body);
        if (!p) return send(res, 404, { error: "not found" });
        return send(res, 200, p);
      }
      if (method === "DELETE") {
        return send(res, deleteProject(id) ? 200 : 404, { ok: true });
      }
    }
  }

  if (method === "GET" && path === "/api/themes") {
    return send(res, 200, listThemes());
  }

  // Templates
  if (method === "GET" && path === "/api/templates") {
    return send(res, 200, { templates: listTemplates() });
  }
  {
    const m = path.match(/^\/api\/templates\/([^/]+)$/);
    if (method === "GET" && m) {
      const t = getTemplate(decodeURIComponent(m[1]));
      if (!t) return send(res, 404, { error: "not found" });
      return send(res, 200, t);
    }
  }

  // Jobs
  if (method === "GET" && path === "/api/jobs") {
    return send(res, 200, { jobs: listJobs() });
  }
  if (method === "POST" && path === "/api/jobs") {
    const body = await readBody(req);
    try {
      const job = await startJob({
        templateId: body.template,
        projectId: body.projectId || null,
        work: body.work,
        source: body.source,
        html: body.html,
        theme: body.theme,
        standards: body.standards,
        genre: body.genre,
      });
      return send(res, 201, job);
    } catch (e) {
      return send(res, 400, { error: e.message });
    }
  }
  {
    const m = path.match(/^\/api\/jobs\/([^/]+)$/);
    if (method === "GET" && m) {
      const job = getJob(decodeURIComponent(m[1]));
      if (!job) return send(res, 404, { error: "not found" });
      return send(res, 200, job);
    }
  }
  {
    const m = path.match(/^\/api\/jobs\/([^/]+)\/cancel$/);
    if (method === "POST" && m) {
      return send(res, 200, { ok: cancelJob(decodeURIComponent(m[1])) });
    }
  }
  {
    const m = path.match(/^\/api\/jobs\/([^/]+)\/stream$/);
    if (method === "GET" && m) {
      const id = decodeURIComponent(m[1]);
      const job = getJob(id);
      if (!job) return send(res, 404, { error: "not found" });
      res.writeHead(200, {
        "content-type": "text/event-stream",
        "cache-control": "no-cache",
        connection: "keep-alive",
      });
      // replay tail
      const live = getJob(id);
      if (live?.logTail) {
        for (const line of live.logTail) {
          res.write(`data: ${JSON.stringify(line)}\n\n`);
        }
      }
      const unsub = subscribe(id, (line) => {
        try {
          res.write(`data: ${JSON.stringify(line)}\n\n`);
        } catch {
          /* */
        }
      });
      const ping = setInterval(() => {
        try {
          res.write(`: ping\n\n`);
        } catch {
          /* */
        }
      }, 15000);
      req.on("close", () => {
        clearInterval(ping);
        unsub();
      });
      return;
    }
  }

  // Safe file read (skills, .work, allowed roots) — never secrets
  if (method === "GET" && path === "/api/file") {
    const p = u.searchParams.get("path");
    try {
      const abs = safeResolve(p, { mustExist: true });
      if (isDeniedPath(abs)) return send(res, 403, { error: "denied" });
      const st = statSync(abs);
      if (!st.isFile() || st.size > 8 * 1024 * 1024) {
        return send(res, 400, { error: "file too large or not a file" });
      }
      const text = await readFile(abs, "utf8");
      return send(res, 200, {
        path: relToRepo(abs),
        name: basename(abs),
        text,
        size: st.size,
      });
    } catch (e) {
      return send(res, 400, { error: e.message });
    }
  }

  return send(res, 404, { error: "unknown api" });
}

function serveDeck(res, path) {
  const m = path.match(/^\/slides\/([^/]+)\/deck\.html$/);
  if (!m) return send(res, 404, { error: "not found" });
  let abs;
  try {
    abs = join(safeWorkDir(decodeURIComponent(m[1])), "slides/deck.html");
  } catch (e) {
    return send(res, 400, { error: e.message });
  }
  if (!existsSync(abs) || !statSync(abs).isFile()) return send(res, 404, { error: "deck not rendered" });
  res.writeHead(200, { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" });
  createReadStream(abs).pipe(res);
}

await mkdir(DATA_DIR, { recursive: true });
server.listen(PORT, "127.0.0.1", () => {
  console.log(`Skill Hub GUI → http://127.0.0.1:${PORT}`);
  console.log(`repo: ${REPO_ROOT}`);
  console.log(`gui:  ${GUI_ROOT}`);
});
