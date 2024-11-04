from flask import Flask

app = Flask(__name__)

@app.route("")
def home():
    return "Home page"

@app.route("/signup")
def signup():
    return "It works"

@app.route("/chat")
def chat():
    return "It works again"

@app.route("/order")
def order():
    return "yep it works"

@app.route("/account")
def account():
    return "again it works"

if __name__ == "__main__":
    app.run(debug=True)