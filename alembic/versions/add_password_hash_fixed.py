"""Add password_hash to User model - SQLite compatible

Revision ID: add_password_hash_fixed
Revises: 51a8dbad3554
Create Date: 2024-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_password_hash_fixed'
down_revision = '51a8dbad3554'
branch_labels = None
depends_on = None


def upgrade():
    # Add password_hash column to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.VARCHAR(length=255), nullable=True))
    
    # SQLite-compatible way to modify account.balance column (if needed)
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.alter_column('balance',
                              existing_type=sa.REAL(),
                              nullable=True)


def downgrade():
    # Remove password_hash column from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('password_hash')
    
    # Revert account.balance column changes
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.alter_column('balance',
                              existing_type=sa.REAL(),
                              nullable=False)