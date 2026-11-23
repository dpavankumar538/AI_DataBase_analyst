from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Common interface for language model providers."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a response from a prompt."""
        pass