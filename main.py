from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
import uuid
import datetime

app = Flask('app')
app.secret_key = "mysecretkey"


@app.route('/reset')
def reset():
    connection = sqlite3.connect("store_schema.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    with open('store_schema.sql', 'r') as f:
        script = f.read()
    cursor.executescript(script)

    connection.commit()

    return redirect(url_for('index'))


@app.route('/')
def index():
    connection = sqlite3.connect("store_schema.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM product")
    product = cursor.fetchall()
    connection.commit()

    cursor.execute("SELECT * FROM category")
    category = cursor.fetchall()
    connection.commit()

    connection.close()

    #check if user is logged in
    username = session.get('username')

    return render_template("index.html",
                           product=product,
                           category=category,
                           username=username)


@app.route('/<category>')
def display_category(category):
    connection = sqlite3.connect("store_schema.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM product p JOIN category c ON c.cid = p.cid WHERE c.cname = ?",
        (category, ))
    product = cursor.fetchall()
    connection.commit()

    cursor.execute("SELECT * FROM category")
    category = cursor.fetchall()
    connection.commit()

    connection.close()

    # check if user is logged in
    username = session.get('username')

    return render_template('index.html',
                           product=product,
                           category=category,
                           username=username)


@app.route('/search', methods=['GET', 'POST'])
def search():
    connection = sqlite3.connect("store_schema.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if request.method == 'POST':
        search_query = request.form['search_query']
        print('Search query:', search_query)
        cursor.execute("SELECT * FROM product WHERE pname LIKE ?",
                       ('%' + search_query + '%', ))
        product = cursor.fetchall()
    else:
        product = []

    cursor.execute("SELECT * FROM category")
    category = cursor.fetchall()

    # check if user is logged in
    username = session.get('username')

    return render_template('index.html',
                           product=product,
                           category=category,
                           username=username)


@app.route('/logout')
def logout():
    session.clear()
    return render_template("login.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        connection = sqlite3.connect("store_schema.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        uName = request.form["field_user"]
        uPass = request.form["field_pass"]

        cursor.execute("SELECT * FROM people WHERE loginId=? AND pass=?",
                       (uName, uPass))
        user = cursor.fetchone()
        if user:
            user = dict(user)
            session['username'] = uName
            session['logged in'] = True
            session['user'] = {'login_id': user['loginId'], 'username': uName}
            return redirect(url_for('index'))
        else:
            error = True
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        connection = sqlite3.connect("store_schema.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        name = request.form["Name"]
        email = request.form["Email"]
        user = request.form["Username"]
        password = request.form["Password"]

        # Check if the user already exists
        cursor.execute("SELECT * FROM people WHERE loginId = ?", (user, ))
        existing_user = cursor.fetchone()

        if existing_user:
            error = True
            return render_template('register.html', error=error)

        session.clear()
        session['username'] = user
        cursor.execute("INSERT INTO people VALUES (?, ?, ?, ?)",
                       [name, user, email, password])
        connection.commit()
        return render_template('login.html')


## Otherwise return register page on get request
    return render_template('register.html')


@app.route('/cart')
def view_cart():
    connection = sqlite3.connect("store_schema.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    total = sum(
        float(item['price']) * float(item['quantity'])
        for item in cart.values())
    total = round(total, 2)
    product_quantities = {}
    for product_id in cart.keys():
        product = cursor.execute("SELECT quantity FROM product WHERE pid= ?",
                                 (int(product_id), )).fetchone()
        if product:
            product_quantities[product_id] = product[0]
    return render_template('cart.html',
                           cart=cart,
                           total=total,
                           product_quantities=product_quantities)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Connect to the database and get product details from cart
    connection = sqlite3.connect("store_schema.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    product_id = str(product_id)

    quantity = int(request.form['quantity'])

    product = cursor.execute("SELECT * FROM product WHERE pid = ?",
                             (product_id, )).fetchone()

    if not product:
        return redirect(url_for('index'))

    # create cart key if it does not exist
    session.setdefault('cart', {})

    if product_id in session['cart']:
        session['cart'][product_id]['quantity'] += quantity
        if quantity + session['cart'][product_id]['quantity'] > product[
                'quantity']:
            session['cart'][product_id]['quantity'] = product['quantity']

    else:
        session['cart'][product_id] = {
            'pid': product_id,
            'name': product['pname'],
            'price': product['price'],
            'quantity': quantity
        }

    session.modified = True
    return redirect(url_for('view_cart'))


@app.route('/deletecart')
def delete_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))


@app.route('/checkout', methods=["POST"])
def checkout():
    # Connect to the database and get product details from cart
    connection = sqlite3.connect("store_schema.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if 'user' not in session:
        # handle the error, redirect to login page, etc.
        return redirect(url_for('login'))

    for product in session['cart'].values():
        if 'pid' not in product:
            continue
        pid = product['pid']
        quantity = product['quantity']
        original = cursor.execute("SELECT * FROM product WHERE pid = ?",
                                  (pid, )).fetchone()
        new = original['quantity'] - quantity
        cursor.execute("UPDATE product SET quantity = ? WHERE pid = ?",
                       (new, pid))

    # Insert order information into orders table
    order_date = datetime.date.today()
    order_id = str(uuid.uuid4())
    login_id = session['user']['login_id']
    total = sum([
        product['price'] * product['quantity']
        for product in session['cart'].values()
    ])
    cursor.execute(
        "INSERT INTO orders (orderDate, orderID, loginId, total) VALUES (?, ?, ?, ?)",
        (order_date, order_id, login_id, total))
    #insert item information into orderitem table
    for product in session['cart'].values():
        if 'pid' not in product:
            continue
        pid = product['pid']
        quantity = product['quantity']
        price = product['price']
        name = product['name']
        cursor.execute(
            "INSERT INTO orderItems (orderID, pid, qty, sumPrice, name) VALUES (?, ?, ?, ?, ?)",
            (order_id, pid, quantity, price, name))

    # Clear the cart from the session
    session.pop('cart', None)

    # Commit the changes to the database
    connection.commit()

    # Close the database connection
    connection.close()

    return redirect(url_for('order_history'))


@app.route('/cart/remove/<int:product_id>', methods=["POST"])
def remove_from_cart(product_id):

    product_id = str(product_id)
    if product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True

    return redirect(url_for('view_cart'))


@app.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):

    new_quantity = int(request.form['quantity'])
    product_id = str(product_id)

    if product_id in session['cart'] and new_quantity >= 0:
        if new_quantity == 0:
            del session['cart'][product_id]
        else:
            session['cart'][product_id]['quantity'] = new_quantity

        session.modified = True
    return redirect(url_for('view_cart'))


@app.route('/order_history')
def order_history():
    # Connect to the database
    connection = sqlite3.connect("store_schema.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if 'user' not in session:
        # handle the error, redirect to login page, etc.
        return redirect(url_for('login'))

    # Get all orders for the logged-in user
    login_id = session['user']['login_id']
    orders = cursor.execute("SELECT * FROM orders WHERE loginId = ?",
                            (login_id, )).fetchall()

    # Get the order items for each order and convert orders to dictionary
    orders_dict_list = []
    for order in orders:
        order_id = order['orderID']
        order_items = cursor.execute(
            "SELECT * FROM orderItems WHERE orderID = ?",
            (order_id, )).fetchall()
        order_dict = dict(order)
        order_dict['items'] = order_items
        orders_dict_list.append(order_dict)

    # Close the database connection
    connection.close()

    return render_template('order_history.html', orders=orders)


app.run(host='0.0.0.0', port=8080)
