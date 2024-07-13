from marshmallow import Schema, fields as ma_fields

class SignupSchema(Schema):
    first_name = ma_fields.String(required=True, error_messages={'required': 'First name is required', 'null': 'First name cannot be empty'})
    last_name = ma_fields.String(required=True, error_messages={'required': 'Last name is required', 'null': 'Last name cannot be empty'})
    email = ma_fields.Email(required=True, error_messages={'required': 'Email is required', 'null': 'Email cannot be empty'})
    password = ma_fields.String(required=True, error_messages={'required': 'Password is required', 'null': 'Password cannot be empty'})
    phone_number = ma_fields.String(required=False, error_messages={'null': 'Phone number cannot be empty'})

class LoginSchema(Schema):
    email = ma_fields.Email(required=True, error_messages={'required': 'Email is required', 'null': 'Email cannot be empty'})
    password = ma_fields.String(required=True, error_messages={'required': 'Password is required', 'null': 'Password cannot be empty'})

class ProductSchema(Schema):
    name = ma_fields.String(required=True, error_messages={'required': 'Product name is required', 'null': 'Product name cannot be empty'})
    description = ma_fields.String(required=True, error_messages={'required': 'Product description is required', 'null': 'Product description cannot be empty'})
    price = ma_fields.Decimal(required=True, error_messages={'required': 'Product price is required', 'null': 'Product price cannot be empty'})
    stock = ma_fields.Integer(required=True, error_messages={'required': 'Product stock is required', 'null': 'Product stock cannot be empty'})
    category_id = ma_fields.Integer(required=True, error_messages={'required': 'Category ID is required', 'null': 'Category ID cannot be empty'})

class FeaturedProductSchema(Schema):
    product_id = ma_fields.Integer(required=True, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})

class ProductImageSchema(Schema):
    image_path = ma_fields.String(required=True, error_messages={'required': 'Image path is required', 'null': 'Image path cannot be empty'})
    product_id = ma_fields.Integer(required=True, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})

class OrderSchema(Schema):
    order_date = ma_fields.DateTime(required=True, error_messages={'required': 'Order date is required', 'null': 'Order date cannot be empty'})
    total_price = ma_fields.Decimal(required=True, error_messages={'required': 'Total price is required', 'null': 'Total price cannot be empty'})
    status = ma_fields.String(required=True, error_messages={'required': 'Status is required', 'null': 'Status cannot be empty'})
    user_id = ma_fields.Integer(required=True, error_messages={'required': 'User ID is required', 'null': 'User ID cannot be empty'})
    address_id = ma_fields.Integer(required=True, error_messages={'required': 'Address ID is required', 'null': 'Address ID cannot be empty'})
    payment_id = ma_fields.Integer(required=True, error_messages={'required': 'Payment ID is required', 'null': 'Payment ID cannot be empty'})

class CategorySchema(Schema):
    name = ma_fields.String(required=True, error_messages={'required': 'Category name is required', 'null': 'Category name cannot be empty'})

class ProductSchema(Schema):
    name = ma_fields.String(required=True, error_messages={'required': 'Product name is required', 'null': 'Product name cannot be empty'})
    description = ma_fields.String(required=True, error_messages={'required': 'Product description is required', 'null': 'Product description cannot be empty'})
    price = ma_fields.Decimal(required=True, error_messages={'required': 'Product price is required', 'null': 'Product price cannot be empty'})
    stock = ma_fields.Integer(required=True, error_messages={'required': 'Product stock is required', 'null': 'Product stock cannot be empty'})
    category_id = ma_fields.Integer(required=True, error_messages={'required': 'Category ID is required', 'null': 'Category ID cannot be empty'})

class PaymentSchema(Schema):
    card_number = ma_fields.Integer(required=True, error_messages={'required': 'Card number is required', 'null': 'Card number cannot be empty'})
    name_on_card = ma_fields.String(required=True, error_messages={'required': 'Name of card is required', 'null': 'Name of card cannot be empty'})
    expiry_date = ma_fields.Date(required=True, error_messages={'required': 'Expiry date is required', 'null': 'Expiry date cannot be empty'})
    security_code = ma_fields.Integer(required=True, error_messages={'required': 'Security code is required', 'null': 'Security code cannot be empty'})