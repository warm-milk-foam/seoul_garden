from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import uuid
from datetime import datetime
#specifically for AI
from flask import jsonify
import requests

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

@app.route("/chat", methods=["GET", "POST"]) # we need the methods to GET messages from the bot and POST messages to it
def chat():
    if 'user_id' not in session: # the session is only granted by signin() function, so it checks for this
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))     # flask session carrying bruh
    
    user_id = session['user_id']
    chat_history_path = f'chat_history/{user_id}_chat_history.txt'
    with open(f'chat_history/{user_id}_chat_history.txt', 'w') as file:
        file.write("Recommendations: KungPao Chicken, Chicken rice, Buffet 1 for 1 special ")

    if request.method == "POST":
        user_input = request.form["user_input"]
        response = chatbot_response(user_input)

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

    print(f"Chat history for user {user_id}: {chat_history}")
    return render_template("chat.html", chat_history=chat_history)


def chatbot_response(user_input):

    api_url = 'http://localhost:11434'  # this is locally btw
    # response = requests.post(api_url, json={'input': user_input})
    payload = {
# apparently i need a user key to authenticate 

        "model": "llama3.2",
        "prompt": user_input
    }
    print(f"Payload: {payload}")
    response = requests.post(api_url, json=payload)
    print(f"API Response Status Code: {response.status_code}")
    print(f"API Response Content: {response.content}")
    if response.status_code == 200:
        return response.json().get('response', 'No response from the model.')
    else:
        return 'Error: Unable to get a response from the model.'
    
    # error because it cannot be found by the model


@app.route("/order")
def order():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'danger')
        return redirect(url_for('signin'))    
        
    user_id = session['user_id'] # use this later to add it into the order history
    order_history_path = f'orders/{user_id}_order_history.txt'


    return render_template("order.html")

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
    app.run(debug=True, port=5000)
