
from google import genai
from google.genai import types

from app.ai.embeddings.base import EmbeddingProvider
from app.core.config import (
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
)


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Gemini implementation of the embedding interface."""

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_EMBEDDING_MODEL

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
            ),
        )

        return [
            embedding.values
            for embedding in response.embeddings
        ]

    def embed_query(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Query text cannot be empty.")

        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
            ),
        )

        return response.embeddings[0].values
