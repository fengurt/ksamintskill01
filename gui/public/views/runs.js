import { api, badge, esc } from "./util.js";

function extractMermaid(md) {
  if (!md) return null;
  const m = md.match(/```mermaid\n([\s\S]*?)```/);
  return m ? m[1].trim() : null;
}

export async function renderRuns(root, parts) {
  const runId = parts[1] ? decodeURIComponent(parts[1]) : null;
  if (runId && parts[2] === "audit") {
    return renderAudit(root, runId, parts[3] ? decodeURIComponent(parts[3]) : null);
  }
  if (runId) return renderRunDetail(root, runId);

  root.innerHTML = `<p class="muted">Loading…</p>`;
  const { runs } = await api("/api/runs");
  root.innerHTML = `
    <h1>Runs</h1>
    <p class="lede">Artifacts under <span class="mono">.work/</span>. Click a run for digest, outline, pages, and audit.</p>
    <div class="card" style="padding:0;overflow:auto">
      <table>
        <thead><tr><th>id</th><th>units</th><th>pages</th><th>hop1</th><th>hop2</th><th>artifacts</th></tr></thead>
        <tbody>
          ${
            runs
              .map((r) => {
                const arts = Object.entries(r.artifacts || {})
                  .filter(([, v]) => v)
                  .map(([k]) => k.replace(".json", "").replace(".md", ""))
                  .slice(0, 6)
                  .join(" ");
                return `<tr class="clickable" data-href="#/runs/${esc(r.id)}">
                <td class="mono">${esc(r.id)}</td>
                <td>${r.summary?.total_units ?? "—"}</td>
                <td>${r.summary?.page_count ?? r.pages ?? "—"}</td>
                <td>${r.summary?.hop1 ? badge(r.summary.hop1.hard ? "fail" : "ok", `h${r.summary.hop1.hard}/w${r.summary.hop1.warn}`) : "—"}</td>
                <td>${r.summary?.hop2 ? badge(r.summary.hop2.hard ? "fail" : "ok", `h${r.summary.hop2.hard}/w${r.summary.hop2.warn}`) : "—"}</td>
                <td class="mono muted" style="font-size:.7rem">${esc(arts)}</td>
              </tr>`;
              })
              .join("") || `<tr><td colspan="6" class="muted">No .work runs</td></tr>`
          }
        </tbody>
      </table>
    </div>
  `;
  root.querySelectorAll("[data-href]").forEach((tr) => {
    tr.addEventListener("click", () => (location.hash = tr.getAttribute("data-href")));
  });
}

async function renderRunDetail(root, runId) {
  root.innerHTML = `<p class="muted">Loading…</p>`;
  const run = await api(`/api/runs/${encodeURIComponent(runId)}`);
  const kinds = run.index?.kinds || {};
  const kindBars = Object.entries(kinds)
    .map(([k, v]) => `<span class="badge">${esc(k)} ${v}</span>`)
    .join(" ");
  const mermaid = extractMermaid(run.outline);

  root.innerHTML = `
    <div class="row">
      <a class="btn ghost" href="#/runs">← runs</a>
      <span class="spacer"></span>
      <a class="btn" href="#/runs/${esc(runId)}/audit">Audit inspector</a>
      ${run.deckHref ? `<a class="btn" href="${esc(run.deckHref)}" target="_blank">Open deck</a>` : ""}
      <button class="btn ghost" id="copy-brief">Copy agent brief</button>
    </div>
    <h1>${esc(runId)}</h1>
    <p class="lede mono">${esc(run.index?.source || run.deck?.source || run.path)}</p>
    <div class="grid grid-4">
      <div class="card"><div class="stat-n">${run.index?.total_units ?? "—"}</div><div class="stat-l">units</div></div>
      <div class="card"><div class="stat-n">${run.deck?.page_count ?? "—"}</div><div class="stat-l">pages</div></div>
      <div class="card"><div class="stat-n">${run.auditSource?.counts?.hard ?? "—"}</div><div class="stat-l">hop1 hard</div></div>
      <div class="card"><div class="stat-n">${run.auditHtml?.counts?.hard ?? "—"}</div><div class="stat-l">hop2 hard</div></div>
    </div>
    <h2>Unit kinds</h2>
    <div class="row">${kindBars || "—"}</div>
    <h2>Outline ${badge("mech", "may be mechanical")}</h2>
    ${mermaid ? `<pre class="pre light">mermaid mindmap present (${mermaid.split("\n").length} lines)\n\n${esc(mermaid.slice(0, 1200))}${mermaid.length > 1200 ? "…" : ""}</pre>` : ""}
    <pre class="pre light" style="max-height:280px">${esc((run.outline || "").slice(0, 8000))}${(run.outline || "").length > 8000 ? "\n…" : ""}</pre>
    <h2>Pages</h2>
    <div class="card" style="padding:0;overflow:auto;max-height:480px">
      <table>
        <thead><tr><th>id</th><th>role</th><th>title</th><th>units</th><th>fit</th><th>overflow</th></tr></thead>
        <tbody>
          ${(run.deck?.pages || [])
            .map((p) => {
              const v = p.fit?.verdict || "—";
              const vb = v === "ok" ? "ok" : v === "overfull" ? "fail" : v === "starved" ? "warn" : "";
              return `<tr class="clickable" data-page="${esc(p.id)}">
                <td class="mono">${esc(p.id)}</td>
                <td>${esc(p.role)}</td>
                <td>${esc(p.title)}</td>
                <td class="mono muted">${esc((p.units || []).join(" "))}</td>
                <td>${badge(vb, v)}</td>
                <td class="mono muted">${esc(p.overflow_of || "")}</td>
              </tr>`;
            })
            .join("")}
        </tbody>
      </table>
    </div>
    <div id="page-preview" style="margin-top:1rem"></div>
  `;

  root.querySelector("#copy-brief")?.addEventListener("click", async () => {
    const b = await api(`/api/runs/${encodeURIComponent(runId)}/brief`);
    await navigator.clipboard.writeText(b.markdown);
    root.querySelector("#copy-brief").textContent = "Copied";
  });

  root.querySelectorAll("[data-page]").forEach((tr) => {
    tr.addEventListener("click", async () => {
      const pid = tr.getAttribute("data-page");
      const page = await api(`/api/runs/${encodeURIComponent(runId)}/pages/${encodeURIComponent(pid)}`);
      root.querySelector("#page-preview").innerHTML = `
        <div class="card">
          <h3>${esc(pid)} material</h3>
          <pre class="pre light">${esc(page.markdown)}</pre>
        </div>`;
    });
  });
}

function highlightAnchors(text, findings) {
  let out = esc(text || "");
  const sorted = [...(findings || [])]
    .filter((f) => f.anchor)
    .sort((a, b) => (b.anchor?.length || 0) - (a.anchor?.length || 0));
  for (const f of sorted) {
    const cls =
      f.code === "MISS" || f.code === "HMISS"
        ? "hl-miss"
        : f.code === "ALTER"
          ? "hl-alter"
          : f.code === "INVENT"
            ? "hl-invent"
            : f.code === "HEXTRA"
              ? "hl-hextra"
              : "";
    if (!cls) continue;
    const needle = esc(f.anchor);
    out = out.split(needle).join(`<mark class="${cls}">${needle}</mark>`);
  }
  return out;
}

async function renderAudit(root, runId, pageId) {
  root.innerHTML = `<p class="muted">Loading audit…</p>`;
  const { pages } = await api(`/api/runs/${encodeURIComponent(runId)}/audit`);
  const selected = pageId || pages[0]?.id;
  let detail = null;
  if (selected) {
    detail = await api(`/api/runs/${encodeURIComponent(runId)}/audit/${encodeURIComponent(selected)}`);
  }

  const unitText = Object.values(detail?.units || {})
    .map((u) => `## ${u.id}\n${u.text || u.digest || ""}`)
    .join("\n\n");

  const allFindings = [...(detail?.findings?.hop1 || []), ...(detail?.findings?.hop2 || [])];

  root.innerHTML = `
    <div class="row">
      <a class="btn ghost" href="#/runs/${esc(runId)}">← run</a>
      <span class="spacer"></span>
      <span class="muted">Sorted by mapping confidence (worst first)</span>
    </div>
    <h1>Audit inspector</h1>
    <p class="lede">Three panes: source units · page material · HTML slide. Mapping confidence is the root cause when hop2 balloons.</p>
    <div class="grid" style="grid-template-columns: 280px 1fr; gap:1rem">
      <div class="card" style="padding:0;max-height:70vh;overflow:auto">
        <table>
          <thead><tr><th>page</th><th>map</th><th>H</th></tr></thead>
          <tbody>
            ${pages
              .map((p) => {
                const active = p.id === selected ? 'style="background:rgba(14,107,92,.1)"' : "";
                const mr = p.map_reason || "—";
                const bad = ["order", "ambiguous", "unmapped"].includes(mr);
                return `<tr class="clickable" ${active} data-href="#/runs/${esc(runId)}/audit/${esc(p.id)}">
                  <td class="mono">${esc(p.id)}</td>
                  <td>${badge(bad ? "warn" : "ok", mr)}</td>
                  <td>${p.hard || 0}</td>
                </tr>`;
              })
              .join("")}
          </tbody>
        </table>
      </div>
      <div>
        ${
          detail
            ? `<div class="row" style="margin-bottom:.75rem">
                <h2 style="margin:0">${esc(selected)} · ${esc(detail.page?.title || "")}</h2>
                <span class="spacer"></span>
                ${badge(detail.map_reason === "order" || detail.map_reason === "ambiguous" ? "warn" : "ok", `map: ${detail.map_reason || "—"}`)}
                ${detail.slide != null ? `<span class="mono muted">slide ${detail.slide.slide}</span>` : ""}
              </div>
              <div class="panes">
                <div class="pane card">
                  <h3>Source units</h3>
                  <pre class="pre light">${highlightAnchors(unitText, allFindings)}</pre>
                </div>
                <div class="pane card">
                  <h3>Page material</h3>
                  <pre class="pre light">${highlightAnchors(detail.material, allFindings)}</pre>
                </div>
                <div class="pane card">
                  <h3>HTML slide</h3>
                  <pre class="pre light">${
                    detail.slide?.text
                      ? highlightAnchors(detail.slide.text, allFindings)
                      : `<span class="muted">No slides.json — re-run hop2 (audit-html dumps slides automatically).</span>`
                  }</pre>
                </div>
              </div>
              <h2>Findings on this page</h2>
              <div class="card" style="padding:0;overflow:auto;max-height:240px">
                <table>
                  <thead><tr><th>code</th><th>sev</th><th>anchor</th><th>detail</th></tr></thead>
                  <tbody>
                    ${
                      allFindings
                        .map(
                          (f) => `<tr>
                          <td class="mono">${esc(f.code)}</td>
                          <td>${badge(f.severity === "hard" ? "fail" : "warn", f.severity)}</td>
                          <td class="mono">${esc(f.anchor)}</td>
                          <td class="muted">${esc(f.detail)}</td>
                        </tr>`
                        )
                        .join("") || `<tr><td colspan="4" class="muted">No findings on this page</td></tr>`
                    }
                  </tbody>
                </table>
              </div>`
            : `<div class="empty">Select a page</div>`
        }
      </div>
    </div>
  `;
  root.querySelectorAll("[data-href]").forEach((tr) => {
    tr.addEventListener("click", () => (location.hash = tr.getAttribute("data-href")));
  });
}
