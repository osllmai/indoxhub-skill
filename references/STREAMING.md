# IndoxHub — SSE Streaming Reference

IndoxHub streams chat completions using Server-Sent Events (SSE). Response events follow OpenAI's **Responses API** streaming shape, not Chat Completions.

---

## Activate streaming

Set `"stream": true` in any request to `POST /chat/completions`.

```bash
curl -N -X POST https://api.indoxhub.com/chat/completions \
  -H "Authorization: Bearer $INDOXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"provider":"openai","model":"gpt-4o-mini","messages":[{"role":"user","content":"count to 3"}],"stream":true,"max_tokens":20}'
```

The `-N` flag disables curl's output buffering, letting you see events arrive live.

---

## Event format

Each event is one line beginning with `data: ` followed by JSON. Events are separated by blank lines. The stream ends when the server closes the connection; some clients emit a terminal `data: [DONE]`.

Observed event types during a completion:

| Type | When | Key fields |
|---|---|---|
| `response.created` | Stream starts | `response.id`, `response.model`, `response.status` |
| `response.output_item.added` | A new output message begins | `output_index`, `item` |
| `response.content_part.added` | Content part container opens | `output_index`, `content_index`, `part` |
| `response.content_part.delta` | Token chunk arrives | `delta` (the text to append) |
| `response.content_part.done` | Content part complete | final `part` snapshot |
| `response.output_item.done` | Output item complete | `item` with final content |
| `response.completed` | Full response done | `response` with usage totals |

**The field you append to your UI is `event.delta`** on `response.content_part.delta` events.

---

## Example event sequence

```
data: {"type": "response.created", "response": {"id": "abc", "status": "in_progress", "model": "openai/gpt-4o-mini"}}

data: {"type": "response.output_item.added", "response_id": "abc", "output_index": 0, "item": {"type": "message", "role": "assistant", "status": "in_progress", "content": []}}

data: {"type": "response.content_part.added", "response_id": "abc", "output_index": 0, "content_index": 0, "part": {"type": "output_text", "text": ""}}

data: {"type": "response.content_part.delta", "response_id": "abc", "output_index": 0, "content_index": 0, "delta": "1"}

data: {"type": "response.content_part.delta", "response_id": "abc", "output_index": 0, "content_index": 0, "delta": ","}

data: {"type": "response.content_part.delta", "response_id": "abc", "output_index": 0, "content_index": 0, "delta": " 2"}

data: {"type": "response.content_part.delta", "response_id": "abc", "output_index": 0, "content_index": 0, "delta": ", 3"}

data: {"type": "response.completed", "response": {"id": "abc", "status": "completed", "usage": {"input_tokens": 12, "output_tokens": 6}}}
```

---

## Python — minimal parser

```python
import requests, json, os

r = requests.post(
    "https://api.indoxhub.com/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['INDOXHUB_API_KEY']}"},
    json={
        "provider": "openai",
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Write a haiku about streams."}],
        "stream": True,
        "max_tokens": 60
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
    elif evt.get("type") == "response.completed":
        usage = evt["response"].get("usage", {})
        print(f"\n[tokens: {usage.get('total_tokens')}]")
```

---

## Node.js / TypeScript — fetch + ReadableStream

```javascript
const res = await fetch("https://api.indoxhub.com/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${process.env.INDOXHUB_API_KEY}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    provider: "openai",
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: "Count to 5." }],
    stream: true,
    max_tokens: 40
  })
});

const reader = res.body.getReader();
const decoder = new TextDecoder();
let buf = "";

while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  buf += decoder.decode(value, { stream: true });
  const lines = buf.split("\n");
  buf = lines.pop();  // keep partial line
  for (const line of lines) {
    if (!line.startsWith("data: ")) continue;
    const payload = line.slice(6);
    if (payload === "[DONE]") return;
    const evt = JSON.parse(payload);
    if (evt.type === "response.content_part.delta") {
      process.stdout.write(evt.delta || "");
    }
  }
}
```

---

## Browser — EventSource alternative with fetch

`EventSource` does not support custom headers in browsers, so use `fetch` + reader (same pattern as Node above). For a server-side proxy example, see any SSE tutorial — the event parsing is identical.

---

## Common gotchas

1. **Don't look for `choices[0].delta.content`.** IndoxHub uses Responses API shape. The field is `event.delta` on `response.content_part.delta` events.
2. **Buffering:** if streaming feels "chunky" or arrives all at once, your client is buffering. Use `-N` with curl, `stream=True` in `requests`, or raw `ReadableStream` in JS.
3. **Proxies:** Cloudflare is in front of IndoxHub. SSE passes through, but some corporate proxies buffer or kill long connections. Test from a clean network first.
4. **Partial JSON lines:** always buffer until you hit `\n\n` (event boundary) when parsing manually.
5. **Errors mid-stream:** a failed provider can emit a final event with `response.status: "failed"` or close the connection. Handle both.

---

## Related

- [ENDPOINTS.md](ENDPOINTS.md#chat-completions) — full chat request/response schema
- [EXAMPLES.md](EXAMPLES.md) — use case 8 is a complete streaming CLI chatbot
