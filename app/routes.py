import time
from datetime import datetime
from flask import render_template, redirect, request, url_for
from flask import flash, session, jsonify
from flask_login import login_user, current_user, LoginManager, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from app import app, db
from app.models import Item, User, Purchase, Rating


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    '''Function to load user details'''
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def home():
    '''Route for Home page'''
    return render_template('home.html')


@app.route('/mission')
def mission():
    '''Route for Mission page'''
    return render_template('mission.html')


@app.route('/product', methods=['GET', 'POST'])
def product():
    '''Route for Product page'''
    # query item from database
    items = Item.query.all()
    item_ratings = {}
    for item in items:
        # sort items by rating
        ratings = Rating.query.filter_by(item_id=item.id).all()
        total_ratings = sum([rating.star_rating for rating in ratings])
        # take the average stars on the item
        average_rating = total_ratings / len(ratings) \
            if len(ratings) > 0 else 0
        # give item an average rating
        item_ratings[item.id] = average_rating
    return render_template(
        'product.html', items=items,
        item_ratings=item_ratings
    )


@app.route('/new-item', methods=['GET', 'POST'])
def new_item():
    '''Function for creating a new item that is added to database'''
    # pylint: disable=E1101
    if request.method == 'POST':
        item_name = request.form['item_name']
        category = request.form['category']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']
        item = Item(
            item_name=item_name,
            category=category,
            description=description,
            price=price,
            image_url=image_url
        )
        # add item to database
        db.session.add(item)
        # link to user_id of person who created item
        item.user_id = current_user.id
        db.session.commit()
        return redirect(url_for('product'))

    return render_template('new_item.html')


@app.route('/delete-item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    '''Function to delete individual items from database'''
    # pylint: disable=E1101
    # Retrieve the item
    item = Item.query.get(item_id)
    # Check if the item exists and belongs to the current user
    if item and item.user_id == current_user.id:
        # Delete the item
        db.session.delete(item)
        # commit changes
        db.session.commit()
        flash("Item deleted successfully.", "success")
    else:
        flash("Failed to delete item. Please try again.", "error")

    return redirect(url_for('product'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    '''Function to create an account for a user'''
    # pylint: disable=E1101
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        print(email)
        fullname = request.form['fullname']
        phone = request.form['phone']
        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            password=hashed_password,
            email=email,
            fullname=fullname,
            phone=phone
        )
        # add user to the database
        db.session.add(user)
        try:
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('home'))
        except IntegrityError:
            # reverse changes if user exists already
            db.session.rollback()
            flash(
                'Username already exists. Please choose a different username.'
            )

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Function to login for a user'''
    # pylint: disable=E1101
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # filter user by username
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # login the user
            login_user(user)
            # session user id is the logged in user
            session['user_id'] = user.id
            print(current_user.id)
            print(current_user.is_authenticated)
            return redirect(url_for('home'))
        else:
            flash('LOGIN FAILED!', 'success')

    return render_template('login.html')


@app.route('/logout/api')
def logout_api():
    '''Logout api function that clears the current session'''
    # clear current user session
    session.clear()
    return redirect(url_for('home'))


@app.route('/error')
def error():
    '''Error route for 404 page'''
    return render_template("404.html")


# Error handler
@app.errorhandler(HTTPException)
def handle_error(error):
    '''Error handling function'''
    # pylint: disable=W0621
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
    '''Function sorting items by price'''
    # order by price
    sort_order = request.form.get('sort_order', 'asc')
    if sort_order == 'desc':
        items = Item.query.order_by(Item.price.desc()).all()
    else:
        items = Item.query.order_by(Item.price.asc()).all()
    return items


@app.route('/sort_by_higher_price', methods=['GET', 'POST'])
def sort_by_higher_price():
    '''Function to sort items by highest price'''
    if request.method == 'POST':
        # sort items by price
        items = get_items_sorted_by_price()
        print(Item.query.order_by(Item.price.asc()).all())
        print("WORKING")
        return redirect(url_for('product', items=items))

    return redirect(url_for('product', items=items))

# ---------------------- BUY FUNCTIONS -----------------------------


@app.route('/buy_action', methods=['POST'])
def buy_action():
    '''function for purchasing items'''
    # pylint: disable=W0612
    # pylint: disable=E1101
    # pylint: disable=W0718
    if current_user.is_authenticated:
        item_id = request.form['item_id']
        item = Item.query.get(item_id)

        if item:
            # Check if the user has enough balance to purchase the item
            if current_user.balance >= item.price:
                # Start a database transaction
                db.session.begin(subtransactions=True)

                try:
                    # Deduct the item's cost from the buyer's balance
                    current_user.balance -= int(item.price)

                    # Create a new purchase record
                    purchase = Purchase(
                        buyer_id=current_user.id,
                        seller_id=item.user_id,
                        item_id=item.id,
                        datetime=datetime.now(),
                        cost_of_item=item.price
                    )

                    # Update the item's owner
                    item.user_id = current_user.id

                    # Commit the changes to the database
                    db.session.add(purchase)
                    db.session.commit()

                    # Add the item's cost to the old seller's balance
                    seller = User.query.get(purchase.seller_id)
                    seller.balance += int(item.price)

                    db.session.commit()

                    flash('Item purchased successfully!', 'success')
                except Exception as e:
                    # Handle any exceptions here
                    db.session.rollback()
                    flash('An error occurred during the purchase')
                finally:
                    db.session.close()
            else:
                flash('Insufficient balance!', 'error')
        else:
            flash('Item does not exist!', 'error')

        return redirect(url_for('home'))
    return redirect(url_for('product'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    '''Function for dashboard'''
    # check if current_user is authenticated
    if current_user.is_authenticated:
        user_items = Item.query.filter_by(
            user_id=current_user.id
            ).order_by(Item.price.desc()).all()
        return render_template('dashboard.html', user_items=user_items)
    return redirect(url_for('login'))


@app.route('/snake', methods=['GET', 'POST'])
def snake():
    '''Function for snake and route to snake page'''
    # pylint: disable=E1101
    if request.method == 'POST':
        # Get the score from the form data
        score = int(request.form.get('score'))
        # Update the user's balance based on the score
        current_user.balance += score
        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('snake'))

    return render_template('snake.html')


@app.route('/update_balance', methods=['POST'])
@login_required
def update_balance():
    '''Function for updating balance of a user'''
    # pylint: disable=E1101
    print("UPDATE BALANCE WORKING")
    # Get the score from the request
    score = int(request.json['score'])
    print(score)
    # Calculate the balance based on the score
    balance = float(current_user.balance) + score
    # Update the user's balance in the User table
    current_user.balance = int(balance)
    print(current_user.balance)
    db.session.commit()
    print(f"Balance updated: {balance}")
    # Print the balance
    return jsonify(message='Balance updated')


@app.route('/star-rating', methods=['POST'])
@login_required
def star_rating():
    '''Function for rating posts'''
    # pylint: disable=W0621
    # pylint: disable=E1101
    if request.method == 'POST':
        item_id = int(request.form.get('item_id'))
        print(item_id)
        item = Item.query.filter_by(id=item_id).first()
        print(item)
        # Get the rating value from the form
        star_rating = int(request.form.get('rate'))
        # Default to 0 if 'rate' is not present or not an integer
        print(star_rating)
        if star_rating == 0:
            flash('Please select a rating!', 'error')
            return redirect(url_for('product'))
        else:
            # Get the item ID from the hidden input in the form
            # Get the currently logged-in user's ID
            user_id = current_user.id  # Assuming you are using Flask-Login
            # Check if the user has already rated this item
            existing_rating = Rating.query.filter_by(
                user_id=user_id,
                item_id=item_id
            ).first()
            print(existing_rating)

            if existing_rating:
                # If the user has already rated, update the rating value
                existing_rating.star_rating = star_rating
            else:
                # If the user has not rated, create a new Rating object
                new_rating = Rating(
                    user_id=user_id,
                    item_id=item_id,
                    star_rating=star_rating
                )
                db.session.add(new_rating)
            # Commit the changes to the database
            db.session.commit()
            # Redirect back to the same page after submitting the rating
            return redirect(url_for('product'))
    # Handle cases where the request method is not POST (optional)
    return redirect(url_for('product'))


@app.route('/blockchain', methods=['GET', 'POST'])
def blockchain():
    '''Function for simple blockchain display'''
    # block is the purchase statment
    blocks = Purchase.query.all()
    users = User.query.all()
    return render_template('blockchain.html', blocks=blocks, users=users)
