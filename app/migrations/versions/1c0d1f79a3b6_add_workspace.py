"""add workspace

Revision ID: 1c0d1f79a3b6
Revises: 4ce0babdaa1d
Create Date: 2023-06-16 20:28:28.058928

"""
from alembic import op
import sqlalchemy as sa

import uuid


# revision identifiers, used by Alembic.
revision = '1c0d1f79a3b6'
down_revision = '4ce0babdaa1d'
branch_labels = None
depends_on = None

DEFAULT_ID = uuid.UUID(hex='3fa85f64-5717-4562-b3fc-2c963f66afa6')

def upgrade() -> None:
    workspace_table = op.create_table('workspace',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('initial', sa.BOOLEAN(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.bulk_insert(workspace_table, [{'id': DEFAULT_ID, 'initial': True}])
    op.add_column('favorite_prompt', sa.Column('workspace_id', sa.UUID(), nullable=False, server_default=str(DEFAULT_ID)))
    op.create_foreign_key(None, 'favorite_prompt', 'workspace', ['workspace_id'], ['id'], ondelete='cascade')
    op.alter_column('favorite_prompt_blank', 'favorite_prompt_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.add_column('gpt_interaction', sa.Column('workspace_id', sa.UUID(), nullable=False, server_default=str(DEFAULT_ID)))
    op.create_foreign_key(None, 'gpt_interaction', 'workspace', ['workspace_id'], ['id'], ondelete='cascade')
    op.add_column('match', sa.Column('workspace_id', sa.UUID(), nullable=False, server_default=str(DEFAULT_ID)))
    op.create_foreign_key(None, 'match', 'workspace', ['workspace_id'], ['id'], ondelete='cascade')
    op.add_column('prompt_blank', sa.Column('workspace_id', sa.UUID(), nullable=False, server_default=str(DEFAULT_ID)))
    op.create_foreign_key(None, 'prompt_blank', 'workspace', ['workspace_id'], ['id'], ondelete='cascade')

    op.alter_column('favorite_prompt', 'workspace_id', server_default=None)
    op.alter_column('gpt_interaction', 'workspace_id', server_default=None)
    op.alter_column('match', 'workspace_id', server_default=None)
    op.alter_column('prompt_blank', 'workspace_id', server_default=None)



def downgrade() -> None:
    op.drop_constraint('prompt_blank_workspace_id_fkey', 'prompt_blank', type_='foreignkey')
    op.drop_column('prompt_blank', 'workspace_id')
    op.drop_constraint('match_workspace_id_fkey', 'match', type_='foreignkey')
    op.drop_column('match', 'workspace_id')
    op.drop_constraint('gpt_interaction_workspace_id_fkey', 'gpt_interaction', type_='foreignkey')
    op.drop_column('gpt_interaction', 'workspace_id')
    op.drop_constraint('filled_prompt_workspace_id_fkey', 'filled_prompt', type_='foreignkey')
    op.drop_column('filled_prompt', 'workspace_id')
    op.drop_constraint('favorite_prompt_blank_workspace_id_fkey', 'favorite_prompt_blank', type_='foreignkey')
    op.alter_column('favorite_prompt_blank', 'favorite_prompt_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('favorite_prompt_blank', 'workspace_id')
    op.drop_constraint('favorite_prompt_workspace_id_fkey', 'favorite_prompt', type_='foreignkey')
    op.drop_column('favorite_prompt', 'workspace_id')
    op.drop_table('workspace')
