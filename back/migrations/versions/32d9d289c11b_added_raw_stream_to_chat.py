"""added raw stream to chat

Revision ID: 32d9d289c11b
Revises: 3539729fadb2
Create Date: 2025-10-24 11:09:11.575866

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '32d9d289c11b'
down_revision = '3539729fadb2'
branch_labels = None
depends_on = None


def upgrade():
    # Only add the new column to the chat table.
    # Do not drop unrelated tables/indexes here.
    op.add_column("chat", sa.Column("raw_stream", sa.Text(), nullable=True))


def downgrade():
    # Remove the column on downgrade.
    op.drop_column("chat", "raw_stream")