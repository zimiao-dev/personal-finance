"""create transactions table

Revision ID: fb78b478204b
Revises:
Create Date: 2026-09-12 20:38:13.930813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb78b478204b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(15, 4), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_transactions_amount_positive",
        ),
        sa.CheckConstraint(
            "type IN ('income', 'expense')",
            name="ck_transactions_type_valid",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("transactions")
