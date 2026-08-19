---
name: ksamint-mcp-skill-publisher
description: Stage, validate, and publish reusable agent SKILL.md files through the Ksamint-status MCP server. Use when an agent needs to create or update a Ksamint-managed skill, request its GitHub pull request, inspect publication status, or synchronize a reviewed skill back into the catalog.
---

# Ksamint MCP skill publisher

Use `https://g.ksamint.cn/mcp` with a key that has `read,skills:write` scopes.
Read the key only at runtime from 1Password field `ksamint-mcp-write-api` in
`Personal/TableAI Catalog`; never print, commit, or place it in a shell profile.

## Stage and validate

1. Draft a `SKILL.md` with YAML frontmatter containing `name` and
   `description`. Make `name` equal the lowercase hyphenated slug.
2. Call `skills.stage` with `slug`, `title`, `description`, and complete
   `content`.
3. Stop if validation is rejected. Remove secrets, private keys, or API-token
   strings; repair frontmatter and stage a new version.
4. Call `skills.request_publish` only for a `validated` draft.

## Publish

Run the local publisher from the Ksamint repository with an ephemeral
environment variable:

```bash
export KSAMINT_MCP_WRITE_KEY="$(op read 'op://Personal/TableAI Catalog/ksamint-mcp-write-api')"
npm run skills:publish -- <draft-id>
unset KSAMINT_MCP_WRITE_KEY
```

It creates `mcp/skill-<slug>-<id>` and a GitHub pull request in
`fengurt/cfker01`; it never pushes `main`. The publisher records the PR URL
and commit back through `skills.record_publish`.

## Readback

Use `skills.list` and `skills.get` to inspect staged and published versions.
After merge, run the normal local repository scan so the catalog discovers the
new `skills/<slug>/SKILL.md` record.

## Guardrails

- Do not use `ADMIN_TOKEN` as an MCP key.
- Do not stage credentials, `.env` data, private infrastructure details, or
  copied third-party instructions as trusted policy.
- Do not bypass the pull-request review step.
- Revoke and replace the scoped API key from the admin key endpoint if it is
  exposed.
