---
name: tableuser
description: "Develop apps against Table AI Unified Identity (TableUser / UAC): discovery, Developer API, @tableai/uac-* SDKs, TAID/roles. Requires TABLEUSER_DEV_KEY for API calls (401 without). Use for TableUser, tableu.opcglobal.cn, UAC, agent-connect."
---

# TableUser (Table AI Unified Identity)

Public agent skill for connecting apps to Table AI’s IdP + Developer API.

**Auth gate:** the skill documents workflows only. Live `tableu-api` calls need
`Authorization: Bearer $TABLEUSER_DEV_KEY`. No key → cannot use the service
(401). Keys are issued by Table AI ops / Admin API Keys UI — never shipped
inside this skill.

## 1. Refresh live endpoints

```bash
curl -sS https://tableu-api.opcglobal.cn/.well-known/tableuser.json
```

Use `docs`, `openapi`, `agentConnect.*`, `adminConsole` from that JSON. Prefer
discovery over memorized paths.

## 2. Obtain a developer key (required for API)

1. Ask Table AI ops for an **App** or **Platform** developer key, **or**
2. If you already have `platform:admin`, mint one at  
   https://tableu-admin.opcglobal.cn/developer-api-keys/

```bash
export TABLEUSER_DEV_KEY="tu_…"   # from ops / admin UI / your secret store
export TABLEUSER_API_URL="https://tableu-api.opcglobal.cn"
```

- **App key** — scoped to bound registries  
- **Platform key** — all registries + merge/link (ops only)

Optional (operators with 1Password access): load from your team vault — item
names are **not** part of the public contract; use whatever your org stored.

## 3. Register / list apps

From a clone of https://github.com/fengurt/tableuser01 (or curl against discovery URLs):

```bash
# list
curl -sS "$TABLEUSER_API_URL/v1/apps" \
  -H "Authorization: Bearer $TABLEUSER_DEV_KEY"

# register (agent-connect helper)
pnpm tableuser:agent-connect -- --name "<App>" --redirect "http://localhost:<port>/uac/callback"
```

Without `TABLEUSER_DEV_KEY`, these fail by design.

## 4. Wire the consuming app

Install from **public npm** (no monorepo clone required):

```bash
npm install @tableai/uac-next @tableai/uac-react   # Next.js
npm install @tableai/uac-express                    # Express / Hono
npm install @tableai/uac-browser                    # SPA / static
```

| Stack | Package |
|-------|---------|
| Next.js App Router | `@tableai/uac-next` |
| Vanilla / Vite | `@tableai/uac-browser` |
| Express / Hono | `@tableai/uac-express` |
| Generic Node | `@tableai/uac-sdk` |

Quickstart: https://github.com/fengurt/tableuser01/blob/main/docs/developers/quickstart.md  
Docs: https://tableu.opcglobal.cn/developers/ ·  
https://github.com/fengurt/tableuser01/tree/main/docs/developers

## 5. Identity contract

- Stable FK: `session.user.taid` (preferred) / `session.user.id` — not email  
- Roles on the token are **platform-coarse labels** (`platform:admin`, `org:*`, `project:*`, `external:guest`) — not org/project membership  
- Resource-scoped checks need a `grant` from the owning app (join by TAID); global `org:admin` must not authorize every org  
- Prefer SDK helpers (`check` / `withUac` / `resolveGrant`); do not reimplement Logto OIDC  
- Docs: https://github.com/fengurt/tableuser01/blob/main/docs/developers/resource-authorization.md

## 6. Admin console (ops)

https://tableu-admin.opcglobal.cn/console/ — OIDC login with `platform:admin`.
End-user sign-in pages do **not** link to admin.

## Install this plugin / skill

| Surface | How |
|---------|-----|
| This repo | already at `.cursor/skills/tableuser` / `plugins/tableuser` |
| Personal Cursor | `pnpm tableuser:skill-install` from tableuser01 |
| Team Marketplace | Import `https://github.com/fengurt/tableuser01` (reads `.cursor-plugin/marketplace.json`) |
| Public Cursor Marketplace | Submit plugin folder for review: https://cursor.com/marketplace/publish |
| Ksamint catalog | slug `tableuser` (staged/published via Table AI catalog) |

## Safety

- Never commit `tu_…` keys or passwords  
- Skill updates must not embed secrets  
- If discovery and this text disagree, trust discovery
