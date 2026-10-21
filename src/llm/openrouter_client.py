
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from src.llm.base import LLMClient
from src.llm.response import LLMResponse
from config.llm_config import LLM_MAX_TOKENS


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class OpenRouterClient(LLMClient):
    """Send prompts to an OpenRouter chat model."""

    def __init__(
        self,
        model: str = "openrouter/free",
        timeout: int = 60,
    ):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

    def generate(self, prompt: str) -> LLMResponse:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": LLM_MAX_TOKENS,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        data = response.json()

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("OpenRouter returned no choices.")

        choice = choices[0]
        content = choice.get("message", {}).get("content")

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("OpenRouter returned empty content.")

        return LLMResponse(
            content=content,
            provider="openrouter",
            model=data.get("model", self.model),
            finish_reason=choice.get("finish_reason"),
        )
