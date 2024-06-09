"""Increased character limit on password field to accomodate password hashing

Revision ID: 5df61b4e831c
Revises: 
Create Date: 2024-06-09 17:45:05.922014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5df61b4e831c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Featured_Product')
    op.drop_table('Order_Item')
    op.drop_table('Order')
    op.drop_table('Payment')
    op.drop_table('Cart_Product')
    op.drop_table('Cart')
    op.drop_table('Product_Image')
    op.drop_table('Product')
    op.drop_table('Address')
    op.drop_table('User')
    op.drop_table('Category')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Category',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Category_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='Category_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('Address',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Address_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('address_line_1', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('address_line_2', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('postcode', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], name='Address_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Address_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('User',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"User_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('phone_number', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('role', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='User_pkey'),
    sa.UniqueConstraint('email', name='User_email_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('Product_Image',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Product_Image_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('image_path', sa.VARCHAR(length=1000), autoincrement=False, nullable=False),
    sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], name='Product_Image_product_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Product_Image_pkey')
    )
    op.create_table('Cart',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Cart_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], name='Cart_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Cart_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('Cart_Product',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Cart_Product_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('cart_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['cart_id'], ['Cart.id'], name='Cart_Product_cart_id_fkey'),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], name='Cart_Product_product_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Cart_Product_pkey')
    )
    op.create_table('Payment',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Payment_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('card_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name_on_card', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('expiry_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('security_code', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], name='Payment_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Payment_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('Product',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Product_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=1000), autoincrement=False, nullable=False),
    sa.Column('price', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('stock', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['Category.id'], name='Product_category_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Product_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('Order',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Order_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('order_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('total_price', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('address_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('payment_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['address_id'], ['Address.id'], name='Order_address_id_fkey'),
    sa.ForeignKeyConstraint(['payment_id'], ['Payment.id'], name='Order_payment_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], name='Order_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Order_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('Order_Item',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Order_Item_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('price', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('order_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['Order.id'], name='Order_Item_order_id_fkey'),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], name='Order_Item_product_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Order_Item_pkey')
    )
    op.create_table('Featured_Product',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Featured_Product_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], name='Featured_Product_product_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Featured_Product_pkey'),
    sa.UniqueConstraint('product_id', name='Featured_Product_product_id_key')
    )
    # ### end Alembic commands ###
