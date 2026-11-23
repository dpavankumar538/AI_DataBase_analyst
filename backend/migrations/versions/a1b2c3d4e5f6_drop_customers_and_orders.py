"""drop customers and orders tables

Revision ID: a1b2c3d4e5f6
Revises: 3cb041fd67b4
Create Date: 2026-11-17 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '3cb041fd67b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the customer/order demo tables that are no longer part of the application."""
    # orders must be dropped before customers (FK constraint)
    op.drop_table('orders')
    op.drop_table('customers')

def upgrade() -> None:
    """Drop legacy customer/order tables if they exist."""
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()

    # Drop orders first because it references customers.
    if "orders" in tables:
        op.drop_table("orders")

    if "customers" in tables:
        op.drop_table("customers")