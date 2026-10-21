
from config.llm_config import (
    LLM_PROVIDER,
    OLLAMA_MODEL,
    OPENROUTER_MODEL,
)
from src.llm.base import LLMClient
from src.llm.ollama_client import OllamaClient
from src.llm.openrouter_client import OpenRouterClient


def create_llm_client() -> LLMClient:
    """Create the configured LLM provider client."""

    provider = LLM_PROVIDER.strip().lower()

    if provider == "ollama":
        return OllamaClient(model=OLLAMA_MODEL)

    if provider == "openrouter":
        return OpenRouterClient(model=OPENROUTER_MODEL)

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER!r}. "
        "Choose 'ollama' or 'openrouter'."
    )
