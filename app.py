# -------------------------------
# 📦 IMPORTS
# -------------------------------
from flask import (Flask, render_template, redirect,
                   url_for, request, flash, jsonify, abort)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, UserMixin,
                         login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import markdown as md


# -------------------------------
# ⚙️ APP CONFIG
# -------------------------------
app = Flask(__name__)     
app.config['SECRET_KEY'] = '108158379'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)


# -------------------------------
# 🔐 FLASK-LOGIN
# -------------------------------
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------------------
# 🗄 DATABASE MODELS
# -------------------------------

# User model
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True,  nullable=False)
    password_hash = db.Column(db.String(200),                  nullable=False)
    is_admin      = db.Column(db.Boolean, default=False) 

# Section model
class Section(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    emoji       = db.Column(db.String(10))
    topics      = db.relationship('Topic', backref='section', lazy=True,
                                  cascade='all, delete-orphan')

# Topic model   
class Topic(db.Model): 
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    elements   = db.relationship('LearningElement', backref='topic', lazy=True,
                                 cascade='all, delete-orphan')

# LearningElement model
class LearningElement(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    topic_id       = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    type           = db.Column(db.String(20),  nullable=False)
    content        = db.Column(db.Text)
    question       = db.Column(db.Text)
    option_a       = db.Column(db.String(200))
    option_b       = db.Column(db.String(200))
    option_c       = db.Column(db.String(200)) 
    option_d       = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))
    answer_key     = db.Column(db.Text)

# Progress model
class Progress(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),             nullable=False)
    element_id = db.Column(db.Integer, db.ForeignKey('learning_element.id'), nullable=False)
    correct    = db.Column(db.Boolean)

# OpenAnswer model
class OpenAnswer(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),             nullable=False)
    element_id = db.Column(db.Integer, db.ForeignKey('learning_element.id'), nullable=False)
    answer     = db.Column(db.Text)

# TopicVisit model
class TopicVisit(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        ))
        db.session.commit()

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Feil brukernavn eller passord', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            flash('Brukernavnet er allerede tatt', 'error')
            return redirect(url_for('register'))
        db.session.add(User(
            username=username,
            password_hash=generate_password_hash(request.form['password']),
            is_admin=False
        ))
        db.session.commit()
        login_user(User.query.filter_by(username=username).first())
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logg-ut')
@login_required
def logg_ut():
    logout_user()
    return redirect(url_for('login'))


