"""add tags column

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2023-11-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add tags column to the Prompt table
    op.add_column('prompt', sa.Column('tags', sa.String(200), nullable=True))
    # Add updated_at column to the Prompt table
    op.add_column('prompt', sa.Column('updated_at', sa.DateTime, nullable=True))
    # Create indexes for improved performance
    op.create_index(op.f('ix_prompt_created_at'), 'prompt', ['created_at'], unique=False)
    op.create_index(op.f('ix_prompt_tags'), 'prompt', ['tags'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_prompt_tags'), table_name='prompt')
    op.drop_index(op.f('ix_prompt_created_at'), table_name='prompt')
    # Drop columns
    op.drop_column('prompt', 'updated_at')
    op.drop_column('prompt', 'tags') 