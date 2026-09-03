import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { basename, join } from "node:path";
import { safeWorkDir, relToRepo } from "./paths.js";
import { getTemplate } from "./templates.js";
import { PACK_FOLDERS, resolvePackSource } from "./archive.js";

function readJsonSafe(p) {
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

/** Primary developable-pack files. HTML slides are not part of pack completion. */
export const PACK_OUTPUTS = [
  { id: "deck-plan.json", label: "deck-plan.json · GF4p2slides 开发输入", primary: true },
  { id: "deck.json", label: "deck.json · 分页素材", primary: true },
  { id: "pages/", label: "pages/ · 每页 Markdown", primary: true, dir: "pages" },
  { id: "outline.md", label: "outline.md · 零损失大纲", primary: true },
  { id: "index.json", label: "index.json · 单元账本", primary: true },
  { id: "units.json", label: "units.json · 单元全文", primary: true },
  { id: "index.md", label: "index.md · 单元目录", primary: true },
  { id: "MANIFEST.md", label: "MANIFEST.md · 包说明", primary: true },
  { id: "pack.json", label: "pack.json · 包清单", primary: true },
  { id: "source-manifest.json", label: "source-manifest.json · 来源与排序", primary: false },
  { id: "assets/tables/", label: "assets/tables/ · 附录表格", primary: false, dir: "assets/tables" },
  { id: "anchors.json", label: "anchors.json · hop1 锚点", primary: false },
  { id: "audit-source.json", label: "audit-source.json · hop1 结果", primary: false },
  { id: "audit.md", label: "audit.md · 校对报告", primary: false },
];

const STAGE_ARTIFACT = {
  "a-segment": "index.json",
  "b-outline": "outline.md",
  "c-pagination": "deck.json",
  "d-emit": "pack.json",
  hop1: "audit-source.json",
  hop2: "audit-html.json",
  render: "slides/deck.html",
};

function fileMeta(abs, relName) {
  if (relName.endsWith("/")) {
    const dir = join(abs, relName.slice(0, -1));
    if (!existsSync(dir)) return { present: false, count: 0, bytes: 0 };
    const files = readdirSync(dir).filter((f) => !f.startsWith("."));
    return { present: true, count: files.length, bytes: 0 };
  }
  const p = join(abs, relName);
  if (!existsSync(p)) return { present: false, count: 0, bytes: 0 };
  try {
    return { present: true, count: 1, bytes: statSync(p).size };
  } catch {
    return { present: true, count: 1, bytes: 0 };
  }
}

export function getPack(runId) {
  if (!runId) return null;
  let abs;
  try {
    abs = safeWorkDir(runId);
  } catch {
    return null;
  }
  if (!existsSync(abs)) return null;
  const packJson = readJsonSafe(join(abs, "pack.json"));
  const plan = readJsonSafe(join(abs, "deck-plan.json")) || readJsonSafe(join(abs, "slide-plan.json"));
  const fidelity = readJsonSafe(join(abs, "fidelity.json"));
  const schema = readJsonSafe(join(abs, "schema-report.json"));
  const files = PACK_OUTPUTS.map((spec) => {
    const meta = fileMeta(abs, spec.dir ? `${spec.dir}/` : spec.id);
    return {
      ...spec,
      ...meta,
      path: relToRepo(join(abs, spec.dir || spec.id)),
    };
  });
  const primary = files.filter((f) => f.primary);
  const gatesPassed =
    packJson?.version !== "2.0" ||
    (fidelity?.hard === 0 && schema?.hard === 0);
  const ready = packJson?.ready === true && gatesPassed && primary.filter((f) => f.id !== "pack.json").every((f) => f.present);
  return {
    ready,
    path: relToRepo(abs),
    counts: packJson?.counts || null,
    fill_counts: packJson?.fill_counts || plan?.fill_counts || {},
    genre: packJson?.genre || plan?.genre || null,
    skin: packJson?.skin || plan?.theme || plan?.skin || null,
    emitted_at: packJson?.emitted_at || null,
    files,
    manifest: files.find((f) => f.id === "MANIFEST.md")?.present || false,
    slides: presentAt(abs, "slides/deck.html") && presentAt(abs, "slides/deck.pdf"),
  };
}

function latestGateByStep(history) {
  const map = {};
  for (const g of history || []) {
    map[g.step] = g;
  }
  return map;
}

/** Clickable studio stages. Current project goal stops at pages, not HTML slides. */
export const VIEW_STAGES = [
  {
    id: "source",
    label: "0 · 原文",
    skill: "source",
    goal: "原始长文档",
    later: false,
  },
  {
    id: "a-segment",
    label: "1 · segment",
    skill: "longdoc2mdpages",
    goal: "切成单元账本，零损失",
    later: false,
  },
  {
    id: "b-outline",
    label: "2 · outline",
    skill: "longdoc2mdpages",
    goal: "大纲覆盖每一个 unit",
    later: false,
  },
  {
    id: "c-pagination",
    label: "3 · pages",
    skill: "longdoc2mdpages",
    goal: "拆成可开发的页面素材（还不是 slides）",
    later: false,
  },
  {
    id: "d-emit",
    label: "4 · pack",
    skill: "longdoc2mdpages",
    goal: "deck-plan + 文件包清单",
    later: false,
  },
  {
    id: "hop1",
    label: "审计 · hop1",
    skill: "deck-audit",
    goal: "原文 → 页面保真",
    later: false,
  },
  {
    id: "slides",
    label: "下一步 · slides",
    skill: "mdpages2htmlslides",
    goal: "Baslide01 HTML，文件包完成之后才做",
    later: true,
  },
];

function presentAt(abs, rel) {
  return existsSync(join(abs, rel));
}

export function stageReady(abs, stageId, { pack = null, source = null } = {}) {
  if (stageId === "source") {
    if (source) return true;
    if (abs && presentAt(abs, "index.json")) {
      const index = readJsonSafe(join(abs, "index.json"));
      return Boolean(index?.source);
    }
    return false;
  }
  if (!abs) return false;
  if (stageId === "a-segment") return presentAt(abs, "index.json");
  if (stageId === "b-outline") return presentAt(abs, "outline.md");
  if (stageId === "c-pagination") return presentAt(abs, "deck.json") && presentAt(abs, "pages");
  if (stageId === "d-emit") return pack?.ready === true;
  if (stageId === "hop1") return presentAt(abs, "audit-source.json");
  if (stageId === "slides") return presentAt(abs, "slides/deck.html") && presentAt(abs, "slides/deck.pdf");
  return !!(pack && pack.ready);
}

export function getStageView(runId, stageId, { source = null } = {}) {
  let abs = null;
  try {
    abs = runId ? safeWorkDir(runId) : null;
  } catch {
    abs = null;
  }
  const spec = VIEW_STAGES.find((s) => s.id === stageId) || VIEW_STAGES.find((s) => s.id === "c-pagination");
  const items = [];
  if (spec.id === "source") {
    let src = source;
    if (!src && abs && presentAt(abs, "index.json")) {
      src = readJsonSafe(join(abs, "index.json"))?.source || null;
    }
    if (src) {
      items.push({ id: "source", kind: "file", label: String(src).split("/").pop(), path: src, sub: "原文" });
    }
  } else if (abs && spec.id === "a-segment") {
    const index = readJsonSafe(join(abs, "index.json"));
    for (const u of index?.units || []) {
      items.push({
        id: u.id,
        kind: "unit",
        label: u.id,
        sub: (u.digest || "").replace(/\s+/g, " ").slice(0, 80),
        meta: u.kind,
        path: u.heading_path || [],
        chapters: u.heading_path || [],
      });
    }
    if (presentAt(abs, "index.md")) {
      items.unshift({ id: "index.md", kind: "file", label: "index.md", path: relToRepo(join(abs, "index.md")), sub: "单元目录" });
    }
  } else if (abs && spec.id === "b-outline") {
    if (presentAt(abs, "outline.md")) {
      items.push({ id: "outline.md", kind: "file", label: "outline.md", path: relToRepo(join(abs, "outline.md")), sub: "零损失大纲" });
    }
  } else if (abs && spec.id === "c-pagination") {
    const deck = readJsonSafe(join(abs, "deck.json"));
    for (const p of deck?.pages || []) {
      items.push({
        id: p.id,
        kind: "page",
        label: p.id,
        sub: p.title || "",
        meta: p.role,
        path: p.outline_path || [],
        chapters: p.outline_path || [],
      });
    }
  } else if (abs && spec.id === "d-emit") {
    const manifest = fileMeta(abs, "MANIFEST.md");
    if (manifest.present) {
      items.push({
        id: "MANIFEST.md",
        kind: "file",
        label: "MANIFEST.md",
        path: relToRepo(join(abs, "MANIFEST.md")),
        sub: manifest.bytes ? `${Math.round(manifest.bytes / 1024)} KB` : "包说明",
        chapters: ["audit"],
      });
    }
    for (const folder of PACK_FOLDERS) {
      if (folder.source) {
        const src = resolvePackSource(abs, source);
        if (src) {
          items.push({
            id: "source",
            kind: "file",
            label: basename(src),
            path: src,
            sub: "原文",
            chapters: [folder.id],
          });
        }
      }
      if (folder.pages) {
        const meta = fileMeta(abs, "pages/");
        if (meta.present) {
          items.push({
            id: "pages",
            kind: "dir",
            label: "pages/*.md",
            sub: `${meta.count} 页`,
            path: relToRepo(join(abs, "pages")),
            chapters: [folder.id],
          });
        }
      }
      for (const id of folder.files) {
        const meta = fileMeta(abs, id);
        if (!meta.present) continue;
        items.push({
          id,
          kind: "file",
          label: id,
          path: relToRepo(join(abs, id)),
          sub: meta.bytes ? `${Math.round(meta.bytes / 1024)} KB` : folder.title,
          chapters: [folder.id],
        });
      }
    }
  } else if (abs && spec.id === "hop1") {
    if (presentAt(abs, "audit.md")) {
      items.push({ id: "audit.md", kind: "file", label: "audit.md", path: relToRepo(join(abs, "audit.md")), sub: "校对报告" });
    }
    const audit = readJsonSafe(join(abs, "audit-source.json"));
    const byPage = new Map();
    for (const f of audit?.findings || []) {
      if (!f.page) continue;
      const row = byPage.get(f.page) || { id: f.page, kind: "audit", label: f.page, hard: 0, warn: 0 };
      if (f.severity === "hard") row.hard += 1;
      else row.warn += 1;
      byPage.set(f.page, row);
    }
    const deck = readJsonSafe(join(abs, "deck.json"));
    for (const p of deck?.pages || []) {
      const row = byPage.get(p.id) || { id: p.id, kind: "audit", label: p.id, hard: 0, warn: 0 };
      row.sub = p.title || "";
      row.meta = row.hard ? "hard" : row.warn ? "warn" : "ok";
      row.path = p.outline_path || [];
      row.chapters = p.outline_path || [];
      items.push(row);
    }
  } else if (abs && spec.id === "slides") {
    if (presentAt(abs, "slides/deck.html")) {
      const plan = readJsonSafe(join(abs, "deck-plan.json")) || readJsonSafe(join(abs, "slide-plan.json"));
      const packMeta = readJsonSafe(join(abs, "pack.json"));
      const fillCounts = plan?.fill_counts || packMeta?.fill_counts || {};
      let planned = Object.values(fillCounts).reduce((n, v) => n + Number(v || 0), 0);
      if (!planned) planned = Number(packMeta?.counts?.fills || 0);
      let drawn = 0;
      try {
        drawn = (readFileSync(join(abs, "slides/deck.html"), "utf8").match(/<svg\b/gi) || []).length;
      } catch {
        drawn = 0;
      }
      const deck = readJsonSafe(join(abs, "deck.json"));
      const sourcePages = deck?.pages || [];
      const rendered = readJsonSafe(join(abs, "slides.json"))?.slides || [];
      const pages = rendered.length && rendered.length !== sourcePages.length
        ? rendered.map((s, i) => ({
            id: s.id || `slide-${i + 1}`,
            title: s.title || String(s.text || "").trim().split(/\n+/)[0] || `Slide ${i + 1}`,
            role: "slide",
            outline_path: [],
          }))
        : sourcePages;
      const roles = { ...(packMeta?.counts?.roles || {}) };
      if (!Object.keys(roles).length) {
        for (const page of pages) {
          const role = page.role || "other";
          roles[role] = (roles[role] || 0) + 1;
        }
      }
      const stats = {
        slides: pages.length || Number(packMeta?.counts?.pages || 0),
        data: (roles.kpi || 0) + (roles["chart-table"] || 0),
        kpi: roles.kpi || 0,
        tables: roles["chart-table"] || 0,
        viz: pages.filter((page) => page.fill).length || planned,
        vizPlanned: planned,
        vizDrawn: drawn,
        roles,
        fills: fillCounts,
      };
      const viz = { planned, drawn };
      const href = `/slides/${runId}/deck.html`;
      items.push({
        id: "deck.html",
        kind: "html",
        label: "整份 HTML 报告",
        href,
        page: 1,
        viz,
        stats,
        sub: `${stats.slides} 页 · 数据 ${stats.data} · L3 ${stats.vizPlanned}/${stats.vizDrawn}`,
      });
      pages.forEach((p, i) => {
        items.push({
          id: p.id,
          kind: "html",
          label: p.id,
          sub: p.title || "",
          meta: p.fill || p.role,
          href: `${href}#p=${i + 1}`,
          page: i + 1,
          viz,
          stats,
          chapters: p.outline_path || [],
          path: p.outline_path || [],
        });
      });
    }
    if (presentAt(abs, "slides.json")) {
      items.push({
        id: "slides.json",
        kind: "file",
        label: "slides.json",
        path: relToRepo(join(abs, "slides.json")),
        sub: "hop2 抽页",
      });
    }
  }
  return {
    stage: spec,
    ready: stageReady(abs, spec.id, { source }),
    items,
  };
}

export function skillStagesFor(project, pack) {
  const tpl = getTemplate(project.template);
  if (!tpl) return { skills: [], laterSkills: [] };
  const artifacts = {};
  if (pack?.files) {
    for (const f of pack.files) artifacts[f.id] = f.present;
  }
  const gates = latestGateByStep(project.gate_history);
  const decorate = (skill) => ({
    ...skill,
    stages: (skill.stages || []).map((st) => {
      const art = st.artifact || STAGE_ARTIFACT[st.id];
      const fromArt = art ? !!artifacts[art] || (pack && art === "pack.json" && pack.ready) : false;
      const stepHits = (st.steps || []).map((id) => gates[id]?.status).filter(Boolean);
      let status = "pending";
      if (stepHits.includes("fail")) status = "fail";
      else if (fromArt || (stepHits.length && stepHits.every((s) => s === "ok"))) status = "ok";
      else if (stepHits.length) status = "warn";
      return { ...st, status, artifact: art || null };
    }),
  });
  return {
    skills: (tpl.skills || []).map(decorate),
    laterSkills: tpl.laterSkills || [],
  };
}
