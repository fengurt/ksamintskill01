import { join } from "node:path";
import { REPO_ROOT, BASLIDE_ROOT } from "./paths.js";

const LONG4H_STAGES = [
  { id: "normalize-source", label: "normalize source", phase: 1 },
  { id: "segment", label: "segment", phase: 1 },
  { id: "coverage-index", label: "coverage · index", phase: 1 },
  { id: "bootstrap", label: "outline + pagination draft", phase: 1, mechanical: true },
  { id: "estimate-fit", label: "layout budget", phase: 1, standard: "fit-overfull" },
  { id: "coverage-deck", label: "coverage · deck", phase: 1 },
  { id: "extract-anchors", label: "extract anchors", phase: 2, standard: "hop1" },
  { id: "audit-source", label: "hop1 · source → pages", phase: 2, standard: "hop1" },
  { id: "audit-report", label: "audit report", phase: 2, standard: "hop1" },
  { id: "emit-pack", label: "emit GF deck-plan", phase: 2 },
  { id: "budget-plan", label: "typographic budget", phase: 2 },
  { id: "gate-fidelity", label: "fidelity gate", phase: 2 },
  { id: "gate-schema", label: "schema gate", phase: 2 },
];

const LONG4H = {
  id: "long4hslides",
  title: "long4hslides · 长文档 → HTML 幻灯片",
  description: "规范化原文，完成可审阅的 page pack；批准后用同一 GF4p2slides contract 渲染、测量并跑 hop2。",
  needs: ["source", "work"],
  mechanicalDraft: true,
  completeWhen: "pack",
  checkpoint: "page-pack",
  skills: [
    {
      id: "longdoc2mdpages",
      label: "longdoc2mdpages",
      stages: [
        { id: "a-segment", label: "normalize + segment", steps: ["normalize-source", "segment", "coverage-index"], artifact: "index.json" },
        { id: "b-outline", label: "outline", steps: ["bootstrap"], artifact: "outline.md", mechanical: true },
        { id: "c-pagination", label: "pagination", steps: ["estimate-fit", "coverage-deck"], artifact: "deck.json" },
        { id: "d-emit", label: "GF page pack", steps: ["emit-pack", "budget-plan", "gate-fidelity", "gate-schema"], artifact: "deck-plan.json" },
      ],
    },
    {
      id: "deck-audit",
      label: "deck-audit",
      stages: [{ id: "hop1", label: "hop1 · source → pages", steps: ["extract-anchors", "audit-source", "audit-report"], artifact: "audit-source.json", standard: "hop1" }],
    },
  ],
  laterSkills: [
    { id: "mdpages2htmlslides", label: "mdpages2htmlslides", note: "批准 page pack 后渲染" },
    { id: "deck-audit", label: "deck-audit hop2", note: "pages → HTML" },
  ],
  steps: LONG4H_STAGES,
};

const SLIDES = {
  id: "long4hslides-slides",
  title: "long4hslides · 批准文件包 → HTML",
  description: "读取已批准的 deck-plan.json，渲染、用 Chrome 测量布局并跑 hop2。",
  needs: ["work"],
  mechanicalDraft: false,
  completeWhen: "slides",
  public: false,
  skills: [
    {
      id: "mdpages2htmlslides",
      label: "mdpages2htmlslides",
      stages: [
        { id: "render", label: "render GF plan", steps: ["render-slides"], artifact: "slides/deck.html" },
        { id: "measure", label: "rendered layout gate", steps: ["gate-layout"], artifact: "audit-layout.json" },
      ],
    },
    {
      id: "deck-audit",
      label: "deck-audit",
      stages: [{ id: "hop2", label: "hop2 · pages → HTML", steps: ["audit-html", "audit-report-2"], artifact: "audit-html.json", standard: "hop2" }],
    },
  ],
  steps: [
    { id: "gate-schema", label: "schema gate", phase: 1 },
    { id: "render-slides", label: "render-deck", phase: 2 },
    { id: "gate-layout", label: "Chrome layout gate", phase: 2 },
    { id: "audit-html", label: "hop2 · pages → HTML", phase: 3, standard: "hop2" },
    { id: "audit-report-2", label: "hop2 report", phase: 3, standard: "hop2" },
  ],
};

export const TEMPLATES = {
  long4hslides: LONG4H,
  "long4hslides-slides": SLIDES,
  "repo-sync": {
    id: "repo-sync",
    title: "Sync vendor + catalog + gates",
    description: "sync-vendor → build-catalog → lint-skills → scan-secrets.",
    needs: [],
    mechanicalDraft: false,
    steps: [
      { id: "sync-vendor", label: "sync-vendor.sh" },
      { id: "build-catalog", label: "build-catalog.py" },
      { id: "lint-skills", label: "lint-skills.py" },
      { id: "scan-secrets", label: "scan-secrets.sh" },
    ],
  },
  "install-links": {
    id: "install-links",
    title: "Install skill symlinks",
    description: "Symlink authored skills into agent skill homes.",
    needs: [],
    mechanicalDraft: false,
    steps: [{ id: "install-links", label: "install-links.sh" }],
  },
};

const ALIASES = {
  "longdoc-to-deck": "long4hslides",
  longdoc2mdpages: "long4hslides",
  alongslides: "long4hslides",
  "baslide-slides": "long4hslides-slides",
  "deck-audit-hop2": "long4hslides-slides",
};

export function listTemplates() {
  return Object.values(TEMPLATES).filter((template) => template.public !== false);
}

export function getTemplate(id) {
  return TEMPLATES[ALIASES[id] || id] || null;
}

const DEFAULT_STANDARDS = { "fit-overfull": true, hop1: true, hop2: false };

export function normalizeStandards(raw) {
  const source = raw && typeof raw === "object" ? raw : {};
  return {
    "fit-overfull": source["fit-overfull"] !== false,
    hop1: source.hop1 !== false,
    hop2: source.hop2 === true,
  };
}

export function stepsFor(templateId, standards) {
  const template = getTemplate(templateId);
  if (!template) return [];
  const selected = { ...DEFAULT_STANDARDS, ...normalizeStandards(standards) };
  return template.steps.filter((step) => !step.standard || selected[step.standard]);
}

export function resolveStep(stepId, ctx) {
  const py = process.env.PYTHON || "python3";
  const work = ctx.workAbs;
  const source = ctx.sourceAbs;
  const html = ctx.htmlAbs || (work && join(work, "slides/deck.html"));
  if (stepId === "normalize-source" && !source) throw new Error("source required");
  if (stepId === "audit-html" && !html) throw new Error("html required");
  if (!work && !["sync-vendor", "build-catalog", "lint-skills", "scan-secrets", "install-links"].includes(stepId)) {
    throw new Error("work required");
  }

  const scripts = {
    "normalize-source": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/longdoc2mdpages/scripts/normalize-source.py"), source, "--work", work] }),
    segment: () => ({ cmd: py, args: [join(REPO_ROOT, "skills/longdoc2mdpages/scripts/segment.py"), join(work, "source.md"), "-o", work] }),
    "coverage-index": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/longdoc2mdpages/scripts/check-coverage.py"), "--stage", "index", "--work", work] }),
    bootstrap: () => ({ cmd: py, args: [join(REPO_ROOT, "skills/longdoc2mdpages/scripts/acceptance-bootstrap.py"), "--work", work] }),
    "estimate-fit": () => {
      const args = [join(REPO_ROOT, "skills/longdoc2mdpages/scripts/estimate-fit.py"), "--work", work, "--write"];
      if (ctx.failOnOverfull !== false) args.push("--fail-on", "overfull");
      return { cmd: py, args };
    },
    "coverage-deck": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/longdoc2mdpages/scripts/check-coverage.py"), "--stage", "deck", "--work", work] }),
    "extract-anchors": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/deck-audit/scripts/extract-anchors.py"), "--work", work] }),
    "audit-source": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/deck-audit/scripts/audit-source.py"), "--work", work] }),
    "audit-html": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/deck-audit/scripts/audit-html.py"), "--work", work, "--html", html, "--dump-slides", join(work, "slides.json")] }),
    "audit-report": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/deck-audit/scripts/audit-report.py"), "--work", work] }),
    "audit-report-2": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/deck-audit/scripts/audit-report.py"), "--work", work] }),
    "emit-pack": () => {
      const args = [join(REPO_ROOT, "skills/longdoc2mdpages/scripts/emit-pack.py"), "--work", work, "--skin", ctx.theme || "TIANSIGHT", "--genre", ctx.genre || "diagnosis"];
      if (ctx.failOnOverfull === false) args.push("--allow-overfull");
      return { cmd: py, args };
    },
    "budget-plan": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/longdoc2mdpages/scripts/budget.py"), join(work, "deck-plan.json")] }),
    "gate-fidelity": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/longdoc2mdpages/scripts/gate_fidelity.py"), "--units", join(work, "units.json"), "--plan", join(work, "deck-plan.json"), "--assets", join(work, "assets/tables"), "--out", join(work, "fidelity.json")] }),
    "gate-schema": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/mdpages2htmlslides/scripts/gate_schema.py"), "--plan", join(work, "deck-plan.json"), "--out", join(work, "schema-report.json")] }),
    "render-slides": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/mdpages2htmlslides/scripts/render-deck.py"), "--work", work, "--theme", ctx.theme || "TIANSIGHT", "--baslide", ctx.baslide || BASLIDE_ROOT, "-o", join(work, "slides/deck.html")] }),
    "gate-layout": () => ({ cmd: py, args: [join(REPO_ROOT, "skills/mdpages2htmlslides/scripts/gate_layout.py"), "--html", join(work, "slides/deck.html"), "--design", join(REPO_ROOT, "skills/mdpages2htmlslides/design"), "--out", join(work, "audit-layout.json")] }),
    "sync-vendor": () => ({ cmd: "bash", args: [join(REPO_ROOT, "scripts/sync-vendor.sh")] }),
    "build-catalog": () => ({ cmd: py, args: [join(REPO_ROOT, "scripts/build-catalog.py")] }),
    "lint-skills": () => ({ cmd: py, args: [join(REPO_ROOT, "scripts/lint-skills.py")] }),
    "scan-secrets": () => ({ cmd: "bash", args: [join(REPO_ROOT, "scripts/scan-secrets.sh"), join(REPO_ROOT, "skills")] }),
    "install-links": () => ({ cmd: "bash", args: [join(REPO_ROOT, "scripts/install-links.sh")] }),
  };
  const build = scripts[stepId];
  if (!build) throw new Error(`unknown step: ${stepId}`);
  return { ...build(), cwd: REPO_ROOT, stepId };
}
