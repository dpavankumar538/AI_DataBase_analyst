
from app.ai.embeddings.gemini import GeminiEmbeddingProvider


def test_gemini_embeddings():
    provider = GeminiEmbeddingProvider()

    # Sample document chunks
    documents = [
        "Python is a popular programming language.",
        "Machine learning helps computers learn from data.",
    ]


    # Generate document embeddings
    document_vectors = provider.embed_documents(documents)

    # Generate a query embedding
    query_vector = provider.embed_query(
        "What is Python?"
    )

    #Validate Embeddings
    assert len(document_vectors) == len(documents)
    assert len(document_vectors[0]) > 0
    assert len(query_vector) == len(document_vectors[0])

    print("\nGemini embedding test successful!")

    print("Document count:", len(document_vectors))
    print("Document vector dimensions:", len(document_vectors[0]))
    print("Query vector dimensions:", len(query_vector))


if __name__ == "__main__":
    test_gemini_embeddings()
