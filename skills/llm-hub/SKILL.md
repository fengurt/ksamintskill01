---
name: llm-hub
description: Unified registry + gateway for calling any LLM provider or aggregator through one OpenAI-compatible (or Anthropic) interface, plus signed image APIs (liblib). Keys live in 1Password locally and in an encrypted store (RSA+AES, decrypted only by a local PEM) on servers — never plaintext on disk. Covers official providers (OpenAI, Anthropic, DeepSeek, Ali Tongyi/Qwen, Volcengine Ark/Doubao, Moonshot Kimi, MiniMax, Together, Gemini, Grok, NVIDIA, Fireworks, Zhipu GLM), hubs/gateways (Nofinity, n1n, OpenRouter, one-api/new-api, OcoolAI, Poloai, DMXAPI), and image/signed providers (liblib). Includes a GUI control panel + one-proxy-key gateway with admin/user roles and Docker deploy. Use when the user wants to call an LLM, switch provider/model, use an LLM gateway, manage keys, or asks which providers/keys are configured.
---

# LLM Hub

One registry + one loader for every LLM. Pick a `provider`, the loader pulls its key from 1Password and exports a uniform env (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_PROTOCOL`, `LLM_DEFAULT_MODEL`). Everything is **OpenAI-compatible** unless `protocol` is `anthropic`.

## Use it

```bash
H=~/.cursor/skills/llm-hub/scripts

# load a key into the shell (approve the 1Password Touch ID prompt)
source $H/load_key.sh deepseek

# end-to-end test (uses default model unless you pass one)
$H/smoke_test.sh ali-tongyi
$H/smoke_test.sh openrouter openai/gpt-4o-mini

# discover models a provider/hub serves
$H/list_models.sh n1n

# list all providers + which are EMPTY
source $H/load_key.sh
```

The source of truth is [registry.tsv](registry.tsv): `provider · group · base_url · protocol · op_ref · default_model`. The `op_ref` is a 1Password **secret reference** (`op://vault/item/field-id`) — not a secret — resolved at runtime. **`EMPTY`** means no key is stored yet.

## Official providers (direct)

| provider | base_url | key (1Password) | default model |
|----------|----------|-----------------|---------------|
| `ali-tongyi` | `token-plan…/compatible-mode/v1` | `Aliyun_apuch与子同泽` · seat key (`sk-sp-`) | `qwen3.7-max` |
| `openai` | `api.openai.com/v1` | `OpenAI API Key` · api key | `gpt-4o-mini` |
| `anthropic` | `api.anthropic.com` (anthropic) | `Anthropic Culling` · Claude301 | `claude-3-5-sonnet-latest` |
| `deepseek` | `api.deepseek.com` | `DeepSeek135` · cursor01 | `deepseek-chat` |
| `ark` | `ark.cn-beijing.volces.com/api/v3` | `API 火山Axisee` | `doubao-seed-1-6-250615` |
| `moonshot` | `api.moonshot.cn/v1` | `kimi api` · claw01 | `moonshot-v1-8k` |
| `minimax` | `api.minimaxi.com/v1` | `Minimaxi…` · 订阅key | `MiniMax-Text-01` |
| `together` | `api.together.xyz/v1` | `Together_githubpilo` | *(pass model)* |
| `gemini` | `…/v1beta/openai` | **EMPTY** | `gemini-2.0-flash` |
| `xai-grok` | `api.x.ai/v1` | **EMPTY** | `grok-2-latest` |
| `nvidia` | `integrate.api.nvidia.com/v1` | **EMPTY** (login only) | *(pass model)* |
| `fireworks` | `api.fireworks.ai/inference/v1` | **EMPTY** | *(pass model)* |
| `zhipu-glm` | `open.bigmodel.cn/api/paas/v4` | **EMPTY** | `glm-4` |

## Hubs / gateways (one key → many models)

| provider | base_url | key (1Password) | default model |
|----------|----------|-----------------|---------------|
| `n1n` | `api.n1n.ai/v1` | `N1n-api-apuch` · N1N-API-nano | `gpt-4o-mini` |
| `openrouter` | `openrouter.ai/api/v1` | `OpenRouter_api_key` | `openai/gpt-4o-mini` |
| `newapi-apuch` | `new01.apuch.cn/v1` | `Apuch-API-newapi` · token | `gpt-4o-mini` |
| `ocoolai` | `one.ocoolai.com/v1` | `OcoolAI-api` · shifu01 | `gpt-4o-mini` |
| `nofinity` | `api.nofinity.tech/v1` | **EMPTY** (console login only; mint a token) | *(pass model)* |
| `oneapi-sealos` | `socmmdpx.cloud.sealos.io/v1` | **EMPTY** (root login only) | *(pass model)* |
| `poloai` | `poloai.top/v1` | **EMPTY** (login only) | *(pass model)* |
| `dmxapi` | `www.dmxapi.cn/v1` | **EMPTY** (login only) | *(pass model)* |

## Image / signed providers (not chat-routable)

| provider | base_url | protocol | key (1Password) |
|----------|----------|----------|-----------------|
| `liblib` | `openapi.liblibai.cloud` | `liblib` | `liblib API Credential` · access key + SecretKey |

`liblib` (image generation) signs every request with **HMAC-SHA1** over `uri&timestamp&nonce` using the **SecretKey**, passing `AccessKey`, `Signature`, `Timestamp`, `SignatureNonce` as query params. It needs an **AK+SK pair**, so its `op_ref` is two references joined by `|` (`<ak-ref>|<sk-ref>`) → resolved to `AK:SK`. It is **not** routed through the OpenAI gateway; the dashboard validates it by signing a query call (a valid signature returns a business error like `model.notExist`).

> See [providers/official.md](providers/official.md) and [providers/hubs.md](providers/hubs.md) for per-provider quirks (Ali `sk-sp-` seat key, Ark "no `/v1`", Anthropic protocol, n1n HK mirror, etc.).

## Conventions

1. **Secrets stay in 1Password.** `registry.tsv` holds only `op://` references (ID-based, ASCII-safe — named refs break on CJK/spaces). Resolve at runtime; never commit plaintext keys.
2. **EMPTY = not configured.** To enable an EMPTY provider: add the key to its 1Password item, copy the field ID (`op item get <item> --format=json`), and replace `EMPTY` in `registry.tsv` with `op://fyg24alzrp23y727yk5n6jt4cu/<item-id>/<field-id>`.
3. **Uniform env.** Downstream code reads `LLM_API_KEY` + `LLM_BASE_URL`, so switching providers never changes app code.
4. **Routing rule:** default to a hub (`n1n` / `openrouter`) for "any model, one key"; use a direct/plan provider when a subscription quota, region, or provider-only feature requires it (e.g. `ali-tongyi` `sk-sp-` seat quota).
5. **Paired keys.** Signed providers (e.g. `liblib`) store two refs as `op_ref="<ak-ref>|<sk-ref>"`; the loader joins resolved values with `:` → `AK:SK`.

## GUI, gateway & deployment

The [gui/](gui/) folder runs a control panel **and** an OpenAI-compatible gateway: one proxy key (admin/user roles) routes `provider:model` to any provider. For servers (no 1Password), keys are sealed into an **encrypted store** — provider keys are never on disk in plaintext:

- `gui/scripts/gen-keypair.sh` → RSA-4096 keypair (`secrets/llmhub_private.pem` + `_public.pem`).
- `gui/scripts/encrypt-keys.sh` → resolves keys from 1Password and seals them into `secrets/keys.enc` (RSA-OAEP + AES-256-GCM).
- The server decrypts at runtime **only** with the local private PEM. Access requires the **pair**: the proxy **API key** (gateway) + the **local PEM** (decrypt). See [gui/DEPLOY.md](gui/DEPLOY.md) (Tencent AMD64 / Docker).

## Using it from code

```python
import os
from openai import OpenAI                       # after: source load_key.sh <provider>
client = OpenAI(api_key=os.environ["LLM_API_KEY"], base_url=os.environ["LLM_BASE_URL"])
r = client.chat.completions.create(
    model=os.environ.get("LLM_DEFAULT_MODEL","gpt-4o-mini"),
    messages=[{"role":"user","content":"hi"}],
)
print(r.choices[0].message.content)
```

> Model names drift — verify with `list_models.sh <provider>` before hardcoding. The default models above are starting points, not guarantees.
