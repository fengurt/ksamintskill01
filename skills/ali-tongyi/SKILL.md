---
name: ali-tongyi
description: Use the Alibaba Cloud Bailian (百炼) / Tongyi (通义) Token Plan LLM API — an OpenAI- and Anthropic-compatible gateway to Qwen (qwen3.7-plus/max, qwen3.6-plus/flash), DeepSeek (v4-pro/flash, v3.2), Kimi (k2.7-code, k2.6, k2.5), GLM (glm-5.2/5.1/5), MiniMax-M2.5, plus Qwen-Image / Wan image generation. The API key is stored in 1Password and loaded at runtime (never written to disk in plaintext). Use when the user wants Qwen/Tongyi/通义千问, Bailian/百炼, DashScope, ali_tongyi, a Token Plan (套餐/订阅) subscription, or a Chinese-accessible LLM gateway, or mentions the token-plan.*.maas.aliyuncs.com base URL.
---

# Alibaba Bailian / Tongyi Token Plan API

> Skill id `ali-tongyi` (aka `ali_tongyi`).

## Getting the key (run this first, every session)

The key lives in 1Password, never in plaintext on disk. Load it into the env:

```bash
source ~/.cursor/skills/ali-tongyi/scripts/load_key.sh
# exports DASHSCOPE_API_KEY (sk-sp-… seat key) by resolving an op:// reference
```

Or run a command with the key injected just for that process:

```bash
op run --env-file=~/.cursor/skills/ali-tongyi/.env -- python my_script.py
```

The `.env` holds only an `op://` **secret reference** (safe, non-secret); `op` resolves it to the real key at runtime. See [scripts/load_key.sh](scripts/load_key.sh) and `.env`. Approve the 1Password Touch ID prompt when it appears.

Alibaba Cloud Bailian (百炼) **Token Plan** (订阅套餐) — a seat-based monthly subscription exposing many models through one OpenAI-compatible and one Anthropic-compatible endpoint. One API key works for every model the plan allows.

## Quick Config

```
OpenAI-compatible:    https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
Anthropic-compatible: https://token-plan.cn-beijing.maas.aliyuncs.com/apps/anthropic
Auth:                 Bearer token — API key from the Bailian console (bailian.console.aliyun.com)
Region:               cn-beijing (华北2/北京)
```

> The base URL is plan-specific (`token-plan.*`), distinct from the standard DashScope URL (`dashscope.aliyuncs.com/compatible-mode/v1`). Use the Token Plan URL so usage draws from the subscription quota, not pay-as-you-go.

### The Token Plan key is a SEAT key (`sk-sp-…`), not the standard key

The Token Plan endpoint requires the **assigned-seat key**, which has prefix **`sk-sp-`** and is ~115 chars. A normal DashScope key (`sk-` + 32 hex, 35 chars) returns **401 invalid_api_key** on the `token-plan.*` URL even though it works on standard DashScope. Always use the `sk-sp-…` seat key for the subscription.

Store it in an env var (recommended `DASHSCOPE_API_KEY`):

```bash
export DASHSCOPE_API_KEY="sk-sp-..."
```

This account's keys live in **1Password** (`op` CLI, account `my`, vault `Personal`, item `Aliyun_apuch与子同泽`):
- Token Plan seat key → field `seat_c42a497589b140f381fac82bb69aa201` (`sk-sp-…`, 115 chars) — **use this for the Token Plan URL**
- Standard pay-as-you-go DashScope key → field `api-ID-2231532` (`sk-…`, 35 chars) — works only on `dashscope.aliyuncs.com`, NOT the Token Plan URL

```bash
# Load the Token Plan seat key (approve the 1Password Touch ID prompt)
source ~/.cursor/skills/ali-tongyi/scripts/load_key.sh
```

> The 1Password item title contains CJK characters, so named `op://` references fail. The `.env` and script use the **ID-based** reference (`op://<vault-id>/<item-id>/<field>`), which is stable and ASCII-safe.

## Available Models (this subscription)

| Brand | Model | Capabilities |
|-------|-------|--------------|
| Qwen 千问 | `qwen3.7-max` | text, reasoning |
| Qwen 千问 | `qwen3.7-plus` | text, reasoning, vision |
| Qwen 千问 | `qwen3.6-plus` | text, reasoning, vision |
| Qwen 千问 | `qwen3.6-flash` | text, reasoning, vision (fast/cheap) |
| DeepSeek | `deepseek-v4-pro` | text, reasoning |
| DeepSeek | `deepseek-v4-flash` | text, reasoning (fast) |
| DeepSeek | `deepseek-v3.2` | text, reasoning |
| Kimi 月之暗面 | `kimi-k2.7-code` | text, reasoning, vision (coding) |
| Kimi 月之暗面 | `kimi-k2.6` | text, reasoning, vision |
| Kimi 月之暗面 | `kimi-k2.5` | text, reasoning, vision |
| GLM 智谱AI | `glm-5.2` / `glm-5.1` / `glm-5` | text, reasoning |
| MiniMax | `MiniMax-M2.5` | text, reasoning |
| Qwen-Image | `qwen-image-2.0` / `qwen-image-2.0-pro` | image generation |
| Wan 万相 | `wan2.7-image` / `wan2.7-image-pro` | image generation |

Defaults to reach for: `qwen3.7-max` (strongest text/reasoning), `qwen3.6-flash` (cheap/fast + vision), `kimi-k2.7-code` (coding), `qwen3.7-plus`/`kimi-k2.6` (vision).

## Text Generation (OpenAI-compatible)

### Python
```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
)

resp = client.chat.completions.create(
    model="qwen3.7-max",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)
print(resp.choices[0].message.content)
```

### JavaScript / TypeScript
```typescript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY,
});

const resp = await client.chat.completions.create({
  model: "qwen3.7-max",
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(resp.choices[0].message.content);
```

### curl
```bash
curl https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.7-max",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Streaming

```python
stream = client.chat.completions.create(
    model="qwen3.7-max",
    messages=[{"role": "user", "content": "Write a haiku."}],
    stream=True,
    stream_options={"include_usage": True},  # usage arrives in final chunk
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

> Qwen models accessed via OpenAI-compatible mode generally require `stream=True` for the largest/long-output requests; if you hit a "must be streaming" error, enable streaming.

## Reasoning / Thinking Mode

Qwen "thinking" models emit a separate reasoning trace. Enable and read it via OpenAI-compatible fields:

```python
resp = client.chat.completions.create(
    model="qwen3.7-plus",
    messages=[{"role": "user", "content": "9.11 vs 9.9, which is larger?"}],
    extra_body={"enable_thinking": True},  # turn reasoning on
    stream=True,                            # thinking output is streamed
)
for chunk in resp:
    delta = chunk.choices[0].delta
    rc = getattr(delta, "reasoning_content", None)
    if rc:
        print(rc, end="")          # the thinking trace
    if delta.content:
        print(delta.content, end="")  # the final answer
```

DeepSeek/GLM/Kimi reasoning models also return `reasoning_content` on the message/delta. Use `extra_body={"enable_thinking": False}` to disable thinking on hybrid Qwen models when you want speed.

## Vision (multimodal input)

Vision-capable models: `qwen3.7-plus`, `qwen3.6-plus`, `qwen3.6-flash`, `kimi-k2.7-code`, `kimi-k2.6`, `kimi-k2.5`.

```python
resp = client.chat.completions.create(
    model="qwen3.6-flash",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": "https://example.com/cat.jpg"}},
            {"type": "text", "text": "What is in this image?"},
        ],
    }],
)
```
Base64 also works: `"url": "data:image/jpeg;base64,<...>"`.

## Tools / Function Calling

Standard OpenAI tool schema works on text/reasoning models:

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a city",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"],
        },
    },
}]

resp = client.chat.completions.create(
    model="qwen3.7-max",
    messages=[{"role": "user", "content": "Weather in Beijing?"}],
    tools=tools,           # tool_choice defaults to "auto"
)
```

## JSON / Structured Output

```python
resp = client.chat.completions.create(
    model="qwen3.7-max",
    messages=[
        {"role": "system", "content": "Output valid JSON only."},
        {"role": "user", "content": "List 3 colors as a JSON array."},
    ],
    response_format={"type": "json_object"},
)
```
Always also instruct the model to produce JSON in the prompt, or output may degrade.

## Image Generation

Image models (`qwen-image-2.0[-pro]`, `wan2.7-image[-pro]`) use DashScope's image synthesis API, not chat completions. Through the Token Plan, prefer the multimodal/generation endpoint with the same key. Minimal pattern via the `dashscope` SDK:

```python
import os, dashscope
from dashscope import MultiModalConversation

dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]
dashscope.base_http_api_url = "https://token-plan.cn-beijing.maas.aliyuncs.com/api/v1"

resp = MultiModalConversation.call(
    model="qwen-image-2.0",
    messages=[{"role": "user", "content": [{"text": "a red panda coding at night, watercolor"}]}],
)
print(resp)
```
If a specific image model rejects the chat-style call, fall back to the async `ImageSynthesis.call(...)` task API (submit → poll task_id → fetch result URL). Check the current Bailian docs for the exact payload of the chosen model.

## Anthropic-Compatible Endpoint (Claude Code, etc.)

Point Anthropic-protocol tools at the plan's Anthropic base URL:

```bash
export ANTHROPIC_BASE_URL="https://token-plan.cn-beijing.maas.aliyuncs.com/apps/anthropic"
export ANTHROPIC_AUTH_TOKEN="$DASHSCOPE_API_KEY"
export ANTHROPIC_MODEL="qwen3.7-max"
export ANTHROPIC_SMALL_FAST_MODEL="qwen3.6-flash"
```
Then run Claude Code (or any Anthropic-SDK client). Set `model` to any allowed model name above.

## Token Plan / Quota Notes

- **Seat-based**: each standard seat carries a token allowance (e.g. 25,000 tokens / seat). Usage is shared across all allowed models; resets at the plan's reset time.
- **Assign the seat**: an unassigned seat (`未分配`) must be assigned to a user/API key in the console before its quota is usable.
- **Shared usage packs** (共享用量包) can be purchased to extend quota beyond seats.
- Only the models listed above are callable on this plan; requesting an unlisted model returns an error.
- Auto-renew (自动续费) may be off — quota expires at the plan end date if not renewed.

## Error Codes

| HTTP | Meaning | Action |
|------|---------|--------|
| 400 | Bad request / invalid params | Fix payload per message |
| 401 | Invalid API key / seat not assigned | Verify key + seat assignment in console |
| 403 | Model not allowed on plan | Use a listed model |
| 429 | Rate limit or quota exhausted | Back off; check remaining seat quota |
| 500/503 | Server error / overloaded | Retry with backoff |

## Getting / Managing the Key

1. Open the Bailian console: https://bailian.console.aliyun.com/cn-beijing (My Subscription / 我的订阅).
2. Ensure the standard seat is assigned to your account/key.
3. Create or copy an API key, then `export DASHSCOPE_API_KEY=...`.
4. Use the plan-specific base URL above so calls draw from the subscription.

> For exact, current request/response schemas of a specific model (especially image models and reasoning fields), fetch the latest Bailian/DashScope docs via Context7 (`resolve-library-id` → `query-docs`) before relying on edge-case parameters.
