# TableUser skill — public reference

Prefer live discovery if this file drifts:

```bash
curl -sS https://tableu-api.opcglobal.cn/.well-known/tableuser.json
```

## Auth

| Credential | Who | Capability |
|------------|-----|------------|
| none | anyone with the skill | read docs / discovery only |
| App `TABLEUSER_DEV_KEY` | app team | list/create bound apps, app-scoped APIs |
| Platform `TABLEUSER_DEV_KEY` | ops | all registries, merge/link |
| `platform:admin` OIDC | ops | admin console `/console/` |

No key → Developer API returns **401**. That is intentional.

Mint keys: https://tableu-admin.opcglobal.cn/developer-api-keys/ (requires admin login).

## Docs

- Hub: https://tableu.opcglobal.cn/developers/
- GitHub: https://github.com/fengurt/tableuser01/tree/main/docs/developers
- OpenAPI: https://tableu-api.opcglobal.cn/openapi.json
- Agent guideline: https://github.com/fengurt/tableuser01/blob/main/docs/agent-guideline.md

## CLI (repo https://github.com/fengurt/tableuser01)

```bash
export TABLEUSER_DEV_KEY=tu_…
pnpm tableuser:apps
pnpm tableuser:agent-connect -- --name "<App>" --redirect "http://localhost:3000/uac/callback"
```

User/role Management API CLIs need Logto M2M (`infra/tableuser/.m2m.env`), not the developer key.

## Live discovery snapshot

<!-- BEGIN DISCOVERY -->
```json
{
  "name": "TableUser",
  "version": "0.3.0",
  "docs": "https://tableu.opcglobal.cn/developers/",
  "developerApi": "https://tableu-api.opcglobal.cn",
  "openapi": "https://tableu-api.opcglobal.cn/openapi.json",
  "adminConsole": "https://tableu-admin.opcglobal.cn/console/",
  "developerApiKeyAdmin": "https://tableu-admin.opcglobal.cn/developer-api-keys/",
  "oidcIssuer": "https://tableu.opcglobal.cn/oidc",
  "authorizationModel": null,
  "agentConnect": {
    "registerAppUrl": "https://tableu-api.opcglobal.cn/v1/apps",
    "listAppsUrl": "https://tableu-api.opcglobal.cn/v1/apps",
    "cli": "pnpm tableuser:agent-connect -- --name <name> --redirect <uri>",
    "listCli": "pnpm tableuser:apps"
  }
}
```
<!-- END DISCOVERY -->

