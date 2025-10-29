"""Delete log table, add chats relationship to users and created chats table

Revision ID: 3539729fadb2
Revises: c7209406c37c
Create Date: 2025-10-24 10:59:11.769849

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3539729fadb2'
down_revision = 'c7209406c37c'
branch_labels = None
depends_on = None


def upgrade():
    # Drop logs safely
    op.execute("DROP TABLE IF EXISTS logs CASCADE")

    # Create chat table
    op.create_table(
        "chat",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("messages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("thread_id", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
    )

    # Indexes
    op.create_index("ix_chat_thread_id", "chat", ["thread_id"], unique=True)
    op.create_index("ix_chat_user_id", "chat", ["user_id"], unique=False)


def downgrade():
    # Drop indexes and table safely
    try:
        op.drop_index("ix_chat_user_id", table_name="chat")
    except Exception:
        pass
    try:
        op.drop_index("ix_chat_thread_id", table_name="chat")
    except Exception:
        pass
    op.execute("DROP TABLE IF EXISTS chat CASCADE")

    # recreate logs table on downgrade
    op.create_table(
        "logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("reply", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )