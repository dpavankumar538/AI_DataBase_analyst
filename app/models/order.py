from typing import TYPE_CHECKING

from sqlalchemy import String ,ForeignKey
from sqlalchemy.orm import mapped_column,Mapped,relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.customer import Customer

class Order (Base):
    __tablename__= "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product: Mapped[str] =mapped_column(String(100), nullable=False)
    
    customer_id: Mapped[int]=mapped_column(
        ForeignKey("customers.id"),
        nullable=False
    )
    
    
    customer: Mapped["Customer"] = relationship(
    "Customer",
    back_populates="orders"
)