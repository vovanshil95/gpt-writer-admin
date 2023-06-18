"""add number to filled prompt

Revision ID: t938q8c1co6w
Revises: 4ade20b0f214
Create Date: 2023-06-18 20:44:43.370773

"""
from alembic import op
import sqlalchemy as sa

import json

revision = 't938q8c1co6w'
down_revision = '4ade20b0f214'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('filled_prompt', sa.Column('number', sa.Integer, nullable=False,server_default='0'))
    op.alter_column('filled_prompt', 'number', server_default=None)
    with open('../db_backups/history_backup.json', 'r') as f:
        id_numbers = json.load(f)
        op.execute(''.join([f"update filled_prompt set number={id_numbers[id]} where id='{id}';" for id in id_numbers]))


def downgrade() -> None:
    op.drop_column('filled_prompt', 'number')
