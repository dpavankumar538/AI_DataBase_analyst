
from app.ai.graph.state import AnalysisState


def evaluation_node(state: AnalysisState) -> dict:
    """Evaluate whether structured and document analysis produced usable results."""

    if state.get("error"):
        return {"evaluation_result": "failed"}

    structured_result = state.get("structured_result")
    document_context = state.get("document_context", [])

    has_structured_result = False

    if structured_result:
        datasets = structured_result.get("datasets", [])

        has_structured_result = (
            structured_result.get("status") == "success"
            and bool(datasets)
            and all(
                result.get("source_type") == "uploaded_dataset"
                or (
                    result.get("source_type") == "external_database"
                    and ("schema" in result or "result" in result)
                )
                for result in datasets
            )
        )

    # A document result is usable when it has both retrieved chunks and sources.
    has_document_result = any(
        bool(result.get("chunks")) and bool(result.get("sources"))
        for result in document_context
    )

    if has_structured_result or has_document_result:
        return {"evaluation_result": "success"}

    return {"evaluation_result": "insufficient"}
