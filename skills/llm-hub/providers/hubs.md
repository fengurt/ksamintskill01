# Hubs / gateways — quirks & notes

Aggregators expose 100s of models behind one OpenAI-compatible key. Base URLs/keys from [../registry.tsv](../registry.tsv). Model names must match each hub's catalog exactly — use `list_models.sh <provider>`.

## n1n
- `api.n1n.ai/v1` (or `hk.n1n.ai/v1` for lower latency in Asia). Item `N1n-api-apuch` holds 4 keys (`N1N-API-nano`, `nano2`, `nano3`, `hermesclaude01`); registry uses `N1N-API-nano`. Single key → 500+ models (GPT, Claude, Gemini, DeepSeek, Grok…).

## openrouter
- `openrouter.ai/api/v1`. Item `OpenRouter_api_key` (key in the `password` field). Model ids are namespaced, e.g. `openai/gpt-4o-mini`, `anthropic/claude-3.5-sonnet`.

## newapi-apuch (new-api, self-hosted)
- `new01.apuch.cn/v1`. Item `Apuch-API-newapi` has two `password` fields — the **API token** is the `sk-…` one (referenced by field ID, not label, to disambiguate). Console/login at `new01.apuch.cn/login` (root). Relays OpenAI-style model names.

## ocoolai
- `one.ocoolai.com/v1` (OpenAI-compatible; has HK/CN accelerated mirrors — see the item's notes). Item `OcoolAI-api`, field `shifu01`.

## EMPTY (mint/add a token, then set op_ref in registry.tsv)
- **nofinity** — your self-hosted gateway (`api.nofinity.tech`, one-api/new-api style: UI + API on one host). 1Password has only the **console logins** (`api.nofinity.tech/login` user `gf`; `can01.nofinity.cn` admin `admin@tableai.ai`), no API token. Log into the console → Tokens/令牌 → create one, save it, then fill the op_ref. (Note: as of last check the origin returned Cloudflare **525** / timed out — bring the service up first.)
- **oneapi-sealos** — one-api on Sealos (`socmmdpx.cloud.sealos.io`). Item `Sealos_oneapi01` is the **root login** only; mint a token in its console.
- **poloai** — `poloai.top`. Item `Poloai-api` is login only.
- **dmxapi** — `www.dmxapi.cn`. Item `DMXAPI` has no `sk-` token field yet.
