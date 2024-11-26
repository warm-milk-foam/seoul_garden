from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import uuid
from datetime import datetime
#specifically for AI
from flask import jsonify
import requests

import ollama

app = Flask(__name__)
app.secret_key = "this_key_does_not_need_to_be_private_lmao"

# The code to create paths IF THEY DO NOT exist, but typically would
# error, faulty because the program relies on the stuff outside the code
# if not os.path.exists('accounts'):
#     os.makedirs('accounts')
# if not os.path.exists('orders'):
#     os.makedirs('orders')
# if not os.path.exists('chat_history'):
#     os.makedirs('chat_history')

setup_instructions = """You will act as a Chatbot for a restaurant called Seoul Garden.
Your job is to enlighten the user on deals: Recommendations: KungPao Chicken, Chicken rice, Buffet 1 for 1 special
Do not add any more items other than what is in the menu:
1) Chicken rice
2) Avocado toast
3) Chicken Casear salad
4) Kung Pao Chicken
5) Pasta Alfredo
6) Plain rice
7) Chicken skewers
8) Beef meatballs in marinara sauce
9) Stir fried vegetables
10) Buffet option 2h 
11)
12)
13)
14)
Additionally, you should attempt to guide the user throughout the website, particularly on the order tab.
To order food, they must click on their item and click the submit button to send requests.
You are unable to actually make reservations/orders for the guests, but you can actually suggest food options to them
You start the job now."""

def setup():
    #prompt the ollama model and give it instructions
    global setup_instructions
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': setup_instructions
        },
    ])



@app.route("/")
def home(): # home page
    return render_template("index.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup(): # signup page
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_id = str(uuid.uuid4()) # generates a unqiue id
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        account_info = f"User ID: {user_id}\nUsername: {username}\nPassword: {password}\nEmail: {email}\nCreated At: {timestamp}\n"
        with open(f'accounts/{user_id}_account.txt', 'w') as file:
            file.write(account_info)
            # saves the account data locally

        order_history_path = f'orders/{user_id}_order_history.txt'
        if not os.path.exists(order_history_path):
            open(order_history_path, 'w').close()
            # creates the order history for the new account (which will be empty of course)
        flash('Account created successfully!', 'success')
        return redirect(url_for('signin'))

    return render_template("signup.html")

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        for filename in os.listdir('accounts'):
            with open(f'accounts/{filename}', 'r') as file: # read the accounts directory
                lines = file.readlines() # read everything
                if lines[3].strip().split(': ')[1] == email and lines[2].strip().split(': ')[1] == password:
                    # get the Email and password section
                    user_id = lines[0].strip().split(': ')[1]
                    # get the user id
                    session['user_id'] = user_id # sets up the session so that the server knows that the person has signed in with an account
                    session['email'] = email
                    flash('Logged in successfully!', 'success') # authenticates
                    return redirect(url_for('order'))

        flash('Invalid email or password', 'danger') # if the password is invalid

    return render_template("signin.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))

    user_id = session['user_id']
    chat_history_path = f'chat_history/{user_id}_chat_history.txt'

    if not os.path.exists(chat_history_path):
        with open(chat_history_path, 'w') as file:
            file.write("Recommendations: KungPao Chicken, Chicken rice, Buffet 1 for 1 special\n")

    if request.method == "POST":
        user_input = request.form["user_input"]
        response = chatbot_response(user_input, chat_history_path)

        # Save the chat history
        with open(chat_history_path, 'a') as file:
            file.write(f"User: {user_input}\n")
            file.write(f"Bot: {response}\n")

        return jsonify({"response": response})

    # Load the chat history
    chat_history = []
    if os.path.exists(chat_history_path):
        with open(chat_history_path, 'r') as file:
            chat_history = file.readlines()

    return render_template("chat.html", chat_history=chat_history)

  
def chatbot_response(user_input, chat_history_path):
    global setup_instructions

    # Load chat history
    chat_history = []
    if os.path.exists(chat_history_path):
        with open(chat_history_path, 'r') as file:
            chat_history = file.readlines()

    # Load order history
    order_history_content = ""
    if 'user_id' in session:
        user_id = session['user_id']
        order_history_path = f'orders/{user_id}_order_history.txt'
        if os.path.exists(order_history_path):
            with open(order_history_path, 'r') as file:
                order_history_content = file.read()

    # Prepare messages for the model
    messages = [
        {'role': 'system', 'content': setup_instructions},
        {'role': 'system', 'content': f"Order history: {order_history_content}"},
    ]

    # Add chat history
    for line in chat_history:
        if line.startswith("User:"):
            messages.append({'role': 'user', 'content': line[len("User: "):].strip()})
        elif line.startswith("Bot:"):
            messages.append({'role': 'assistant', 'content': line[len("Bot: "):].strip()})

    # Append the latest user input
    messages.append({'role': 'user', 'content': user_input})

    # Call the model with the updated messages
    response = ollama.chat(model='llama3.2', messages=messages)
    print(response)  # For debugging purposes, to see the response
    return response['message']['content']


@app.route("/order")
def order():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))

    user_id = session['user_id'] # use this later to add it into the order history
    order_history_path = f'orders/{user_id}_order_history.txt'

    return render_template("order.html")

@app.route("/submit_order", methods=["POST"])
def submit_order():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))

    user_id = session['user_id']
    order_history_path = f'orders/{user_id}_order_history.txt'
    

    # Read the order items from the form data
    location = request.form.get('location', 'Unknown location')
    order_items = request.form.getlist('order_item')
    print("Order items received:", order_items)

    if not order_items:
        flash('No items in the order list.', 'danger')
        return redirect(url_for('order'))  

    with open(order_history_path, 'a') as file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"Order placed at: {timestamp}\n")
        file.write(f"Location: {location}\n")
        for item in order_items:
            file.write(f"{item}\n")
        file.write("\n")

    flash('Order submitted successfully!', 'success')
    return redirect(url_for('order'))


def read_order_history():
    user_id = session['user_id']
    file_path = os.path.join('orders', f'{user_id}_order_history.txt')
    with open(file_path, 'r') as file:
        orders = file.read().split('\n\n')
    return orders

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

    orders = read_order_history()
    return render_template("account.html", user_info=user_info, orders=orders)
    
@app.route("/logout")
def logout():
    # Clear the session
    session.clear()
    return redirect("/")


# this is just a debug route
@app.route("/debug_order", methods=["POST"])
def debug_order():
    print("Form data:", request.form)
    return "Check the server logs"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
