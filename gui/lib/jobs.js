import { spawn } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync, appendFileSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { randomBytes } from "node:crypto";
import { EventEmitter } from "node:events";
import { DATA_DIR, REPO_ROOT, BASLIDE_ROOT, safeWorkDir, safeResolve, expandHome } from "./paths.js";
import { getTemplate, resolveStep, stepsFor, normalizeStandards } from "./templates.js";
import { appendGate } from "./projects.js";

const JOBS_DIR = join(DATA_DIR, "jobs");
const RING = 4000;
const jobs = new Map();
const bus = new EventEmitter();
bus.setMaxListeners(100);

function ensure() {
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });
  if (!existsSync(JOBS_DIR)) mkdirSync(JOBS_DIR, { recursive: true });
}

function persist(job) {
  ensure();
  const slim = {
    id: job.id,
    template: job.template,
    projectId: job.projectId,
    status: job.status,
    steps: job.steps,
    created_at: job.created_at,
    finished_at: job.finished_at,
    error: job.error,
    ctx: {
      work: job.ctx.work,
      source: job.ctx.source,
      html: job.ctx.html,
      theme: job.ctx.theme,
    },
  };
  writeFileSync(join(JOBS_DIR, `${job.id}.json`), JSON.stringify(slim, null, 2) + "\n");
}

function emit(job, event, payload = {}) {
  const line = { ts: Date.now(), event, ...payload };
  job.log.push(line);
  if (job.log.length > RING) job.log.splice(0, job.log.length - RING);
  appendFileSync(join(JOBS_DIR, `${job.id}.log`), JSON.stringify(line) + "\n");
  bus.emit(job.id, line);
}

export function listJobs() {
  ensure();
  const fromMem = [...jobs.values()].map(publicJob);
  const seen = new Set(fromMem.map((j) => j.id));
  for (const f of readdirSync(JOBS_DIR).filter((n) => n.endsWith(".json"))) {
    const id = f.replace(/\.json$/, "");
    if (seen.has(id)) continue;
    try {
      fromMem.push(JSON.parse(readFileSync(join(JOBS_DIR, f), "utf8")));
    } catch {
      /* */
    }
  }
  return fromMem.sort((a, b) => (b.created_at || 0) - (a.created_at || 0));
}

export function getJob(id) {
  if (jobs.has(id)) return publicJob(jobs.get(id));
  const p = join(JOBS_DIR, `${id}.json`);
  if (!existsSync(p)) return null;
  const job = JSON.parse(readFileSync(p, "utf8"));
  const logPath = join(JOBS_DIR, `${id}.log`);
  const logTail = [];
  if (existsSync(logPath)) {
    const lines = readFileSync(logPath, "utf8").trim().split("\n").filter(Boolean);
    for (const line of lines.slice(-80)) {
      try {
        logTail.push(JSON.parse(line));
      } catch {
        /* */
      }
    }
  }
  return { ...job, logTail };
}

function publicJob(job) {
  return {
    id: job.id,
    template: job.template,
    projectId: job.projectId,
    status: job.status,
    steps: job.steps,
    created_at: job.created_at,
    finished_at: job.finished_at,
    error: job.error,
    mechanicalDraft: job.mechanicalDraft,
    ctx: { work: job.ctx.work, source: job.ctx.source, html: job.ctx.html, theme: job.ctx.theme },
    logTail: job.log.slice(-80),
  };
}

export function subscribe(jobId, fn) {
  bus.on(jobId, fn);
  return () => bus.off(jobId, fn);
}

export async function startJob({
  templateId,
  projectId = null,
  work,
  source,
  html,
  theme,
  standards,
}) {
  const tpl = getTemplate(templateId);
  if (!tpl) throw new Error(`unknown template: ${templateId}`);
  const std = normalizeStandards(standards);

  const ctx = {
    work: null,
    source: null,
    html: null,
    workAbs: null,
    sourceAbs: null,
    htmlAbs: null,
    theme: theme || "TIANSIGHT",
    baslide: BASLIDE_ROOT,
    failOnOverfull: std["fit-overfull"],
    standards: std,
  };
  if (tpl.needs.includes("work") || work) {
    ctx.workAbs = safeWorkDir(work);
    ctx.work = ctx.workAbs.replace(REPO_ROOT + "/", "");
    if (!existsSync(ctx.workAbs)) mkdirSync(ctx.workAbs, { recursive: true });
  }
  if (tpl.needs.includes("source") || source) {
    if (!source) throw new Error("source required");
    ctx.sourceAbs = safeResolve(expandHome(source), { mustExist: true });
    ctx.source = ctx.sourceAbs;
  }
  if (tpl.needs.includes("html") || html) {
    if (!html) throw new Error("html required");
    ctx.htmlAbs = safeResolve(expandHome(html), { mustExist: true });
    ctx.html = ctx.htmlAbs;
  }

  const planned = stepsFor(templateId, std);
  const id = `job_${randomBytes(4).toString("hex")}`;
  const job = {
    id,
    template: templateId,
    projectId,
    status: "running",
    steps: planned.map((s) => ({
      id: s.id,
      label: s.label,
      mechanical: !!s.mechanical,
      phase: s.phase || null,
      status: "pending",
      exitCode: null,
      started_at: null,
      finished_at: null,
    })),
    created_at: Date.now(),
    finished_at: null,
    error: null,
    mechanicalDraft: !!tpl.mechanicalDraft,
    ctx,
    log: [],
    child: null,
    cancel: false,
  };
  ensure();
  writeFileSync(join(JOBS_DIR, `${id}.log`), "");
  jobs.set(id, job);
  persist(job);
  emit(job, "job_start", { template: templateId });
  runPipeline(job).catch((e) => {
    job.status = "error";
    job.error = e.message;
    job.finished_at = Date.now();
    emit(job, "job_error", { error: e.message });
    persist(job);
  });
  return publicJob(job);
}

export function cancelJob(id) {
  const job = jobs.get(id);
  if (!job) return false;
  job.cancel = true;
  if (job.child) {
    try {
      job.child.kill("SIGTERM");
    } catch {
      /* */
    }
  }
  emit(job, "cancel", {});
  return true;
}

async function runPipeline(job) {
  for (const step of job.steps) {
    if (job.cancel) {
      job.status = "cancelled";
      job.finished_at = Date.now();
      emit(job, "job_cancelled", {});
      persist(job);
      return;
    }
    step.status = "running";
    step.started_at = Date.now();
    persist(job);
    emit(job, "step_start", { step: step.id, label: step.label });
    if (step.mechanical) {
      emit(job, "note", {
        text: "Mechanical draft — not curated. Copy the agent brief after this job to refine outline + pagination.",
      });
    }
    const resolved = resolveStep(step.id, job.ctx);
    const code = await spawnStep(job, resolved);
    step.exitCode = code;
    step.finished_at = Date.now();
    step.status = code === 0 ? "ok" : "fail";
    if (step.id === "render-slides" && code === 0 && job.ctx.workAbs) {
      const deckHtml = join(job.ctx.workAbs, "slides/deck.html");
      job.ctx.htmlAbs = deckHtml;
      job.ctx.html = deckHtml;
      emit(job, "note", { text: `Rendered deck → ${deckHtml}` });
    }
    emit(job, "step_end", { step: step.id, exitCode: code, status: step.status });
    persist(job);
    if (job.projectId) {
      appendGate(job.projectId, {
        job: job.id,
        step: step.id,
        status: step.status,
        exitCode: code,
      });
    }
    if (code !== 0) {
      job.status = "failed";
      job.error = `step ${step.id} exited ${code}`;
      job.finished_at = Date.now();
      emit(job, "job_failed", { step: step.id, exitCode: code });
      persist(job);
      return;
    }
  }
  job.status = "ok";
  job.finished_at = Date.now();
  emit(job, "job_ok", {});
  persist(job);
}

function spawnStep(job, resolved) {
  return new Promise((resolve) => {
    emit(job, "cmd", { cmd: resolved.cmd, args: resolved.args });
    const child = spawn(resolved.cmd, resolved.args, {
      cwd: resolved.cwd || REPO_ROOT,
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
    });
    job.child = child;
    child.stdout.on("data", (buf) => emit(job, "stdout", { text: buf.toString() }));
    child.stderr.on("data", (buf) => emit(job, "stderr", { text: buf.toString() }));
    child.on("error", (err) => {
      emit(job, "stderr", { text: err.message });
      job.child = null;
      resolve(1);
    });
    child.on("close", (code) => {
      job.child = null;
      resolve(code ?? 1);
    });
  });
}
