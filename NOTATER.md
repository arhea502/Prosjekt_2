# ===============================
# APP.PY – FULL KODE
# ===============================

# -------------------------------
# ⚙️ IMPORTS
# -------------------------------
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# -------------------------------
# ⚙️ KONFIGURASJON
# -------------------------------

# Lager Flask-appen. __name__ hjelper Flask å finne templates og static mapper
app = Flask(__name__)

# Secret key brukes til å signere session cookies. Innlogging fungerer ikke uten
app.config['SECRET_KEY'] = '108158379'

# Databasekonfigurasjon – SQLite database i prosjektmappen. Den sier også at den skal hete database.db
# '///' betyr relativ sti til prosjektmappen
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Kobler Flask til databasen, tilgjengelig overalt
db = SQLAlchemy(app)

# -------------------------------
# 🔐 FLASK-LOGIN
# -------------------------------

 # Kobler Flask til login-systemet
login_manager = LoginManager(app)     


 # Redirect til 'login' hvis ikke logget inn
login_manager.login_view = 'login'  


# -------------------------------
# 👤 DATABASEMODELLER
# -------------------------------
class User(UserMixin, db.Model):
    """
    User-modell for innlogging
    - id: Primærnøkkel
    - username: Brukernavn
    - password: Passord (klartekst her; i praksis bruk hashing)
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# -------------------------------
# 🧩 USER LOADER
# -------------------------------
@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login trenger å vite hvordan den henter brukere fra databasen
    - Kalles automatisk ved hver forespørsel med session-cookie
    - user_id konverteres til int fordi ID er tall i databasen
    """
    return User.query.get(int(user_id))

# -------------------------------
# 🔨 DATABASE INITIALISERING
# -------------------------------
if __name__ == '__main__':
    db.create_all()  # Opprett databasen og tabeller hvis de ikke finnes
    app.run(debug=True)