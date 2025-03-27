from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # "admin" or "user"

    def set_password(self, password):
        """Hash and store password securely"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify user-entered password"""
        return check_password_hash(self.password_hash, password)

    def serialize(self):
        """Convert object to JSON format (excluding password)"""
        return {"id": self.id, "username": self.username, "role": self.role}
    

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order_status = db.Column(db.String(20), default="Completed")  # Possible values: "Pending", "Completed"

    user = db.relationship('User', backref='orders')
    menu_item = db.relationship('MenuItem', backref='orders')

    def serialize(self):
        """Convert object to JSON format"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "menu_item_id": self.menu_item_id,
            "quantity": self.quantity,
            "order_status": self.order_status,
            "menu_item_name": self.menu_item.name
        }