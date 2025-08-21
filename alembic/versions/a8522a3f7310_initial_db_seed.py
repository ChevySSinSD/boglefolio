"""initial db seed

Revision ID: a8522a3f7310
Revises: 7e186dfc93c4
Create Date: 2025-08-21 09:30:28.028833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8522a3f7310'
down_revision: Union[str, Sequence[str], None] = '7e186dfc93c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
