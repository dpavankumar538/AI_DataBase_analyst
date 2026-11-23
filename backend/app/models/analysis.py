from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.dataset import Dataset


from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

from app.core.time import utc_now


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    dataset_id: Mapped[int | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    route: Mapped[str] = mapped_column(
        String(30),
        default="general",
        nullable=False
    )

    selected_resources: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    generated_query: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    structured_result: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    document_citations: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True
    )

    result_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    evaluation_result: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="analyses"
    )

    dataset: Mapped[Optional["Dataset"]] = relationship(
        back_populates="analyses"
    )
