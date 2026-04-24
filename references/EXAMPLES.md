# IndoxHub — Real Use-Case Examples

8 working examples. Every request uses `INDOXHUB_API_KEY` from env. Base URL: `https://api.indoxhub.com`

---

## 1. Chat with GPT-4o-mini

```python
import requests, os

r = requests.post(
    "https://api.indoxhub.com/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={
        "provider": "openai",
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Explain recursion in one sentence."}],
        "max_tokens": 100
    }
)
print(r.json()["output"][0]["content"][0]["text"])
```

---

## 2. Compare Claude vs GPT-4 on the same prompt

```python
import requests, os

prompt = "What is 2+2? Answer with just the number."
key = os.environ["INDOXHUB_API_KEY"]
url = "https://api.indoxhub.com/chat/completions"
headers = {"Authorization": f"Bearer {key}"}

for provider, model in [("openai", "gpt-4o-mini"), ("anthropic", "Claude Sonnet 4.6")]:
    r = requests.post(url, headers=headers, json={
        "provider": provider,
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 20
    })
    text = r.json()["output"][0]["content"][0]["text"]
    print(f"{provider}: {text}")
```

Every call hits the same endpoint with the same shape. No SDK swap.

---

## 3. Generate an embedding for semantic search

```python
import requests, os

r = requests.post(
    "https://api.indoxhub.com/embeddings",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={
        "provider": "openai",
        "model": "text-embedding-3-small",
        "text": "the quick brown fox"
    }
)
vector = r.json()["data"]          # flat list of 1536 floats
dims = r.json()["dimensions"]      # 1536
print(f"Vector of {dims} dims, first 5: {vector[:5]}")
```

---

## 4. Generate an image with gpt-image-1

```python
import requests, os

r = requests.post(
    "https://api.indoxhub.com/images/generations",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={
        "provider": "openai",
        "model": "gpt-image-1",
        "prompt": "a robot painting a sunset, oil on canvas",
        "size": "1024x1024",
        "n": 1
    }
)
print(r.json())
```

---

## 5. Generate a short video with Google Veo

```python
import requests, os, time

key = os.environ["INDOXHUB_API_KEY"]
headers = {"Authorization": f"Bearer {key}"}

# Submit
r = requests.post(
    "https://api.indoxhub.com/videos/generations",
    headers=headers,
    json={
        "provider": "google",
        "model": "veo-3.0-generate-001",
        "prompt": "a 3-second clip of waves on a beach",
        "duration": 3
    }
)
job = r.json()
job_id = job.get("data", {}).get("job_id") or job["request_id"]

# Poll
while True:
    s = requests.get(
        f"https://api.indoxhub.com/videos/jobs/{job_id}",
        headers=headers
    ).json()
    if s.get("status") == "completed":
        print("URL:", s["data"].get("url"))
        break
    time.sleep(5)
```

---

## 6. Synthesize speech (TTS) and save to MP3

```python
import requests, base64, os

r = requests.post(
    "https://api.indoxhub.com/audio/tts/generations",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={
        "provider": "openai",
        "model": "tts-1",
        "voice": "alloy",
        "input": "Hello from IndoxHub."
    }
)
audio_b64 = r.json()["data"]["audio"]
with open("output.mp3", "wb") as f:
    f.write(base64.b64decode(audio_b64))
print("Saved output.mp3")
```

---

## 7. Transcribe an audio file (STT)

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

---

## 8. Build a streaming chatbot (CLI)

```python
import requests, json, os

r = requests.post(
    "https://api.indoxhub.com/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={
        "provider": "openai",
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Count to 5."}],
        "stream": True,
        "max_tokens": 50
    },
    stream=True
)

for line in r.iter_lines(decode_unicode=True):
    if not line or not line.startswith("data: "):
        continue
    payload = line[6:]
    if payload == "[DONE]":
        break
    evt = json.loads(payload)
    if evt.get("type") == "response.content_part.delta":
        print(evt.get("delta", ""), end="", flush=True)
print()
```

See `../STREAMING.md` for the full event reference and JS/Node parser.
