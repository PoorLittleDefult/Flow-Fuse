from app import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String)
    category = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)



