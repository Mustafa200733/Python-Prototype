
from flask import Flask, render_template, request, redirect, url_for, session, g
import os

import sqlite3


app = Flask(__name__, template_folder="../templates", static_folder="../static")

app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")


DATABASE = os.path.join(os.path.dirname(__file__), "shop.db")



def get_db():
    if "_database" not in g:
        g._database = sqlite3.connect(DATABASE)
    return g._database



@app.teardown_appcontext
def close_connection(exception):
    db = g.pop("_database", None)

    if db is not None:
        db.close()



def init_db():
    with app.app_context():

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM products")

        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO products (name, price) VALUES (?, ?)",
                [
                    ("Laptop", 999.99),
                    ("Headset", 59.99),
                    ("Muis", 29.99)
                ]
            )

        cursor.execute("SELECT COUNT(*) FROM users")

        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("admin", "1234")
            )

        db.commit()


init_db()



@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            session["user"] = username
            session["cart"] = {}  # lege winkelwagen
            return redirect(url_for("home"))
        else:
            error = "Onjuiste gebruikersnaam of wachtwoord."

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            error = "Vul gebruikersnaam en wachtwoord in."
            return render_template("register.html", error=error)

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            error = "Gebruikersnaam bestaat al."
            return render_template("register.html", error=error)

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password),
        )
        db.commit()

        session["user"] = username
        session["cart"] = {}
        return redirect(url_for("home"))

    return render_template("register.html", error=error)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    # Producten ophalen uit database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Producten tonen in home.html
    return render_template("home.html", products=products)


# =========================
# WINKELWAGEN
# =========================

# Product toevoegen aan winkelwagen
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "user" not in session:
        return redirect(url_for("login"))

    # Winkelwagen ophalen of nieuwe maken
    cart = session.get("cart", {})

    # Product ID als string gebruiken
    key = str(product_id)

    # Aantal verhogen
    cart[key] = cart.get(key, 0) + 1

    # Opslaan in session
    session["cart"] = cart
    session.modified = True

    return redirect(url_for("home"))


# Winkelwagen bekijken
@app.route("/cart")
def cart():
    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    cart_items = []
    total = 0

    # Door alle producten in de winkelwagen lopen
    for pid, qty in session.get("cart", {}).items():
        cursor.execute("SELECT * FROM products WHERE id=?", (int(pid),))
        product = cursor.fetchone()

        if product:
            cart_items.append((product, qty))
            total += product[2] * qty

    return render_template("cart.html", cart_items=cart_items, total=total)


# Aantal verhogen
@app.route("/increase_quantity/<int:product_id>")
def increase_quantity(product_id):
    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart"))


# Aantal verlagen
@app.route("/decrease_quantity/<int:product_id>")
def decrease_quantity(product_id):
    cart = session.get("cart", {})
    key = str(product_id)

    if key in cart:
        if cart[key] > 1:
            cart[key] -= 1
        else:
            del cart[key]

    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart"))


# Winkelwagen leegmaken
@app.route("/clear_cart")
def clear_cart():
    session["cart"] = {}
    session.modified = True
    return redirect(url_for("cart"))


# =========================
# ACCOUNT
# =========================
@app.route("/account", methods=["GET", "POST"])
def account():
    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    # Gegevens opslaan
    if request.method == "POST":
        new_username = request.form["username"]
        new_password = request.form["password"]

        cursor.execute(
            "UPDATE users SET username=?, password=? WHERE username=?",
            (new_username, new_password, session["user"])
        )
        db.commit()

        session["user"] = new_username

        return render_template(
            "account.html",
            user=new_username,
            password=new_password,
            message="Gegevens opgeslagen!"
        )

    # Accountgegevens ophalen
    cursor.execute(
        "SELECT username, password FROM users WHERE username=?",
        (session["user"],)
    )
    user = cursor.fetchone()

    return render_template("account.html", user=user[0], password=user[1])


# =========================
# CONTACT
# =========================
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        return render_template("contact.html", message_sent=True)

    return render_template("contact.html")


# =========================
# APP STARTEN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
