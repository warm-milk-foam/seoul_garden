from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import uuid
from datetime import datetime
#specifically for AI
from flask import jsonify
import subprocess

def chatbot_response(user_input, model_name="llama3.2"):
    # Use subprocess to run the Ollama CLI command
    command = f"ollama run {model_name} --input '{user_input}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    response = result.stdout.strip()
    return response

app = Flask(__name__)
app.secret_key = "this_key_does_not_need_to_be_private_lmao"

# The code to create paths IF THEY DO NOT exist, but typically would
if not os.path.exists('accounts'):
    os.makedirs('accounts')
if not os.path.exists('orders'):
    os.makedirs('orders')


@app.route("/")
def home(): # home page
    return render_template("index.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup(): # signup page
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

@app.route("/chat", methods=["GET", "POST"]) # we need the methods to GET messages from the bot and POST messages to it
def chat():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))    
    if request.method == "POST":
        user_input = request.form["user_input"]
        response = chatbot_response(user_input)
        return jsonify({"response": response})
    return render_template("chat.html")

@app.route("/order")
def order():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))    
        
    user_id = session['user_id']
    user_info = {}

    with open(f'accounts/{user_id}_account.txt', 'r') as file:
        lines = file.readlines()
        user_info['user_id'] = lines[0].strip().split(': ')[1]
        user_info['username'] = lines[1].strip().split(': ')[1]
        user_info['email'] = lines[3].strip().split(': ')[1]
        user_info['created_at'] = lines[4].strip().split(': ')[1]

    return render_template("order.html", user_info=user_info)

@app.route("/account")
def account():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))
    
    user_id = session['user_id']
    user_info = {}

    with open(f'accounts/{user_id}_account.txt', 'r') as file:
        lines = file.readlines()
        user_info['user_id'] = lines[0].strip().split(': ')[1]
        user_info['username'] = lines[1].strip().split(': ')[1]
        user_info['email'] = lines[3].strip().split(': ')[1]
        user_info['created_at'] = lines[4].strip().split(': ')[1]

    return render_template("account.html", user_info=user_info)
    

if __name__ == "__main__":
    app.run(debug=True)
