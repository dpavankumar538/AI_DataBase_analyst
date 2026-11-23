
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class ExternalDatabaseCreate(BaseModel):
    """Request schema for connecting an external database."""

    database_type: Literal["mysql", "postgresql"]
    source_name: str = Field(min_length=1, max_length=150)
    host: str = Field(min_length=1, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    database: str = Field(min_length=1, max_length=150)
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=1, max_length=1000)
    ssl_enabled: bool = False



class ExternalDatabaseResponse(BaseModel):
    """Safe response schema without database credentials."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_name: str
    source_type: str
    connection_status: str | None = None
