import { api, badge, esc } from "./util.js";

const FILTERS = [
  { id: "ksamint", label: "ksamint" },
  { id: "matt", label: "matt" },
  { id: "system", label: "系统 · cc / cursor" },
  { id: "other", label: "其他 vendor" },
];

const SECTION_ORDER = ["ksamint", "matt", "other", "system"];
const SECTION_TITLE = {
  ksamint: "ksamint",
  matt: "matt",
  other: "其他 vendor",
  system: "系统自带 · cc / cursor",
};

export async function renderSkills(root, parts) {
  root.classList.remove("studio-page");
  if (parts[1] && parts[2]) {
    return renderSkillDetail(root, parts[1], decodeURIComponent(parts[2]));
  }
  root.innerHTML = `<p class="muted">Loading skills…</p>`;
  const data = await api("/api/skills");
  const graph = await api("/api/skills/graph").catch(() => ({ nodes: [], edges: [] }));
  const all = [...(data.authored || []), ...(data.vendored || [])];
  const totals = data.totals || {};
  const on = new Set(["ksamint", "matt", "system"]);

  root.innerHTML = `
    <h1>Skills gallery</h1>
    <p class="lede">按作者 / 来源筛选。ksamint 与 matt 在前，Cursor / Claude Code 自带技能在最后。</p>
    <div class="toolbar">
      <input class="search" id="q" placeholder="搜索名称或 SKILL.md…" />
      ${FILTERS.map(
        (f) =>
          `<label class="filter-chip"><input type="checkbox" data-origin="${f.id}" ${on.has(f.id) ? "checked" : ""} /> ${esc(f.label)} <span class="mono muted">${totals[f.id] ?? 0}</span></label>`
      ).join("")}
      <span class="spacer"></span>
      <span class="muted mono">${totals.ksamint ?? 0} ksamint · ${totals.matt ?? 0} matt · ${totals.system ?? 0} 系统 · ${totals.other ?? 0} 其他</span>
    </div>
    <div id="skill-results"></div>
    <h2>Skill graph (ksamint 交叉引用)</h2>
    <div class="card">
      <ul class="graph">
        ${
          graph.edges
            .map((e) => `<li><span class="mono">${esc(e.from)}</span> → <span class="mono">${esc(e.to)}</span></li>`)
            .join("") || `<li class="muted">No cross-references found</li>`
        }
      </ul>
    </div>
  `;

  const results = root.querySelector("#skill-results");

  function activeOrigins() {
    return new Set(
      [...root.querySelectorAll("[data-origin]")]
        .filter((el) => el.checked)
        .map((el) => el.getAttribute("data-origin"))
    );
  }

  function card(s) {
    const ver = s.version?.hash || (s.version?.synced_commit || "").slice(0, 7) || "—";
    const dirty = s.version?.dirty ? badge("warn", "dirty") : "";
    const who = s.agent ? badge("", s.agent) : badge("", s.origin);
    return `<a class="card clickable" href="#/skills/${esc(s.kind)}/${encodeURIComponent(s.folder)}" style="text-decoration:none;color:inherit">
      <div class="row"><h3 style="margin:0">${esc(s.name)}</h3>${who}${dirty}</div>
      <p class="muted" style="margin:.4rem 0;font-size:.88rem">${esc((s.description || "").slice(0, 140))}${(s.description || "").length > 140 ? "…" : ""}</p>
      <div class="mono muted">${esc(s.source)} · ${esc(ver)}</div>
    </a>`;
  }

  function paint(list, origins) {
    const shown = list.filter((s) => origins.has(s.origin || "other"));
    const blocks = SECTION_ORDER.filter((id) => origins.has(id))
      .map((id) => {
        const rows = shown.filter((s) => s.origin === id);
        if (!rows.length) return "";
        return `<h2>${esc(SECTION_TITLE[id])} <span class="mono muted">${rows.length}</span></h2>
          <div class="grid grid-3">${rows.map(card).join("")}</div>`;
      })
      .join("");
    results.innerHTML = blocks || `<div class="empty">没有命中当前筛选。</div>`;
  }

  paint(all, activeOrigins());

  function refresh() {
    const q = root.querySelector("#q").value.trim();
    const origins = activeOrigins();
    if (!q) {
      paint(all, origins);
      return;
    }
    api(`/api/skills/search?q=${encodeURIComponent(q)}`).then(({ hits }) => {
      paint(
        (hits || []).map((s) => ({
          ...s,
          origin: s.origin || (s.kind === "authored" ? "ksamint" : "other"),
        })),
        origins
      );
    });
  }

  root.querySelectorAll("[data-origin]").forEach((el) => {
    el.addEventListener("change", refresh);
  });

  let searchTimer;
  root.querySelector("#q").addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(refresh, 220);
  });
}

async function renderSkillDetail(root, kind, id) {
  root.classList.remove("studio-page");
  root.innerHTML = `<p class="muted">Loading…</p>`;
  const s = await api(`/api/skills/${encodeURIComponent(kind)}/${encodeURIComponent(id)}`);
  const treeHtml = (nodes, depth = 0) =>
    nodes
      .map((n) => {
        if (n.type === "dir") {
          return `<div style="margin-left:${depth * 12}px">📁 ${esc(n.name)}${treeHtml(n.children || [], depth + 1)}</div>`;
        }
        return `<div style="margin-left:${depth * 12}px">· ${esc(n.name)} <span class="muted">${n.size}b</span></div>`;
      })
      .join("");

  const extras = s.runtime || [];
  root.innerHTML = `
    <div class="row"><a class="btn ghost" href="#/skills">← gallery</a><span class="spacer"></span>
      ${badge("", s.origin || s.kind)} ${s.agent ? badge("", s.agent) : ""} ${(s.installTargets || []).map((t) => badge("ok", `装到 ${t}`)).join("")}
      ${s.zip ? `<a class="btn" href="${esc(s.zip)}">下载 skill 包</a>` : ""}
    </div>
    <h1>${esc(s.name)}</h1>
    <p class="lede">${esc(s.description)}</p>
    <p class="muted">导出是整包 zip（${esc(s.zipName || "skill.zip")}），不是单份 SKILL.md。${
      extras.length ? "下面 runtime 会一并打进压缩包。" : ""
    }</p>
    <div class="grid grid-2">
      <div class="card">
        <h3>Meta</h3>
        <div class="mono">path: ${esc(s.path)}</div>
        <div class="mono">source: ${esc(s.source)}</div>
        <div class="mono">origin: ${esc(s.origin || "—")} ${s.agent ? `· ${esc(s.agent)}` : ""}</div>
        <div class="mono">version: ${esc(s.version?.hash || s.version?.synced_commit || "—")} ${s.version?.dirty ? badge("warn", "dirty") : ""}</div>
        <div class="mono">license: ${esc(s.license || "—")}</div>
        ${
          extras.length
            ? `<h3 style="margin-top:1rem">Zip 另含 runtime</h3><ul>${extras
                .map((e) => `<li class="mono">${esc(e.to)} <span class="muted">${esc(e.why)}</span></li>`)
                .join("")}</ul>`
            : ""
        }
        <h3 style="margin-top:1rem">Tree</h3>
        <div class="mono" style="font-size:.75rem">${treeHtml(s.tree || [])}</div>
      </div>
      <div class="card">
        <h3>SKILL.md</h3>
        <pre class="pre light">${esc(s.raw)}</pre>
      </div>
    </div>
  `;
}
