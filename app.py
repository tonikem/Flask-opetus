from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import gen_salt, generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "qwerty12345"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Tietokanta
db = SQLAlchemy(app)


@app.route('/')
def index():
    return "Hello World"


@app.route('/index')
def index_html():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', debug=True)


