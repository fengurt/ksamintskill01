import { api, badge, esc } from "./util.js";

export async function renderSkills(root, parts) {
  if (parts[1] && parts[2]) {
    return renderSkillDetail(root, parts[1], decodeURIComponent(parts[2]));
  }
  root.innerHTML = `<p class="muted">Loading skills…</p>`;
  const data = await api("/api/skills");
  const graph = await api("/api/skills/graph").catch(() => ({ nodes: [], edges: [] }));

  root.innerHTML = `
    <h1>Skills gallery</h1>
    <p class="lede">Authored skills in this repo plus vendored upstream trees. Version = last commit (authored) or synced_commit (vendored).</p>
    <div class="toolbar">
      <input class="search" id="q" placeholder="Search SKILL.md…" />
      <label class="row" style="gap:.35rem"><input type="checkbox" id="show-vendor" checked /> vendored</label>
      <span class="spacer"></span>
      <span class="muted mono">${data.totals.authored} authored · ${data.totals.vendored} vendored</span>
    </div>
    <div id="skill-results"></div>
    <h2>Skill graph (authored cross-refs)</h2>
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
  const paint = (authored, vendored, showVendor) => {
    const cards = (list, kind) =>
      list
        .map((s) => {
          const ver = s.version?.hash || (s.version?.synced_commit || "").slice(0, 7) || "—";
          const dirty = s.version?.dirty ? badge("warn", "dirty") : "";
          return `<a class="card clickable" href="#/skills/${kind}/${encodeURIComponent(s.folder)}" style="text-decoration:none;color:inherit">
            <div class="row"><h3 style="margin:0">${esc(s.name)}</h3>${badge("", kind)}${dirty}</div>
            <p class="muted" style="margin:.4rem 0;font-size:.88rem">${esc((s.description || "").slice(0, 140))}${(s.description || "").length > 140 ? "…" : ""}</p>
            <div class="mono muted">${esc(s.source)} · ${esc(ver)}
              ${(s.installTargets || []).map((t) => badge("ok", t)).join("")}
            </div>
          </a>`;
        })
        .join("");
    results.innerHTML = `
      <h2>Authored</h2>
      <div class="grid grid-3">${cards(authored, "authored") || `<div class="empty">none</div>`}</div>
      ${
        showVendor
          ? `<h2>Vendored</h2><div class="grid grid-3">${cards(vendored, "vendored") || `<div class="empty">vendor/ empty — run repo-sync</div>`}</div>`
          : ""
      }
    `;
  };

  paint(data.authored, data.vendored, true);

  let searchTimer;
  root.querySelector("#q").addEventListener("input", (e) => {
    clearTimeout(searchTimer);
    const q = e.target.value.trim();
    searchTimer = setTimeout(async () => {
      if (!q) {
        paint(data.authored, data.vendored, root.querySelector("#show-vendor").checked);
        return;
      }
      const { hits } = await api(`/api/skills/search?q=${encodeURIComponent(q)}`);
      results.innerHTML = `
        <h2>Search · ${hits.length}</h2>
        <div class="grid grid-3">
          ${hits
            .map(
              (s) => `<a class="card clickable" href="#/skills/${s.kind}/${encodeURIComponent(s.folder)}" style="text-decoration:none;color:inherit">
              <h3>${esc(s.name)}</h3>
              <div class="mono muted">${esc(s.source)}</div>
              <p class="muted" style="font-size:.82rem">${esc(s.snippet || "")}</p>
            </a>`
            )
            .join("") || `<div class="empty">No hits</div>`}
        </div>`;
    }, 220);
  });
  root.querySelector("#show-vendor").addEventListener("change", (e) => {
    paint(data.authored, data.vendored, e.target.checked);
  });
}

async function renderSkillDetail(root, kind, id) {
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

  root.innerHTML = `
    <div class="row"><a class="btn ghost" href="#/skills">← gallery</a><span class="spacer"></span>
      ${badge("", s.kind)} ${(s.installTargets || []).map((t) => badge("ok", t)).join("")}
    </div>
    <h1>${esc(s.name)}</h1>
    <p class="lede">${esc(s.description)}</p>
    <div class="grid grid-2">
      <div class="card">
        <h3>Meta</h3>
        <div class="mono">path: ${esc(s.path)}</div>
        <div class="mono">source: ${esc(s.source)}</div>
        <div class="mono">version: ${esc(s.version?.hash || s.version?.synced_commit || "—")} ${s.version?.dirty ? badge("warn", "dirty") : ""}</div>
        <div class="mono">license: ${esc(s.license || "—")}</div>
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
