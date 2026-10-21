from abc import ABC, abstractmethod

from .response import LLMResponse


class LLMClient(ABC):
    """
    Common interface for all LLM providers.

    Agents will depend on this interface,
    not on a specific LLM provider.
    """

    @abstractmethod
    def generate(self, prompt: str) -> LLMResponse:
        """
        Generate a standardized LLM response.
        """
        pass