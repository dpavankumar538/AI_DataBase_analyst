from typing import TypedDict, Optional, Any
from sqlalchemy.orm import Session



class AnalysisState(TypedDict, total=False):
    # Authenticated user
    # user_id: int

    # User's question
    question: str

    # Selected data sources
    dataset_ids: list[int]
    document_ids: list[int]
    data_source_ids: list[int]

    # Router decision
    route: str

    # Structured data
    schema: Optional[dict[str, Any]]
    structured_result: Optional[dict[str, Any]]

    # Document retrieval
    document_context: Optional[list[dict[str, Any]]]

    # Evaluation
    evaluation_result: Optional[str]
    retry_count: int

    # Final response
    final_answer: Optional[str]

    # Error handling
    error: Optional[str]

class AnalysisContext(TypedDict):
    user_id: int
    db: Session
