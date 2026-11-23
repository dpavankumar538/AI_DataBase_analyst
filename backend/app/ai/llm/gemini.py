from google import genai

from app.ai.llm.base import LLMProvider
from app.core.config import GEMINI_API_KEY

from google.genai import types


class GeminiLLMProvider(LLMProvider):
    """Gemini implementation of the language model interface."""

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(
                timeout=120000,
                retry_options=types.HttpRetryOptions(
                    attempts=1
                    )
                )
            )
        self.model = "gemini-3.5-flash-lite"

    def generate_response(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return response.text


    def generate_sql(
        self,
        question: str,
        schema: dict,
        database_type: str,
    ) -> str:
        """Generate a read-only SQL query using the supplied database schema."""

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if database_type not in ("mysql", "postgresql"):
            raise ValueError("Unsupported database type.")

        prompt = f"""
You are an expert SQL query generator.

Generate exactly one read-only SQL SELECT query.

Database type: {database_type}

Available database schema:
{schema}

User question:
{question}

Rules:
1. Use only tables and columns present in the supplied schema.
2. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE.
3. Never use SELECT INTO or locking clauses.
4. Do not invent table or column names.
5. Use the correct SQL dialect.
6. Return only SQL, without Markdown fences or explanations.
"""

        return self.generate_response(prompt).strip()
