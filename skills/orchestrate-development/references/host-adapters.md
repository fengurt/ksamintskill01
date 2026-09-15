# Host adapters

Use this reference when installing the skill or adapting execution to a host. Documentation checked 2026-09-15; confirm the installed version before changing its settings. These are documented discovery paths, not a claim of live end-to-end testing on every client.

## Portable installation

Copy the complete skill folder, including `references/`, to the selected host's project skill directory and name the folder `orchestrate-development`. If the source uses a managed directory name, restore the frontmatter name when exporting. Keep one maintained source; update host copies together. Preserve existing files and avoid installing duplicate names in overlapping discovery roots.

| Host | Project destination | Source |
| --- | --- | --- |
| Codex CLI | `.agents/skills/orchestrate-development/` | [Build skills](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code | `.claude/skills/orchestrate-development/` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Cursor | `.cursor/skills/orchestrate-development/`; `.agents/skills/` is also supported | [Cursor skills](https://cursor.com/docs/skills) |
| Kiro | `.kiro/skills/orchestrate-development/` | [Kiro skills](https://kiro.dev/docs/skills/) |
| Grok Build | `.grok/skills/orchestrate-development/` | [Grok Build skills](https://docs.x.ai/build/features/skills-plugins-marketplaces) |
| Other agent or CLI | Its documented skill directory, or an explicit request to read `SKILL.md` | Verify its loader; do not assume a universal directory |

Use the host's skill selector or ask in ordinary language: “Use orchestrate-development for this change; keep quality first and delegate only bounded work.” Claude Code, Kiro, and Grok Build document slash-command invocation. A plain chat surface without file loading can receive the skill body and necessary reference text as instructions; that is manual use, not installation or automatic discovery.

Use standard `name`, `description`, and optional string-valued `metadata` fields; this package records author and version in `metadata`. The optional `agents/openai.yaml` is OpenAI UI metadata, not routing configuration for other hosts. Keep all core instructions and relative references portable. See the [Agent Skills specification](https://agentskills.io/specification).

## Adapt execution separately

**Codex / ChatGPT Work.** Inspect actual delegation tools and available model IDs. Codex documents model settings for custom subagents; Work uses its advertised controls. Explicitly set a worker model when supported rather than relying on inheritance. Use actual returned identifiers for follow-ups. Do not assume that a local CLI configuration controls a hosted Work session. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

**Claude Code.** Use its native subagent configuration when needed, separately from this portable skill. Verify supported model selectors and resume behavior in the installed version. A native Claude workflow should use its available models; a requested Astra/Luna mapping requires a separately configured provider bridge and is not supplied by a skill. [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)

**Cursor.** Native skill loading does not prove arbitrary per-child model selection or resume support. Inspect the tools exposed to the current agent and its model settings. If mixed-model delegation is unavailable, keep the main model and use the single-agent workflow. Do not fabricate a model-switch tool. [Cursor skills](https://cursor.com/docs/skills)

**Kiro.** Import the folder through its skill interface or documented workspace location. Check the selected agent's resource configuration if discovery fails. Verify model and subagent capabilities separately for the installed surface/version. [Kiro skills](https://kiro.dev/docs/skills/)

**Grok Build.** Its skill documentation says `model` and `effort` frontmatter fields are accepted but not applied. Configure real model selection through supported host controls, not those skill fields. Its subagents have separate contexts and return summaries; personas are behavioral overlays, not a guarantee of a different model. Verify continuation and model selection before use. [Grok skills](https://docs.x.ai/build/features/skills-plugins-marketplaces), [Grok subagents](https://docs.x.ai/build/features/subagents)

**Other hosts / API clients.** Detect four capabilities: load instructions; select model; delegate; continue a prior task. Use only those demonstrated available. An API application must implement its own execution loop and load the skill text at an appropriate instruction level; an endpoint does not discover local skills by itself. Share files and task contracts across hosts, never raw provider thread IDs as a universal resume mechanism.

## External controller boundary

If strict enforcement is requested, map host-specific operations to logical start-task, continue-task, collect-result, and cancel-task actions. This skill supplies the policy and [handoff contract](handoff-and-state.md), not those executable adapters.

A controller should track actual IDs, task revisions, budgets, attempts, and check results; validate scope before writes; and block successful completion until applicable acceptance gates have evidence. Keep gate definitions outside worker control. Handle failures and cancellation explicitly. Do not add credentials, bypass a rejected action, or claim that this instruction-only package already enforces these checks programmatically.
