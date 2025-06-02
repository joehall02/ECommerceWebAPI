from exts import db

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)    
    email = db.Column(db.String(100), nullable=True, unique=True) # unique=True ensures that no two users can have the same email, nullable=True allows for NULL values for guest users
    password = db.Column(db.String(300), nullable=False)    
    stripe_customer_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    last_verification_email_sent = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    addresses = db.relationship('Address', backref='user', lazy=True, cascade="all, delete", passive_deletes=True) # cascade="all, delete" ensures that when a user is deleted, all addresses are also deleted and passive_deletes=True ensures that the database handles the deletion of the addresses
    carts = db.relationship('Cart', backref='user', lazy=True, uselist=False, cascade="all, delete", passive_deletes=True) # uselist=False ensures that a user can only have one cart, cascade="all, delete" ensures that when a user is deleted, their cart is also deleted, and passive_deletes=True ensures that the database handles the deletion of the cart
    orders = db.relationship('Order', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.id} {self.full_name}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Address(db.Model):
    __tablename__ = 'Address'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    address_line_1 = db.Column(db.String(100), nullable=False)
    address_line_2 = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(20), nullable=False)
    is_default = db.Column(db.Boolean, nullable=False)

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Address {self.id} {self.address_line_1}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
class Category(db.Model):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    # Relationships
    products = db.relationship('Product', backref='category', lazy=True, cascade="all, delete", passive_deletes=True) # cascade="all, delete" ensures that when a category is deleted, all products in that category are also deleted and passive_deletes=True ensures that the database handles the deletion of the products

    def __repr__(self):
        return f'<Category {self.id} {self.name}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Product(db.Model):
    __tablename__ = 'Product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    reserved_stock = db.Column(db.Integer, nullable=False, default=0) # Reserved stock is the stock that is reserved in the cart but not yet purchased
    stripe_product_id = db.Column(db.String(50), nullable=True) # Stripe product id
    stripe_price_id = db.Column(db.String(50), nullable=True) # Stripe price id

    # Foreign key
    category_id = db.Column(db.Integer, db.ForeignKey('Category.id', ondelete='CASCADE'), nullable=False) # ondelete='CASCADE' ensures that when a category is deleted, all products in that category are also deleted

    # Relationships
    product_images = db.relationship('ProductImage', backref='product', lazy=True, cascade="all, delete", passive_deletes=True) # cascade="all, delete" ensures that when a product is deleted, all product images are also deleted and passive_deletes=True ensures that the database handles the deletion of the product images
    featured_products = db.relationship('FeaturedProduct', backref='product', lazy=True, uselist=False, cascade="all, delete", passive_deletes=True) # uselist=False ensures that a product can only be featured once. cascade="all, delete" ensures that when a product is deleted, the featured product is also deleted and passive_deletes=True ensures that the database handles the deletion of the featured product
    cart_products = db.relationship('CartProduct', backref='product', lazy=True, cascade="all, delete", passive_deletes=True) # cascade="all, delete" ensures that when a product is deleted, all cart products are also deleted and passive_deletes=True ensures that the database handles the deletion of the cart products

    def __repr__(self):
        return f'<Product {self.id} {self.name}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Cart(db.Model):
    __tablename__ = 'Cart'
    id = db.Column(db.Integer, primary_key=True)
    locked = db.Column(db.Boolean, nullable=False, default=False) # Indicates if the cart is locked
    locked_at = db.Column(db.DateTime(timezone=True), nullable=True) # Date and time when the cart was locked
    product_added_at = db.Column(db.DateTime(timezone=True), nullable=True) # Date and time when the item was added to the cart

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'), nullable=False) # ondelete='CASCADE' ensures that when a user is deleted, their cart is also deleted

    # Relationships
    cart_products = db.relationship('CartProduct', backref='cart', lazy=True, cascade="all, delete", passive_deletes=True) # cascade="all, delete" ensures that when a cart is deleted, all cart products are also deleted and passive_deletes=True ensures that the database handles the deletion of the cart products

    def __repr__(self):
        return f'<Cart {self.id}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

# Cart and Product have a many-to-many relationship so an association object is required
class CartProduct(db.Model):
    __tablename__ = 'Cart_Product'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    # Foreign keys
    cart_id = db.Column(db.Integer, db.ForeignKey('Cart.id', ondelete='CASCADE'), nullable=False) # ondelete='CASCADE' ensures that when a cart is deleted, all cart products are also deleted
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id', ondelete='CASCADE'), nullable=False) # ondelete='CASCADE' ensures that when a product is deleted, all cart products are also deleted

    def __repr__(self):
        return f'<CartProduct {self.id} {self.quantity}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
class ProductImage(db.Model):
    __tablename__ = 'Product_Image'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(1000), nullable=False)

    # Foreign key
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id', ondelete='CASCADE'), nullable=False) # ondelete='CASCADE' ensures that when a product is deleted, all product images are also deleted

    def __repr__(self):
        return f'<ProductImage {self.id} {self.image_path}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
class FeaturedProduct(db.Model):
    __tablename__ = 'Featured_Product'
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id', ondelete='CASCADE'), unique=True, nullable=False) # ondelete='CASCADE' ensures that when a product is deleted, the featured product is also deleted

    def __repr__(self):
        return f'<FeaturedProduct {self.id}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
class Order(db.Model):
    __tablename__ = 'Order'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime(timezone=True), nullable=False)
    total_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    address_line_1 = db.Column(db.String(100), nullable=False)
    address_line_2 = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    stripe_session_id = db.Column(db.String(200), nullable=False)
    tracking_url = db.Column(db.String(300), nullable=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=True)  # Allow NULL

    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete", passive_deletes=True) # cascade="all, delete" ensures that when an order is deleted, all order items are also deleted and passive_deletes=True ensures that the database handles the deletion of the order items    

    def __repr__(self):
        return f'<Order {self.id} {self.total_price}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
class OrderItem(db.Model):
    __tablename__ = 'Order_Item'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False) # Price at the time of purchase
    name = db.Column(db.String(100), nullable=False) # Product name at the time of purchase

    # Foreign key
    order_id = db.Column(db.Integer, db.ForeignKey('Order.id', ondelete='CASCADE'), nullable=False) # ondelete='CASCADE' ensures that when an order is deleted, all order items are also deleted
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id', ondelete='SET NULL'), nullable=True)  # Allow NULL
    
    def __repr__(self):
        return f'<OrderItem {self.id} {self.quantity} {self.price}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()