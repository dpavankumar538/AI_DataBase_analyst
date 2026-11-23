from app.services.document_retrieval import retrieve_document_context


def test_document_retrieval():

    question = "What is the Turing Test in artificial intelligence?"

    results = retrieve_document_context(
        question=question,
        user_id=1,
        document_id=1001,
        top_k=3,
    )

    print("\nQuestion:", question)
    print("\nRetrieved chunks:", len(results))

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print("Page:", result["page_number"])
        print("Distance:", result["distance"])
        print("Text:")
        print(result["text"])


if __name__ == "__main__":
    test_document_retrieval()