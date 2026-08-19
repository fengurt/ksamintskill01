# Ksamint skill MCP tools

`skills.list` returns draft metadata. `skills.get` accepts `id` or `slug` and
returns the complete skill body. `skills.stage` writes a new immutable draft;
it requires `read,skills:write`. `skills.request_publish` changes a validated
draft to `publish_requested`. The local publisher creates the GitHub branch and
PR, then calls `skills.record_publish` with the PR URL and commit SHA.

The only accepted publication target is `fengurt/ksacloudf01` under
`skills/<slug>/SKILL.md`.
