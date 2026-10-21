
import ollama
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.llm_config import (
    OLLAMA_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
)

from .base import LLMClient
from .response import LLMResponse


class OllamaClient(LLMClient):
    """LLM client for local Ollama models."""

    def __init__(self, model: str = OLLAMA_MODEL):
        self.model = model

    def generate(self, prompt: str) -> LLMResponse:
        response = ollama.chat(
            model=self.model,
                       messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            think=False,
            options={
                "temperature": LLM_TEMPERATURE,
                "num_predict": LLM_MAX_TOKENS,
            },
        )

        print("DEBUG finish reason:", response.done_reason)
        print("DEBUG raw content:", repr(response.message.content))

        return LLMResponse(
            content=response.message.content or "",
            provider="ollama",
            model=self.model,
            finish_reason=response.done_reason,
        )
