"""BE-9: rename enum values to UPPER_SNAKE_CASE

Revision ID: 703db884292d
Revises: 1c91aec90e8d
Create Date: 2026-06-26 15:28:54.872744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '703db884292d'
down_revision: Union[str, Sequence[str], None] = '1c91aec90e8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE invite_status RENAME VALUE 'Active' TO 'ACTIVE'")
    op.execute(
        "ALTER TYPE invite_status RENAME VALUE 'Pending_invite' TO 'PENDING_INVITE'"
    )
    op.execute(
        "ALTER TYPE invite_status RENAME VALUE 'Pending_request' TO 'PENDING_REQUEST'"
    )
    op.execute("ALTER TYPE invite_status RENAME VALUE 'Rejected' TO 'REJECTED'")
    op.execute("ALTER TYPE role RENAME VALUE 'Owner' TO 'OWNER'")
    op.execute("ALTER TYPE role RENAME VALUE 'Member' TO 'MEMBER'")


def downgrade() -> None:
    op.execute("ALTER TYPE invite_status RENAME VALUE 'ACTIVE' TO 'Active'")
    op.execute(
        "ALTER TYPE invite_status RENAME VALUE 'PENDING_INVITE' TO 'Pending_invite'"
    )
    op.execute(
        "ALTER TYPE invite_status RENAME VALUE 'PENDING_REQUEST' TO 'Pending_request'"
    )
    op.execute("ALTER TYPE invite_status RENAME VALUE 'REJECTED' TO 'Rejected'")
    op.execute("ALTER TYPE role RENAME VALUE 'OWNER' TO 'Owner'")
    op.execute("ALTER TYPE role RENAME VALUE 'MEMBER' TO 'Member'")
