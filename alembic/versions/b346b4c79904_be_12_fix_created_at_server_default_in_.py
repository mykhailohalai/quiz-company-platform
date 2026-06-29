"""BE-12: fix created_at server_default in quiz_results

Revision ID: b346b4c79904
Revises: 1c91aec90e8d
Create Date: 2026-06-22 17:01:24.066521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b346b4c79904'
down_revision: Union[str, Sequence[str], None] = '1c91aec90e8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
