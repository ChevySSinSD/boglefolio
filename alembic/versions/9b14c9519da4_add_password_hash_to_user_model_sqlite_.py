"""Add password_hash to User model - SQLite compatible

Revision ID: 9b14c9519da4
Revises: add_password_hash_fixed
Create Date: 2025-09-04 07:46:12.636537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '9b14c9519da4'
down_revision: Union[str, Sequence[str], None] = 'add_password_hash_fixed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
