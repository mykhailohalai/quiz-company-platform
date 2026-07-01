"""Add notification table

Revision ID: fa323baafa2c
Revises: 4e75ebc7dd4e
Create Date: 2026-07-01 12:28:21.326741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa323baafa2c'
down_revision: Union[str, Sequence[str], None] = '4e75ebc7dd4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE company_visibility RENAME VALUE 'Hidden' TO 'HIDDEN'")
    op.execute("ALTER TYPE company_visibility RENAME VALUE 'Visible_to_all' TO 'VISIBLE_TO_ALL'")
    op.execute("ALTER TYPE questiontype RENAME VALUE 'SingleAnswer' TO 'SINGLE_ANSWER'")
    op.execute("ALTER TYPE questiontype RENAME VALUE 'MultipleAnswer' TO 'MULTIPLE_ANSWER'")

    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("unread", "read", name="notificationstatus"),
            nullable=False,
        ),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.execute("DROP TYPE IF EXISTS notificationstatus")

    op.execute("ALTER TYPE questiontype RENAME VALUE 'MULTIPLE_ANSWER' TO 'MultipleAnswer'")
    op.execute("ALTER TYPE questiontype RENAME VALUE 'SINGLE_ANSWER' TO 'SingleAnswer'")
    op.execute("ALTER TYPE company_visibility RENAME VALUE 'VISIBLE_TO_ALL' TO 'Visible_to_all'")
    op.execute("ALTER TYPE company_visibility RENAME VALUE 'HIDDEN' TO 'Hidden'")
