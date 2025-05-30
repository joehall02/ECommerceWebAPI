"""Changed DateTime columns to be timezone aware

Revision ID: d8cad68812c4
Revises: de19ad23a209
Create Date: 2025-05-11 14:38:16.256545

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd8cad68812c4'
down_revision = 'de19ad23a209'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Cart', schema=None) as batch_op:
        batch_op.alter_column('locked_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
        batch_op.alter_column('product_added_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)

    with op.batch_alter_table('Order', schema=None) as batch_op:
        batch_op.alter_column('order_date',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)

    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
        batch_op.alter_column('last_verification_email_sent',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.alter_column('last_verification_email_sent',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    with op.batch_alter_table('Order', schema=None) as batch_op:
        batch_op.alter_column('order_date',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    with op.batch_alter_table('Cart', schema=None) as batch_op:
        batch_op.alter_column('product_added_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
        batch_op.alter_column('locked_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)

    # ### end Alembic commands ###
