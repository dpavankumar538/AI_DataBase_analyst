from app.ai.embeddings.gemini import GeminiEmbeddingProvider
from app.services.vector_store import search_chunks


def retrieve_document_context(
    question: str,
    user_id: int,
    document_id: int = None,
    top_k: int = 5,
) -> list:
    """Retrieve relevant PDF chunks for a user's question."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # 1. Convert the question into an embedding
    embedding_provider = GeminiEmbeddingProvider()
    query_embedding = embedding_provider.embed_query(question)

    # 2. Search ChromaDB for relevant chunks
    results = search_chunks(
        user_id=user_id,
        document_id=document_id,
        query_embedding=query_embedding,
        top_k=top_k,
    )

    # 3. Format the retrieved chunks
    retrieved_context = []

    if not results["documents"] or not results["documents"][0]:
        return retrieved_context

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved_context.append({
            "text": text,
            "page_number": metadata["page_number"],
            "document_id": metadata["document_id"],
            "distance": distance,
        })

    return retrieved_context