from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "this_key_does_not_need_to_be_private_lmao"

if not os.path.exists('accounts'):
    os.makedirs('accounts')
if not os.path.exists('orders'):
    os.makedirs('orders')
# emergency code i suppose

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email'] # these 3 are obvious
        user_id = str(uuid.uuid4()) # unqiue user id
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # date of account creation

        account_info = f"User ID: {user_id}\nUsername: {username}\nPassword: {password}\nCreated At: {timestamp}\n"
        with open(f'accounts/{user_id}_account.txt', 'w') as file:
            file.write(account_info)

        order_history_path = f'orders/{user_id}_order_history.txt'
        if not os.path.exists(order_history_path):
            open(order_history_path, 'w').close()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('order'))

    return render_template("signup.html")

@app.route("/signin")
def signin():
   # account_folder = os.path.join(os.path.dirname(__file__), "accounts")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        for filename in os.listdir('accounts'):
            with open(f'accounts/{filename}', 'r') as file:
                lines = file.readlines()
                if lines[1].strip().split(': ')[1] == username and lines[2].strip().split(': ')[1] == password:
                    user_id = lines[0].strip().split(': ')[1]
                    session['user_id'] = user_id
                    session['username'] = username
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template("signin.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/order")
def order():
    return render_template("order.html")

@app.route("/account")
def account():
    return render_template("account.html")

if __name__ == "__main__":
    app.run(debug=True)