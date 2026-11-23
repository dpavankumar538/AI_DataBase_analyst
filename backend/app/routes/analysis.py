from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisDetailResponse,
    AnalysisSummaryResponse,
)

from app.ai.graph.workflow import analysis_graph

from app.models.analysis import Analysis
from app.models.dataset import Dataset
from app.models.document import Document
from app.models.data_source import DataSource

router = APIRouter(prefix="/analysis", tags=["AI Analysis"])
def validate_selected_resources(
    db: Session,
    request: AnalysisRequest,
    user_id: int,
) -> None:

    if request.dataset_ids:
        datasets = (
            db.query(Dataset.id)
            .filter(
                Dataset.id.in_(request.dataset_ids),
                Dataset.user_id == user_id,
            )
            .all()
        )

        if len(datasets) != len(set(request.dataset_ids)):
            raise HTTPException(
                status_code=404,
                detail="One or more selected datasets were not found.",
            )

    if request.document_ids:
        documents = (
            db.query(Document.id)
            .filter(
                Document.id.in_(request.document_ids),
                Document.user_id == user_id,
            )
            .all()
        )

        if len(documents) != len(set(request.document_ids)):
            raise HTTPException(
                status_code=404,
                detail="One or more selected documents were not found.",
            )

    if request.data_source_ids:
        data_sources = (
            db.query(DataSource.id)
            .filter(
                DataSource.id.in_(request.data_source_ids),
                DataSource.user_id == user_id,
            )
            .all()
        )

        if len(data_sources) != len(set(request.data_source_ids)):
            raise HTTPException(
                status_code=404,
                detail="One or more selected data sources were not found.",
            )

@router.post("/run")
def run_analysis(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate ownership of selected resources
    validate_selected_resources(
        db=db,
        request=request,
        user_id=current_user.id,
    )

    # Prepare graph input
    input_state = {
        "question": request.question.strip(),
        "dataset_ids": request.dataset_ids,
        "document_ids": request.document_ids,
        "data_source_ids": request.data_source_ids,
    }

    try:
        result = analysis_graph.invoke(
            input_state,
            context={
                "user_id": current_user.id,
                "db": db,
            },
        )

        answer = result.get("final_answer")
        route = result.get("route", "general")
        evaluation = result.get("evaluation_result")
        structured_result = result.get("structured_result")
        document_context = result.get("document_context")
        error = result.get("error")

        # Extract generated query if available from structured result
        generated_query = None
        if structured_result and isinstance(structured_result, dict):
            datasets = structured_result.get("datasets", [])
            for ds in datasets:
                if isinstance(ds, dict) and "sql_query" in ds:
                    generated_query = ds.get("sql_query")
                    break

        # Persist analysis with multi-source provenance
        analysis_record = Analysis(
            user_id=current_user.id,
            dataset_id=request.dataset_ids[0] if request.dataset_ids else None,
            question=request.question.strip(),
            route=route,
            selected_resources={
                "dataset_ids": request.dataset_ids,
                "data_source_ids": request.data_source_ids,
                "document_ids": request.document_ids,
            },
            generated_query=generated_query,
            structured_result=structured_result,
            document_citations=document_context,
            result_summary=answer,
            evaluation_result=evaluation,
            error=error,
        )
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)

        return {
            "id": analysis_record.id,
            "answer": answer,
            "route": route,
            "evaluation": evaluation,
            "structured_result": structured_result,
            "document_context": document_context,
            "error": error,
            "created_at": analysis_record.created_at,
        }

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to complete the analysis. Please try again.",
        ) from None


@router.get("/", response_model=list[AnalysisSummaryResponse])
def list_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    """List historical analyses for the authenticated user."""
    analyses = (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full details and provenance of a specific analysis."""
    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id,
        )
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )
    return analysis