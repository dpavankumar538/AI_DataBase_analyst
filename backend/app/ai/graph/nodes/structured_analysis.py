
from langgraph.runtime import Runtime

from app.ai.graph.state import AnalysisState, AnalysisContext
from app.services.dataset_analysis import analyze_user_dataset
from app.services.ai_sql_analysis import analyze_external_database


def structured_analysis_node(
    state: AnalysisState,
    runtime: Runtime[AnalysisContext],
) -> dict:
    """Analyze uploaded datasets and external databases."""

    dataset_ids = state.get("dataset_ids", [])
    data_source_ids = state.get("data_source_ids", [])

    question = state.get("question", "").strip()

    user_id = runtime.context["user_id"]
    db = runtime.context["db"]

    if not dataset_ids and not data_source_ids:
        return {"error": "No structured data sources were selected."}

    results = []

    try:
        # Analyze uploaded datasets.
        for dataset_id in dataset_ids:
            result = analyze_user_dataset(
                db=db,
                dataset_id=dataset_id,
                user_id=user_id,
            )

            results.append({
                "source_type": "uploaded_dataset",
                **result,
            })

        # Analyze external MySQL/PostgreSQL databases.
        for source_id in data_source_ids:
            result = analyze_external_database(
                db=db,
                user_id=user_id,
                data_source_id=source_id,
                question=question,
            )

            results.append({
                "source_type": "external_database",
                "data_source_id": source_id,
                **result,
            })

    except ValueError as exc:
        return {"error": str(exc)}

    except Exception:
        return {"error": "Unable to analyze the selected data sources."}

    return {
        "structured_result": {
            "status": "success",
            "datasets": results,
        }
    }
