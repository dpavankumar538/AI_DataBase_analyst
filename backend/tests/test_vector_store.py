
from app.ai.embeddings.gemini import GeminiEmbeddingProvider
from app.services.vector_store import store_chunks, search_chunks


def test_vector_store():
    provider = GeminiEmbeddingProvider()

    user_id = 1
    document_id = 999

    # Sample document chunks
    chunks = [
        {
            "page_number": 1,
            "chunk_index": 0,
            "text": "Python is a programming language used for web development and automation.",
        },
        {
            "page_number": 2,
            "chunk_index": 0,
            "text": "Machine learning uses algorithms to learn patterns from data.",
        },
        {
            "page_number": 3,
            "chunk_index": 0,
            "text": "ChromaDB stores vector embeddings and supports semantic search.",
        },
    ]

    # Generate embeddings
    texts = [chunk["text"] for chunk in chunks]
    embeddings = provider.embed_documents(texts)

    # Store vectors
    stored_count = store_chunks(
        user_id=user_id,
        document_id=document_id,
        chunks=chunks,
        embeddings=embeddings,
    )

    print("Stored chunks:", stored_count)

    # Search using a natural-language question
    question = "Which technology stores vector embeddings?"
    query_embedding = provider.embed_query(question)

    results = search_chunks(
        user_id=user_id,
        document_id=document_id,
        query_embedding=query_embedding,
        top_k=2,
    )

    print("\nSearch results:")

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        print("\nPage:", metadata["page_number"])
        print("Text:", text)
        print("Distance:", distance)


if __name__ == "__main__":
    test_vector_store()
