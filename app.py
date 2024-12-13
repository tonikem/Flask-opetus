from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, session, url_for
from flask_restful import Api, Resource
from werkzeug.security import gen_salt, generate_password_hash, check_password_hash


# Palvelin-olio.
app = Flask(__name__)
app.secret_key = "qwerty12345"

# REST-olio
api = Api(app)

# Tietokannan muuttujat
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Tietokanta
db = SQLAlchemy(app)


class Usermodel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(90), nullable=False)

    # Asetetaan käyttäjän nimi.
    def set_username(self, username):
        self.username = username

    # Asetetaan salasana (hash).
    def set_password(self, password):
        ## ChatGPT selittää "hash"-funktion:
        # Hash-funktio on matemaattinen funktio, joka ottaa syötteenä jonkinlaisen datan
        # ja tuottaa siitä lyhyemmän, kiinteän pituisen arvon,
        # joka tunnetaan nimellä hash-arvo tai tiiviste.
        self.password_hash = generate_password_hash(password)

    # Tarkistetaan salasanasta saatu hash.
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route('/')
def index():
    # Palauttaa merkkijonon.
    return "Hello World"


@app.route('/index')
def index_html():
    # Tarkistaa onko käyttäjä kirjautunut ja ohjaa sitten dashboard-sivulle.
    if "username" in session:
        return redirect(url_for("dashboard"))
    # Muutoin, jos käyttäjä ei ole kirjautunut, tuodaan index-sivu.
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def login():
    # Otetaan HTML-formin data muuttujiin.
    username = request.form['username']
    password = request.form['password']
    user = Usermodel.query.filter_by(username=username).first() # <- Haetaan käyttäjä.
    # Tarkistetaan käyttäjän salasana.
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template("index.html")


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    user = Usermodel.query.filter_by(username=username).first() # <- Haetaan käyttäjä.
    # Testataan onko käyttäjä jo olemassa.
    # Jos on, palautetaan virheilmoitus.
    if user:
        return render_template("index.html", error="Käyttäjä on jo olemassa!")
    else:
        # Luodaan uusi käyttäjä tietokantaan.
        new_user = Usermodel()
        new_user.set_username(username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        # Asetetaan session-muuttujaan username.
        session['username'] = username
        return redirect(url_for('dashboard'))


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if "username" in session:
        # Jos käyttäjä on session-listalla, renderöidään dashboard.html
        return render_template("dashboard.html", username=session["username"])
    else:
        return redirect(url_for("index"))


@app.route('/logout', methods=['GET'])
def logout():
    # Poistetaan session-listasta käyttäjä pop-komennolla.
    session.pop('username', None)
    return redirect("index")


class REST_rajapinta(Resource):
    def get(self):
        return {"msg": "Hello World!"}


if __name__ == "__main__":
    with app.app_context():
        # Luodaan tietokanta taulut.
        db.create_all()
    
    # Lisätään rajapinta-resurssi.
    api.add_resource(REST_rajapinta, "/api")

    # Ajetaan palvelin.
    app.run(host='0.0.0.0', debug=True)


