from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# ======================
# USER TABLE (LOGIN)
# ======================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")

    # relation (important for PostgreSQL apps)
    candidates = db.relationship('Candidate', backref='user', lazy=True)


# ======================
# CANDIDATE TABLE
# ======================
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # 🔥 FIXED: proper foreign key connection
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(100))
    transcript = db.Column(db.Text)
    skill_score = db.Column(db.Integer)
    confidence_score = db.Column(db.Float)