import { join } from "node:path";
import { REPO_ROOT, BASLIDE_ROOT } from "./paths.js";

/**
 * Allowlisted pipeline templates. Each step is a named recipe resolved by jobs.js.
 * No free-form shell.
 */
export const TEMPLATES = {
  "longdoc-to-deck": {
    id: "longdoc-to-deck",
    title: "Long doc → deck material",
    description:
      "Segment → coverage(index) → mechanical bootstrap (draft) → fit → coverage(deck) → hop1 audit. Stages b/c need agent curation after.",
    needs: ["source", "work"],
    mechanicalDraft: true,
    steps: [
      { id: "segment", label: "segment.py" },
      { id: "coverage-index", label: "coverage · index" },
      { id: "bootstrap", label: "acceptance-bootstrap (mechanical)", mechanical: true },
      { id: "estimate-fit", label: "estimate-fit --fail-on overfull" },
      { id: "coverage-deck", label: "coverage · deck" },
      { id: "extract-anchors", label: "extract-anchors" },
      { id: "audit-source", label: "audit-source (hop1)" },
      { id: "audit-report", label: "audit-report" },
    ],
  },
  "deck-audit-hop2": {
    id: "deck-audit-hop2",
    title: "Deck audit hop2 (pages → HTML)",
    description: "audit-html.py with slides dump → audit-report.",
    needs: ["work", "html"],
    mechanicalDraft: false,
    steps: [
      { id: "audit-html", label: "audit-html --dump-slides" },
      { id: "audit-report", label: "audit-report" },
    ],
  },
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
    description: "Symlink authored skills into ~/.cursor|claude|codex/skills.",
    needs: [],
    mechanicalDraft: false,
    steps: [{ id: "install-links", label: "install-links.sh" }],
  },
  alongslides: {
    id: "alongslides",
    title: "Alongslides · longdoc → themed slides",
    description:
      "Four phases: material (segment/bootstrap/fit) → hop1 audit → TIANSIGHT render → hop2 audit. Theme + standards selected at project create.",
    needs: ["source", "work"],
    mechanicalDraft: true,
    phases: 4,
    steps: [
      { id: "segment", label: "segment.py", phase: 1 },
      { id: "coverage-index", label: "coverage · index", phase: 1 },
      { id: "bootstrap", label: "acceptance-bootstrap (mechanical)", mechanical: true, phase: 1 },
      { id: "estimate-fit", label: "estimate-fit", phase: 1, standard: "fit-overfull" },
      { id: "coverage-deck", label: "coverage · deck", phase: 1 },
      { id: "extract-anchors", label: "extract-anchors", phase: 2, standard: "hop1" },
      { id: "audit-source", label: "audit-source (hop1)", phase: 2, standard: "hop1" },
      { id: "audit-report", label: "audit-report", phase: 2, standard: "hop1" },
      { id: "render-slides", label: "render-deck (theme)", phase: 3 },
      { id: "audit-html", label: "audit-html hop2", phase: 4, standard: "hop2" },
      { id: "audit-report-2", label: "audit-report (hop2)", phase: 4, standard: "hop2" },
    ],
  },
};

export function listTemplates() {
  return Object.values(TEMPLATES);
}

export function getTemplate(id) {
  return TEMPLATES[id] || null;
}

const DEFAULT_STANDARDS = { "fit-overfull": true, hop1: true, hop2: true };

export function normalizeStandards(raw) {
  const src = raw && typeof raw === "object" ? raw : {};
  return {
    "fit-overfull": src["fit-overfull"] !== false,
    hop1: src.hop1 !== false,
    hop2: src.hop2 !== false,
  };
}

/** Filter template steps by project standards (gates). Render always stays. */
export function stepsFor(templateId, standards) {
  const tpl = getTemplate(templateId);
  if (!tpl) return [];
  const std = { ...DEFAULT_STANDARDS, ...normalizeStandards(standards) };
  return tpl.steps.filter((s) => {
    if (!s.standard) return true;
    return !!std[s.standard];
  });
}

/** Resolve a step id + project context into {cmd, args, cwd, label}. */
export function resolveStep(stepId, ctx) {
  const py = process.env.PYTHON || "python3";
  const work = ctx.workAbs;
  const source = ctx.sourceAbs;
  const html = ctx.htmlAbs;

  if (["segment"].includes(stepId) && !source) throw new Error("source required");
  if (["audit-html"].includes(stepId) && !html) throw new Error("html required");
  if (
    [
      "segment",
      "coverage-index",
      "bootstrap",
      "estimate-fit",
      "coverage-deck",
      "extract-anchors",
      "audit-source",
      "audit-html",
      "audit-report",
      "audit-report-2",
      "render-slides",
    ].includes(stepId) &&
    !work
  ) {
    throw new Error("work required");
  }

  /** @type {Record<string, () => {cmd:string,args:string[]}>} */
  const builders = {
    segment: () => ({
      cmd: py,
      args: [join(REPO_ROOT, "skills/longdoc-to-deck/scripts/segment.py"), source, "-o", work],
    }),
    "coverage-index": () => ({
      cmd: py,
      args: [
        join(REPO_ROOT, "skills/longdoc-to-deck/scripts/check-coverage.py"),
        "--stage",
        "index",
        "--work",
        work,
      ],
    }),
    bootstrap: () => ({
      cmd: py,
      args: [join(REPO_ROOT, "skills/longdoc-to-deck/scripts/acceptance-bootstrap.py"), "--work", work],
    }),
    "estimate-fit": () => {
      const args = [
        join(REPO_ROOT, "skills/longdoc-to-deck/scripts/estimate-fit.py"),
        "--work",
        work,
        "--write",
      ];
      if (ctx.failOnOverfull !== false) args.push("--fail-on", "overfull");
      return { cmd: py, args };
    },
    "coverage-deck": () => ({
      cmd: py,
      args: [
        join(REPO_ROOT, "skills/longdoc-to-deck/scripts/check-coverage.py"),
        "--stage",
        "deck",
        "--work",
        work,
      ],
    }),
    "extract-anchors": () => ({
      cmd: py,
      args: [join(REPO_ROOT, "skills/deck-audit/scripts/extract-anchors.py"), "--work", work],
    }),
    "audit-source": () => ({
      cmd: py,
      args: [join(REPO_ROOT, "skills/deck-audit/scripts/audit-source.py"), "--work", work],
    }),
    "audit-html": () => ({
      cmd: py,
      args: [
        join(REPO_ROOT, "skills/deck-audit/scripts/audit-html.py"),
        "--work",
        work,
        "--html",
        html,
        "--dump-slides",
        join(work, "slides.json"),
      ],
    }),
    "audit-report": () => ({
      cmd: py,
      args: [join(REPO_ROOT, "skills/deck-audit/scripts/audit-report.py"), "--work", work],
    }),
    "audit-report-2": () => ({
      cmd: py,
      args: [join(REPO_ROOT, "skills/deck-audit/scripts/audit-report.py"), "--work", work],
    }),
    "render-slides": () => ({
      cmd: py,
      args: [
        join(REPO_ROOT, "skills/md-to-html-slides/scripts/render-deck.py"),
        "--work",
        work,
        "--theme",
        ctx.theme || "TIANSIGHT",
        "--baslide",
        ctx.baslide || BASLIDE_ROOT,
        "-o",
        join(work, "slides/deck.html"),
      ],
    }),
    "sync-vendor": () => ({
      cmd: "bash",
      args: [join(REPO_ROOT, "scripts/sync-vendor.sh")],
    }),
    "build-catalog": () => ({
      cmd: py,
      args: [join(REPO_ROOT, "scripts/build-catalog.py")],
    }),
    "lint-skills": () => ({
      cmd: py,
      args: [join(REPO_ROOT, "scripts/lint-skills.py")],
    }),
    "scan-secrets": () => ({
      cmd: "bash",
      args: [join(REPO_ROOT, "scripts/scan-secrets.sh"), join(REPO_ROOT, "skills")],
    }),
    "install-links": () => ({
      cmd: "bash",
      args: [join(REPO_ROOT, "scripts/install-links.sh")],
    }),
  };
  const build = builders[stepId];
  if (!build) throw new Error(`unknown step: ${stepId}`);
  return { ...build(), cwd: REPO_ROOT, stepId };
}
