---
name: n1n-ai-gateway
description: Use n1n.ai as the LLM API provider. OpenAI-compatible gateway to 500+ models. Use when the user wants to use n1n.ai, switch to n1n models, or needs a Chinese-accessible LLM API.
---

# n1n.ai — LLM API Gateway

n1n.ai is an enterprise-grade LLM API aggregation platform providing OpenAI-compatible access to 500+ AI models (GPT-5, Claude 4.5, Gemini 3 Pro, DeepSeek, etc.). Designed for users who face barriers with direct Western AI provider subscriptions.

## Quick Config

```
Base URL:  https://api.n1n.ai/v1   (global)
           https://hk.n1n.ai/v1     (HK mirror, lower latency in Asia)
Auth:      API Key (Bearer token or `api_key` field)
Protocol:  OpenAI-compatible — drop-in replacement for any OpenAI SDK
```

## SDK Usage

### Python (openai SDK)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.n1n.ai/v1",
    api_key="YOUR_N1N_API_KEY"
)

response = client.chat.completions.create(
    model="gpt-5",  # model names from Model Plaza
    messages=[{"role": "user", "content": "Hello"}]
)
```

### JavaScript/TypeScript
```typescript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://api.n1n.ai/v1",
  apiKey: "YOUR_N1N_API_KEY",
});

const response = await client.chat.completions.create({
  model: "gpt-5",
  messages: [{ role: "user", content: "Hello" }],
});
```

### curl
```bash
curl https://api.n1n.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_N1N_API_KEY" \
  -d '{
    "model": "gpt-5",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `/v1/chat/completions` | Chat completions (streaming supported) |
| `/v1/responses` | OpenAI Responses API |

Supports all standard OpenAI parameters: `temperature`, `max_tokens`, `top_p`, `stream`, `tools`, `response_format`, etc.

## Getting an API Key

1. Go to https://api.n1n.ai/console
2. Navigate to **Tokens** (令牌) page
3. Click **Add Token** (添加令牌)
4. Copy the key — **shown only once**

New users receive **$0.20** free credit. Payment methods: Alipay, WeChat Pay, Stripe, USDT. Exchange rate: 1 RMB = 1 USD credit.

## API Key (from env)

```bash
# Available in shell as env vars (sourced from ~/.zshrc via 1Password)
$N1N_API_KEY          # primary nano key
$N1N_API_KEY_2        # nano key 2
$N1N_API_KEY_CLAUDE   # hermesclaude01 key
```

Use `$N1N_API_KEY` by default. Retrieve live: `source ~/.zshrc && echo $N1N_API_KEY`

## Key Models (verified 2026-05-27 via `/v1/models`)

### Claude (Anthropic)
| Model ID | Notes |
|----------|-------|
| `claude-sonnet-4-6` | Current Sonnet — best balance |
| `claude-opus-4-7` | Most capable Claude |
| `claude-opus-4-6` | Previous Opus |
| `claude-haiku-4-5-20251001` | Fastest/cheapest Claude |

### OpenAI
| Model ID | Notes |
|----------|-------|
| `gpt-5` | Latest flagship |
| `gpt-4.1` | Strong, cost-effective |
| `gpt-4o` | Multimodal |
| `o3` | Reasoning flagship |
| `o3-pro` | Max reasoning |

### DeepSeek
| Model ID | Notes |
|----------|-------|
| `deepseek-r1` | Reasoning flagship |
| `deepseek-r1-0528` | Latest R1 checkpoint |
| `deepseek-chat` | V3 chat (fast) |
| `deepseek-v3` | V3 explicit |

### Grok (xAI)
| Model ID | Notes |
|----------|-------|
| `grok-4` | Latest flagship |
| `grok-4-fast` | Faster variant |

Full live list: `curl -s https://api.n1n.ai/v1/models -H "Authorization: Bearer $N1N_API_KEY" | jq '[.data[].id] | sort'`

## Finding Model Names

Visit the **Model Plaza** (模型广场) at https://api.n1n.ai/console for the current model catalog. Model names must match **exactly** as listed.

## Debugging

Use the online debugger at https://docs.n1n.ai/llm-api-debug to test requests before coding:
1. Set your API key in environment variables (local-only, never synced)
2. Send test requests to validate auth and model availability
3. Requires [Apifox Browser Extension](https://apifox.com/help/applications-and-plugins/browser-extensions/microsoft-edge) if using browser

## Key Notes

- **OpenAI-compatible** — any SDK or tool that works with OpenAI just needs `base_url` changed
- **Single key for all models** — one API key unlocks all 500+ models
- **Use https://hk.n1n.ai/v1** if you're in Asia for lower latency
- **Model names may change** — always verify in the Model Plaza before hardcoding
- **Rate limits** — not documented publicly, check your token's quota in the console
