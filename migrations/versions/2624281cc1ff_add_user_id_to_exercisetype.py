"""add user_id to ExerciseType

Revision ID: 2624281cc1ff
Revises: de9cf00db031
Create Date: 2025-08-08 01:01:49.975857

"""

import sqlalchemy as sa
from alembic import op

revision = "2624281cc1ff"
down_revision = "de9cf00db031"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("exercise_type", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key("fk_exercise_type_user_id", "user", ["user_id"], ["id"])


def downgrade():
    with op.batch_alter_table("exercise_type", schema=None) as batch_op:
        batch_op.drop_constraint("fk_exercise_type_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")
