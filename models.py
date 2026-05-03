from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # Login
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))

    # Profile
    dob = db.Column(db.String(20))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    address = db.Column(db.String(200))

    education = db.Column(db.String(100))
    field = db.Column(db.String(100))

    skill = db.Column(db.String(100))
    experience = db.Column(db.String(50))

    language = db.Column(db.String(50))

    # Resume
    resume = db.Column(db.String(200))

    # Relation
    candidates = db.relationship('Candidate', backref='user', lazy=True)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    name = db.Column(db.String(100))
    transcript = db.Column(db.Text)

    skill_score = db.Column(db.Integer)
    confidence_score = db.Column(db.Float)
    trust_score = db.Column(db.Integer)

    status = db.Column(db.String(50))
    recommendation = db.Column(db.String(200))