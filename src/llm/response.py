from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """
    Standard response returned by any LLM provider.
    """

    content: str
    provider: str
    model: str
    finish_reason: Optional[str] = None