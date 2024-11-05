from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "this_key_does_not_need_to_be_private_lmao"

if not os.path.exists('accounts'):
    os.makedirs('accounts')
if not os.path.exists('orders'):
    os.makedirs('orders')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        account_info = f"User ID: {user_id}\nUsername: {username}\nPassword: {password}\nEmail: {email}\nCreated At: {timestamp}\n"
        with open(f'accounts/{user_id}_account.txt', 'w') as file:
            file.write(account_info)

        order_history_path = f'orders/{user_id}_order_history.txt'
        if not os.path.exists(order_history_path):
            open(order_history_path, 'w').close()

        flash('Account created successfully!', 'success')
        return redirect(url_for('signin'))

    return render_template("signup.html")

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        for filename in os.listdir('accounts'):
            with open(f'accounts/{filename}', 'r') as file:
                lines = file.readlines()
                if lines[3].strip().split(': ')[1] == email and lines[2].strip().split(': ')[1] == password:
                    user_id = lines[0].strip().split(': ')[1]
                    session['user_id'] = user_id
                    session['email'] = email
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('order'))

        flash('Invalid email or password', 'danger')

    return render_template("signin.html")

@app.route("/chat")
def chat():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))    
    return render_template("chat.html")

@app.route("/order")
def order():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))    
    return render_template("order.html")

@app.route("/account")
def account():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))    
    return render_template("account.html")

if __name__ == "__main__":
    app.run(debug=True)
