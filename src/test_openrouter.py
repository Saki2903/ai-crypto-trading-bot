import os
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise SystemExit("ERROR: OpenRouter API key not found.")

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "openrouter/free",
        "messages": [
            {"role": "user", "content": "Reply with exactly: OK"}
        ],
        "max_tokens": 300,
    },
    timeout=60,
)

print("HTTP status:", response.status_code)

data = response.json()

if response.ok and data.get("choices"):
    choice = data["choices"][0]
    print("Model:", data.get("model"))
    print("Finish reason:", choice.get("finish_reason"))
    print("AI reply:", repr(choice.get("message", {}).get("content")))
else:
    error = data.get("error", {})
    print("API error:", error.get("message", "No response returned"))