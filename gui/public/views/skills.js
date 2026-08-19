import { api, badge, esc, fmtTime } from "./util.js";
import { renderRichSkillDetail } from "./skill-detail.js";

const FILTERS = [
  { id: "ksamint", label: "ksamint" },
  { id: "mattpocock", label: "mattpocock" },
  { id: "system", label: "system" },
  { id: "other", label: "其他 vendor" },
];

const CAPABILITIES = [
  ["Context", "Domain language, retrieval, memory, and source quality."],
  ["Tools", "Reliable access to code, data, browsers, and real systems."],
  ["Evals", "Tests, rubrics, traces, and fast feedback on actual outcomes."],
  ["Judgment", "Problem framing, tradeoffs, taste, and knowing when to stop."],
  ["Shipping", "Security, observability, ownership, and production learning."],
];

const VIEWS = {
  starred: ["Starred", "Your saved set for repeat work."],
  trending: ["Trending", "Recently updated here. Freshness, not internet popularity."],
  all: ["All skills", "Every unique skill from the selected sources."],
};

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
  const on = new Set(["ksamint", "mattpocock", "system"]);
  const copyNote =
    totals.copies && totals.unique && totals.copies !== totals.unique
      ? `${totals.unique} unique from ${totals.copies} copies`
      : "";
  let view = "trending";
  let searchToken = 0;

  root.innerHTML = `
    <section class="skills-hero">
      <div>
        <p class="skills-kicker">AI capability library</p>
        <h1>Learn the whole loop, not only skills.</h1>
        <p>Skills make good judgment repeatable. Durable advantage also needs context, tools, evaluation, and disciplined shipping.</p>
      </div>
      <dl class="skills-summary">
        <div><dt>Unique skills</dt><dd>${totals.unique ?? all.length}</dd></div>
        <div><dt>Authored here</dt><dd>${totals.ksamint ?? 0}</dd></div>
        <div><dt>Matt Pocock</dt><dd>${totals.mattpocock ?? 0}</dd></div>
      </dl>
    </section>

    <section class="capability-compass" aria-labelledby="capability-title">
      <div class="capability-intro">
        <h2 id="capability-title">What matters beyond a skill file</h2>
        <p>Build these five capabilities together. A larger skill folder cannot compensate for weak feedback or poor context.</p>
      </div>
      <div class="capability-tracks">
        ${CAPABILITIES.map(([name, description]) => `<article><strong>${name}</strong><span>${description}</span></article>`).join("")}
      </div>
    </section>

    <div class="skill-viewbar">
      <div class="skill-view-tabs" role="tablist" aria-label="Skill views">
        ${Object.entries(VIEWS)
          .map(([id, [label]]) => `<button type="button" role="tab" data-view="${id}" aria-selected="${id === view}">${label}<span data-view-count="${id}"></span></button>`)
          .join("")}
      </div>
      <a class="btn ghost" id="export-starred" href="/api/skills/export.zip?starred=1" hidden>Export starred</a>
    </div>

    <div class="toolbar skill-toolbar">
      <input class="search" id="q" aria-label="Search skills" placeholder="Search names and SKILL.md" />
      ${FILTERS.map(
        (f) =>
          `<label class="filter-chip"><input type="checkbox" data-origin="${f.id}" ${on.has(f.id) ? "checked" : ""} /> ${esc(f.label)} <span class="mono muted">${totals[f.id] ?? 0}</span></label>`
      ).join("")}
      <span class="spacer"></span>
      <span class="muted mono">${copyNote}</span>
    </div>
    <div id="skill-results"></div>
    <details class="skill-graph">
      <summary>Authored skill relationships <span>${graph.edges.length}</span></summary>
      <ul class="graph">
        ${
          graph.edges
            .map((e) => `<li><span class="mono">${esc(e.from)}</span> to <span class="mono">${esc(e.to)}</span></li>`)
            .join("") || `<li class="muted">No cross-references found</li>`
        }
      </ul>
    </details>
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
    return `<article class="skill-card">
      <div class="row">
        <button type="button" class="star ${s.starred ? "on" : ""}" data-star="${id}" aria-label="${s.starred ? "Unstar" : "Star"} ${esc(s.name)}" aria-pressed="${Boolean(s.starred)}">★</button>
        <a class="skill-card-title" href="${href}"><h3 style="margin:0">${esc(s.name)}</h3></a>
        ${who}${dirty}${copies > 1 ? badge("", `${copies} 处`) : ""}
        <span class="spacer"></span>
        ${s.zip ? `<a class="btn ghost skill-export" href="${esc(s.zip)}" download="${esc(s.zipName || `${s.name}-skill.zip`)}">Export</a>` : ""}
      </div>
      <a class="skill-card-body" href="${href}">
        <p class="muted" style="margin:.4rem 0;font-size:.88rem">${esc((s.description || "").slice(0, 140))}${(s.description || "").length > 140 ? "…" : ""}</p>
        <div class="skill-meta mono muted"><span>${esc(s.author || s.origin)}</span><span>${esc(s.repo || s.source)}</span><time>${esc(fmtTime(s.updatedAt))}</time></div>
      </a>
    </article>`;
  }

  function paint(list, origins, { searching = false } = {}) {
    let shown = [...list].filter((s) => origins.has(s.origin || "other"));
    let title = "Search results";
    let description = "Matches across names, descriptions, and skill instructions.";
    if (!searching) {
      [title, description] = VIEWS[view];
      if (view === "starred") shown = shown.filter((s) => s.starred);
      if (view === "trending") shown = shown.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0)).slice(0, 24);
      if (view === "all") shown = shown.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
    }
    results.innerHTML = `<div class="skill-section-head"><div><h2>${esc(title)}</h2><p>${esc(description)}</p></div><strong>${shown.length}</strong></div>${
      shown.length ? `<div class="skill-grid">${shown.map(card).join("")}</div>` : `<div class="empty">Nothing here yet. Change the source filters or star a skill.</div>`
    }`;
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
      exportBtn.textContent = starredN ? `Export starred ${starredN}` : "Export starred";
    }
    root.querySelector('[data-view-count="starred"]').textContent = ` ${starredN}`;
    root.querySelector('[data-view-count="trending"]').textContent = ` ${Math.min(24, all.length)}`;
    root.querySelector('[data-view-count="all"]').textContent = ` ${all.length}`;
    root.querySelectorAll("[data-view]").forEach((button) => button.setAttribute("aria-selected", String(button.dataset.view === view)));
  }

  paint(all, activeOrigins());

  function refresh() {
    const token = ++searchToken;
    const q = root.querySelector("#q").value.trim();
    const origins = activeOrigins();
    if (!q) {
      paint(all, origins);
      return;
    }
    api(`/api/skills/search?q=${encodeURIComponent(q)}`).then(({ hits }) => {
      if (token !== searchToken) return;
      paint(
        (hits || []).map((s) => ({
          ...s,
          origin: s.origin || (s.kind === "authored" ? "ksamint" : "other"),
        })),
        origins,
        { searching: true }
      );
    });
  }

  root.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      view = button.dataset.view;
      root.querySelector("#q").value = "";
      refresh();
    });
  });

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
  return renderRichSkillDetail(root, kind, id);
}
