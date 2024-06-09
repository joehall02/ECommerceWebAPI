"""empty message

Revision ID: 035cec603bf4
Revises: 5df61b4e831c
Create Date: 2024-06-09 18:04:08.768207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '035cec603bf4'
down_revision: Union[str, None] = '5df61b4e831c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=300), nullable=False),
    sa.Column('phone_number', sa.String(length=100), nullable=True),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('Address',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address_line_1', sa.String(length=100), nullable=False),
    sa.Column('address_line_2', sa.String(length=100), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=False),
    sa.Column('postcode', sa.String(length=20), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Cart',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_number', sa.Integer(), nullable=False),
    sa.Column('name_on_card', sa.String(length=100), nullable=False),
    sa.Column('expiry_date', sa.DateTime(), nullable=False),
    sa.Column('security_code', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.Column('price', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['Category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Cart_Product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('cart_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cart_id'], ['Cart.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Featured_Product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('product_id')
    )
    op.create_table('Order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_date', sa.DateTime(), nullable=False),
    sa.Column('total_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('address_id', sa.Integer(), nullable=False),
    sa.Column('payment_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['address_id'], ['Address.id'], ),
    sa.ForeignKeyConstraint(['payment_id'], ['Payment.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Product_Image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_path', sa.String(length=1000), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Order_Item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['Order.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Order_Item')
    op.drop_table('Product_Image')
    op.drop_table('Order')
    op.drop_table('Featured_Product')
    op.drop_table('Cart_Product')
    op.drop_table('Product')
    op.drop_table('Payment')
    op.drop_table('Cart')
    op.drop_table('Address')
    op.drop_table('User')
    op.drop_table('Category')
    # ### end Alembic commands ###
