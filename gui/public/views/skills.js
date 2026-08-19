import { api, badge, esc, fmtTime } from "./util.js";

const FILTERS = [
  { id: "ksamint", label: "ksamint" },
  { id: "ksa", label: "KSA MAT" },
  { id: "matt", label: "matt" },
  { id: "system", label: "系统 · cc / cursor" },
  { id: "other", label: "其他 vendor" },
];

export async function renderSkills(root, parts) {
  root.classList.remove("studio-page");
  if (parts[1] && parts[2]) {
    return renderSkillDetail(root, parts[1], decodeURIComponent(parts[2]));
  }
  root.innerHTML = `<p class="muted">Loading skills…</p>`;
  const data = await api("/api/skills");
  const graph = await api("/api/skills/graph").catch(() => ({ nodes: [], edges: [] }));
  const all = data.items || [...(data.authored || []), ...(data.vendored || [])];
  const totals = data.totals || {};
  const on = new Set(["ksamint", "ksa", "matt", "system"]);
  const copyNote =
    totals.copies && totals.unique && totals.copies !== totals.unique
      ? ` · ${totals.unique} 条（${totals.copies} 份收成一条）`
      : "";

  root.innerHTML = `
    <h1>Skills gallery</h1>
    <p class="lede">同一 name 只记一条（本仓库优先）。星标和导出都打这条。</p>
    <div class="toolbar">
      <input class="search" id="q" placeholder="搜索名称或 SKILL.md…" />
      ${FILTERS.map(
        (f) =>
          `<label class="filter-chip"><input type="checkbox" data-origin="${f.id}" ${on.has(f.id) ? "checked" : ""} /> ${esc(f.label)} <span class="mono muted">${totals[f.id] ?? 0}</span></label>`
      ).join("")}
      <a class="btn ghost" id="export-starred" href="/api/skills/export.zip?starred=1" hidden>导出星标</a>
      <span class="spacer"></span>
      <span class="muted mono">${totals.ksamint ?? 0} ksamint · ${totals.ksa ?? 0} KSA MAT · ${totals.matt ?? 0} matt · ${totals.system ?? 0} 系统 · ${totals.other ?? 0} 其他${copyNote}</span>
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
    const dirty = s.version?.dirty ? badge("warn", "dirty") : "";
    const who = s.agent ? badge("", s.agent) : badge("", s.origin);
    const copies = (s.copies || []).length;
    const href = `#/skills/${esc(s.kind)}/${encodeURIComponent(s.folder)}`;
    const id = esc(s.id || s.name);
    return `<article class="card skill-card">
      <div class="row">
        <button type="button" class="star ${s.starred ? "on" : ""}" data-star="${id}" title="星标">★</button>
        <a class="skill-card-title" href="${href}"><h3 style="margin:0">${esc(s.name)}</h3></a>
        ${who}${dirty}${copies > 1 ? badge("", `${copies} 处`) : ""}
        <span class="spacer"></span>
        ${s.zip ? `<a class="btn ghost skill-export" href="${esc(s.zip)}" download="${esc(s.zipName || `${s.name}-skill.zip`)}">导出</a>` : ""}
      </div>
      <a class="skill-card-body" href="${href}">
        <p class="muted" style="margin:.4rem 0;font-size:.88rem">${esc((s.description || "").slice(0, 140))}${(s.description || "").length > 140 ? "…" : ""}</p>
        <div class="mono muted">${esc(s.author || s.origin)} · ${esc(s.repo || s.source)} · ${esc(fmtTime(s.updatedAt))}</div>
      </a>
    </article>`;
  }

  function paint(list, origins) {
    const shown = [...list]
      .filter((s) => origins.has(s.origin || "other"))
      .sort((a, b) => {
        if (!!b.starred !== !!a.starred) return a.starred ? -1 : 1;
        return (b.updatedAt || 0) - (a.updatedAt || 0);
      });
    const starred = shown.filter((s) => s.starred);
    const rest = shown.filter((s) => !s.starred);
    const block = (title, rows) =>
      rows.length
        ? `<h2>${esc(title)} <span class="mono muted">${rows.length}</span></h2><div class="grid grid-3">${rows.map(card).join("")}</div>`
        : "";
    results.innerHTML =
      block("星标", starred) + block("按更新", rest) || `<div class="empty">没有命中当前筛选。</div>`;
    results.querySelectorAll("[data-star]").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.preventDefault();
        e.stopPropagation();
        const key = btn.getAttribute("data-star");
        const out = await api("/api/skills/star", { method: "POST", body: { id: key } });
        const hit = all.find((s) => (s.id || s.name) === key || s.name === key);
        if (hit) hit.starred = out.starred;
        refresh();
      });
    });
    const exportBtn = root.querySelector("#export-starred");
    const starredN = all.filter((s) => s.starred).length;
    if (exportBtn) {
      exportBtn.hidden = starredN === 0;
      exportBtn.textContent = starredN ? `导出星标 ${starredN}` : "导出星标";
    }
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
      <button type="button" class="star ${s.starred ? "on" : ""}" id="star-one" title="星标">★</button>
      ${badge("", s.origin || s.kind)} ${s.agent ? badge("", s.agent) : ""} ${(s.installTargets || []).map((t) => badge("ok", `装到 ${t}`)).join("")}
      ${s.zip ? `<a class="btn" href="${esc(s.zip)}">导出</a>` : ""}
    </div>
    <h1>${esc(s.name)}</h1>
    <p class="lede">${esc(s.description)}</p>
    <p class="muted">导出是整包 zip（${esc(s.zipName || "skill.zip")}），同一 name 只打这份。${
      extras.length ? "下面 runtime 会一并打进压缩包。" : ""
    }</p>
    <div class="grid grid-2">
      <div class="card">
        <h3>Meta</h3>
        <div class="mono">path: ${esc(s.path)}</div>
        <div class="mono">author: ${esc(s.author || "—")}</div>
        <div class="mono">repo: ${esc(s.repo || s.source)}</div>
        <div class="mono">updated: ${esc(fmtTime(s.updatedAt))}</div>
        <div class="mono">origin: ${esc(s.origin || "—")} ${s.agent ? `· ${esc(s.agent)}` : ""}</div>
        <div class="mono">version: ${esc(s.version?.hash || s.version?.synced_commit || "—")} ${s.version?.dirty ? badge("warn", "dirty") : ""}</div>
        <div class="mono">license: ${esc(s.license || "—")}</div>
        ${
          (s.copies || []).length > 1
            ? `<h3 style="margin-top:1rem">出现位置 ${(s.copies || []).length}</h3><ul>${(s.copies || [])
                .map((c) => `<li class="mono">${esc(c.path)} · ${esc(c.source || c.sourceId || "")}</li>`)
                .join("")}</ul>`
            : ""
        }
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
  root.querySelector("#star-one")?.addEventListener("click", async () => {
    const out = await api("/api/skills/star", { method: "POST", body: { id: s.id || s.name } });
    root.querySelector("#star-one")?.classList.toggle("on", out.starred);
  });
}
