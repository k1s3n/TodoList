from flask import Flask, request, render_template, url_for

app = Flask(__name__)
#dkhejdawda
@app.route("/")
def home():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(debug=True)