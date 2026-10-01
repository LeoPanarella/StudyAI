"""material connections and job focus

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-23 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'material_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_material_id', sa.Integer(), nullable=False),
        sa.Column('target_material_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.String(length=30), nullable=False, server_default='related'),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['source_material_id'], ['materials.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_material_id'], ['materials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_material_id', 'target_material_id', name='uq_material_connection'),
        sa.CheckConstraint('source_material_id != target_material_id', name='chk_connection_different'),
    )
    op.create_index(op.f('ix_material_connections_source'), 'material_connections', ['source_material_id'])
    op.create_index(op.f('ix_material_connections_target'), 'material_connections', ['target_material_id'])

    op.add_column('ai_jobs', sa.Column('focus', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('ai_jobs', 'focus')
    op.drop_index(op.f('ix_material_connections_target'), table_name='material_connections')
    op.drop_index(op.f('ix_material_connections_source'), table_name='material_connections')
    op.drop_table('material_connections')
