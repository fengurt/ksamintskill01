import { api, badge, esc, fmtTime } from "./util.js";

function jobTone(status) {
  if (status === "ok") return "ok";
  if (status === "running") return "warn";
  return "fail";
}

function sourceState(source) {
  if (source.kind !== "git") return badge("", "local");
  if (!source.present) return badge("fail", "missing");
  return source.match ? badge("ok", "current") : badge("warn", "check drift");
}

export async function renderHome(root) {
  root.classList.remove("studio-page");
  root.innerHTML = `
    <div class="home-loading" aria-live="polite">
      <div></div><div></div><div></div>
      <p>Reading workspace status...</p>
    </div>`;

  const [status, health] = await Promise.all([
    api("/api/status"),
    api("/api/health").catch(() => null),
  ]);
  const repo = status.repo;
  const totals = status.totals || {};
  const baslide = status.baslide || {};
  const links = status.links?.summary || {};
  const linkState = links.foreign || links.broken ? "fail" : links.missing ? "warn" : "ok";
  const gateCount = [health?.lint?.ok, health?.secrets?.ok, linkState === "ok"].filter(Boolean).length;
  const sources = status.registry?.sources || [];
  const sourceCurrent = sources.filter((source) => source.present && (source.kind !== "git" || source.match)).length;
  const recentProjects = (status.recentProjects || []).slice(0, 3);
  const recentJobs = (status.recentJobs || []).slice(0, 4);

  root.innerHTML = `
    <div class="home-shell">
      <section class="home-hero" aria-labelledby="home-title">
        <div class="home-hero-copy">
          <div class="home-kicker">Local skill operations</div>
          <h1 id="home-title">Build, audit, and ship from one workspace.</h1>
          <p>Skills, document pipelines, Baslide rendering, registry sync, and release jobs share one operational view.</p>
          <div class="home-actions">
            <a class="btn" href="#/projects/new">Create project</a>
            <a class="btn ghost" href="#/skills">Browse skills</a>
          </div>
        </div>

        <aside class="home-repo" aria-label="Repository status">
          <div class="home-repo-head">
            <div>
              <span class="home-label">Repository</span>
              <strong class="mono">${esc(repo.branch)}</strong>
            </div>
            <div class="home-repo-badges">
              ${badge(repo.synced ? "ok" : "warn", repo.synced ? "synced" : `ahead ${repo.ahead}, behind ${repo.behind}`)}
              ${badge(repo.dirty ? "warn" : "ok", repo.dirty ? "dirty" : "clean")}
            </div>
          </div>
          <p class="home-commit"><span>${esc(repo.head?.hash || "unknown")}</span>${esc(repo.head?.subject || "No commit message")}</p>
          <div class="home-gates" aria-label="Authoritative gates">
            <div><span>Skill lint</span>${badge(health?.lint?.ok ? "ok" : "fail", health?.lint?.ok ? "pass" : "fail")}</div>
            <div><span>Secret scan</span>${badge(health?.secrets?.ok ? "ok" : "fail", health?.secrets?.ok ? "pass" : "fail")}</div>
            <div><span>Install links</span>${badge(linkState, linkState === "ok" ? `${links.ok || 0} ready` : "attention")}</div>
          </div>
          <div class="home-repo-actions">
            <button class="btn ghost" id="run-health">Re-run gates</button>
            <button class="btn" id="run-sync">Sync repository</button>
          </div>
        </aside>
      </section>

      <section class="home-capacity" aria-label="Workspace totals">
        <a href="#/skills"><strong>${status.skills?.authored ?? 0}</strong><span>authored skills</span></a>
        <a href="#/projects"><strong>${totals.projects ?? 0}</strong><span>projects</span></a>
        <a href="#/runs"><strong>${totals.runs ?? 0}</strong><span>artifact runs</span></a>
        <a href="#/registry"><strong>${sourceCurrent}/${totals.sources ?? sources.length}</strong><span>sources ready</span></a>
        <a href="#/jobs"><strong>${totals.templates ?? 0}</strong><span>job templates</span></a>
      </section>

      <section class="home-section" aria-labelledby="workflow-title">
        <div class="home-section-head">
          <h2 id="workflow-title">Two connected production paths</h2>
          <p>Finish the file pack first. Develop slides only when the source-to-page ledger closes.</p>
        </div>
        <div class="home-workflows">
          <article class="workflow-card workflow-pack">
            <div class="workflow-title-row">
              <div>
                <span class="home-label">Alongslides</span>
                <h3>Long document to developable pack</h3>
              </div>
              <span class="workflow-count">4 stages</span>
            </div>
            <div class="workflow-track" aria-label="Alongslides stages">
              <span>Segment</span><i></i><span>Outline</span><i></i><span>Pages</span><i></i><span>Pack</span>
            </div>
            <p>Coverage, fit, and hop1 fidelity must pass before <code>slide-plan.json</code> is emitted.</p>
            <div class="workflow-links">
              <a href="#/projects">Open projects</a>
              <a href="#/runs">Inspect runs</a>
            </div>
          </article>

          <article class="workflow-card workflow-baslide">
            <div class="workflow-title-row">
              <div>
                <span class="home-label">Baslide01 module</span>
                <h3>Pack to audited HTML</h3>
              </div>
              ${badge(baslide.present ? "ok" : "fail", baslide.present ? "bundled" : "missing")}
            </div>
            <div class="baslide-metrics">
              <div><strong>${baslide.jobs || 0}</strong><span>L2 jobs</span></div>
              <div><strong>${baslide.fills || 0}</strong><span>L3 fills</span></div>
              <div><strong>${baslide.skins || 0}</strong><span>skins</span></div>
            </div>
            <p>Clone the selected job, draw the locked SVG recipe, render HTML, then run hop2.</p>
            <a class="workflow-primary-link" href="#/projects">Develop slides</a>
          </article>
        </div>
      </section>

      <section class="home-section" aria-labelledby="modules-title">
        <div class="home-section-head compact">
          <h2 id="modules-title">Workspace modules</h2>
          <p>Every route has one operational responsibility.</p>
        </div>
        <div class="home-modules">
          <a class="module-link module-skills" href="#/skills">
            <span class="module-name">Skills</span><strong>${status.skills?.authored ?? 0}</strong>
            <p>Authored instructions, install targets, dependency graph, and full-text search.</p>
          </a>
          <a class="module-link module-projects" href="#/projects">
            <span class="module-name">Projects</span><strong>${totals.projects ?? 0}</strong>
            <p>Create pipelines, browse each production stage, download packs, and start slide development.</p>
          </a>
          <a class="module-link module-runs" href="#/runs">
            <span class="module-name">Runs</span><strong>${totals.runs ?? 0}</strong>
            <p>Inspect units, page material, audits, mappings, and generated artifacts.</p>
          </a>
          <a class="module-link module-registry" href="#/registry">
            <span class="module-name">Registry</span><strong>${sourceCurrent}/${totals.sources ?? sources.length}</strong>
            <p>Track upstream sources, pinned commits, local libraries, and drift.</p>
          </a>
          <a class="module-link module-jobs" href="#/jobs">
            <span class="module-name">Jobs</span><strong>${totals.jobs ?? 0}</strong>
            <p>Launch allowlisted templates, follow live logs, and revisit job history.</p>
          </a>
        </div>
      </section>

      <section class="home-section home-recent" aria-labelledby="recent-title">
        <div class="home-section-head compact">
          <h2 id="recent-title">Continue working</h2>
          <p>Recent projects and job activity from this workspace.</p>
        </div>
        <div class="home-recent-grid">
          <div class="home-activity">
            <div class="activity-head"><h3>Projects</h3><a href="#/projects">View all</a></div>
            <div class="activity-list">
              ${recentProjects.length
                ? recentProjects.map((project) => `
                  <a href="#/projects/${esc(project.id)}">
                    <span><strong>${esc(project.name)}</strong><small>${esc(project.template)} / ${esc(project.work || "No work directory")}</small></span>
                    <time>${fmtTime(project.updated_at)}</time>
                  </a>`).join("")
                : `<div class="home-empty"><strong>No projects yet</strong><span>Create a project to start the document pipeline.</span></div>`}
            </div>
          </div>
          <div class="home-activity">
            <div class="activity-head"><h3>Jobs</h3><a href="#/jobs">View all</a></div>
            <div class="activity-list job-list">
              ${recentJobs.length
                ? recentJobs.map((job) => `
                  <a href="#/jobs/${esc(job.id)}">
                    <span><strong>${esc(job.template)}</strong><small class="mono">${esc(job.id)}</small></span>
                    <span class="job-meta">${badge(jobTone(job.status), job.status)}<time>${fmtTime(job.created_at)}</time></span>
                  </a>`).join("")
                : `<div class="home-empty"><strong>No jobs yet</strong><span>Run an allowlisted template when work is ready.</span></div>`}
            </div>
          </div>
        </div>
      </section>

      <details class="home-sources">
        <summary><span>Source registry</span><strong>${sourceCurrent} ready</strong><small>${sources.length} total</small></summary>
        <div class="source-grid">
          ${sources.map((source) => `
            <div><span class="mono">${esc(source.id)}</span>${sourceState(source)}</div>`).join("") || `<p class="muted">No sources configured.</p>`}
        </div>
      </details>

      <footer class="home-foot">
        <span class="mono">${esc(status.repoRoot || "")}</span>
        <span>${gateCount}/3 authoritative gates passing</span>
      </footer>
    </div>
  `;

  root.querySelector("#run-health")?.addEventListener("click", async (event) => {
    event.currentTarget.disabled = true;
    event.currentTarget.textContent = "Checking...";
    await renderHome(root);
  });
  root.querySelector("#run-sync")?.addEventListener("click", async () => {
    const job = await api("/api/jobs", { method: "POST", body: { template: "repo-sync" } });
    location.hash = `#/jobs/${job.id}`;
  });
}
