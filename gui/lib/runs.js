import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, basename } from "node:path";
import { WORK_DIR, safeWorkDir, relToRepo } from "./paths.js";

const ARTIFACTS = [
  "index.json",
  "index.md",
  "units.json",
  "outline.md",
  "deck.json",
  "anchors.json",
  "audit-source.json",
  "audit-html.json",
  "audit.md",
  "slides.json",
  "fit-report.json",
  "slide-plan.json",
  "pack.json",
  "MANIFEST.md",
  "slides/deck.html",
];

function mtime(p) {
  try {
    return statSync(p).mtimeMs;
  } catch {
    return null;
  }
}

export function listRuns() {
  if (!existsSync(WORK_DIR)) return [];
  return readdirSync(WORK_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => {
      const abs = join(WORK_DIR, d.name);
      const present = {};
      for (const a of ARTIFACTS) present[a] = existsSync(join(abs, a));
      let pages = 0;
      const pagesDir = join(abs, "pages");
      if (existsSync(pagesDir)) {
        pages = readdirSync(pagesDir).filter((f) => f.endsWith(".md")).length;
      }
      let summary = {};
      try {
        if (present["index.json"]) {
          const idx = JSON.parse(readFileSync(join(abs, "index.json"), "utf8"));
          summary.total_units = idx.total_units;
          summary.kinds = idx.kinds;
          summary.source = idx.source;
        }
      } catch {
        /* */
      }
      try {
        if (present["deck.json"]) {
          const deck = JSON.parse(readFileSync(join(abs, "deck.json"), "utf8"));
          summary.page_count = (deck.pages || []).length;
        }
      } catch {
        /* */
      }
      try {
        if (present["audit-source.json"]) {
          const a = JSON.parse(readFileSync(join(abs, "audit-source.json"), "utf8"));
          summary.hop1 = a.counts;
        }
      } catch {
        /* */
      }
      try {
        if (present["audit-html.json"]) {
          const a = JSON.parse(readFileSync(join(abs, "audit-html.json"), "utf8"));
          summary.hop2 = a.counts;
        }
      } catch {
        /* */
      }
      return {
        id: d.name,
        path: relToRepo(abs),
        mtime: mtime(abs),
        pages,
        artifacts: present,
        summary,
      };
    })
    .sort((a, b) => (b.mtime || 0) - (a.mtime || 0));
}

function readJsonSafe(p) {
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

export function getRun(runId) {
  const abs = safeWorkDir(runId);
  if (!existsSync(abs)) return null;
  const index = readJsonSafe(join(abs, "index.json"));
  const deck = readJsonSafe(join(abs, "deck.json"));
  const auditSource = readJsonSafe(join(abs, "audit-source.json"));
  const auditHtml = readJsonSafe(join(abs, "audit-html.json"));
  const slides = readJsonSafe(join(abs, "slides.json"));
  let outline = null;
  if (existsSync(join(abs, "outline.md"))) {
    outline = readFileSync(join(abs, "outline.md"), "utf8");
  }
  let auditMd = null;
  if (existsSync(join(abs, "audit.md"))) {
    auditMd = readFileSync(join(abs, "audit.md"), "utf8");
  }
  const pageSummaries = (deck?.pages || []).map((p) => ({
    id: p.id,
    role: p.role,
    title: p.title,
    outline_path: p.outline_path || [],
    units: p.units || [],
    overflow_of: p.overflow_of || null,
    fit: p.fit || null,
  }));
  return {
    id: basename(abs),
    path: relToRepo(abs),
    index,
    outline,
    deck: deck
      ? {
          version: deck.version,
          source: deck.source,
          page_count: (deck.pages || []).length,
          pages: pageSummaries,
        }
      : null,
    auditSource: auditSource
      ? { counts: auditSource.counts, findings: auditSource.findings || [] }
      : null,
    auditHtml: auditHtml
      ? {
          counts: auditHtml.counts,
          mapping: auditHtml.mapping || {},
          map_notes: auditHtml.map_notes || [],
          findings: auditHtml.findings || [],
          html: auditHtml.html,
        }
      : null,
    slides: slides?.slides || null,
    deckHtml: existsSync(join(abs, "slides/deck.html")),
    deckHref: existsSync(join(abs, "slides/deck.html")) ? `/slides/${basename(abs)}/deck.html` : null,
    auditMd,
  };
}

export function getPageMaterial(runId, pageId) {
  const abs = safeWorkDir(runId);
  const mdPath = join(abs, "pages", `${pageId}.md`);
  if (!existsSync(mdPath)) return null;
  return { id: pageId, markdown: readFileSync(mdPath, "utf8") };
}

export function getUnitTexts(runId, unitIds) {
  const abs = safeWorkDir(runId);
  const units = readJsonSafe(join(abs, "units.json"));
  if (!units) return {};
  const index = readJsonSafe(join(abs, "index.json"));
  const metaById = Object.fromEntries((index?.units || []).map((u) => [u.id, u]));
  const out = {};
  for (const id of unitIds || []) {
    const raw = units[id];
    if (raw == null) continue;
    const meta = metaById[id] || {};
    const text = typeof raw === "string" ? raw : raw.text || raw.body || raw.content || "";
    out[id] = {
      id,
      kind: meta.kind || raw.kind,
      heading_path: meta.heading_path || raw.heading_path,
      text,
      digest: meta.digest || raw.digest,
    };
  }
  return out;
}

/** Build inspector payload for one page: source units, material, slide text, findings. */
export function getAuditPage(runId, pageId) {
  const run = getRun(runId);
  if (!run) return null;
  const page = (run.deck?.pages || []).find((p) => p.id === pageId);
  if (!page) return null;
  const material = getPageMaterial(runId, pageId);
  const units = getUnitTexts(runId, page.units);
  const hop1 = (run.auditSource?.findings || []).filter((f) => f.page === pageId);
  const hop2 = (run.auditHtml?.findings || []).filter((f) => f.page === pageId);
  let slide = null;
  let mapReason = null;
  if (run.slides) {
    slide = run.slides.find((s) => s.mapped_page === pageId) || null;
    mapReason = slide?.map_reason || null;
  } else if (run.auditHtml?.mapping) {
    const entry = Object.entries(run.auditHtml.mapping).find(([, pid]) => pid === pageId);
    if (entry) {
      const slideIdx = Number(entry[0]);
      mapReason =
        (run.auditHtml.map_notes || []).find((n) => n.slide === slideIdx)?.detail || "mapped";
      slide = { slide: slideIdx, mapped_page: pageId, map_reason: mapReason, text: "", title: "" };
    }
  }
  const confidenceRank = {
    "data-page-id": 0,
    id: 1,
    title: 2,
    order: 3,
    ambiguous: 4,
    unmapped: 5,
  };
  return {
    page,
    material: material?.markdown || "",
    units,
    slide,
    map_reason: mapReason || slide?.map_reason || null,
    confidence: confidenceRank[slide?.map_reason] ?? 3,
    findings: { hop1, hop2 },
  };
}

export function listAuditPages(runId) {
  const run = getRun(runId);
  if (!run?.deck) return [];
  const byPage = new Map();
  for (const p of run.deck.pages) {
    byPage.set(p.id, {
      id: p.id,
      title: p.title,
      role: p.role,
      hard: 0,
      warn: 0,
      map_reason: null,
      slide: null,
    });
  }
  if (run.slides) {
    for (const s of run.slides) {
      if (!s.mapped_page || !byPage.has(s.mapped_page)) continue;
      const row = byPage.get(s.mapped_page);
      row.map_reason = s.map_reason;
      row.slide = s.slide;
    }
  } else if (run.auditHtml?.mapping) {
    for (const [si, pid] of Object.entries(run.auditHtml.mapping)) {
      if (!byPage.has(pid)) continue;
      const row = byPage.get(pid);
      row.slide = Number(si);
      const note = (run.auditHtml.map_notes || []).find((n) => n.slide === Number(si));
      row.map_reason = note?.detail?.includes("via ")
        ? note.detail.split("via ").pop()
        : note
          ? "noted"
          : "mapped";
    }
  }
  for (const f of run.auditSource?.findings || []) {
    if (!f.page || !byPage.has(f.page)) continue;
    if (f.severity === "hard") byPage.get(f.page).hard += 1;
    else byPage.get(f.page).warn += 1;
  }
  for (const f of run.auditHtml?.findings || []) {
    if (!f.page || !byPage.has(f.page)) continue;
    if (f.severity === "hard") byPage.get(f.page).hard += 1;
    else byPage.get(f.page).warn += 1;
  }
  const rank = { "data-page-id": 0, id: 1, title: 2, order: 3, ambiguous: 4, unmapped: 5 };
  return [...byPage.values()].sort((a, b) => {
    const ra = rank[a.map_reason] ?? 3;
    const rb = rank[b.map_reason] ?? 3;
    if (ra !== rb) return rb - ra; // worst mapping first
    if (b.hard !== a.hard) return b.hard - a.hard;
    return a.id.localeCompare(b.id);
  });
}

export function agentBrief(runId) {
  const run = getRun(runId);
  if (!run) return null;
  const overfull = (run.deck?.pages || []).filter((p) => p.fit?.verdict === "overfull");
  const starved = (run.deck?.pages || []).filter((p) => p.fit?.verdict === "starved");
  return [
    `# Agent brief — refine outline + pagination`,
    ``,
    `Work dir: \`${run.path}\``,
    `Source: ${run.index?.source || run.deck?.source || "(unknown)"}`,
    `Units: ${run.index?.total_units ?? "?"} · Pages: ${run.deck?.page_count ?? "?"}`,
    ``,
    `The current outline.md and deck.json were produced by **acceptance-bootstrap.py**`,
    `(mechanical draft, not curated). Please:`,
    ``,
    `1. Rewrite \`outline.md\` so every unit id appears exactly once, mirroring document structure + mermaid mindmap.`,
    `2. Re-paginate into \`deck.json\` + \`pages/p-NNNN.md\` following pagination.md + budgets.json.`,
    `3. Run:`,
    `   python3 skills/longdoc-to-deck/scripts/estimate-fit.py --work ${run.path} --write --fail-on overfull`,
    `   python3 skills/longdoc-to-deck/scripts/check-coverage.py --stage outline --work ${run.path}`,
    `   python3 skills/longdoc-to-deck/scripts/check-coverage.py --stage deck --work ${run.path}`,
    `   python3 skills/deck-audit/scripts/audit-source.py --work ${run.path}`,
    `   python3 skills/deck-audit/scripts/audit-report.py --work ${run.path}`,
    ``,
    `Current fit: overfull=${overfull.length} starved=${starved.length}`,
    overfull.length
      ? `Overfull pages: ${overfull
          .slice(0, 12)
          .map((p) => p.id)
          .join(", ")}${overfull.length > 12 ? "…" : ""}`
      : "",
    ``,
    `Hop1 hard: ${run.auditSource?.counts?.hard ?? "—"} · Hop2 hard: ${run.auditHtml?.counts?.hard ?? "—"}`,
  ]
    .filter((l) => l !== "")
    .join("\n");
}
