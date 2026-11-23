
from pathlib import Path

import chromadb


# Persistent ChromaDB storage
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_ROOT / "storage" / "chroma"

_client = None
_collection = None


def get_client() -> chromadb.PersistentClient:
    """Return persistent ChromaDB client instance (lazy-initialized)."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return _client


def get_collection():
    """Return ChromaDB collection with cosine distance (lazy-initialized)."""
    global _collection
    if _collection is None:
        _collection = get_client().get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def __getattr__(name: str):
    """Support direct attribute imports (e.g. from app.services.vector_store import collection)."""
    if name == "collection":
        return get_collection()
    if name == "client":
        return get_client()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def store_chunks(
    user_id: int,
    document_id: int,
    chunks: list,
    embeddings: list,
):
    """Store document chunks and their embeddings."""

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings count must match.")

    if not chunks:
        return 0

    ids = []
    documents = []
    metadatas = []

    for chunk, embedding in zip(chunks, embeddings):
        chunk_index = chunk["chunk_index"]

        page_number = chunk["page_number"]

        ids.append(
            f"user_{user_id}_document_{document_id}_page_{page_number}_chunk_{chunk_index}"
        )

        documents.append(chunk["text"])

        metadatas.append({
            "user_id": user_id,
            "document_id": document_id,
            "page_number": chunk["page_number"],
            "chunk_index": chunk_index,
        })

    get_collection().upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(ids)


def search_chunks(
    user_id: int,
    query_embedding: list,
    document_id: int = None,
    top_k: int = 5,
):
    """Search document chunks belonging to a specific user."""

    if top_k <= 0:
        raise ValueError("top_k must be positive.")
    conditions = [
        {"user_id": {"$eq": user_id}}
    ]

    if document_id is not None:
        conditions.append(
            {"document_id": {"$eq": document_id}}
        )

    filters = {"$and": conditions}

    return get_collection().query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=filters,
        include=["documents", "metadatas", "distances"],
    )

def delete_document_chunks(user_id: int, document_id: int) -> None:
    """Delete all chunks belonging to a specific user's document."""

    if type(user_id) is not int or user_id <= 0:
        raise ValueError("Invalid user ID.")

    if type(document_id) is not int or document_id <= 0:
        raise ValueError("Invalid document ID.")

    get_collection().delete(
        where={
            "$and": [
                {"user_id": {"$eq": user_id}},
                {"document_id": {"$eq": document_id}},
            ]
        }
    )