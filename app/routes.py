from app import app, db
from app import models
from flask import render_template, redirect, request, url_for
from app.models import Item

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/product', methods=['GET', 'POST'])
def product():
    items = Item.query.all()
    return render_template('product.html', items=items)


@app.route('/new-item', methods=['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        category = request.form['category']
        price = request.form['price']
        item = Item(item_name=item_name, category=category, price=price)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_item.html')