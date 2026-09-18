import { esc } from "./util.js";

// Editorial picks, not a live ranking. Review licenses before installing.
export const RESOURCE_GROUPS = [
  { title: "Benchmark skill sources", note: "Reference collections to study, compare, and adapt.", items: [
    ["Matt Pocock", "https://github.com/mattpocock/skills", "Engineering workflows", "Study reusable approaches to planning, code review, testing, and codebase design."],
    ["Anthropic Skills", "https://github.com/anthropics/skills", "Official examples", "Explore skill structure and practical examples. Check each skill's license before reuse."],
    ["Superpowers", "https://github.com/obra/superpowers", "Development methodology", "Compare a connected approach to planning, implementation, and verification."],
    ["Skills.sh", "https://skills.sh/", "Discovery & trends", "Browse the skills ecosystem and its trending directory. Popularity is not a security audit."],
  ] },
  { title: "AI & vibe coding", note: "Tools for moving from an idea to working software. Review and test generated code.", items: [
    ["Cursor", "https://cursor.com/docs", "Agentic coding", "Learn repository-aware coding, rules, skills, and agent workflows."],
    ["v0", "https://v0.app/", "Interface to application", "Explore AI-assisted web app and interface creation."],
    ["Lovable", "https://lovable.dev/", "Prompt to app", "Build and iterate on websites and applications through conversation."],
    ["Bolt", "https://bolt.new/", "Browser-based building", "Prototype websites and apps in an AI-assisted browser workspace."],
  ] },
  { title: "Latest updates, at the source", note: "Open these official feeds for current releases. This page does not aggregate live news.", items: [
    ["Codex releases", "https://github.com/openai/codex/releases", "Release feed", "Follow published Codex releases and their change notes."],
    ["Claude Code changelog", "https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md", "Changelog", "Track changes to Claude Code directly in its official repository."],
    ["Cursor changelog", "https://cursor.com/changelog", "Product updates", "See the latest changes to Cursor's coding tools and agent experience."],
  ] },
  { title: "Beyond prompts: learn the foundations", note: "Understand portable instructions and tool integration, not only individual products.", items: [
    ["Agent Skills", "https://agentskills.io/", "Open standard", "Learn the portable skill format and how to structure reusable capabilities."],
    ["Model Context Protocol", "https://modelcontextprotocol.io/", "Tools & context", "Understand how AI applications connect to external tools and data sources."],
  ] },
];

export async function renderHome(root) {
  root.classList.remove("studio-page");
  root.innerHTML = `<div class="resource-home">
    <header class="resource-intro">
      <p class="skills-kicker">The AI builder's reading list</p>
      <h1>Better sources.<br>Better skills.</h1>
      <p>A curated starting point for reusable skills, AI coding, and the ideas behind reliable agent workflows.</p>
      <div class="home-actions"><a class="btn" href="#/skills">Explore our skills</a><a class="btn ghost" href="https://github.com/fengurt/ksamintskill01" target="_blank" rel="noopener noreferrer">Skill Hub on GitHub ↗</a></div>
      <p class="muted resource-review">Editorial selection · Links reviewed 18 September 2026 · Not a benchmark score or endorsement</p>
    </header>
    ${RESOURCE_GROUPS.map((group, i) => `<section aria-labelledby="resources-${i}">
      <div class="resource-heading"><span class="mono">0${i + 1}</span><div><h2 id="resources-${i}">${esc(group.title)}</h2><p class="muted">${esc(group.note)}</p></div></div>
      <div class="resource-grid">${group.items.map(([name, url, category, description]) => `<a class="resource-card" href="${esc(url)}" target="_blank" rel="noopener noreferrer">
        <span class="skills-kicker">${esc(category)}</span><h3>${esc(name)} <span aria-hidden="true">↗</span></h3><p>${esc(description)}</p><small class="mono">${esc(new URL(url).hostname)}</small>
      </a>`).join("")}</div>
    </section>`).join("")}
  </div>`;
}
