---
name: deepseek-api
description: Use DeepSeek API (deepseek-v4-pro, deepseek-v4-flash) with OpenAI-compatible endpoints. Use when the user wants DeepSeek models, thinking mode, or needs Chinese-optimized LLM.
---

# DeepSeek API

DeepSeek API — OpenAI-compatible LLM API. Models: `deepseek-v4-pro` (full), `deepseek-v4-flash` (fast/cheap). Supports thinking/reasoning mode, tools/function calling, JSON mode, streaming, context caching.

## Quick Config

```
Base URL:  https://api.deepseek.com           (OpenAI-compatible)
           https://api.deepseek.com/anthropic  (Anthropic-compatible, for Claude Code)
           https://api.deepseek.com/beta       (Beta features: chat prefix completion)
Auth:      Bearer token (API key from https://platform.deepseek.com/api_keys)
Models:    deepseek-v4-pro, deepseek-v4-flash
```

## SDK Usage

### Python
```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
    stream=False,
)

print(response.choices[0].message.content)
```

### JavaScript/TypeScript
```typescript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://api.deepseek.com",
  apiKey: process.env.DEEPSEEK_API_KEY,
});

const response = await client.chat.completions.create({
  model: "deepseek-v4-pro",
  messages: [{ role: "user", content: "Hello!" }],
});
```

### curl
```bash
curl https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -d '{
    "model": "deepseek-v4-pro",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Models

| Model | Description |
|-------|-------------|
| `deepseek-v4-pro` | Full capability. Thinking mode enabled by default. |
| `deepseek-v4-flash` | Fast, lightweight. Lower cost. |

> **Deprecated:** `deepseek-chat` → `deepseek-v4-flash` (non-thinking); `deepseek-reasoner` → `deepseek-v4-flash` (thinking). Migrate to v4 models.

## Thinking / Reasoning Mode

DeepSeek v4 models support native thinking. Control via the `thinking` parameter:

```json
{
  "thinking": {
    "type": "enabled",          // or "disabled"
    "reasoning_effort": "high"  // "high" (default) or "max"
  }
}
```

In Python SDK, pass via `extra_body`:
```python
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[...],
    extra_body={"thinking": {"type": "enabled"}},
    reasoning_effort="high",  # max_tokens alias, OK to use here
)
```

Response includes `reasoning_content` in `choices[].message` (thinking mode).

**Reasoning effort levels:**
- `high` — default for normal requests
- `max` — auto-set for complex agent requests (Claude Code, OpenCode)
- `low`/`medium` aliases → `high`; `xhigh` → `max`

## Tools / Function Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "What's the weather in Beijing?"}],
    tools=tools,
    # tool_choice="auto"  # default when tools present
)
```

`tool_choice` options: `"none"`, `"auto"`, `"required"`, or force a specific function via `{"type": "function", "function": {"name": "my_func"}}`.

Max 128 functions. Function name: `[a-zA-Z0-9_-]`, max 64 chars. Beta `strict` mode enforces JSON Schema compliance.

## JSON Mode

```python
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "Always output valid JSON."},
        {"role": "user", "content": "List 3 colors."},
    ],
    response_format={"type": "json_object"},
)
```

**Important:** You MUST also instruct the model to produce JSON in the system/user message, otherwise it may generate endless whitespace.

## Streaming

Set `stream: true`. Response arrives as SSE chunks with `delta` (incremental content). Stream ends with `data: [DONE]`.

```python
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[...],
    stream=True,
    stream_options={"include_usage": True},  # get usage in final chunk
)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Context Caching (KVCache)

DeepSeek automatically caches the prompt context on disk. `prompt_tokens` = `prompt_cache_hit_tokens + prompt_cache_miss_tokens`. Cache hits reduce cost. Isolated per `user_id`.

## Key Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `model` | string | required | `deepseek-v4-pro` or `deepseek-v4-flash` |
| `messages` | object[] | required | roles: system, user, assistant, tool |
| `max_tokens` | integer | — | Max output tokens |
| `temperature` | number ≤2 | 1 | Higher = more random |
| `top_p` | number ≤1 | 1 | Nucleus sampling |
| `stop` | string/string[] | — | Stop sequences (max 16) |
| `stream` | boolean | — | Enable SSE streaming |
| `stream_options` | object | — | `include_usage: true` |
| `thinking` | object | — | `{type, reasoning_effort}` |
| `tools` | object[] | — | Max 128 functions |
| `tool_choice` | string/object | auto | none, auto, required, or specific function |
| `response_format` | object | — | `{type: "json_object"}` |
| `logprobs` | boolean | — | Return log probabilities |
| `top_logprobs` | integer ≤20 | — | Top-N per token (requires logprobs=true) |
| `user_id` | string | — | KVCache isolation, max 512 chars |

> **Deprecated:** `frequency_penalty`, `presence_penalty` — no effect.

## Response

```json
{
  "id": "930c60df-...",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you?",
      "reasoning_content": null
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 16,
    "completion_tokens": 10,
    "total_tokens": 26,
    "completion_tokens_details": {"reasoning_tokens": 0}
  }
}
```

### Finish Reasons

| Value | Meaning |
|-------|---------|
| `stop` | Natural stop or stop sequence hit |
| `length` | max_tokens or context limit reached |
| `content_filter` | Blocked by safety filter |
| `tool_calls` | Model called a tool |
| `insufficient_system_resource` | Interrupted by resource shortage |

## Error Codes

| HTTP | Meaning | Action |
|------|---------|--------|
| 400 | Malformed request | Fix body per error message |
| 401 | Invalid API key | Check key at platform.deepseek.com/api_keys |
| 402 | Insufficient balance | Top up account |
| 422 | Invalid parameters | Adjust per error details |
| 429 | Rate limit (TPM/RPM) | Slow down, add retry delay |
| 500 | Server error | Retry, contact support if persistent |
| 503 | Server overloaded | Retry after brief delay |

## Claude Code Integration

Set env vars to use DeepSeek as Claude Code backend:

```bash
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_AUTH_TOKEN="sk-your-deepseek-api-key"
export ANTHROPIC_MODEL="deepseek-v4-pro[1m]"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro[1m]"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro[1m]"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_EFFORT_LEVEL="max"
```

## Getting an API Key

1. Go to https://platform.deepseek.com
2. Navigate to API Keys page
3. Create a new key
4. Set `DEEPSEEK_API_KEY` env var
