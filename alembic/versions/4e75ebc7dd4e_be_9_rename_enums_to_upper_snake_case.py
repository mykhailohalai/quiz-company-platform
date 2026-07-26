"""BE-9: rename enums to UPPER_SNAKE_CASE

Revision ID: 4e75ebc7dd4e
Revises: 703db884292d
Create Date: 2026-06-29 13:47:48.080957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e75ebc7dd4e'
down_revision: Union[str, Sequence[str], None] = '703db884292d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE role RENAME VALUE 'Admin' TO 'ADMIN'")


def downgrade() -> None:
    op.execute("ALTER TYPE role RENAME VALUE 'ADMIN' TO 'Admin'")
