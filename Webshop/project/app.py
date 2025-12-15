from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3


app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = "geheimesleutel"

DATABASE = "shop.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3


app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = "geheimesleutel"

DATABASE = "shop.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO products (name, price) VALUES (?, ?)",
                [("Laptop", 999.99), ("Headset", 59.99), ("Muis", 29.99)]
            )
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("admin", "1234")
            )
        db.commit()

init_db()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/home')
def home():
    if "user" not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('home.html', products=products, logged_in=('user' in session))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = username
            return redirect(url_for('account'))
        else:
            return 'Onjuiste login!'

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'cart' not in session:
        session['cart'] = {}
    if isinstance(session['cart'], list):
        new_cart = {}
        for pid in session['cart']:
            key = str(pid)
            new_cart[key] = new_cart.get(key, 0) + 1
        session['cart'] = new_cart

    pid_key = str(product_id)
    session['cart'][pid_key] = session['cart'].get(pid_key, 0) + 1
    session.modified = True

    return redirect(url_for('home'))


@app.route('/cart')
def cart():
    if 'user' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    cart_items = []
    total = 0

    if 'cart' in session:
        cart_data = session['cart']
        if isinstance(cart_data, list):
            counts = {}
            for pid in cart_data:
                counts[str(pid)] = counts.get(str(pid), 0) + 1
            cart_data = counts
            session['cart'] = cart_data

        for pid_str, quantity in cart_data.items():
            try:
                cursor.execute('SELECT * FROM products WHERE id=?', (int(pid_str),))
            except Exception:
                continue
            product = cursor.fetchone()
            if product:
                cart_items.append((product, quantity))
                total += product[2] * quantity

    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        return render_template('contact.html', message_sent=True)

    return render_template('contact.html')


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'cart' in session:
        cart = session['cart']
        if isinstance(cart, dict):
            key = str(product_id)
            if key in cart:
                del cart[key]
                session['cart'] = cart
                session.modified = True
        else:
            try:
                cart.remove(product_id)
                session['cart'] = cart
                session.modified = True
            except ValueError:
                pass

    return redirect(url_for('cart'))


@app.route('/clear_cart')
def clear_cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    session['cart'] = {}
    session.modified = True
    return redirect(url_for('cart'))


@app.route('/increase_quantity/<int:product_id>')
def increase_quantity(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'cart' in session:
        cart = session['cart']
        if isinstance(cart, list):
            new_cart = {}
            for pid in cart:
                new_cart[str(pid)] = new_cart.get(str(pid), 0) + 1
            cart = new_cart
        key = str(product_id)
        cart[key] = cart.get(key, 0) + 1
        session['cart'] = cart
        session.modified = True

    return redirect(url_for('cart'))


@app.route('/decrease_quantity/<int:product_id>')
def decrease_quantity(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'cart' in session:
        cart = session['cart']
        if isinstance(cart, list):
            new_cart = {}
            for pid in cart:
                new_cart[str(pid)] = new_cart.get(str(pid), 0) + 1
            cart = new_cart
        key = str(product_id)
        if key in cart:
            if cart[key] > 1:
                cart[key] -= 1
            else:
                del cart[key]
            session['cart'] = cart
            session.modified = True

    return redirect(url_for('cart'))


@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        username = session['user']

        cursor.execute('UPDATE users SET username=?, password=? WHERE username=?', (new_username, new_password, username))
        db.commit()

        session['user'] = new_username
        session.modified = True
        return render_template('account.html', user=new_username, password=new_password, message='Gegevens opgeslagen!')

    cursor.execute('SELECT username, password FROM users WHERE username=?', (session['user'],))
    user_data = cursor.fetchone()

    if user_data:
        return render_template('account.html', user=user_data[0], password=user_data[1])
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
