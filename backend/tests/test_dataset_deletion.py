import os
from pathlib import Path
import pytest
from app.models.analysis import Analysis
from app.models.dataset import Dataset
from app.models.data_source import DataSource
from app.models.user import User
from app.services.file_storage import save_uploaded_file


def register_and_get_token(client, email, name="User", password="password123"):
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


def test_delete_dataset_success_and_file_cleanup(client):
    """Verify deleting a dataset cleans up its DB record and physical file."""
    token, user_id = register_and_get_token(client, "delete_owner@example.com")

    # Create dummy stored file
    content = b"col1,col2\n1,2\n3,4\n"
    file_path, filename = save_uploaded_file(user_id, "test.csv", content)
    assert os.path.exists(file_path)

    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()

    # Create data source and dataset
    data_source = DataSource(
        user_id=user_id,
        source_type="file",
        source_name=filename,
        file_path=file_path,
    )
    db.add(data_source)
    db.commit()
    db.refresh(data_source)

    dataset = Dataset(
        user_id=user_id,
        data_source_id=data_source.id,
        dataset_name="Test Dataset",
        schema_metadata={"row_count": 2},
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    ds_id = dataset.id
    source_id = data_source.id
    db.close()

    resp = client.delete(f"/datasets/{ds_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "Dataset deleted successfully."

    # Verify DB records deleted
    db = TestingSessionLocal()
    assert db.query(Dataset).filter(Dataset.id == ds_id).first() is None
    assert db.query(DataSource).filter(DataSource.id == source_id).first() is None
    db.close()

    # Verify physical file was deleted
    assert not os.path.exists(file_path)


def test_delete_dataset_ownership_isolation(client):
    """Verify users cannot delete datasets owned by other users."""
    token1, user1_id = register_and_get_token(client, "victim@example.com")
    token2, user2_id = register_and_get_token(client, "attacker@example.com")

    content = b"a,b\n1,2\n"
    file_path, filename = save_uploaded_file(user1_id, "victim.csv", content)

    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()

    data_source = DataSource(
        user_id=user1_id,
        source_type="file",
        source_name=filename,
        file_path=file_path,
    )
    db.add(data_source)
    db.commit()
    db.refresh(data_source)

    dataset = Dataset(
        user_id=user1_id,
        data_source_id=data_source.id,
        dataset_name="Victim Dataset",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    ds_id = dataset.id
    db.close()

    # User 2 attempts to delete User 1's dataset -> must return 404
    resp = client.delete(f"/datasets/{ds_id}", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 404

    # File and dataset must still exist
    assert os.path.exists(file_path)
    db = TestingSessionLocal()
    assert db.query(Dataset).filter(Dataset.id == ds_id).first() is not None
    db.close()

    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)


def test_delete_dataset_shared_file_reference_safety(client):
    """Verify physical file is NOT deleted if another dataset still references the same DataSource."""
    token, user_id = register_and_get_token(client, "shared_user@example.com")

    content = b"x,y\n10,20\n"
    file_path, filename = save_uploaded_file(user_id, "shared.csv", content)

    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()

    data_source = DataSource(
        user_id=user_id,
        source_type="file",
        source_name=filename,
        file_path=file_path,
    )
    db.add(data_source)
    db.commit()
    db.refresh(data_source)

    # Dataset 1
    d1 = Dataset(
        user_id=user_id,
        data_source_id=data_source.id,
        dataset_name="Sheet 1",
    )
    # Dataset 2 (pointing to same DataSource)
    d2 = Dataset(
        user_id=user_id,
        data_source_id=data_source.id,
        dataset_name="Sheet 2",
    )
    db.add_all([d1, d2])
    db.commit()
    db.refresh(d1)
    db.refresh(d2)
    d1_id = d1.id
    d2_id = d2.id
    source_id = data_source.id
    db.close()

    # Delete Dataset 1
    resp = client.delete(f"/datasets/{d1_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    # Dataset 2 still exists, and physical file MUST NOT be deleted!
    assert os.path.exists(file_path)

    db = TestingSessionLocal()
    assert db.query(Dataset).filter(Dataset.id == d1_id).first() is None
    assert db.query(Dataset).filter(Dataset.id == d2_id).first() is not None
    assert db.query(DataSource).filter(DataSource.id == source_id).first() is not None
    db.close()

    # Now delete Dataset 2
    resp2 = client.delete(f"/datasets/{d2_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 200

    # Now that 0 datasets reference it, physical file and DataSource are cleaned up
    assert not os.path.exists(file_path)
    db = TestingSessionLocal()
    assert db.query(DataSource).filter(DataSource.id == source_id).first() is None
    db.close()


def test_delete_dataset_preserves_linked_analyses(client):
    """Verify deleting a dataset disassociates dataset_id on linked analyses and preserves analysis history."""
    token, user_id = register_and_get_token(client, "linked_user@example.com")

    content = b"q,w\n1,2\n"
    file_path, filename = save_uploaded_file(user_id, "linked.csv", content)

    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()

    data_source = DataSource(
        user_id=user_id,
        source_type="file",
        source_name=filename,
        file_path=file_path,
    )
    db.add(data_source)
    db.commit()
    db.refresh(data_source)

    dataset = Dataset(
        user_id=user_id,
        data_source_id=data_source.id,
        dataset_name="Linked Dataset",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Create linked analysis
    analysis = Analysis(
        user_id=user_id,
        dataset_id=dataset.id,
        question="What are the columns?",
        route="structured",
        selected_resources={"dataset_ids": [dataset.id], "data_source_ids": [], "document_ids": []},
        result_summary="Columns are q and w.",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    analysis_id = analysis.id
    ds_id = dataset.id
    db.close()

    resp = client.delete(f"/datasets/{ds_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    # Verify analysis STILL EXISTS in DB with dataset_id set to None
    db = TestingSessionLocal()
    preserved_analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    assert preserved_analysis is not None
    assert preserved_analysis.dataset_id is None
    assert preserved_analysis.result_summary == "Columns are q and w."
    db.close()
