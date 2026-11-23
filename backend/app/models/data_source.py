from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.dataset import Dataset

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.time import utc_now

from app.database.base import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    source_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    connection_config: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    connection_status: Mapped[str | None] = mapped_column(
        String(20),
        default=None,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="data_sources"
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="data_source",
        cascade="all, delete-orphan"
    )
