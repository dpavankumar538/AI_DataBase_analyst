import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ai.graph.workflow import analysis_graph, route_after_structured, route_after_evaluation


def test_langgraph_routing_functions():
    """Verify routing decision logic after structured analysis."""
    # Hybrid routes to document_rag
    assert route_after_structured({"route": "hybrid"}) == "document"

    # Structured routes to evaluation
    assert route_after_structured({"route": "structured"}) == "evaluation"

    # Error during structured analysis routes to evaluation directly
    assert route_after_structured({"route": "hybrid", "error": "Query error"}) == "evaluation"
    assert route_after_structured({"route": "structured", "error": "Query error"}) == "evaluation"

    # Evaluation always routes to response
    assert route_after_evaluation({"evaluation_result": "success"}) == "response"
    assert route_after_evaluation({"evaluation_result": "failed"}) == "response"
    assert route_after_evaluation({"evaluation_result": "insufficient"}) == "response"


def test_langgraph_compiled_graph_edges():
    """Verify that structured_analysis has conditional edges and no direct __end__ edge."""
    edges = analysis_graph.get_graph().edges

    structured_targets = [
        edge.target for edge in edges if edge.source == "structured_analysis"
    ]
    # structured_analysis must reach document_rag and evaluation
    assert "document_rag" in structured_targets
    assert "evaluation" in structured_targets
    # structured_analysis must NOT terminate at __end__
    assert "__end__" not in structured_targets

    # Evaluation must have conditional edge to response
    eval_edges = [edge for edge in edges if edge.source == "evaluation"]
    assert len(eval_edges) == 1
    assert eval_edges[0].target == "response"
    assert eval_edges[0].conditional is True


def test_cors_middleware_allowed_origin(client):
    """Verify CORS preflight allows configured origins with credentials."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_middleware_disallowed_origin(client):
    """Verify CORS preflight denies unconfigured origins."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://unauthorized-domain.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") is None
