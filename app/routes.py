from app import app, db
from flask import render_template, redirect
from app.models import Item

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/product', methods=['GET', 'POST'])
def product():
    items = Item.query.all()
    return render_template('product.html', items=items)