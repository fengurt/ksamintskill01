---
name: ark-api
description: Use 火山方舟 (Volcengine Ark) API — Doubao/豆包 LLM, TTS speech synthesis, ASR speech recognition. Use when the user wants Doubao models, Chinese TTS/ASR, or Volcengine AI.
---

# 火山方舟 Ark API

Volcengine Ark — ByteDance AI platform. OpenAI-compatible LLM API + speech/voice services (TTS + ASR).

## Quick Config

```
LLM Base URL:  https://ark.cn-beijing.volces.com/api/v3
Auth:          Bearer token (API Key from console)
Protocol:      OpenAI-compatible — drop-in replacement for any OpenAI SDK
```

## Chat Completions (LLM)

### Endpoint
```
POST https://ark.cn-beijing.volces.com/api/v3/chat/completions
```

### Python
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="YOUR_ARK_API_KEY",
)

response = client.chat.completions.create(
    model="doubao-seed-1-6-250615",  # or endpoint ID
    messages=[{"role": "user", "content": "你好"}],
)
print(response.choices[0].message.content)
```

### JavaScript
```typescript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://ark.cn-beijing.volces.com/api/v3",
  apiKey: "YOUR_ARK_API_KEY",
});

const response = await client.chat.completions.create({
  model: "doubao-seed-1-6-250615",
  messages: [{ role: "user", content: "你好" }],
});
```

### curl
```bash
curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seed-1-6-250615",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

## Common LLM Models

| Model ID | Description |
|----------|-------------|
| `doubao-seed-1-6-250615` | 豆包 Seed 1.6 — latest flagship, reasoning |
| `doubao-1-5-pro-32k-250115` | 豆包 1.5 Pro 32K — solid general purpose |
| `doubao-1-5-lite-32k-250115` | 豆包 1.5 Lite 32K — fast/cheap |
| `doubao-1.5-vision-pro-32k` | Vision model (multimodal) |

> Use your **endpoint ID** (from console) as the model name for custom deployment configs.

## Supported Features

- **Streaming:** `stream: true`
- **Deep Thinking:** Models return `reasoning_content` in response
- **Function Calling / Tools:** Supported via standard `tools` parameter
- **JSON Mode:** `response_format: {"type": "json_object"}`
- **Context Cache:** Auto disk cache for prompt prefixes
- **Vision:** `doubao-1.5-vision-pro-32k` supports image input

---

## Voice / Speech Models

Volcengine voice services use a **separate** service from Ark LLM. Different base URL, different auth.

### Base URL for Voice
```
https://openspeech.bytedance.com
```

### Authentication for Voice

Voice services use **Bearer token with semicolon** (NOT the same as Ark API Key):

```http
Authorization: Bearer; <SPEECH_ACCESS_TOKEN>
```

Or HMAC256 signature auth:
```http
Authorization: HMAC256; access_token="<TOKEN>"; mac="<SIGNATURE>"; h="Host,Resource-Id"
```

### TTS — Text to Speech

| Method | Endpoint | Notes |
|--------|----------|-------|
| Async (long text) | `POST /api/v1/tts_async` | Submit task → poll result |
| Streaming | WebSocket | Real-time audio streaming |

**Async TTS flow:**
1. Submit: `POST /api/v1/tts_async` with `appid`, text, voice type
2. Poll: `GET /api/v1/tts_async/query?appid=<APP_ID>&task_id=<TASK_ID>` with `Authorization: Bearer; <TOKEN>`

**Common voice types:** `BV001_V2_streaming` (streaming), `BV007_***ming` (standard)

### ASR — Speech Recognition

| Method | Endpoint | Notes |
|--------|----------|-------|
| Streaming | WebSocket | Real-time speech-to-text |
| Batch | (refer to docs) | File-based recognition |

### Python TTS Example
```python
import requests

# Submit TTS task
resp = requests.post(
    "https://openspeech.bytedance.com/api/v1/tts_async",
    headers={
        "Authorization": f"Bearer; {SPEECH_TOKEN}",
        "Resource-Id": "volc.tts_async.default",
        "Content-Type": "application/json",
    },
    json={
        "app": {"appid": APP_ID},
        "request": {
            "text": "你好世界",
            "voice_type": "BV001_V2_streaming",
            "encoding": "mp3",
        },
    },
)
task_id = resp.json()["task_id"]

# Poll result
result = requests.get(
    f"https://openspeech.bytedance.com/api/v1/tts_async/query?appid={APP_ID}&task_id={task_id}",
    headers={
        "Authorization": f"Bearer; {SPEECH_TOKEN}",
        "Resource-Id": "volc.tts_async.default",
    },
)
```

---

## Getting Credentials

| Credential | Console URL |
|-----------|-------------|
| **Ark API Key** (LLM) | https://console.volcengine.com/ark → Endpoint → API Access |
| **Endpoint ID** | https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint |
| **TTS APP ID + Token** | https://console.volcengine.com/speech/service/8 |
| **ASR APP ID + Token** | https://console.volcengine.com/speech/service/16 |
| **AK/SK** (IAM) | https://console.volcengine.com/iam/keymanage |

## Key Notes

- **OpenAI-compatible** — any OpenAI SDK works, just change `base_url`
- **Voice is separate** — TTS/ASR uses `openspeech.bytedance.com`, NOT `ark.cn-beijing.volces.com`
- **Voice auth is different** — semicolon Bearer token (`Bearer; <token>`), not regular Bearer
- **Don't repeat `/v1`** — the base already includes `/api/v3`. Using `/v1` creates 404.
- **Endpoint ID as model** — you can use your custom endpoint ID as the `model` parameter
- **Enterprise cert required** — voice models currently require enterprise certification
