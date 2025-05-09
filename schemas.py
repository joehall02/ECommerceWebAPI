from marshmallow import Schema, fields as ma_fields

# Auth schemas
class SignupSchema(Schema):
    full_name = ma_fields.String(required=True, error_messages={'required': 'Full name is required', 'null': 'Full name cannot be empty'})    
    email = ma_fields.Email(required=True, error_messages={'required': 'Email is required', 'null': 'Email cannot be empty'})
    password = ma_fields.String(required=True, error_messages={'required': 'Password is required', 'null': 'Password cannot be empty'})    
    role = ma_fields.String(required=False, error_messages={'null': 'Role cannot be empty'})

class LoginSchema(Schema):
    email = ma_fields.Email(required=True, error_messages={'required': 'Email is required', 'null': 'Email cannot be empty'})
    password = ma_fields.String(required=True, error_messages={'required': 'Password is required', 'null': 'Password cannot be empty'})
    remember_me = ma_fields.Boolean(required=True, error_messages={'required': 'Remember me is required', 'null': 'Remember me cannot be empty'})

# Product schemas
class ProductSchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})
    name = ma_fields.String(required=True, error_messages={'required': 'Product name is required', 'null': 'Product name cannot be empty'})
    description = ma_fields.String(required=True, error_messages={'required': 'Product description is required', 'null': 'Product description cannot be empty'})
    price = ma_fields.Decimal(required=True, error_messages={'required': 'Product price is required', 'null': 'Product price cannot be empty'})
    stock = ma_fields.Integer(required=True, error_messages={'required': 'Product stock is required', 'null': 'Product stock cannot be empty'})
    reserved_stock = ma_fields.Integer(required=False, error_messages={'required': 'Reserved stock is required', 'null': 'Reserved stock cannot be empty'})
    category_id = ma_fields.Integer(required=True, error_messages={'required': 'Category ID is required', 'null': 'Category ID cannot be empty'})

class ProductShopSchema(Schema):
    id = ma_fields.Integer(required=True, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})
    name = ma_fields.String(required=True, error_messages={'required': 'Product name is required', 'null': 'Product name cannot be empty'})
    price = ma_fields.Decimal(required=True, error_messages={'required': 'Product price is required', 'null': 'Product price cannot be empty'})
    stock = ma_fields.Integer(required=True, error_messages={'required': 'Product stock is required', 'null': 'Product stock cannot be empty'})
    image_path = ma_fields.String(required=True, error_messages={'required': 'Image path is required', 'null': 'Image path cannot be empty'})
    category_name = ma_fields.String(required=True, error_messages={'required': 'Category name is required', 'null': 'Category name cannot be empty'})

class ProductAdminSchema(Schema):
    id = ma_fields.Integer(required=True, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})
    name = ma_fields.String(required=True, error_messages={'required': 'Product name is required', 'null': 'Product name cannot be empty'})
    price = ma_fields.Decimal(required=True, error_messages={'required': 'Product price is required', 'null': 'Product price cannot be empty'})
    stock = ma_fields.Integer(required=True, error_messages={'required': 'Product stock is required', 'null': 'Product stock cannot be empty'})
    reserved_stock = ma_fields.Integer(required=True, error_messages={'required': 'Reserved stock is required', 'null': 'Reserved stock cannot be empty'})

class FeaturedProductSchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'Featured product ID is required', 'null': 'Featured product ID cannot be empty'})
    product_id = ma_fields.Integer(required=True, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})

class ProductImageSchema(Schema):
    image_path = ma_fields.String(required=True, error_messages={'required': 'Image path is required', 'null': 'Image path cannot be empty'})
    product_id = ma_fields.Integer(required=True, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})

# Order schemas
class OrderSchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'Order ID is required', 'null': 'Order ID cannot be empty'})
    order_date = ma_fields.Date(required=True, error_messages={'required': 'Order date is required', 'null': 'Order date cannot be empty'})
    total_price = ma_fields.Decimal(required=True, error_messages={'required': 'Total price is required', 'null': 'Total price cannot be empty'})
    status = ma_fields.String(required=True, error_messages={'required': 'Status is required', 'null': 'Status cannot be empty'})
    full_name = ma_fields.String(required=True, error_messages={'required': 'Full name is required', 'null': 'Full name cannot be empty'})
    address_line_1 = ma_fields.String(required=True, error_messages={'required': 'Address line 1 is required', 'null': 'Address line 1 cannot be empty'})
    address_line_2 = ma_fields.String(required=False, error_messages={'null': 'Address line 2 cannot be empty'})
    city = ma_fields.String(required=True, error_messages={'required': 'City is required', 'null': 'City cannot be empty'})
    postcode = ma_fields.String(required=True, error_messages={'required': 'Postcode is required', 'null': 'City cannot be empty'})
    customer_email = ma_fields.String(required=True, error_messages={'required': 'Customer email is required', 'null': 'Customer email cannot be empty'})
    user_id = ma_fields.Integer(required=True, error_messages={'required': 'User ID is required', 'null': 'User ID cannot be empty'})
    
# Order admin schema
class OrderAdminSchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'Order ID is required', 'null': 'Order ID cannot be empty'})
    order_date = ma_fields.Date(required=True, error_messages={'required': 'Order date is required', 'null': 'Order date cannot be empty'})
    total_price = ma_fields.Decimal(required=True, error_messages={'required': 'Total price is required', 'null': 'Total price cannot be empty'})
    status = ma_fields.String(required=True, error_messages={'required': 'Status is required', 'null': 'Status cannot be empty'})
    full_name = ma_fields.String(required=True, error_messages={'required': 'Full name is required', 'null': 'Full name cannot be empty'})

class OrderItemSchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'Order item ID is required', 'null': 'Order item ID cannot be empty'})
    quantity = ma_fields.Integer(required=True, error_messages={'required': 'Quantity is required', 'null': 'Quantity cannot be empty'})
    name = ma_fields.String(required=True, error_messages={'required': 'Product name is required', 'null': 'Product name cannot be empty'})
    price = ma_fields.Decimal(required=True, error_messages={'required': 'Price is required', 'null': 'Price cannot be empty'})
    product_image = ma_fields.String(required=False, error_messages={'null': 'Product image cannot be empty'})
    product_id = ma_fields.Integer(required=False, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})
    order_id = ma_fields.Integer(required=True, error_messages={'required': 'Order ID is required', 'null': 'Order ID cannot be empty'})

class OrderItemCombinedSchema(Schema):
    order = ma_fields.Nested(OrderSchema)
    order_items = ma_fields.List(ma_fields.Nested(OrderItemSchema)) # List of order items

class OrderItemCombinedAdminSchema(Schema):
    order = ma_fields.Nested(OrderSchema)
    order_items = ma_fields.List(ma_fields.Nested(OrderItemSchema)) # List of order items
    customer_name = ma_fields.String(required=True, error_messages={'required': 'Customer name is required', 'null': 'Customer name cannot be empty'})    

# Category schemas
class CategorySchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'Category ID is required', 'null': 'Category ID cannot be empty'})
    name = ma_fields.String(required=True, error_messages={'required': 'Category name is required', 'null': 'Category name cannot be empty'})

# Cart schemas
class CartSchema(Schema):
    user_id = ma_fields.Integer(required=True, error_messages={'required': 'User ID is required', 'null': 'User ID cannot be empty'})

class CartProductSchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'Cart product ID is required', 'null': 'Cart product ID cannot be empty'})
    quantity = ma_fields.Integer(required=True, error_messages={'required': 'Quantity is required', 'null': 'Quantity cannot be empty'})
    product_id = ma_fields.Integer(required=True, error_messages={'required': 'Product ID is required', 'null': 'Product ID cannot be empty'})
    cart_id = ma_fields.Integer(required=True, error_messages={'required': 'Cart ID is required', 'null': 'Cart ID cannot be empty'})

class ProductCartProductCombinedSchema(Schema):
    product = ma_fields.Nested(ProductShopSchema)
    cart_product = ma_fields.Nested(CartProductSchema)

# Address schemas
class AddressSchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'Address ID is required', 'null': 'Address ID cannot be empty'})
    full_name = ma_fields.String(required=True, error_messages={'required': 'Full name is required', 'null': 'Full name cannot be empty'})
    address_line_1 = ma_fields.String(required=True, error_messages={'required': 'Address line 1 is required', 'null': 'Address line 1 cannot be empty'})
    address_line_2 = ma_fields.String(required=False, error_messages={'null': 'Address line 2 cannot be empty'})
    city = ma_fields.String(required=True, error_messages={'required': 'City is required', 'null': 'City cannot be empty'})
    postcode = ma_fields.String(required=True, error_messages={'required': 'Postcode is required', 'null': 'City cannot be empty'})
    is_default = ma_fields.Boolean(required=True, error_messages={'required': 'Default status is required', 'null': 'Default status cannot be empty'})

# User schemas
class UserSchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'User ID is required', 'null': 'User ID cannot be empty'})
    full_name = ma_fields.String(required=True, error_messages={'required': 'Full name is required', 'null': 'Full name cannot be empty'})
    email = ma_fields.Email(required=True, error_messages={'required': 'Email is required', 'null': 'Email cannot be empty'})
    stripe_customer_id = ma_fields.String(required=False, error_messages={'null': 'Stripe customer ID cannot be empty'})
    created_at = ma_fields.DateTime(required=True, error_messages={'required': 'Created at is required', 'null': 'Created at cannot be empty'})
    role = ma_fields.String(required=True, error_messages={'required': 'Role is required', 'null': 'Role cannot be empty'})

class UserAdminSchema(Schema):
    id = ma_fields.Integer(required=False, error_messages={'required': 'User ID is required', 'null': 'User ID cannot be empty'})
    full_name = ma_fields.String(required=True, error_messages={'required': 'Full name is required', 'null': 'Full name cannot be empty'})
    email = ma_fields.Email(required=True, error_messages={'required': 'Email is required', 'null': 'Email cannot be empty'})
    role = ma_fields.String(required=True, error_messages={'required': 'Role is required', 'null': 'Role cannot be empty'})
    