from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class AnalysisRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

    dataset_ids: list[int] = Field(default_factory=list)
    document_ids: list[int] = Field(default_factory=list)
    data_source_ids: list[int] = Field(default_factory=list)


class AnalysisDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    dataset_id: Optional[int] = None
    question: str
    route: str
    selected_resources: Optional[dict[str, Any]] = None
    generated_query: Optional[str] = None
    structured_result: Optional[dict[str, Any]] = None
    document_citations: Optional[list[Any]] = None
    result_summary: Optional[str] = None
    evaluation_result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime


class AnalysisSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    route: str
    result_summary: Optional[str] = None
    evaluation_result: Optional[str] = None
    created_at: datetime