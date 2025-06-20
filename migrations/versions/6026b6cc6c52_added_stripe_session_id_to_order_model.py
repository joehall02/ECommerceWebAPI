"""Added stripe session id to order model

Revision ID: 6026b6cc6c52
Revises: d8cad68812c4
Create Date: 2025-05-31 21:32:02.857089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6026b6cc6c52'
down_revision = 'd8cad68812c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stripe_session_id', sa.String(length=200), nullable=True, server_default='unknown'))

    op.execute('UPDATE "Order" SET stripe_session_id = \'unknown\' WHERE stripe_session_id IS NULL')

    with op.batch_alter_table('Order', schema=None) as batch_op:
        batch_op.alter_column('stripe_session_id', nullable=False, server_default=None)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Order', schema=None) as batch_op:
        batch_op.drop_column('stripe_session_id')

    # ### end Alembic commands ###
