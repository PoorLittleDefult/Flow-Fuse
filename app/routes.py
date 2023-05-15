from app import app, db
from app import models
from flask import render_template, redirect, request, url_for, session, logging, flash
from app.models import Item, User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from sqlalchemy.orm import scoped_session,sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from passlib.hash import sha256_crypt



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
        return redirect(url_for('product'))
    return render_template('new_item.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        print(email)
        fullname = request.form['fullname']
        phone = request.form['phone']
        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password, email=email, fullname=fullname, phone=phone)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different username.', 'danger')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/error')
def error():
    return render_template("404.html")

# Error handler
@app.errorhandler(HTTPException)
def handle_error(error):
    response = {
        "code": error.code,
        "name": error.name,
        "description": error.description,
    }
    
    return render_template(
        "404.html",
        response=response
    )
