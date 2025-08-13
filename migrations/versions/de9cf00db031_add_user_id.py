"""add user_id

Revision ID: de9cf00db031
Revises: 60eff82dc257
Create Date: 2025-08-07 17:43:11.735025
"""

import sqlalchemy as sa
from alembic import op

revision = "de9cf00db031"
down_revision = "60eff82dc257"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("exercise_type", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_exercise_type_user_id",
            "user",
            ["user_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("exercise_type", schema=None) as batch_op:
        batch_op.drop_constraint("fk_exercise_type_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")
