# LLM Hub GUI

A local control panel for the `llm-hub` registry: browse every official provider and gateway, test connectivity (latency + HTTP status), edit the model per provider, and persist results so you can always re-check.

## Run

```bash
cd ~/.cursor/skills/llm-hub/gui
./scripts/dev-up.sh                 # http://localhost:7878  (PORT=9000 ./scripts/dev-up.sh to change)
# or: npm start
```

Zero dependencies — needs only Node ≥ 20 (uses built-in `http` + global `fetch`). No `npm install`.

## How it works

- Reads `../registry.tsv` (single source of truth).
- **Keys** resolve in this order (`lib/keys.js`): `LLMHUB_KEY_<PROVIDER>` env → **encrypted store** `secrets/keys.enc` (decrypted with the local PEM) → **1Password** `op` CLI (local dev, Touch ID). They live only in server memory — never sent to the browser, never written in plaintext.
- Test calls are **proxied by the server** (avoids CORS, keeps keys server-side).
- **State** (`data/state.json`): last result + model override per provider, so the dashboard shows connectivity history across restarts.
- **No plaintext export.** For servers, seal keys into `secrets/keys.enc` (hybrid RSA-4096 + AES-256-GCM) with `scripts/gen-keypair.sh` + `scripts/encrypt-keys.sh`; the server decrypts only with the local private PEM. See `DEPLOY.md`.

## Gateway (one key, all providers)

`POST /v1/chat/completions`, `GET /v1/models` — authenticate with a proxy key (admin or user). Route by model: `provider:model` (e.g. `deepseek:deepseek-chat`). Issue keys in **⚿ API Keys**.

## UI

- Three sections: **Official · direct**, **Gateways · hubs**, **Image · signed**.
- Card per provider: status LED (green online / red fail / grey untested), latency, HTTP code, model, key status. EMPTY providers are dimmed.
- Click a card → drawer with run-test, response sample, copyable `curl`. Chat providers get **Check key** + **Chat test**; signed providers (liblib) get **Check signature** only.
- **Check all keys** runs every configured provider sequentially.

## Signed (non-chat) providers

`liblib` (image generation) uses an **AccessKey + SecretKey** pair with HMAC-SHA1 request signing instead of a bearer token. In the registry its `op_ref` is two refs joined by `|` (`<ak-ref>|<sk-ref>`), resolved to `AK:SK`. It is **not** routable through the chat gateway; the dashboard validates it by signing a query call.

## Requirements

- Local dev: 1Password desktop app unlocked + CLI integration enabled (Touch ID).
- Endpoints must be reachable from this machine (note: a fake-IP VPN/TUN proxy can intercept some hosts).
