# Platform installation and invocation

The skill follows the open Agent Skills directory format. Keep one canonical copy under version control and install or link it into the appropriate directory.

## Codex

- User/global: `~/.agents/skills/build-unified-data-package/`
- Repository: `.agents/skills/build-unified-data-package/`
- Invoke explicitly with `$build-unified-data-package`; matching data-packaging requests may trigger it automatically.

## Claude Code

- User/global: `~/.claude/skills/build-unified-data-package/`
- Project: `.claude/skills/build-unified-data-package/`
- Invoke with `/build-unified-data-package`; automatic discovery uses the description.

## Cursor

- User/global: `~/.agents/skills/build-unified-data-package/` or `~/.cursor/skills/build-unified-data-package/`
- Project: `.agents/skills/build-unified-data-package/` or `.cursor/skills/build-unified-data-package/`
- Invoke from the `/` menu. Cursor also discovers Claude and Codex skill directories.

## Other compatible agents

Install the complete directory wherever the client scans Agent Skills. The client must expose the skill root so the agent can read relative references and run bundled scripts. If the client only accepts one prompt file, the instructions remain usable but deterministic scripts and progressive disclosure are unavailable; treat that as degraded mode and do not claim automated validation unless an equivalent validator ran.

## Dependencies

Create an isolated Python environment and install `scripts/requirements.txt`. Do not grant the skill broad network or external-write permissions merely for data packaging. Source-specific extraction tools may require additional dependencies and authorization.
