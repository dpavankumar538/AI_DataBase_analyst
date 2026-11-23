from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.data_source import DataSource
    from app.models.analysis import Analysis

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.time import utc_now

from app.database.base import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    data_source_id: Mapped[int] = mapped_column(
        ForeignKey("data_sources.id"),
        nullable=False
    )

    dataset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    schema_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="datasets"
    )

    data_source: Mapped["DataSource"] = relationship(
        back_populates="datasets"
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="dataset"
    )
