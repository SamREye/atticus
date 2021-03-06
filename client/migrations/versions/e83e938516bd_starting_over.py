"""starting over

Revision ID: e83e938516bd
Revises: 
Create Date: 2018-08-09 11:25:02.276562

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e83e938516bd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('template',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('code', sa.TEXT(), nullable=True),
    sa.Column('body', sa.TEXT(), nullable=True),
    sa.Column('party_labels', sa.TEXT(), nullable=True),
    sa.Column('params', sa.TEXT(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_index(op.f('ix_template_owner_id'), 'template', ['owner_id'], unique=False)
    op.create_table('contract',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('template_id', sa.Integer(), nullable=True),
    sa.Column('memo', sa.TEXT(), nullable=True),
    sa.Column('params', sa.TEXT(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['contract.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['template.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contract_owner_id'), 'contract', ['owner_id'], unique=False)
    op.create_index(op.f('ix_contract_parent_id'), 'contract', ['parent_id'], unique=False)
    op.create_index(op.f('ix_contract_status'), 'contract', ['status'], unique=False)
    op.create_index(op.f('ix_contract_template_id'), 'contract', ['template_id'], unique=False)
    op.create_table('party',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contract_id', sa.Integer(), nullable=True),
    sa.Column('role', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('signed_on', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['contract_id'], ['contract.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_party_contract_id'), 'party', ['contract_id'], unique=False)
    op.create_index(op.f('ix_party_user_id'), 'party', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_party_user_id'), table_name='party')
    op.drop_index(op.f('ix_party_contract_id'), table_name='party')
    op.drop_table('party')
    op.drop_index(op.f('ix_contract_template_id'), table_name='contract')
    op.drop_index(op.f('ix_contract_status'), table_name='contract')
    op.drop_index(op.f('ix_contract_parent_id'), table_name='contract')
    op.drop_index(op.f('ix_contract_owner_id'), table_name='contract')
    op.drop_table('contract')
    op.drop_index(op.f('ix_template_owner_id'), table_name='template')
    op.drop_table('template')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
