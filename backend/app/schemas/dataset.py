
from datetime import datetime

from pydantic import BaseModel, ConfigDict

class DatasetResponse(BaseModel):
    id: int
    data_source_id: int
    dataset_name: str
    schema_metadata: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
