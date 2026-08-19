import { api, badge, esc, fmtTime } from "./util.js";

export async function renderProjects(root, parts) {
  if (parts[1] === "new") return renderNewProject(root);
  if (parts[1]) return renderProjectDetail(root, parts[1]);

  root.innerHTML = `<p class="muted">Loading…</p>`;
  const [{ projects }, { templates }] = await Promise.all([
    api("/api/projects"),
    api("/api/templates"),
  ]);
  root.innerHTML = `
    <div class="row"><h1 style="margin:0">Projects</h1><span class="spacer"></span>
      <a class="btn" href="#/projects/new">New project</a></div>
    <p class="lede">First-class projects with source doc, work dir, template, and gate history.</p>
    <div class="grid grid-3">
      ${
        projects
          .map(
            (p) => `<a class="card clickable" href="#/projects/${esc(p.id)}" style="text-decoration:none;color:inherit">
        <h3>${esc(p.name)}</h3>
        <div>${badge("", p.template)} ${p.theme ? badge("", p.theme) : ""}</div>
        <div class="mono muted" style="margin-top:.4rem">${esc(p.work || "")}</div>
        <div class="muted" style="margin-top:.35rem">${fmtTime(p.updated_at)}</div>
      </a>`
          )
          .join("") || `<div class="empty">No projects — create one to run a template.</div>`
      }
    </div>
    <h2>Templates</h2>
    <div class="grid grid-2">
      ${templates
        .map(
          (t) => `<div class="card">
        <h3>${esc(t.title)}</h3>
        <p class="muted">${esc(t.description)}</p>
        <div class="step-rail">${t.steps.map((s) => `<span class="step-pill">${esc(s.label)}${s.mechanical ? " · draft" : ""}</span>`).join("")}</div>
      </div>`
        )
        .join("")}
    </div>
  `;
}

async function renderNewProject(root) {
  const [{ templates }, { themes }] = await Promise.all([api("/api/templates"), api("/api/themes")]);
  root.innerHTML = `
    <a class="btn ghost" href="#/projects">← projects</a>
    <h1>New project</h1>
    <div class="card" style="max-width:640px">
      <div class="field"><label>Name</label><input id="name" style="width:100%" /></div>
      <div class="field"><label>Template</label>
        <select id="template" style="width:100%">
          ${templates.map((t) => `<option value="${esc(t.id)}" ${t.id === "alongslides" ? "selected" : ""}>${esc(t.title)}</option>`).join("")}
        </select>
      </div>
      <div class="field"><label>Theme / skin</label>
        <select id="theme" style="width:100%">
          ${(themes || [])
            .map(
              (t) =>
                `<option value="${esc(t.id)}">${esc(t.label)} · ${esc(t.canvas)}${t.mechanical ? "" : " · agent path"}</option>`
            )
            .join("")}
        </select>
      </div>
      <div class="field"><label>Standards (gates)</label>
        <label class="row"><input type="checkbox" id="std-fit" checked /> fit-overfull</label>
        <label class="row"><input type="checkbox" id="std-hop1" checked /> hop1 source fidelity</label>
        <label class="row"><input type="checkbox" id="std-hop2" checked /> hop2 HTML fidelity</label>
        <p class="muted" style="margin:.35rem 0 0">page-loop / page-audit stay a manual checklist in the agent brief.</p>
      </div>
      <div class="field"><label>Source markdown (absolute or repo-relative)</label><input id="source" style="width:100%" placeholder="fixtures/local/doc.md" /></div>
      <div class="field"><label>Work id under .work/ (optional)</label><input id="work" style="width:100%" placeholder="my-run" /></div>
      <div class="field"><label>Target HTML for hop2 (optional — alongslides renders this)</label><input id="html" style="width:100%" placeholder="/path/to/deck.html" /></div>
      <div class="field"><label>Notes</label><textarea id="notes"></textarea></div>
      <button class="btn" id="create">Create</button>
      <p id="err" class="muted" style="color:var(--fail)"></p>
    </div>
  `;
  root.querySelector("#create").addEventListener("click", async () => {
    try {
      const body = {
        name: root.querySelector("#name").value,
        template: root.querySelector("#template").value,
        theme: root.querySelector("#theme").value,
        standards: {
          "fit-overfull": root.querySelector("#std-fit").checked,
          hop1: root.querySelector("#std-hop1").checked,
          hop2: root.querySelector("#std-hop2").checked,
        },
        source: root.querySelector("#source").value || undefined,
        work_id: root.querySelector("#work").value || undefined,
        html: root.querySelector("#html").value || undefined,
        notes: root.querySelector("#notes").value,
      };
      const p = await api("/api/projects", { method: "POST", body });
      location.hash = `#/projects/${p.id}`;
    } catch (e) {
      root.querySelector("#err").textContent = e.message;
    }
  });
}

async function renderProjectDetail(root, id) {
  root.innerHTML = `<p class="muted">Loading…</p>`;
  const p = await api(`/api/projects/${encodeURIComponent(id)}`);
  const runId = (p.work || "").replace(/^\.work\//, "");
  let run = null;
  try {
    if (runId) run = await api(`/api/runs/${encodeURIComponent(runId)}`);
  } catch {
    /* no run yet */
  }
  let brief = null;
  try {
    if (runId) brief = await api(`/api/runs/${encodeURIComponent(runId)}/brief`);
  } catch {
    /* */
  }

  root.innerHTML = `
    <div class="row">
      <a class="btn ghost" href="#/projects">← projects</a>
      <span class="spacer"></span>
      <button class="btn" id="run-tpl">Run template · ${esc(p.template)}</button>
      ${p.html ? `<button class="btn ghost" id="run-hop2">Run hop2 audit</button>` : ""}
      <button class="btn danger ghost" id="del">Delete</button>
    </div>
    <h1>${esc(p.name)}</h1>
    <p class="lede mono">${esc(p.work || "")} · ${esc(p.template)} · ${esc(p.theme || "—")}
      ${p.standards ? Object.entries(p.standards).map(([k, v]) => badge(v ? "ok" : "warn", k)).join(" ") : ""}
    </p>
    <div class="grid grid-2">
      <div class="card">
        <h3>Paths</h3>
        <div class="mono">source: ${esc(p.source || "—")}</div>
        <div class="mono">html: ${esc(p.html || "—")}</div>
        <div class="mono">work: ${esc(p.work || "—")}</div>
        ${p.notes ? `<p style="margin-top:.75rem">${esc(p.notes)}</p>` : ""}
        <h3 style="margin-top:1rem">Gate history</h3>
        <div class="mono" style="font-size:.75rem;max-height:180px;overflow:auto">
          ${(p.gate_history || [])
            .slice()
            .reverse()
            .map((g) => `${fmtTime(g.at)} · ${esc(g.step)} · ${esc(g.status)}`)
            .join("<br>") || "—"}
        </div>
      </div>
      <div class="card">
        <h3>Run snapshot ${run ? badge("ok", "artifacts") : badge("warn", "empty")}</h3>
        ${
          run
            ? `<div class="mono">units: ${run.index?.total_units ?? "—"} · pages: ${run.deck?.page_count ?? "—"}</div>
               <div class="mono">hop1 hard: ${run.auditSource?.counts?.hard ?? "—"} · hop2 hard: ${run.auditHtml?.counts?.hard ?? "—"}</div>
               <div class="row" style="margin-top:.75rem">
                 <a class="btn ghost" href="#/runs/${esc(runId)}">Open run</a>
                 <a class="btn ghost" href="#/runs/${esc(runId)}/audit">Audit inspector</a>
                 ${run.deckHref ? `<a class="btn" href="${esc(run.deckHref)}" target="_blank">Open deck</a>` : ""}
               </div>
               ${
                 brief
                   ? `<h3 style="margin-top:1rem">Agent brief <span class="badge mech">mechanical draft</span></h3>
                      <pre class="pre light" id="brief">${esc(brief.markdown)}</pre>
                      <button class="btn ghost" id="copy-brief">Copy brief</button>`
                   : ""
               }`
            : `<p class="muted">No artifacts yet — run the template.</p>`
        }
      </div>
    </div>
    <p id="err" style="color:var(--fail)"></p>
  `;

  root.querySelector("#run-tpl")?.addEventListener("click", async () => {
    try {
      const job = await api("/api/jobs", {
        method: "POST",
        body: {
          template: p.template,
          projectId: p.id,
          work: p.work,
          source: p.source,
          html: p.html,
          theme: p.theme,
          standards: p.standards,
        },
      });
      location.hash = `#/jobs/${job.id}`;
    } catch (e) {
      root.querySelector("#err").textContent = e.message;
    }
  });
  root.querySelector("#run-hop2")?.addEventListener("click", async () => {
    try {
      const job = await api("/api/jobs", {
        method: "POST",
        body: {
          template: "deck-audit-hop2",
          projectId: p.id,
          work: p.work,
          html: p.html,
        },
      });
      location.hash = `#/jobs/${job.id}`;
    } catch (e) {
      root.querySelector("#err").textContent = e.message;
    }
  });
  root.querySelector("#del")?.addEventListener("click", async () => {
    if (!confirm("Delete project? (.work artifacts are kept)")) return;
    await api(`/api/projects/${encodeURIComponent(id)}`, { method: "DELETE" });
    location.hash = "#/projects";
  });
  root.querySelector("#copy-brief")?.addEventListener("click", async () => {
    await navigator.clipboard.writeText(brief.markdown);
    root.querySelector("#copy-brief").textContent = "Copied";
  });
}
