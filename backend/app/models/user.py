from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.data_source import DataSource
    from app.models.dataset import Dataset
    from app.models.analysis import Analysis
    from app.models.user_session import UserSession
    from app.models.document import Document

from datetime import datetime
from app.core.time import utc_now

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False
    )

    # Relationships
    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    data_sources: Mapped[list["DataSource"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan"
    )
