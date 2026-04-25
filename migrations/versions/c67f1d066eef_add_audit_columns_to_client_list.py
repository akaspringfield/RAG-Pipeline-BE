"""add audit columns to client_list

Revision ID: c67f1d066eef
Revises: c575c10808c9
Create Date: 2026-04-25 10:38:23.362040

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c67f1d066eef'
down_revision = 'c575c10808c9'
branch_labels = None
depends_on = None



def upgrade():

    # ---------------- password reset ----------------
    op.create_table(
        'password_resets',
        sa.Column('uuid', sa.UUID(), nullable=False),
        sa.Column('client_uuid', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('uuid')
    )

    # ---------------- blacklist ----------------
    op.create_table(
        'token_blacklist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jti')
    )

    # ---------------- add columns ----------------
    with op.batch_alter_table('biscuits') as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()')))
        batch_op.add_column(sa.Column('updated_on', sa.DateTime(), server_default=sa.text('now()')))
        batch_op.add_column(sa.Column('updated_by', sa.UUID(), nullable=True))

        batch_op.create_unique_constraint('uq_biscuits_client_uuid', ['client_uuid'])
        batch_op.create_foreign_key(
            'fk_biscuits_client',
            'client_list',
            ['client_uuid'],
            ['uuid']
        )

    # ---------------- backfill ----------------
    op.execute("""
    UPDATE biscuits
    SET password_hash = 'TEMP_HASH'
    WHERE password_hash IS NULL
    """)

    # ---------------- enforce NOT NULL ----------------
    with op.batch_alter_table('biscuits') as batch_op:
        batch_op.alter_column('password_hash', nullable=False)
        

def downgrade():

    # 🔥 remove blacklist + reset tables
    op.drop_table('token_blacklist')
    op.drop_table('password_resets')

    # 🔥 revert biscuits safely
    with op.batch_alter_table('biscuits') as batch_op:
        batch_op.drop_constraint('uq_biscuits_client_uuid', type_='unique')
        batch_op.drop_constraint('fk_biscuits_client', type_='foreignkey')

        batch_op.drop_column('updated_by')
        batch_op.drop_column('updated_on')
        batch_op.drop_column('created_on')
        batch_op.drop_column('password_hash')

    # ⚠️ DO NOT touch:
    # - client_list.role_uuid
    # - client_sessions.expires_at