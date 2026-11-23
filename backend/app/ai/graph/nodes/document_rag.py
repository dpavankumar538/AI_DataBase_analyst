from langgraph.runtime import Runtime

from app.ai.graph.state import AnalysisState, AnalysisContext
from app.services.document_retrieval import retrieve_document_context


def document_rag_node(
    state: AnalysisState,
    runtime: Runtime[AnalysisContext],
) -> dict:
    """Retrieve relevant document chunks for each selected document.

    This node is responsible only for *retrieval* — it does not call the LLM.
    The single LLM synthesis call happens later in ``response_node``, which
    prevents a redundant duplicate LLM invocation per document.

    The ``document_context`` list that is written to state contains one entry
    per document with the raw retrieved chunks (text, page number, distance)
    so that ``response_node`` can build proper page-level citations.
    """
    user_id = runtime.context["user_id"]
    question = state.get("question", "").strip()
    document_ids = state.get("document_ids", [])

    if not question:
        return {"error": "Please provide a question."}

    if not document_ids:
        return {"error": "No documents were selected."}

    results = []

    try:
        for document_id in document_ids:
            chunks = retrieve_document_context(
                question=question,
                user_id=user_id,
                document_id=document_id,
            )

            # Preserve source references even when no chunks are found so
            # that evaluation_node and response_node can handle empty results
            # gracefully.
            results.append({
                "document_id": document_id,
                "chunks": chunks,   # list of {text, page_number, document_id, distance}
                # Provide a flat ``sources`` list so evaluation_node's existing
                # check (result.get("sources")) continues to work correctly.
                "sources": [
                    {
                        "page_number": c["page_number"],
                        "distance": c["distance"],
                    }
                    for c in chunks
                ],
            })

    except ValueError as exc:
        return {"error": str(exc)}
    except Exception:
        return {"error": "Unable to retrieve context from the selected documents."}

    return {"document_context": results}