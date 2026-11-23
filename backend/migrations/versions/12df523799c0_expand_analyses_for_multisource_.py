"""expand_analyses_for_multisource_persistence

Revision ID: 12df523799c0
Revises: 899bc1e0d9b0
Create Date: 2026-11-23 18:13:07.125786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12df523799c0'
down_revision: Union[str, Sequence[str], None] = '899bc1e0d9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to support multi-source analyses persistence."""
    bind = op.get_bind()
    dialect = bind.dialect.name

    # 1. Modify dataset_id to be nullable with SET NULL on delete
    if dialect == 'mysql':
        try:
            op.drop_constraint('analyses_ibfk_1', 'analyses', type_='foreignkey')
        except Exception:
            pass
        op.alter_column('analyses', 'dataset_id', existing_type=sa.Integer(), nullable=True)
        op.create_foreign_key(
            'analyses_ibfk_1',
            'analyses',
            'datasets',
            ['dataset_id'],
            ['id'],
            ondelete='SET NULL'
        )
    else:
        with op.batch_alter_table('analyses') as batch_op:
            batch_op.alter_column('dataset_id', existing_type=sa.Integer(), nullable=True)

    # 2. Add multi-source and execution provenance columns
    op.add_column(
        'analyses',
        sa.Column('route', sa.String(length=30), nullable=False, server_default='general')
    )
    op.add_column(
        'analyses',
        sa.Column('selected_resources', sa.JSON(), nullable=True)
    )
    op.add_column(
        'analyses',
        sa.Column('structured_result', sa.JSON(), nullable=True)
    )
    op.add_column(
        'analyses',
        sa.Column('document_citations', sa.JSON(), nullable=True)
    )
    op.add_column(
        'analyses',
        sa.Column('evaluation_result', sa.String(length=30), nullable=True)
    )
    op.add_column(
        'analyses',
        sa.Column('error', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('analyses', 'error')
    op.drop_column('analyses', 'evaluation_result')
    op.drop_column('analyses', 'document_citations')
    op.drop_column('analyses', 'structured_result')
    op.drop_column('analyses', 'selected_resources')
    op.drop_column('analyses', 'route')

    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == 'mysql':
        try:
            op.drop_constraint('analyses_ibfk_1', 'analyses', type_='foreignkey')
        except Exception:
            pass
        op.alter_column('analyses', 'dataset_id', existing_type=sa.Integer(), nullable=False)
        op.create_foreign_key('analyses_ibfk_1', 'analyses', 'datasets', ['dataset_id'], ['id'])
    else:
        with op.batch_alter_table('analyses') as batch_op:
            batch_op.alter_column('dataset_id', existing_type=sa.Integer(), nullable=False)
