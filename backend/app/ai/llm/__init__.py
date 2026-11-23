"""
LLM provider factory.

Import ``get_llm_provider`` wherever an LLM is needed.  The concrete
implementation (currently Gemini) is selected here so that individual
nodes and services never hardcode a provider class.
"""

from app.ai.llm.base import LLMProvider
from app.ai.llm.gemini import GeminiLLMProvider


def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider instance."""
    return GeminiLLMProvider()
