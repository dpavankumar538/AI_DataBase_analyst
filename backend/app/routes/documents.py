from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.models.document import Document

from app.services.vector_store import delete_document_chunks

from sqlalchemy.exc import SQLAlchemyError

from app.services.file_storage import (
    save_uploaded_file,
    delete_stored_file,
    MAX_UPLOAD_SIZE,
)

from app.services.document_processing import process_pdf_document


router = APIRouter(prefix="/documents", tags=["Documents"])


def get_owned_document(
    db: Session,
    document_id: int,
    user_id: int,
) -> Document:
    """Retrieve a document only if it belongs to the user."""

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Verify that this document belongs to the logged-in user.
    document = get_owned_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    try:
        # 2. Delete the document's ChromaDB chunks.
        delete_document_chunks(
            user_id=current_user.id,
            document_id=document_id,
        )

        # 3. Delete the physical PDF file.
        delete_stored_file(
            user_id=current_user.id,
            file_path=document.file_path,
        )

        # 4. Delete the MySQL document record.
        db.delete(document)
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to delete document. Please try again.",
        ) from None

    return {"message": "Document deleted successfully."}

@router.get("/{document_id}")
def get_document_details(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_owned_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    return {
        "id": document.id,
        "filename": document.filename,
        "page_count": document.page_count,
        "processing_status": document.processing_status,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
    }

@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    content = await file.read(MAX_UPLOAD_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 16 MB limit.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file.",
        )

    try:
        file_path, original_filename = save_uploaded_file(
            current_user.id,
            file.filename,
            content,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from None

    document = Document(
        user_id=current_user.id,
        filename=original_filename,
        file_path=file_path,
        processing_status="processing",
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)

        result = process_pdf_document(
            file_path=file_path,
            user_id=current_user.id,
            document_id=document.id,
        )

        document.page_count = result["page_count"]
        document.processing_status = "completed"

        db.commit()
        db.refresh(document)

        return {
            "message": "PDF uploaded and processed successfully.",
            "document_id": document.id,
            "filename": document.filename,
            "page_count": document.page_count,
            "chunk_count": result["chunk_count"],
            "processing_status": document.processing_status,
        }

    except Exception:
        db.rollback()

        try:
            delete_document_chunks(
                user_id=current_user.id,
                document_id=document.id,
            )
            delete_stored_file(
                user_id=current_user.id,
                file_path=file_path,
            )
        except Exception:
            pass

        if document.id is not None:
            db.query(Document).filter(
                Document.id == document.id,
                Document.user_id == current_user.id,
            ).update({"processing_status": "failed"})
            db.commit()

        raise HTTPException(
            status_code=500,
            detail="Unable to process PDF document.",
        ) from None


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "page_count": document.page_count,
            "processing_status": document.processing_status,
            "created_at": document.created_at,
        }
        for document in documents
    ]