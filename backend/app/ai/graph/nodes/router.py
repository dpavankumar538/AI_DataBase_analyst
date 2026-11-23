from app.ai.graph.state import AnalysisState


def query_router_node(state: AnalysisState) -> dict:
    """
    Determine which analysis path is required.
    """

    question = state.get("question", "").strip()

    if not question:
        return {
            "error": "Please provide a question.",
            "route": "error",
        }

    has_datasets = bool(state.get("dataset_ids"))
    has_documents = bool(state.get("document_ids"))
    has_data_sources = bool(state.get("data_source_ids"))

    if has_datasets or has_data_sources:
        if has_documents:
            route = "hybrid"
        else:
            route = "structured"

    elif has_documents:
        route = "document"

    else:
        route = "general"

    return {"route": route}