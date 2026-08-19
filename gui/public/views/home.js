import { api, badge, esc, fmtTime } from "./util.js";

export async function renderHome(root) {
  root.innerHTML = `<p class="muted">Loading status…</p>`;
  const [status, health] = await Promise.all([
    api("/api/status"),
    api("/api/health").catch(() => null),
  ]);
  const r = status.repo;
  const syncBadge = r.synced
    ? badge("ok", "synced")
    : badge("warn", `ahead ${r.ahead} / behind ${r.behind}`);
  const dirtyBadge = r.dirty ? badge("warn", "dirty") : badge("ok", "clean");
  const vendorRows = (status.registry?.sources || [])
    .map((s) => {
      const m =
        s.kind !== "git"
          ? badge("", s.kind)
          : !s.present
            ? badge("fail", "missing")
            : s.match
              ? badge("ok", "match")
              : badge("warn", "drift?");
      return `<tr><td class="mono">${esc(s.id)}</td><td>${m}</td><td class="mono muted">${esc(
        (s.synced_commit || "").slice(0, 7) || "—"
      )}</td></tr>`;
    })
    .join("");

  const linkSum = status.links?.summary || {};
  root.innerHTML = `
    <h1>Home</h1>
    <p class="lede">Repo status, vendor freshness, and recent work. Gates stay authoritative in the scripts — this panel observes and launches allowlisted jobs.</p>
    <div class="grid grid-4">
      <div class="card"><div class="stat-n">${esc(r.branch)}</div><div class="stat-l">branch</div>
        <div class="row" style="margin-top:.5rem">${syncBadge}${dirtyBadge}</div>
        <p class="mono muted" style="margin:.5rem 0 0">${esc(r.head?.hash)} · ${esc(r.head?.subject || "")}</p>
      </div>
      <div class="card"><div class="stat-n">${status.skills?.authored ?? "—"}</div><div class="stat-l">authored skills</div></div>
      <div class="card"><div class="stat-n">${(status.registry?.sources || []).filter((s) => s.present).length}/${(status.registry?.sources || []).length}</div><div class="stat-l">vendor sources present</div></div>
      <div class="card"><div class="stat-n">${status.recentRuns?.length ?? 0}</div><div class="stat-l">recent .work runs</div></div>
    </div>

    <h2>Gates</h2>
    <div class="row">
      ${
        health
          ? `${badge(health.lint?.ok, "lint-skills")} ${badge(health.secrets?.ok, "scan-secrets")}
             ${badge(linkSum.foreign || linkSum.broken ? "fail" : linkSum.missing ? "warn" : "ok", `links ok ${linkSum.ok || 0} · miss ${linkSum.missing || 0} · foreign ${linkSum.foreign || 0}`)}`
          : `<span class="muted">health check unavailable</span>`
      }
      <span class="spacer"></span>
      <button class="btn ghost" id="run-health">Re-run gates</button>
      <button class="btn" id="run-sync">Run repo-sync job</button>
    </div>
    ${
      health?.lint && !health.lint.ok
        ? `<pre class="pre light" style="margin-top:.75rem">${esc(health.lint.stderr || health.lint.stdout)}</pre>`
        : ""
    }

    <h2>Vendor freshness</h2>
    <div class="card" style="padding:0;overflow:auto">
      <table><thead><tr><th>source</th><th>status</th><th>synced</th></tr></thead>
      <tbody>${vendorRows || `<tr><td colspan="3" class="muted">no sources</td></tr>`}</tbody></table>
    </div>

    <h2>Recent projects</h2>
    <div class="grid grid-3">
      ${(status.recentProjects || [])
        .map(
          (p) => `<a class="card clickable" href="#/projects/${esc(p.id)}" style="text-decoration:none;color:inherit">
        <h3>${esc(p.name)}</h3>
        <div class="mono muted">${esc(p.template)} · ${esc(p.work || "")}</div>
        <div class="muted" style="margin-top:.35rem">${fmtTime(p.updated_at)}</div>
      </a>`
        )
        .join("") || `<div class="empty">No projects yet — create one under Projects.</div>`}
    </div>

    <h2>Recent jobs</h2>
    <div class="card" style="padding:0;overflow:auto">
      <table><thead><tr><th>id</th><th>template</th><th>status</th><th>when</th></tr></thead>
      <tbody>
        ${(status.recentJobs || [])
          .map(
            (j) => `<tr class="clickable" data-href="#/jobs/${esc(j.id)}">
          <td class="mono">${esc(j.id)}</td><td>${esc(j.template)}</td>
          <td>${badge(j.status === "ok" ? "ok" : j.status === "running" ? "warn" : "fail", j.status)}</td>
          <td class="muted">${fmtTime(j.created_at)}</td></tr>`
          )
          .join("") || `<tr><td colspan="4" class="muted">No jobs yet</td></tr>`}
      </tbody></table>
    </div>
  `;

  root.querySelector("#run-health")?.addEventListener("click", async () => {
    root.querySelector("#run-health").disabled = true;
    await renderHome(root);
  });
  root.querySelector("#run-sync")?.addEventListener("click", async () => {
    const job = await api("/api/jobs", { method: "POST", body: { template: "repo-sync" } });
    location.hash = `#/jobs/${job.id}`;
  });
  root.querySelectorAll("[data-href]").forEach((tr) => {
    tr.addEventListener("click", () => (location.hash = tr.getAttribute("data-href")));
  });
}
