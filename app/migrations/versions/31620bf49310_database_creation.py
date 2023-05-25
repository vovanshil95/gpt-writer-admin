"""database creation

Revision ID: 31620bf49310
Revises: 
Create Date: 2023-05-19 14:25:14.564124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31620bf49310'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gpt_interaction',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('gpt_answer', sa.String(), nullable=False),
    sa.Column('time_happened', sa.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prompt_blank',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('text_data', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('question',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('text_data', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('filled_prompt',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('text_data', sa.String(), nullable=False),
    sa.Column('gpt_interaction_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['gpt_interaction_id'], ['gpt_interaction.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('question_prompt_blank',
    sa.Column('question_id', sa.UUID(), nullable=False),
    sa.Column('prompt_blank_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['prompt_blank_id'], ['prompt_blank.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.PrimaryKeyConstraint('question_id', 'prompt_blank_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('question_prompt_blank')
    op.drop_table('filled_prompt')
    op.drop_table('question')
    op.drop_table('prompt_blank')
    op.drop_table('gpt_interaction')
    # ### end Alembic commands ###
