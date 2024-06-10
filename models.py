from exts import db

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True) # unique=True ensures that no two users can have the same email
    password = db.Column(db.String(300), nullable=False)
    phone_number = db.Column(db.String(100), nullable=True) # nullable=True allows for the phone number to be empty
    role = db.Column(db.String(50), nullable=False)

    # Relationships
    addresses = db.relationship('Address', backref='user', lazy=True) 
    payments = db.relationship('Payment', backref='user', lazy=True)
    carts = db.relationship('Cart', backref='user', lazy=True, uselist=False) # uselist=False ensures that a user can only have one cart
    orders = db.relationship('Order', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.id} {self.first_name}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Address(db.Model):
    __tablename__ = 'Address'
    id = db.Column(db.Integer, primary_key=True)
    address_line_1 = db.Column(db.String(100), nullable=False)
    address_line_2 = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(20), nullable=False)

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

    def __repr__(self):
        return f'<Address {self.id} {self.address_line_1}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Payment(db.Model):
    __tablename__ = 'Payment'
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.Integer, nullable=False)
    name_on_card = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    security_code = db.Column(db.Integer, nullable=False)

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

    def __repr__(self):
        return f'<Payment {self.id} {self.name_on_card}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
class Category(db.Model):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)

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

    # Foreign key
    category_id = db.Column(db.Integer, db.ForeignKey('Category.id'), nullable=False)

    # Relationships
    product_images = db.relationship('ProductImage', backref='product', lazy=True)
    featured_products = db.relationship('FeaturedProduct', backref='product', lazy=True, uselist=False) # uselist=False ensures that a product can only be featured once
    cart_products = db.relationship('CartProduct', backref='product', lazy=True)

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

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

    # Relationships
    cart_products = db.relationship('CartProduct', backref='cart', lazy=True)

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
    cart_id = db.Column(db.Integer, db.ForeignKey('Cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'), nullable=False)

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
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'), nullable=False)

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
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'), unique=True, nullable=False) 

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
    order_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('Address.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('Payment.id'), nullable=False)

    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    address = db.relationship('Address', backref='order', lazy=True, uselist=False) # uselist=False ensures that an order can only have one address
    payment = db.relationship('Payment', backref='order', lazy=True, uselist=False) # uselist=False ensures that an order can only have one payment

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
    price = db.Column(db.DECIMAL(10, 2), nullable=False)

    # Foreign key
    order_id = db.Column(db.Integer, db.ForeignKey('Order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'), nullable=False)

    def __repr__(self):
        return f'<OrderItem {self.id} {self.quantity} {self.price}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()