"""add oauth fields

Revision ID: b4d5e6f7g8h9
Revises: ac3c3796fea0
Create Date: 2026-02-10 15:07:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b4d5e6f7g8h9"
down_revision: Union[str, Sequence[str], None] = "ac3c3796fea0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add oauth_provider column to users table
    op.add_column("users", sa.Column("oauth_provider", sa.String(), nullable=True))
    # Add oauth_id column to users table
    op.add_column("users", sa.Column("oauth_id", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop oauth_id column from users table
    op.drop_column("users", "oauth_id")
    # Drop oauth_provider column from users table
    op.drop_column("users", "oauth_provider")
