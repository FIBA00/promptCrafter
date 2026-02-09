"""add user rate limit

Revision ID: 45d8b74a3311
Revises: 29223a176eda
Create Date: 2026-02-09 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "45d8b74a3311"
down_revision: Union[str, Sequence[str], None] = "29223a176eda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "daily_token_limit",
            sa.Integer(),
            server_default=sa.text("10"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "tokens_used_today",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column("users", sa.Column("last_token_reset", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "last_token_reset")
    op.drop_column("users", "tokens_used_today")
    op.drop_column("users", "daily_token_limit")
