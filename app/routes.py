from flask import render_template, redirect, request, url_for, session, logging, flash
from flask_login import login_user, current_user, LoginManager, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from passlib.hash import sha256_crypt
from app import app, db
from app.models import Item, User
import time

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def home(): # Retrieve the user from the database
    return render_template('home.html')  # Pass the 'user' object to the template


@app.route('/mission')
def mission():
    return render_template('mission.html')

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
            flash('Username already exists. Please choose a different username.')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['user_id'] = user.id
            print(current_user.id)
            print(current_user.is_authenticated)
            return redirect(url_for('home'))
        else:
            flash('LOGIN FAILED!', 'success')

    return render_template('login.html')


@app.route('/logout/api')
def logout_api():
    session.clear()
    return redirect(url_for('home'))


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


# -------------------- SORTING --------------------


def get_items_sorted_by_price():
    sort_order = request.form.get('sort_order', 'asc')
    if sort_order == 'desc':
        items = Item.query.order_by(Item.price.desc()).all()
    else:
        items = Item.query.order_by(Item.price.asc()).all()
    return items


@app.route('/sort_by_higher_price', methods=['GET', 'POST'])
def sort_by_higher_price():
    if request.method == 'POST':
        items = get_items_sorted_by_price()
        print(Item.query.order_by(Item.price.asc()).all())
        print("WORKING")
        return redirect(url_for('product', items=items))
    else:
        return redirect(url_for('product', items=items))
    

# --------------------------------------------------------

@app.route('/buy_action', methods=['POST'])
def buy_action():
    if current_user.is_authenticated:
        item_id = request.form['item_id']
        item = Item.query.get(item_id)  # Assuming 'item_id' is the primary key of the Item model
        if item:
            if item.user_id is None:
                item.user_id = current_user.id
                db.session.commit()
                flash('Item purchased successfully!', 'success')
            else:
                time.sleep(2.4)
                flash('Item already purchased!', 'error')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('product'))


