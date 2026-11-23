
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Common interface for all embedding providers."""

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Convert multiple document chunks into vectors."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Convert a user query into a vector."""
        pass
