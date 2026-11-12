from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.order import Order


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str|None] = mapped_column(
        String(150),nullable=True
    )
    
    orders: Mapped[list["Order"]]=relationship("Order",back_populates="customer")
