"""add user_id

Revision ID: de9cf00db031
Revises: 60eff82dc257
Create Date: 2025-08-07 17:43:11.735025

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'de9cf00db031'
down_revision = '60eff82dc257'
branch_labels = None
depends_on = None


def upgrade():
    # dodajemy kolumnę user_id i klucz obcy do istniejącej tabeli
    with op.batch_alter_table('exercise_type', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_exercise_type_user_id',  # nazwa constraintu
            'user',                      # docelowa tabela
            ['user_id'],                 # kolumna lokalna
            ['id']                       # kolumna zdalna
        )


def downgrade():
    # usuwamy kolumnę i constraint
    with op.batch_alter_table('exercise_type', schema=None) as batch_op:
        batch_op.drop_constraint('fk_exercise_type_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')
