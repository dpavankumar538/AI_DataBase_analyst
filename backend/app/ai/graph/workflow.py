
from langgraph.graph import StateGraph, START, END

from app.ai.graph.state import AnalysisState, AnalysisContext

from app.ai.graph.nodes.router import query_router_node
from app.ai.graph.nodes.structured_analysis import structured_analysis_node
from app.ai.graph.nodes.document_rag import document_rag_node
from app.ai.graph.nodes.evaluation import evaluation_node
from app.ai.graph.nodes.response import response_node


def route_after_router(state: AnalysisState) -> str:
    return state.get("route", "error")


def route_after_structured(state: AnalysisState) -> str:
    """Choose the next node after structured analysis."""

    if state.get("error"):
        return "evaluation"

    if state.get("route") == "hybrid":
        return "document"

    return "evaluation"


def route_after_evaluation(state: AnalysisState) -> str:
    """Route after evaluation.

    * ``success``      – proceed to the response node.
    * ``failed``       – proceed to the response node (error already set).
    * ``insufficient`` – proceed to the response node; no retry is performed
                         because re-running the same analysis node with
                         unchanged inputs cannot produce a different result.
    """
    # All evaluation outcomes proceed directly to response.
    return "response"


def build_analysis_graph():

    graph = StateGraph(
        AnalysisState,
        context_schema=AnalysisContext,
    )

    # Register primary nodes
    graph.add_node("query_router", query_router_node)
    graph.add_node("structured_analysis", structured_analysis_node)
    graph.add_node("document_rag", document_rag_node)
    graph.add_node("evaluation", evaluation_node)
    graph.add_node("response", response_node)

    # Entry point
    graph.add_edge(START, "query_router")

    # Route the user's question
    graph.add_conditional_edges(
        "query_router",
        route_after_router,
        {
            "structured": "structured_analysis",
            "document": "document_rag",
            "hybrid": "structured_analysis",
            "general": "response",
            "error": "response",
        },
    )

    # Route after structured analysis (hybrid goes to document_rag; structured/error goes to evaluation)
    graph.add_conditional_edges(
        "structured_analysis",
        route_after_structured,
        {
            "document": "document_rag",
            "evaluation": "evaluation",
        },
    )

    # Document analysis always proceeds to evaluation
    graph.add_edge("document_rag", "evaluation")

    # Evaluation always proceeds to response
    graph.add_conditional_edges(
        "evaluation",
        route_after_evaluation,
        {
            "response": "response",
        },
    )

    # Terminal edge
    graph.add_edge("response", END)

    return graph.compile()


analysis_graph = build_analysis_graph()
