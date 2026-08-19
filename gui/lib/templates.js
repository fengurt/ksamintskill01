import { join } from "node:path";
import { REPO_ROOT } from "./paths.js";

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
};

export function listTemplates() {
  return Object.values(TEMPLATES);
}

export function getTemplate(id) {
  return TEMPLATES[id] || null;
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
    "estimate-fit": () => ({
      cmd: py,
      args: [
        join(REPO_ROOT, "skills/longdoc-to-deck/scripts/estimate-fit.py"),
        "--work",
        work,
        "--write",
        "--fail-on",
        "overfull",
      ],
    }),
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
