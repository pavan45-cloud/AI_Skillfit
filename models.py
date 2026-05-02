from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Candidate table
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    transcript = db.Column(db.Text)
    skill_score = db.Column(db.Integer)
    confidence_score = db.Column(db.Float)

# User table (LOGIN SYSTEM)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default="user")