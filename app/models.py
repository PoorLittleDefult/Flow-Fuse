from app import db
from datetime import datetime
from flask_login import UserMixin

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Numeric, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Float, default=0)


    def is_active(self):
        return True  
    
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username}>"


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('item.user_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    cost_of_item = db.Column(db.Numeric, db.ForeignKey('item.price'), nullable=False)