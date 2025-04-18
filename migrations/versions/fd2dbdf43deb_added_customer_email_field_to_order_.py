"""Added customer_email field to Order table

Revision ID: fd2dbdf43deb
Revises: 739e0cc05914
Create Date: 2025-02-23 19:27:23.148613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd2dbdf43deb'
down_revision = '739e0cc05914'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customer_email', sa.String(length=100), nullable=False, server_default=''))

    # ### end Alembic commands ###

    # Remove the server default after the column has been populated
    with op.batch_alter_table('Order', schema=None) as batch_op:
        batch_op.alter_column('customer_email', server_default=None)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Order', schema=None) as batch_op:
        batch_op.drop_column('customer_email')

    # ### end Alembic commands ###
