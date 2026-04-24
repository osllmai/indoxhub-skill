---
name: indoxhub
description: Call 233+ LLMs from 9 providers (OpenAI, Anthropic, Google, Mistral, xAI, Qwen, DeepSeek, Luma, Resemble) through a single unified API at api.indoxhub.com. Covers chat completions with SSE streaming, embeddings, image generation, video generation (Sora, Veo, Luma), text-to-speech, and speech-to-text. Use this skill when the user wants to call any LLM, generate media (images, videos, audio), transcribe or synthesize speech, compare outputs across multiple providers, or build multi-modal AI applications without switching SDKs. Response format follows OpenAI's Responses API shape, not Chat Completions.
license: MIT
metadata:
  author: osllmai
  version: "0.1.0"
  homepage: "https://indoxhub.com"
  api_base: "https://api.indoxhub.com"
---

# IndoxHub

Unified LLM gateway. One API key, one OpenAI-compatible interface, 233+ verified models across 9 providers and 6 modalities.

## When to use this skill

Activate this skill when the user wants to:
- Call any LLM (OpenAI, Anthropic, Google, Mistral, xAI, Qwen, DeepSeek)
- Generate images (OpenAI `gpt-image-1`, Google Imagen, xAI, Qwen)
- Generate videos (OpenAI Sora, Google Veo, Luma)
- Synthesize speech (TTS) or transcribe audio (STT)
- Compute embeddings for semantic search, RAG, clustering
- Compare outputs across providers without juggling SDKs
- Stream chat responses (SSE)

## Authentication

Every request uses a bearer token.

```bash
export INDOXHUB_API_KEY="indox-..."
curl -H "Authorization: Bearer $INDOXHUB_API_KEY" ...
```

Get a key at https://indoxhub.com

## Base URL

All endpoints: `https://api.indoxhub.com`

## Universal request pattern

Every request body includes at minimum:
- `provider` — provider slug (e.g. `openai`, `anthropic`, `google`)
- `model` — model ID from that provider (see `references/MODELS.md`)

Every response is wrapped:
```json
{
  "request_id": "uuid",
  "created_at": "ISO-8601",
  "duration_ms": 1234.5,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "success": true,
  "usage": { ... },
  "data": { ... }      // or "output" for chat
}
```

## Endpoints at a glance

| Capability | Method + Path | Reference |
|---|---|---|
| Chat completion | `POST /chat/completions` | [ENDPOINTS.md](references/ENDPOINTS.md#chat-completions) |
| Chat streaming | `POST /chat/completions` with `stream:true` | [STREAMING.md](references/STREAMING.md) |
| Embeddings | `POST /embeddings` | [ENDPOINTS.md](references/ENDPOINTS.md#embeddings) |
| Image generation | `POST /images/generations` | [ENDPOINTS.md](references/ENDPOINTS.md#images) |
| Video generation | `POST /videos/generations` | [ENDPOINTS.md](references/ENDPOINTS.md#videos) |
| Text-to-speech | `POST /audio/tts/generations` | [ENDPOINTS.md](references/ENDPOINTS.md#tts) |
| Speech-to-text | `POST /audio/stt/transcriptions` | [ENDPOINTS.md](references/ENDPOINTS.md#stt) |
| List models by provider+capability | `GET /models/{provider}/{capability}` | [MODELS.md](references/MODELS.md) |
| List providers | `GET /providers/` | [ENDPOINTS.md](references/ENDPOINTS.md#providers) |

## Quickstart — chat

```python
import requests, os

r = requests.post(
    "https://api.indoxhub.com/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={
        "provider": "openai",
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 100
    }
)
# Response format = OpenAI Responses API shape
text = r.json()["output"][0]["content"][0]["text"]
print(text)
```

## Critical — response shape is NOT OpenAI Chat Completions

IndoxHub uses OpenAI's **Responses API** format. Do not reach for `choices[0].message.content` — it does not exist.

**Chat response path:** `response.output[0].content[0].text`
**Streaming event type:** `response.content_part.delta` with `delta` field
**Embeddings vector:** `response.data` (array of floats, flat — not wrapped in `data[0].embedding`)
**Embedding dimensions:** `response.dimensions` (top-level field)

See `references/ENDPOINTS.md` for every shape with a working example.

## Model discovery pattern

Models are scoped by provider and capability. There is no flat `/models` list.

```python
# List OpenAI chat models
r = requests.get(
    "https://api.indoxhub.com/models/openai/text_completions",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"}
)
# Each model object has `modelName` (canonical ID) and `name` (display)
for m in r.json():
    print(m["modelName"], "-", m["name"])
```

**Canonical ID field is `modelName`**, not `id`. The `id` field is a display string like `"GPT-4o-mini"`. Always send `modelName` as the `model` in request bodies.

See `scripts/list_models.py` for a working model discovery script.

## Streaming

Chat streaming uses Server-Sent Events. Set `stream: true` in the request body. See `references/STREAMING.md` for event format and parsing examples in Python, JS, and curl.

## Errors

Errors return HTTP 4xx/5xx with JSON body:
```json
{ "detail": "Model '...' is not supported or configured for provider '...'" }
```

Common cases:
- `401` — invalid or missing bearer token
- `402` — insufficient credits (top up at https://indoxhub.com)
- `404` — model not found for provider (check `modelName`)
- `429` — rate limit hit (backoff + retry)
- `500` — upstream provider issue

## Common patterns

**Multi-provider comparison** (see `references/EXAMPLES.md`):
Loop the same prompt through OpenAI, Anthropic, and Google — all via IndoxHub, same request shape.

**Embedding + chat RAG** (see `references/EXAMPLES.md`):
Embed a query with OpenAI, retrieve, send context to Claude — all one API.

**Video generation with polling** (see `references/EXAMPLES.md`):
POST `/videos/generations` → returns job — poll for completion.

## Supported providers and capability matrix (verified)

```
Provider    Chat  Embed  Image  Video  TTS  STT
────────────────────────────────────────────────
OpenAI       55     3      5      2     3    3
Google       35     4      4      5     2    0
Anthropic    22     0      0      0     0    0
Mistral      35     1      0      0     0    0
xAI          15     0      3      0     0    0
Qwen         28     1      2      0     0    0
DeepSeek      5     0      0      0     0    0
Luma          0     0      0      1     0    0
Resemble      0     0      0      0     1    1
────────────────────────────────────────────────
Total       195    9     14      7     5    3
```

## References

- [`references/ENDPOINTS.md`](references/ENDPOINTS.md) — full schema + curl/Python/JS examples per endpoint
- [`references/MODELS.md`](references/MODELS.md) — canonical model IDs grouped by provider + capability
- [`references/STREAMING.md`](references/STREAMING.md) — SSE event format and streaming code
- [`references/EXAMPLES.md`](references/EXAMPLES.md) — 8 full use-case walkthroughs
- [`scripts/list_models.py`](scripts/list_models.py) — regenerable model catalog script

## Not supported in v1

- Web scraping (roadmap)
- Admin, user management, payments, analytics endpoints (out of scope for coding agents)
