#!/usr/bin/env python3
"""List IndoxHub models grouped by provider and capability.

Usage:
    INDOXHUB_API_KEY=indox-... python scripts/list_models.py
    INDOXHUB_API_KEY=indox-... python scripts/list_models.py > references/MODELS.md

Regenerates MODELS.md from the live catalog. Safe to run anytime.
"""
import os
import sys
import urllib.request
import urllib.error
import json

BASE = "https://api.indoxhub.com"
PROVIDERS = ["openai", "anthropic", "google", "mistral", "xai",
             "qwen", "deepseek", "luma", "resemble"]
CAPABILITIES = [
    ("text_completions", "Chat"),
    ("embeddings", "Embeddings"),
    ("image_generation", "Image generation"),
    ("video_generation", "Video generation"),
    ("text_to_speech", "Text-to-speech"),
    ("speech_to_text", "Speech-to-text"),
]


def fetch(provider: str, capability: str, key: str) -> list:
    url = f"{BASE}/models/{provider}/{capability}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "User-Agent": "indoxhub-skill/0.1 (+https://github.com/osllmai/indoxhub-skill)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            return data if isinstance(data, list) else []
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        return []


def main() -> int:
    key = os.environ.get("INDOXHUB_API_KEY")
    if not key:
        print("ERROR: set INDOXHUB_API_KEY", file=sys.stderr)
        return 1

    print("# IndoxHub — Model Catalog\n")
    print("Regenerate: `python scripts/list_models.py > references/MODELS.md`\n")

    for provider in PROVIDERS:
        lines = []
        for cap_slug, cap_label in CAPABILITIES:
            models = fetch(provider, cap_slug, key)
            enabled = [m for m in models if not m.get("is_disabled")]
            if enabled:
                ids = ", ".join(f"`{m.get('modelName', '?')}`" for m in enabled[:20])
                extra = f" (+{len(enabled)-20} more)" if len(enabled) > 20 else ""
                lines.append(f"- **{cap_label}:** {ids}{extra}")
        if lines:
            print(f"## {provider}\n")
            print("\n".join(lines))
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
