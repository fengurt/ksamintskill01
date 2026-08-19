# Official providers — quirks & notes

All OpenAI-compatible (`/chat/completions`, `Authorization: Bearer`) unless noted. Base URLs and keys come from [../registry.tsv](../registry.tsv).

## ali-tongyi (Qwen / 通义) — Bailian Token Plan
- Plan endpoint needs the **`sk-sp-…` seat key** (115 chars), NOT the standard `sk-` key — the standard key 401s here. Item `Aliyun_apuch与子同泽`, field `seat_…` (=op_ref). The 35-char `api-ID-2231532` field is the pay-as-you-go key for `dashscope.aliyuncs.com` only.
- Reasoning is on by default for `qwen3.7-max` (returns `reasoning_content`); budget `max_tokens`. Full detail: the dedicated `ali-tongyi` skill.

## openai
- Standard. Item `OpenAI API Key`. Watch model availability per account.

## anthropic — **protocol = anthropic**
- Uses `/v1/messages`, headers `x-api-key` + `anthropic-version: 2023-06-01`, and `max_tokens` is **required**. The loader/scripts handle this automatically. Item `Anthropic Culling` (field `Claude301 api key`; `dify01` is an alternate).

## deepseek
- Item `DeepSeek135` has 4 keys (`dify01`/`GoR101`/`cursor01`/`api-key-sale01`); registry uses `cursor01`. Models: `deepseek-chat` (V3, fast), `deepseek-reasoner` (R1). Supports `thinking`/`reasoning_content`.

## ark (Volcengine 火山方舟 / Doubao 豆包)
- Base already includes `/api/v3` — **do not add `/v1`** (→ 404). You can use a custom **endpoint ID** as the `model`. Item `API 火山Axisee`. Voice (TTS/ASR) is a separate service — see the `ark-api` skill.

## moonshot (Kimi)
- `api.moonshot.cn/v1`. Item `kimi api`, field `claw01`. Models: `moonshot-v1-8k/32k/128k`, `kimi-k2-*`. (Kimi via the Ali Token Plan is a different path/model id.)

## minimax
- `api.minimaxi.com/v1` (OpenAI mode) or `/anthropic`. Item `Minimaxi-use-api-apuch与子`, field `订阅key` (CJK label — referenced by field ID). There is also a JWT-style `api-key-test002`.

## together
- `api.together.xyz/v1`. Item `Together_githubpilo`. No default model set — pass one (e.g. a Llama/Qwen id from `list_models.sh together`).

## EMPTY (add key, then set op_ref in registry.tsv)
- **gemini** — item `Google_Gemini api Meta` has no key field. Use the OpenAI-compat base `…/v1beta/openai`.
- **xai-grok** — only a reseller login (`Trygrokai`); no official xAI key. Official base `api.x.ai/v1`.
- **nvidia** — item `NVIDIA_api_AI` is login only. Base `integrate.api.nvidia.com/v1`.
- **fireworks** — item `Fireworks_API` has no key field. Base `api.fireworks.ai/inference/v1`.
- **zhipu-glm** — no 1Password item yet. Base `open.bigmodel.cn/api/paas/v4`, models `glm-4*`.
