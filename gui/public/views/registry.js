import { api, badge, esc } from "./util.js";

export async function renderRegistry(root) {
  root.innerHTML = `<p class="muted">Loading…</p>`;
  const [reg, health] = await Promise.all([api("/api/registry"), api("/api/health")]);
  const links = health.links || { rows: [], summary: {} };

  root.innerHTML = `
    <h1>Registry & health</h1>
    <p class="lede">Upstream sources from <span class="mono">registry/sources.yaml</span>, vendor presence, and install-map symlink integrity.</p>
    <div class="row" style="margin-bottom:1rem">
      ${badge(health.lint?.ok, "lint-skills")}
      ${badge(health.secrets?.ok, "scan-secrets")}
      <span class="spacer"></span>
      <button class="btn" id="sync">Run repo-sync</button>
    </div>
    <h2>Sources</h2>
    <div class="card" style="padding:0;overflow:auto">
      <table>
        <thead><tr><th>id</th><th>kind</th><th>pin</th><th>synced</th><th>vendor HEAD</th><th>status</th><th></th></tr></thead>
        <tbody>
          ${(reg.sources || [])
            .map((s) => {
              const st = !s.present
                ? badge("fail", "missing")
                : s.kind !== "git"
                  ? badge("", "local")
                  : s.match
                    ? badge("ok", "match")
                    : badge("warn", "check");
              return `<tr>
                <td class="mono">${esc(s.id)}</td>
                <td>${esc(s.kind)}</td>
                <td class="mono">${esc(s.pin || "—")}</td>
                <td class="mono">${esc((s.synced_commit || "").slice(0, 10) || "—")}</td>
                <td class="mono">${esc((s.vendor_head || "").slice(0, 10) || "—")}</td>
                <td>${st}</td>
                <td>${
                  s.kind === "git" && s.present
                    ? `<button class="btn ghost" data-drift="${esc(s.id)}">Check upstream</button><span class="mono muted" data-drift-out="${esc(s.id)}"></span>`
                    : ""
                }</td>
              </tr>`;
            })
            .join("")}
        </tbody>
      </table>
    </div>
    <h2>Symlink integrity</h2>
    <p class="muted">ok ${links.summary?.ok ?? 0} · missing ${links.summary?.missing ?? 0} · foreign ${links.summary?.foreign ?? 0} · broken ${links.summary?.broken ?? 0}</p>
    <div class="card" style="padding:0;overflow:auto;max-height:420px">
      <table>
        <thead><tr><th>skill</th><th>target</th><th>status</th><th>path</th></tr></thead>
        <tbody>
          ${(links.rows || [])
            .map(
              (r) => `<tr>
              <td class="mono">${esc(r.name)}</td>
              <td>${esc(r.target)}</td>
              <td>${badge(r.status === "ok" ? "ok" : r.status === "missing" ? "warn" : "fail", r.status)}</td>
              <td class="mono muted" style="font-size:.72rem">${esc(r.path || "")}</td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;

  root.querySelector("#sync")?.addEventListener("click", async () => {
    const job = await api("/api/jobs", { method: "POST", body: { template: "repo-sync" } });
    location.hash = `#/jobs/${job.id}`;
  });
  root.querySelectorAll("[data-drift]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-drift");
      btn.disabled = true;
      try {
        const d = await api(`/api/registry/${encodeURIComponent(id)}/drift`, { method: "POST" });
        const out = root.querySelector(`[data-drift-out="${CSS.escape(id)}"]`);
        if (out) {
          out.textContent = d.drifted
            ? ` drifted · remote ${(d.remote || "").slice(0, 7)}`
            : ` ok · ${(d.remote || "").slice(0, 7)}`;
        }
      } catch (e) {
        alert(e.message);
      } finally {
        btn.disabled = false;
      }
    });
  });
}
