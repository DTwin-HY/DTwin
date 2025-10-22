"""create users

Revision ID: 7471de4727cf
Revises: d19cb545f7c3
Create Date: 2025-10-22 19:16:27.735220
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7471de4727cf'
down_revision = 'd19cb545f7c3'
branch_labels = None
depends_on = None


def upgrade():
    # create users table (adjust types/constraints to match your SQLAlchemy model)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('username', sa.String(length=150), nullable=False, unique=True),
        sa.Column('password', sa.String(length=255), nullable=False),
    )


def downgrade():
    op.drop_table('users')