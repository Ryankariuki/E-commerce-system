from flask import Flask, url_for, request, jsonify, redirect, session, send_from_directory
from flask_mysqldb import MySQL
import mysql.connector
import config
import werkzeug.security
import json 

app = Flask(__name__)
app.secret_key = '2003'

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

@app.route('/select-role')
def select_role():
    return send_from_directory('templates', 'select_role.html')

@app.route('/')
def home():
    return redirect(url_for('select_role'))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect('/admin-dashboard')
        else:
            return "Admin Login Failed"
    return send_from_directory('templates', 'admin_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.form.get('role', 'buyer')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s AND role=%s", (email, password, role))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user[0]
            if role == 'seller':
                return redirect('/seller-dashboard')
            else:
                return redirect('/buyer-dashboard')
        else:
            return "Login Failed"
        
    return send_from_directory('templates', 'login.html')


@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('/admin-login'))
    return send_from_directory('templates', 'admin-dashboard.html')

@app.route('/api/user_counts')
def user_counts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE role='seller'")
    seller_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE role='buyer'")
    buyer_count = cur.fetchone()[0]
    cur.close()
    return jsonify({"seller_count": seller_count, "buyer_count": buyer_count})

@app.route('/buyer-dashboard')
def buyer_dashboard():
    return send_from_directory('templates', 'buyer_dashboard.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES(%s, %s, %s, %s)", (name, email, password, role))
        mysql.connection.commit()
        cursor.close()

        return redirect('/login')
    
    return send_from_directory('templates', 'register.html')


@app.route('/products')
def products():
    return send_from_directory('templates', 'products.html')


@app.route('/api/products')
def api_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, description, price, image_url FROM products")
    products = cur.fetchall()
    cur.close()

    product_list = []
    for p in products:
        product_list.append({
            "id": p[0],
            "name": p[1],
            "description": p[2],
            "price": float(p[3]),
            "image_url": p[4]
        })
    
    return jsonify(product_list)



@app.route('/cart')
def cart():
    return send_from_directory('templates','cart.html')



@app.route('/seller-dashboard')
def seller_dashboard():
    return send_from_directory('templates', 'seller-dashboard.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']
        stock = request.form['stock']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO products (name, description, price, image_url, stock) VALUES(%s, %s, %s, %s, %s)",(name, description, price, image_url, stock))
        mysql.connection.commit()
        cur.close()

        return redirect('/seller-dashboard')
    
@app.route('/api/seller_products')
def api_seller_products():
    cur = mysql.connection.cursor() 
    cur.execute("SELECT id, name, description, price, image_url, stock FROM products")
    products = cur.fetchall()
    cur.close()

    product_list = []
    for p in products:
        product_list.append({
            "id": p[0],
            "name": p[1],
            "description": p[2],
            "price": float(p[3]),
            "image_url": p[4],
            "stock": p[5]
        })
    
    return jsonify(product_list)

@app.route('/api/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"success": True})

@app.route('/api/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET name=%s, description=%s, price=%s, image_url=%s, stock=%s WHERE id=%s",
                (data['name'], data['description'], data['price'], data['image_url'], data['stock'], product_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"success": True})

@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return "User not found", 404

    return send_from_directory('templates', 'checkout.html')

@app.route('/api/submit_order', methods=['POST'])
def submit_order():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    products = data.get('products', [])
    total = data.get('total')
    delivery_date = data.get('deliveryDate')

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Insert into orders table
    cur.execute("INSERT INTO orders (user_id, total, delivery_date) VALUES (%s, %s, %s)", 
                (user_id, total, delivery_date))
    mysql.connection.commit()
    order_id = cur.lastrowid

    # Insert each product into order_items
    for item in products:
        product_id = item['id']
        quantity = item['quantity']
        price = item['price']
        cur.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (order_id, product_id, quantity, price))
    
    mysql.connection.commit()
    cur.close()

    return jsonify({
        'success': True,
        'order_id': order_id,
        'user_id': user_id
    })

@app.route('/api/check_session')
def check_session():
    return jsonify({'user_id': session.get('user_id')})



if __name__ == '__main__':
    app.run(debug=True)