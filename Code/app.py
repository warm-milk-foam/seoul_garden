from flask import Flask, render_template, request
import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

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