from app.services.vector_store import collection


def test_view_vectors():

    results = collection.get(
        where={
            "$and": [
                {"user_id": {"$eq": 1}},
                {"document_id": {"$eq": 1001}},
            ]
        },
        include=["documents", "metadatas", "embeddings"],
        limit=2,
    )

    print("\nTotal retrieved chunks:", len(results["ids"]))

    for i in range(len(results["ids"])):
        print("\nID:", results["ids"][i])
        print("Metadata:", results["metadatas"][i])
        print("Text:", results["documents"][i][:200])
        print("Vector dimensions:", len(results["embeddings"][i]))
        print("First 10 vector values:", results["embeddings"][i][:10])


if __name__ == "__main__":
    test_view_vectors()