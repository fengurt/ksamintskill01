import { renderHome } from "./views/home.js";
import { renderSkills } from "./views/skills.js";
import { renderProjects } from "./views/projects.js";
import { renderRuns } from "./views/runs.js";
import { renderJobs } from "./views/jobs.js";
import { renderRegistry } from "./views/registry.js";
import { installShortcuts } from "./shortcuts.js";

const app = document.getElementById("app");
const nav = document.getElementById("nav");

function routeParts() {
  const h = location.hash.replace(/^#\/?/, "");
  return h.split("/").filter(Boolean);
}

function setActive(parts) {
  const top = parts[0] || "";
  nav.querySelectorAll("a").forEach((a) => {
    a.classList.toggle("active", (a.dataset.route || "") === top);
  });
}

async function route() {
  const parts = routeParts();
  setActive(parts);
  app.innerHTML = "";
  try {
    const top = parts[0] || "";
    if (!top) await renderHome(app);
    else if (top === "skills") await renderSkills(app, parts);
    else if (top === "projects") await renderProjects(app, parts);
    else if (top === "runs") await renderRuns(app, parts);
    else if (top === "jobs") await renderJobs(app, parts);
    else if (top === "registry") await renderRegistry(app);
    else app.innerHTML = `<div class="empty">Unknown route</div>`;
  } catch (e) {
    app.innerHTML = `<div class="card"><h2>Error</h2><pre class="pre light">${String(e.message || e)}</pre></div>`;
  }
}

window.addEventListener("hashchange", route);
installShortcuts();
route();
