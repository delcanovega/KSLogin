from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return "Work in progress"

@app.route("/train")
def train():
    return render_template("train.html")

if __name__ == "__main__":
    app.run(debug = True)
