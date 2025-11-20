"""Add product_id column and populate sequentially

Revision ID: 72f55e3ccaed
Revises: 32d9d289c11b
Create Date: 2025-11-20 12:33:59.030641
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "72f55e3ccaed"
down_revision = "32d9d289c11b"
branch_labels = None
depends_on = None


def upgrade():
    # 1) Lisää product_id ensin nullable=True
    with op.batch_alter_table("sales", schema=None) as batch_op:
        batch_op.add_column(sa.Column("product_id", sa.Integer(), nullable=True))

    # 2) Täytä product_id arvoilla 1,2,3,... sales.id-järjestyksessä
    op.execute(
        """
        WITH numbered AS (
            SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
            FROM sales
        )
        UPDATE sales s
        SET product_id = n.rn
        FROM numbered n
        WHERE s.id = n.id;
        """
    )

    # 3) Tee sarakkeesta NOT NULL
    with op.batch_alter_table("sales", schema=None) as batch_op:
        batch_op.alter_column(
            "product_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade():
    # Palauta tilanne: poista product_id
    with op.batch_alter_table("sales", schema=None) as batch_op:
        batch_op.drop_column("product_id")
