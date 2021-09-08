"""article

Revision ID: 1f725cba805f
Revises: ee54809c099e
Create Date: 2021-09-03 10:51:07.949344

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f725cba805f'
down_revision = 'ee54809c099e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lang', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_id'), 'article', ['id'], unique=False)
    op.create_table('reset_passwords',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_in', sa.DateTime(), nullable=False),
    sa.Column('temporary_password', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reset_passwords_id'), 'reset_passwords', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_reset_passwords_id'), table_name='reset_passwords')
    op.drop_table('reset_passwords')
    op.drop_index(op.f('ix_article_id'), table_name='article')
    op.drop_table('article')
    # ### end Alembic commands ###
