
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.dependencies import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.models.data_source import DataSource
from app.models.dataset import Dataset

from app.schemas.dataset import DatasetResponse

from app.services.file_processing import process_uploaded_file
from app.services.file_storage import (
    save_uploaded_file,
    delete_stored_file,
    MAX_UPLOAD_SIZE,
)

from app.services.dataset_analysis import analyze_user_dataset


router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("/upload", response_model=DatasetResponse, status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    content = await file.read(MAX_UPLOAD_SIZE + 1)

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 16 MB limit.",
        )

    try:
        _, metadata = process_uploaded_file(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None

    try:
        file_path, original_filename = save_uploaded_file(
            current_user.id,
            file.filename,
            content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None

    try:
        data_source = DataSource(
            user_id=current_user.id,
            source_type="file",
            source_name=original_filename,
            file_path=file_path,
            connection_config=None,
        )

        db.add(data_source)
        db.flush()

        dataset = Dataset(
            user_id=current_user.id,
            data_source_id=data_source.id,
            dataset_name=original_filename,
            schema_metadata=metadata,
        )

        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        return dataset

    except SQLAlchemyError:
        db.rollback()
        delete_stored_file(current_user.id, file_path)

        raise HTTPException(
            status_code=500,
            detail="Unable to save dataset information.",
        ) from None



@router.get("/{dataset_id}/analysis")
def analyze_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return analyze_user_dataset(
            db=db,
            dataset_id=dataset_id,
            user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from None

@router.get("/")
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    datasets = (
        db.query(Dataset)
        .filter(Dataset.user_id == current_user.id)
        .order_by(Dataset.created_at.desc())
        .all()
    )

    return [
        {
            "id": dataset.id,
            "dataset_name": dataset.dataset_name,
            "row_count": (dataset.schema_metadata or {}).get("row_count"),
            "column_count": (dataset.schema_metadata or {}).get("column_count"),
            "columns": (dataset.schema_metadata or {}).get("columns", []),
            "created_at": dataset.created_at,
        }
        for dataset in datasets
    ]


@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Safely delete a dataset and its physical file if no other records reference it."""
    # 1. Verify ownership: must exist and belong to current_user
    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id,
            Dataset.user_id == current_user.id,
        )
        .first()
    )
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    # 2. Disassociate any linked analyses to preserve analysis history
    from app.models.analysis import Analysis
    linked_analyses = (
        db.query(Analysis)
        .filter(Analysis.dataset_id == dataset.id)
        .all()
    )
    for analysis in linked_analyses:
        analysis.dataset_id = None

    # 3. Retrieve associated DataSource
    data_source_id = dataset.data_source_id
    data_source = (
        db.query(DataSource)
        .filter(DataSource.id == data_source_id)
        .first()
    )

    # 4. Check if other datasets reference the same data_source
    other_dataset_refs = (
        db.query(Dataset)
        .filter(
            Dataset.data_source_id == data_source_id,
            Dataset.id != dataset.id,
        )
        .count()
    )

    should_delete_data_source = False
    file_to_delete = None

    if other_dataset_refs == 0 and data_source:
        if data_source.source_type == "file" and data_source.file_path:
            other_file_refs = (
                db.query(DataSource)
                .filter(
                    DataSource.file_path == data_source.file_path,
                    DataSource.id != data_source.id,
                )
                .count()
            )
            if other_file_refs == 0:
                file_to_delete = data_source.file_path

        should_delete_data_source = True

    try:
        db.delete(dataset)

        if should_delete_data_source and data_source:
            db.delete(data_source)

        db.commit()

        if file_to_delete:
            try:
                delete_stored_file(current_user.id, file_to_delete)
            except Exception:
                pass

        return {"message": "Dataset deleted successfully."}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to delete dataset. Please try again.",
        ) from None
