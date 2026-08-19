import { api, badge, esc, fmtTime } from "./util.js";

export async function renderJobs(root, parts) {
  if (parts[1]) return renderJobDetail(root, parts[1]);
  root.innerHTML = `<p class="muted">Loading…</p>`;
  const { jobs } = await api("/api/jobs");
  root.innerHTML = `
    <div class="row"><h1 style="margin:0">Jobs</h1><span class="spacer"></span>
      <button class="btn ghost" id="sync">Start repo-sync</button>
      <button class="btn ghost" id="links">Install links</button>
    </div>
    <p class="lede">Allowlisted pipeline runs with streamed logs. No free-form shell.</p>
    <div class="card" style="padding:0;overflow:auto">
      <table>
        <thead><tr><th>id</th><th>template</th><th>status</th><th>steps</th><th>when</th></tr></thead>
        <tbody>
          ${
            jobs
              .map((j) => {
                const steps = (j.steps || [])
                  .map((s) => `<span class="step-pill ${esc(s.status)}">${esc(s.id)}</span>`)
                  .join("");
                return `<tr class="clickable" data-href="#/jobs/${esc(j.id)}">
                  <td class="mono">${esc(j.id)}</td>
                  <td>${esc(j.template)}</td>
                  <td>${badge(j.status === "ok" ? "ok" : j.status === "running" ? "warn" : "fail", j.status)}</td>
                  <td><div class="step-rail">${steps}</div></td>
                  <td class="muted">${fmtTime(j.created_at)}</td>
                </tr>`;
              })
              .join("") || `<tr><td colspan="5" class="muted">No jobs</td></tr>`
          }
        </tbody>
      </table>
    </div>
  `;
  root.querySelectorAll("[data-href]").forEach((tr) => {
    tr.addEventListener("click", () => (location.hash = tr.getAttribute("data-href")));
  });
  root.querySelector("#sync")?.addEventListener("click", async () => {
    const job = await api("/api/jobs", { method: "POST", body: { template: "repo-sync" } });
    location.hash = `#/jobs/${job.id}`;
  });
  root.querySelector("#links")?.addEventListener("click", async () => {
    const job = await api("/api/jobs", { method: "POST", body: { template: "install-links" } });
    location.hash = `#/jobs/${job.id}`;
  });
}

async function renderJobDetail(root, id) {
  root.innerHTML = `<p class="muted">Connecting…</p>`;
  const job = await api(`/api/jobs/${encodeURIComponent(id)}`);
  const paint = (j, logLines) => {
    root.innerHTML = `
      <div class="row">
        <a class="btn ghost" href="#/jobs">← jobs</a>
        <span class="spacer"></span>
        ${j.status === "running" ? `<button class="btn danger" id="cancel">Cancel</button>` : ""}
        ${j.mechanicalDraft ? `<span class="badge mech">includes mechanical draft</span>` : ""}
      </div>
      <h1>${esc(j.id)}</h1>
      <p class="lede">${esc(j.template)} · ${badge(j.status === "ok" ? "ok" : j.status === "running" ? "warn" : "fail", j.status)}
        ${j.error ? ` · <span style="color:var(--fail)">${esc(j.error)}</span>` : ""}
      </p>
      <div class="step-rail">
        ${(j.steps || [])
          .map(
            (s) =>
              `<span class="step-pill ${esc(s.status)}">${esc(s.label)}${s.mechanical ? " · draft" : ""} · ${esc(s.status)}</span>`
          )
          .join("")}
      </div>
      <div class="mono muted" style="margin:.5rem 0">work: ${esc(j.ctx?.work || "—")} · source: ${esc(j.ctx?.source || "—")}</div>
      <pre class="pre" id="log">${esc(logLines.join(""))}</pre>
    `;
    root.querySelector("#cancel")?.addEventListener("click", async () => {
      await api(`/api/jobs/${encodeURIComponent(id)}/cancel`, { method: "POST" });
    });
  };

  const lines = [];
  for (const ev of job.logTail || []) {
    lines.push(formatEvent(ev));
  }
  paint(job, lines);

  const es = new EventSource(`/api/jobs/${encodeURIComponent(id)}/stream`);
  es.onmessage = async (msg) => {
    try {
      const ev = JSON.parse(msg.data);
      lines.push(formatEvent(ev));
      if (lines.length > 500) lines.splice(0, lines.length - 500);
      const logEl = root.querySelector("#log");
      if (logEl) {
        logEl.textContent = lines.join("");
        logEl.scrollTop = logEl.scrollHeight;
      }
      if (["job_ok", "job_failed", "job_cancelled", "job_error", "step_end"].includes(ev.event)) {
        const fresh = await api(`/api/jobs/${encodeURIComponent(id)}`);
        const keep = lines.slice();
        paint(fresh, keep);
        if (["job_ok", "job_failed", "job_cancelled", "job_error"].includes(ev.event)) es.close();
      }
    } catch {
      /* */
    }
  };
  es.onerror = () => {
    /* browser retries; ok */
  };
}

function formatEvent(ev) {
  if (ev.event === "stdout" || ev.event === "stderr") return ev.text || "";
  if (ev.event === "cmd") return `\n$ ${ev.cmd} ${(ev.args || []).join(" ")}\n`;
  if (ev.event === "note") return `\n※ ${ev.text}\n`;
  if (ev.event === "step_start") return `\n── ${ev.label || ev.step} ──\n`;
  if (ev.event === "step_end") return `← exit ${ev.exitCode}\n`;
  return `\n[${ev.event}]\n`;
}
