
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "").strip()

if not api_key:
    raise ValueError("GEMINI_API_KEY পাওয়া যায়নি। .env পরীক্ষা করো।")

url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.5-flash:generateContent"
)

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key,
}

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Reply with only: API connection successful"
                }
            ]
        }
    ],
    "generationConfig": {
        "maxOutputTokens": 30,
        "temperature": 0
    }
}

print("Testing direct Gemini API connection...")

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    print("HTTP status:", response.status_code)

    if response.ok:
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        print("Gemini response:", text)
    else:
        print("API error:", response.text[:1500])

except requests.RequestException as error:
    print("Connection error:", type(error).__name__, str(error))
