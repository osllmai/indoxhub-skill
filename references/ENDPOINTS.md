# IndoxHub Endpoints — Complete Reference

All examples use `INDOXHUB_API_KEY` from environment. Base URL: `https://api.indoxhub.com`

---

## Chat completions

**POST** `/chat/completions`

### Request

```json
{
  "provider": "openai",
  "model": "gpt-4o-mini",
  "messages": [{"role": "user", "content": "Hello"}],
  "temperature": 0.7,
  "max_tokens": 100,
  "top_p": 1.0,
  "frequency_penalty": 0,
  "presence_penalty": 0,
  "stream": false
}
```

### Response (non-streaming)

```json
{
  "id": "uuid",
  "object": "response",
  "created_at": 1777002220,
  "model": "gpt-4o-mini",
  "provider": "openai",
  "duration_ms": 1172.3,
  "output": [
    {
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {"type": "output_text", "text": "Hi there", "annotations": []}
      ]
    }
  ],
  "usage": {
    "input_tokens": 11,
    "output_tokens": 2,
    "total_tokens": 13
  },
  "status": "completed"
}
```

**Extract the text:** `response["output"][0]["content"][0]["text"]`

### Python

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
print(r.json()["output"][0]["content"][0]["text"])
```

### curl

```bash
curl -X POST https://api.indoxhub.com/chat/completions \
  -H "Authorization: Bearer $INDOXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"provider":"openai","model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}'
```

For streaming, see [STREAMING.md](STREAMING.md).

---

## Embeddings

**POST** `/embeddings`

### Request

```json
{
  "provider": "openai",
  "model": "text-embedding-3-small",
  "text": "hello world"
}
```

Note: field is **`text`**, not `input`. Accepts string or array of strings.

### Response

```json
{
  "request_id": "uuid",
  "provider": "openai",
  "model": "text-embedding-3-small",
  "dimensions": 1536,
  "success": true,
  "data": [0.0123, -0.045, ...],
  "usage": {"tokens_prompt": 2, "tokens_total": 2}
}
```

**Extract vector:** `response["data"]` (flat array of floats, length = `dimensions`)

### Python

```python
import requests, os
r = requests.post(
    "https://api.indoxhub.com/embeddings",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={"provider": "openai", "model": "text-embedding-3-small", "text": "hello"}
)
vector = r.json()["data"]  # list of 1536 floats
```

---

## Image generation

**POST** `/images/generations`

### Request

```json
{
  "provider": "openai",
  "model": "gpt-image-1",
  "prompt": "a red apple on a white table",
  "size": "1024x1024",
  "n": 1,
  "quality": "standard"
}
```

Note: `dall-e-3` is deprecated. Use `gpt-image-1` or `gpt-image-1.5`.

### Response

Wrapped response. `data` contains URLs or base64 per the `response_format` you asked for.

### Python

```python
import requests, os
r = requests.post(
    "https://api.indoxhub.com/images/generations",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={
        "provider": "openai",
        "model": "gpt-image-1",
        "prompt": "a red apple",
        "size": "1024x1024",
        "n": 1
    }
)
print(r.json())
```

---

## Video generation

**POST** `/videos/generations`

### Request

```json
{
  "provider": "openai",
  "model": "sora-2",
  "prompt": "a 3-second sunset over the ocean",
  "duration": 3,
  "resolution": "720p",
  "aspect_ratio": "16:9"
}
```

Available models:
- `openai/sora-2`, `openai/sora-2-pro`
- `google/veo-2.0-generate-001`, `google/veo-3.0-generate-001`
- `luma/` (see MODELS.md)

### Response

Returns a job descriptor. For async polling, see the video jobs endpoints:
- `GET /videos/jobs/{job_id}` — check status
- `GET /videos/jobs` — list jobs
- `POST /videos/jobs/{job_id}/cancel` — cancel

### Python

```python
import requests, os, time

r = requests.post(
    "https://api.indoxhub.com/videos/generations",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={"provider": "google", "model": "veo-3.0-generate-001", "prompt": "sunset"}
)
job = r.json()
job_id = job.get("data", {}).get("job_id") or job.get("request_id")

# Poll
while True:
    status = requests.get(
        f"https://api.indoxhub.com/videos/jobs/{job_id}",
        headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"}
    ).json()
    if status.get("status") == "completed":
        print(status["data"]["url"])
        break
    time.sleep(5)
```

---

## Text-to-speech (TTS)

**POST** `/audio/tts/generations`

### Request

```json
{
  "provider": "openai",
  "model": "tts-1",
  "voice": "alloy",
  "input": "Hello, world",
  "response_format": "mp3",
  "speed": 1.0
}
```

### Response

JSON wrapper with base64 audio payload:

```json
{
  "success": true,
  "data": {
    "audio": "//PkxAB...(base64 mp3)...",
    "format": "mp3",
    "voice": "alloy",
    "speed": 1.0,
    "character_count": 12
  }
}
```

**Decode:** `base64.b64decode(response["data"]["audio"])` → write bytes to `.mp3`.

### Python

```python
import requests, base64, os

r = requests.post(
    "https://api.indoxhub.com/audio/tts/generations",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={
        "provider": "openai",
        "model": "tts-1",
        "voice": "alloy",
        "input": "Hello, world"
    }
)
audio_b64 = r.json()["data"]["audio"]
with open("out.mp3", "wb") as f:
    f.write(base64.b64decode(audio_b64))
```

---

## Speech-to-text (STT)

**POST** `/audio/stt/transcriptions`

### Request (multipart form)

Fields:
- `provider` — e.g. `openai`
- `model` — e.g. `whisper-1`
- `file` — audio file upload

### Response

```json
{
  "request_id": "uuid",
  "provider": "openai",
  "model": "whisper-1",
  "success": true,
  "data": {"text": "transcribed content"},
  "usage": {...}
}
```

### Python

```python
import requests, os

with open("audio.mp3", "rb") as f:
    r = requests.post(
        "https://api.indoxhub.com/audio/stt/transcriptions",
        headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
        data={"provider": "openai", "model": "whisper-1"},
        files={"file": f}
    )
print(r.json()["data"]["text"])
```

### curl

```bash
curl -X POST https://api.indoxhub.com/audio/stt/transcriptions \
  -H "Authorization: Bearer $INDOXHUB_API_KEY" \
  -F provider=openai \
  -F model=whisper-1 \
  -F file=@audio.mp3
```

---

## Providers

**GET** `/providers/`

Returns the full provider catalog with capabilities and metadata.

```python
import requests, os
r = requests.get(
    "https://api.indoxhub.com/providers/",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"}
)
```

---

## Models by provider + capability

**GET** `/models/{provider}/{capability}`

Capability values: `text_completions`, `embeddings`, `image_generation`, `video_generation`, `text_to_speech`, `speech_to_text`

```bash
curl https://api.indoxhub.com/models/openai/text_completions \
  -H "Authorization: Bearer $INDOXHUB_API_KEY"
```

Each model object has:
- `modelName` — **canonical ID** (use this in request bodies)
- `name` — display string
- `provider` — provider slug
- `pricing`, `specs`, `capabilities`, `metadata`

See `references/MODELS.md` for the grouped catalog. See `scripts/list_models.py` to regenerate.
