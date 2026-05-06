from flask import (Flask, render_template, redirect,
                   url_for, request, flash, jsonify, abort)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, UserMixin,
                         login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import markdown as md

app = flask(__name__)
app.config['SECRET_KEY'] = 108158379

login_manager = LoginManager(app)

Class User(UserMixin, DB.Model):
id = db.Column(db.Integer, primarykey = True)
username = db.Column(db.String(80), unique = True, nullable = False)
password_hash = db.Column(db.string(200), nullable = False)
is_admin = db.Column(db.bolean, default = False)

with app.app_context():
    db.create_all()
    if not User.querry.filter_by(Username = 'admin',).first():
        db.session.add(User(
            Username = 'admin'
            Password_hash = generate_password_hash('admin123')
            is_admin = True
        ))
    db.session.commit()
-----
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        ))
        db.session.commit()