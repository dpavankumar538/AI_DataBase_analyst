import pytest
from app.models.analysis import Analysis
from app.models.dataset import Dataset
from app.models.data_source import DataSource
from app.models.user import User
from app.core.security import hash_password


def register_and_get_token(client, email="analyst@example.com", name="Analyst", password="password123"):
    reg_resp = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert reg_resp.status_code == 201
    login_resp = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"], reg_resp.json()["id"]


def test_analysis_persistence_multisource_model(client):
    """Verify Analysis model supports multi-source provenance, JSON results and nullable dataset_id."""
    token, user_id = register_and_get_token(client, email="multi@example.com")

    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()

    # Document-only analysis (dataset_id is None)
    analysis = Analysis(
        user_id=user_id,
        dataset_id=None,
        question="What does the document say about revenue?",
        route="document",
        selected_resources={
            "dataset_ids": [],
            "data_source_ids": [],
            "document_ids": [10, 11],
        },
        document_citations=[
            {"document_id": 10, "page_number": 2, "distance": 0.38, "text": "Q3 Revenue reached 5M"}
        ],
        result_summary="Q3 Revenue was 5M according to [Document 10] [Page 2].",
        evaluation_result="success",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    assert analysis.id is not None
    assert analysis.dataset_id is None
    assert analysis.route == "document"
    assert analysis.selected_resources["document_ids"] == [10, 11]
    assert len(analysis.document_citations) == 1
    assert analysis.document_citations[0]["page_number"] == 2
    assert analysis.evaluation_result == "success"
    db.close()


def test_analysis_get_history_and_detail(client):
    """Verify GET /analysis/ and GET /analysis/{id} with strict user isolation."""
    from tests.conftest import TestingSessionLocal

    token1, u1_id = register_and_get_token(client, email="u1@example.com", name="User One")
    token2, u2_id = register_and_get_token(client, email="u2@example.com", name="User Two")

    db = TestingSessionLocal()
    # Create analysis for user1
    a1 = Analysis(
        user_id=u1_id,
        dataset_id=None,
        question="Analysis 1 question",
        route="general",
        selected_resources={"dataset_ids": [], "data_source_ids": [], "document_ids": []},
        result_summary="Summary 1",
        evaluation_result="success",
    )
    # Create analysis for user2
    a2 = Analysis(
        user_id=u2_id,
        dataset_id=None,
        question="Analysis 2 question",
        route="structured",
        selected_resources={"dataset_ids": [1], "data_source_ids": [], "document_ids": []},
        result_summary="Summary 2",
        evaluation_result="success",
    )
    db.add_all([a1, a2])
    db.commit()
    db.refresh(a1)
    db.refresh(a2)
    a1_id = a1.id
    db.close()

    # User 1 history list: must only show User 1's analysis
    resp1 = client.get("/analysis/", headers={"Authorization": f"Bearer {token1}"})
    assert resp1.status_code == 200
    items1 = resp1.json()
    assert len(items1) == 1
    assert items1[0]["id"] == a1_id
    assert items1[0]["question"] == "Analysis 1 question"

    # User 1 detail: must succeed for own analysis
    detail_resp = client.get(f"/analysis/{a1_id}", headers={"Authorization": f"Bearer {token1}"})
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == a1_id
    assert detail_resp.json()["route"] == "general"

    # User 2 cannot access User 1's analysis (must return 404)
    forbidden_resp = client.get(f"/analysis/{a1_id}", headers={"Authorization": f"Bearer {token2}"})
    assert forbidden_resp.status_code == 404


def test_analysis_run_persists_record(client, monkeypatch):
    """Verify POST /analysis/run creates an Analysis record and returns its ID."""
    token, user_id = register_and_get_token(client, email="run_persist@example.com", name="Runner")

    # Mock analysis_graph.invoke to return predictable mock result without making remote Gemini API calls
    from app.routes import analysis as analysis_route_module

    def mock_invoke(state, context=None):
        return {
            "final_answer": "Mock generated answer for general prompt.",
            "route": "general",
            "evaluation_result": "success",
            "structured_result": None,
            "document_context": None,
            "error": None,
        }

    monkeypatch.setattr(analysis_route_module.analysis_graph, "invoke", mock_invoke)

    run_resp = client.post(
        "/analysis/run",
        json={"question": "How to optimize queries?", "dataset_ids": [], "document_ids": [], "data_source_ids": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert run_resp.status_code == 200
    data = run_resp.json()
    assert "id" in data
    assert data["answer"] == "Mock generated answer for general prompt."
    assert data["route"] == "general"

    # Query GET /analysis/{id} to verify persistence
    detail_resp = client.get(f"/analysis/{data['id']}", headers={"Authorization": f"Bearer {token}"})
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == data["id"]
    assert detail["question"] == "How to optimize queries?"
    assert detail["result_summary"] == "Mock generated answer for general prompt."
    assert detail["selected_resources"]["dataset_ids"] == []
