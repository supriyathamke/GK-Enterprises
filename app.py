
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "gk_enterprises_secret_key_2026"


# Product details
PRODUCTS = [
    {"id": 1, "name": "Broom", "price": 120, "image": "broom.jpg",
     "description": "Useful broom for cleaning floors."},
    {"id": 2, "name": "Bucket", "price": 180, "image": "bucket.jpg",
     "description": "Strong bucket for household cleaning."},
    {"id": 3, "name": "Toilet Cleaner Brush", "price": 80,
     "image": "toilet_brush.jpg",
     "description": "Brush for easy toilet cleaning."},
    {"id": 4, "name": "Floor Cleaner", "price": 120,
     "image": "floor_cleaner.jpg",
     "description": "Liquid for regular floor cleaning."},
    {"id": 5, "name": "Scotch Brite", "price": 40,
     "image": "scotch_brite.jpg",
     "description": "Scrubber for cleaning surfaces."},
    {"id": 6, "name": "Cleaning Cloth", "price": 60,
     "image": "cleaning_cloth.jpg",
     "description": "Cloth for home and office cleaning."},
    {"id": 7, "name": "Dustpan", "price": 70, "image": "dustpan.jpg",
     "description": "Useful for collecting dust and waste."},
    {"id": 8, "name": "Floor Mop", "price": 150, "image": "floor_mop.jpg",
     "description": "Mop for regular floor cleaning."},
    {"id": 9, "name": "Harpic", "price": 110, "image": "harpic.jpg",
     "description": "Liquid for toilet cleaning."},
    {"id": 10, "name": "Naphthalene Balls", "price": 60,
     "image": "naphthalene_balls.jpg",
     "description": "Useful for storage areas."},
    {"id": 11, "name": "Room Freshener", "price": 100,
     "image": "room_freshener.jpg",
     "description": "Helps keep rooms fresh."},
    {"id": 12, "name": "Hand Gloves", "price": 80,
     "image": "hand_gloves.jpg",
     "description": "Gloves for cleaning work."}
]


# Connect to MySQL
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="gk_enterprises"
    )


# Check customer login
def login_required(function):
    @wraps(function)
    def check_login(*args, **kwargs):
        if "customer_id" not in session:
            flash("Please log in to continue.")
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return check_login


# Home page
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not username or not password or not confirm_password:
        flash("Please fill in all fields.")
        return redirect(url_for("register"))

    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect(url_for("register"))

    if len(password) < 8:
        flash("Password must have at least 8 characters.")
        return redirect(url_for("register"))

    db = None
    cursor = None

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM customers WHERE name = %s",
            (username,)
        )

        if cursor.fetchone():
            flash("Username already exists. Please choose another.")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO customers (name, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )

        db.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))

    except mysql.connector.Error as error:
        print("Database error:", error)
        flash("Could not register. Please check your MySQL database.")
        return redirect(url_for("register"))

    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("Please enter your username and password.")
        return redirect(url_for("login"))

    db = None
    cursor = None

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM customers WHERE name = %s",
            (username,)
        )

        customer = cursor.fetchone()

        if customer and check_password_hash(
            customer["password_hash"], password
        ):
            session["customer_id"] = customer["id"]
            session["customer_name"] = customer["name"]
            flash("Login successful!")
            return redirect(url_for("home"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    except mysql.connector.Error as error:
        print("Database error:", error)
        flash("Could not log in. Please check your MySQL database.")
        return redirect(url_for("login"))

    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


# Products page
@app.route("/products")
@login_required
def products():
    return render_template("products.html", products=PRODUCTS)


# Add selected quantity to cart
@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = next(
        (item for item in PRODUCTS if item["id"] == product_id),
        None
    )

    if product is None:
        flash("Product not found.")
        return redirect(url_for("products"))

    try:
        quantity = int(request.form.get("quantity", 1))
        if quantity < 1 or quantity > 99:
            raise ValueError
    except (ValueError, TypeError):
        flash("Please select a quantity between 1 and 99.")
        return redirect(url_for("products"))

    cart_items = session.get("cart", {})
    product_key = str(product_id)
    cart_items[product_key] = cart_items.get(product_key, 0) + quantity

    session["cart"] = cart_items
    flash(str(quantity) + " " + product["name"] + " added to cart!")
    return redirect(url_for("products"))


# Increase or decrease quantity on cart page
@app.route("/update_cart/<int:product_id>/<action>", methods=["POST"])
@login_required
def update_cart(product_id, action):
    cart_items = session.get("cart", {})
    product_key = str(product_id)

    if product_key not in cart_items:
        return redirect(url_for("cart"))

    if action == "increase":
        if cart_items[product_key] < 99:
            cart_items[product_key] += 1

    elif action == "decrease":
        cart_items[product_key] -= 1

        if cart_items[product_key] <= 0:
            del cart_items[product_key]

    session["cart"] = cart_items
    return redirect(url_for("cart"))


# View cart
@app.route("/cart")
@login_required
def cart():
    cart_items = session.get("cart", {})
    cart_products = []
    total = 0

    for product in PRODUCTS:
        product_key = str(product["id"])

        if product_key in cart_items:
            quantity = cart_items[product_key]
            item_total = product["price"] * quantity

            cart_products.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "item_total": item_total,
                "image": product["image"]
            })

            total += item_total

    return render_template(
        "cart.html",
        cart_items=cart_products,
        total=total
    )


# Remove product from cart
@app.route("/remove_from_cart/<int:product_id>", methods=["POST"])
@login_required
def remove_from_cart(product_id):
    cart_items = session.get("cart", {})
    product_key = str(product_id)

    if product_key in cart_items:
        del cart_items[product_key]
        session["cart"] = cart_items
        flash("Product removed from cart.")

    return redirect(url_for("cart"))


# About page
@app.route("/about")
@login_required
def about():
    return render_template("about.html")


# Contact page
@app.route("/contact")
@login_required
def contact():
    return render_template("contact.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out successfully.")
    return redirect(url_for("home"))


# Start website
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5001)
