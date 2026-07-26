"""Add multiple answer option to quiz

Revision ID: eca4f369a656
Revises: 00e460544b7c
Create Date: 2026-06-19 15:18:38.393966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eca4f369a656'
down_revision: Union[str, Sequence[str], None] = '00e460544b7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    questiontype = sa.Enum('SingleAnswer', 'MultipleAnswer', name='questiontype')
    questiontype.create(op.get_bind())
    op.add_column('questions', sa.Column('question_type', questiontype, nullable=False, server_default='SingleAnswer'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('questions', 'question_type')
    sa.Enum(name='questiontype').drop(op.get_bind())
